"""Healthcheck e status das fontes."""

from __future__ import annotations

from fastapi import APIRouter

from radar3d.sources.registry import ALL_ADAPTERS

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/sources")
def sources() -> dict:
    """Quais fontes estão ativas (têm credenciais)."""
    return {
        "sources": [
            {"platform": a.platform, "enabled": a.is_enabled()} for a in ALL_ADAPTERS
        ]
    }
