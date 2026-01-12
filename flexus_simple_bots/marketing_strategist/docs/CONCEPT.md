# Концепция построения ботов в Flexus

**Архитектура: Персона + Навыки (Persona + Skills)**
Бот разделен на два слоя: **Персона** и **Навыки**. Персона (`PERSONA_PROMPT`) определяет идентичность, Tone of Voice и общий подход к работе: "взять задачу, применить экспертизу, выдать результат". Персона не содержит сложной логики маршрутизации; она служит фундаментом для взаимодействия. Вся функциональность вынесена в **Навыки** — изолированные модули доменной экспертизы. "Оркестратор" (default skill с логикой выбора суб-чатов) упразднен; задачи направляются либо напрямую в нужный навык, либо обрабатываются персоной через свободное общение, если задача не требует специфических инструментов.

**Анатомия Навыка (Skill Unit)**
Каждый навык (`skills/*.py`) — это самодостаточный модуль, решающий конкретный класс задач (например, "Диагностика", "Написание контента"). Он состоит из четырех компонентов:
1.  **System Prompt**: Глубокая доменная экспертиза и инструкции.
2.  **Tools**: Строгий, минимально необходимый набор инструментов (`SKILL_TOOLS`), явно запрашиваемый из реестра бота.
3.  **Knowledge (RAG)** *(planned)*: Теги (`SKILL_KNOWLEDGE_TAGS`) для фильтрации базы знаний, обеспечивающие контекст именно для этой области. *Пока не реализовано: теги объявлены, но фильтрация по ним при поиске ещё не подключена.*
4.  **Lark Kernel**: Python-подобный скрипт для жесткой логики (валидация ввода, форматирование вывода, проверка условий завершения), который выполняется до или после вызова LLM, снимая нагрузку с промпта.

**Управление Инструментами и Безопасность**
Используется принцип "Centralized Registry, Decentralized Access". Все доступные боту инструменты регистрируются в `TOOL_REGISTRY` (в `_bot.py`), но каждый навык получает доступ *только* к тем инструментам, которые он явно объявил в своем списке `SKILL_TOOLS`. Это обеспечивает архитектуру с минимальными привилегиями, упрощает отладку (fail-fast при опечатках в именах тулов) и делает зависимости каждого навыка прозрачными и самодокументируемыми.

---

# Bot Construction Concept in Flexus

**Architecture: Persona + Skills**
The bot is divided into two layers: **Persona** and **Skills**. The Persona (`PERSONA_PROMPT`) defines identity, Tone of Voice, and the general work approach: "take the task, apply expertise, deliver the result". The Persona does not contain complex routing logic; it serves as the foundation for interaction. All functionality is offloaded to **Skills** — isolated modules of domain expertise. The "Orchestrator" (default skill with sub-chat selection logic) is abolished; tasks are directed either directly to the specific skill or handled by the persona via free talk if no specific tools are required.

**Skill Unit Anatomy**
Each skill (`skills/*.py`) is a self-contained module solving a specific class of tasks (e.g., "Diagnostics", "Content Writing"). It consists of four components:
1.  **System Prompt**: Deep domain expertise and instructions.
2.  **Tools**: A strict, minimally necessary set of tools (`SKILL_TOOLS`), explicitly requested from the bot's registry.
3.  **Knowledge (RAG)** *(planned)*: Tags (`SKILL_KNOWLEDGE_TAGS`) for knowledge base filtering, ensuring context specific to this area. *Not yet implemented: tags are declared but filtering by them during search is not connected yet.*
4.  **Lark Kernel**: A Python-like script for rigid logic (input validation, output formatting, completion condition checks), executed before or after the LLM call, relieving the prompt of load.

**Tool Management & Security**
The principle of "Centralized Registry, Decentralized Access" is used. All tools available to the bot are registered in `TOOL_REGISTRY` (in `_bot.py`), but each skill gains access *only* to those tools it explicitly declared in its `SKILL_TOOLS` list. This ensures a least-privilege architecture, simplifies debugging (fail-fast on tool name typos), and makes each skill's dependencies transparent and self-documenting.
