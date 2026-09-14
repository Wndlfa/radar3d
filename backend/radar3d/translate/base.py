"""Contrato de um tradutor."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def to_english(self, text: str) -> str:
        """Traduz PT->EN. Deve retornar o próprio texto se já estiver em inglês."""
