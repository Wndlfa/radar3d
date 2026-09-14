# Radar3D — Plano de Implementação

Stack: **Next.js (App Router, TS)** no front · **Python (FastAPI)** no back ·
**PostgreSQL + pgvector** · **Redis + fila de workers** · embeddings de
imagem/texto para matching.

## 0. Arquitetura em uma imagem

```
┌────────────┐     HTTPS/JSON     ┌──────────────────┐
│  Next.js   │  ───────────────▶  │  FastAPI (API)   │
│  (Vercel)  │  ◀───────────────  │                  │
└────────────┘                    └───────┬──────────┘
                                          │ enfileira
                                  ┌───────▼──────────┐
                                  │  Redis (fila)    │
                                  └───────┬──────────┘
                                          │
                     ┌────────────────────┼─────────────────────┐
                     ▼                    ▼                     ▼
             ┌──────────────┐   ┌──────────────────┐   ┌────────────────┐
             │ Coletor      │   │ Gerador de       │   │ Classificador  │
             │ Shopee       │   │ embeddings       │   │ de licença     │
             └──────────────┘   └──────────────────┘   └────────────────┘
                     └──────── Coletores de bibliotecas ──────┘
                                          │
                              ┌───────────▼───────────┐
                              │ PostgreSQL + pgvector  │
                              └────────────────────────┘
```

O front nunca fala com coletores nem com o banco direto — só com a API.

## 1. Fase 0 — Fundação e decisões (bloqueante)

Antes de escrever features, resolver o que trava tudo:

- **Viabilidade legal/técnica das fontes.** Para cada fonte (Shopee + 6
  bibliotecas): existe API oficial / programa de afiliados / feed? O que o
  `robots.txt` e os termos permitem? Rate limits? Registrar em
  `docs/fontes.md` com a decisão por fonte (API oficial ▸ feed ▸ público ▸ não
  usar). **Nenhum coletor entra em produção sem essa checagem.**
- **Estratégia de dados da Shopee** (ver §7.2 das regras) — decidir e documentar.
- Escolha do modelo de embeddings (visual + texto). Candidato: CLIP-like
  self-hosted vs. API. Critérios: custo, licença do modelo, latência.
- Setup: monorepo (`/web` Next, `/api` FastAPI, `/workers`), Docker Compose para
  Postgres+Redis, lint/format/CI, gestão de segredos.

Entregável: repo inicial + `docs/fontes.md` + ADR das 3 decisões acima.

## 2. Fase 1 — Modelo de dados e API base

Schema (PostgreSQL):

- `products` — dados comerciais da Shopee (§7.1). Inclui `collected_at`.
- `models` — modelos das bibliotecas (§7.2), com `license_tier`,
  `license_raw`, `license_checked_at`, `platform`, `source_url`.
- `product_model_matches` — N:N com `visual_score`, `text_score`,
  `feature_score`, `final_score`, `match_level`.
- `embeddings` — vetores (pgvector) para produtos e modelos.
- `sources`, `crawl_jobs`, `users`, `plans/entitlements`.

API (FastAPI):

- `GET /products` (filtros da §8: plataforma, preço, tendência, nível, licença,
  toggle comercial), `GET /products/{id}` com modelos e matches.
- Auth (JWT/sessão), entitlements por plano.
- OpenAPI gerado → tipos consumidos pelo front.

## 3. Fase 2 — Coleta

- **Coletor Shopee** conforme decisão da Fase 0. Normaliza para `products`.
- **Coletores de bibliotecas** (um adapter por plataforma, interface comum):
  MakerWorld, Printables, Cults3D, MyMiniFactory, Thingiverse, Thangs.
  Cada adapter extrai metadados **e o texto de licença bruto**.
- Orquestração via fila; agendamento; deduplicação; respeito a rate limits e
  `robots.txt` (R5). Reprocessa e registra `collected_at`.

### Coletor Shopee agendado — implementado (arquitetura)

- Fonte trocável `radar3d.shopee` (`stub` / `affiliate`); `affiliate` = Shopee
  Affiliate Open Platform GraphQL (`productOfferV2`), a via oficial escolhida
  (ver docs/fontes.md). `stub` gera dados mock para testar sem credenciais.
- `workers/collect.collect_shopee`: descobre por termos-alvo, **upsert por
  `external_id`** (idempotente), grava um `ProductSnapshot` por rodada e
  **enriquece só produtos NOVOS** (CLIP roda 1× por produto; a atualização
  diária de métricas é barata e alimenta as tendências).
- Serviço `scheduler` (imagem alpine, sem torch) enfileira a coleta 1×/dia no
  horário `SHOPEE_COLLECT_HOUR`. Disparo manual: `POST /collect/shopee`.
- Validado com o stub: 15 produtos, 2ª rodada 0 novos/15 atualizados (sem
  duplicar), snapshots acumulando. Falta: credenciais reais de afiliado
  (aprovação ~5-15 dias) ou Apify como ponte.

## 4. Fase 3 — Matching

- Gerar embeddings de imagem e texto para produtos e modelos.
- Busca ANN via pgvector (candidatos) → reranking com score combinado
  (visual + textual + características).
- Atribuir `match_level` (§6 das regras) por thresholds configuráveis.
- Ferramenta interna de avaliação: conjunto rotulado à mão para medir precisão
  e calibrar pesos/limiares.

### Status: implementado (CLIP self-hosted)

- Provider trocável (`stub`/`local_clip`/`api`) — `local_clip` = CLIP ViT-B-32
  no worker Debian; texto e imagem no mesmo espaço (foto do anúncio × render).
- Score por cosseno, pesos **visual 0.6 · texto 0.25 · características 0.15**
  (visual é o sinal mais confiável de "mesmo objeto"), renormalizados quando
  falta algum sinal.

### Calibração (registro — `radar3d.scripts.calibrate`)

Distribuição real medida na busca "controller stand" (Cults3D, 20 modelos):

| Medida | mediana | p90 | máx |
|--------|---------|-----|-----|
| Visual render×render (mesma categoria) | 0.62 | 0.74 | 0.87 |
| Produto×render (mesmo objeto no topo) | 0.64 | 0.74 | 1.00 |
| Texto nome×nome | 0.72 | 1.00 | 1.00 |

Limiares provisórios sobre o score final: EXATA ≥ 0.80 · MUITO_SEMELHANTE ≥
0.66 · ALTERNATIVA ≥ 0.52. Muito abaixo do padrão ingênuo (0.9), porque o CLIP
raramente passa de ~0.87 mesmo para itens muito parecidos, e há gap de domínio
foto↔render.

### Conjunto de avaliação rotulado (`radar3d.eval`)

- `dataset.json`: casos com produto + rótulos gold por `source_url`
  (exact/similar/alternative/unrelated).
- `radar3d.eval.evaluate`: roda o pipeline real, junta previsões aos rótulos e
  reporta score médio por classe, **AUC** (relevante acima de irrelevante) e o
  corte de limiar que maximiza F1.

**Resultado do 1º caso (dragão / controller stand): AUC = 0.583** — pouco acima
do aleatório. Achado central: o matching só-imagem acha bem a **duplicata visual
exata** (0.884, topo), mas falha em "mesmo produto com render/foto diferente" —
outro suporte cabeça-de-dragão ficou em 0.643 (quase no fim), abaixo até de
"alternative" genéricos (média 0.710). Texto de título genérico não separa.

**Próximas iterações para elevar o AUC** (ordem de custo/benefício):
1. ~~Embutir **múltiplas imagens** por modelo~~ ✅ implementado (Cults
   `illustrations`, Thingiverse `/images`, MMF `images[]`); visual = MAIOR
   cosseno entre a foto do produto e qualquer imagem do modelo. Download
   paralelo + encode em batch. **Ganho pequeno** no caso de teste
   (similar 0.643→0.691) e AUC ainda 0.583 — porque os genéricos também sobem.
2. **Sinal de palavras-chave / texto melhor** — o achado mais forte: com título
   de produto **descritivo** ("dragon head controller stand" em vez de
   "controller stand"), o topo passou a ser dominado por suportes de dragão
   reais (exato 0.884→0.934). O título genérico do teste neutralizava o texto.
   Anúncio real da Shopee traz texto rico → priorizar isso.
3. ~~**Idioma PT↔EN**~~ ✅ implementado. Tradução PT→EN trocável
   (`radar3d.translate`: none/glossary/marian/argos) aplicada ao título antes da
   **busca** e do **match textual**. Achados:
   - Argos: **CDN inacessível** neste ambiente (erro de rede no download).
   - MarianMT (HF): funciona, mas **erra o jargão** ("suporte controle" →
     "control support", não "controller stand") → busca ruim.
   - **Glossário de domínio (padrão): melhor e sem RAM.** "suporte de controle
     cabeça de dragão" → "controller stand dragon head". Produto PT passou a
     achar "Dragon Head Gaming Controller Stand" no topo (0.874, EXATA).
   - O glossário cresce com os títulos reais observados.
4. Modelo maior (CLIP ViT-L) ou afinado para produto; reavaliar limiares.

**Limitação do harness atual:** a busca depende do título do produto, então
mudar o título muda os candidatos e "quebra" os rótulos fixos. Próxima versão do
eval deve **desacoplar candidatos (fixos, rotulados) do scoring**.

> **Nota:** dataset atual é pequeno e provisório (rotulado por título/thumbnail).
> O ideal é fotos reais de anúncios da Shopee + negativos claros.

## 5. Fase 4 — Classificador de licença (diferencial do produto)

- Mapear `license_raw` → faixa (§5) por plataforma, começando com **regras
  determinísticas por plataforma/licença conhecida** (mais auditável que ML).
- Aplicar R6 (fallback conservador) e a flag ⚠️ `POSSIVEL_IP_PROTEGIDO`
  (heurística de marcas/personagens em nome/descrição → lista de revisão).
- Painel admin para revisar ⚪ e ⚠️ e corrigir mapeamentos.
- Guardar sempre `license_checked_at` e o texto original para a UI.

## 6. Fase 5 — Frontend

Seguindo o [design system](design-system.md):

- Componentes base: `<LicenseBadge>`, `<MatchScore>`, `<ProductCard>`,
  `<ModelRow>`, filtros (com o toggle comercial em destaque), estados
  (skeleton/vazio/erro/⚪).
- Páginas: lista de produtos com filtros; detalhe `/produto/[id]`.
- Consome a API tipada; nada de acesso direto a dados.
- Tema claro/escuro; acessibilidade AA; microcopy da §8 do design system.

## 7. Fase 6 — Contas, planos e limites

- Auth completa, planos Free/Pro/Business, entitlements (§10 das regras),
  contagem de consultas, filtro comercial gated por plano.
- Billing (provedor a definir) — pode ser fase posterior ao MVP.

### Status: implementado (backend)

- `radar3d.auth` **sem dependências externas**: hash de senha pbkdf2 + JWT
  assinado por HMAC (stdlib), para não rebuildar a imagem pesada do worker.
- Modelo `User` (email, password_hash, plan), rotas `/auth/register|login|me`
  e `/auth/me/plan` (troca de plano manual — billing depois).
- Entitlements em `auth/plans.py`; **filtro comercial (`commercial_only`)
  gated**: free → HTTP 402, pro/business → 200. Validado ponta a ponta.
- **Login no frontend** ✅: route handler `/api/session` guarda o token num
  **cookie httpOnly**; server components leem via `lib/session` e enviam no
  Authorization. Tela `/login`, chip de plano + logout no cabeçalho, upsell no
  filtro comercial. Validado pela UI (free→upsell, pro→lista).
- **Contagem de consultas do Free** ✅: `auth/usage` conta 1 consulta por
  visualização de detalhe (modelos+licenças); Free = `FREE_MONTHLY_QUERIES`/mês
  (padrão 20), Pro/Business ilimitado. Detalhe exige login (401 se anônimo, 402
  ao estourar). Header mostra `usado/limite`; `GET /auth/me/usage`. Validado.
- **Falta:** billing real (troca de plano ainda é manual via `/auth/me/plan`).

## 8. Fase 7 — Qualidade e operação

- Testes: unit (classificador, scoring), contrato de API, e2e do fluxo.
- Observabilidade: logs estruturados, métricas da §11 das regras, alertas de
  fonte indisponível.
- Jobs de reverificação de licença (políticas mudam) + selo "verificada em".
- LGPD: só dados públicos; política de privacidade; sem dados privados de
  vendedor.

## 9. Ordem sugerida de entrega (MVP → completo)

1. **MVP vertical fino:** 1 fonte de biblioteca (ex.: Cults3D, que tem licença
   comercial clara) + coleta de produtos + matching textual+visual básico +
   classificação determinística + tela de lista/detalhe. Prova o valor central.
2. Adicionar as demais bibliotecas (um adapter por vez).
3. Refino do matching (reranking, características) e calibração.
4. Filtro comercial + planos + billing.
5. Alertas de tendência, exportação, API pública (Business).

## 10. Riscos e mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Fonte bloqueia coleta / muda termos | Alto | Preferir APIs oficiais; adapters isolados; degradar com "dados de {data}". |
| Classificação de licença errada | Alto (legal) | Regras determinísticas + R6 conservador + revisão humana de ⚪/⚠️ + disclaimer sempre. |
| Falso "é o mesmo STL" | Médio | Nunca afirmar origem (R3); só nível de correspondência. |
| IP protegido (personagens) | Alto | Flag ⚠️ + aviso explícito na UI. |
| Custo de embeddings | Médio | Batch, cache, avaliar self-host vs API na Fase 0. |
| Escala de coleta | Médio | Fila, dedupe, agendamento incremental. |

## 11. Definição de pronto (por fase)

- Coletor: respeita robots/rate limit, normaliza, registra `collected_at`, tem
  teste de parsing.
- Matching: precisão medida no conjunto rotulado; thresholds documentados.
- Licença: cobertura por plataforma documentada; ⚪ vai para revisão.
- Front: componente segue tokens; estados cobertos; AA; sem hex solto.
