"""Entrypoint da API FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from radar3d.config import settings
from radar3d.api.routers import auth, collect, health, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Garante extensão pgvector + tabelas no boot (idempotente). Ver scripts/init_db.
    try:
        from radar3d.scripts.init_db import main as init_db

        init_db()
    except Exception as e:  # não derruba a API se o banco estiver indisponível no boot
        print(f"[startup] init_db falhou: {e}")
    yield


app = FastAPI(title="Radar3D API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(collect.router)
