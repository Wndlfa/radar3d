"""Registro de adapters ativos. Adicione novas fontes aqui."""

from __future__ import annotations

from radar3d.sources.base import SourceAdapter
from radar3d.sources.cults3d import Cults3DAdapter
from radar3d.sources.myminifactory import MyMiniFactoryAdapter
from radar3d.sources.thingiverse import ThingiverseAdapter

ALL_ADAPTERS: list[SourceAdapter] = [
    Cults3DAdapter(),
    ThingiverseAdapter(),
    MyMiniFactoryAdapter(),
]


def enabled_adapters() -> list[SourceAdapter]:
    return [a for a in ALL_ADAPTERS if a.is_enabled()]
