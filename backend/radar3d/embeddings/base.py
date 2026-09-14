"""Contrato de um provedor de embeddings.

CLIP coloca texto e imagem no MESMO espaço, então dá para comparar foto do
anúncio com render do STL (visual) e título com nome do modelo (texto).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    dim: int

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Um vetor por texto (mesma ordem)."""

    @abstractmethod
    def embed_image_urls(self, urls: list[str | None]) -> list[list[float] | None]:
        """Um vetor por URL de imagem; None quando a URL falha/está vazia."""
