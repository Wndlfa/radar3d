"""Tradução PT->EN atrás de interface (trocável: none/argos/api).

Motivação: anúncios da Shopee são em português; as bibliotecas (Cults,
Thingiverse, MMF) são em inglês. Traduzir a consulta melhora TANTO a busca nas
APIs quanto o match textual — e é mais leve que carregar um 2º modelo de
embedding. Ver docs/plano §Fase 3.
"""

from __future__ import annotations

# Marcadores simples de português para não traduzir texto que já é inglês.
_PT_WORDS = {
    "de", "da", "do", "para", "com", "sem", "suporte", "controle", "cabeça",
    "videogame", "jogo", "peça", "peças", "organizador", "porta", "não",
}


def looks_portuguese(text: str) -> bool:
    t = text.lower()
    if any(c in t for c in "ãõáéíóúâêôàç"):
        return True
    tokens = set(t.replace("-", " ").split())
    return len(tokens & _PT_WORDS) >= 1
