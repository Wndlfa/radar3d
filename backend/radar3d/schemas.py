"""Schemas Pydantic (contrato da API → tipos consumidos pelo front)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: str
    title: str
    creator: str | None
    thumbnail_url: str | None
    source_url: str
    is_paid: bool
    price_brl: float | None
    downloads: int | None
    rating: float | None
    license_tier: str
    license_raw: str | None
    possible_protected_ip: bool
    license_checked_at: datetime | None


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    final_score: float
    match_level: int
    model: ModelOut


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    image_url: str | None
    price_brl: float | None
    public_sales: int | None
    trend: str | None
    rating: float | None
    shop_name: str | None
    competitors: int | None
    shopee_url: str | None
    collected_at: datetime
    # Resumo de licença dos modelos encontrados (responde "posso vender?" na lista)
    models_count: int = 0
    commercial_available: bool = False
    best_license_tier: str | None = None
    protected_ip: bool = False


class ProductDetailOut(ProductOut):
    matches: list[MatchOut] = []


class TrendingOut(ProductOut):
    """Produto em alta num período, com o crescimento medido por snapshots."""

    period: str
    growth_abs: int | None  # variação de vendas públicas na janela
    growth_pct: float | None
    first_sales: int | None
    last_sales: int | None


class SnapshotInput(BaseModel):
    """Datapoint de coleta. Campos omitidos mantêm o valor atual do produto."""

    price_brl: float | None = None
    public_sales: int | None = None
    competitors: int | None = None
    rating: float | None = None


class ProductCreate(BaseModel):
    """Entrada de produto Shopee curado manualmente (MVP, ver docs/fontes.md)."""

    title: str
    description: str | None = None
    image_url: str | None = None
    price_brl: float | None = None
    public_sales: int | None = None
    trend: str | None = None
    rating: float | None = None
    shop_name: str | None = None
    competitors: int | None = None
    shopee_url: str | None = None
