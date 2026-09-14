"""Fonte Shopee via actor scraper do Apify (raspa páginas públicas).

Ponte para testar com dados reais sem conta de afiliado. Custa por resultado
(crédito Apify) e depende do scraping de páginas públicas (ver nota de ToS em
docs/fontes.md). Actor padrão: lergassy~shopee-scraper (mode "search", BR).

Roda o actor sincronamente e lê os itens do dataset:
  POST /v2/acts/{actor}/run-sync-get-dataset-items?token=...
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.shopee.base import ShopeeProduct, ShopeeSource

_API = "https://api.apify.com/v2"


def _first(d: dict, *keys):
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return None


class ApifyShopeeSource(ShopeeSource):
    name = "apify"

    def is_enabled(self) -> bool:
        return bool(settings.apify_token)

    def discover(self, query: str, limit: int = 50) -> Iterable[ShopeeProduct]:
        if not self.is_enabled():
            return []

        url = f"{_API}/acts/{settings.apify_shopee_actor}/run-sync-get-dataset-items"
        payload = {
            "mode": "search",
            "country": "BR",
            "searchTerms": [query],
            "maxItems": limit,
            "sortBy": "sales",
            "enrichProducts": False,
        }
        try:
            resp = httpx.post(
                url, params={"token": settings.apify_token}, json=payload, timeout=300
            )
            resp.raise_for_status()
            items = resp.json() or []
        except (httpx.HTTPError, ValueError):
            return []

        out: list[ShopeeProduct] = []
        for it in items:
            if it.get("type") not in (None, "product", "product_detail"):
                continue  # pula shop/error
            item_id = _first(it, "itemId", "id")
            if not item_id:
                continue
            price = _first(it, "price", "priceMin")
            out.append(
                ShopeeProduct(
                    external_id=str(item_id),
                    title=_first(it, "title", "name", "productName") or "",
                    shopee_url=_first(it, "url", "productLink", "offerLink") or "",
                    image_url=_first(it, "imageUrl", "image"),
                    # o actor retorna preço em centavos (899 = R$ 8,99)
                    price_brl=round(float(price) / 100, 2) if price not in (None, "") else None,
                    public_sales=_first(it, "sold", "historicalSold", "sales", "monthlySold"),
                    rating=_first(it, "rating", "ratingStar"),
                    shop_name=_first(it, "sellerName", "shopName", "location"),
                )
            )
        return out
