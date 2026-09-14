"""Interface comum de adapter de fonte.

Cada biblioteca é um adapter isolado (ver docs/fontes.md). Se uma fonte cair,
não derruba as outras. Adapters NUNCA baixam o arquivo 3D (R1) — só metadados.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class RawModel:
    """Modelo normalizado que todo adapter devolve, antes de virar Model3D."""

    platform: str
    external_id: str
    title: str
    source_url: str
    creator: str | None = None
    thumbnail_url: str | None = None  # imagem de capa (para a UI)
    image_urls: list[str] = field(default_factory=list)  # todas, para matching visual
    is_paid: bool = False
    price_brl: float | None = None
    downloads: int | None = None
    rating: float | None = None
    license_raw: str = ""  # texto original — o classificador decide a faixa
    tags: list[str] = field(default_factory=list)
    description: str = ""


class SourceAdapter(ABC):
    """Contrato de uma fonte de modelos."""

    platform: str

    @abstractmethod
    def is_enabled(self) -> bool:
        """False quando faltam credenciais — o coletor apenas pula a fonte."""

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> Iterable[RawModel]:
        """Busca textual por modelos semelhantes ao produto."""
