Этап 3. Структура выходного пакета Совы-Стратега (Оглавление v1.0)
Это скелет верхнего уровня:
1. Strategy Summary
2. Hypothesis Analysis
3. Target Segment (ICP/JTBD/CJM)
4. Value Proposition & Messaging
5. Channel Strategy
6. Experiment Design
7. Tactical Execution Plan (Machine-Readable)
8. Creative Requirements
9. Landing Page Requirements
10. Tracking & Attribution Requirements
11. Risk Assessment
12. Compliance Assessment
13. Decision Log (JSON)
14. Full JSON Specification for Execution Agents


Теперь разбираем каждый раздел глубоко.

1. Strategy Summary (резюме стратегии)

1.1. Описание идеи
1.2. Проверяемая гипотеза (в нормализованном виде)
1.3. Цель эксперимента (business → metric → time)
1.4. Что является успешным исходом
1.5. Прогноз ожидаемых метрик (диапазоны CTR/CPC/CVR/CPL)
1.6. Общий стратегический подход (каналы, формат теста, основные решения)

(Это как executive summary для фаундера+для последующих агентов.)

2. Hypothesis Analysis (аналитика гипотезы)

2.1. Тип гипотезы
2.2. Диагностированное ядро гипотезы (what is really being tested)
2.3. Ключевые неизвестные (unknowns)
2.4. Степень неопределённости
2.5. Тестируемые допущения
2.6. Ограничения теста
2.7. Сигналы, которые можно / нельзя получить из теста

3. Target Segment (ICP/JTBD/CJM)

3.1. ICP (машиночитаемо)

демография

психография

профессия

поведение

платёжеспособность

контекст покупки

3.2. JTBD

functional jobs

emotional jobs

social jobs

ситуации, триггеры, барьеры

3.3. Pain/Gain analysis
3.4. Customer Journey (Awareness → Consideration → Purchase → Activation)
3.5. Риски сегмента
3.6. Ожидаемый канал обнаружения (Discovery Channels)

4. Value Proposition & Messaging

4.1. Матрица проблема → решение
4.2. Основные Value props
4.3. Дополнительные Value props
4.4. Key Messages
4.5. Angles (variations)
4.6. Барьеры + как их снимаем
4.7. Примеры коротких сообщений (для креативов)

5. Channel Strategy (канальная стратегия)

5.1. Каналы для теста
5.2. Обоснования выбора
5.3. Роль каждого канала
5.4. Каналы для будущих итераций (если нужны)
5.5. Исключённые каналы (и почему)
5.6. Диапазоны бенчмарков по каждому каналу (из RAG)
5.7. Прогноз эффективности по каналам

(Это важный раздел для agent-traffic-executor и контентных агентов.)

6. Experiment Design (дизайн эксперимента)

6.1. Тестовые клетки (cells)

сегмент × оффер × angle × канал

6.2. Распределение бюджета
6.3. Механика теста (ad→landing→lead / content→inbox / waitlist)
6.4. Минимальные объёмы выборки
6.5. Stop-rules
6.6. Accelerate rules
6.7. MDE и статистическая мощность
6.8. План снятия выводов

7. Tactical Execution Plan (машиночитаемое ТЗ)

Это — сердце взаимодействия с другими агентами.

7.1. Кампании (структура)
campaigns:
  - id:
    channel:
    objective:
    daily_budget:
    optimization_goal:
    adsets:
      - id:
        audience:
        placements:
        geo:
        schedule:
        creatives:

7.2. Аудитории

interest-based

lookalikes (если есть данные)

behaviors

custom audiences

контекстные сегменты

7.3. Плейсменты

feed

stories

reels

in-stream

pmax (для Google)

search / display / YT

8. Creative Requirements

8.1. Key messages
8.2. Creative angles
8.3. Visual requirements
8.4. Video scripts (если требуется)
8.5. Variations (A/B)
8.6. Call-to-action
8.7. Размеры/форматы

(Это отдаётся генератору креативов.)

9. Landing Page Requirements

9.1. Цель лендинга
9.2. Структура блоков
9.3. Value props
9.4. Visual guidelines
9.5. Тестируемые офферы
9.6. Формы конверсии
9.7. A/B варианты
9.8. Технические требования (скорость, mobile-first)

10. Tracking & Attribution Requirements

10.1. События (events)
10.2. Pixels / Tags
10.3. Consent mode requirements (GDPR)
10.4. Настройка UTM
10.5. Ограничения по платформенным policy
10.6. Минимальные условия для корректной атрибуции
10.7. Метрики мониторинга в реальном времени

11. Risk Assessment

11.1. Риск-матрица (вероятность × ущерб)
11.2. Операционные риски
11.3. Маркетинговые риски
11.4. Бюджетные риски
11.5. Платформенные риски (баны Ads)
11.6. Меры смягчения

12. Compliance Assessment

12.1. Политики соответствия Ads (Meta/Google/TikTok/LinkedIn)
12.2. Privacy/GDPR требования
12.3. CCPA
12.4. Высокорисковые утверждения / claims
12.5. Список запрещённых practice
12.6. Рекомендации по безопасному запуску

13. Decision Log (JSON)

Каждое решение Совы фиксируется в:

{
  "step": "channel_selection",
  "input": [...],
  "decision": "...",
  "alternatives": [...],
  "rationale": "...",
  "risks": [...],
  "source_citations": ["benchmarks/meta", "jtbd/segment_A"]
}

14. Full JSON Specification for Execution Agents

Единый документ, который подписывает тактическую часть:

strategy:
experiment:
campaigns:
creatives:
landing:
tracking:
risks:
compliance:
decision_log:


Этот блок прямо отдаётся агентам:

traffic-executor

creative-generator

landing-builder

analytics-agent