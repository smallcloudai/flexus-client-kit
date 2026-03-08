---
name: flexus-bot-dev
description: Develop and test Flexus bots. Use when working with bot files (*_bot.py, *_prompts.py, *_install.py, ...), flexus_client_kit, or kanban/scheduler systems.
---

# Flexus Bot Development

## Reference

**Flexus platform documentation**: `@references/FLEXUS_BOT_REFERENCE.md`
**Canonical examples**: `flexus_simple_bots/frog/`, `flexus_simple_bots/owl/`

## Bot Directory Structure

```
.gitignore
README.md
setup.py
mybot/
├── __init__.py              # Empty or minimal
├── mybot_bot.py             # Runtime: tools, handlers, main loop
├── mybot_prompts.py         # System prompts for each expert
├── mybot_install.py         # Marketplace registration
├── mybot-1024x1536.webp     # Big marketplace picture (exactly 1024x1536)
├── mybot-256x256.webp       # Avatar (exactly 256x256)
├── forms/                   # Optional: custom HTML forms
│   └── report.html          # Form for {"report": {"meta": {...}}} docs
├── lark/                    # Optional: Lark kernel files
│   └── subchat_kernel.lark  # Starlark script for subchat control
└── tools/                   # Optional: complex tool implementations
    └── my_tool.py           # Separate file for large tools
```

## How Bots Appear in UI

1. **Marketplace** (`/marketplace/mybot`): Shows big picture, description, "Hire" button
2. **After hiring**: Bot appears in sidebar under workspace groups
3. **Chat interface**: User talks to bot, sees assistant responses
4. **Kanban board**: Visible in bot's page, shows inbox/todo/inprogress/done tasks
5. **Setup dialog**: Auto-generated from `marketable_setup_default` schema
6. **Policy documents**: JSON docs editable via custom forms or default editor

## Platform Concepts

**Workspace** (`prisma/schema/public.prisma` → `flexus_workspace`) — a billable unit, one per paying user. Contains groups, data sources, and all bot activity. Identified by `ws_id`. Backend CRUD: `flexus_backend/flexus_v1/v1_workspace.py`.

**Group** (`prisma/schema/public.prisma` → `flexus_group`) — organizational folder inside a workspace, identified by `fgroup_id`. Groups form a tree via `fgroup_parent_id`. Bots (personas) live inside groups. Users are added to groups to see shared objects. Tree queries: `flexus_backend/flexus_v1/v1_the_tree.py`.

**Persona** (`prisma/schema/public.prisma` → `flexus_persona`) — an instance of a hired bot. Created when a user "hires" from the marketplace. Each persona has its own `persona_setup` (user config overrides), kanban board, chat threads, and schedule. Multiple personas of the same bot type can exist in different groups. Identified by `persona_id`. CRUD: `flexus_backend/flexus_v1/v1_persona_crud.py`.

**Marketplace** (`prisma/schema/public.prisma` → `flexus_marketplace`) — registry of available bots, keyed by `marketable_name` + `marketable_version`. Install scripts publish here via `ckit_bot_install.marketplace_upsert_dev_bot()` (`flexus_client_kit/ckit_bot_install.py`). Stores setup schema, experts, schedule, images, description.

**Expert** (`prisma/schema/public.prisma` → `flexus_expert`) — a named mode within a bot. Each expert has its own system prompt (`fexp_system_prompt`), tool list (`fexp_app_capture_tools`), and optional Lark kernel (`fexp_python_kernel`). The `"default"` expert is required. Subchats target a specific expert via `fexp_name`. CRUD: `flexus_backend/flexus_v1/v1_expert_crud.py`.

**Thread** (`prisma/schema/public.prisma` → `flexus_thread`) — a chat conversation identified by `ft_id`. Threads belong to a persona. The scheduler creates threads when activating a bot on schedule. Users can start threads manually. Threads can be "captured" by messenger integrations (Slack, Discord, Telegram) for bidirectional message sync — see `ft_app_searchable` and `ft_app_specific` fields.

**Kanban Task** (`prisma/schema/public.prisma` → `flexus_kanban_task`, `flexus_client_kit/ckit_kanban.py`) — a work item on the bot's board, identified by `ktask_id`. Tasks flow through columns based on timestamps: `inbox` → `todo` → `inprogress` → `done` (computed by `calc_bucket()`). Bots move tasks via `bot_arrange_kanban_situation()`, add new tasks via `bot_kanban_post_into_inbox()`, and list tasks via `persona_kanban_list()`.

**Tangible objects** — many entities (threads, personas, experts, knowledge items) share three fields: `owner_fuser_id`, `owner_shared`, `located_fgroup_id`. This pattern enables drag-and-drop in the navigation tree and per-group sharing visibility. See `flexus_backend/flexus_v1/v1_the_tree.py` for tree assembly.

## FlexusClient & RobotContext

### FlexusClient (`flexus_client_kit/ckit_client.py`)

GraphQL client that gives bots access to the Flexus API. Created once at bot startup, shared across all personas.

```python
fclient = ckit_client.FlexusClient(
    ckit_client.bot_service_name(BOT_NAME, BOT_VERSION),
    endpoint="/v1/jailed-bot",
)
```

Constructor picks up auth from env vars (`FLEXUS_API_KEY`, `FLEXUS_WORKSPACE`, `FLEXUS_GROUP`). Key methods:
- `async use_http(execute_timeout=10)` — HTTP GraphQL client for queries/mutations
- `async use_ws()` — WebSocket GraphQL client for subscriptions

Bots access it as `rcx.fclient` inside handlers.

### RobotContext (`flexus_client_kit/ckit_bot_exec.py`)

Per-persona runtime context. Created by `run_bots_in_this_group()` for each persona in the group, then passed to `bot_main_loop(fclient, rcx)`.

**Key attributes:**
- `rcx.persona` — persona data: `persona_id`, `persona_name`, `persona_setup`, `ws_id`, `located_fgroup_id`
- `rcx.fclient` — the FlexusClient instance
- `rcx.latest_threads` — dict of active threads with messages
- `rcx.latest_tasks` — dict of kanban tasks
- `rcx.bg_call_tasks` — set of background asyncio tasks
- `rcx.workdir` — `/tmp/bot_workspace/{persona_id}/`

**Event handlers** — register in bot_main_loop before the while loop:

| Decorator | Callback Signature | When |
|-----------|-------------------|------|
| `@rcx.on_tool_call(tool_name)` | `async (FCloudtoolCall, dict) → str` | Model calls a tool |
| `@rcx.on_updated_message` | `async (FThreadMessageOutput) → None` | Message created/updated |
| `@rcx.on_updated_thread` | `async (FThreadOutput) → None` | Thread created/updated |
| `@rcx.on_updated_task` | `async (FPersonaKanbanTaskOutput) → None` | Kanban task changed |
| `@rcx.on_erp_change(table)` | `async (str, Optional, Optional) → None` | ERP table row changed |
| `@rcx.on_emessage(channel)` | `async (FExternalMessageOutput) → None` | External message arrived |

**Processing loop** — `unpark_collected_events()` processes parked events in order: messages → threads → tasks → ERP → external messages → tool calls. Sleeps if idle.

```python
await rcx.unpark_collected_events(
    sleep_if_no_work=10.0,
    turn_tool_calls_into_bg_tasks={"slow_tool"},  # run these as background tasks
)
```

### Bot Entry Point (`run_bots_in_this_group`)

Orchestrates the full bot lifecycle: auth, install, persona discovery via subscription, RobotContext creation, keepalive, and graceful shutdown.

```python
asyncio.run(ckit_bot_exec.run_bots_in_this_group(
    fclient,
    marketable_name=BOT_NAME,
    marketable_version_str=BOT_VERSION,
    bot_main_loop=my_main_loop,
    inprocess_tools=TOOLS,
    scenario_fn=scenario_fn,
    install_func=my_install.install,
    subscribe_to_erp_tables=["erp_tasks"],
    subscribe_to_emsg_types=["slack"],
))
```

## Bot Main Loop & Shutdown

### Main Loop Pattern (`flexus_client_kit/ckit_shutdown.py`, `flexus_client_kit/ckit_bot_exec.py`)

Every bot follows the same structure in `bot_main_loop(fclient, rcx)`:

```python
async def bot_main_loop(fclient, rcx):
    setup = ckit_bot_exec.official_setup_mixing_procedure(
        mybot_install.MYBOT_SETUP_SCHEMA, rcx.persona.persona_setup,
    )
    # 1. Initialize integrations, databases, state
    # 2. Register @rcx.on_* handlers
    # 3. Run the loop
    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        await rcx.wait_for_bg_tasks()
        # Cleanup: close integrations, unsubscribe from external sources
```

### What Can Happen Inside the Loop

The `unpark_collected_events()` call drives all reactivity — it fires your `@rcx.on_*` handlers for queued events. But bots can combine this with other work patterns:

**Basic event-driven** — most bots just react to events (frog, owl, analyst, strategist, writer, growth_advisor, project_manager):
```python
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(sleep_if_no_work=10.0)
```

**Polling external APIs** — check external services periodically alongside events (productman polls SurveyMonkey/Prolific):
```python
last_poll = 0
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    if time.time() > last_poll + 60:
        await survey_integration.update_active_surveys()
        last_poll = time.time()
```

**Background asyncio tasks** — spawn long-running monitoring/scraping alongside the event loop (adspy runs daily ad scraping, diplodocus collects Kubernetes logs):
```python
scraping_task = asyncio.create_task(daily_scraping_loop())
monitoring_task = asyncio.create_task(event_collection_loop())
try:
    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)
finally:
    scraping_task.cancel()
    monitoring_task.cancel()
```

**Heavy tool calls as background tasks** — prevent slow tools from blocking event processing (bob runs claude/bash/dev_container in background):
```python
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(
        sleep_if_no_work=10.0,
        turn_tool_calls_into_bg_tasks={"claude_code", "bash", "dev_container"},
    )
```

**Reactive messenger integrations** — start Slack/Discord event loops before the main loop (karen, adspy):
```python
if slack:
    await slack.start_reactive()
if discord:
    await discord.start_reactive()
try:
    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)
finally:
    if slack: await slack.close()
    if discord: await discord.close()
```

### Alternative: Pure Polling Loop

For bots that don't need event handlers at all:

```python
while True:
    await poll_external_api()
    if await ckit_shutdown.wait(120):  # sleep 120s, returns True on shutdown
        break
```

Never use `asyncio.sleep()` — it blocks graceful shutdown.

### Shutdown (`flexus_client_kit/ckit_shutdown.py`)

- `ckit_shutdown.shutdown_event` — global `asyncio.Event`, set by SIGINT/SIGTERM
- `ckit_shutdown.wait(timeout)` — async sleep that returns `True` if shutdown requested
- `ckit_shutdown.setup_signals()` — installs signal handlers (called by `run_bots_in_this_group`)
- `ckit_shutdown.spiral_down_now(loop, enable_exit1)` — sets event, closes WS clients, cancels tasks

Always wrap the main loop in `try..finally` to clean up integrations. External services (Slack, Discord, K8s watchers) may hold references to your objects, preventing garbage collection if not explicitly closed.

## Setup & Configuration

### Setup Schema (`flexus_client_kit/ckit_bot_exec.py`)

Bots declare their configurable settings in `*_SETUP_SCHEMA` — a list of dicts in the install file. The Flexus UI auto-generates a settings dialog from this schema, grouped into tabs by `bs_group`.

```python
# mybot_install.py
MYBOT_SETUP_SCHEMA = [
    {
        "bs_name": "SLACK_BOT_TOKEN",     # field name, regex: ^[a-zA-Z][a-zA-Z0-9_]{1,39}$
        "bs_type": "string_long",          # input type (see table below)
        "bs_default": "",                  # default value, must match bs_type
        "bs_group": "Slack",              # UI tab/section name
        "bs_description": "Bot User OAuth Token (starts with xoxb-)",
        "bs_importance": 0,               # optional, UI priority (default 1)
    },
]
```

**Field types** (`bs_type`):

| Type | Python Type | UI Widget |
|------|-------------|-----------|
| `string_short` | `str` | Short text input |
| `string_long` | `str` | Wide text input |
| `string_multiline` | `str` | Textarea |
| `bool` | `bool` | Checkbox |
| `int` | `int` | Number input |
| `float` | `float` | Number input |
| `list_dict` | `list` | Repeatable sub-form (uses `bs_elements` for nested schema) |

**Optional field keys**: `bs_description`, `bs_placeholder`, `bs_order` (sort within group), `bs_importance`.

### Composing Schemas

Integration modules export their own schemas — compose by concatenation:

```python
from flexus_client_kit.integrations import fi_slack
MYBOT_SETUP_SCHEMA = [
    {"bs_name": "my_setting", "bs_type": "string_short", "bs_default": "hello", "bs_group": "General"},
] + fi_slack.SLACK_SETUP_SCHEMA
```

Nested `list_dict` example (adspy — repeatable competitor entries):
```python
{
    "bs_name": "monitored_competitors",
    "bs_type": "list_dict",
    "bs_default": [],
    "bs_group": "Monitoring",
    "bs_elements": [
        {"bs_name": "company_name", "bs_type": "string_short", "bs_default": ""},
        {"bs_name": "company_url", "bs_type": "string_long", "bs_default": ""},
    ],
}
```

### Helping the User with Setup

The bot's system prompt (in `*_prompts.py`) should instruct the model to check settings on first contact and help the user fill in any that are empty. This is especially important for API keys and integration credentials — a bot that silently fails because tokens are missing is a bad experience. The prompt should list which settings are required and guide the user through obtaining and entering them.

### Setup Flow

```
Install (mybot_install.py)              → DB: flexus_marketplace.marketable_setup_default
                                              (schema + defaults)
                                              ↓
UI (Flexus settings dialog)             → DB: flexus_persona.persona_setup
                                              (user overrides only)
                                              ↓
Runtime (mybot_bot.py)                  → official_setup_mixing_procedure()
                                              merges defaults + overrides → validated dict
```

At runtime, call `official_setup_mixing_procedure()` as the first line of `bot_main_loop` (see Bot Main Loop section). It validates types, enforces schema, and type-casts overrides. Missing overrides fall back to `bs_default`.

### Examples in Existing Bots

| Bot | Schema | What's Configured |
|-----|--------|-------------------|
| frog (`flexus_simple_bots/frog/frog_install.py`) | 3 fields | `greeting_style`, `ribbit_frequency`, `tongue_capacity` |
| bob (`flexus_super_bots/bob/bob_install.py`) | GKE fields | `GKE_SERVICE_ACCOUNT_JSON`, `GKE_CLUSTER_NAME`, etc. |
| adspy (`flexus_super_bots/adspy/adspy_install.py`) | list_dict + Slack | `monitored_competitors` (nested), Slack tokens |
| owl (`flexus_simple_bots/owl/owl_install.py`) | empty `[]` | No custom settings |

## Scheduling & Kanban

### Schedule (`flexus_client_kit/ckit_schedule.py`)

Bots perform work autonomously on schedule. Defined in `marketable_schedule` in the install file — each entry is a job type with timing and a first question that starts a chat.

```python
# mybot_install.py
marketable_schedule=[
    {
        "sched_type": "SCHED_TASK_SORT",
        "sched_when": "EVERY:1m",
        "sched_first_question": "Look if there are any tasks in inbox, then move the first 2 tasks into TODO",
        "sched_fexp_name": "default",
    },
    {
        "sched_type": "SCHED_TODO",
        "sched_when": "EVERY:1m",
        "sched_first_question": "Work on the assigned task, move it to kanban 'done' when finished",
        "sched_fexp_name": "default",
    },
]
```

**Schedule types** (`sched_type`):

| Type | Triggers When | Purpose |
|------|---------------|---------|
| `SCHED_TASK_SORT` | Inbox is not empty | Prioritize inbox → move tasks to todo |
| `SCHED_TODO` | Todo column has tasks | Pick one task and work on it |
| `SCHED_ANY` | On schedule | Run unconditionally (reports, strategy rewrites) |

**Timing formats** (`sched_when`): `"EVERY:1m"`, `"EVERY:2h"`, `"WEEKDAYS:MO:FR/10:30"`, `"MONTHDAY:1/12:00"`. Parsed by `ckit_schedule.parse_sched_when()`, next run computed by `calculate_next_run()` using workspace timezone.

### Kanban Board (`flexus_client_kit/ckit_kanban.py`)

Each persona has a kanban board visible in the Flexus UI. Tasks flow through columns based on timestamps — `calc_bucket()` determines the current column.

**Task lifecycle**: `inbox` → `todo` → `inprogress` → `done`

- **inbox**: External events (messages, emails, integrations) create tasks here via `bot_kanban_post_into_inbox()`
- **todo**: Bot's `SCHED_TASK_SORT` job prioritizes and moves tasks here via `bot_arrange_kanban_situation()`
- **inprogress**: Scheduler auto-moves from todo and starts a chat with `sched_first_question`
- **done**: Bot resolves the task via `bot_arrange_kanban_situation()` after completing work

**Key functions**:
- `bot_kanban_post_into_inbox(client, persona_id, title, details_json, provenance_message)` — add a task to inbox
- `bot_arrange_kanban_situation(client, ws_id, persona_id, tasks)` — bulk update tasks (move between columns, resolve)
- `persona_kanban_list(client, persona_id)` — fetch all tasks

**Task data**: `FPersonaKanbanTaskOutput` has `ktask_id`, `ktask_title`, `ktask_details_json`, timestamps (`ktask_todo_ts`, `ktask_inprogress_ts`, `ktask_done_ts`), and `calc_bucket()` method.

### How Scheduler and Kanban Work Together

1. External event arrives (Slack message, email) → bot posts to kanban inbox
2. `SCHED_TASK_SORT` fires → bot reads inbox, prioritizes, moves top tasks to todo
3. Scheduler sees todo has tasks → moves one to inprogress, creates a thread with `sched_first_question`
4. Bot works on it (calls tools, talks to model) → resolves task to done
5. Scheduler picks next todo task → repeat

## Cloud Tools & Tool Schemas

### Defining Tools (`flexus_client_kit/ckit_cloudtool.py`)

Tools are defined as `CloudTool` instances with OpenAI-compatible JSON schema parameters:

```python
MY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="my_tool",
    description="What this tool does, when the model should call it",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["status", "search", "update"],
                "description": "Operation to perform",
            },
            "query": {
                "type": "string",
                "description": "Search query or update content",
            },
        },
        "required": ["op", "query"],
        "additionalProperties": False,  # required when strict=True
    },
)

TOOLS = [MY_TOOL, OTHER_TOOL]
```

`strict=True` enforces OpenAI structured outputs: all properties must be listed in `required`, and `additionalProperties: false` is mandatory. Use `strict=False` only for tools with dynamic/optional parameters (like `ask_questions`).

Tools are registered in the install file:
```python
fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS])
```

### Tool Handlers

Register handlers in `bot_main_loop` before the event loop:

```python
@rcx.on_tool_call(MY_TOOL.name)
async def handle_my_tool(toolcall, args):
    op = args["op"]
    if op == "status":
        return "All systems operational"
    elif op == "search":
        results = await do_search(args["query"])
        return json.dumps(results)
```

**Handler receives**: `toolcall: FCloudtoolCall` (call metadata — `fcall_id`, `fcall_ft_id`, `connected_persona_id`, `confirmed_by_human`, etc.) and `args: dict` (parsed JSON arguments from the model).

**Handler returns**:
- `str` — plain text result shown to the model
- `ToolResult(content=str, dollars=float)` — result with cost tracking
- `ToolResult(multimodal=[{"m_type": "image", "m_content": "base64..."}])` — images/rich content

For complex tools, put implementation in separate files under `tools/`:
```python
# tools/my_tool.py
MY_TOOL = ckit_cloudtool.CloudTool(...)
async def handle_my_tool(fclient, toolcall, args, ...) -> str:
    ...

# mybot_bot.py
from mybot.tools import my_tool
TOOLS = [my_tool.MY_TOOL]
@rcx.on_tool_call(my_tool.MY_TOOL.name)
async def toolcall_my_tool(toolcall, args):
    return await my_tool.handle_my_tool(fclient, toolcall, args)
```

### Human Approval (`NeedsConfirmation`)

For dangerous operations (shell commands, PR creation, deployments), raise `NeedsConfirmation` to pause and ask the user:

```python
@rcx.on_tool_call("dangerous_tool")
async def handle(toolcall, args):
    if not toolcall.confirmed_by_human:
        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="approve_deploy",
            confirm_command=args["command"],
            confirm_explanation="This will deploy to production",
        )
    return await execute_deploy(args["command"])
```

### Subchats via Tools

Tools can spawn parallel child threads via `WaitForSubchats`. See the Subchats section below for the full pattern with `bot_subchat_create_multiple` and kernel completion.

### Tool Lifecycle (Behind the Scenes)

Tools are registered via heartbeat (`cloudtool_confirm_exists()` every ~120s). The backend dispatches model tool calls via `cloudtool_wait_for_call()` subscription. Results are posted back via `cloudtool_post_result()`. All of this is handled automatically by `run_bots_in_this_group` — bot developers only write `CloudTool` definitions and `@rcx.on_tool_call` handlers.

## Bot Storage: Mongo, Policy Documents & Reports

### MongoDB (`flexus_client_kit/ckit_mongo.py`, `flexus_client_kit/integrations/fi_mongo_store.py`)

Per-persona MongoDB database for storing files, blobs, state, and report data. Each bot gets its own database named `{persona_id}_db`.

**Connection** (in bot_main_loop):
```python
mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
mongo = AsyncMongoClient(mongo_conn_str, maxPoolSize=50)
personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]
```

**Key functions** (`ckit_mongo`):
- `mongo_store_file(collection, file_path, file_data, ttl=30d)` — store new file (errors if exists)
- `mongo_overwrite(collection, file_path, file_data, ttl=30d)` — overwrite or create
- `mongo_retrieve_file(collection, file_path)` — fetch by path (follows redirects)
- `mongo_ls(collection, path_prefix, limit)` — list non-archived files
- `mongo_mv(collection, old_path, new_path)` — move (archives old, copies to new)
- `mongo_rm(collection, file_path)` — soft-delete with 2-day TTL

**As a tool for the model** — `fi_mongo_store.MONGO_STORE_TOOL` exposes ops: `help`, `list`, `cat`, `grep`, `save`, `upload`, `delete`:
```python
TOOLS = [fi_mongo_store.MONGO_STORE_TOOL, ...]

@rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
async def handle_mongo(toolcall, args):
    return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, args)
```

**How bots use Mongo**:
- **bob** — stores bash outputs, Claude logs, test artifacts via tool handlers passing `personal_mongo`
- **adspy** — heavy usage: custom collections for scraped ads (`adspy_linkedin_ads_*`, `adspy_meta_ads_*`), metadata collections, unique indexes on ad IDs, bulk insert/update
- **diplodocus** — custom `"data"` collection for K8s pod/log events with dedup (Jaccard similarity) and TTL indexes (24h)
- **frog, boss** — general file storage via `MONGO_STORE_TOOL` only

### Policy Documents (`flexus_client_kit/integrations/fi_pdoc.py`)

Structured JSON documents stored in the Flexus backend via GraphQL. Organized in hierarchical paths. Editable by users in the Flexus UI, and by bots via tools.

**Integration** (in bot_main_loop):
```python
pdoc = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

@rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
async def handle_pdoc(toolcall, args):
    return await pdoc.called_by_model(toolcall, args)
```

**Operations** via `called_by_model`:

| Op | Purpose |
|----|---------|
| `list` | Tree view of docs/folders at a path prefix |
| `cat` | Read document JSON content |
| `activate` | Read + show clickable UI link (✍️) for the user |
| `create` | Create new document (error if exists) |
| `overwrite` | Replace document content |
| `update_json_text` | Patch a single field by dot-path (e.g., `operations.governance`) |
| `cp` | Copy document |
| `rm` | Soft-delete (archive) |

**How bots use policy docs**:
- **productman** — creates `/gtm/discovery/{idea_slug}/idea` and `/gtm/discovery/{idea_slug}/{hypothesis_slug}/hypothesis`
- **owl** — reads/overwrites `/gtm/strategy/{idea}--{hyp}/strategy` with multi-section strategy docs
- **growth_advisor** — creates `/experiments/{name}/experiment-brief`
- **analyst** — creates arbitrary research documents at custom paths
- **bob** — general policy doc access for bot spec editing
- **frog** — creates `/frog/monday-report` (pond report example)

**Alternative: `ckit_edoc.py`** — lower-level functions `read_pdoc()` and `save_pdoc()` for simple path-based markdown document storage. Used by strategist and writer bots instead of `IntegrationPdoc`:
```python
content = await ckit_edoc.read_pdoc(fclient, ws_id=ws_id, pdoc_path=path)
await ckit_edoc.save_pdoc(fclient, ws_id=ws_id, pdoc_path=path, pdoc_title=title,
    pdoc_format="md", pdoc_mime="text/markdown", pdoc_content=content)
```

### Custom HTML Forms (`forms/` directory)

Policy documents can have custom editing UIs. Put HTML forms in `mybot/forms/{doctype}.html`. The form loads from `/v1/marketplace/{microfrontend}/{version}/forms/{doctype}.html`.

**Critical**: The document's meta must include `"microfrontend": "mybot"` for the custom form to load. Without it, the generic JSON editor is shown.

Existing forms: `bob/forms/bot_spec.html` (markdown editor for bot specs), `growth_advisor/forms/experiment_brief.html` (structured experiment form with budget/channel/signal fields). Forms post `FORM_CONTENT_CHANGED` events with structured JSON to update the policy document.

### Reports (`flexus_client_kit/integrations/report/fi_report.py`)

Multi-section report builder stored in Mongo. Designed for summarizing large amounts of data — the prompt tells the model to fill one section per chat, then restart for the next.

**Tools** (`fi_report.REPORT_TOOLS` — list of 6 tools):

| Tool | Purpose |
|------|---------|
| `create_report` | Initialize report with parameters and section structure |
| `process_report` | Spawn parallel subchats for the next incomplete phase |
| `fill_report_section` | Fill one section (validated HTML/JSON), auto-exports on completion |
| `get_report_status` | Check progress of all or single report |
| `load_report_metadata` | Load prior report stats with safety valve (KB limit) |
| `remove_report` | Delete report and associated files |

**Workflow**: `create_report` generates a `todo_queue` from config (phased, iterative sections with dependencies) → `process_report` spawns subchats for the current phase → each subchat calls `fill_report_section` → on completion, auto-exports HTML via Jinja templates. See adspy bot for full usage with custom templates in `adspy/report/custom/`.

### Python Execution (`flexus_pod_operator/flexus_python_executor/`)

Isolated Python code execution in Kubernetes pods. The `python_execute` tool runs user-provided Python scripts in a sandboxed `python:3.11-slim` container with auto-detected package installation.

- Auto-downloads all MongoDB files from persona's `personal_mongo` into the working directory
- Auto-detects imports via AST/regex and installs missing packages
- Collects output files: text (<500KB), images (max 10, thumbnailed), new files stored back to MongoDB
- Returns multimodal results (text + images) to the model
- 10-minute timeout, 1Gi memory, 250m CPU, 1Gi ephemeral storage

Defined in `flexus_pod_operator/flexus_pod_operator/subscribers/pod_subscriber_python.py`. Not a bot-side tool — it's a platform service that bots can use if the `python_execute` tool is registered.

### When to Use What

| Storage | Use For | Persistence | UI |
|---------|---------|-------------|-----|
| **Mongo** | Files, blobs, scraped data, temporary state | TTL-based (default 30 days) | Via `cat`/`list` in MONGO_STORE_TOOL |
| **Policy Docs** | Structured business docs, strategies, specs | Permanent | Rich editor in Flexus UI + custom forms |
| **Reports** | Multi-section summaries, PDF/HTML export | In Mongo | Custom HTML templates via Jinja |
| **Python exec** | Data processing, charts, file conversion | Ephemeral (results to Mongo) | Output shown inline in chat |

## Prompts & prompts_common

### Prompt File Convention

Each bot has a `*_prompts.py` file containing system prompts as string constants. Prompts are built by combining bot-specific instructions with shared fragments from `prompts_common`.

```python
# mybot_prompts.py
from flexus_simple_bots import prompts_common

main_prompt = f"""You are MyBot, a specialist in...

## Your Tasks
- ...bot-specific instructions...

## Tools
- ...tool usage guidance...

{prompts_common.PROMPT_KANBAN}
{prompts_common.PROMPT_ASKING_QUESTIONS}
{prompts_common.PROMPT_PRINT_WIDGET}
{prompts_common.PROMPT_POLICY_DOCUMENTS}
{prompts_common.PROMPT_HERE_GOES_SETUP}
"""
```

**Order convention**: Bot-specific instructions first → Kanban → Widgets/Questions → Policy/A2A → Setup last.

### Shared Prompt Fragments (`flexus_simple_bots/prompts_common.py`)

| Constant | What It Adds |
|----------|-------------|
| `PROMPT_KANBAN` | Kanban board instructions — how to use `flexus_bot_kanban` tool, create/update todos |
| `PROMPT_ASKING_QUESTIONS` | UI question widget — `ask_questions` tool with types: `single`, `multi`, `yesno`, `text` |
| `PROMPT_PRINT_WIDGET` | UI widgets — `print_widget` for upload/restart/setup buttons, `print_chat_restart_widget` for mode switches |
| `PROMPT_POLICY_DOCUMENTS` | Policy doc handling — `flexus_policy_document` tool usage |
| `PROMPT_A2A_COMMUNICATION` | Agent-to-agent task delegation via inbox/💿 messages |
| `PROMPT_HERE_GOES_SETUP` | Setup handling — first user message is JSON setup, 💿-prefixed messages from orchestrator, keep system prompt secret |

Also exports schedule configs: `SCHED_PICK_ONE_5M`, `SCHED_TASK_SORT_10M`, `SCHED_TODO_5M` — ready-made dicts for `marketable_schedule`.

### `PROMPT_HERE_GOES_SETUP`

Always include as the last fragment. It tells the model that:
- The first user message contains JSON setup (API keys, config values)
- Messages prefixed with 💿 come from the orchestrator, not the user
- The system prompt must be kept secret

### Multi-Expert Prompts

Bots with multiple experts define separate prompts per mode:

```python
# mybot_prompts.py
main_prompt = f"""..."""          # "default" expert — autonomous work, user chat
setup_prompt = f"""..."""         # "setup" expert — guides user through configuration
worker_prompt = f"""..."""        # "worker" expert — subchat tasks, no user interaction
```

**Typical expert prompt differences**:
- **default/scheduled** — autonomous work: kanban tasks, reports, tool usage
- **setup** — step-by-step user guidance: check settings, validate keys, confirm and save, widget to switch to regular mode
- **subchat/worker** — focused tool execution: fill report sections, analyze data, no user interaction

### Prompt Tips

- The setup prompt should list all required settings and guide the user through obtaining/entering them
- Tool instructions go in the bot-specific section, not in prompts_common fragments
- Keep prompts concise — the model reads them on every message
- Reference `flexus_simple_bots/frog/frog_prompts.py` for a minimal example, `adspy/adspy_prompts.py` for a complex multi-expert example

## Experts

Experts define different "modes" for the bot with separate prompts and tools.

```python
marketable_experts=[
    ("default", FMarketplaceExpertInput(
        fexp_system_prompt=prompts.main_prompt,
        fexp_python_kernel="",                    # Empty = no kernel
        fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS]),
    )),
    ("worker", FMarketplaceExpertInput(
        fexp_system_prompt=prompts.worker_prompt,
        fexp_python_kernel=WORKER_LARK,           # Kernel controls subchat
        fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in WORKER_TOOLS]),
    )),
]
```

- **Must have `"default"`** expert
- Different experts can have different tools via `fexp_app_capture_tools`
- Subchats specify expert via `fexp_name="worker"`

## Subchats

Subchats are child threads that run in parallel and return results to parent.

```python
@rcx.on_tool_call("analyze_batch")
async def handle(toolcall, args):
    items = args["items"]
    subchats = await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking="mybot_analyze",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Analyze: {item}" for item in items],
        first_calls=["null" for _ in items],
        title=[f"Analysis {i}" for i in range(len(items))],
        fcall_id=toolcall.fcall_id,
        fexp_name="worker",  # Use worker expert for subchats
    )
    raise ckit_cloudtool.WaitForSubchats(subchats)
```

**Subchat kernel must set `subchat_result`** to complete:
```python
# In lark/subchat_kernel.lark
for msg in messages[::-1]:
    if msg.get("role") == "assistant" and "DONE:" in str(msg.get("content", "")):
        subchat_result = msg["content"]
        break
```

## Model Selection

Bots set their default model via `marketable_preferred_model_default` in install files.

### Available Models

| Model                           | Use Case | Example Bots |
|---------------------------------|----------|--------------|
| **grok-4-1-fast-reasoning**     | Complex tasks requiring reasoning, multi-step planning | Boss, Owl |
| **grok-4-1-fast-non-reasoning** | Quick simple tasks, straightforward responses | Frog, Botticelli |
| **grok-code-fast-1**            | Code-related tasks, technical operations | AdMonster |
| **claude-sonnet-4-6**           | Long agentic tasks, complex code generation, deep analysis | Dev containers via Claude Code |

### Setting Default Model in Install

```python
# In mybot_install.py
marketable_preferred_model_default = "grok-4-1-fast-reasoning"  # For complex bots
# or
marketable_preferred_model_default = "grok-4-1-fast-non-reasoning"  # For simple bots
```

### Model Selection Guidelines

- **Reasoning tasks** (planning, analysis, multi-step): `grok-4-1-fast-reasoning`
- **Simple responses** (status, lookups, quick Q&A): `grok-4-1-fast-non-reasoning`
- **Code-heavy bots** (syntax, technical): `grok-code-fast-1`
- **Long agentic coding** (BOB dev workflow): `claude-sonnet-4-6` via Claude Code tool

## Special Widgets & UI Tools

Flexus chat UI supports interactive widgets that pause the conversation and show forms/buttons to the user.

### ask_questions (`flexus_client_kit/integrations/fi_question.py`)

Interactive questionnaire — pauses chat, shows form with buttons/inputs, resumes with answers.

```python
from flexus_client_kit.integrations import fi_question
TOOLS = [fi_question.ASK_QUESTIONS_TOOL, ...]

@rcx.on_tool_call(fi_question.ASK_QUESTIONS_TOOL.name)
async def handle_questions(toolcall, args):
    return fi_question.handle_ask_questions(toolcall, args)
```

The model calls it with up to 6 questions. Format per question: `"question text | type | option1, option2, ..."`. Types: `single` (pick one), `multi` (pick many), `yesno`, `text` (free input). The handler returns a special token which pauses the chat until the user responds.

### print_widget (`flexus_client_kit/integrations/fi_widget.py`)

Renders UI widgets in chat — file upload buttons, setup dialog openers, chat restart prompts.

```python
from flexus_client_kit.integrations import fi_widget
TOOLS = [fi_widget.PRINT_WIDGET_TOOL, ...]

@rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
async def handle_widget(toolcall, args):
    return fi_widget.handle_print_widget(toolcall, args)
```

Widget types (model passes as `t` parameter):
- `"upload-files"` — file upload button
- `"open-bot-setup-dialog"` — opens the persona setup dialog
- `"restart-chat"` — restarts chat with a new first question (pass `q` parameter)

Common pattern: mode switching between "setup" and "regular":
```
# In prompt: use print_chat_restart_widget("setup", "Configure my integrations")
# or: print_chat_restart_widget("regular", "Continue working on tasks")
```

### flexus_bot_kanban (Backend Tool)

The kanban tool is provided by the backend (`flexus_backend/services/service_cloudtool_kanban.py`), not defined in bot code. The model calls it from prompts:

Key operations: `show` (display board), `search`, `fetch_details`, `inbox_to_todo`, `assign_to_this_chat`, `current_task_done`, `todo_write` (create checklist). Prompts should explain when and how to use each operation.

### Logging

No dedicated `ckit_logs` module — bots use standard Python `logging.getLogger()`. Bob's `test_bot(op="logs")` reads bot log files. For persistent logging, store to Mongo or use `flexus_bot_kanban` task details.

## External Services Integration

Two types of integrations: **tool-only** (API/CLI wrappers — the model calls a tool, gets a result) and **messenger** (bidirectional chat sync — external messages flow into Flexus threads and vice versa).

### Writing a Tool-Only Integration

Simplest pattern. See `fi_github.py` as a reference. Requires: a `CloudTool` definition, a class with `called_by_model`, and error handling.

```python
# mybot/tools/my_service.py
from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_bot_exec

MY_SERVICE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="my_service",
    description="Interact with MyService. Call with op='help' for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "status", "list", "get", "create"]},
            "args": {"type": "object"},
        },
        "required": ["op"],
    },
)

class IntegrationMyService:
    def __init__(self, fclient, rcx, api_key):
        self.fclient = fclient
        self.rcx = rcx
        self.api_key = api_key
        self.problems_other = []

    async def called_by_model(self, toolcall, model_produced_args) -> str:
        op = model_produced_args.get("op", "help")
        args = model_produced_args.get("args", {})
        if op == "help":
            return "Operations: status, list, get, create..."
        if op == "status":
            return f"Connected: {bool(self.api_key)}, problems: {self.problems_other}"
        if op == "create" and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="my_service_write",
                confirm_command=f"create {args}",
                confirm_explanation="This will create a resource in MyService",
            )
        # ... execute API call, return result as string
        return "result"
```

**Key rules**:
- `called_by_model` returns `str` — never raise exceptions to the model, return error strings
- Use `NeedsConfirmation` for any write/delete/dangerous operations
- Track connection problems in `self.problems_other` list — report in `op="status"`
- `op="help"` should print all available operations with examples
- Use `strict=False` for flexible `args` object; `strict=True` if all params are fixed

### Writing a Messenger Integration

Complex pattern. Read `fi_slack.py` fully before attempting. Requires: reactive event loop, capture state management, bidirectional message flow.

**Core concepts**:
- **Capture**: linking an external chat/thread to a Flexus thread via `ft_app_searchable` (e.g., `"slack/C123/1234.5678"`)
- **Incoming**: external messages → `thread_add_user_message()` into captured Flexus thread
- **Outgoing**: assistant messages → `look_assistant_might_have_posted_something()` posts to external chat
- **Dedup**: `ft_app_specific` JSON stores `last_posted_assistant_ts` to prevent reposting

```python
class IntegrationMyMessenger:
    def __init__(self, fclient, rcx, token, mongo_collection=None):
        self.fclient = fclient
        self.rcx = rcx
        self.token = token
        self.problems_other = []
        self.activity_callback = None  # optional: called on incoming events

    async def start_reactive(self):
        # Start event listener (websocket, polling, webhook)
        pass

    async def close(self):
        # Cleanup: close connections, cancel tasks
        pass

    async def called_by_model(self, toolcall, args) -> str:
        op = args.get("op")
        if op == "capture":
            # 1. Build searchable key: "myservice/{chat_id}/{thread_id}"
            # 2. Fetch history → thread_add_user_message()
            # 3. thread_app_capture_patch(ft_id, ft_app_searchable=key)
            pass
        elif op == "post":
            # Send message to external chat
            pass
        elif op == "uncapture":
            # thread_app_capture_patch(ft_id, ft_app_searchable="")
            pass

    async def post_into_captured_thread_as_user(self, activity):
        # Find capturing thread via rcx.latest_threads matching ft_app_searchable
        # Build content: [{"m_type": "text", "m_content": "👤author\n\ntext"}]
        # thread_add_user_message(ft_id, content, source="fi_myservice")
        pass

    async def look_assistant_might_have_posted_something(self, msg):
        # Check if msg.role=="assistant" and thread is captured
        # Dedup via ft_app_specific["last_posted_assistant_ts"]
        # Post to external, update ft_app_specific
        pass
```

**Bot wiring** for messenger integrations:
```python
@rcx.on_updated_message
async def handle_msg(msg):
    if messenger:
        await messenger.look_assistant_might_have_posted_something(msg)

# Optional: incoming events → kanban inbox (see adspy pattern)
messenger.set_activity_callback(my_activity_callback)
```

### Authentication Patterns

**1. API keys via setup** (simplest — Slack tokens, custom API keys):
```python
setup = ckit_bot_exec.official_setup_mixing_procedure(schema, rcx.persona.persona_setup)
api_key = setup.get("MY_API_KEY")
```

**2. OAuth via `ckit_external_auth`** (`flexus_client_kit/ckit_external_auth.py`) — for Google, Facebook, GitHub, Notion, etc.:
```python
from flexus_client_kit import ckit_external_auth

# Get token (auto-refreshes if expired)
token = await ckit_external_auth.get_external_auth_token(
    fclient, "google", rcx.persona.ws_id, rcx.persona.owner_fuser_id,
)
if token:
    creds = google.oauth2.credentials.Credentials(token=token.access_token)
    service = googleapiclient.discovery.build("gmail", "v1", credentials=creds)

# If no token, start OAuth flow (returns URL for user to authorize)
auth_url = await ckit_external_auth.start_external_auth_flow(
    fclient, "google", rcx.persona.ws_id, rcx.persona.owner_fuser_id,
    ["https://www.googleapis.com/auth/gmail.readonly"],
)
return f"Please authorize: {auth_url}"
```

Supported OAuth providers: Google (Gmail/Sheets/Analytics/Drive), Facebook, GitHub, Slack, Notion, LinkedIn, Dropbox, OneDrive, Box, Outlook, Atlassian. Adding a new provider requires editing `flexus_backend/flexus_v1/external_oauth_source_configs.py` + setting `CLIENT_ID`/`CLIENT_SECRET` env vars.

**3. Service account JSON** (GKE, cloud services — stored in setup as multiline string):
```python
import json
gke_creds = json.loads(setup.get("GKE_SERVICE_ACCOUNT_JSON", "{}"))
```

### MCP Integration

MCP (Model Context Protocol) servers provide external tools to bots without any bot-side code changes. MCP tools are **group-scoped** — they're discovered via the group hierarchy and merged automatically into the model's tool list alongside the bot's own tools.

**How it works**:
1. User creates an MCP server via UI or `flexus_mcp_setup` tool (presets available for PostgreSQL, Notion, GitHub, Stripe, etc.)
2. Backend runs the MCP server (remote URL or `npx`/`uvx` command), discovers its tools
3. Tools appear as `mcp_{name}_{short_id}` CloudTools, available to all bots in that group
4. Bot calls them like any other tool — no special wiring needed

**Presets** (`flexus_backend/integrations/mcp_presets/presets/*.json`): pre-configured MCP servers with env vars, install scripts, and OAuth links. Users pick a preset → fill in secrets → server starts.

**Bot developer impact**: None. MCP tools just appear in the model's context. If your bot should suggest MCP setup to users, mention it in the prompt.

### Available Integrations

Read the source file before using any integration — each has quirks.

| Module | Type | Auth | Used By | Notes |
|--------|------|------|---------|-------|
| `fi_slack.py` | Messenger | Bot Token + App Token (Socket Mode) | adspy, diplodocus | Full thread capture, `SLACK_SETUP_SCHEMA` exportable |
| `fi_discord2.py` | Messenger | Bot Token | — | Thread creation is unusual, read carefully |
| `fi_telegram.py` | Messenger | Bot Token | — | Captures entire chats (no thread concept) |
| `fi_gmail.py` | Tool-only | OAuth2 (Google) | — | Send/search/get; NeedsConfirmation for deletes; no incoming→kanban |
| `fi_github.py` | Tool-only | `gh` CLI + token | — | Read/write commands; NeedsConfirmation for mutations |
| `fi_erp.py` | Tool-only | FlexusClient | boss, frog | ERP table CRUD (meta/data/crud/csv_import — 4 tools) |
| `fi_google_analytics.py` | Tool-only | OAuth2 (Google) | — | GA4/UA reports, properties, user activity |
| `facebook/fi_facebook.py` | Tool-only | OAuth2 (Facebook) | — | Ads API: accounts, campaigns, ads |
| `fi_crm_automations.py` | Tool-only | FlexusClient | — | CRM automation rules engine, triggers on ERP changes |

### Testing Integrations

**Every new integration must be tested against real APIs.** No mocks — real keys, real calls, real validation.

**API keys**: Should be available as environment variables in the dev environment. If a key is missing, report exactly which env var is needed and what service it's for — it will be provided for the next session.

**Testing approach**:

1. **Import check** — verify the code compiles:
```bash
python -c "from mybot.tools import my_service; print('OK')"
```

2. **Status check** — verify authentication and connection:
```python
# In a test script or via bot chat:
result = await integration.called_by_model(mock_toolcall, {"op": "status"})
assert "ERROR" not in result
```

3. **Read operations** — verify the API works:
```python
result = await integration.called_by_model(mock_toolcall, {"op": "list"})
# Should return actual data, not errors
```

4. **Write operations** — verify with small safe operations (if applicable):
```python
# Create something small, verify it exists, clean up
result = await integration.called_by_model(mock_toolcall, {"op": "create", "args": {...}})
```

5. **Error handling** — verify graceful failure:
```python
# Bad input should return error string, not crash
result = await integration.called_by_model(mock_toolcall, {"op": "get", "args": {"id": "nonexistent"}})
assert isinstance(result, str)  # Not an exception
```

For messenger integrations, also test: `start_reactive()` connects without error, incoming messages arrive in Flexus threads, outgoing messages post to the external service.

**Never ship a mocked integration.** If you can't test with real keys, say so in the final report and list what's needed.

## Client Kit Modules Reference

### Core Modules (`flexus_client_kit/`)

| Module | Purpose |
|--------|---------|
| `ckit_client.py` | FlexusClient — HTTP/WS GraphQL transport, auth, workspace queries |
| `ckit_bot_exec.py` | RobotContext, event unparking, subscriptions, `run_bots_in_this_group()` |
| `ckit_bot_install.py` | Marketplace upsert, dev bot publishing, persona setup, CLI helpers |
| `ckit_bot_query.py` | GraphQL queries for personas, threads, messages, schedules, tasks |
| `ckit_ask_model.py` | Ask AI models, create threads/subchats, add messages, bot activation |
| `ckit_cloudtool.py` | CloudTool definitions, FCloudtoolCall, tool results, NeedsConfirmation, WaitForSubchats |
| `ckit_kanban.py` | Kanban task CRUD: post to inbox, arrange tasks, list tasks |
| `ckit_schedule.py` | Schedule parsing (`EVERY:1m`, `WEEKDAYS:MO:FR/10:30`), next run calculation |
| `ckit_shutdown.py` | Graceful shutdown: `shutdown_event`, `wait()`, signal handlers |
| `ckit_mongo.py` | MongoDB file storage: store/retrieve/ls/mv/rm with TTL |
| `ckit_edoc.py` | External documents/data sources: CRUD, subscriptions, `read_pdoc`/`save_pdoc` |
| `ckit_erp.py` | ERP table CRUD: query/create/patch/delete/batch_upsert with filters |
| `ckit_devenv.py` | Dev environments: list/create/patch/delete, API key generation, GitHub auth |
| `ckit_utils.py` | Shared utilities |

### Integration Modules (`flexus_client_kit/integrations/`)

| Module | Purpose | Read before using |
|--------|---------|-------------------|
| `fi_slack.py` | Slack: Socket Mode, channel watching, thread capture, message sync | Yes — full-featured, complex |
| `fi_discord2.py` | Discord: channel/thread/DM watching, capture/post, file handling | Yes — thread creation is unusual |
| `fi_telegram.py` | Telegram: bot token, chat capture (no threads), message sync | Yes — captures entire chats |
| `fi_gmail.py` | Gmail: OAuth2, send/search/get/delete, label management | Yes — guardrails against spam |
| `fi_question.py` | `ask_questions` tool — interactive UI questionnaires | Short, easy to use |
| `fi_widget.py` | `print_widget` tool — upload/restart/setup UI widgets | Short, easy to use |
| `fi_pdoc.py` | Policy documents — IntegrationPdoc, list/cat/create/overwrite/rm | Yes — main doc storage |
| `fi_mongo_store.py` | MongoDB file tool — list/cat/grep/save/upload/delete for models | Short wrapper |
| `fi_erp.py` | ERP tools — table meta/data/CRUD, CSV import | Yes — schema-driven |
| `fi_crm_automations.py` | CRM automation rules — triggers on ERP changes, actions | Complex, read first |
| `fi_github.py` | GitHub CLI via `gh` — read/write commands with confirmation | Short |
| `fi_google_analytics.py` | GA4/UA reports, properties, user activity via OAuth | Specialized |
| `report/fi_report.py` | Multi-section report builder with Jinja templates and subchats | Complex, read first |
| `facebook/` | Facebook Ads API — accounts, ads, campaigns | Subpackage |

### Simple Bots (`flexus_simple_bots/`) — Reference Implementations

| Bot | Purpose | Complexity |
|-----|---------|------------|
| `frog/` | Educational example — showcases all bot patterns | Simple, start here |
| `owl/` | Multi-section strategy document builder | Medium |
| `boss/` | Workspace management, colleague bot setup | Medium |
| `karen/` | Customer support — Slack/Discord monitoring → kanban | Medium |
| `productman/` | Product management — surveys, hypothesis validation | Complex |
| `botticelli/` | Quick simple responses | Simple |
| `admonster/` | Ad monitoring | Medium |
| `slonik/` | Database operations | Medium |
| `vix/` | Visual content | Medium |

## Bot Installation

Bot installation has two steps: **make code importable** (pip install) + **register in marketplace** (install script).

### For New Bot Repos (separate repository)

When creating a bot in a new repository, you **must create setup.py** in the repo root:

```python
from setuptools import setup, find_packages
setup(
    name="mybot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["flexus-client-kit"],
    package_data={"": ["*.webp", "*.png", "*.html", "*.lark", "*.json"]},
)
```

Without `setup.py`, the install will fail because Python can't find the bot module.

### For Bots Inside flexus-client-kit

Already handled - flexus-client-kit has its own setup.py that includes all bots.

### Running Installation

After you finish coding and commit your changes, tell BOB to install the bot. BOB will:
1. Bump the version
2. Install the package
3. Register in marketplace
4. Let the user test interactively

## Testing Bots

Testing follows a strict progression: install → run → unit/integration tests → scenario. Each step must pass before moving to the next.

### Step 1: Install the Bot

Install the package and register in the marketplace:

```bash
pip install -e /workspace
python -m mybot.mybot_install --ws=$FLEXUS_WORKSPACE
```

If using Bob's `test_bot` tool, `op="run"` does this automatically (version bump → pip install → marketplace install → persona creation → start).

### Step 2: Run and Check Logs

The bot is a never-ending process. Run it for a limited time and check for startup errors:

```bash
# Start in background, capture logs
nohup python -u -m mybot.mybot_bot > /tmp/bot.log 2>&1 &
BOT_PID=$!

# Wait for startup (10-30 seconds is enough for import/init errors)
sleep 15

# Check if still alive
if kill -0 $BOT_PID 2>/dev/null; then
    echo "✅ Bot is running"
    tail -50 /tmp/bot.log
else
    echo "❌ Bot crashed"
    cat /tmp/bot.log
fi

# Stop
kill $BOT_PID 2>/dev/null
```

**What to look for in logs**:
- Import errors → fix missing dependencies
- Auth/connection errors → check API keys and env vars
- Schema validation errors → fix setup schema or install file
- Clean startup with "subscribed" / "waiting" messages → good

If using Bob's `test_bot` tool: `op="run"` starts the bot, `op="logs"` shows output, `op="stop"` kills it.

### Step 3: Write and Run Tests

Write tests for all testable logic, **especially external integrations**. Test against real APIs — no mocks.

```python
# tests/test_mybot.py
import pytest

def test_imports():
    from mybot import mybot_bot, mybot_prompts, mybot_install

def test_prompts_structure():
    from mybot import mybot_prompts
    assert hasattr(mybot_prompts, "main_prompt")
    assert len(mybot_prompts.main_prompt) > 100
```

**For external integrations** — test with real API keys from environment:

```python
import os
import pytest

@pytest.mark.asyncio
async def test_my_service_status():
    api_key = os.environ.get("MY_SERVICE_API_KEY")
    if not api_key:
        pytest.skip("MY_SERVICE_API_KEY not set")
    integration = IntegrationMyService(fclient=None, rcx=None, api_key=api_key)
    result = await integration.called_by_model(mock_toolcall, {"op": "status"})
    assert "ERROR" not in result

@pytest.mark.asyncio
async def test_my_service_read():
    api_key = os.environ.get("MY_SERVICE_API_KEY")
    if not api_key:
        pytest.skip("MY_SERVICE_API_KEY not set")
    integration = IntegrationMyService(fclient=None, rcx=None, api_key=api_key)
    result = await integration.called_by_model(mock_toolcall, {"op": "list"})
    assert isinstance(result, str)
    assert "ERROR" not in result
```

Run: `pytest tests/ -v`

**API keys**: Should be available as environment variables in the dev container. If a key is missing, report exactly which env var is needed and what service it's for — it will be provided for the next session.

**Never ship a mocked integration.** All integrations must work against real services.

### Step 4: Create and Run a Scenario

After the bot works, create a scenario to test the full conversation flow and catch regressions.

#### Writing a Scenario

Record a "happy path" — the ideal conversation (user messages, assistant tool calls, tool results):

```yaml
# mybot/mybot__s1.yaml
messages:
- role: user
  content: Find competitors for Acme Corp
- role: assistant
  tool_calls:
  - function:
      name: my_tool
      arguments: '{"op": "search", "query": "Acme Corp competitors"}'
    id: call_001
    type: function
- role: tool
  call_id: call_001
  content: |-
    Found 3 competitors: Beta Inc, Gamma LLC, Delta Co
- role: assistant
  content: I found 3 competitors for Acme Corp...
persona_marketable_name: mybot
judge_instructions: |-
  Reward: finding real competitors, using the search tool correctly.
  Penalize: hallucinating companies, skipping tool calls.
  Ignore: exact wording differences.
```

**Naming**: `botname__scenarioname.yaml` (double underscore). The part before `__` is the expert name.

**Fields**:
- `messages` (required) — alternating user/assistant/tool messages in OpenAI chat format
- `judge_instructions` (optional) — tell the judge LLM what to reward, penalize, and ignore
- `persona_marketable_name` (optional) — matches bot name

**Tips for writing**:
- First assistant message's `tool_calls` auto-kickstart the conversation
- Use multiline `|-` for long content
- Include realistic tool results — the simulation LLM will try to match them
- Don't include system prompts (scenarios test behavior, not prompt wording)
- Cover the main use case, not edge cases

#### Running a Scenario

```bash
python -m mybot.mybot_bot --scenario mybot/mybot__s1.yaml
```

**Output** (in `scenario-dumps/`, gitignored):
- `mybot__s1-v{version}-{model}-happy.yaml` — the input happy path
- `mybot__s1-v{version}-{model}-actual.yaml` — recorded bot run
- `mybot__s1-v{version}-{model}-score.yaml` — judge results

#### How Scenarios Work (Behind the Scenes)

1. **Setup**: Creates a temporary group and persona, loads happy YAML
2. **Execution loop** (max 30 steps, 600s timeout per step):
   - Backend simulates next human message using LLM (`grok-4-1-fast-non-reasoning`), matching the happy path
   - Bot receives message, runs tools, responds
   - Tool results are simulated by an LLM that reads the happy path + tool source code
   - If the LLM can't match the happy path, it marks the step as **shaky**
3. **Judging**: A reasoning LLM (`grok-4-1-fast-reasoning`) compares actual vs happy trajectory

#### Scoring

The score YAML contains:

```yaml
happy_rating: 8        # Quality of the reference itself (1-10)
happy_feedback: "..."   # Assessment of the happy path
actual_rating: 7        # How well the bot performed (0-10)
actual_feedback: "..."  # Assessment of the actual run
criticism:              # Per-turn detailed feedback
  turn00:
    human_criticism: "..."
    human_problem_severity: 0   # 0=match, 1=extra, 2=fabrication
    assistant_criticism: "..."
    assistant_problem_severity: 0  # 0=perfect, 1=minor, 2=major
shaky_human: 1          # Times human simulation improvised
shaky_tool: 0           # Times tool simulation improvised
stop_reason: "scenario_done"
cost:
  judge: 500            # Micro-dollars
  human: 200
  tools: 100
  assistant: 800
```

**What "shaky" means**: The simulation LLM had to invent content not supported by the happy path. `shaky_human` = human messages fabricated. `shaky_tool` = tool results fabricated. High shaky counts mean either the scenario needs more coverage or the bot deviated too far.

**Rating < 8 needs improvement.** Use the `actual_feedback` and per-turn `criticism` to identify what went wrong. Generalize prompt improvements — don't fix specific scenario cases.

#### Scenario Tips

- Expensive to run — only test the bot you just changed, not all bots
- After changing prompts/experts/schedules: reinstall the bot first, then run the scenario
- Reference examples: `flexus_simple_bots/frog/frog__s1.yaml` (simple), `flexus_simple_bots/admonster/admonster_s1.yaml` (complex)

### External API Keys

If your bot needs API keys for external services (Slack, Discord, etc.), tell BOB in the final report what's needed:
- Which environment variable (e.g., `SLACK_BOT_TOKEN`)
- What service it's for
- BOB will ask the user and configure the dev environment
- Never make dummy/mocked integrations. Make a real one and if you lack keys — ask for them in the final report

### After You Finish

You must update the README to keep the specification updated!
Commit your changes. BOB will install the bot and let the user test it interactively via the UI.

## Key Rules

- Every tool in `TOOLS` needs `@rcx.on_tool_call(TOOL.name)` handler
- Subchat kernel **must** set `subchat_result` to complete
- Changes to prompts/experts/schedules require reinstall
- Use prefixes in naming: `fgroup_name` not `name`
- Use logs actively to debug stuff, cover with logs especially tricky parts
- We do not use mocked external integration! All integration must be real

## Coding Style

No stupid comments. No docstrings. Simple code. Trailing commas. Follow surrounding file style for imports.
