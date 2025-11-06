# Productman A2 Analysis: Current State vs Target

## Executive Summary

**A2 Activity**: "Сгенерировать и приоритизировать гипотезы о проблеме"

**Current Coverage**: ~10% (есть только старый template_hypothesis для гипотез, но без методологии, без Challenge Loop, без приоритизации)

**Required Work**: 
- 1 новый артефакт (Problem Hypothesis List с приоритизацией)
- 3-4 новых tool (web_research, counter_example, score_matrix, обновление validate_artifact)
- Обновление промпта с методологией формулировки гипотез, Challenge Loop, приоритизацией ICE
- Добавление workflow A21-A24 (извлечение → оппонирование → приоритизация → валидация)

---

## 1. Что НУЖНО ДОБАВИТЬ (новое)

### 1.1. Problem Hypothesis List (артефакт)

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Структурированный список проблемных гипотез, извлечённых из Idea Framing Sheet, с приоритизацией по матрице Impact × Evidence × Feasibility.

**Структура** (из документации):
```json
{
  "source_idea_framing_sheet_id": "idea_001",
  "hypotheses": [
    {
      "hypothesis_id": "H1",
      "formulation": "Our customer [segment] wants [goal], but cannot [action], because [reason]",
      "segment": "Specific customer segment",
      "goal": "What customer wants to achieve",
      "barrier": "What prevents them",
      "reason": "Why barrier exists (ONE assumption only)",
      "challenge_log": [
        {
          "iteration": 1,
          "counterexample": "...",
          "refinement": "..."
        }
      ],
      "priority_scores": {
        "impact": 5,
        "evidence": 4,
        "feasibility": 5,
        "weighted_score": 4.6
      },
      "research_evidence": [
        {"source_url": "...", "snippet": "..."}
      ],
      "validation_status": "draft | challenged | validated | selected"
    }
  ],
  "prioritization_date": "2025-11-04T10:30:00Z",
  "selected_hypothesis_id": "H1"
}
```

**Ключевые отличия от текущего hypothesis template**:
- Канонический формат: "Our customer [segment] wants [goal], but cannot [action], because [reason]"
- Приоритизационные оценки (Impact, Evidence, Feasibility)
- Challenge log (история оппонирования)
- Research evidence (ссылки на веб-исследование)
- Validation status workflow

**Что делать**:
- Создать tool `generate_problem_hypotheses` для генерации списка гипотез из Idea Framing Sheet
- Сохранять в `/customer-research/{idea-name}/hypotheses/problem-list`

**Приоритет**: 🔴 HIGH (критично для A2, блокирует A21-A24)

---

### 1.2. Web Research Tool

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Tool для поиска доказательств (evidence) существования проблемы в публичных источниках (форумы, Reddit, Twitter, блоги, отчёты).

**Зачем**: Для оценки Evidence score (0-5) в приоритизации гипотез.

**Функционал**:
- Принимает query (проблема + сегмент)
- Возвращает список ссылок + snippets с упоминаниями проблемы
- Используется в A21 (после извлечения гипотез) для поиска доказательств

**Реализация**:
- Либо использовать существующий web_search tool из ckit (если есть)
- Либо добавить новый через ckit_cloudtool
- Handler должен парсить результаты и форматировать как `research_evidence[]`

**Приоритет**: 🟡 MEDIUM (можно начать без веб-исследования, просто ставить Evidence = 3 по умолчанию)

---

### 1.3. Challenge Loop Mechanism (Counter Example)

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Механизм оппонирования гипотез — создание контрпримера для выявления неточностей в формулировке.

**Как работает**:
1. Фаундер/бот предлагает гипотезу
2. Challenger (LLM) придумывает бизнес/сервис, который **буквально выполняет гипотезу**, но приводит к противоположному результату
3. Фаундер видит парадокс и уточняет формулировку
4. Повтор до тех пор, пока гипотеза не становится конкретной и фальсифицируемой

**Пример**:
```
Гипотеза: "Founders want faster campaigns"

Контрпример: "A service that launches campaigns in 1 second by sending spam to random people."

Issue Revealed: "Faster" without quality/effectiveness constraint is meaningless.

Refined: "Founders want to launch qualified, targeted campaigns in <1 week (vs 2-4 weeks currently),
          but cannot build lead lists fast enough,
          because they lack access to accurate B2B contact data."
```

**Что реализовать**:
- Добавить tool `challenge_hypothesis` (принимает hypothesis, возвращает counterexample)
- Либо интегрировать в основной промпт как инструкцию для LLM (без отдельного tool)
- Сохранять challenge_log в структуре гипотезы

**Приоритет**: 🟡 MEDIUM (можно начать без Challenge Loop, просто генерировать гипотезы напрямую)

---

### 1.4. Prioritization Tool (Score Matrix)

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Tool для оценки и ранжирования гипотез по матрице Impact × Evidence × Feasibility.

**Функционал**:
- Принимает список гипотез
- Для каждой гипотезы оценивает Impact (0-5), Evidence (0-5), Feasibility (0-5)
- Вычисляет weighted_score = 0.4×Impact + 0.4×Evidence + 0.2×Feasibility
- Ранжирует по убыванию score
- Возвращает таблицу с оценками и рекомендацией

**Реализация**:
- Добавить tool `prioritize_hypotheses` (принимает problem-list path, возвращает prioritized table)
- Handler использует LLM для оценки каждого критерия (prompt с правилами оценки)
- Обновляет problem-list с priority_scores

**Приоритет**: 🔴 HIGH (критично для A23, без этого нет приоритизации)

---

### 1.5. Методология Problem Hypothesis Formulation в промпте

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Инструкции для LLM как формулировать проблемные гипотезы по каноническому формату.

**Что добавить в `productman_prompts.py`**:
- Раздел "Problem Hypothesis Formulation Rules" (из `problem-hypothesis-formulation-rules.md`)
- Канонический формат: "Our customer [segment] wants [goal], but cannot [action], because [reason]"
- Правила:
  - Rule 1: Single Assumption (только одна причина на гипотезу)
  - Rule 2: Goal is Outcome, Not Method (цель = результат, не метод)
  - Rule 3: Testability (причина должна быть проверяемой)
  - Rule 4: Specificity (конкретика, не лозунги)
- Примеры хороших/плохих гипотез
- Challenge Loop workflow

**Объем**: ~100 строк текста в промпт

**Приоритет**: 🔴 HIGH (критично для A21, определяет качество гипотез)

---

### 1.6. Validation Criteria для Problem Hypothesis List

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Критерии валидации для списка проблемных гипотез (A24).

**Что реализовать**:
- Добавить `PROBLEM_HYPOTHESIS_LIST_VALIDATION_CRITERIA` в `productman_prompts.py`
- Critical criteria:
  - C1: Формат строго "Our customer [segment]..." (hypothesis_format)
  - C2: Каждая гипотеза содержит ОДНУ причину (single_assumption)
  - C3: Причина тестируема (testable)
  - C4: Нет дубликатов (unique)
- Warning criteria:
  - W1: Меньше 3 гипотез (minimum_count)
  - W2: Нет research_evidence (scores_not_justified)
  - W3: Все оценки одинаковые (suspicious_uniformity)

**Приоритет**: 🟡 MEDIUM (можно начать без валидации, просто генерировать и показывать)

---

## 2. Что НУЖНО ИЗМЕНИТЬ (из существующего)

### 2.1. HYPOTHESIS_TEMPLATE_TOOL → обновить или оставить для solution hypotheses

**Текущая структура** (`productman_bot.py` lines 38-51):
- Создает skeleton hypothesis file в `/customer-research/{idea-name}-hypotheses/{hypothesis-name}`
- Структура: section01-04 (ICP, Customer Context, Solution Hypothesis, Validation Strategy)

**Проблемы**:
- ❌ Это структура для **solution hypotheses** (A3), не для **problem hypotheses** (A2)
- ❌ Нет канонического формата "Our customer [segment] wants [goal]..."
- ❌ Нет приоритизационных полей
- ❌ Нет challenge_log

**Что изменить**:

**Вариант A**: Оставить как есть для A3, создать новый tool для A2
```python
# Оставить HYPOTHESIS_TEMPLATE_TOOL для solution hypotheses (A3)
# Добавить GENERATE_PROBLEM_HYPOTHESES_TOOL для problem hypotheses (A2)
```

**Вариант B**: Переделать на Problem Hypothesis List
```python
PROBLEM_HYPOTHESIS_TOOL = ckit_cloudtool.CloudTool(
    name="generate_problem_hypotheses",
    description="Generate Problem Hypothesis List from Idea Framing Sheet. Path: /customer-research/{idea-name}/hypotheses/problem-list",
    parameters={...}
)
```

**Рекомендация**: Вариант A (оставить старый для A3, добавить новый для A2) — меньше breaking changes, чётко разделены problem vs solution hypotheses.

**Приоритет**: 🔴 HIGH (критично для A2)

---

### 2.2. Обновить VALIDATE_ARTIFACT_TOOL для Problem Hypothesis List

**Текущая реализация** (`productman_bot.py` lines 72-90):
- Валидирует только Canvas и Sheet
- artifact_type: enum ["canvas", "sheet"]

**Что добавить**:
- Добавить "problem-hypothesis-list" в enum artifact_type
- Добавить `PROBLEM_HYPOTHESIS_LIST_VALIDATION_CRITERIA` в промпт
- Handler должен валидировать:
  - Формат каждой гипотезы
  - Single assumption
  - Testability
  - Минимум 3 гипотезы
  - Наличие priority_scores

**Приоритет**: 🟡 MEDIUM (можно начать без валидации)

---

### 2.3. Обновить промпт `productman_prompt`

**Текущий промпт** (`productman_prompts.py` lines 148-311):
- Объясняет только A1 (Canvas → Sheet → Validation)
- Упоминает A2 как "Future Phases (Not Yet Implemented)"

**Что добавить**:

1. **Методология Problem Hypothesis Formulation** (~100 lines):
   - Канонический формат
   - Rule 1-4 (Single Assumption, Goal is Outcome, Testability, Specificity)
   - Примеры хороших/плохих гипотез
   - Challenge Loop workflow

2. **Процесс A2** (~80 lines):
   ```
   ## Your A2 Workflow (Problem Hypothesis Generation & Prioritization)
   
   Step 1 (A21): Extract Problem Hypotheses from Idea Framing Sheet
   - Use generate_problem_hypotheses(idea_name="...")
   - Read core_problem, key_assumptions from Sheet
   - Generate 3-7 hypotheses covering different angles (time, skill, access, cost)
   - Format: "Our customer [segment] wants [goal], but cannot [action], because [reason]"
   
   Step 2 (A22): Challenge Loop (Optional but Recommended)
   - For each hypothesis, create counterexample
   - Ask user: "What if [counterexample]? Would your hypothesis still hold?"
   - Refine based on user feedback
   - Log iterations in challenge_log
   
   Step 3 (A23): Prioritize Hypotheses
   - Use prioritize_hypotheses(problem_list_path="...")
   - Score each hypothesis:
     * Impact (0-5): How significant is this problem?
     * Evidence (0-5): How much evidence exists?
     * Feasibility (0-5): How easy to test?
   - Calculate weighted_score = 0.4×Impact + 0.4×Evidence + 0.2×Feasibility
   - Rank by score descending
   
   Step 4 (A24): Validate and Select
   - Use validate_artifact(artifact_path="...", artifact_type="problem-hypothesis-list")
   - Check: format correct? single assumption? testable? ≥3 hypotheses?
   - If PASS → Present top 3 to user for selection
   - If FAIL → Fix issues, re-validate
   ```

3. **Обновить Path Structure**:
   ```
   /customer-research/{idea-name}/canvas                      # First Principles Canvas (A1)
   /customer-research/{idea-name}/sheet                       # Idea Framing Sheet (A1)
   /customer-research/{idea-name}/hypotheses/problem-list     # Problem Hypothesis List (A2)
   /customer-research/{idea-name}/hypotheses/{solution-name}  # Solution Hypotheses (future A3)
   /customer-research/{idea-name}/surveys/...                 # Surveys (future A4-A6)
   ```

4. **Добавить примеры Problem Hypothesis List** (из документации)

**Приоритет**: 🔴 HIGH (критично для A2, определяет поведение бота)

---

### 2.4. Обновить описание path structure для hypotheses

**Текущее** (неявно, в HYPOTHESIS_TEMPLATE_TOOL):
- Путь: `/customer-research/{idea-name}-hypotheses/{hypothesis-name}`
- Один файл = одна гипотеза (структура section01-04)

**Что изменить**:
- **Problem hypotheses** (A2): `/customer-research/{idea-name}/hypotheses/problem-list` (один файл со списком)
- **Solution hypotheses** (A3): `/customer-research/{idea-name}/hypotheses/{solution-name}` (один файл на solution)

**Приоритет**: 🟢 LOW (косметическое, но нужно обновить для ясности)

---

## 3. Приоритизация работ

### Must Have (Фаза 1, критично для базового A2)

1. 🔴 **Добавить Problem Hypothesis List структуру**
   - Создать tool `generate_problem_hypotheses` для генерации списка из Idea Framing Sheet
   - Skeleton по спецификации (hypotheses[], priority_scores, challenge_log)
   - Путь: `/customer-research/{idea-name}/hypotheses/problem-list`

2. 🔴 **Обновить промпт с методологией формулировки гипотез**
   - Problem Hypothesis Formulation Rules (~100 lines)
   - Канонический формат "Our customer [segment] wants [goal], but cannot [action], because [reason]"
   - Правила: Single Assumption, Goal is Outcome, Testability, Specificity
   - Примеры хороших/плохих гипотез

3. 🔴 **Добавить Prioritization Tool**
   - Tool `prioritize_hypotheses` для оценки Impact/Evidence/Feasibility
   - Weighted formula: 0.4×Impact + 0.4×Evidence + 0.2×Feasibility
   - Обновление problem-list с priority_scores

4. 🔴 **Обновить промпт с процессом A2**
   - A21-A24 workflow (~80 lines)
   - Интеграция с существующим A1 workflow
   - Примеры Problem Hypothesis List

### Should Have (Фаза 2, улучшение качества)

5. 🟡 **Добавить Challenge Loop механизм**
   - Tool `challenge_hypothesis` для создания контрпримеров
   - Prompt инструкции для LLM как оппонировать
   - Логирование в challenge_log

6. 🟡 **Добавить Web Research Tool**
   - Интеграция для поиска evidence в публичных источниках
   - Автоматическое заполнение research_evidence[]
   - Улучшение Evidence score

7. 🟡 **Добавить валидацию Problem Hypothesis List**
   - `PROBLEM_HYPOTHESIS_LIST_VALIDATION_CRITERIA`
   - Обновление VALIDATE_ARTIFACT_TOOL для поддержки "problem-hypothesis-list"
   - Валидация формата, single assumption, testability

### Nice to Have (Фаза 3, автоматизация)

8. 🟢 **Автоматическая генерация гипотез из Sheet**
   - Парсинг core_problem, key_assumptions
   - Генерация 5-7 гипотез без участия пользователя
   - Пока можно через диалог с пользователем

9. 🟢 **Кастомные веса для приоритизации**
   - Позволить фаундеру переопределить веса (0.4/0.4/0.2)
   - Если нужна обратная совместимость

---

## 4. Тестовый сценарий для A2

После реализации Must Have (пункты 1-4), протестировать:

### Тест 1: Генерация Problem Hypothesis List из Sheet

**Input**: Пользователь говорит "Generate problem hypotheses from Idea Framing Sheet (slack-microwave/sheet)"

**Expected Output**:
1. Бот читает Sheet `/customer-research/slack-microwave/sheet`
2. Извлекает core_problem, key_assumptions
3. Генерирует 3-5 гипотез в каноническом формате
4. Создает Problem Hypothesis List: `/customer-research/slack-microwave/hypotheses/problem-list`
5. Структура содержит hypotheses[], каждая с hypothesis_id, formulation, segment, goal, barrier, reason

**Проверка**: Читаем файл через `flexus_policy_document()`, проверяем JSON структуру и формат гипотез

---

### Тест 2: Challenge Loop (если реализовано)

**Input**: Пользователь говорит "Challenge hypothesis H1"

**Expected Output**:
1. Бот читает H1 из problem-list
2. Создает контрпример (бизнес, который буквально выполняет гипотезу, но приводит к противоположному)
3. Показывает контрпример пользователю
4. Пользователь уточняет гипотезу
5. Бот обновляет H1 и добавляет запись в challenge_log

**Проверка**: Читаем problem-list, проверяем наличие challenge_log с iteration, counterexample, refinement

---

### Тест 3: Приоритизация гипотез

**Input**: Пользователь говорит "Prioritize problem hypotheses"

**Expected Output**:
1. Бот читает problem-list
2. Для каждой гипотезы оценивает Impact (0-5), Evidence (0-5), Feasibility (0-5)
3. Вычисляет weighted_score = 0.4×Impact + 0.4×Evidence + 0.2×Feasibility
4. Ранжирует гипотезы по убыванию score
5. Обновляет problem-list с priority_scores
6. Показывает таблицу с топ-3 гипотезами и рекомендацией

**Проверка**: Читаем problem-list, проверяем наличие priority_scores для каждой гипотезы, сортировка по weighted_score

---

### Тест 4: Валидация Problem Hypothesis List

**Input**: Пользователь говорит "Validate problem hypotheses"

**Expected Output**:
1. Бот вызывает `validate_artifact(artifact_path="/customer-research/slack-microwave/hypotheses/problem-list", artifact_type="problem-hypothesis-list")`
2. Возвращает статус: `pass` или `fail`
3. Если `fail` — список issues (например: "H2 contains two assumptions", "H3 format incorrect")

**Проверка**: Статус корректен, issues описательны

---

### Тест 5: Выбор гипотезы для A3

**Input**: Пользователь говорит "Select H1 for solution design"

**Expected Output**:
1. Бот обновляет problem-list: selected_hypothesis_id = "H1"
2. H1.validation_status = "selected"
3. Бот говорит: "H1 selected! Ready to move to A3 (solution hypothesis generation). Would you like to start?"

**Проверка**: Читаем problem-list, проверяем selected_hypothesis_id = "H1"

---

## 5. Оценка сложности

| Задача | Сложность | Время (оценка) |
|--------|-----------|----------------|
| 1. Problem Hypothesis List структура | Средняя (JSON + tool) | 1-2 часа |
| 2. Методология формулировки в промпте | Низкая (копипаста + адаптация) | 1 час |
| 3. Prioritization Tool | Средняя (LLM scoring + formula) | 2-3 часа |
| 4. A2 workflow в промпте | Низкая (описание процесса) | 1 час |
| 5. Challenge Loop | Средняя (контрпример + логика) | 2-3 часа |
| 6. Web Research Tool | Средняя-высокая (интеграция поиска) | 2-4 часа |
| 7. Валидация Problem Hypothesis List | Средняя (критерии + проверка) | 2 часа |

**Total Must Have (1-4)**: ~5-7 часов работы

---

## 6. Рекомендации

### Начать с:
1. Problem Hypothesis List структура (самое простое)
2. Промпт обновление — методология (критично для качества)
3. Prioritization Tool (критично для ранжирования)
4. A2 workflow в промпте (связывает всё вместе)

### Отложить на потом:
- Challenge Loop (можно работать без оппонирования)
- Web Research (можно ставить Evidence = 3 вручную)
- Валидация (не критично для MVP)

### Риски:
- **Промпт слишком длинный**: A1 методология + A2 методология = ~400 строк. Проверить, не превышает ли context limit.
- **LLM-based scoring субъективно**: Оценки Impact/Evidence/Feasibility зависят от LLM, могут быть непредсказуемы. Решение: добавить примеры scoring в промпт для калибровки.
- **Challenge Loop может зациклиться**: Если LLM плохо генерирует контрпримеры. Решение: ограничить 3 итерациями.

---

## Следующие шаги

1. Согласовать приоритеты (Must Have vs Should Have)
2. Начать с Problem Hypothesis List (самое простое)
3. Протестировать генерацию гипотез из Sheet
4. Добавить Prioritization Tool
5. Обновить промпт с A2 workflow
6. Протестировать весь flow A2 (Generation → Prioritization → Selection)

---

## Связь A1 → A2

**Input A2**: Утверждённый Idea Framing Sheet (output A1)

**Output A2**: Приоритизированный Problem Hypothesis List с выбранной гипотезой для A3

**Workflow**:
1. A1 завершается с validated Sheet
2. User/Bot инициирует A2: "Generate problem hypotheses"
3. A21: Извлечение гипотез из Sheet
4. A22: Challenge Loop (optional)
5. A23: Приоритизация по ICE matrix
6. A24: Валидация и выбор топ-гипотезы
7. Переход к A3 (solution hypothesis generation)

---

**Готово к работе? Начинаем с пункта 1 (Problem Hypothesis List)?**


