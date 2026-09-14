"""Limpa os dados de catálogo/coleta (mantém usuários). Uso: python -m radar3d.scripts.reset

Remove produtos (cascade: snapshots e matches), modelos, embeddings e contadores
de uso. NÃO apaga a tabela `users`.
"""

from __future__ import annotations

from radar3d.db import SessionLocal
from radar3d.models import Embedding, Model3D, Product, UsageCounter


def main() -> None:
    session = SessionLocal()
    try:
        p = session.query(Product).delete()  # cascade -> snapshots, matches
        m = session.query(Model3D).delete()  # cascade -> matches
        e = session.query(Embedding).delete()
        u = session.query(UsageCounter).delete()
        session.commit()
        print(f"Limpo: {p} produtos, {m} modelos, {e} embeddings, {u} contadores de uso.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
