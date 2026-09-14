"""Testa uma fonte real rapidamente (valida credenciais + query).

Uso:
  python -m radar3d.scripts.test_source "controller stand"
  python -m radar3d.scripts.test_source "controller stand" cults3d

Mostra os primeiros resultados ou avisa se a fonte está desativada (sem credenciais).
"""

from __future__ import annotations

import sys

from radar3d.domain.licenses import SEAL, classify_license
from radar3d.sources.registry import ALL_ADAPTERS


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python -m radar3d.scripts.test_source "<busca>" [plataforma]')
        raise SystemExit(2)

    query = sys.argv[1]
    only = sys.argv[2].lower() if len(sys.argv) > 2 else None

    adapters = [a for a in ALL_ADAPTERS if only is None or a.platform == only]
    if not adapters:
        print(f"Nenhum adapter para '{only}'.")
        return

    for adapter in adapters:
        print(f"\n=== {adapter.platform} ===")
        if not adapter.is_enabled():
            print("DESATIVADO — faltam credenciais no .env (ver docs/fontes.md).")
            continue

        results = list(adapter.search(query, limit=5))
        if not results:
            print("Sem resultados (ou falha de rede/credencial/query).")
            continue

        for r in results:
            verdict = classify_license(r.platform, r.license_raw)
            seal = SEAL[verdict.tier]
            paid = f"pago" if r.is_paid else "grátis"
            print(f"  {seal} {r.title[:60]!r} · {paid} · lic='{r.license_raw}'")
            print(f"      {r.source_url}")


if __name__ == "__main__":
    main()
