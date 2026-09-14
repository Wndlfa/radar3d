"""Calibração de matching: mostra a distribuição real de similaridade do CLIP.

Lê embeddings já guardados no banco e reporta percentis de similaridade
visual (imagem×imagem) e textual (texto×texto) entre os modelos, além de
produto×modelo quando o produto tem imagem.

Uso:
  python -m radar3d.scripts.calibrate [product_id]

Objetivo: escolher os limiares de nível (exata/muito semelhante/...) com base
em dados, não em chute. Ver docs/plano §Fase 3.
"""

from __future__ import annotations

import statistics
import sys

from sqlalchemy import select

from radar3d.db import SessionLocal
from radar3d.embeddings import cosine
from radar3d.models import Embedding, ProductModelMatch


def _percentiles(values: list[float]) -> str:
    if not values:
        return "(sem dados)"
    vs = sorted(values)

    def pct(p: float) -> float:
        i = min(len(vs) - 1, int(p * len(vs)))
        return vs[i]

    return (
        f"n={len(vs)} min={vs[0]:.3f} p25={pct(.25):.3f} "
        f"mediana={statistics.median(vs):.3f} p75={pct(.75):.3f} "
        f"p90={pct(.90):.3f} max={vs[-1]:.3f}"
    )


def main() -> None:
    session = SessionLocal()
    try:
        product_id = sys.argv[1] if len(sys.argv) > 1 else None

        if product_id:
            model_ids = [
                m.model_id
                for m in session.scalars(
                    select(ProductModelMatch).where(
                        ProductModelMatch.product_id == product_id
                    )
                ).all()
            ]
        else:
            model_ids = None

        def load(kind: str) -> dict[str, list[float]]:
            stmt = select(Embedding).where(
                Embedding.owner_type == "model", Embedding.kind == kind
            )
            rows = session.scalars(stmt).all()
            out = {}
            for r in rows:
                if model_ids is None or r.owner_id in model_ids:
                    out[r.owner_id] = list(r.vector)
            return out

        img = load("image")
        txt = load("text")

        # Distribuição par-a-par entre modelos (mesma categoria de busca).
        def pairwise(vecs: dict[str, list[float]]) -> list[float]:
            ids = list(vecs)
            sims = []
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    sims.append(cosine(vecs[ids[i]], vecs[ids[j]]))
            return sims

        print("=== Similaridade VISUAL (render × render, mesma busca) ===")
        print(_percentiles(pairwise(img)))
        print("=== Similaridade TEXTUAL (nome × nome, mesma busca) ===")
        print(_percentiles(pairwise(txt)))

        # Produto × modelos, se o produto tiver embedding de imagem.
        if product_id:
            prod_img = session.scalars(
                select(Embedding).where(
                    Embedding.owner_type == "product",
                    Embedding.owner_id == product_id,
                    Embedding.kind == "image",
                )
            ).first()
            if prod_img is not None:
                pv = list(prod_img.vector)
                sims = sorted(
                    (cosine(pv, v) for v in img.values()), reverse=True
                )
                print("\n=== Produto × modelos (VISUAL), ordenado ===")
                print(_percentiles(sims))
                print("top:", [round(s, 3) for s in sims[:8]])
            else:
                print("\n(produto sem embedding de imagem — defina image_url para calibrar o visual)")
    finally:
        session.close()


if __name__ == "__main__":
    main()
