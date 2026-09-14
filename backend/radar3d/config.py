"""Configuração central lida de variáveis de ambiente (ver .env.example)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str = "postgresql+psycopg://radar3d:radar3d@localhost:5432/radar3d"
    redis_url: str = "redis://localhost:6379/0"

    api_cors_origins: str = "http://localhost:3000"

    # Credenciais de fontes (ver docs/fontes.md). Vazias => adapter fica inativo.
    cults3d_username: str = ""
    cults3d_api_key: str = ""
    thingiverse_app_token: str = ""
    # MyMiniFactory aceita API key simples via query param `key` (mais fácil
    # que OAuth2 para leitura). Ver docs/fontes.md.
    myminifactory_api_key: str = ""

    embeddings_provider: str = "stub"
    # Provider "api" (CLIP multimodal hospedado — deixa o worker leve, sem torch).
    # Default: Jina CLIP v2 (texto + imagem no mesmo espaço). dim truncado (Matryoshka).
    embeddings_api_url: str = "https://api.jina.ai/v1/embeddings"
    embeddings_api_key: str = ""
    embeddings_api_model: str = "jina-clip-v2"
    embeddings_api_dim: int = 512  # casa com a coluna Vector(512)
    # Task LoRA (v3/v5). Vazio = padrão do modelo. Para match simétrico
    # produto<->modelo, "text-matching" costuma ser melhor que retrieval.*
    embeddings_api_task: str = ""

    # Auth (JWT assinado por HMAC — troque o segredo em produção).
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_hours: int = 168
    free_monthly_queries: int = 20  # limite de consultas/mês do plano Free
    # Tradução PT->EN da consulta/título antes da busca e do match textual.
    # "none" (sem tradução) ou "argos" (offline, no worker). Ver docs/plano.
    translate_provider: str = "none"

    # --- Coletor Shopee (ver docs/fontes.md) ---
    # "stub" | "affiliate" (API oficial) | "apify" (actor pago por resultado).
    shopee_source: str = "stub"
    shopee_affiliate_app_id: str = ""
    shopee_affiliate_secret: str = ""
    apify_token: str = ""
    apify_shopee_actor: str = "lergassy~shopee-scraper"
    # Termos-alvo da coleta (PT — Shopee BR). Nichos imprimíveis em 3D.
    shopee_queries: str = "suporte controle videogame,suporte headset,suporte de celular,organizador de cabos,luminaria abajur"
    shopee_max_per_query: int = 30  # itens por termo por rodada (custo Apify)
    shopee_collect_hour: int = 3  # hora do dia (UTC) para a coleta agendada

    @property
    def shopee_queries_list(self) -> list[str]:
        return [q.strip() for q in self.shopee_queries.split(",") if q.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


settings = Settings()
