"""Embeddings — atrás de uma interface para trocar self-hosted <-> API.

Provider escolhido por settings.embeddings_provider:
  - "stub"       : vetores determinísticos, sem dependências pesadas (alpine/API).
  - "local_clip" : CLIP self-hosted (roda no worker Debian). Ver docs/plano §4/Fase 3.
  - "api"        : (futuro) provedor externo por HTTP.
"""

from __future__ import annotations

import math


def cosine(a: list[float] | None, b: list[float] | None) -> float:
    """Similaridade de cosseno. Retorna 0.0 se algum vetor faltar."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
