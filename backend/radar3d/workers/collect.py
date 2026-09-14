"""Coleta diária da Shopee: descobre produtos, salva e registra snapshots.

Regra de custo: só ENRIQUECE (CLIP, caro) produtos NOVOS. Produtos já
conhecidos recebem apenas atualização de métricas + um snapshot (barato) —
é isso que alimenta as tendências dia/semana/mês sem re-rodar o matching.
"""

from __future__ import annotations

from redis import Redis
from rq import Queue
from sqlalchemy import select

from radar3d.config import settings
from radar3d.db import SessionLocal
from radar3d.models import Product, ProductSnapshot
from radar3d.shopee.factory import get_shopee_source


def _enqueue_enrichment(product_id: str) -> None:
    from radar3d.workers.tasks import enrich_product

    conn = Redis.from_url(settings.redis_url)
    Queue("radar3d", connection=conn).enqueue(enrich_product, product_id)


def collect_shopee(queries: list[str] | None = None) -> dict:
    """Roda uma rodada de coleta. Retorna contagem de novos/atualizados."""
    source = get_shopee_source()
    if not source.is_enabled():
        return {"source": source.name, "enabled": False, "new": 0, "updated": 0}

    queries = queries or settings.shopee_queries_list
    session = SessionLocal()
    new = updated = 0
    new_ids: list[str] = []
    try:
        for query in queries:
            for sp in source.discover(query, limit=50):
                if not sp.external_id:
                    continue
                product = session.scalars(
                    select(Product).where(Product.external_id == sp.external_id)
                ).first()
                is_new = product is None
                if is_new:
                    product = Product(external_id=sp.external_id)
                    session.add(product)

                # atualiza métricas atuais
                product.title = sp.title
                product.shopee_url = sp.shopee_url
                product.image_url = sp.image_url
                product.price_brl = sp.price_brl
                product.public_sales = sp.public_sales
                product.rating = sp.rating
                product.shop_name = sp.shop_name
                product.competitors = sp.competitors
                product.trend = "coletado"
                session.flush()

                # snapshot (série temporal para as tendências)
                session.add(
                    ProductSnapshot(
                        product_id=product.id,
                        price_brl=sp.price_brl,
                        public_sales=sp.public_sales,
                        competitors=sp.competitors,
                        rating=sp.rating,
                    )
                )

                if is_new:
                    new += 1
                    new_ids.append(product.id)
                else:
                    updated += 1

        session.commit()

        # Enriquece só os produtos NOVOS desta rodada (CLIP roda 1x por produto).
        for pid in new_ids:
            _enqueue_enrichment(pid)

        return {"source": source.name, "enabled": True, "new": new, "updated": updated}
    finally:
        session.close()
