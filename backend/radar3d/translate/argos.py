"""Tradutor offline PT->EN via Argos Translate (CTranslate2, leve, CPU).

Baixa o pacote pt->en na primeira vez (cache em HOME=/models, persistido no
volume). Só traduz textos que parecem português (looks_portuguese).
"""

from __future__ import annotations

from radar3d.translate import looks_portuguese
from radar3d.translate.base import Translator


class ArgosTranslator(Translator):
    def __init__(self) -> None:
        import argostranslate.package
        import argostranslate.translate

        self._translate = argostranslate.translate
        installed = {
            (p.from_code, p.to_code)
            for p in argostranslate.package.get_installed_packages()
        }
        if ("pt", "en") not in installed:
            argostranslate.package.update_package_index()
            pkg = next(
                p
                for p in argostranslate.package.get_available_packages()
                if p.from_code == "pt" and p.to_code == "en"
            )
            argostranslate.package.install_from_path(pkg.download())

    def to_english(self, text: str) -> str:
        if not text or not looks_portuguese(text):
            return text
        try:
            return self._translate.translate(text, "pt", "en")
        except Exception:
            return text  # falha de tradução não quebra o pipeline
