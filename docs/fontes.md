# Radar3D — Fontes de Dados

Este documento é a fonte da verdade sobre **de onde e como** o Radar3D obtém
dados. Nenhum coletor entra em produção sem uma decisão registrada aqui.

> **Regra R5 (regras de negócio):** priorizar API oficial ▸ feed/afiliados ▸
> página pública (respeitando `robots.txt`, termos e rate limit) ▸ **não usar**.
> Nunca contornar proteção anti-bot; nunca baixar/hospedar STLs.

**Pesquisa realizada em:** 2026-09-13. Políticas e endpoints mudam — reverificar
antes de implementar cada coletor e registrar a data.

## Legenda de decisão

| Decisão | Significado |
|---------|-------------|
| ✅ API oficial | Existe API pública documentada; caminho preferido. |
| 🟡 Oficial c/ ressalvas | API existe mas com limites, aprovação ou termos que restringem nosso uso. |
| 🟠 Sem API — avaliar público | Sem API; coleta pública possível, sujeita a termos/robots — decisão legal pendente. |
| 🔴 Bloqueado / não usar | Sem caminho legítimo hoje. |

---

## Resumo executivo

| Fonte | Papel | API oficial? | Decisão | Prioridade MVP |
|-------|-------|--------------|---------|----------------|
| **Cults3D** | Biblioteca | ✅ GraphQL, dá tudo menos o arquivo | ✅ | **1ª (âncora do MVP)** |
| **Thingiverse** | Biblioteca | ✅ REST + app token | ✅ | 2ª |
| **MyMiniFactory** | Biblioteca | ✅ REST/OpenAPI + OAuth2 | ✅ | 3ª |
| **Printables** | Biblioteca | 🟠 sem API pública oficial | 🟠 avaliar | depois |
| **MakerWorld** | Biblioteca | 🔴 nenhuma API pública (só endpoints não oficiais c/ JWT) | 🟠→🔴 | depois / talvez não |
| **Thangs** | Biblioteca | 🟡 API existe, focada em vendedores/membership | 🟡 contatar | avaliar (busca geométrica!) |
| **Shopee** | Mercado (tração) | 🟡 Open Platform (Seller/Product) + Afiliados | 🟡 decisão de escopo | **bloqueante da Fase 0** |

**Conclusão de estratégia:** o MVP deve ser construído sobre as **3 bibliotecas
com API oficial** (Cults3D → Thingiverse → MyMiniFactory), que já cobrem a
proposta de valor e cujos termos permitem acessar metadados **sem** os arquivos.
Printables/MakerWorld/Thangs entram depois, conforme viabilidade. A fonte Shopee
é o ponto que mais precisa de decisão jurídica/comercial antes de codar.

---

## Bibliotecas de modelos

### Cults3D — ✅ âncora do MVP
- **API:** GraphQL oficial, endpoint único `https://cults3d.com/graphql`.
- **Auth:** HTTP Basic (`usuário` + API key gerada nas configurações da conta).
- **Dados:** fotos, títulos, descrições, tags, preço, downloads/likes, dados do
  criador. **Não dá acesso aos arquivos 3D** — explicitamente "mantidos no
  Cults por razões legais". Isso está perfeitamente alinhado com a R1 do Radar3D.
- **Licença:** Cults tem a licença "Cults Commercial Use", que pode permitir a
  comercialização das impressões físicas → ótima para popular a faixa 🟢.
- **Rate limit (segundo doc comunitário, confirmar no oficial):** ~60 req/30s e
  ~500 req/dia; usar backoff exponencial em 429/5xx.
- **Ação:** gerar API key oficial; validar rate limit real e termos de uso da
  API na página oficial (`cults3d.com/en/pages/graphql` deu 403 ao bot, abrir no
  navegador logado). Construir o **primeiro adapter** aqui.

### Thingiverse — ✅
- **API:** REST oficial, docs + Swagger em `thingiverse.com/developers`.
- **Auth:** criar app em `thingiverse.com/developers/my-apps` → Client ID,
  Client Secret e **App Token**; aceitar os termos da API MakerBot.
- **Dados:** things, imagens, descrições, tags, contadores; licença por thing
  (Thingiverse usa licenças Creative Commons — bom para classificação, mas
  atenção: CC-NC = 🔴, e muitas permitem uso mas não a venda).
- **Ação:** criar conta developer, obter token, mapear licenças CC → faixas §5.

### MyMiniFactory — ✅
- **API:** REST/OpenAPI oficial (`/api/v2`), docs no GitHub
  (`github.com/MyMiniFactory/api-documentation`).
- **Auth:** OAuth 2.0; criar API Client nas configurações da conta.
- **Dados:** objetos, imagens, metadados, upload (não usaremos upload). Detalhes
  de licença por objeto a mapear a partir do OpenAPI spec.
- **Ação:** ler o `myminifactory-api.yaml`, mapear campos de licença, registrar
  rate limits (não documentados no README — confirmar).

### Printables — 🟠 avaliar
- **API:** **sem API pública oficial** até a última verificação (discussões no
  fórum Prusa; nada lançado). Existe uma API interna/GraphQL usada pelo site,
  não documentada nem suportada.
- **Licença:** criadores podem oferecer licença comercial em certos planos do
  Club → relevante para 🟡.
- **Ação:** monitorar lançamento de API oficial. Enquanto isso, avaliar
  juridicamente coleta pública respeitando `robots.txt`/termos, ou usar apenas
  como fonte manual. **Não implementar coletor automatizado sem decisão legal.**

### MakerWorld — 🔴 / 🟠
- **API:** **nenhuma API pública oficial.** Só existem endpoints não oficiais
  (reverse-engineered do app Bambu Handy, `api.bambulab.com/v1` /
  `makerworld.com/api/v1`, protegidos por Cloudflare e exigindo JWT de conta).
  Usar isso viola R5 (contornar proteção) — **não usar.**
- **Licença:** muitos modelos padrão proíbem venda digital e física; alguns
  criadores oferecem assinatura comercial → relevante, mas sem via legítima de
  coleta hoje.
- **Ação:** só entra se a Bambu lançar API oficial **ou** via parceria. Até lá,
  fora do escopo automatizado.

### Thangs — 🟡 (potencial estratégico)
- **API:** existe uma "Membership API" e API custom, mas voltada a
  vendedores/gestão de membership, não claramente aberta para busca de terceiros.
- **Diferencial:** Thangs tem **busca geométrica por deep learning** e ~19M
  modelos — exatamente o tipo de matching que o Radar3D faz internamente. Pode
  ser parceiro ou concorrente; avaliar com cuidado.
- **Ação:** contatar Thangs para entender acesso de API de busca/leitura e
  termos. Não implementar sem clareza.

---

## Mercado — Shopee (🟡 bloqueante da Fase 0)

Fonte da "tração de mercado" (preço, vendas públicas, tendência, concorrentes).
É o ponto mais sensível do projeto.

- **Shopee Open Platform (Seller API):** feita para o vendedor acessar a
  própria loja, não para inteligência sobre terceiros. **Não** cobre o caso.
- **✅ Shopee Affiliate Open Platform (API GraphQL oficial) — via escolhida.**
  Brasil: `https://open-api.affiliate.shopee.com.br/graphql` (POST), docs em
  affiliateshopee.com.br/documentacao. `productOfferV2` retorna itemId,
  productName, productLink/offerLink, imageUrl, priceMin/Max, `sales`,
  `ratingStar`, commissionRate, shopId/shopName. **Tem tudo que precisamos**
  (inclusive vendas para as tendências). Oficial e gratuito (modelo de comissão);
  exige aprovação da conta de afiliado (~5-15 dias em affiliate.shopee.com.br).
  Auth por assinatura SHA256 (appId+timestamp+payload+secret).
- **Apify:** actor `viralanalyzer/shopee-affiliate-products` cobra por resultado
  (~US$ 0,0002–0,0009/produto), MAS **testado: é wrapper da API de afiliados e
  exige o `appId`/secret de afiliado** ("Missing required credential: appId").
  Ou seja, NÃO é atalho sem aprovação. Com credenciais de afiliado, use
  `SHOPEE_SOURCE=affiliate` direto (oficial, grátis, sem markup do Apify). Só
  vale Apify com um actor **scraper** de verdade (outro id), sujeito a ToS.
- **Coleta pública:** "vendas públicas" e preço aparecem nas páginas de produto,
  mas coleta automatizada esbarra em termos de uso e proteção anti-bot da Shopee.
- **Terceiros (Apify etc.):** existem scrapers comerciais de "Shopee Affiliate
  Products / Commission Tracking". Terceirizar a coleta transfere parte do risco,
  mas gera dependência e custo, e ainda exige avaliar os termos.

**Visão do produto (definida pelo usuário):** a coleta da Shopee será
**automatizada e recorrente** — ex.: rodar 1×/dia — alimentando um histórico que
o app usa para mostrar **tendências por período (dia / semana / mês)**. A entrada
manual (`/adicionar`) é só para testar agora. Isso implica:
- Um coletor agendado (cron/worker) que varre categorias/termos-alvo da Shopee.
- **Snapshots temporais** por produto (preço, vendas públicas, posição) para
  calcular crescimento/tendência — provavelmente uma tabela `product_snapshots`
  além de `products`.
- Agregações por janela (dia/semana/mês) e ranking de "em alta".

> **⚠️ Uso da API de afiliados — ponto legal (não é aconselhamento jurídico).**
> Os T&C do programa de afiliados Shopee proíbem "robôs/ferramentas de consulta
> automatizada" e "scraping" da propriedade intelectual da Shopee, e existem para
> quem **promove produtos e gera vendas via seus links de afiliado** (comissão).
> Um SaaS puramente de inteligência de mercado que redistribui dados a terceiros
> pode ficar **fora do propósito** do programa. **Alinhamento recomendado:** o
> Radar3D já direciona o usuário para o produto na Shopee — usar aí o
> `offerLink` (link de afiliado da própria API) faz do produto um caso legítimo
> de afiliação (você promove e ganha comissão), não só analytics. **[Implementado:
> os adapters affiliate/apify usam `offerLink` como `shopee_url`; o CTA "Comprar
> na Shopee" no front sai com `rel="sponsored"`.]** Mesmo assim:
> ler os T&C atuais (help.shopee.com.br), exibir só dado público, sem sugerir
> endosso, e confirmar com o suporte de afiliados o uso automatizado (frequência
> da coleta) antes de escalar.

**Decisões a tomar na Fase 0 (registrar aqui quando fechadas):**
1. Usar o programa de **Afiliados** como via oficial de dados de produto? (verificar cobertura)
2. Se não, terceirizar coleta (Apify-like) ou coletar público próprio?
3. Restringir "vendas" ao que é exibido publicamente (nunca dado privado de vendedor).
4. Aprovação jurídica dos termos da Shopee para o caso de uso escolhido.
5. Frequência da coleta e retenção do histórico para as tendências.

> **Postura recomendada:** iniciar o MVP com **entrada manual/curada** de alguns
> produtos-alvo da Shopee (ou lista fornecida pelo usuário) enquanto a via
> automatizada é decidida juridicamente. Assim o valor (matching + licença) é
> provado sem travar no ponto mais arriscado.
>
> **Status: implementado.** Tela `/adicionar` (front) + `POST /products` (API)
> permitem colar um anúncio real (título, foto, preço...) e disparam a busca de
> modelos automaticamente. A via automatizada segue como decisão pendente.

---

## Princípios de coleta (todas as fontes)

- Respeitar `robots.txt`, `User-Agent` identificável, rate limit + backoff.
- Preferir sempre API oficial autenticada.
- Guardar `collected_at` / `license_checked_at`; nunca o arquivo 3D.
- Um **adapter isolado por fonte**, com interface comum, para que uma fonte cair
  não derrube as outras (degradar com "dados de {data}").
- Reverificar termos periodicamente e atualizar a tabela de decisão acima.

## Fontes consultadas
- Shopee API: [api2cart – Shopee API Guide](https://api2cart.com/api-technology/shopee-api/), [Shopee Affiliate Products (Apify)](https://apify.com/viralanalyzer/shopee-affiliate-products/api/openapi)
- MakerWorld: [Feature Request: MakerWorld API (fórum Bambu)](https://forum.bambulab.com/t/feature-request-makerworld-api-or-rss-feed-for-user-data/205669), [OpenBambuAPI cloud-makerworld](https://github.com/Doridian/OpenBambuAPI/blob/main/cloud-makerworld.md)
- Printables: [Printables API (fórum Prusa)](https://forum.prusa3d.com/forum/english-forum-general-discussion-announcements-and-releases/printables-application-programmable-interface-api/)
- Cults3D: [Cults API (oficial)](https://cults3d.com/en/pages/graphql), [cults3d-api-docs (comunidade)](https://github.com/CheekyCodexConjurer/cults3d-api-docs)
- Thingiverse: [Thingiverse Developers](https://www.thingiverse.com/developers), [Getting Started](https://www.thingiverse.com/developers/getting-started)
- MyMiniFactory: [api-documentation (GitHub)](https://github.com/MyMiniFactory/api-documentation), [For Developers](https://www.myminifactory.com/pages/for-developers)
- Thangs: [Thangs Marketplace](https://thangs.com/marketplace), [Thangs 3D search (DEVELOP3D)](https://develop3d.com/collaborate/thangs-3d-search-engine-powered-by-deep-learning/)
