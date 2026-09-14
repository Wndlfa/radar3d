"""Endpoints de produtos + modelos encontrados.

Implementa os filtros da §8 das regras, incluindo o toggle "só comercialmente
utilizável".
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from redis import Redis
from rq import Queue

from radar3d.config import settings
from datetime import datetime, timedelta, timezone

from radar3d.auth.deps import get_current_user, get_current_user_optional
from radar3d.auth.plans import can
from radar3d.auth import usage
from radar3d.db import get_session
from radar3d.domain.licenses import LicenseTier
from radar3d.models import Model3D, Product, ProductModelMatch, ProductSnapshot, User
from radar3d.schemas import (
    ProductCreate,
    ProductDetailOut,
    ProductOut,
    SnapshotInput,
    TrendingOut,
)

_PERIODS = {"day": timedelta(days=1), "week": timedelta(weeks=1), "month": timedelta(days=30)}

# Prioridade das faixas para escolher a "melhor" licença encontrada por produto.
_TIER_RANK = {
    LicenseTier.VENDA_PERMITIDA.value: 3,
    LicenseTier.EXIGE_LICENCA.value: 2,
    LicenseTier.SOMENTE_PESSOAL.value: 1,
    LicenseTier.NAO_IDENTIFICADA.value: 0,
}
_RANK_TO_TIER = {v: k for k, v in _TIER_RANK.items()}


def _license_summary(session: Session, product_ids: list[str]) -> dict[str, dict]:
    """Para cada produto: nº de modelos, melhor faixa e se é comercializável."""
    if not product_ids:
        return {}
    rows = session.execute(
        select(
            ProductModelMatch.product_id,
            Model3D.license_tier,
            Model3D.possible_protected_ip,
        )
        .join(Model3D, Model3D.id == ProductModelMatch.model_id)
        .where(ProductModelMatch.product_id.in_(product_ids))
    ).all()
    agg: dict[str, dict] = {}
    for pid, tier, ip in rows:
        s = agg.setdefault(pid, {"models_count": 0, "best_rank": -1, "ip": False})
        s["models_count"] += 1
        s["best_rank"] = max(s["best_rank"], _TIER_RANK.get(tier, 0))
        s["ip"] = s["ip"] or bool(ip)
    out: dict[str, dict] = {}
    for pid, s in agg.items():
        best = _RANK_TO_TIER.get(s["best_rank"])
        out[pid] = {
            "models_count": s["models_count"],
            "best_license_tier": best,
            "commercial_available": s["best_rank"] >= 2,  # 🟢 ou 🟡
            "protected_ip": s["ip"],
        }
    return out

router = APIRouter(prefix="/products", tags=["products"])

_COMMERCIAL_TIERS = {LicenseTier.VENDA_PERMITIDA.value, LicenseTier.EXIGE_LICENCA.value}


def _enqueue_enrichment(product_id: str) -> str:
    """Enfileira a coleta+matching do produto no worker (ver workers/tasks.py)."""
    from radar3d.workers.tasks import enrich_product

    conn = Redis.from_url(settings.redis_url)
    job = Queue("radar3d", connection=conn).enqueue(enrich_product, product_id)
    return job.id


def _record_snapshot(session: Session, product: Product) -> None:
    """Grava um datapoint com as métricas atuais do produto."""
    session.add(
        ProductSnapshot(
            product_id=product.id,
            price_brl=product.price_brl,
            public_sales=product.public_sales,
            competitors=product.competitors,
            rating=product.rating,
        )
    )


@router.get("", response_model=list[ProductOut])
def list_products(
    session: Session = Depends(get_session),
    q: str | None = Query(None, description="Busca no título do produto."),
    trend: str | None = None,
    max_price: float | None = None,
    sort: str = Query("sales", pattern="^(sales|price_asc|price_desc)$"),
    commercial_only: bool = Query(
        False, description="Só produtos com modelo comercialmente utilizável (§8)."
    ),
    limit: int = Query(50, le=200),
    offset: int = 0,
    user: User | None = Depends(get_current_user_optional),
) -> list[dict]:
    # Filtro comercial é recurso de plano pago (ver docs/regras-de-negocio.md §10).
    if commercial_only and not (user and can(user.plan, "commercial_filter")):
        raise HTTPException(
            status_code=402,
            detail="O filtro comercial exige plano Pro ou Business.",
        )

    stmt = select(Product)
    if q:
        stmt = stmt.where(Product.title.ilike(f"%{q}%"))
    if trend:
        stmt = stmt.where(Product.trend == trend)
    if max_price is not None:
        stmt = stmt.where(Product.price_brl <= max_price)

    if commercial_only:
        # Produtos que têm ao menos um modelo em faixa comercial (🟢/🟡).
        sub = (
            select(ProductModelMatch.product_id)
            .join(Model3D, Model3D.id == ProductModelMatch.model_id)
            .where(Model3D.license_tier.in_(_COMMERCIAL_TIERS))
        )
        stmt = stmt.where(Product.id.in_(sub))

    order = {
        "sales": Product.public_sales.desc().nullslast(),
        "price_asc": Product.price_brl.asc().nullslast(),
        "price_desc": Product.price_brl.desc().nullslast(),
    }[sort]
    stmt = stmt.order_by(order).limit(limit).offset(offset)
    products = list(session.scalars(stmt).all())

    summary = _license_summary(session, [p.id for p in products])
    return [
        {**ProductOut.model_validate(p).model_dump(), **summary.get(p.id, {})}
        for p in products
    ]


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate, session: Session = Depends(get_session)
) -> Product:
    """Cadastra um produto Shopee curado e já dispara a busca de modelos."""
    product = Product(**payload.model_dump())
    session.add(product)
    session.flush()
    _record_snapshot(session, product)  # datapoint inicial
    session.commit()
    session.refresh(product)
    _enqueue_enrichment(product.id)
    return product


@router.get("/trending", response_model=list[TrendingOut])
def trending(
    session: Session = Depends(get_session),
    period: str = Query("week", pattern="^(day|week|month)$"),
    limit: int = Query(20, le=100),
) -> list[dict]:
    """Produtos "em alta": maior crescimento de vendas públicas na janela.

    Cresce comparando o snapshot mais antigo dentro da janela com o mais recente.
    """
    window_start = datetime.now(timezone.utc) - _PERIODS[period]
    results: list[dict] = []

    for product in session.scalars(select(Product)).all():
        snaps = session.scalars(
            select(ProductSnapshot)
            .where(ProductSnapshot.product_id == product.id)
            .order_by(ProductSnapshot.captured_at)
        ).all()
        in_window = [s for s in snaps if s.captured_at >= window_start] or snaps[-1:]
        if len(in_window) < 2 or in_window[0].public_sales is None:
            continue
        first, last = in_window[0].public_sales, in_window[-1].public_sales or 0
        growth = last - first
        if growth <= 0:
            continue
        results.append(
            {
                **ProductOut.model_validate(product).model_dump(),
                "period": period,
                "growth_abs": growth,
                "growth_pct": round(growth / first, 4) if first else None,
                "first_sales": first,
                "last_sales": last,
                "_pid": product.id,
            }
        )

    results.sort(key=lambda r: r["growth_abs"], reverse=True)
    results = results[:limit]

    summary = _license_summary(session, [r["_pid"] for r in results])
    for r in results:
        r.update(summary.get(r.pop("_pid"), {}))
    return results


@router.post("/{product_id}/snapshot", response_model=ProductOut)
def add_snapshot(
    product_id: str, payload: SnapshotInput, session: Session = Depends(get_session)
) -> Product:
    """Registra um datapoint de coleta (simula a coleta diária da Shopee)."""
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    _record_snapshot(session, product)
    session.commit()
    session.refresh(product)
    return product


@router.post("/{product_id}/enrich")
def enrich(product_id: str, session: Session = Depends(get_session)) -> dict:
    """(Re)dispara a coleta de modelos semelhantes + classificação de licença."""
    if session.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    job_id = _enqueue_enrichment(product_id)
    return {"enqueued": True, "job_id": job_id}


@router.get("/{product_id}", response_model=ProductDetailOut)
def get_product(
    product_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> Product:
    # Ver o detalhe (modelos + licenças) é a "consulta" medida no plano Free.
    quota = usage.consume(session, user)
    if not quota.allowed:
        raise HTTPException(
            status_code=402,
            detail=f"Limite mensal do plano Free atingido ({quota.limit} consultas). "
            "Assine o Pro para consultas ilimitadas.",
        )
    stmt = (
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.matches).selectinload(ProductModelMatch.model))
    )
    product = session.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    # Ordena os modelos por semelhança (melhor primeiro).
    product.matches.sort(key=lambda m: m.final_score, reverse=True)
    return product
