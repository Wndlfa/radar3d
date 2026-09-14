"""Harness de avaliação do matching contra rótulos gold (Fase 3).

Roda o pipeline real (busca + embeddings + score) para cada caso do
dataset.json, junta as previsões aos rótulos por source_url e reporta:
  - score médio por classe gold (o score separa relevante de irrelevante?)
  - qualidade de ranking (AUC: relevante acima de irrelevante)
  - varredura de limiar recomendando o corte "relevante" (gold exact/similar)

Uso: python -m radar3d.eval.evaluate
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from sqlalchemy import select

from radar3d.db import SessionLocal
from radar3d.models import Model3D, Product, ProductModelMatch
from radar3d.workers.tasks import enrich_product

GOLD_LEVEL = {"exact": 1, "similar": 2, "alternative": 3, "unrelated": 4}
_DATASET = Path(__file__).with_name("dataset.json")


def _predictions_by_url(session, product_id: str) -> dict[str, float]:
    rows = session.execute(
        select(Model3D.source_url, ProductModelMatch.final_score)
        .join(ProductModelMatch, ProductModelMatch.model_id == Model3D.id)
        .where(ProductModelMatch.product_id == product_id)
    ).all()
    return {url: score for url, score in rows}


def _auc(pos: list[float], neg: list[float]) -> float:
    """Fração de pares (pos, neg) com pos > neg. 1.0 = ranking perfeito."""
    if not pos or not neg:
        return float("nan")
    wins = sum(1 for p in pos for n in neg if p > n) + 0.5 * sum(
        1 for p in pos for n in neg if p == n
    )
    return wins / (len(pos) * len(neg))


def _best_threshold(scored: list[tuple[float, bool]]) -> tuple[float, float, float, float]:
    """Corte que maximiza F1 para 'relevante'. Retorna (thr, precision, recall, f1)."""
    best = (0.0, 0.0, 0.0, -1.0)
    for thr_src, _ in scored:
        thr = thr_src
        tp = sum(1 for s, rel in scored if s >= thr and rel)
        fp = sum(1 for s, rel in scored if s >= thr and not rel)
        fn = sum(1 for s, rel in scored if s < thr and rel)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        if f1 > best[3]:
            best = (thr, prec, rec, f1)
    return best


def main() -> None:
    data = json.loads(_DATASET.read_text(encoding="utf-8"))
    session = SessionLocal()
    try:
        all_scored: list[tuple[float, bool]] = []
        by_gold: dict[str, list[float]] = {}

        for case in data["cases"]:
            product = Product(**case["product"])
            session.add(product)
            session.commit()
            try:
                enrich_product(product.id)
                preds = _predictions_by_url(session, product.id)

                print(f"\n=== caso: {case['id']} ===")
                rows = []
                for lab in case["labels"]:
                    url = lab["source_url"]
                    gold = lab["gold"]
                    score = preds.get(url)
                    if score is None:
                        continue  # modelo não veio na busca desta vez
                    rows.append((score, gold, lab.get("note", "")))
                    by_gold.setdefault(gold, []).append(score)
                    all_scored.append((score, GOLD_LEVEL[gold] <= 2))

                rows.sort(reverse=True)
                print("score  gold         nota")
                for score, gold, note in rows:
                    print(f"{score:.3f}  {gold:11}  {note}")
            finally:
                session.delete(session.get(Product, product.id))
                session.commit()

        print("\n=== score médio por classe gold ===")
        for gold in ["exact", "similar", "alternative", "unrelated"]:
            vs = by_gold.get(gold, [])
            if vs:
                print(f"{gold:11} n={len(vs)} média={statistics.mean(vs):.3f} "
                      f"min={min(vs):.3f} max={max(vs):.3f}")

        pos = by_gold.get("exact", []) + by_gold.get("similar", [])
        neg = by_gold.get("alternative", []) + by_gold.get("unrelated", [])
        print(f"\nAUC (relevante=exact/similar acima de alternative/unrelated): "
              f"{_auc(pos, neg):.3f}")

        if all_scored:
            thr, prec, rec, f1 = _best_threshold(all_scored)
            print(f"Melhor corte 'relevante': score>={thr:.3f} "
                  f"(precision={prec:.2f} recall={rec:.2f} F1={f1:.2f})")
    finally:
        session.close()


if __name__ == "__main__":
    main()
