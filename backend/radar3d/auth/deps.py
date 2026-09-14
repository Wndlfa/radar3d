"""Dependências de autenticação para o FastAPI."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from radar3d.auth.security import decode_token
from radar3d.db import get_session
from radar3d.models import User


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User | None:
    """Usuário se houver Bearer token válido; None se anônimo."""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    user_id = decode_token(authorization.split(" ", 1)[1])
    if not user_id:
        return None
    return session.get(User, user_id)


def get_current_user(user: User | None = Depends(get_current_user_optional)) -> User:
    """Exige autenticação."""
    if user is None:
        raise HTTPException(status_code=401, detail="Autenticação necessária")
    return user
