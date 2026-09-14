"""Tradutor por glossário de domínio PT->EN (leve, sem modelo, sem RAM).

MT genérico erra o jargão de impressão 3D/games ("suporte controle" ->
"control support" em vez de "controller stand"). Aqui mapeamos os termos do
domínio para o idioma real das bibliotecas, gerando uma consulta de palavras-
chave concisa — melhor para a busca das APIs e para o match textual.

Cresce conforme observamos títulos reais. Termo desconhecido é mantido como está.
"""

from __future__ import annotations

import re

from radar3d.translate import looks_portuguese
from radar3d.translate.base import Translator

# Frases (aplicadas primeiro, mais longas antes) — capturam idiomas do domínio.
_PHRASES = [
    ("cabeça de dragão", "dragon head"),
    ("controle de videogame", "video game controller"),
    ("controles de videogame", "video game controllers"),
    ("porta controle", "controller holder"),
    ("suporte de controle", "controller stand"),
    ("suporte para controle", "controller stand"),
]

# Palavras. Chave = PT (singular/plural), valor = EN.
_WORDS = {
    "suporte": "stand", "suportes": "stands",
    "controle": "controller", "controles": "controllers",
    "cabeça": "head", "dragão": "dragon", "dragao": "dragon",
    "organizador": "organizer", "organizadores": "organizers",
    "videogame": "video game", "videogames": "video games",
    "jogo": "game", "jogos": "games",
    "porta": "holder", "suporta": "holder",
    "fone": "headphone", "fones": "headphones", "headset": "headset",
    "celular": "phone", "telefone": "phone",
    "parede": "wall", "mesa": "desk", "vaso": "pot", "planta": "plant",
    "chaveiro": "keychain", "caixa": "box", "gancho": "hook",
    "prateleira": "shelf", "miniatura": "miniature", "boneco": "figure",
}

# Preposições/artigos a descartar (viram ruído na busca por palavra-chave).
_DROP = {"de", "da", "do", "das", "dos", "para", "com", "e", "o", "a",
         "os", "as", "em", "no", "na", "pra", "p"}


class GlossaryTranslator(Translator):
    def to_english(self, text: str) -> str:
        if not text or not looks_portuguese(text):
            return text

        t = text.lower()
        for pt, en in _PHRASES:
            t = t.replace(pt, en)

        out: list[str] = []
        for tok in re.split(r"[\s,;/]+", t):
            tok = tok.strip()
            if not tok or tok in _DROP:
                continue
            out.append(_WORDS.get(tok, tok))
        return " ".join(out) or text
