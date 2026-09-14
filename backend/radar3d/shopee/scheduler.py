"""Agendador leve: enfileira a coleta Shopee 1x/dia no horário configurado.

Roda num serviço próprio (imagem alpine, sem torch) — dorme até a próxima
execução e enfileira `collect_shopee` na fila do worker. Sem dependências extras.

Uso: python -m radar3d.shopee.scheduler
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from redis import Redis
from rq import Queue

from radar3d.config import settings


def _seconds_until_next_run(hour: int) -> float:
    now = datetime.now(timezone.utc)
    nxt = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return (nxt - now).total_seconds()


def main() -> None:
    conn = Redis.from_url(settings.redis_url)
    queue = Queue("radar3d", connection=conn)
    hour = settings.shopee_collect_hour
    print(f"[scheduler] coleta Shopee agendada para {hour:02d}:00 UTC diariamente")

    while True:
        wait = _seconds_until_next_run(hour)
        print(f"[scheduler] próxima coleta em {wait / 3600:.1f}h")
        time.sleep(wait)
        from radar3d.workers.collect import collect_shopee

        job = queue.enqueue(collect_shopee)
        print(f"[scheduler] coleta enfileirada: {job.id}")
        time.sleep(60)  # evita reenfileirar no mesmo minuto


if __name__ == "__main__":
    main()
