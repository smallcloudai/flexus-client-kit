# Сова-Стратег: План Имплементации

## 📊 Текущее состояние (обновлено)

| Этап | Статус | Комментарий |
|------|--------|-------------|
| 1. Скелет бота | ✅ | `__init__.py`, `_bot.py`, `_install.py`, `_prompts.py` |
| 2. Промпты агентов | ✅ | 8 промптов: DEFAULT + 7 агентов |
| 3. Lark kernels | ✅ | AGENT_LARK для субчатов |
| 4. Tools + handlers | ✅ | `run_agent`, `rerun_agent` + subchats |
| 5. Install.py | ✅ | 8 skills зарегистрировано |
| 6. Default prompt | ✅ | Human-in-the-loop flow описан |
| 7. Knowledge items | ⏭️ | ПРОПУСКАЕМ |
| 8. Тестирование | ⬜ | Следующий шаг |

### Важно: Backend cloudtools

`get_knowledge` и `create_knowledge` — это **backend cloudtools**, они:
- Регистрируются автоматически сервисом `service_cloudtool_knowledge.py`
- Доступны всем ботам через `cloud_tools_discovery_procedure`
- **НЕ нужно** добавлять в TOOLS бота — только упоминать в промптах

---

## Соответствие правилам Flexus (FLEXUS_PROJECT_RULES.mdc)

### Структура файлов бота (строго по правилам):
```
owl_strategist/
├── __init__.py                    # Package marker ✅
├── owl_strategist_bot.py          # BOT_NAME, BOT_VERSION, TOOLS, main loop, handlers ✅
├── owl_strategist_install.py      # Skills + imports TOOLS from _bot.py ✅
├── owl_strategist_prompts.py      # Prompts for all skills ✅
├── owl_strategist-1024x1536.webp  # Marketplace image (< 0.3M) — позже
├── owl_strategist-256x256.webp    # Avatar (transparent/white background) — позже
└── docs/
    ├── planing/                   # Existing methodology (phases 0-5)
    └── implementation-plan.md     # This file
```

### Ключевые правила которым следуем:

| Правило | Как соблюдаем |
|---------|---------------|
| Tools в _bot.py | `TOOLS = [...]` определяется в owl_strategist_bot.py |
| Install импортирует из bot | `from .owl_strategist_bot import TOOLS` |
| Нет docstrings | Комментарии только для tricks/hacks/XXX |
| Короткие локальные переменные | `t`, `r`, `args` вместо `toolcall_result` |
| Импорты вверху | Никаких import внутри функций |
| Prefixes в именах | `strategy_name`, не `name` |
| try..finally в main loop | Для корректного shutdown |
| Не ловить Exception | Только конкретные исключения |

## Skills (8 штук)

| Skill | Назначение | Lark Kernel |
|-------|-----------|-------------|
| `default` | Оркестратор, диалог с человеком | Нет |
| `diagnostic` | Agent A: анализ гипотезы | Возвращает JSON |
| `segment` | Agent B: ICP/JTBD/CJM | Возвращает JSON |
| `messaging` | Agent C: ценность/позиционирование | Возвращает JSON |
| `channels` | Agent D: каналы/эксперименты | Возвращает JSON |
| `tactics` | Agent E: ТЗ/кампании/креативы | Возвращает JSON |
| `compliance` | Agent F: риски/policies | Возвращает JSON |
| `metrics` | Agent G: KPI/MDE/stop-rules | Возвращает JSON |

## Tools для default skill

| Tool | Источник | Назначение |
|------|----------|-----------|
| `run_agent` | bot.py | Запускает конкретного агента после обсуждения |
| `rerun_agent` | bot.py | Перезапускает агента с feedback |
| `flexus_policy_document` | fi_pdoc | CRUD для policy documents |
| `get_knowledge` | backend cloudtool | RAG поиск по knowledge base |
| `create_knowledge` | backend cloudtool | Создание записей в knowledge base |

---

# ЭТАП 1: Скелет бота (базовая структура) ✅ ВЫПОЛНЕН

**Цель:** Создать работающий бот с одним skill (default), без агентов.

**Файлы:**
- `__init__.py` — пустой, package marker
- `owl_strategist_bot.py` — BOT_NAME, BOT_VERSION, TOOLS, main loop
- `owl_strategist_install.py` — только default skill
- `owl_strategist_prompts.py` — только default prompt

**Обязательные константы в `_bot.py`:**
```python
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

BOT_NAME = "owl_strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)
```

**Что делает:**
- Бот запускается
- Может вести диалог
- Работает policy_document tool
- Работает get_knowledge tool

**Проверка:**
```bash
python -m flexus_simple_bots.owl_strategist.owl_strategist_install --ws <ws_id>
python -m flexus_simple_bots.owl_strategist.owl_strategist_bot --group <group_id>
```

---

# ЭТАП 2: Промпты для агентов (A-G) ✅ ВЫПОЛНЕН

**Цель:** Написать системные промпты для всех 7 агентов на основе phase2.md и phase5.md.

**Файлы:**
- `owl_strategist_prompts.py` — добавить промпты для каждого skill

**Структура каждого промпта:**
```python
AGENT_X_PROMPT = """
# Your Role
You are Agent X responsible for [specific task].

# Input
You receive:
- /strategies/{name}/input.json — исходный запрос от фаундера
- /strategies/{name}/[previous_agent].json — результаты предыдущих агентов (если есть)
- Knowledge items по запросу

# Your Task
[Детальное описание задачи из phase2.md]

# Output Format
You MUST output valid JSON matching this structure:
{output_schema}

# Critical Rules
- Use get_knowledge() to fetch relevant benchmarks/patterns
- Save result via flexus_policy_document(op="create", ...)
- End with AGENT_COMPLETE when done
"""
```

**JSON схемы выхода:** Взять из phase4.md (SovaStrategyResponse).

---

# ЭТАП 3: Lark kernels для субчатов ✅ ВЫПОЛНЕН

**Цель:** Создать Lark kernels которые возвращают subchat_result.

**Файлы:**
- `owl_strategist_install.py` — добавить Lark для каждого agent skill

**Шаблон Lark kernel:**
```python
AGENT_LARK = '''
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"])
    if "AGENT_COMPLETE" in content:
        # Извлекаем JSON результат
        subchat_result = content
    elif len(msg["tool_calls"]) == 0:
        post_cd_instruction = "You must complete the analysis. Call get_knowledge if needed, then output your analysis ending with AGENT_COMPLETE."
'''
```

---

# ЭТАП 4: Tools и pipeline orchestration ✅ ВЫПОЛНЕН

**Цель:** Реализовать tools для запуска pipeline с state machine.

**Файлы:**
- `owl_strategist_bot.py` — Tools + handlers (всё в одном файле по правилам!)

## Tools:

### 1. start_pipeline
```python
START_PIPELINE_TOOL = CloudTool(
    name="start_pipeline",
    description="Start analysis pipeline. Initializes state and runs first agent (diagnostic).",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "kebab-case name for this strategy"},
        },
        "required": ["strategy_name"],
    },
)
```

### 2. continue_pipeline
```python
CONTINUE_PIPELINE_TOOL = CloudTool(
    name="continue_pipeline",
    description="Continue pipeline to next agent. Call this after receiving subchat result.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "Strategy name to continue"},
        },
        "required": ["strategy_name"],
    },
)
```

### 3. rerun_agent
```python
RERUN_AGENT_TOOL = CloudTool(
    name="rerun_agent",
    description="Rerun specific agent with feedback for corrections.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "Strategy name"},
            "agent": {"type": "string", "enum": ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]},
            "feedback": {"type": "string", "description": "What to change/improve"},
        },
        "required": ["strategy_name", "agent", "feedback"],
    },
)
```

## Handlers:

```python
AGENTS_ORDER = ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]

@rcx.on_tool_call("start_pipeline")
async def start_pipeline(toolcall, args):
    strategy_name = args["strategy_name"]
    
    # Проверяем что input.json существует
    input_exists = await pdoc_integration.pdoc_exists(f"/strategies/{strategy_name}/input.json")
    if not input_exists:
        return "Error: /strategies/{strategy_name}/input.json not found. Collect input first."
    
    # Инициализируем state
    state = {
        "current_idx": 0,
        "agents_order": AGENTS_ORDER,
        "completed": [],
        "status": "running"
    }
    await pdoc_integration.pdoc_create(
        f"/strategies/{strategy_name}/_state.json",
        json.dumps(state, indent=2),
        toolcall.fcall_ft_id,
    )
    
    # Запускаем первого агента
    first_agent = AGENTS_ORDER[0]
    await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking=f"owl_{first_agent}",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Strategy: {strategy_name}"],
        first_calls=["null"],
        title=[f"{first_agent.title()} Analysis"],
        fcall_id=toolcall.fcall_id,
        skill=first_agent,
    )
    raise ckit_cloudtool.WaitForSubchats()


@rcx.on_tool_call("continue_pipeline")
async def continue_pipeline(toolcall, args):
    strategy_name = args["strategy_name"]
    
    # Читаем state
    state_content = await pdoc_integration.pdoc_read(f"/strategies/{strategy_name}/_state.json")
    state = json.loads(state_content)
    
    # Обновляем completed
    current_agent = state["agents_order"][state["current_idx"]]
    state["completed"].append(current_agent)
    state["current_idx"] += 1
    
    # Проверяем есть ли следующий
    if state["current_idx"] >= len(state["agents_order"]):
        state["status"] = "completed"
        await pdoc_integration.pdoc_update(
            f"/strategies/{strategy_name}/_state.json",
            json.dumps(state, indent=2),
            toolcall.fcall_ft_id,
        )
        return "Pipeline completed! All agents finished. Show results to user."
    
    # Сохраняем обновлённый state
    await pdoc_integration.pdoc_update(
        f"/strategies/{strategy_name}/_state.json",
        json.dumps(state, indent=2),
        toolcall.fcall_ft_id,
    )
    
    # Запускаем следующего агента
    next_agent = state["agents_order"][state["current_idx"]]
    await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking=f"owl_{next_agent}",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Strategy: {strategy_name}"],
        first_calls=["null"],
        title=[f"{next_agent.title()} Analysis"],
        fcall_id=toolcall.fcall_id,
        skill=next_agent,
    )
    raise ckit_cloudtool.WaitForSubchats()
```

## КРИТИЧНО: Human-in-the-Loop на каждом шаге

### Flow для КАЖДОГО агента:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ФАЗА 1: ОБСУЖДЕНИЕ ДО ЗАПУСКА                                              │
│                                                                              │
│  Сова: "Сейчас будем анализировать гипотезу. На этом шаге я:                │
│         - Классифицирую тип гипотезы (ценность/сегмент/канал/...)           │
│         - Определю что реально тестируется                                  │
│         - Оценю уровень неопределённости                                    │
│         - Выявлю ключевые unknown'ы                                         │
│                                                                              │
│         Есть что-то важное про вашу гипотезу, что я должна учесть?          │
│         Может, вы уже знаете какие-то инсайты или есть ограничения?"        │
│                                                                              │
│  Пользователь: добавляет контекст, уточняет, или говорит "ок, погнали"      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ФАЗА 2: ЗАПУСК СУБЧАТА                                                     │
│                                                                              │
│  Сова вызывает start_pipeline() или continue_pipeline()                     │
│  Субчат выполняет работу автономно                                          │
│  Результат сохраняется в policy document                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ФАЗА 3: ОБЪЯСНЕНИЕ И ОБСУЖДЕНИЕ РЕЗУЛЬТАТА                                 │
│                                                                              │
│  Сова: "Готово! Вот что получилось:                                         │
│                                                                              │
│         Тип гипотезы: VALUE (проверяем ценность продукта)                   │
│         Почему: вы говорите '10 часов экономии' — это про выгоду,           │
│                 не про сегмент и не про канал.                              │
│                                                                              │
│         Неопределённость: MEDIUM                                            │
│         Почему: есть конкуренты в нише, но ваш angle уникален.              │
│                                                                              │
│         Ключевые unknowns:                                                  │
│         - Поверят ли в цифру '10 часов'?                                    │
│         - Важнее время или деньги для этого сегмента?                       │
│                                                                              │
│         Что думаете? Всё верно или что-то нужно скорректировать?"           │
│                                                                              │
│  Пользователь: "Всё ок" / "Поменяй X на Y потому что..."                    │
│                                                                              │
│  Если правки → Сова вызывает rerun_agent() с feedback                       │
│  Если ок → переход к Фазе 1 следующего агента                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Это НЕ автоматический pipeline!

Lark kernel НЕ должен автоматически вызывать continue_pipeline().
Вместо этого — Сова объясняет результат и ждёт подтверждения от пользователя.

```python
DEFAULT_LARK = '''
# Пустой или минимальный Lark — всё управление через диалог
'''
```

### Обновлённые tools (определяются в owl_strategist_bot.py):

```python
# owl_strategist_bot.py

RUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    name="run_agent",
    description="Run specific agent. Call ONLY after discussing with user what will be done.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string"},
            "agent": {"type": "string", "enum": ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]},
            "user_additions": {"type": "string", "description": "Important context from user to consider"},
        },
        "required": ["strategy_name", "agent"],
    },
)

RERUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    name="rerun_agent",
    description="Rerun agent with corrections after user feedback.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string"},
            "agent": {"type": "string"},
            "feedback": {"type": "string", "description": "What to change based on user feedback"},
        },
        "required": ["strategy_name", "agent", "feedback"],
    },
)

# КРИТИЧНО: TOOLS экспортируется для install.py
TOOLS = [
    RUN_AGENT_TOOL,
    RERUN_AGENT_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]
```

```python
# owl_strategist_install.py — импортирует из _bot.py

from flexus_simple_bots.owl_strategist import owl_strategist_bot

# Используем TOOLS из _bot.py (не дублируем определения!)
bot_internal_tools = json.dumps([t.openai_style_tool() for t in owl_strategist_bot.TOOLS])
```

### Промпт оркестратора должен явно требовать:

```
## CRITICAL: Discussion Before Each Agent

NEVER run an agent without first:
1. Explaining what this agent will do (in simple terms, no textbook quotes)
2. Listing what fields/decisions will be made
3. Asking if user has important context to add

AFTER agent completes:
1. Explain the logic behind each decision (why this, not that)
2. Ask if results look correct
3. Only proceed to next agent after explicit approval

If user wants changes → call rerun_agent() with their feedback
If user approves → discuss next agent before running it
```

---

# ЭТАП 5: Registration (install.py)

**Цель:** Зарегистрировать все skills в marketplace.

**Файлы:**
- `owl_strategist_install.py` — полная версия с 8 skills

**КРИТИЧНО: Импортируем TOOLS из _bot.py (не дублируем!):**
```python
from flexus_simple_bots.owl_strategist import owl_strategist_bot, owl_strategist_prompts

# Tools определены в _bot.py, здесь только используем
bot_tools_json = json.dumps([t.openai_style_tool() for t in owl_strategist_bot.TOOLS])
```

**Структура:**
```python
marketable_experts=[
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=owl_strategist_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_app_capture_tools=bot_tools_json,
    )),
    ("diagnostic", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=owl_strategist_prompts.DIAGNOSTIC_PROMPT,
        fexp_python_kernel=AGENT_LARK,
        fexp_block_tools="run_agent,rerun_agent",  # агенты не могут запускать других агентов
        fexp_allow_tools="",
        fexp_app_capture_tools=bot_tools_json,
    )),
    # ... остальные 6 агентов аналогично ...
]
```

---

# ЭТАП 6: Default prompt (оркестратор)

**Цель:** Написать промпт для оркестратора который ведёт диалог с человеком.

**Ключевые обязанности:**
1. Собрать input от фаундера (SovaStrategyRequest из phase4.md)
2. Сохранить в /strategies/{name}/input.json
3. Получить подтверждение на начало анализа
4. ДЛЯ КАЖДОГО АГЕНТА: обсудить → запустить → объяснить → утвердить
5. Финализировать стратегию

**Flow в промпте:**
```
## Phase 1: Input Collection

Ask founder about their hypothesis, product, target audience.
Fill SovaStrategyRequest structure step by step.
Save to policy document when each section is complete.

## Phase 2: Confirmation of Input

Show summary of collected input.
Ask: "This is what I understood. Anything to add or correct?"

## Phase 3: Agent-by-Agent Analysis (7 agents)

For EACH agent in order [diagnostic → metrics → segment → messaging → channels → tactics → compliance]:

### Before running:
- Explain what this agent will analyze (simple terms, no jargon)
- List what decisions/fields will be filled
- Ask: "Any important context I should know before analyzing?"

### Run agent:
- Call run_agent(strategy_name, agent, user_additions)
- Wait for subchat result

### After agent completes:
- Read the saved result from policy document
- Explain each decision with reasoning (why this, not that)
- Ask: "Does this look right? Anything to adjust?"

### Handle response:
- If user approves → proceed to next agent discussion
- If user wants changes → call rerun_agent() with feedback, then re-explain

## Phase 4: Final Review

After all 7 agents complete:
- Show complete strategy summary
- Ask for final approval
- If approved → "Strategy ready! Here's your full document."
```

**Порядок агентов и что каждый делает (для промпта):**

| # | Agent | Простое объяснение для пользователя |
|---|-------|-------------------------------------|
| 1 | diagnostic | "Разберёмся что именно тестируем и какие риски" |
| 2 | metrics | "Определим KPI, когда остановить тест, когда масштабировать" |
| 3 | segment | "Уточним кто ваш клиент, их боли и мотивации" |
| 4 | messaging | "Сформулируем ценностное предложение и ключевые месседжи" |
| 5 | channels | "Выберем каналы и спроектируем эксперимент" |
| 6 | tactics | "Детальное ТЗ: кампании, креативы, лендинг" |
| 7 | compliance | "Проверим риски и соответствие политикам рекламных платформ" |

---

# ЭТАП 7: Knowledge items (domain expertise) ПРОПУСКАЕМ

**Цель:** Наполнить knowledge base данными из methodology.

**Источники:**
- phase0.md → общие принципы
- phase1.md → структура входных данных
- phase2.md → reasoning chain
- phase3.md → структура выхода
- phase4.md → JSON schemas
- phase5.md → спецификации агентов

**Формат knowledge items:**
```
Topic: Channel Benchmarks - Meta Ads
Content: CPM ranges by industry: SaaS $15-40, E-commerce $8-20...

Topic: JTBD Patterns - Side Hustlers
Content: Functional jobs: validate idea fast, launch with minimal time...

Topic: Ads Policies - Meta Prohibited Content
Content: No exaggerated claims, no before/after without disclaimer...
```

**Как добавить:** Через UI Flexus или скриптом через API.

---

# ЭТАП 8: Тестирование и сценарии

**Цель:** Создать тестовые сценарии.

**Файлы:**
- `owl_strategist__s1.yaml` — happy path: SaaS idea validation

**Сценарий s1:**
1. User описывает SaaS идею
2. Сова собирает input
3. User подтверждает
4. Pipeline запускается
5. Результат показывается
6. User просит изменить messaging
7. Agent C перезапускается
8. Финальный результат утверждается

---

# Порядок выполнения

| # | Этап | Зависимости | Примерное время |
|---|------|-------------|-----------------|
| 1 | Скелет бота | — | 30 мин |
| 2 | Промпты агентов | phase2.md, phase5.md | 2 часа |
| 3 | Lark kernels | Этап 2 | 30 мин |
| 4 | Tools + pipeline | Этап 3, проверка API | 1-2 часа |
| 5 | Install.py | Этап 2-4 | 30 мин |
| 6 | Default prompt | Этап 4, phase1.md, phase4.md | 1 час |
| 7 | Knowledge items | — (можно параллельно) | 2+ часа |
| 8 | Тестирование | Всё выше | 1+ час |

---

# Результаты проверки API

## bot_subchat_create_multiple — ОДИН skill для всех субчатов!

```python
async def bot_subchat_create_multiple(
    ...
    skill: str,  # <-- ОДИН skill, не список!
    ...
)
```

**Следствие:** Нельзя запустить 7 агентов с разными skills в одном вызове.

## Решение: State Machine через Policy Documents

### Как работает:

1. Оркестратор создаёт `/strategies/{name}/_pipeline_state.json`:
```json
{
  "current_agent": "diagnostic",
  "agents_order": ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"],
  "completed": [],
  "status": "running"
}
```

2. Оркестратор запускает ОДИН субчат с skill="diagnostic"

3. Субчат diagnostic:
   - Читает input.json
   - Делает анализ
   - Сохраняет результат в diagnostic.json
   - Lark kernel возвращает "AGENT_COMPLETE:diagnostic"

4. Оркестратор получает результат:
   - Обновляет _pipeline_state.json (completed += "diagnostic", current_agent = "metrics")
   - Запускает следующий субчат с skill="metrics"

5. Повторяется пока все агенты не завершены

### Реализация в bot code:

```python
@rcx.on_tool_call("run_full_pipeline")
async def run_pipeline(toolcall, args):
    strategy_name = args["strategy_name"]
    
    # Инициализируем state
    state = {
        "current_agent": "diagnostic",
        "agents_order": ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"],
        "completed": [],
        "status": "running"
    }
    await pdoc_integration.pdoc_create(
        f"/strategies/{strategy_name}/_pipeline_state.json",
        json.dumps(state),
        toolcall.fcall_ft_id,
    )
    
    # Запускаем первого агента
    await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking="owl_diagnostic",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Analyze strategy '{strategy_name}'"],
        first_calls=["null"],
        title=["Diagnostic Analysis"],
        fcall_id=toolcall.fcall_id,
        skill="diagnostic",
    )
    raise ckit_cloudtool.WaitForSubchats()
```

### Проблема: Как запустить следующего агента?

После WaitForSubchats() результат возвращается в исходный чат как tool response. 
Нужен механизм для продолжения pipeline.

**Вариант A: Отдельный tool для каждого агента**
```python
# Оркестратор вызывает: run_diagnostic() → run_metrics() → run_segment() → ...
# Каждый tool = один субчат
# Но это требует чтобы модель понимала последовательность
```

**Вариант B: Один tool с циклом (рекурсивный вызов)**
```python
# Tool "continue_pipeline" вызывается после каждого субчата
# Проблема: модель должна сама вызвать этот tool
```

**Вариант C: Lark kernel в default skill**
```python
# После получения результата субчата, Lark проверяет state
# Если есть следующий агент → post_cd_instruction = "Call continue_pipeline()"
```

**Рекомендую Вариант C** — Lark в default skill управляет pipeline.

---

# Обновлённая архитектура Этапа 4

## Lark kernel для default skill:

```python
DEFAULT_LARK = '''
msg = messages[-1]
if msg["role"] == "tool":
    content = str(msg["content"])
    if "AGENT_COMPLETE:" in content:
        # Агент завершился, нужно запустить следующего
        post_cd_instruction = "An agent completed. Call continue_pipeline() to proceed with the next agent, or show results if all done."
'''
```

## Tools:

1. **start_pipeline(strategy_name)** — инициализирует state, запускает первого агента
2. **continue_pipeline()** — читает state, запускает следующего агента или возвращает "all done"

---

# Открытые вопросы

1. ~~bot_subchat_create_multiple — разные skills?~~ **ОТВЕТ: Нет, один skill**

2. **Размер контекста** — хватит ли контекста агенту чтобы прочитать input.json + knowledge items + выдать результат?

3. ~~Картинки~~ — сделают без нас

---

# Начинаем с Этапа 1

Готов начать? Скажи "давай этап 1" и я создам базовую структуру файлов.

