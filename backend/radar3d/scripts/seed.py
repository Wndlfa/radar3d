"""Popula dados de demonstração para ver o pipeline sem fontes reais.

Uso: python -m radar3d.scripts.seed
Cria 1 produto Shopee curado + modelos de exemplo já classificados e casados,
espelhando o exemplo da proposta (organizador de controles).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from radar3d.db import SessionLocal
from radar3d.domain.licenses import classify_license
from radar3d.domain.matching import combine
from radar3d.models import Model3D, Product, ProductModelMatch, ProductSnapshot


_DEMO_TITLE = "Organizador de controles para videogame"
_DEMO_EXT_IDS = ["demo-1", "demo-2", "demo-3"]


def main() -> None:
    session = SessionLocal()
    try:
        # Idempotente: remove dados de demo anteriores (não toca em dados reais).
        for p in session.scalars(
            select(Product).where(Product.title == _DEMO_TITLE)
        ).all():
            session.delete(p)  # cascade remove snapshots e matches
        for m in session.scalars(
            select(Model3D).where(
                Model3D.platform == "cults3d", Model3D.external_id.in_(_DEMO_EXT_IDS)
            )
        ).all():
            session.delete(m)
        session.commit()

        product = Product(
            title="Organizador de controles para videogame",
            description="Suporte modular para controles de videogame.",
            image_url="https://example.com/produto.jpg",
            price_brl=49.90,
            public_sales=720,
            trend="crescendo",
            rating=4.8,
            shop_name="Loja Exemplo",
            competitors=9,
            shopee_url="https://shopee.com.br/exemplo",
        )
        session.add(product)
        session.flush()

        # Histórico de vendas (snapshots) para as tendências mostrarem "em alta".
        now = datetime.now(timezone.utc)
        for days_ago, sales in [(30, 300), (14, 430), (7, 560), (1, 690), (0, 720)]:
            session.add(
                ProductSnapshot(
                    product_id=product.id,
                    price_brl=product.price_brl,
                    public_sales=sales,
                    competitors=product.competitors,
                    rating=product.rating,
                    captured_at=now - timedelta(days=days_ago),
                )
            )

        demo_models = [
            dict(platform="cults3d", external_id="demo-1", title="Universal Gamepad Holder",
                 creator="maker_a", source_url="https://cults3d.com/en/demo-1",
                 is_paid=True, price_brl=18.0, downloads=1500,
                 license_raw="Cults Commercial Use", visual=0.82, text=0.80),
            dict(platform="cults3d", external_id="demo-2", title="Modular Controller Stand",
                 creator="maker_b", source_url="https://cults3d.com/en/demo-2",
                 is_paid=True, price_brl=None, downloads=900,
                 license_raw="Subscription commercial", visual=0.89, text=0.72),
            dict(platform="cults3d", external_id="demo-3", title="Game Controller Stand",
                 creator="maker_c", source_url="https://cults3d.com/en/demo-3",
                 is_paid=False, price_brl=None, downloads=12000,
                 license_raw="Personal use only", visual=0.96, text=0.90),
        ]

        for m in demo_models:
            verdict = classify_license(m["platform"], m["license_raw"], m["title"])
            model = Model3D(
                platform=m["platform"], external_id=m["external_id"], title=m["title"],
                creator=m["creator"], source_url=m["source_url"], is_paid=m["is_paid"],
                price_brl=m["price_brl"], downloads=m["downloads"],
                license_tier=verdict.tier.value, license_raw=verdict.raw,
                license_reason=verdict.reason,
                possible_protected_ip=verdict.possible_protected_ip,
                license_checked_at=datetime.now(timezone.utc),
            )
            session.add(model)
            session.flush()

            result = combine(visual=m["visual"], text=m["text"], feature=0.5)
            session.add(ProductModelMatch(
                product_id=product.id, model_id=model.id,
                visual_score=result.visual_score, text_score=result.text_score,
                feature_score=result.feature_score, final_score=result.final_score,
                match_level=int(result.level),
            ))

        session.commit()
        print(f"Seed criado. Produto: {product.id}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
