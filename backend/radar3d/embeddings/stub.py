"""Provider stub: vetores determinísticos por hash, sem torch.

Serve para rodar o pipeline em qualquer imagem (alpine/API) sem baixar modelos.
Os scores resultantes NÃO são semânticos — use local_clip para testar de verdade.
"""

from __future__ import annotations

import hashlib
import random

from radar3d.embeddings.base import EmbeddingProvider

DIM = 512


def _vec(seed: str) -> list[float]:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    rng = random.Random(int(h[:16], 16))
    return [rng.uniform(-1, 1) for _ in range(DIM)]


class StubProvider(EmbeddingProvider):
    dim = DIM

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [_vec("text:" + (t or "")) for t in texts]

    def embed_image_urls(self, urls: list[str | None]) -> list[list[float] | None]:
        return [_vec("img:" + u) if u else None for u in urls]
