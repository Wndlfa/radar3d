"""Tradutor PT->EN via MarianMT (transformers, modelo do HuggingFace).

Usa Helsinki-NLP/opus-mt-ROMANCE-en (línguas românicas -> inglês). transformers
e torch já vêm com o sentence-transformers, e o HF é acessível neste ambiente
(diferente do CDN do Argos). Só traduz texto que parece português.
"""

from __future__ import annotations

from radar3d.translate import looks_portuguese
from radar3d.translate.base import Translator

_MODEL = "Helsinki-NLP/opus-mt-ROMANCE-en"


class MarianTranslator(Translator):
    def __init__(self) -> None:
        from transformers import MarianMTModel, MarianTokenizer

        self._tok = MarianTokenizer.from_pretrained(_MODEL)
        self._model = MarianMTModel.from_pretrained(_MODEL)

    def to_english(self, text: str) -> str:
        if not text or not looks_portuguese(text):
            return text
        try:
            batch = self._tok([text], return_tensors="pt", truncation=True)
            generated = self._model.generate(**batch, max_new_tokens=64)
            return self._tok.decode(generated[0], skip_special_tokens=True)
        except Exception:
            return text  # falha de tradução não quebra o pipeline
