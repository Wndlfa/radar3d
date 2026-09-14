"""Escolhe o provider por configuração. Import preguiçoso do CLIP."""

from __future__ import annotations

from functools import lru_cache

from radar3d.config import settings
from radar3d.embeddings.base import EmbeddingProvider


@lru_cache(maxsize=1)
def get_provider() -> EmbeddingProvider:
    provider = settings.embeddings_provider.lower()

    if provider == "local_clip":
        from radar3d.embeddings.local_clip import LocalClipProvider

        return LocalClipProvider()

    if provider == "api":
        from radar3d.embeddings.api_provider import ApiEmbeddingProvider

        return ApiEmbeddingProvider()

    from radar3d.embeddings.stub import StubProvider

    return StubProvider()
