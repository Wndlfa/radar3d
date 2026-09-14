"""Adapter Cults3D — API GraphQL oficial (âncora do MVP, ver docs/fontes.md).

Endpoint: https://cults3d.com/graphql
Auth: HTTP Basic (usuário + API key).
A API NÃO expõe o arquivo 3D — perfeito para a R1.

NOTA: o schema GraphQL exato deve ser validado no GraphiQL oficial antes de
confiar nos nomes de campo abaixo. Rate limit reportado (~60 req/30s, ~500/dia)
exige backoff — implementar antes de produção.
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.sources.base import RawModel, SourceAdapter

_ENDPOINT = "https://cults3d.com/graphql"

# Schema real da API GraphQL do Cults3D (validado via docs/exemplos públicos).
# Observações: `name`/`url` exigem `locale`; busca é `creationsSearchBatch` com
# `results` aninhado; `price` exige `currency`.
_SEARCH_QUERY = """
query Search($q: String!, $limit: Int!) {
  creationsSearchBatch(query: $q, limit: $limit) {
    total
    results {
      id
      name(locale: EN)
      shortUrl
      illustrationImageUrl
      illustrations { imageUrl }
      downloadsCount
      price(currency: USD) { cents }
      creator { nick }
      license { name(locale: EN) }
    }
  }
}
"""


class Cults3DAdapter(SourceAdapter):
    platform = "cults3d"

    def is_enabled(self) -> bool:
        return bool(settings.cults3d_username and settings.cults3d_api_key)

    def search(self, query: str, limit: int = 20) -> Iterable[RawModel]:
        if not self.is_enabled():
            return []

        auth = (settings.cults3d_username, settings.cults3d_api_key)
        try:
            resp = httpx.post(
                _ENDPOINT,
                json={"query": _SEARCH_QUERY, "variables": {"q": query, "limit": limit}},
                auth=auth,
                timeout=20,
            )
            resp.raise_for_status()
            batch = resp.json().get("data", {}).get("creationsSearchBatch") or {}
            data = batch.get("results", []) or []
        except (httpx.HTTPError, ValueError):
            # Falha de fonte não derruba o coletor — degradar silenciosamente.
            return []

        results: list[RawModel] = []
        for c in data:
            cents = (c.get("price") or {}).get("cents")
            imgs = [
                i.get("imageUrl")
                for i in (c.get("illustrations") or [])
                if i.get("imageUrl")
            ]
            main = c.get("illustrationImageUrl")
            if main and main not in imgs:
                imgs.insert(0, main)
            results.append(
                RawModel(
                    platform=self.platform,
                    external_id=str(c.get("id")),
                    title=c.get("name") or "",
                    source_url=c.get("shortUrl") or "",
                    creator=(c.get("creator") or {}).get("nick"),
                    thumbnail_url=main or (imgs[0] if imgs else None),
                    image_urls=imgs,
                    is_paid=bool(cents),
                    price_brl=None,  # price vem em USD cents; conversão BRL depois
                    downloads=c.get("downloadsCount"),
                    license_raw=(c.get("license") or {}).get("name") or "",
                )
            )
        return results
