"""Cria a extensão pgvector e as tabelas. Uso: python -m radar3d.scripts.init_db

Para o MVP usamos create_all; migrações Alembic entram quando o schema estabilizar.
"""

from __future__ import annotations

from sqlalchemy import text

from radar3d.db import Base, engine
from radar3d import models  # noqa: F401  (registra as tabelas)


def main() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
    print("Banco inicializado (extensão vector + tabelas).")


if __name__ == "__main__":
    main()
