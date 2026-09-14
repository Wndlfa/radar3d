"""Tradutor no-op (provider "none")."""

from __future__ import annotations

from radar3d.translate.base import Translator


class IdentityTranslator(Translator):
    def to_english(self, text: str) -> str:
        return text
