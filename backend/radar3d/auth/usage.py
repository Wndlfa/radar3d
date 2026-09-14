"""Contagem de consultas por plano (limite mensal do Free)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from radar3d.auth.plans import FEATURES
from radar3d.config import settings
from radar3d.models import UsageCounter, User

# Planos com consultas ilimitadas.
_UNLIMITED = {p for p, f in FEATURES.items() if p != "free"}


def _period() -> str:
    return date.today().strftime("%Y-%m")


def _limit_for(plan: str) -> int | None:
    """None = ilimitado."""
    return None if plan in _UNLIMITED else settings.free_monthly_queries


@dataclass
class Quota:
    used: int
    limit: int | None  # None = ilimitado
    allowed: bool


def _get_or_create(session: Session, user_id: str) -> UsageCounter:
    row = session.scalars(
        select(UsageCounter).where(
            UsageCounter.user_id == user_id,
            UsageCounter.period == _period(),
            UsageCounter.kind == "query",
        )
    ).first()
    if row is None:
        row = UsageCounter(user_id=user_id, period=_period(), kind="query", count=0)
        session.add(row)
        session.flush()
    return row


def peek(session: Session, user: User) -> Quota:
    """Estado atual sem consumir."""
    limit = _limit_for(user.plan)
    used = _get_or_create(session, user.id).count
    return Quota(used=used, limit=limit, allowed=limit is None or used < limit)


def consume(session: Session, user: User) -> Quota:
    """Consome uma consulta se permitido. Ilimitado não incrementa."""
    limit = _limit_for(user.plan)
    if limit is None:
        return Quota(used=0, limit=None, allowed=True)
    row = _get_or_create(session, user.id)
    if row.count >= limit:
        return Quota(used=row.count, limit=limit, allowed=False)
    row.count += 1
    session.commit()
    return Quota(used=row.count, limit=limit, allowed=True)
