"""Escolhe o tradutor por configuração (import preguiçoso do Argos)."""

from __future__ import annotations

from functools import lru_cache

from radar3d.config import settings
from radar3d.translate.base import Translator


@lru_cache(maxsize=1)
def get_translator() -> Translator:
    provider = settings.translate_provider.lower()

    if provider == "glossary":
        from radar3d.translate.glossary import GlossaryTranslator

        return GlossaryTranslator()

    if provider == "marian":
        from radar3d.translate.marian import MarianTranslator

        return MarianTranslator()

    if provider == "argos":
        from radar3d.translate.argos import ArgosTranslator

        return ArgosTranslator()

    from radar3d.translate.identity import IdentityTranslator

    return IdentityTranslator()
