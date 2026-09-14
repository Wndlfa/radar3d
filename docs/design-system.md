# Radar3D — Design System

Sistema de design para o front em Next.js + Tailwind. A meta visual: uma
ferramenta de **inteligência de mercado** — densa em dados, calma, legível,
sem parecer marketplace. O elemento visual mais importante é o **selo de
licença**, que precisa ser lido em um relance.

## 1. Princípios

- **Clareza acima de decoração.** Cada card responde "vende?" e "posso vender?".
- **Licença é semântica, não estética.** As cores das faixas (§3) têm significado
  fixo e nunca são usadas para outra coisa.
- **Densidade honesta.** Muita informação, hierarquia forte, respiro suficiente.
- **Estados sempre visíveis.** Loading, vazio, ⚪ não-identificada, erro de fonte.
- **Acessível.** Contraste AA mínimo; nunca comunicar só por cor (selo tem cor +
  ícone + texto).

## 2. Tokens

Definidos como CSS variables e mapeados no `tailwind.config`. Tema claro e
escuro; escuro é o padrão para ferramenta de trabalho.

> **Identidade "build-chamber / radar" (v2).** Fundo escuro de câmara de
> impressão; o accent é o **ciano de sinal** do radar (fora da faixa das cores
> de licença, para não competir com o veredito). Assinaturas: **radar mark** com
> sweep girando no cabeçalho, **hairlines de "layer line"** (motivo do FDM) como
> divisores, e a **espinha colorida do veredito de licença** na borda esquerda
> de cada card — a lista inteira vira um radar de "posso vender?".

### Cores base (neutras)
```
--bg            #0D1417   (dark)   / #F6F7F8 (light)
--surface       #131C21   / #FFFFFF
--surface-2     #1B262C   / #EEF1F3
--border        #26323A   / #DDE3E7
--text          #E9EFF2   / #10191E
--text-muted    #8FA0AA   / #566069
--text-faint    #5D6D76   / #8A97A0
--accent        #22C7E6   (ciano — sinal do radar; ações, links, foco)
--accent-hover  #10B6D6
```
Texto sobre o accent usa um tom escuro (#04222A), não branco (o ciano é claro).

### Cores semânticas de LICENÇA (fixas, não reutilizar)
```
--lic-green   #22C55E   🟢 VENDA_PERMITIDA
--lic-yellow  #E0A112   🟡 EXIGE_LICENCA
--lic-red     #EF4444   🔴 SOMENTE_PESSOAL
--lic-gray    #7C8B95   ⚪ NAO_IDENTIFICADA
--lic-warn    #D97706   ⚠️ POSSIVEL_IP_PROTEGIDO (borda/badge de alerta)
```
Estas cores viram a **espinha esquerda** do card e o selo. Como são `var()`,
NÃO use o modificador de opacidade do Tailwind (`bg-lic-green/10`) — use
`color-mix` inline quando precisar de tinta suave.

### Correspondência (escala azul→neutra, distinta das licenças)
```
--match-1 #2563EB  Correspondência exata
--match-2 #4F82E0  Muito semelhante
--match-3 #6B7280  Alternativa semelhante
--match-4 #8A94A0  Conceito relacionado
```

### Tipografia
```
--font-display "Space Grotesk"  (marca, títulos, rank, números-chave — engenhada/CAD)
--font-sans    "Inter", system-ui, sans-serif  (corpo, densidade de dados)
--font-mono    "JetBrains Mono", ui-monospace  (preço, vendas, %, scores)

Escala (rem): 0.75 / 0.875 / 1 / 1.125 / 1.25 / 1.5 / 2 / 2.5
Pesos: 400 corpo · 500 rótulos · 600 títulos · 700 display forte
```
Carregadas via Google Fonts no `<head>`. Números de mercado usam mono tabular.

### Espaçamento / raio / sombra
```
space: 4 8 12 16 24 32 48 64 (px)
radius: sm 6 · md 10 · lg 14 · pill 999
shadow: card 0 1px 2px rgba(0,0,0,.3) · pop 0 8px 24px rgba(0,0,0,.4)
```

## 3. Componente-chave: Selo de Licença (`<LicenseBadge>`)

O componente mais importante do sistema. Sempre **cor + ícone (forma) + texto**.
Os ícones são **SVG** (`<LicenseIcon>`), diferenciados pela FORMA (não só cor —
acessível a daltônicos). NÃO usar emoji (inconsistente entre sistemas e feio).

```
[✓  Venda permitida]     check      · lic-green
[🔒 Exige licença]       cadeado    · lic-yellow
[⊘  Somente pessoal]     proibido   · lic-red
[?  Não identificada]    interrog.  · lic-gray
[⚠  Possível marca protegida]   triângulo (<WarnIcon>) · lic-warn
```
A flag ⚠️ aparece junto de qualquer faixa e também é **agregada por produto**
na lista/`<LicenseSummary>` (chip "IP protegido?") quando algum modelo a tem.
- Formato pill, `radius-pill`, altura 24px, ícone 14px, texto 0.75rem/500.
- Tooltip no hover: texto original da licença + "Verificada em {data} · confira
  na origem".
- Nunca aparece sozinho sem o link para a fonte por perto.

## 4. Componente: Medidor de Correspondência (`<MatchScore>`)

- Percentual em mono + rótulo do nível (§6 das regras).
- Barra fina de progresso na cor `--match-N`.
- Tooltip: quebra visual→textual→características.

## 5. Componente: Card de Produto (`<ProductCard>`)

Estrutura em duas áreas (espelha §7 das regras):

```
┌───────────────────────────────────────────────┐
│  [foto]   Organizador de controles             │
│           R$ 49,90   ·   720 vendas   ↑ crescendo│
│           ★ 4.8 · Loja X · 9 concorrentes      │
│           [Ver na Shopee ↗]                     │
├───────────────────────────────────────────────┤
│  Modelos encontrados (3)          [filtrar ▾]  │
│  ┌─────────────────────────────────────────┐  │
│  │ [img] Game Controller Stand · MakerWorld │  │
│  │       96% exata · Grátis · [🟢 Venda ok] │  │
│  │       ↓ 12k · ★4.9 · [Abrir modelo ↗]    │  │
│  └─────────────────────────────────────────┘  │
│  ... mais linhas de modelo                     │
└───────────────────────────────────────────────┘
```

Sub-componente `<ModelRow>`: miniatura, nome, criador, plataforma, `<MatchScore>`,
gratuito/pago, `<LicenseBadge>`, downloads, avaliações, CTA "Abrir modelo".

## 6. Layout de página

- **Topbar:** logo, busca, seletor de plano, avatar.
- **Sidebar de filtros** (colapsável em mobile): plataforma, preço, tendência,
  nível de correspondência, faixa de licença, e o toggle destacado **"Só com
  modelo comercialmente utilizável"**.
- **Grid de resultados:** cards de produto, 1 col mobile / 2–3 col desktop.
- **Detalhe do produto:** rota `/produto/[id]` com todas as áreas expandidas.

## 7. Estados

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeletons dos cards, nunca spinner solto. |
| Vazio | "Nenhum produto com esses filtros." + sugestão de afrouxar filtro. |
| Sem modelo encontrado | Card mostra área comercial + "Nenhum modelo semelhante encontrado ainda". |
| Licença ⚪ | Selo cinza + aviso "confira na origem". |
| Fonte indisponível | Badge "dados de {data}" + aviso de defasagem. |

## 8. Voz e microcopy

- Direta e honesta. Nunca "baixe e venda". Sempre "Abrir modelo na origem".
- Percentuais acompanhados do rótulo ("96% · correspondência exata").
- Datas de verificação sempre visíveis onde há licença.

## 9. Convenções de código do front

- Componentes em `components/`, um arquivo por componente, tipados.
- Tokens só via CSS vars / classes Tailwind — nada de hex solto no JSX.
- Selos e scores são componentes; proibido reconstruir inline.
- Ícones: lucide-react (formato consistente com o pill de selo).
