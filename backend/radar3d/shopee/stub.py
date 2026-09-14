"""Fonte Shopee mock — gera produtos determinísticos para testar o coletor
sem credenciais. As vendas variam a cada dia para as tendências evoluírem.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import date

from radar3d.shopee.base import ShopeeProduct, ShopeeSource


class StubShopeeSource(ShopeeSource):
    name = "stub"

    def is_enabled(self) -> bool:
        return True

    def discover(self, query: str, limit: int = 50) -> Iterable[ShopeeProduct]:
        # "Crescimento" diário: vendas sobem um pouco a cada dia do ano.
        day = date.today().timetuple().tm_yday
        out: list[ShopeeProduct] = []
        for i in range(min(limit, 5)):
            seed = f"{query}-{i}"
            h = int(hashlib.sha256(seed.encode()).hexdigest()[:6], 16)
            base_sales = 200 + (h % 500)
            out.append(
                ShopeeProduct(
                    external_id=f"stub-{hashlib.sha256(seed.encode()).hexdigest()[:10]}",
                    title=f"{query} modelo {i + 1}",
                    shopee_url="https://shopee.com.br/exemplo",
                    image_url=None,
                    price_brl=round(29.9 + (h % 70), 2),
                    public_sales=base_sales + day * (1 + i),  # cresce com o dia
                    rating=round(4.0 + (h % 10) / 10, 1),
                    shop_name=f"Loja {chr(65 + (h % 5))}",
                    competitors=1 + (h % 12),
                )
            )
        return out
