"""Planos e entitlements. Ver docs/regras-de-negocio.md §10."""

from __future__ import annotations

PLANS = ("free", "pro", "business")

# Recursos por plano.
FEATURES = {
    "free": {"commercial_filter": False, "export": False, "api": False},
    "pro": {"commercial_filter": True, "export": True, "api": False},
    "business": {"commercial_filter": True, "export": True, "api": True},
}


def can(plan: str, feature: str) -> bool:
    return FEATURES.get(plan, FEATURES["free"]).get(feature, False)
