"""Adapter Thingiverse — API REST oficial (ver docs/fontes.md).

Auth: App Token via Bearer. Busca: GET /search/{term}?type=things.
A licença NÃO vem na busca — buscamos o detalhe GET /things/{id} por item.

NOTA: nomes de campo baseados na doc pública; validar com token real via
radar3d.scripts.test_source e ajustar se necessário (como foi feito no Cults).
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.sources.base import RawModel, SourceAdapter

_BASE = "https://api.thingiverse.com"


class ThingiverseAdapter(SourceAdapter):
    platform = "thingiverse"

    def is_enabled(self) -> bool:
        return bool(settings.thingiverse_app_token)

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {settings.thingiverse_app_token}"}

    def _license_for(self, client: httpx.Client, thing_id: str, hit: dict) -> str:
        # Alguns retornos já trazem `license` na busca; senão, detalhe da thing.
        if hit.get("license"):
            return str(hit["license"])
        try:
            resp = client.get(f"{_BASE}/things/{thing_id}", headers=self._headers())
            resp.raise_for_status()
            return str(resp.json().get("license") or "")
        except (httpx.HTTPError, ValueError):
            return ""

    def _images_for(self, client: httpx.Client, thing_id: str, limit: int = 6) -> list[str]:
        """GET /things/{id}/images -> uma URL por imagem (prefere tamanho grande)."""
        try:
            resp = client.get(f"{_BASE}/things/{thing_id}/images", headers=self._headers())
            resp.raise_for_status()
            images = resp.json() or []
        except (httpx.HTTPError, ValueError):
            return []

        urls: list[str] = []
        for im in images[:limit]:
            sizes = im.get("sizes") or []
            chosen = None
            # preferência: display/large > preview/featured > thumb/large
            for want_type, want_size in (
                ("display", "large"), ("preview", "featured"), ("thumb", "large"),
            ):
                for s in sizes:
                    if s.get("type") == want_type and s.get("size") == want_size:
                        chosen = s.get("url")
                        break
                if chosen:
                    break
            if not chosen and sizes:
                chosen = sizes[0].get("url")
            if chosen:
                urls.append(chosen)
        return urls

    def search(self, query: str, limit: int = 20) -> Iterable[RawModel]:
        if not self.is_enabled():
            return []

        try:
            with httpx.Client(timeout=20) as client:
                resp = client.get(
                    f"{_BASE}/search/{query}",
                    params={"type": "things", "per_page": limit},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                hits = resp.json().get("hits", []) or []

                results: list[RawModel] = []
                for h in hits:
                    tid = str(h.get("id"))
                    imgs = self._images_for(client, tid)
                    results.append(
                        RawModel(
                            platform=self.platform,
                            external_id=tid,
                            title=h.get("name") or "",
                            source_url=h.get("public_url") or h.get("url") or "",
                            creator=(h.get("creator") or {}).get("name"),
                            thumbnail_url=h.get("thumbnail") or (imgs[0] if imgs else None),
                            image_urls=imgs,
                            is_paid=False,  # Thingiverse é gratuito
                            downloads=h.get("download_count"),
                            license_raw=self._license_for(client, tid, h),
                        )
                    )
                return results
        except (httpx.HTTPError, ValueError):
            return []
