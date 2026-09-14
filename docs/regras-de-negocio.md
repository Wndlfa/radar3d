# Radar3D — Regras de Negócio

## 1. Proposta

Radar3D ajuda vendedores e makers a responder três perguntas em uma única tela:

1. **O que está vendendo?** — produtos impressos em 3D com tração na Shopee.
2. **De onde veio o modelo?** — modelos semelhantes nas bibliotecas de STL.
3. **Eu posso vender isso?** — a licença permite comercialização da impressão física?

A terceira pergunta é o coração do produto e o que o diferencia de um simples
scraper. Radar3D vende **clareza de licença**, não arquivos.

## 2. Princípios inegociáveis

Estas regras têm precedência sobre qualquer funcionalidade:

- **R1 — Não hospedar, não baixar, não redistribuir STLs.** Radar3D nunca
  armazena o arquivo 3D de terceiros. Guarda apenas metadados públicos
  (título, imagem de miniatura, criador, licença, link, contadores públicos)
  e sempre encaminha o usuário para a página original.
- **R2 — Nunca afirmar propriedade nem legalidade absoluta.** O sistema
  classifica a licença *declarada na fonte* e sempre recomenda conferir a
  página original, que pode mudar.
- **R3 — Semelhança não é prova de origem.** Uma correspondência visual alta
  indica que os produtos se parecem, não que um veio do outro. A UI nunca diz
  "este é o STL do anúncio"; diz o nível de correspondência (ver §6).
- **R4 — Licença comercial ≠ direito sobre a propriedade intelectual.** Um
  criador oferecer "uso comercial" de um modelo de personagem famoso não
  significa que ele detém os direitos do personagem. O sistema deve sinalizar
  possível marca/personagem protegido (flag ⚠️).
- **R5 — Respeitar as fontes.** Coleta obedece `robots.txt`, termos de uso,
  rate limits e prioriza APIs/feeds oficiais quando existirem. Sem contornar
  proteções anti-bot.

## 3. Atores

| Ator | Descrição |
|------|-----------|
| **Vendedor / Maker** | Usuário final. Quer achar produtos vendáveis e modelos legalmente comercializáveis. |
| **Analista de mercado** | Usa só a parte de tendências da Shopee. |
| **Sistema de coleta** | Workers que buscam e normalizam dados públicos. |
| **Motor de matching** | Compara produto ↔ modelos (texto + imagem + características). |
| **Classificador de licença** | Mapeia a licença da fonte para uma das faixas de §5. |
| **Administrador** | Gerencia fontes, limites, planos e revisa flags de IP. |

## 4. Fluxo do produto (caminho feliz)

1. Sistema identifica um produto físico impresso em 3D na Shopee.
2. Analisa título, descrição e fotos → gera embeddings de texto e imagem.
3. Busca modelos semelhantes nas bibliotecas (MakerWorld, Printables, Cults3D,
   MyMiniFactory, Thingiverse, Thangs; outras no futuro).
4. Calcula o grau de semelhança (visual + textual + características).
5. Classifica a licença de cada modelo encontrado.
6. Exibe: dados comerciais do anúncio + modelos encontrados com semelhança,
   licença e link.
7. Usuário clica em **"Abrir modelo"** e vai direto à página do criador.

## 5. Faixas de licença (a regra central)

Cada modelo recebe **exatamente uma faixa**, definida pela licença declarada na
fonte no momento da coleta. A faixa nunca é definitiva — sempre acompanhada de
"confira na origem".

| Selo | Faixa | Significado |
|------|-------|-------------|
| 🟢 | `VENDA_PERMITIDA` | Venda comercial da impressão física permitida pela licença declarada. |
| 🟡 | `EXIGE_LICENCA` | Permitido mediante assinatura, compra de licença ou plano pago do criador. |
| 🔴 | `SOMENTE_PESSOAL` | Apenas uso pessoal; venda proibida. |
| ⚪ | `NAO_IDENTIFICADA` | Licença não encontrada ou ambígua na fonte. |
| ⚠️ | `POSSIVEL_IP_PROTEGIDO` | Flag adicional (não exclusiva): possível marca/personagem protegido. Pode coexistir com qualquer faixa. |

Notas por plataforma (documentar e revisar periodicamente — políticas mudam):

- **MakerWorld:** muitos modelos padrão proíbem venda da versão digital e da
  impressão física; alguns criadores oferecem assinatura comercial específica.
- **Printables:** criadores podem oferecer licença comercial em certos planos
  do Club.
- **Cults3D:** possui a licença "Cults Commercial Use", que pode permitir a
  comercialização das impressões físicas.

**Regra R6 — Fallback conservador:** na dúvida entre duas faixas, classificar na
mais restritiva e marcar como ⚪ para revisão, nunca na mais permissiva.

## 6. Níveis de correspondência

Separados da licença. Descrevem *quão parecido* o modelo é do anúncio.

| Nível | Rótulo | Critério (orientativo) |
|-------|--------|------------------------|
| 1 | **Correspondência exata** | Aparenta ser o mesmo modelo (visual ≥ ~93% + forte match textual). |
| 2 | **Muito semelhante** | Pequenas modificações ou possível remix. |
| 3 | **Alternativa semelhante** | Mesma função, design diferente. |
| 4 | **Conceito relacionado** | Apenas inspiração/categoria em comum. |

Score final = combinação ponderada de similaridade **visual**, **textual** e de
**características** (formato, função, nº de peças, encaixes, categoria). Os pesos
são configuráveis; a UI mostra o percentual e o rótulo do nível.

## 7. Dados coletados

### 7.1 Produto Shopee (dados comerciais)
Foto, nome, preço, vendas públicas, tendência/crescimento, avaliações, loja,
nº de concorrentes, link da Shopee.

### 7.2 Modelo encontrado (arquivos)
Imagem de miniatura, criador, plataforma, link, gratuito/pago, licença (faixa +
texto original), semelhança, downloads, avaliações, perfis de impressão
disponíveis.

> **Sobre a fonte dos dados da Shopee:** priorizar programa de afiliados/API
> oficial quando disponível; caso não exista, coleta de páginas públicas
> respeitando §2-R5. "Vendas públicas" usa apenas o que a Shopee exibe
> publicamente — nunca dados privados de vendedor. **Esta é uma decisão de
> escopo a validar antes da implementação** (ver plano, Fase 1).

## 8. Filtros e visão

- Filtro-chave: **"Mostrar apenas produtos com modelo comercialmente utilizável
  encontrado"** (faixa 🟢, opcionalmente incluir 🟡).
- Filtros: plataforma, faixa de preço, tendência, nível de correspondência,
  gratuito/pago, licença.
- Ordenação: tração de mercado, semelhança, downloads.

## 9. Regras de exibição (proteção do usuário)

- Nunca renderizar "baixe e venda". Sempre: faixa de licença + "confira na
  origem" + link para o criador.
- Ao exibir ⚠️, mostrar aviso explícito de possível IP protegido.
- Todo modelo pago exibe onde o pagamento/licença ocorre (na plataforma de
  origem, nunca no Radar3D nesta versão).
- Registrar `coletado_em` e mostrar "licença verificada em {data}".

## 10. Planos (rascunho comercial)

| Plano | Limite | Recursos |
|-------|--------|----------|
| Free | N consultas/mês | Tendências + matching básico, sem filtro comercial |
| Pro | Ampliado | Filtro comercial, alertas de tendência, exportação |
| Business | Alto/equipe | API, múltiplos usuários, histórico |

(Preços a definir; estrutura serve para modelar entitlements desde o início.)

## 11. Métricas de sucesso

- % de produtos com pelo menos 1 modelo de correspondência nível 1–2.
- % de modelos com licença classificada (não ⚪).
- Precisão do classificador de licença (validação manual amostral).
- Cliques em "Abrir modelo" / conversão para a fonte.
