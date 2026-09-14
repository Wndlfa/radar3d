"""Modelos ORM. Ver docs/plano-de-implementacao.md §2 (modelo de dados).

Nunca armazenamos o arquivo 3D (R1) — apenas metadados públicos e links.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from radar3d.db import Base

EMBEDDING_DIM = 512  # ajustar ao modelo de embeddings escolhido na Fase 0


def _uuid() -> str:
    return str(uuid.uuid4())


class Product(Base):
    """Produto físico impresso em 3D anunciado na Shopee (dados comerciais)."""

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    external_id: Mapped[str | None] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String)
    price_brl: Mapped[float | None] = mapped_column(Float)
    public_sales: Mapped[int | None] = mapped_column(Integer)
    trend: Mapped[str | None] = mapped_column(String)  # ex.: "crescendo"
    rating: Mapped[float | None] = mapped_column(Float)
    shop_name: Mapped[str | None] = mapped_column(String)
    competitors: Mapped[int | None] = mapped_column(Integer)
    shopee_url: Mapped[str | None] = mapped_column(String)

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    matches: Mapped[list["ProductModelMatch"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class User(Base):
    """Usuário e plano (entitlements). Ver docs/regras-de-negocio.md §10."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    plan: Mapped[str] = mapped_column(String, default="free")  # free | pro | business
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UsageCounter(Base):
    """Contador de consultas por usuário/mês (limite do plano Free)."""

    __tablename__ = "usage_counters"
    __table_args__ = (
        UniqueConstraint("user_id", "period", "kind", name="uq_usage_user_period"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    period: Mapped[str] = mapped_column(String)  # "YYYY-MM"
    kind: Mapped[str] = mapped_column(String, default="query")
    count: Mapped[int] = mapped_column(Integer, default=0)


class ProductSnapshot(Base):
    """Métrica pontual de um produto no tempo — base das tendências.

    A coleta automatizada (1×/dia) insere um snapshot por produto por rodada;
    a diferença entre snapshots numa janela (dia/semana/mês) dá o crescimento.
    """

    __tablename__ = "product_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    price_brl: Mapped[float | None] = mapped_column(Float)
    public_sales: Mapped[int | None] = mapped_column(Integer)
    competitors: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Float)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class Model3D(Base):
    """Modelo encontrado em uma biblioteca (metadados públicos + link)."""

    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("platform", "external_id", name="uq_platform_ext"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    platform: Mapped[str] = mapped_column(String, index=True)  # cults3d, thingiverse...
    external_id: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    creator: Mapped[str | None] = mapped_column(String)
    thumbnail_url: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(String, nullable=False)
    is_paid: Mapped[bool] = mapped_column(default=False)
    price_brl: Mapped[float | None] = mapped_column(Float)
    downloads: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Float)

    # Licença — o campo mais importante (ver domain/licenses.py)
    license_tier: Mapped[str] = mapped_column(String, default="NAO_IDENTIFICADA")
    license_raw: Mapped[str | None] = mapped_column(Text)
    license_reason: Mapped[str | None] = mapped_column(Text)
    possible_protected_ip: Mapped[bool] = mapped_column(default=False)
    license_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    matches: Mapped[list["ProductModelMatch"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class ProductModelMatch(Base):
    """Correspondência produto ↔ modelo com scores (ver domain/matching.py)."""

    __tablename__ = "product_model_matches"
    __table_args__ = (
        UniqueConstraint("product_id", "model_id", name="uq_product_model"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id", ondelete="CASCADE"))

    visual_score: Mapped[float] = mapped_column(Float, default=0.0)
    text_score: Mapped[float] = mapped_column(Float, default=0.0)
    feature_score: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    match_level: Mapped[int] = mapped_column(Integer, default=4)

    product: Mapped[Product] = relationship(back_populates="matches")
    model: Mapped[Model3D] = relationship(back_populates="matches")


class Embedding(Base):
    """Vetores para busca ANN (pgvector). Um por entidade+tipo."""

    __tablename__ = "embeddings"
    __table_args__ = (
        UniqueConstraint("owner_type", "owner_id", "kind", name="uq_embedding_owner"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    owner_type: Mapped[str] = mapped_column(String)  # "product" | "model"
    owner_id: Mapped[str] = mapped_column(String, index=True)
    kind: Mapped[str] = mapped_column(String)  # "image" | "text"
    vector: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))
