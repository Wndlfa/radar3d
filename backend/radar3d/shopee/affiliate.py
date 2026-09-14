"""Fonte Shopee via Affiliate Open Platform (API GraphQL oficial).

Endpoint BR: https://open-api.affiliate.shopee.com.br/graphql (sempre POST).
Auth por assinatura: SHA256(appId + timestamp + payload + secret), no header
Authorization: SHA256 Credential=<appId>, Timestamp=<ts>, Signature=<sign>.

NOTA: validar campos/assinatura com credenciais reais (como foi feito no Cults);
requer conta de afiliado aprovada. Ver docs/fontes.md.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.shopee.base import ShopeeProduct, ShopeeSource

_ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"

_QUERY = """
query ($kw: String!, $limit: Int!) {
  productOfferV2(keyword: $kw, limit: $limit, sortType: 2) {
    nodes {
      itemId productName offerLink productLink imageUrl
      priceMin sales ratingStar shopName
    }
  }
}
"""


class AffiliateShopeeSource(ShopeeSource):
    name = "affiliate"

    def is_enabled(self) -> bool:
        return bool(settings.shopee_affiliate_app_id and settings.shopee_affiliate_secret)

    def _headers(self, payload: str) -> dict:
        app_id = settings.shopee_affiliate_app_id
        ts = int(time.time())
        base = f"{app_id}{ts}{payload}{settings.shopee_affiliate_secret}"
        sign = hashlib.sha256(base.encode()).hexdigest()
        return {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={app_id}, Timestamp={ts}, Signature={sign}",
        }

    def discover(self, query: str, limit: int = 50) -> Iterable[ShopeeProduct]:
        if not self.is_enabled():
            return []
        payload = json.dumps(
            {"query": _QUERY, "variables": {"kw": query, "limit": limit}}
        )
        try:
            resp = httpx.post(_ENDPOINT, content=payload, headers=self._headers(payload), timeout=20)
            resp.raise_for_status()
            nodes = (
                resp.json().get("data", {}).get("productOfferV2", {}).get("nodes", [])
                or []
            )
        except (httpx.HTTPError, ValueError):
            return []

        out: list[ShopeeProduct] = []
        for n in nodes:
            out.append(
                ShopeeProduct(
                    external_id=str(n.get("itemId")),
                    title=n.get("productName") or "",
                    # offerLink = link de afiliado (saída monetizável); productLink como fallback.
                    shopee_url=n.get("offerLink") or n.get("productLink") or "",
                    image_url=n.get("imageUrl"),
                    price_brl=float(n["priceMin"]) if n.get("priceMin") else None,
                    public_sales=n.get("sales"),
                    rating=n.get("ratingStar"),
                    shop_name=n.get("shopName"),
                )
            )
        return out
