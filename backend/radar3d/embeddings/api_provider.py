"""Provider de embeddings por API (CLIP multimodal hospedado).

Não usa torch → o worker roda na imagem leve (alpine) e o custo em produção
cai muito. Default: Jina CLIP v2 (texto e imagem no MESMO espaço; a API busca a
imagem pela URL, sem download local). Ver docs/plano §Fase 3.

Formato da requisição (compatível com Jina /v1/embeddings):
  {"model": "...", "dimensions": 512, "input": [{"text": "..."}, {"image": "url"}]}
"""

from __future__ import annotations

import httpx

from radar3d.config import settings
from radar3d.embeddings.base import EmbeddingProvider


class ApiEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        if not settings.embeddings_api_key:
            raise RuntimeError("EMBEDDINGS_API_KEY não configurada para o provider 'api'.")
        self.dim = settings.embeddings_api_dim

    def _embed(self, inputs: list[dict], task: str = "") -> list[list[float] | None]:
        """Envia inputs já montados ({text|image}) e devolve vetores na ordem."""
        if not inputs:
            return []
        body: dict = {
            "model": settings.embeddings_api_model,
            "dimensions": self.dim,
            "input": inputs,
        }
        if task:  # task só se aplica a texto; imagem manda sem task
            body["task"] = task
        try:
            resp = httpx.post(
                settings.embeddings_api_url,
                headers={"Authorization": f"Bearer {settings.embeddings_api_key}"},
                json=body,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
        except (httpx.HTTPError, ValueError):
            return [None] * len(inputs)
        # A resposta pode vir fora de ordem — reordena por `index`.
        out: list[list[float] | None] = [None] * len(inputs)
        for item in data:
            idx = item.get("index")
            if isinstance(idx, int) and 0 <= idx < len(inputs):
                out[idx] = item.get("embedding")
        return out

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vecs = self._embed([{"text": t or " "} for t in texts], task=settings.embeddings_api_task)
        # texto sempre deve ter vetor; se a API falhar, devolve zeros do tamanho certo
        return [v if v is not None else [0.0] * self.dim for v in vecs]

    def embed_image_urls(self, urls: list[str | None]) -> list[list[float] | None]:
        valid = [(i, u) for i, u in enumerate(urls) if u]
        vecs = self._embed([{"image": u} for _, u in valid])
        out: list[list[float] | None] = [None] * len(urls)
        for (i, _), vec in zip(valid, vecs):
            out[i] = vec
        return out
