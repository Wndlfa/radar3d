"""Escolhe a fonte Shopee por configuração."""

from __future__ import annotations

from functools import lru_cache

from radar3d.config import settings
from radar3d.shopee.base import ShopeeSource


@lru_cache(maxsize=1)
def get_shopee_source() -> ShopeeSource:
    src = settings.shopee_source.lower()

    if src == "affiliate":
        from radar3d.shopee.affiliate import AffiliateShopeeSource

        return AffiliateShopeeSource()

    if src == "apify":
        from radar3d.shopee.apify import ApifyShopeeSource

        return ApifyShopeeSource()

    from radar3d.shopee.stub import StubShopeeSource

    return StubShopeeSource()
