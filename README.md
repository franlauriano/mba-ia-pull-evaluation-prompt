# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Este projeto foca na **avaliação de prompts** usando métricas objetivas: **F1-Score**, **Clarity**, **Precision**, **Helpfulness** e **Correctness**. O fluxo inclui pull de prompts do LangSmith, refatoração com técnicas de Prompt Engineering, push de volta ao Hub e **avaliação até atingir média ≥ 0,9** nessas cinco métricas.

*Bug → User Story* é apenas o **exemplo de domínio** usado neste repositório (dataset e prompts de conversão de bug em user story); a abordagem de avaliação por essas métricas pode ser aplicada a outros tipos de prompt.

O software deve:

1. **Fazer pull de prompts** do LangSmith Prompt Hub (prompts de baixa qualidade publicados no Hub).
2. **Refatorar e otimizar** os prompts aplicando ao menos duas técnicas de Prompt Engineering (ver tabela abaixo).
3. **Fazer push dos prompts otimizados** de volta ao LangSmith (repositório público no Hub).
4. **Avaliar os prompts** com as métricas **F1-Score, Clarity, Precision, Helpfulness e Correctness** (cada uma de 0 a 1; o script deriva Helpfulness e Correctness a partir das demais).
5. **Atingir média mínima de 0,9** (90%) na avaliação — ou seja, a média das cinco métricas deve ser ≥ 0,9.

O ciclo pull → otimizar → push → avaliar pode ser repetido até o critério ser atingido.

### Técnicas de Prompt Engineering (resumo)

Para a refatoração, utilize **pelo menos duas** das técnicas abaixo. Breve descrição de cada uma:

| Técnica | O que é |
|--------|--------|
| **Few-shot Learning** | Fornecer exemplos claros de **entrada/saída** no próprio prompt. O modelo tende a replicar o formato e o estilo dos exemplos, reduzindo ambiguidade e erros de estrutura. |
| **Chain of Thought (CoT)** | Instruir o modelo a **"pensar passo a passo"** (ex.: "Primeiro analise X, depois conclua Y"). Ajuda em tarefas que exigem raciocínio encadeado e torna a resposta mais consistente. |
| **Tree of Thought** | Explorar **múltiplos caminhos de raciocínio** antes de responder (ex.: considerar várias interpretações do bug e escolher a melhor). Útil quando há mais de uma forma válida de abordar o problema. |
| **Skeleton of Thought** | **Estruturar a resposta em etapas claras** (ex.: "1) Identifique a persona; 2) Redija a user story; 3) Liste os critérios"). O modelo preenche cada parte na ordem, melhorando completude e formato. |
| **ReAct** | **Raciocínio + Ação** para tarefas complexas: o modelo alterna entre pensar (Reasoning) e agir (Action), por exemplo consultar um passo ou fazer uma decisão intermediária. Comum em fluxos que exigem planejamento e execução. |
| **Role Prompting** | **Definir persona e contexto detalhado** (ex.: "Você é um Product Manager experiente em ágil"). Alinha tom, vocabulário e nível de detalhe às expectativas do papel, em vez de um assistente genérico. |

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) e API Key
- API Key da OpenAI ou do Google (Gemini), conforme o provider escolhido

### Configuração

1. **Clone o repositório** e crie o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure o arquivo `.env`** (copie de `.env.example`):

- `LANGSMITH_API_KEY` – obrigatório para pull, push e avaliação
- `USERNAME_LANGSMITH_HUB` – seu username no LangSmith Hub (necessário para pull e push)
- `PROMPT_KEY_PULL_FROM_LANGSMITH_HUB` – (opcional) chave do prompt a puxar do Hub (ex.: `bug_to_user_story_v1`). Salva em `prompts/{valor}.yml`. Padrão no `.env.example`: `bug_to_user_story_v1`.
- `PROMPT_KEY_PUSH_TO_LANGSMITH_HUB` – chave do prompt a enviar (ex.: `bug_to_user_story_v2`). O script usa `prompts/{valor}.yml` e a chave no YAML deve ser a mesma.
- `OPENAI_API_KEY` ou `GOOGLE_API_KEY` – conforme o provider
- `LLM_PROVIDER` – `openai` ou `google`
- `LLM_MODEL` e `EVAL_MODEL` – modelos a usar (ex.: `gpt-4o-mini` / `gpt-4o` ou `gemini-2.5-flash`)
- `EVAL_RATE_LIMIT_DELAY_SECONDS` – (opcional) delay em segundos entre cada chamada ao LLM no `evaluate.py`.
- `EVAL_PROMPT_LANGSMITH` – (opcional) caminho **completo** do prompt no LangSmith Hub (ex: `seu_username/bug_to_user_story_v2`). Se preenchido, o `evaluate.py` avalia esse prompt.
- `EVAL_PROMPT_LOCAL_FILE` – (opcional) caminho do arquivo YAML do prompt local (ex: `prompts/bug_to_user_story_v1.yml`). Se preenchido, avalia esse prompt.
- `EVAL_PROMPT_LOCAL_KEY` – (opcional) chave do prompt no YAML; se não informada, usa o nome do arquivo sem extensão.

Se **nenhuma** das duas (`EVAL_PROMPT_LANGSMITH` e `EVAL_PROMPT_LOCAL_FILE`) estiver preenchida, o script usa o padrão: **v2 do Hub** (`bug_to_user_story_v2`). Se **alguma** estiver preenchida, só os prompts indicados são avaliados (pode usar as duas ao mesmo tempo para comparar prompts).

### Ordem de execução

```bash
# 1. Pull do prompt do LangSmith (arquivo definido por PROMPT_KEY_PULL_FROM_LANGSMITH_HUB; ex.: salva em prompts/bug_to_user_story_v1.yml)
python src/pull_prompts.py

# 2. Refatorar o prompt: editar o arquivo que será enviado (ex.: prompts/bug_to_user_story_v2.yml)

# 3. Push do prompt otimizado (arquivo e chave definidos por PROMPT_KEY_PUSH_TO_LANGSMITH_HUB no .env)
python src/push_prompts.py

# 4. Avaliar o prompt no dataset (datasets/bug_to_user_story.jsonl)
python src/evaluate.py
```

### Validação com testes

```bash
pytest tests/test_prompts.py -v
```

Exemplo de saída (6 testes obrigatórios):

```text
===================================== test session starts =====================================
platform darwin -- Python 3.12.8, pytest-8.3.4
collected 6 items
tests/test_prompts.py::TestPrompts::test_prompt_has_system_prompt PASSED                [ 16%]
tests/test_prompts.py::TestPrompts::test_prompt_has_role_definition PASSED              [ 33%]
tests/test_prompts.py::TestPrompts::test_prompt_mentions_format PASSED                  [ 50%]
tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples PASSED            [ 66%]
tests/test_prompts.py::TestPrompts::test_prompt_no_todos PASSED                         [ 83%]
tests/test_prompts.py::TestPrompts::test_minimum_techniques PASSED                      [100%]
====================================== 6 passed in 0.02s ======================================
```

---

## Técnicas aplicadas no prompt v2

O prompt otimizado **v2** aplica várias técnicas da lista (Few-shot, CoT, Role Prompting, etc.). Abaixo está documentado o que foi feito no v2 e por quê.

### Prompt v2 (`prompts/bug_to_user_story_v2.yml`)

**Técnicas:** Role Prompting, Few-shot Learning, Chain-of-Thought (classificação), Template por tipo/complexidade, Separação de processo interno, Framework de complexidade.

- **Role Prompting:** Persona de *Product Manager Sênior* no system prompt, com abordagem **empática** (linguagem que demonstra compreensão do impacto do bug), profissional e focada em valor. Inclui **Guia de Personas** (tabela Tipo de Bug → Persona exata: ex. dashboard → "administrador visualizando o dashboard", carrinho → "cliente navegando na loja").
- **Few-shot Learning:** Vários exemplos completos (bug → User Story + Critérios Dado/Quando/Então) para SIMPLES, além de **tabelas de formato exato** por contexto (Dashboard/métricas, Browser, Performance, Cálculo, iOS). Reduz ambiguidade e fixa o formato desejado.
- **Chain-of-Thought (classificação):** Processo interno em passos: (1) classificar complexidade (SIMPLES / MODERADO / COMPLEXO), (2) identificar persona, (3) formular benefício, (4) escolher formato. Tabelas **Passo 1: Complexidade** e **Passo 2: Tipo** (TÉCNICO, SEGURANÇA, CÁLCULO, etc.) definem seções adicionais e formato de saída.
- **Template filling / Framework de complexidade:** Formatos distintos para SIMPLES (apenas User Story + 5 critérios), MODERADO (5–7 critérios + seções contextuais) e COMPLEXO (seções A/B/C/D). Regra explícita: bug SIMPLES = proibido adicionar Contexto Técnico, Tasks ou seções extras.
- **Separação de processo interno:** Instrução "PROCESSO INTERNO (não incluir na saída)" e "Sua resposta deve começar DIRETAMENTE com 'Como um...'" — o modelo analisa por dentro mas não despeja análise na saída.

Regras explícitas para critérios (mensuráveis, sem "corretamente"/"adequadamente"), exemplos de linguagem proibida vs. recomendada, e tratamento de edge cases (performance = meta de melhoria, CÁLCULO = R$ e operação matemática).

---

## Resultados Finais

Avaliação com **15 exemplos**, modelo gpt-4o-mini e avaliador gpt-4o. O **v1** é o baseline (pull do Hub); o **v2** é o prompt otimizado (técnicas aplicadas acima).

### Comparativo v1 (baseline) vs v2 (otimizado)

| Métrica       | v1 (baseline) | v2 (otimizado) | Δ    |
|---------------|---------------|----------------|------|
| Helpfulness   | 0,87 ✗        | 0,94 ✓          | +0,07 |
| Correctness   | 0,78 ✗        | 0,90 ✓          | +0,12 |
| F1-Score      | 0,72 ✗        | 0,88            | +0,16 |
| Clarity       | 0,89 ✗        | 0,95 ✓          | +0,06 |
| Precision     | 0,84 ✗        | 0,93 ✓          | +0,09 |
| **Média geral** | **0,8211**    | **0,9208**     | **+0,10** |
| **Status**    | ❌ REPROVADO   | ✅ APROVADO     | —    |

- **v1** (`bug_to_user_story_v1.yml`): média 0,82 — abaixo do critério 0,9.
- **v2** (`bug_to_user_story_v2.yml`): média 0,92 — atinge o critério de aprovação (média ≥ 0,9).

---

## Estrutura do projeto

```text
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
│
├── prompts/
│   ├── bug_to_user_story_v1.yml    # Prompt inicial (baseline); atualizado pelo pull
│   ├── bug_to_user_story_v2.yml    # Prompt otimizado (Role, Few-shot, CoT, template por complexidade)
│   └── (outros, conforme PROMPT_KEY_PUSH_TO_LANGSMITH_HUB)
│
├── datasets/
│   └── bug_to_user_story.jsonl     # Dataset de avaliação
│
├── src/
│   ├── pull_prompts.py             # Pull do LangSmith Hub
│   ├── push_prompts.py             # Push ao LangSmith Hub
│   ├── evaluate.py                 # Avaliação (métricas + LangSmith)
│   ├── metrics.py                  # Métricas (F1, Clarity, Precision, Tone, etc.)
│   └── utils.py                    # Helpers (YAML, env, validação)
│
└── tests/
    └── test_prompts.py             # Testes de validação do prompt v2
```

---

## Objetivo de cada script

### `src/pull_prompts.py`

**O que faz:** Baixa (pull) o prompt de **baixa qualidade** do LangSmith Prompt Hub para o seu ambiente local.

**Fluxo:** Conecta ao LangSmith com `LANGSMITH_API_KEY` e `USERNAME_LANGSMITH_HUB`, puxa o repositório definido por `PROMPT_KEY_PULL_FROM_LANGSMITH_HUB` (ex.: `franlauriano/bug_to_user_story_v1`), converte o template em estrutura legível e **salva em `prompts/{PROMPT_KEY_PULL_FROM_LANGSMITH_HUB}.yml`**. Assim você tem o prompt baseline para comparar e refatorar.

**Quando usar:** No início do desafio, para obter o prompt do Hub (ex.: v1) que será otimizado.

---

### `src/push_prompts.py`

**O que faz:** Publica o **prompt otimizado** (v2, v3, etc.) no LangSmith Prompt Hub, deixando-o disponível para avaliação e para outros.

**Fluxo:** Lê o arquivo e a chave definidos por `PROMPT_KEY_PUSH_TO_LANGSMITH_HUB` no `.env` (ex.: `bug_to_user_story_v2` → arquivo `prompts/bug_to_user_story_v2.yml`, chave `bug_to_user_story_v2` no YAML). Valida estrutura (system_prompt, user_prompt, etc.), monta um `ChatPromptTemplate` e faz **push público** para `{USERNAME_LANGSMITH_HUB}/{PROMPT_KEY_PUSH_TO_LANGSMITH_HUB}`. Inclui metadados como descrição, tags e técnicas aplicadas.

**Quando usar:** Depois de editar o prompt que será enviado (v2, v3, etc.). Se for avaliar pelo Hub, faça o push antes de rodar `evaluate.py`; se for avaliar só por YAML local, use `EVAL_PROMPT_LOCAL_FILE` com o caminho do arquivo e o push é opcional.

---

### `src/evaluate.py`

**O que faz:** **Avalia o prompt otimizado** em cima de um dataset real e calcula se ele atinge o critério de aprovação (média das métricas ≥ 0,9).

**Fluxo:**  
1. Carrega o dataset de `datasets/bug_to_user_story.jsonl` (15 bugs de exemplo).  
2. Cria ou reutiliza um dataset no LangSmith com esses exemplos.  
3. Carrega o(s) prompt(s) do Hub e/ou de arquivos locais (conforme `EVAL_PROMPT_LANGSMITH` e `EVAL_PROMPT_LOCAL_FILE`; se vazios, usa v2 do Hub).  
4. Para cada exemplo do dataset: gera a user story com o LLM e avalia com **F1-Score, Clarity e Precision** (LLM-as-Judge).  
5. Deriva Helpfulness e Correctness e exibe o resumo no terminal (média e status APROVADO/REPROVADO).

**Avaliar o v1 ou outros prompts:** Por padrão (sem env de prompt preenchida) o script avalia apenas o **v2** do Hub (`bug_to_user_story_v2`). Para avaliar o v1 local ou outros, defina no `.env` `EVAL_PROMPT_LOCAL_FILE` (ex.: `prompts/bug_to_user_story_v1.yml`) e/ou `EVAL_PROMPT_LANGSMITH` (ex.: `seu_username/bug_to_user_story_v2`).

**Diferença para o `metrics.py`:** O `evaluate.py` **gera** as respostas (prompt + LLM por exemplo) e depois usa as métricas; o `metrics.py` só calcula notas para textos já existentes (e no script usa exemplos fixos).

**Quando usar:** Depois do push (ou ao usar apenas YAML local); é o script que “diz” se o prompt está bom o suficiente.

---

### `src/metrics.py`

**O que faz:** **Módulo de métricas** usado pelo `evaluate.py` e também executável como script para **testar as métricas em exemplos fixos**.

**Conteúdo:**  
- **Parte 1 – Métricas gerais:** F1-Score (precision/recall), Clarity (clareza da resposta), Precision (informações corretas e relevantes).  
- **Parte 2 – Métricas específicas Bug → User Story:** Tone Score (tom profissional e empático), Acceptance Criteria Score (qualidade dos critérios Dado/Quando/Então), User Story Format Score (formato Como... Eu quero... Para que...), Completeness Score (completude e contexto).

O **`evaluate.py` usa só F1, Clarity e Precision** para o critério de aprovação; as outras quatro estão em `metrics.py` para análise detalhada. Rodar `python src/metrics.py` dispara um teste com exemplos fixos e imprime score + reasoning de cada métrica (útil para debug e para entender o que cada uma mede).

**Diferença em relação ao `evaluate.py`:** O `metrics.py` **não** carrega dataset, **não** puxa prompt do Hub e **não** gera respostas. Ele só **avalia** textos que já existem (pergunta + resposta + referência). O `evaluate.py` é quem **produz** as user stories (rodando o prompt + LLM para cada bug) e depois usa as funções do `metrics.py` para dar nota.

---

### `tests/test_prompts.py`

**O que faz:** **Testes automatizados** que garantem que o prompt v2 atende aos requisitos mínimos do desafio, sem precisar chamar a API.

**O que cada teste verifica:**  
- `test_prompt_has_system_prompt` — existe `system_prompt` e não está vazio.  
- `test_prompt_has_role_definition` — o prompt define uma persona (ex.: “Você é um Product Manager”).  
- `test_prompt_mentions_format` — exige formato User Story ou Markdown (Como... Eu quero... Para que... ou Dado/Quando/Então).  
- `test_prompt_has_few_shot_examples` — contém exemplos de entrada/saída (Few-shot).  
- `test_prompt_no_todos` — não há `[TODO]` esquecido no texto.  
- `test_minimum_techniques` — no YAML há ao menos 2 técnicas em `techniques_applied`.

**Quando usar:** Sempre que alterar o prompt otimizado (ex.: `prompts/bug_to_user_story_v2.yml`); rodar `pytest tests/test_prompts.py` garante que o prompt continua válido antes do push e da avaliação. (Os testes atuais validam o arquivo v2; para v3, ajuste `V2_FILE` e `PROMPT_KEY` em `test_prompts.py` ou duplique os testes.)

---

## Tecnologias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

### APIs

| Provider | Uso | Links |
|----------|-----|--------|
| **OpenAI** | `gpt-4o-mini` (resposta) / `gpt-4o` (avaliação) | [API Keys](https://platform.openai.com/api-keys) |
| **Google Gemini** | `gemini-2.5-flash` (resposta e avaliação) | [API Key](https://aistudio.google.com/app/apikey) |

Configure no `.env`: `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL`.

---

## Requisitos do desafio (resumo)

1. **Pull:** Script em `src/pull_prompts.py` que puxa o prompt do Hub (definido por `USERNAME_LANGSMITH_HUB` e `PROMPT_KEY_PULL_FROM_LANGSMITH_HUB`) e salva em `prompts/{PROMPT_KEY_PULL_FROM_LANGSMITH_HUB}.yml`.
2. **Otimização:** Criar/editar `prompts/bug_to_user_story_v2.yml` aplicando ao menos duas técnicas (Few-shot, CoT, Role Prompting, etc.) e documentar no README.
3. **Push:** Script em `src/push_prompts.py` que lê o prompt indicado por `PROMPT_KEY_PUSH_TO_LANGSMITH_HUB` (ex.: v2 ou v3), valida e publica como `{USERNAME_LANGSMITH_HUB}/{PROMPT_KEY_PUSH_TO_LANGSMITH_HUB}` (público).
4. **Avaliação:** `src/evaluate.py` usa o dataset em `datasets/bug_to_user_story.jsonl`, carrega o(s) prompt(s) do Hub e/ou de YAML local (variáveis `EVAL_PROMPT_LANGSMITH` e `EVAL_PROMPT_LOCAL_FILE`; se vazias, padrão v2 do Hub), roda as métricas e exibe o resumo. Aprovação: **média das 5 métricas ≥ 0,9**.
5. **Testes:** Em `tests/test_prompts.py`, os 6 testes exigidos (system_prompt, role, formato, few-shot, sem TODO, técnicas_applied).

---

## Entregável

Entregáveis do desafio:

1. **Repositório público** com código-fonte, prompt otimizado (ex.: `prompts/bug_to_user_story_v2.yml`) e README atualizado.
2. **README** contendo:
   - **Técnicas aplicadas no prompt v2** — quais técnicas de Prompt Engineering foram usadas e por quê.
   - **Resultados Finais** — tabela comparativa v1 (baseline) vs v2 (otimizado) com as 5 métricas, link do projeto no LangSmith e status (aprovado/reprovado).
   - **Como executar** — variáveis de ambiente, ordem de execução (pull → refatorar → push → avaliar) e uso dos scripts.
3. **Testes de validação** — 6 testes com pytest em `tests/test_prompts.py` (system_prompt, role, formato, few-shot, sem TODO, técnicas_applied).
4. **Implementação do pull** — script `src/pull_prompts.py` que baixa prompts do LangSmith Hub para YAML local.
5. **Implementação do push** — script `src/push_prompts.py` que publica os prompts otimizados no LangSmith Hub. Exemplo: [bug_to_user_story_v2](https://smith.langchain.com/hub/franlauriano/bug_to_user_story_v2).

---

## Referências

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
