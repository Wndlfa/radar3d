"""Provider CLIP self-hosted (sentence-transformers). Roda no worker Debian.

Importa torch/sentence-transformers só quando instanciado — assim a API alpine
(que usa o stub) nunca tenta importar torch.
"""

from __future__ import annotations

import io

import httpx

from radar3d.embeddings.base import EmbeddingProvider

_MODEL_NAME = "clip-ViT-B-32"  # texto + imagem no mesmo espaço, dim 512


class LocalClipProvider(EmbeddingProvider):
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(_MODEL_NAME)
        # get_embedding_dimension (nome novo) com fallback pro antigo.
        get_dim = getattr(
            self._model, "get_embedding_dimension", None
        ) or self._model.get_sentence_embedding_dimension
        self.dim = get_dim()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vecs = self._model.encode(
            [t or "" for t in texts], normalize_embeddings=True
        )
        return [v.tolist() for v in vecs]

    def embed_image_urls(self, urls: list[str | None]) -> list[list[float] | None]:
        """Baixa as imagens em paralelo e codifica todas num único batch.

        Ordem preservada; imagem que falhar vira None (só cai o sinal visual).
        """
        from concurrent.futures import ThreadPoolExecutor

        from PIL import Image

        def fetch(url: str | None):
            if not url:
                return None
            try:
                resp = httpx.get(url, timeout=15, follow_redirects=True)
                resp.raise_for_status()
                return Image.open(io.BytesIO(resp.content)).convert("RGB")
            except Exception:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            images = list(pool.map(fetch, urls))

        valid = [(i, im) for i, im in enumerate(images) if im is not None]
        out: list[list[float] | None] = [None] * len(urls)
        if valid:
            vecs = self._model.encode(
                [im for _, im in valid], normalize_embeddings=True, batch_size=32
            )
            for (i, _), vec in zip(valid, vecs):
                out[i] = vec.tolist()
        return out
