"""Fonte Shopee via Apify (actor de Shopee Affiliate, pago por resultado).

Ponte enquanto a conta de afiliado não é aprovada — o actor puxa da mesma API
oficial. Custo ~US$ 0,0002–0,0009 por produto (ver docs/fontes.md).

Roda o actor sincronamente e lê os itens do dataset:
  POST /v2/acts/{actor}/run-sync-get-dataset-items?token=...

NOTA: nomes de campo do actor validar com token real (como no Cults).
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.shopee.base import ShopeeProduct, ShopeeSource

_API = "https://api.apify.com/v2"


def _first(d: dict, *keys):
    for k in keys:
        if d.get(k) not in (None, ""):
            return d[k]
    return None


class ApifyShopeeSource(ShopeeSource):
    name = "apify"

    def is_enabled(self) -> bool:
        return bool(settings.apify_token)

    def discover(self, query: str, limit: int = 50) -> Iterable[ShopeeProduct]:
        if not self.is_enabled():
            return []

        url = f"{_API}/acts/{settings.apify_shopee_actor}/run-sync-get-dataset-items"
        payload: dict = {"mode": "products", "keyword": query, "maxResults": limit}
        # Este actor é wrapper da API oficial de afiliados: repassa appId/secret
        # quando existirem. (Com credenciais de afiliado, prefira SHOPEE_SOURCE=affiliate.)
        if settings.shopee_affiliate_app_id:
            payload["appId"] = settings.shopee_affiliate_app_id
        if settings.shopee_affiliate_secret:
            payload["appSecret"] = settings.shopee_affiliate_secret
        try:
            resp = httpx.post(
                url,
                params={"token": settings.apify_token},
                json=payload,
                timeout=180,  # roda o actor sincronamente
            )
            resp.raise_for_status()
            items = resp.json() or []
        except (httpx.HTTPError, ValueError):
            return []

        out: list[ShopeeProduct] = []
        for it in items:
            price = _first(it, "priceMin", "price")
            out.append(
                ShopeeProduct(
                    external_id=str(_first(it, "itemId", "id") or ""),
                    title=_first(it, "productName", "name") or "",
                    shopee_url=_first(it, "offerLink", "productLink", "url") or "",
                    image_url=_first(it, "imageUrl", "image"),
                    price_brl=float(price) if price else None,
                    public_sales=_first(it, "sales", "historicalSold"),
                    rating=_first(it, "ratingStar", "rating"),
                    shop_name=_first(it, "shopName", "shop"),
                )
            )
        return [p for p in out if p.external_id]
