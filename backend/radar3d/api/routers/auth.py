"""Registro, login e plano do usuário."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from radar3d.auth.deps import get_current_user
from radar3d.auth.plans import FEATURES, PLANS
from radar3d.auth.security import create_token, hash_password, verify_password
from radar3d.auth import usage
from radar3d.db import get_session
from radar3d.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    token: str
    plan: str


class MeOut(BaseModel):
    id: str
    email: str
    plan: str
    features: dict


class PlanIn(BaseModel):
    plan: str


@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: Credentials, session: Session = Depends(get_session)) -> TokenOut:
    exists = session.scalars(select(User).where(User.email == body.email)).first()
    if exists:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    user = User(email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    session.commit()
    return TokenOut(token=create_token(user.id), plan=user.plan)


@router.post("/login", response_model=TokenOut)
def login(body: Credentials, session: Session = Depends(get_session)) -> TokenOut:
    user = session.scalars(select(User).where(User.email == body.email)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return TokenOut(token=create_token(user.id), plan=user.plan)


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)) -> MeOut:
    return MeOut(id=user.id, email=user.email, plan=user.plan, features=FEATURES[user.plan])


@router.get("/me/usage")
def my_usage(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> dict:
    q = usage.peek(session, user)
    return {"plan": user.plan, "used": q.used, "limit": q.limit, "unlimited": q.limit is None}


@router.patch("/me/plan", response_model=MeOut)
def set_plan(
    body: PlanIn,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> MeOut:
    """Troca de plano (DEV/manual — sem billing ainda)."""
    if body.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Plano inválido. Use: {PLANS}")
    user.plan = body.plan
    session.commit()
    return MeOut(id=user.id, email=user.email, plan=user.plan, features=FEATURES[user.plan])
