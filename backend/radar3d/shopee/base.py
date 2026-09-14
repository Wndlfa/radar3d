"""Fonte de produtos da Shopee (trocável: stub / affiliate / apify)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class ShopeeProduct:
    """Produto normalizado da Shopee, antes de virar Product + snapshot."""

    external_id: str
    title: str
    shopee_url: str
    image_url: str | None = None
    price_brl: float | None = None
    public_sales: int | None = None
    rating: float | None = None
    shop_name: str | None = None
    competitors: int | None = None


class ShopeeSource(ABC):
    name: str

    @abstractmethod
    def is_enabled(self) -> bool:
        ...

    @abstractmethod
    def discover(self, query: str, limit: int = 50) -> Iterable[ShopeeProduct]:
        """Descobre produtos em alta para um termo/categoria."""
