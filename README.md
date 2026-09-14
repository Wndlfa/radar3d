# Radar3D

Descubra quais produtos impressos em 3D estão vendendo na Shopee, encontre
modelos semelhantes nas principais bibliotecas (MakerWorld, Printables, Cults3D,
MyMiniFactory, Thingiverse, Thangs) e confira se existe licença para
comercializá-los.

> **Radar3D não é um repositório de STLs.** Não hospeda, não redistribui e não
> baixa arquivos de terceiros. Ele é um radar de mercado + descoberta de fontes
> originais + classificação de licença, sempre direcionando o usuário para a
> página do criador.

## Stack

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind
- **Backend:** Python (FastAPI) + workers assíncronos
- **Banco:** PostgreSQL + pgvector (busca por similaridade de imagem/texto)
- **Fila:** Redis + RQ/Celery
- **IA:** embeddings de imagem (CLIP-like) e texto para matching

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [Regras de negócio](docs/regras-de-negocio.md) | Domínio, atores, licenças, matching, limites legais |
| [Design system](docs/design-system.md) | Tokens, componentes, padrões de UI, tela do produto |
| [Fontes de dados](docs/fontes.md) | APIs de Shopee e das bibliotecas, decisão por fonte |
| [Plano de implementação](docs/plano-de-implementacao.md) | Fases, arquitetura, entregáveis, riscos |

## Estrutura

```
radar3d/
├── backend/        # Python — API (FastAPI) + workers, um pacote, dois modos
│   └── radar3d/
│       ├── api/        # FastAPI (routers)
│       ├── workers/    # coleta + matching + classificação (RQ)
│       ├── sources/    # um adapter por biblioteca (Cults3D no MVP)
│       ├── domain/     # licenças e matching (regras de negócio)
│       ├── scripts/    # init_db, seed
│       ├── models.py   # ORM (nunca guarda o arquivo 3D)
│       └── schemas.py  # contrato da API
├── web/            # Next.js (App Router) + Tailwind — design system
└── docs/           # regras de negócio, design system, fontes, plano
```

> **Decisão:** back é **um pacote** (`backend/`) rodando em dois modos (api e
> worker) para compartilhar models/domínio, em vez de dois pacotes separados.

## Como rodar (dev)

Tudo via Docker:

```bash
cp .env.example .env
docker compose up --build
```

Depois, inicializar o banco e popular dados de demonstração:

```bash
docker compose exec api python -m radar3d.scripts.init_db
docker compose exec api python -m radar3d.scripts.seed
```

- Front: http://localhost:3000
- API + docs: http://localhost:8000/docs

Testes do backend:

```bash
cd backend && pip install -e ".[dev]" && pytest
```

## Status

MVP funcional de ponta a ponta:
- **Coleta** de 3 bibliotecas com API oficial: Cults3D, Thingiverse, MyMiniFactory
  (múltiplas imagens por modelo).
- **Matching** por embeddings CLIP self-hosted (visual = maior similaridade entre
  a foto do produto e qualquer imagem do modelo; + texto).
- **Classificação de licença** determinística (🟢🟡🔴⚪ + flag ⚠️ de IP).
- **Entrada curada da Shopee** via tela `/adicionar` (foto/título/preço) que
  dispara a busca; detalhe com auto-refresh.
- **Tradução PT→EN** por glossário de domínio (leve, sem RAM) na busca e no match.
- **Tendências**: tabela `product_snapshots` (série temporal), endpoint
  `/products/trending?period=day|week|month` e tela `/em-alta`.
- Conjunto de avaliação rotulado (`radar3d.eval`) para calibrar o matching.

Próximo: **coletor agendado da Shopee** (1×/dia) que alimenta os snapshots —
decisão de coleta em aberto (ver [fontes](docs/fontes.md)); eval com fotos reais.
