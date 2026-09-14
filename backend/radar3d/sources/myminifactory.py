"""Adapter MyMiniFactory — API REST v2 oficial (ver docs/fontes.md).

Auth: API key via query param `key`. Busca: GET /api/v2/search?q=...
Resultados em `items[]`. A licença vem em `license` (string) ou `licenses[]`.

NOTA: validar campos com key real via radar3d.scripts.test_source.
"""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from radar3d.config import settings
from radar3d.sources.base import RawModel, SourceAdapter

_BASE = "https://www.myminifactory.com/api/v2"


def _img_url(v) -> str | None:
    """Cada variante pode ser string ou objeto {url, width, height}."""
    if isinstance(v, dict):
        return v.get("url")
    return v if isinstance(v, str) else None


def _image_urls(images) -> list[str]:
    """images[] = [{thumbnail:{url,..}, standard:{..}, original:{..}}, ...].

    Uma URL por imagem (prefere standard, senão thumbnail/original).
    """
    urls: list[str] = []
    for img in images or []:
        if isinstance(img, dict):
            u = None
            for key in ("standard", "thumbnail", "original"):
                if img.get(key):
                    u = _img_url(img[key])
                    break
            u = u or _img_url(img.get("url"))
        else:
            u = img if isinstance(img, str) else None
        if u:
            urls.append(u)
    return urls


def _license_raw(item: dict) -> str:
    if item.get("license"):
        return str(item["license"])
    parts = []
    for lic in item.get("licenses", []) or []:
        if isinstance(lic, dict):
            parts.append(str(lic.get("value") or lic.get("name") or lic.get("type") or ""))
        else:
            parts.append(str(lic))
    return " ".join(p for p in parts if p)


class MyMiniFactoryAdapter(SourceAdapter):
    platform = "myminifactory"

    def is_enabled(self) -> bool:
        return bool(settings.myminifactory_api_key)

    def search(self, query: str, limit: int = 20) -> Iterable[RawModel]:
        if not self.is_enabled():
            return []

        try:
            resp = httpx.get(
                f"{_BASE}/search",
                params={
                    "q": query,
                    "per_page": limit,
                    "key": settings.myminifactory_api_key,
                },
                timeout=20,
            )
            resp.raise_for_status()
            items = resp.json().get("items", []) or []
        except (httpx.HTTPError, ValueError):
            return []

        results: list[RawModel] = []
        for it in items:
            designer = it.get("designer") or {}
            price = it.get("price")
            imgs = _image_urls(it.get("images"))
            results.append(
                RawModel(
                    platform=self.platform,
                    external_id=str(it.get("id")),
                    title=it.get("name") or "",
                    source_url=it.get("url") or "",
                    creator=designer.get("name") or designer.get("username"),
                    thumbnail_url=imgs[0] if imgs else None,
                    image_urls=imgs,
                    is_paid=bool(price),
                    price_brl=None,
                    downloads=it.get("download_count") or it.get("total_downloads"),
                    license_raw=_license_raw(it),
                )
            )
        return results
