# Productman A1 Analysis: Current State vs Target

## Executive Summary

**A1 Activity**: "Разложить идею и получить проверенный Sheet"

**Current Coverage**: ~30% (только создание шаблонов идей, без First Principles Canvas и валидации)

**Required Work**: 
- 2 новых артефакта (First Principles Canvas, Idea Framing Sheet)
- 3 новых tool (validate_artifact + обновления существующих)
- Обновление промпта с методологией First Principles
- Добавление валидационной логики с циклом доработки

---

## 1. Что НУЖНО ДОБАВИТЬ (новое)

### 1.1. First Principles Canvas (артефакт)

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Промежуточный артефакт для декомпозиции сырой идеи на первые принципы, предшествует Idea Framing Sheet.

**Структура** (из документации):
```json
{
  "fundamental_truth": "Core observation (factual, not assumption)",
  "atomic_value": "Minimum measurable benefit",
  "constraints": [
    {
      "constraint_type": "time | money | skills | access | regulatory",
      "description": "..."
    }
  ],
  "current_workarounds": "How solved today + why inadequate",
  "minimum_end_to_end_scenario": ["Step 1", "Step 2", ...],
  "critical_assumptions": ["Testable assumption 1", ...],
  "success_metrics": {
    "metric_name": "...",
    "order_of_magnitude": "10x / 2-4x / ..."
  },
  "one_sentence_statement": "We help [who] achieve [result] within [constraints] by [approach]"
}
```

**Что делать**:
- Добавить tool `create_first_principles_canvas` (или обновить `template_idea` для создания Canvas)
- Сохранять в `/customer-research/{idea-name}-canvas`

**Приоритет**: 🔴 HIGH (критично для A1, блокирует A11)

---

### 1.2. Idea Framing Sheet (артефакт)

**Статус**: ⚠️ ЧАСТИЧНО ЕСТЬ (текущая структура `idea` слишком упрощена)

**Что это**: Финальный валидированный резюме идеи, синтезированный из First Principles Canvas.

**Отличие от текущей структуры**:

| Компонент | Сейчас в productman | Нужно по A1 |
|-----------|---------------------|-------------|
| Title | ❌ Нет | ✅ Concise title |
| One-sentence pitch | ❌ Нет | ✅ Template: "We help [who]..." |
| Target segment | ❌ В question03 вкратце | ✅ Детальная структура: who, characteristics, size_estimate |
| Core problem | ⚠️ В question02 базово | ✅ description, current_impact, frequency |
| Value proposition | ❌ В question04 неявно | ✅ atomic_value (REQUIRED), differentiation |
| Key assumptions | ❌ Нет | ✅ Массив: {assumption, criticality, testability} |
| Constraints | ⚠️ В section02/question01 | ✅ Массив строк с конкретикой |
| Why now | ❌ Нет | ⚠️ Optional но recommended |
| Version | ❌ Нет | ✅ v0, v1, v2... |
| Validation status | ❌ Нет | ✅ pending, pass, pass-with-warnings, fail, approved, proceed-as-is |

**Что делать**:
- Переделать структуру `idea` → `IdeaFramingSheet` по спецификации
- Обновить `template_idea` или создать отдельный tool `synthesize_idea_framing_sheet`
- Сохранять в `/customer-research/{idea-name}-sheet`

**Приоритет**: 🔴 HIGH (критично для A1)

---

### 1.3. Tool: `validate_artifact`

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Валидация артефактов по критериям (A12 в процессе A1).

**Функционал**:
- Принимает артефакт (First Principles Canvas или Idea Framing Sheet)
- Проверяет по критериям (см. `idea-validation-criteria.md`)
- Возвращает:
  ```json
  {
    "status": "pass | pass-with-warnings | fail",
    "issues": [
      {
        "severity": "critical | warning | info",
        "criterion": "C1",
        "description": "Target segment too broad",
        "location": "target_segment.who"
      }
    ],
    "suggestions": [
      {
        "issue_ref": 0,
        "fix": "Narrow to: 'B2B SaaS, 10-50 employees...'"
      }
    ]
  }
  ```

**Реализация**:
- Добавить в `TOOLS` в `productman_bot.py`
- Handler `@rcx.on_tool_call("validate_artifact")`
- Логика валидации: hardcoded rules из `idea-validation-criteria.md` или LLM-based через промпт

**Приоритет**: 🔴 HIGH (критично для A12)

---

### 1.4. Методология First Principles в промпте

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Инструкции для LLM как применять First Principles мышление.

**Что добавить в `productman_prompts.py`**:
- Раздел "First Principles Canvas — Rules & Usage Guide" (из `first-principles-canvas-rules.md`)
- Правила:
  - Rule 1.1: Challenge Assumptions ("users want X" → "what I know, what I assume, what I test")
  - Rule 1.2: Decompose to First Principles
  - Rule 1.3: Rebuild from Fundamentals
- Примеры хороших/плохих формулировок
- Валидационный чеклист для Canvas полей

**Объем**: ~150 строк текста в промпт

**Приоритет**: 🔴 HIGH (критично для A11, определяет поведение бота)

---

### 1.5. Validation Status & Sanction Policy (логика)

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Логика обработки результатов валидации и запроса санкции пользователя.

**Что реализовать**:

1. **Статусы**:
   - `pass` → автозавершение, переход к A2
   - `pass-with-warnings` → запросить санкцию у пользователя
   - `fail` → обязательная доработка, цикл A11 → A12 → A13 → A11

2. **Sanction workflow** (для `pass-with-warnings`):
   ```
   Bot: "Idea Framing Sheet has 2 warnings:
     - W1: Market size estimate is vague
     - W2: 'Why now' field is missing
     
   Do you want to:
     [A] Address warnings now
     [B] Proceed as-is (warnings acknowledged)"
   
   User: [selects B]
   
   Bot: Status updated to 'proceed-as-is'. Moving to A2.
   ```

3. **Revision loop** (для `fail`):
   - Вернуться к Canvas/Sheet редактированию
   - Показать issues и suggestions
   - Повторить валидацию после исправлений

**Приоритет**: 🟡 MEDIUM (можно отложить, начать без санкций — просто показывать warnings как информацию)

---

### 1.6. Versioning для артефактов

**Статус**: ❌ ОТСУТСТВУЕТ

**Что это**: Версионирование Idea Framing Sheet при итеративной доработке (v0 → v1 → v2).

**Что реализовать**:
- Добавить поле `version` в артефакты
- При записи: проверять существующую версию, инкрементировать
- Пути: `/customer-research/{idea-name}-sheet-v0`, `-v1`, `-v2` (или хранить историю в одном файле)

**Приоритет**: 🟢 LOW (nice-to-have, можно начать без версионирования)

---

## 2. Что НУЖНО ИЗМЕНИТЬ (из существующего)

### 2.1. Структура `idea` документа

**Текущая структура** (из `productman_bot.py` lines 87-133):
```json
{
  "idea": {
    "meta": {
      "author": "",
      "date": "",
      "status": "in_progress"
    },
    "section01": {
      "section_title": "Idea Summary",
      "question01": {"q": "What is the idea in one sentence?", "a": ""},
      "question02": {"q": "What problem does this solve?", "a": ""},
      "question03": {"q": "Who is the target audience?", "a": ""},
      "question04": {"q": "What value do you provide?", "a": ""}
    },
    "section02": {
      "section_title": "Constraints & Context",
      "question01": {"q": "What constraints exist?", "a": ""},
      "question02": {"q": "What observations support this?", "a": ""},
      "question03": {"q": "What are key assumptions?", "a": ""},
      "question04": {"q": "What are known risks?", "a": ""}
    }
  }
}
```

**Проблемы**:
- ❌ Слишком упрощена (вопросы-ответы вместо структурированных полей)
- ❌ Нет атомарной ценности как обязательного измеримого поля
- ❌ Нет детализации target segment (characteristics, size_estimate)
- ❌ Нет one-sentence pitch в стандартном формате
- ❌ Нет валидационного статуса
- ❌ Нет версионирования

**Что изменить**:

**Вариант A**: Заменить на Idea Framing Sheet
```json
{
  "ideaFramingSheet": {
    "title": "...",
    "one_sentence_pitch": "We help [who] achieve [result] within [constraints] by [approach]",
    "target_segment": {
      "who": "...",
      "characteristics": ["trait 1", "trait 2"],
      "size_estimate": "..."
    },
    "core_problem": {
      "description": "...",
      "current_impact": "...",
      "frequency": "..."
    },
    "value_proposition": {
      "atomic_value": "...",
      "differentiation": "..."
    },
    "key_assumptions": [
      {"assumption": "...", "criticality": "high|medium|low", "testability": "easy|medium|hard"}
    ],
    "constraints": ["...", "..."],
    "why_now": "...",
    "version": "v0",
    "validation_status": "pending"
  }
}
```

**Вариант B**: Поэтапная миграция
- Сначала добавить First Principles Canvas как отдельный артефакт
- Потом синтезировать Idea Framing Sheet из Canvas
- Держать старую структуру `idea` для обратной совместимости (если нужно)

**Рекомендация**: Вариант B (поэтапно), но не заморачиваться с обратной совместимостью — это dev версия, можно breaking change.

**Приоритет**: 🔴 HIGH (критично для A1)

---

### 2.2. Tool `template_idea` → `create_first_principles_canvas`

**Текущий код** (`productman_bot.py` lines 73-137):
- Создает skeleton idea file
- Валидирует путь (kebab-case, `/customer-research/`)
- Записывает через `pdoc_integration.pdoc_write`

**Что изменить**:

**Шаг 1**: Переименовать tool
```python
# Было
IDEA_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_idea",
    description="Create skeleton idea file in pdoc...",
    ...
)

# Стало
FIRST_PRINCIPLES_CANVAS_TOOL = ckit_cloudtool.CloudTool(
    name="create_first_principles_canvas",
    description="Create First Principles Canvas for decomposing raw idea into fundamental truths, constraints, and testable assumptions. Path format: /customer-research/{idea-name}-canvas",
    ...
)
```

**Шаг 2**: Обновить skeleton структуру
```python
canvas_skeleton = {
    "fundamental_truth": "",
    "atomic_value": "",
    "constraints": [],
    "current_workarounds": "",
    "minimum_end_to_end_scenario": [],
    "critical_assumptions": [],
    "success_metrics": {
        "metric_name": "",
        "order_of_magnitude": ""
    },
    "one_sentence_statement": ""
}
```

**Шаг 3**: Обновить путь
```python
# Было: /customer-research/{idea-name}
# Стало: /customer-research/{idea-name}-canvas
```

**Приоритет**: 🔴 HIGH (критично для A11)

---

### 2.3. Добавить tool `synthesize_idea_framing_sheet`

**Новый tool** (создать, не менять существующий):

```python
IDEA_FRAMING_SHEET_TOOL = ckit_cloudtool.CloudTool(
    name="synthesize_idea_framing_sheet",
    description="Synthesize Idea Framing Sheet from First Principles Canvas. Reads Canvas, validates structure, creates validated Sheet. Path format: /customer-research/{idea-name}-sheet",
    parameters={
        "type": "object",
        "properties": {
            "canvas_path": {
                "type": "string",
                "description": "Path to First Principles Canvas (e.g. /customer-research/unicorn-horn-car-canvas)"
            },
            "output_path": {
                "type": "string",
                "description": "Path to write Idea Framing Sheet (e.g. /customer-research/unicorn-horn-car-sheet)"
            }
        },
        "required": ["canvas_path", "output_path"]
    }
)
```

**Логика handler**:
1. Читает Canvas через `pdoc_integration.pdoc_read(canvas_path)`
2. Парсит JSON
3. Синтезирует Idea Framing Sheet структуру
4. Записывает через `pdoc_integration.pdoc_write(output_path, sheet_json)`

**Приоритет**: 🟡 MEDIUM (можно начать без этого, пусть LLM пишет Sheet руками через pdoc)

---

### 2.4. Обновить промпт `productman_prompt`

**Текущий промпт** (`productman_prompts.py` lines 44-87):
- Объясняет структуру идей и гипотез
- Правила путей (kebab-case, `/customer-research/`)
- Инструкция "Before you do anything, load all ideas using flexus_policy_document()"

**Что добавить**:

1. **Методология First Principles** (~150 lines):
   - Вставить содержимое `first-principles-canvas-rules.md`
   - Разделы:
     - Core Logic (Challenge Assumptions, Decompose, Rebuild)
     - Canvas Field Rules (что писать в каждое поле)
     - Anti-Patterns (что НЕ делать)
     - Validation Checklist

2. **Процесс A1** (~50 lines):
   ```
   ## Your Workflow for A1 (Idea Structuring)
   
   Step 1 (A11): Create First Principles Canvas
   - Use create_first_principles_canvas()
   - Path: /customer-research/{idea-name}-canvas
   - Challenge assumptions, decompose to fundamentals
   
   Step 2 (A11): Synthesize Idea Framing Sheet
   - Read Canvas, extract key points
   - Create structured Sheet with target_segment, core_problem, value_proposition, key_assumptions
   - Path: /customer-research/{idea-name}-sheet
   
   Step 3 (A12): Validate Sheet
   - Use validate_artifact() [КОГДА БУДЕТ РЕАЛИЗОВАНО]
   - Check: target segment specific? value measurable? assumptions testable?
   - Return: pass / pass-with-warnings / fail
   
   Step 4 (A13): Handle validation
   - If PASS → Done, move to A2 (hypothesis generation)
   - If PASS-WITH-WARNINGS → Ask user: address now or proceed as-is?
   - If FAIL → Return to Step 2, fix issues
   ```

3. **Обновить примеры**:
   - Заменить `example_idea` на First Principles Canvas пример (из документации)
   - Добавить `example_idea_framing_sheet` (из документации)

**Приоритет**: 🔴 HIGH (критично для A11, определяет поведение)

---

### 2.5. Обновить описание tool `flexus_policy_document`

**Текущее** (неявно, через интеграцию `fi_pdoc`):
- Читает/пишет policy documents
- Используется для идей и гипотез

**Что изменить**:
- Документация в промпте: упомянуть, что теперь артефактов 3 типа:
  1. First Principles Canvas (`-canvas`)
  2. Idea Framing Sheet (`-sheet`)
  3. Hypothesis (как было: `-hypotheses/...`)

**Приоритет**: 🟢 LOW (косметическое, не блокирует функциональность)

---

## 3. Приоритизация работ

### Must Have (Фаза 1, критично для базового A1)

1. 🔴 **Добавить First Principles Canvas структуру**
   - Обновить `template_idea` → `create_first_principles_canvas`
   - Skeleton по спецификации (8 полей)
   - Путь: `/customer-research/{idea-name}-canvas`

2. 🔴 **Добавить Idea Framing Sheet структуру**
   - Создать новый skeleton (10 полей)
   - Путь: `/customer-research/{idea-name}-sheet`

3. 🔴 **Обновить промпт с методологией**
   - First Principles Rules (~150 lines)
   - Процесс A11-A12-A13 (~50 lines)
   - Примеры Canvas + Sheet

4. 🟡 **Добавить tool `validate_artifact` (упрощенная версия)**
   - Базовая валидация: проверка required fields
   - Статус: pass / fail (без warnings на первом этапе)
   - Без санкций (просто показываем issues)

### Should Have (Фаза 2, улучшение UX)

5. 🟡 **Полная валидация с warnings**
   - Critical / warning / info severity
   - Suggestions для исправления

6. 🟡 **Sanction workflow**
   - Запрос санкции для `pass-with-warnings`
   - Логирование решения пользователя

7. 🟢 **Versioning артефактов**
   - v0, v1, v2 при итеративной доработке
   - История изменений

### Nice to Have (Фаза 3, автоматизация)

8. 🟢 **Tool `synthesize_idea_framing_sheet`**
   - Автоматический синтез Sheet из Canvas
   - Пока можно через LLM руками

9. 🟢 **Миграция старых документов**
   - Конвертация старых `idea` → новые Canvas/Sheet
   - Если нужна обратная совместимость

---

## 4. Тестовый сценарий для A1

После реализации Must Have (пункты 1-4), протестировать:

### Тест 1: Создание First Principles Canvas

**Input**: Пользователь говорит "У меня идея — микроволновка, которая меняет статус в Slack"

**Expected Output**:
1. Бот создает Canvas: `/customer-research/slack-microwave-canvas`
2. Структура содержит 8 полей (fundamental_truth, atomic_value, constraints, ...)
3. Поля частично заполнены на основе input

**Проверка**: Читаем файл через `flexus_policy_document()`, проверяем JSON структуру

---

### Тест 2: Синтез Idea Framing Sheet

**Input**: Пользователь говорит "Теперь создай Sheet на основе Canvas"

**Expected Output**:
1. Бот читает Canvas
2. Создает Sheet: `/customer-research/slack-microwave-sheet`
3. Структура содержит 10 полей (title, one_sentence_pitch, target_segment, ...)
4. Поля синтезированы из Canvas (например, `fundamental_truth` → `core_problem.description`)

**Проверка**: Читаем Sheet, проверяем mapping из Canvas

---

### Тест 3: Валидация (базовая)

**Input**: Пользователь говорит "Провалидируй Sheet"

**Expected Output**:
1. Бот вызывает `validate_artifact()`
2. Возвращает статус: `pass` или `fail`
3. Если `fail` — список issues (например: "target_segment.who is empty")

**Проверка**: Статус корректен, issues описательны

---

### Тест 4: Итерация при FAIL

**Input**: Пользователь получил `fail`, говорит "Исправь issues"

**Expected Output**:
1. Бот обновляет Sheet, исправляет проблемы
2. Снова вызывает `validate_artifact()`
3. Теперь статус `pass`

**Проверка**: Цикл A11 → A12 → A13 → A11 работает

---

## 5. Оценка сложности

| Задача | Сложность | Время (оценка) |
|--------|-----------|----------------|
| 1. First Principles Canvas | Низкая (JSON skeleton + путь) | 30 мин |
| 2. Idea Framing Sheet | Низкая (JSON skeleton + путь) | 30 мин |
| 3. Обновить промпт | Средняя (копипаста + адаптация) | 1-2 часа |
| 4. Validate artifact (базовый) | Средняя (логика валидации) | 2-3 часа |
| 5. Полная валидация | Средняя | 2 часа |
| 6. Sanction workflow | Средняя (UI logic) | 2 часа |
| 7. Versioning | Низкая | 1 час |
| 8. Synthesize tool | Низкая | 1 час |

**Total Must Have (1-4)**: ~4-5 часов работы

---

## 6. Рекомендации

### Начать с:
1. First Principles Canvas (самое простое)
2. Промпт обновление (самое критичное для поведения)
3. Idea Framing Sheet
4. Базовая валидация (без warnings/sanctions)

### Отложить на потом:
- Sanction workflow (можно работать без него)
- Versioning (не критично для MVP)
- Synthesize tool (LLM справится через pdoc вручную)

### Риски:
- **Промпт слишком длинный**: Методология First Principles + примеры = ~300 строк. Проверить, не превышает ли context limit для выбранной модели.
- **Валидация LLM-based vs hardcoded**: Если делать валидацию через LLM (передавать rules в промпт), это гибче, но медленнее и дороже. Hardcoded rules быстрее, но менее гибко.

---

## Следующие шаги

1. Согласовать приоритеты (Must Have vs Should Have)
2. Начать с First Principles Canvas (самое простое)
3. Протестировать создание Canvas
4. Продолжить с Idea Framing Sheet
5. Обновить промпт
6. Добавить базовую валидацию
7. Протестировать весь flow A1 (Canvas → Sheet → Validation → Iteration)

---

**Готово к работе? Начинаем с пункта 1 (First Principles Canvas)?**


