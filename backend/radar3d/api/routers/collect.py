"""Disparo manual da coleta Shopee (a agendada roda no serviço scheduler)."""

from __future__ import annotations

from fastapi import APIRouter
from redis import Redis
from rq import Queue

from radar3d.config import settings
from radar3d.shopee.factory import get_shopee_source

router = APIRouter(prefix="/collect", tags=["collect"])


@router.get("/shopee/status")
def shopee_status() -> dict:
    src = get_shopee_source()
    return {
        "source": src.name,
        "enabled": src.is_enabled(),
        "queries": settings.shopee_queries_list,
    }


@router.post("/shopee")
def trigger_shopee() -> dict:
    """Enfileira uma rodada de coleta agora (para testar sem esperar o agendador)."""
    from radar3d.workers.collect import collect_shopee

    conn = Redis.from_url(settings.redis_url)
    job = Queue("radar3d", connection=conn).enqueue(collect_shopee)
    return {"enqueued": True, "job_id": job.id}
