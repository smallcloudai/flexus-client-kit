# Product Lion Test Cases

Тест-кейсы для проверки функциональности Product Lion v0.4 (A1-A2 workflow).

---

## A0: Начало работы

### TC-001: Первый запуск
**Сообщение пользователя:** "Hi" или "Начнем"

**Что проверяем:** Бот проверяет существующие идеи и предлагает начать

**Допустимое поведение:**
- Бот МОЛЧА вызывает `flexus_policy_document(op="list", args={"p": "/customer-research/"})`
- Отвечает: "I checked your workspace. You have no existing ideas. Let's start! What's your product idea in a few words?"
- Короткий ответ (2-4 предложения)
- НЕ упоминает технические детали (tools, paths, JSON)

**Недопустимое поведение:**
- ❌ Пишет "I called flexus_policy_document" или "[calls tool]"
- ❌ Длинный ответ с инструкциями
- ❌ Показывает JSON структуру
- ❌ Упоминает имена тулов в ответе

---

### TC-002: Возврат к существующей идее
**Сообщение пользователя:** "Hi" (когда уже есть идея "gtm-automation")

**Что проверяем:** Бот распознает существующие идеи и предлагает выбор

**Допустимое поведение:**
- Бот МОЛЧА вызывает `flexus_policy_document(op="list")`
- Отвечает: "I see you have 1 idea: 'gtm-automation'. Would you like to continue with it or start a new idea?"
- Предлагает явный выбор

**Недопустимое поведение:**
- ❌ Не проверяет существующие идеи
- ❌ Сразу начинает новую идею
- ❌ Выводит список файлов/путей

---

## A1: First Principles Canvas

### TC-003: Создание Canvas - инициация
**Сообщение пользователя:** "I want to help B2B founders launch sales campaigns faster"

**Что проверяем:** Бот начинает заполнение Canvas через вопросы

**Допустимое поведение:**
- Бот НЕ создает Canvas сразу
- Задает первый вопрос: "What evidence shows that founders struggle with campaign launch speed? How many founders? What exactly takes too long?"
- КОРОТКИЙ вопрос (1-2 предложения)
- НЕ предлагает ответ за пользователя

**Недопустимое поведение:**
- ❌ Сразу создает Canvas без уточнений
- ❌ Пишет JSON в чат
- ❌ Предлагает заполнить поля ("Maybe your fundamental truth is...")
- ❌ Длинный ответ (>5 предложений)

---

### TC-004: Создание Canvas - уточнение конкретики
**Сообщение пользователя:** "Founders struggle with GTM, they want it faster"

**Что проверяем:** Бот требует конкретики вместо лозунгов

**Допустимое поведение:**
- "What does 'faster' mean in numbers? Days? Hours?"
- "How do you know founders struggle? Did you interview them?"
- Вопрос челленджит расплывчатость

**Недопустимое поведение:**
- ❌ Принимает "faster" без уточнения
- ❌ Сам придумывает цифры ("Maybe 10x faster?")

---

### TC-005: Создание Canvas - подтверждение и создание
**Контекст:** Пользователь дал конкретные ответы на все вопросы

**Сообщение пользователя:** "Yes, that's correct"

**Что проверяем:** Бот МОЛЧА создает Canvas, подтверждает создание

**Допустимое поведение:**
- Бот МОЛЧА вызывает `create_first_principles_canvas(idea_name="gtm-automation")`
- Отвечает: "Canvas created at /customer-research/gtm-automation/canvas. Now let's synthesize Idea Framing Sheet from this Canvas."
- НЕ пишет "I called tool" или "calling create_first_principles_canvas"
- НЕ показывает JSON

**Недопустимое поведение:**
- ❌ Пишет "I'm calling create_first_principles_canvas..."
- ❌ Выводит JSON Canvas в чат
- ❌ Пишет "[calls tool]" или "calling tool"

---

## A1: Idea Framing Sheet

### TC-006: Создание Sheet - автоматический маппинг
**Контекст:** Canvas создан

**Сообщение пользователя:** "Create the Sheet"

**Что проверяем:** Бот создает Sheet на основе Canvas

**Допустимое поведение:**
- Бот МОЛЧА читает Canvas через `flexus_policy_document`
- Бот МОЛЧА создает Sheet через `create_idea_framing_sheet`
- Отвечает: "Sheet created at /customer-research/gtm-automation/sheet (v0). Ready to validate."
- Краткий ответ

**Недопустимое поведение:**
- ❌ Просит пользователя вручную заполнить Sheet
- ❌ Показывает JSON Sheet
- ❌ Пишет "[I'm mapping Canvas to Sheet]"

---

### TC-007: Валидация Sheet - pass
**Контекст:** Sheet создан

**Сообщение пользователя:** "Validate the sheet"

**Что проверяем:** Валидация проходит успешно

**Допустимое поведение:**
- Бот МОЛЧА вызывает `validate_artifact(artifact_path="/customer-research/gtm-automation/sheet", artifact_type="sheet")`
- Отвечает:
  ```
  Validation Status: PASS
  
  Sheet validated! Ready to move to A2 (hypothesis generation). Would you like to start generating problem hypotheses?
  ```
- Краткий, понятный ответ

**Недопустимое поведение:**
- ❌ Не валидирует, сразу переходит к A2
- ❌ Показывает технические детали валидации

---

### TC-008: Валидация Sheet - fail
**Контекст:** Sheet создан с критическими ошибками (например, отсутствует atomic_value)

**Сообщение пользователя:** "Validate the sheet"

**Что проверяем:** Валидация fail → возврат на доработку

**Допустимое поведение:**
- Отвечает:
  ```
  Validation Status: FAIL
  
  Issues:
    [CRITICAL] C2: Atomic value must be measurable with specific change (at section04.question01)
  
  Suggestions:
    - Add measurable benefit like "reduce time from 14 days to 2 days"
  
  Let's fix these issues. What's the measurable benefit your solution provides?
  ```
- Перечисляет конкретные проблемы
- Задает вопрос для исправления

**Недопустимое поведение:**
- ❌ Игнорирует fail и продолжает
- ❌ Показывает весь JSON с ошибками
- ❌ Не помогает исправить

---

### TC-009: Валидация Sheet - pass-with-warnings (sanction workflow)
**Контекст:** Sheet создан с предупреждениями (например, отсутствует market size estimate)

**Сообщение пользователя:** "Validate the sheet"

**Что проверяем:** Pass-with-warnings → запрос санкции пользователя

**Допустимое поведение:**
- Отвечает:
  ```
  Validation Status: PASS-WITH-WARNINGS
  
  Issues:
    [WARNING] W1: Market size estimate missing (at section02.question03)
    [WARNING] W2: Why now field is empty (at section01.question03)
  
  Suggestions:
    - Add order-of-magnitude market size estimate
    - Explain why this problem is solvable/urgent now
  
  These are not blocking, but recommended to address.
  
  Options:
  A) Fix warnings now
  B) Proceed as-is (acknowledge and continue to A2)
  
  Which would you prefer?
  ```
- Ясно объясняет проблемы
- Дает выбор

**Недопустимое поведение:**
- ❌ Автоматически продолжает без запроса санкции
- ❌ Трактует warnings как fail

---

### TC-010: Sanction - пользователь выбирает "proceed as-is"
**Контекст:** Pass-with-warnings

**Сообщение пользователя:** "B, proceed as-is"

**Что проверяем:** Бот принимает санкцию и продолжает

**Допустимое поведение:**
- Отвечает: "Acknowledged. Ready to move to A2 (hypothesis generation). Would you like to start?"
- НЕ пытается обновить meta.validation_status (это было в неиспользуемой функции)

**Недопустимое поведение:**
- ❌ Игнорирует выбор пользователя
- ❌ Настаивает на исправлениях

---

## A2: Problem Hypothesis Generation

### TC-011: Генерация гипотез - инициация
**Контекст:** Sheet валидирован

**Сообщение пользователя:** "Generate problem hypotheses"

**Что проверяем:** Бот генерирует гипотезы на основе Sheet

**Допустимое поведение:**
- Бот МОЛЧА вызывает `generate_problem_hypotheses(idea_name="gtm-automation")`
- Отвечает:
  ```
  Problem Hypothesis List created at /customer-research/gtm-automation/hypotheses/problem-list
  
  Generated 4 hypotheses:
  H1: Pre-seed B2B SaaS founders want to launch first campaign in <2 weeks, but cannot build qualified lead lists fast, because they lack B2B databases
  H2: Technical founders want 5%+ email response rates, but cannot craft effective messages, because they lack copywriting expertise
  H3: ...
  H4: ...
  
  Next steps:
  1. Review hypotheses for clarity
  2. Prioritize hypotheses using prioritize_hypotheses tool
  ```
- Показывает сгенерированные гипотезы (не JSON!)
- Предлагает следующий шаг

**Недопустимое поведение:**
- ❌ Показывает JSON структуру problem-list
- ❌ Не показывает текст гипотез
- ❌ Генерирует гипотезы с несколькими reasons ("because X and Y")

---

### TC-012: Проверка формата гипотез
**Контекст:** Гипотезы сгенерированы

**Что проверяем:** Формат "Our customer [segment] wants [goal], but cannot [action], because [reason]"

**Допустимое поведение:**
- Каждая гипотеза строго следует формату
- ОДИН reason (не "because X and Y")
- Goal = outcome, не method (не "wants to use AI")
- Reason testable (не "because they're lazy")

**Недопустимое поведение:**
- ❌ "Founders want AI for GTM" (goal = method)
- ❌ "...because they lack time and budget" (два reason)
- ❌ "...because they're overwhelmed" (не testable)

---

### TC-013: Приоритизация гипотез
**Контекст:** Гипотезы сгенерированы

**Сообщение пользователя:** "Prioritize these hypotheses"

**Что проверяем:** Бот применяет ICE matrix

**Допустимое поведение:**
- Бот МОЛЧА вызывает `prioritize_hypotheses(problem_list_path="/customer-research/gtm-automation/hypotheses/problem-list")`
- Отвечает:
  ```
  Prioritization complete!
  
  Top 3 Problem Hypotheses:
  
  1. Hypothesis H1 (Score: I:5 E:4 F:5 = 4.6)
     Pre-seed B2B SaaS founders want to launch first campaign in <2 weeks, but cannot build qualified lead lists fast, because they lack B2B databases
  
  2. Hypothesis H3 (Score: I:4 E:5 F:3 = 4.2)
     ...
  
  3. Hypothesis H2 (Score: I:4 E:3 F:4 = 3.6)
     ...
  
  Next steps:
  1. Review top hypotheses
  2. Optional: Validate hypothesis list
  3. Select one hypothesis for solution design (A3)
  ```
- Показывает топ-3 с оценками
- Ясный формат

**Недопустимое поведение:**
- ❌ Не показывает scores
- ❌ Показывает JSON
- ❌ Не ранжирует по priority

---

### TC-014: Валидация Problem Hypothesis List
**Контекст:** Гипотезы приоритизированы

**Сообщение пользователя:** "Validate the hypothesis list"

**Что проверяем:** Валидация проверяет формат и дубликаты

**Допустимое поведение:**
- Бот МОЛЧА вызывает `validate_artifact(artifact_path="...", artifact_type="problem-hypothesis-list")`
- При pass:
  ```
  Validation Status: PASS
  
  Top 3 hypotheses ranked. Which would you like to test first? (Recommendation: H1 with score 4.6)
  ```
- При fail:
  ```
  Validation Status: FAIL
  
  Issues:
    [CRITICAL] C2: Hypothesis H3 contains multiple reasons (at section03.question01)
  
  Let's fix this issue.
  ```

**Недопустимое поведение:**
- ❌ Пропускает валидацию
- ❌ Не указывает конкретную проблему

---

## Edge Cases

### TC-015: Идея с non-kebab-case именем
**Сообщение пользователя:** "Create canvas for 'My Product Idea'"

**Что проверяем:** Бот отклоняет invalid имена

**Допустимое поведение:**
- Отвечает: "Error: idea_name 'My Product Idea' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'my-product-idea'"
- Предлагает исправленный вариант

**Недопустимое поведение:**
- ❌ Создает с пробелами/заглавными
- ❌ Молча конвертирует без уведомления

---

### TC-016: Попытка создать Canvas дважды
**Контекст:** Canvas уже создан для "gtm-automation"

**Сообщение пользователя:** "Create canvas for gtm-automation"

**Что проверяем:** Бот обрабатывает существующий Canvas

**Допустимое поведение:**
- Бот читает существующий Canvas
- Отвечает: "Canvas already exists at /customer-research/gtm-automation/canvas. Would you like to update it or continue to Sheet?"
- Не создает дубликат

**Недопустимое поведение:**
- ❌ Создает новый Canvas без предупреждения
- ❌ Перезаписывает существующий

---

### TC-017: Версионирование Sheet при обновлении
**Контекст:** Sheet v0 существует

**Сообщение пользователя:** "Update the sheet with new atomic value"

**Что проверяем:** Версионирование работает (v0 → v1)

**Допустимое поведение:**
- Бот создает Sheet v1 по пути `/customer-research/gtm-automation/sheet-v1`
- Отвечает: "Sheet created at /customer-research/gtm-automation/sheet-v1 (v1)"
- Старый v0 сохраняется

**Недопустимое поведение:**
- ❌ Перезаписывает v0
- ❌ Не инкрементирует версию

---

### TC-018: Пустой или неполный ответ пользователя
**Контекст:** Бот задал вопрос "What's the fundamental truth?"

**Сообщение пользователя:** "I don't know" или ""

**Что проверяем:** Бот помогает сформулировать ответ

**Допустимое поведение:**
- Отвечает: "Let me rephrase: What problem have you observed? Did someone complain? Did you measure something?"
- Дает контекст
- НЕ предлагает готовый ответ за пользователя (если не попросили явно)

**Недопустимое поведение:**
- ❌ Пишет "Maybe your fundamental truth is X" без запроса
- ❌ Создает Canvas с пустыми полями

---

## Коммуникационный стиль

### TC-019: Проверка краткости ответов
**Любой вопрос пользователя**

**Что проверяем:** Ответы короткие (2-4 предложения)

**Допустимое поведение:**
- 2-4 предложения максимум
- Один вопрос за раз
- Динамичный диалог

**Недопустимое поведение:**
- ❌ Ответы >5 предложений
- ❌ Несколько вопросов одновременно
- ❌ Длинные объяснения методологии

---

### TC-020: Проверка отсутствия технических деталей
**Любой вопрос пользователя**

**Что проверяем:** Бот не упоминает технические детали

**Допустимое поведение:**
- НЕ упоминает имена тулов ("create_first_principles_canvas")
- НЕ упоминает пути ("/customer-research/...")
- НЕ упоминает JSON, sections, keys
- НЕ показывает prompt structure или validation criteria

**Недопустимое поведение:**
- ❌ "I'm calling create_first_principles_canvas tool"
- ❌ Показывает validation criteria в ответе
- ❌ "Let me fill section01.question01"

---

### TC-021: Молчаливое выполнение тулов
**Любой сценарий с tool call**

**Что проверяем:** Бот НЕ анонсирует tool calls

**Допустимое поведение:**
- Бот МОЛЧА вызывает тулы
- Отвечает только результатом: "Canvas created at /customer-research/..."
- НЕ пишет "I called X" или "[calls Y]"

**Недопустимое поведение:**
- ❌ "I'm calling flexus_policy_document to check..."
- ❌ "[calls create_first_principles_canvas]"
- ❌ "Let me use the tool to create..."
- ❌ "I called the tool and got..."

---

## Интеграция с файловой системой

### TC-022: Чтение существующих артефактов
**Сообщение пользователя:** "Show me my Canvas for gtm-automation"

**Что проверяем:** Бот читает и показывает контент

**Допустимое поведение:**
- Бот МОЛЧА вызывает `flexus_policy_document(op="read", args={"p": "/customer-research/gtm-automation/canvas"})`
- Показывает content человекочитаемо (не JSON dump)
- Отвечает: "Your Canvas has 3 sections covering fundamental truth, constraints, and validation path. Core problem: 'Launching campaigns takes 2-4 weeks...'"

**Недопустимое поведение:**
- ❌ Выводит весь JSON в чат
- ❌ Не форматирует для читаемости

---

### TC-023: Список всех идей
**Сообщение пользователя:** "List all my ideas"

**Что проверяем:** Бот показывает список идей

**Допустимое поведение:**
- Бот МОЛЧА вызывает `flexus_policy_document(op="list", args={"p": "/customer-research/"})`
- Отвечает:
  ```
  You have 2 ideas:
  1. gtm-automation (Sheet: validated, Hypotheses: 4 prioritized)
  2. slack-microwave (Canvas: created, Sheet: pending)
  
  Which would you like to work on?
  ```
- Показывает статус каждой идеи

**Недопустимое поведение:**
- ❌ Показывает сырой список путей
- ❌ Не показывает статус прогресса

---

## Негативные сценарии

### TC-024: Несуществующий артефакт
**Сообщение пользователя:** "Validate the sheet for non-existent-idea"

**Что проверяем:** Обработка ошибок чтения

**Допустимое поведение:**
- Отвечает: "Error reading artifact: File not found at /customer-research/non-existent-idea/sheet. Did you create the Sheet first?"
- Предлагает правильный flow

**Недопустимое поведение:**
- ❌ Показывает stack trace
- ❌ Креш бота

---

### TC-025: Invalid JSON от LLM при генерации гипотез
**Контекст:** LLM вернул невалидный JSON при generate_problem_hypotheses

**Что проверяем:** Graceful error handling

**Допустимое поведение:**
- Отвечает: "Error: Failed to parse hypotheses (got non-JSON response). Try again."
- Логирует ошибку (logger.error)
- Не крешится

**Недопустимое поведение:**
- ❌ Показывает сырой output от LLM
- ❌ Креш с exception

---

## A3/A4 (Not Implemented)

### TC-026: Попытка использовать A3/A4
**Сообщение пользователя:** "Generate solution hypotheses" или "Create survey"

**Что проверяем:** Бот сообщает о недоступности

**Допустимое поведение:**
- Отвечает: "Solution hypothesis generation (A3) is coming soon. Currently available: A1 (Idea Structuring) and A2 (Problem Hypothesis Prioritization)."
- Предлагает текущие возможности

**Недопустимое поведение:**
- ❌ Пытается выполнить несуществующую функциональность
- ❌ Игнорирует запрос

---

## Summary: Critical Quality Gates

**Для прохождения manual QA все эти пункты ОБЯЗАТЕЛЬНЫ:**

1. ✅ Бот НЕ пишет "I called tool" или "[calls X]" НИКОГДА
2. ✅ Бот НЕ показывает JSON в ответах (только человекочитаемый текст)
3. ✅ Ответы короткие (2-4 предложения)
4. ✅ Бот задает вопросы, НЕ предлагает ответы за пользователя
5. ✅ Tool calls выполняются молча
6. ✅ Проверка существующих идей при старте (flexus_policy_document)
7. ✅ Валидация с правильными статусами (pass/fail/pass-with-warnings)
8. ✅ ICE scoring работает (Impact, Evidence, Feasibility)
9. ✅ Гипотезы следуют формату (segment → goal → barrier → reason)
10. ✅ Kebab-case validation работает
11. ✅ Версионирование Sheet работает (v0 → v1)
12. ✅ Graceful error handling (не крешится на invalid input)

---

## Как использовать эти тест-кейсы

**Manual QA:**
1. Запусти бота локально
2. Пройди по TC-001 → TC-014 последовательно (happy path A1→A2)
3. Проверь edge cases TC-015 → TC-018
4. Проверь стиль коммуникации TC-019 → TC-021
5. Отметь ✅/❌ для каждого кейса

**Automated tests (future):**
- Unit: моки для tool calls, проверка формата гипотез
- Integration: реальные tool calls с test fixtures
- E2E: Playwright с реальным ботом

**Regression testing:**
- При любых изменениях в промптах → прогони TC-019 → TC-021 (коммуникация)
- При изменении тулов → прогони TC-005, TC-006, TC-011, TC-013 (tool execution)
- При изменении валидации → прогони TC-007 → TC-009, TC-014

