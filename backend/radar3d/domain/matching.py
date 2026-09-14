"""Score de correspondência e níveis. Ver docs/regras-de-negocio.md §6.

Score final = combinação ponderada de similaridade visual, textual e de
características. Pesos e limiares configuráveis (aqui, defaults iniciais a
calibrar com o conjunto rotulado — ver plano, Fase 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

# Visual é o sinal mais confiável de "é o mesmo objeto" (a foto do print parece
# o render); o nome do criador é ruidoso. Ver calibração abaixo.
WEIGHTS = {"visual": 0.6, "text": 0.25, "feature": 0.15}


class MatchLevel(IntEnum):
    EXATA = 1  # aparenta ser o mesmo modelo
    MUITO_SEMELHANTE = 2  # pequenas modificações / possível remix
    ALTERNATIVA = 3  # mesma função, design diferente
    RELACIONADO = 4  # apenas inspiração / categoria


LEVEL_LABEL = {
    MatchLevel.EXATA: "Correspondência exata",
    MatchLevel.MUITO_SEMELHANTE: "Muito semelhante",
    MatchLevel.ALTERNATIVA: "Alternativa semelhante",
    MatchLevel.RELACIONADO: "Conceito relacionado",
}

# Limiares calibrados com a distribuição real do CLIP ViT-B-32
# (ver radar3d.scripts.calibrate; busca "controller stand" no Cults3D):
#   VISUAL render×render mesma categoria: mediana 0.62, p90 0.74, máx 0.87
#   Produto×render mesmo objeto: 1.0, próximo design ~0.74; degrau claro
#   TEXTO nome×nome mesma categoria: mediana 0.72, idêntico 1.0
# Por isso os limiares são bem menores que o padrão ingênuo (0.9). Ainda são
# PROVISÓRIOS: o ajuste fino exige um conjunto rotulado foto×render (Fase 3).
_THRESHOLDS = [
    (0.80, MatchLevel.EXATA),
    (0.66, MatchLevel.MUITO_SEMELHANTE),
    (0.52, MatchLevel.ALTERNATIVA),
    (0.0, MatchLevel.RELACIONADO),
]


@dataclass(frozen=True)
class MatchResult:
    visual_score: float
    text_score: float
    feature_score: float
    final_score: float
    level: MatchLevel

    @property
    def level_label(self) -> str:
        return LEVEL_LABEL[self.level]


def combine(
    visual: float | None = None,
    text: float | None = None,
    feature: float | None = None,
) -> MatchResult:
    """Combina os sinais disponíveis, renormalizando os pesos.

    Sinais ausentes (None) são ignorados — assim um match só-textual não é
    penalizado por não ter imagem. Ex.: só `text` presente => final = text.
    """
    parts = {"visual": visual, "text": text, "feature": feature}
    present = {k: v for k, v in parts.items() if v is not None}

    if not present:
        final = 0.0
    else:
        wsum = sum(WEIGHTS[k] for k in present)
        final = sum(WEIGHTS[k] * v for k, v in present.items()) / wsum

    level = next(lvl for thr, lvl in _THRESHOLDS if final >= thr)
    return MatchResult(visual or 0.0, text or 0.0, feature or 0.0, round(final, 4), level)
