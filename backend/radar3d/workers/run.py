"""Worker RQ. Consome a fila de jobs de enriquecimento.

Uso: python -m radar3d.workers.run
Enfileirar um job de exemplo: python -m radar3d.workers.run --demo <product_id>
"""

from __future__ import annotations

import sys

from redis import Redis
from rq import Queue, Worker

from radar3d.config import settings

QUEUE_NAME = "radar3d"


def _connection() -> Redis:
    return Redis.from_url(settings.redis_url)


def main() -> None:
    conn = _connection()
    if len(sys.argv) >= 3 and sys.argv[1] == "--demo":
        # Enfileira um enriquecimento e sai (útil para testar).
        from radar3d.workers.tasks import enrich_product

        q = Queue(QUEUE_NAME, connection=conn)
        job = q.enqueue(enrich_product, sys.argv[2])
        print(f"Job enfileirado: {job.id}")
        return

    Worker([Queue(QUEUE_NAME, connection=conn)], connection=conn).work()


if __name__ == "__main__":
    main()
