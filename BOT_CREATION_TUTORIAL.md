# Flexus Bot Creation Tutorial

A comprehensive guide to creating bots for Flexus, the AI agent orchestration platform.

## Table of Contents

1. [Core Concepts & Terminology](#core-concepts--terminology)
2. [Bot Architecture Overview](#bot-architecture-overview)
3. [Structure](#The-File-Structure)
4. [Step-by-Step: Creating Your First Bot](#step-by-step-creating-your-first-bot)
5. [Tools: Cloudtools vs Inprocess Tools](#tools-cloudtools-vs-inprocess-tools)
6. [Experts & Skills](#experts--skills)
7. [Lark Kernels](#lark-kernels)
8. [Kanban Board & Task Management](#kanban-board--task-management)
9. [Scheduling & Activation](#scheduling--activation)
10. [Subchats vs A2A Communication](#subchats-vs-a2a-communication)
11. [Policy Documents & Custom Forms](#policy-documents--custom-forms)
12. [Messenger Integrations](#messenger-integrations)
13. [Testing with Scenarios](#testing-with-scenarios)
14. [Deployment & Running](#deployment--running)
15. [Complete Example: Frog Bot](#complete-example-frog-bot)

---

## Core Concepts & Terminology

### The Terminology Map

| Term | Definition | Database Table |
|------|------------|----------------|
| **Persona** | A deployed instance of a bot with user configuration | `flexus_persona` |
| **Bot** | Informal alias for Persona - a running AI agent | (same as Persona) |
| **Expert** | A behavior mode with specific system prompt + tool restrictions | `flexus_expert` |
| **Skill** | String alias for an Expert (e.g., "default", "huntmode", "survey") | N/A (string key) |
| **Marketplace Bot** | The template/definition that gets installed as a Persona | `flexus_marketplace` |
| **Thread** | A conversation with the bot | `flexus_thread` |
| **Cloudtool** | A tool that runs as a separate service (e.g., `flexus_bot_kanban`) | `flexus_tool_call` |
| **Inprocess Tool** | A tool defined and handled within the bot's own code | N/A |


### How They Relate

```
Marketplace Template ─────► Persona Instance ─────► Expert Modes ─────► Thread
   (bob_install.py)         (flexus_persona)       (flexus_expert)    (conversation)
         │                        │                      │                  │
    Defines experts         User's config          System prompt      Uses expert's
    + default setup         + customizations       + tool filters     prompt & tools
```

---

## Bot Architecture Overview

### Where Do Bots Run?

Bots run in **Kubernetes pods** in an isolated namespace, managed by the `flexus_pod_operator`:

```
GraphQL Subscription (/v1/jailed-bot)
       │
       ▼
pod_subscriber_bot.py ──► PodTask ──► kube.py ──► Kubernetes Pod
                                                   (isolated namespace)
```

**Two types of bots:**

| Type | Endpoint | Use Case | Auth |
|------|----------|----------|------|
| **Jailed Bot** | `/v1/jailed-bot` | User-deployed marketplace bots | API Key |
| **Superuser Bot** | `/v1/superuser-core` | Internal/admin services | HMAC ticket |

### Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Flexus Backend                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Database │──│  Redis   │──│  GraphQL WS  │──│ Tool Services  │  │
│  │ (Prisma) │  │ (pubsub) │  │ Subscriptions│  │ (cloudtools)   │  │
│  └──────────┘  └──────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                    WebSocket Subscriptions
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Bot Process (K8s Pod)                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    RobotContext (rcx)                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │ │
│  │  │ @on_message │  │  @on_task   │  │ @on_tool_call("ribbit") │ │ │
│  │  │   handler   │  │   handler   │  │      handler            │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     Main Loop                                  │ │
│  │  while not shutdown:                                           │ │
│  │      await rcx.unpark_collected_events(sleep_if_no_work=10)    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The File Structure

Every bot consists of three core files plus required images:

```
mybot/
├── mybot_bot.py       # Runtime logic: main loop, tool handlers
├── mybot_prompts.py   # System prompts for each expert/skill
├── mybot_install.py   # Marketplace registration, experts, schedule
├── mybot-1024x1536.webp  # Detailed marketplace picture (<0.3MB) [REQUIRED]
├── mybot-256x256.webp    # Small avatar (transparent or white bg) [REQUIRED]
└── forms/                # Optional: custom HTML forms for pdocs
    └── my_report.html
└── tools/                # Optional: custom tools
    └── my_tool.py
```

> ⚠️ **Image files are required!** The install script reads and base64-encodes these images.
> If they don't exist, install will crash with `FileNotFoundError`.

### File Responsibilities

| File | Contains | When Changed |
|------|----------|--------------|
| `mybot_prompts.py` | System prompts, prompt fragments | **Requires reinstall** |
| `mybot_install.py` | Experts, setup schema, schedule, metadata | **Requires reinstall** |
| `mybot_bot.py` | Tool handlers, main loop, integrations | **Auto-restarts pod** |

---

## Step-by-Step: Creating Your First Bot

### Step 1: Create the Prompts File

```python
# mybot_prompts.py
from flexus_simple_bots import prompts_common

MYBOT_PROMPT = f"""
You are MyBot, a helpful assistant that does X, Y, Z.

## Your Capabilities
- Capability 1
- Capability 2

{prompts_common.PROMPT_KANBAN}
{prompts_common.PROMPT_POLICY_DOCUMENTS}
{prompts_common.PROMPT_HERE_GOES_SETUP}
"""
```

### Step 2: Create the Install File

```python
# mybot_install.py
import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.mybot import mybot_prompts

BOT_DESCRIPTION = """
## MyBot - What It Does

Describe your bot for the marketplace here.
"""

mybot_setup_schema = [
    {
        "bs_name": "api_key",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Integration",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "API key for external service",
    },
    {
        "bs_name": "max_items",
        "bs_type": "int",
        "bs_default": 10,
        "bs_group": "Behavior",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Maximum items to process",
    },
]

MYBOT_DEFAULT_LARK = """
print("Processing %d messages" % len(messages))
# Lark kernel logic here
"""

async def install(client, ws_id, bot_name, bot_version, tools):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name("mybot-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("mybot-256x256.webp"), "rb").read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#4A90D9",
        marketable_title1="MyBot",
        marketable_title2="A brief tagline for your bot",
        marketable_author="Your Name",
        marketable_occupation="Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Productivity",
        marketable_github_repo="https://github.com/yourorg/yourrepo.git",
        marketable_run_this="python -m flexus_simple_bots.mybot.mybot_bot",
        marketable_setup_default=mybot_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Hello, what can you do?", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm MyBot. How can I help you today?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=mybot_prompts.MYBOT_PROMPT,
                fexp_python_kernel=MYBOT_DEFAULT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["Productivity", "Assistant"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )

if __name__ == "__main__":
    from flexus_simple_bots.mybot import mybot_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("mybot_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=mybot_bot.BOT_NAME, bot_version=mybot_bot.BOT_VERSION, tools=mybot_bot.TOOLS))
```

### Step 3: Create the Bot File

```python
# mybot_bot.py
import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_client, ckit_cloudtool, ckit_bot_exec, ckit_shutdown, ckit_ask_model, ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.mybot import mybot_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_mybot")

BOT_NAME = "mybot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

# Define your custom tools
MY_TOOL = ckit_cloudtool.CloudTool(
    name="my_action",
    description="Performs my custom action",
    parameters={
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "The input to process"},
        },
        "required": ["input"],
    },
)

TOOLS = [
    MY_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]

async def mybot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    # Mix defaults with user's custom setup
    setup = ckit_bot_exec.official_setup_mixing_procedure(mybot_install.mybot_setup_schema, rcx.persona.persona_setup)

    # Initialize integrations
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    # Handler: when a message is updated in the database
    @rcx.on_updated_message
    async def updated_message(msg: ckit_ask_model.FThreadMessageOutput):
        logger.info(f"Message updated: {msg.ftm_belongs_to_ft_id} alt={msg.ftm_alt} num={msg.ftm_num}")

    # Handler: when a thread is updated
    @rcx.on_updated_thread
    async def updated_thread(th: ckit_ask_model.FThreadOutput):
        logger.info(f"Thread updated: {th.ft_id}")

    # Handler: when a kanban task is updated
    @rcx.on_updated_task
    async def updated_task(t: ckit_kanban.FPersonaKanbanTaskOutput):
        logger.info(f"Task updated: {t.ktask_id} - {t.ktask_title}")

    # Handler: your custom tool
    @rcx.on_tool_call(MY_TOOL.name)
    async def toolcall_my_action(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        input_val = model_produced_args.get("input", "")
        # Your logic here
        result = f"Processed: {input_val}"
        logger.info(f"my_action called with: {input_val}")
        return result

    # Handler: policy documents
    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    # Main loop
    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info(f"{rcx.persona.persona_id} exit")

def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=mybot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=mybot_install.install,
    ))

if __name__ == "__main__":
    main()
```

### Step 4: Install and Run

```bash
# Set environment variables for API connectivity (required before install/run)
export FLEXUS_API_BASEURL=...
export FLEXUS_API_KEY=...
export FLEXUS_WORKSPACE=...

# Or for a specific group only:
# export FLEXUS_GROUP=...

# Install to marketplace (required once, and after prompt/expert changes)
python -m flexus_simple_bots.mybot.mybot_install --ws=solarsystem

# Run the bot locally (for development)
# Note: NO --group flag! Bot reads FLEXUS_WORKSPACE or FLEXUS_GROUP from env
python -m flexus_simple_bots.mybot.mybot_bot
```

> ⚠️ **Gotcha**: If you set only `FLEXUS_GROUP` (not `FLEXUS_WORKSPACE`), the bot will NOT auto-install.
> Always run the install step with `--ws=` first, then you can run the bot with just `FLEXUS_GROUP`.

> 💡 **Tip**: These env vars can be set inside a claude_code pod to install bots programmatically.

---

## Tools: Cloudtools vs Inprocess Tools

### What's the Difference?

| Aspect | Cloudtools | Inprocess Tools |
|--------|-----------|-----------------|
| **Where they run** | Separate services (`service_cloudtool_*.py`) | Inside bot's own process |
| **Registration** | `run_cloudtool_service()` → GraphQL subscription | Defined in `TOOLS` list, handled by `@rcx.on_tool_call` |
| **Use case** | Shared tools, heavy deps, scalable | Bot-specific logic, low latency |
| **Examples** | `flexus_bot_kanban`, `web`, `vecsearch` | `ribbit`, `catch_insects`, custom actions |

### Built-in Cloudtools (Backend Services)

These are handled by Flexus backend cloud services (no bot wiring needed):

- `flexus_bot_kanban` - Kanban board operations
- `web` - Web browsing
- `vecsearch` - Vector search in knowledge base
- `flexus_hand_over_task` - A2A task delegation

### Inprocess Integration Tools (Require Wiring)

These look like cloudtools but require explicit setup in your bot:

- `flexus_policy_document` - Policy document CRUD
- `slack` - Slack integration
- `discord` - Discord integration

**Example: Wiring policy documents:**
```python
from flexus_client_kit.integrations import fi_pdoc

# Add to TOOLS list
TOOLS = [
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    # ... your other tools
]

# In main loop, create integration and handler
pdoc = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

@rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
async def toolcall_pdoc(toolcall, args):
    return await pdoc.called_by_model(toolcall, args)
```

> ⚠️ **Gotcha**: If you mention policy docs in your prompt but don't wire the tool,
> the model will try to call it and get "unknown tool" errors.

### Creating Inprocess Tools

```python
MY_TOOL = ckit_cloudtool.CloudTool(
    name="unique_tool_name",  # Must be unique across all tools bot uses
    description="What this tool does (shown to LLM)",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"},
            "param2": {"type": "integer", "enum": [1, 2, 3], "description": "Choices"},
        },
        "required": ["param1"],
    },
)

# Register in TOOLS list
TOOLS = [MY_TOOL, ...]

# Handle in main loop
@rcx.on_tool_call(MY_TOOL.name)
async def handle_my_tool(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
    # Return string result (shown to LLM)
    return "Tool result here"
```

> ⚠️ **Critical Gotcha**: Every `CloudTool` in your `TOOLS` list **must** have exactly one matching
> `@rcx.on_tool_call(tool.name)` handler. If the sets don't match, the bot **silently shuts down**.
> This is the #1 cause of "my bot immediately dies" issues.

---

## Experts & Skills

### What Are Experts?

Experts are **behavior modes** for your bot. Each expert defines:
- A system prompt
- Tool restrictions (block/allow lists)
- A Lark kernel for control flow
- Inactivity timeout

### Defining Multiple Experts

```python
marketable_experts=[
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mybot_prompts.DEFAULT_PROMPT,
        fexp_python_kernel=DEFAULT_LARK,
        fexp_block_tools="*setup*",           # Block setup-related tools
        fexp_allow_tools="",                  # Empty = allow all (except blocked)
        fexp_app_capture_tools=bot_internal_tools,
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mybot_prompts.SETUP_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="*setup*,flexus_policy_document",  # Only allow specific tools
        fexp_app_capture_tools=bot_internal_tools,
    )),
    ("analyst", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mybot_prompts.ANALYST_PROMPT,
        fexp_python_kernel=ANALYST_LARK,
        fexp_block_tools="*dangerous*",
        fexp_allow_tools="",
        fexp_app_capture_tools=bot_internal_tools,
        fexp_inactivity_timeout=300,  # Auto-close after 5 min idle
    )),
]
```

### Activating a Skill

Skills are activated via:
1. **Subchats**: `skill="huntmode"` parameter
2. **Schedule**: Different schedules can use different skills
3. **Bot activation**: `bot_activate(persona_id, skill="analyst")`

---

## Lark Kernels

### What Are Lark Kernels?

Lark kernels are **Starlark scripts** (Python-like) that run **before and after each LLM generation**. They provide deterministic control over the conversation without using LLM tokens.

### When Kernels Run

```
User Message
     │
     ▼
┌─────────────┐
│ Lark Kernel │ ◄── Can set error, post instructions
│  (before)   │
└─────────────┘
     │
     ▼
┌─────────────┐
│  LLM Call   │
└─────────────┘
     │
     ▼
┌─────────────┐
│ Lark Kernel │ ◄── Can kill tools, return subchat result
│  (after)    │
└─────────────┘
     │
     ▼
Response/Tool Calls
```

### Kernel Inputs & Outputs

**Inputs (read-only):**
- `messages` - List of all messages in conversation
- `coins` - Tokens spent so far
- `budget` - Token budget limit

**Outputs (set these to control flow):**
- `error` - Set error message, stops processing
- `kill_tools` - Boolean, cancels pending tool calls
- `post_cd_instruction` - Inject instruction to LLM
- `subchat_result` - Return value for subchats (ends subchat)

### Kernel Examples

```python
# Basic logging kernel
BASIC_LARK = """
print("Messages: %d, Coins: %d/%d" % (len(messages), coins, budget))
"""

# Subchat that always returns a value
SUBCHAT_LARK = """
subchat_result = "Task completed!"
"""

# Control flow kernel
CONTROL_LARK = """
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"]).lower()
    if "forbidden_word" in content:
        error = "You said something you shouldn't have!"
    elif len(msg.get("tool_calls", [])) > 3:
        kill_tools = True
        post_cd_instruction = "Too many tools! Try a simpler approach."
"""

# Budget enforcement
BUDGET_LARK = """
if coins > budget * 0.8:
    post_cd_instruction = "You're running low on budget. Wrap up quickly."
if coins > budget:
    error = "Budget exceeded"
"""
```

---

## Kanban Board & Task Management

### Task Lifecycle

```
INBOX ──────► TODO ──────► INPROGRESS ──────► DONE
  │            │              │                │
  │            │              │                │
SCHED_TASK_SORT    SCHED_TODO    Bot working    Bot calls
(bot sorts)       (auto-assign)                ktask_resolve()
```

### How Tasks Flow

1. **External input** (messenger, email, A2A) creates task in **INBOX**
2. **SCHED_TASK_SORT** triggers bot to prioritize and move tasks to **TODO**
3. **SCHED_TODO** auto-assigns one task to **INPROGRESS** and activates bot
4. Bot works on task, calls `flexus_bot_kanban(op="resolve")` to move to **DONE**

### Using Kanban in Your Bot

Include in your prompt:
```python
from flexus_simple_bots import prompts_common

MY_PROMPT = f"""
...your prompt...
{prompts_common.PROMPT_KANBAN}
"""
```

The LLM will use `flexus_bot_kanban()` cloudtool automatically.

### Handling Task Updates

```python
@rcx.on_updated_task
async def updated_task(t: ckit_kanban.FPersonaKanbanTaskOutput):
    if t.ktask_inprogress_ft_id:
        logger.info(f"Working on: {t.ktask_title}")
    if t.ktask_done_ts:
        logger.info(f"Completed: {t.ktask_title}")
```

---

## Scheduling & Activation

### Schedule Types

| Type | Trigger Condition | Use Case |
|------|-------------------|----------|
| `SCHED_TASK_SORT` | `tasks_inbox > 0` | Sort and prioritize inbox |
| `SCHED_TODO` | `tasks_todo > 0` | Work on next task |
| `SCHED_ANY` | Time-based only | Regular check-ins, reports |
| `SCHED_CREATE_TASK` | Time-based only | Create recurring tasks |

### Schedule Configuration

```python
marketable_schedule=[
    # Sort inbox every 5 minutes
    {
        "sched_type": "SCHED_TASK_SORT",
        "sched_when": "EVERY:5m",
        "sched_first_question": "Sort inbox tasks by priority.",
    },
    # Process todo every 2 minutes
    {
        "sched_type": "SCHED_TODO",
        "sched_when": "EVERY:2m",
        "sched_first_question": "Work on the assigned task.",
    },
    # Daily report at 9am
    {
        "sched_type": "SCHED_ANY",
        "sched_when": "CRON:0 9 * * *",
        "sched_first_question": "Generate daily summary report.",
    },
]
```

### Activation Triggers

Bots can be activated by:

1. **User message** - User sends message in UI → `bot_activate()` → new thread
2. **Schedule** - `service_scheduler.py` checks schedules every ~1 minute
3. **OOB wakeup** - Kanban changes trigger immediate schedule check
4. **Subchat** - Parent thread spawns child threads

---

## Subchats vs A2A Communication

### Decision Matrix

| Need | Use Subchats | Use A2A |
|------|--------------|---------|
| Same bot, parallel work | ✅ | ❌ |
| Different bot | ❌ | ✅ |
| Parent must wait for result | ✅ | ❌ |
| Long background task | ❌ | ✅ |
| Need boss approval | ❌ | ✅ |
| Multiple parallel validations | ✅ | ❌ |

### Using Subchats

```python
@rcx.on_tool_call("my_parallel_tool")
async def handle_parallel(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
    N = args.get("count", 3)

    subchats = await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient,
        who_is_asking="my_parallel_tool",
        persona_id=rcx.persona.persona_id,
        first_question=[f"Process item #{i+1}" for i in range(N)],
        first_calls=["null" for _ in range(N)],
        title=[f"Processing #{i+1}" for i in range(N)],
        fcall_id=toolcall.fcall_id,
        skill="worker_mode",  # Uses different expert
    )

    # This exception tells Flexus to wait for subchats to complete
    raise ckit_cloudtool.WaitForSubchats(subchats)
```

### Using A2A (Task Handover)

In your prompt, instruct the LLM:
```
To delegate work to another bot, use:
flexus_hand_over_task(to_bot="other_bot_name", description="What needs to be done", skill="default")

The task will appear in that bot's inbox. You'll receive a 💿-message when it's completed.
```

---

## Policy Documents & Custom Forms

### What Are Policy Documents?

Policy documents (pdocs) are **structured JSON documents** stored hierarchically by path. They're used for:
- Bot configuration
- Persistent state
- User-editable content
- Reports and summaries

### Using Policy Documents

Include `prompts_common.PROMPT_POLICY_DOCUMENTS` in your system prompt. The LLM will use `flexus_policy_document()` with operations:
- `help` - Show usage help (default when no args)
- `list` - List documents in a folder
- `cat` / `read` / `activate` - Read a document (`activate` creates UI link with ✍️)
- `create` - Create new document (error if exists)
- `overwrite` - Create or replace document
- `update_json_text` - Update specific field via dot notation (e.g., `"section1.field"`)
- `cp` - Copy document (`p1` → `p2`)
- `rm` - Archive (soft delete) document

### Custom Forms

Custom HTML forms provide a nice UI for editing policy documents instead of raw JSON.

**Form filename must match the top-level JSON key:**
```
forms/pond_report.html  ←→  {"pond_report": {"meta": {...}, "field1": "..."}}
```

**Form Protocol (postMessage):**

```
Parent → Form:
  INIT: {content, themeCss, marketplace}
  CONTENT_UPDATE: {content}
  FOCUS: {focused}

Form → Parent:
  FORM_READY: {formName}
  FORM_CONTENT_CHANGED: {content}
```

**Form Template:**
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Use CSS variables for theme support */
    body { background: var(--p-content-hover-background); }
    .paper { background: var(--p-primary-contrast-color); color: var(--p-primary-color); }
    input { background: var(--p-content-hover-background); color: var(--p-text-color); }
  </style>
  <style id="theme-css"></style>
</head>
<body>
  <div class="paper">
    <input type="text" id="field1" oninput="notifyChange()">
  </div>
  <script>
    const FormBridge = {
      handlers: {},
      init(name) {
        window.addEventListener('message', e => {
          if (e.data?.type && this.handlers[e.data.type]) {
            this.handlers[e.data.type].forEach(h => h(e.data));
          }
        });
        setTimeout(() => this.send('FORM_READY', { formName: name }), 0);
      },
      send(type, data) { window.parent.postMessage({ type, ...data }, '*'); },
      on(type, handler) {
        if (!this.handlers[type]) this.handlers[type] = [];
        this.handlers[type].push(handler);
      }
    };

    let content = {};

    FormBridge.on('INIT', data => {
      content = data.content || {};
      if (data.themeCss) document.getElementById('theme-css').textContent = data.themeCss;
      render();
    });

    FormBridge.on('CONTENT_UPDATE', data => { content = data.content || {}; render(); });
    FormBridge.init('my-form');

    function render() {
      document.getElementById('field1').value = (content.my_doc || {}).field1 || '';
    }

    function getContent() {
      return { my_doc: { ...content.my_doc, field1: document.getElementById('field1').value } };
    }

    function notifyChange() {
      FormBridge.send('FORM_CONTENT_CHANGED', { content: getContent() });
    }
  </script>
</body>
</html>
```

---

## Messenger Integrations

### Available Integrations

| Messenger | File | Thread Capture | Full-Featured |
|-----------|------|----------------|---------------|
| Slack | `fi_slack.py` | ✅ channel/thread | ✅ |
| Discord | `fi_discord2.py` | ✅ channel/thread | Mostly |
| Telegram | `fi_telegram.py` | ✅ entire chat | Partial |
| Gmail | `fi_gmail.py` | ❌ | Pull-only |

### Message Flow

```
External Message
      │
      ▼
┌─────────────────────────────┐
│  Is thread captured?        │
│  (ft_app_searchable set)    │
└─────────────────────────────┘
      │
      ├── YES ──► Post to captured Flexus thread
      │
      └── NO ───► Create Kanban inbox task
```

### Using Slack Integration

```python
from flexus_client_kit.integrations import fi_slack

# Add Slack tool to TOOLS list
TOOLS = [
    fi_slack.SLACK_TOOL,
    # ... your other tools
]

# In your main loop
slack = fi_slack.IntegrationSlack(
    fclient=fclient,
    rcx=rcx,
    SLACK_BOT_TOKEN=setup.get("SLACK_BOT_TOKEN", ""),
    SLACK_APP_TOKEN=setup.get("SLACK_APP_TOKEN", ""),
    should_join=setup.get("slack_should_join", "#general"),
    mongo_collection=None,  # Optional: for file uploads
)

# Join channels and start listening
await slack.join_channels()
await slack.start_reactive()

# Wire the tool handler
@rcx.on_tool_call(fi_slack.SLACK_TOOL.name)
async def toolcall_slack(toolcall, args):
    return await slack.called_by_model(toolcall, args)

# Handle outgoing messages (auto-post to captured threads)
@rcx.on_updated_message
async def on_message(msg):
    if msg.ftm_role == "assistant":
        await slack.look_assistant_might_have_posted_something(msg)

# Clean up in finally block
try:
    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)
finally:
    await slack.close()
```

**Required setup schema fields** (add to your `_install.py`):
```python
from flexus_client_kit.integrations.fi_slack import SLACK_SETUP_SCHEMA

mybot_setup_schema = [
    *SLACK_SETUP_SCHEMA,  # Adds SLACK_BOT_TOKEN, SLACK_APP_TOKEN, slack_should_join
    # ... your other setup fields
]
```

---

## Testing with Scenarios

### What Are Scenarios?

Scenarios are YAML files that define expected bot behavior ("happy path"). They're used for:
- Regression testing
- Behavior verification
- Documentation of expected flows

### Scenario File Naming

**Format: `$SKILL$__$SCENARIO$.yaml`** (double underscore)

**Rules for naming:**
- To test the **default expert**: name file `<BOT_NAME>__s1.yaml` (e.g., `mybot__s1.yaml`)
  - The runner detects skill == bot name and converts to `"default"` internally
- To test a **non-default expert**: name file `<skill_name>__s1.yaml` (e.g., `huntmode__s1.yaml`)
  - Runner uses that skill directly

> 🚨 **Critical**: Do NOT name your file `default__s1.yaml` - it will crash with an assertion error!
> The code has `assert skill != "default"`. Use `<botname>__s1.yaml` for default expert instead.

### Scenario File Format

```yaml
# mybot__s1.yaml
messages:
- role: user
  content: Hello, do something
- role: assistant
  tool_calls:
  - function:
      arguments: '{"input":"test"}'
      name: my_action
    id: call_12345
    type: function
- role: tool
  call_id: call_12345
  content: Processed: test
- role: assistant
  content: Done! I processed your request.
persona_marketable_name: mybot
```

### Running Scenarios

```bash
# For default expert, use <botname>__<scenario>.yaml (NOT default__s1.yaml!)
python -m flexus_simple_bots.mybot.mybot_bot \
  --scenario flexus_simple_bots/mybot/mybot__s1.yaml

# For non-default expert (e.g., "huntmode" skill):
python -m flexus_simple_bots.mybot.mybot_bot \
  --scenario flexus_simple_bots/mybot/huntmode__s1.yaml
```

**Output files:**
```
scenario-dumps/mybot__s1-happy.yaml   # Original expected behavior
scenario-dumps/mybot__s1-actual.yaml  # What actually happened
scenario-dumps/mybot__s1-score.yaml   # Judge's evaluation
```

### Interpreting Results

The `-score.yaml` file contains:
- **Score**: How well actual matched expected
- **Shaky**: How much was simulated vs. supported by happy path
- **Feedback**: Specific issues and suggestions

---

## Deployment & Running

### Development Workflow

```bash
# 1. Start Flexus backend (if running locally)
python -m flexus_backend.flexus_v1_server --dev

# 2. Set environment variables (required before install/run)
export FLEXUS_API_BASEURL=http://127.0.0.1:8008
export FLEXUS_API_KEY=sk_alice_123456
export FLEXUS_WORKSPACE=solarsystem

# 3. Install/update bot to marketplace (required after prompt/expert changes)
python -m flexus_simple_bots.mybot.mybot_install --ws=solarsystem

# 4. Run bot locally (reads workspace/group from env vars)
python -m flexus_simple_bots.mybot.mybot_bot

# Optional: Run with scenario test (use <botname>__s1.yaml, NOT default__s1.yaml!)
python -m flexus_simple_bots.mybot.mybot_bot --scenario flexus_simple_bots/mybot/mybot__s1.yaml
```

> 💡 **From claude_code pod**: These same env vars work inside a dev container, allowing BOB
> or other bots to install new bots programmatically.

**Available CLI flags for bot runner:**
- `--scenario PATH` - Run scenario test from YAML file
- `--no-cleanup` - Keep test group after scenario (for debugging)
- `--model NAME` - Override model for scenario
- `--experiment NAME` - Tag experiment name in output files

### Production Deployment

In production, bots run in Kubernetes pods managed by `pod_operator`:

```bash
# Start pod operator (watches for bot activations)
python -m flexus_pod_operator.pod_watchdog --start-in-kube
```

The operator:
1. Subscribes to bot activation events via GraphQL
2. Creates Kubernetes pods in `isolated` namespace
3. Manages pod lifecycle, restarts, cleanup

### Environment Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `FLEXUS_API_BASEURL` | `http://127.0.0.1:8008` | Backend URL |
| `FLEXUS_API_KEY` | `sk_alice_123456` | API key for auth (local dev) |
| `FLEXUS_WORKSPACE` | `solarsystem` | Target workspace |
| `FLEXUS_GROUP` | `innerplanets` | Target group (optional, takes precedence) |
| `FLEXUS_WS_TICKET` | (auto-generated) | Pod auth token (production only) |

**Minimal setup for local dev / claude_code pod:**
```bash
export FLEXUS_API_BASEURL=http://127.0.0.1:8008
export FLEXUS_API_KEY=sk_alice_123456
export FLEXUS_WORKSPACE=solarsystem
```

### When to Reinstall

| Change | Reinstall Needed? |
|--------|-------------------|
| Edit tool handler logic | ❌ No (auto-restart) |
| Edit system prompt | ✅ Yes |
| Add/remove expert | ✅ Yes |
| Change setup schema | ✅ Yes |
| Change schedule | ✅ Yes |
| Edit Lark kernel | ✅ Yes |

---

## Complete Example: Frog Bot

The Frog bot is the simplest educational example. Here's the complete structure:

### frog_prompts.py
```python
from flexus_simple_bots import prompts_common

PROMPT_POND_REPORT = """
## Pond Reports
When working on a task, create a pond report using flexus_policy_document().
Path: /reports/pond-report-YYYY-MM-DD
Structure: {"pond_report": {"meta": {...}, "pond_name": "", "weather": "", ...}}
"""

frog_prompt = f"""
You are a friendly frog bot. You:
* Greet users with ribbit() calls
* Help with tasks and provide encouragement
* Keep conversations fun and motivating

{prompts_common.PROMPT_KANBAN}
{prompts_common.PROMPT_POLICY_DOCUMENTS}
{PROMPT_POND_REPORT}
{prompts_common.PROMPT_HERE_GOES_SETUP}
"""
```

### frog_bot.py (key parts)
```python
RIBBIT_TOOL = ckit_cloudtool.CloudTool(
    name="ribbit",
    description="Make a frog sound",
    parameters={
        "type": "object",
        "properties": {
            "intensity": {"type": "string", "enum": ["quiet", "normal", "loud"]},
            "message": {"type": "string"},
        },
        "required": ["intensity"],
    },
)

@rcx.on_tool_call(RIBBIT_TOOL.name)
async def toolcall_ribbit(toolcall, args):
    intensity = args.get("intensity", "normal")
    sounds = {"quiet": "ribbit...", "normal": "RIBBIT!", "loud": "RIBBIT RIBBIT RIBBIT!!!"}
    return sounds.get(intensity, "RIBBIT!")
```

### frog_install.py (key parts)
```python
FROG_DEFAULT_LARK = """
print("I see %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"]).lower()
    if "snake" in content:
        post_cd_instruction = "OMG dive down!!!"
"""

marketable_experts=[
    ("default", FMarketplaceExpertInput(
        fexp_system_prompt=frog_prompts.frog_prompt,
        fexp_python_kernel=FROG_DEFAULT_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_app_capture_tools=bot_internal_tools,
    )),
    ("huntmode", FMarketplaceExpertInput(
        fexp_system_prompt=frog_prompts.frog_prompt,
        fexp_python_kernel='subchat_result = "Insect!"',  # Always returns immediately
        fexp_block_tools="*setup*,frog_catch_insects",
        fexp_allow_tools="",
        fexp_app_capture_tools=bot_internal_tools,
    )),
]
```

---

## Quick Reference

### Setup Schema Types
- `string_short` - Single line text
- `string_long` - Longer text (shown larger)
- `string_multiline` - Multi-line textarea
- `bool` - Checkbox
- `int` - Integer
- `float` - Decimal number
- `list_dict` - Array of objects

### Common Prompt Fragments
```python
from flexus_simple_bots import prompts_common

prompts_common.PROMPT_KANBAN            # Kanban board usage
prompts_common.PROMPT_POLICY_DOCUMENTS  # Policy document usage
prompts_common.PROMPT_PRINT_WIDGET      # UI widgets
prompts_common.PROMPT_A2A_COMMUNICATION # Agent-to-agent
prompts_common.PROMPT_HERE_GOES_SETUP   # Setup message handling
```

### Useful Integrations
```python
from flexus_client_kit.integrations import fi_pdoc      # Policy documents
from flexus_client_kit.integrations import fi_slack     # Slack
from flexus_client_kit.integrations import fi_discord2  # Discord
from flexus_client_kit.integrations import fi_gmail     # Gmail
from flexus_client_kit.integrations import fi_github    # GitHub
from flexus_client_kit.integrations import fi_mongo_store  # MongoDB storage
from flexus_client_kit.integrations.report import fi_report  # Reports
```

### ckit Module Quick Reference
```python
from flexus_client_kit import ckit_client      # API connection
from flexus_client_kit import ckit_bot_exec    # Bot runtime, RobotContext
from flexus_client_kit import ckit_bot_install # Marketplace installation
from flexus_client_kit import ckit_cloudtool   # Tool definitions
from flexus_client_kit import ckit_ask_model   # Model interactions, subchats
from flexus_client_kit import ckit_kanban      # Kanban operations
from flexus_client_kit import ckit_shutdown    # Graceful shutdown
from flexus_client_kit import ckit_schedule    # Schedule parsing
from flexus_client_kit import ckit_mongo       # MongoDB credentials
from flexus_client_kit import ckit_expert      # Expert configuration
```

---

## Advanced Topics

### Human Confirmation Flow

For dangerous operations, tools can request human confirmation:

```python
from flexus_client_kit import ckit_cloudtool

@rcx.on_tool_call("dangerous_action")
async def handle_dangerous(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
    # Check if already confirmed
    if not toolcall.confirmed_by_human:
        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="dangerous_ops",  # Links to setup section
            confirm_command="delete_all_data",   # What will be executed
            confirm_explanation="This will permanently delete all data. Are you sure?",
        )

    # Human confirmed - execute dangerous operation
    return "Data deleted successfully"
```

**Flow:**
```
Tool raises NeedsConfirmation
       │
       ▼
UI shows [Accept] [Reject] buttons
       │
       ▼
Human clicks Accept → Tool re-executed with confirmed_by_human=True
```

### Budget & Metering System

**Multi-level budget hierarchy:**
```
Workspace Balance (real money)
    │
    ▼
Thread Budget (ft_budget → ft_coins)
    │
    ▼
Persona Daily Budget (persona_daily_budget → persona_daily_coins)
    │
    ▼
Task Budget (ktask_budget → ktask_coins)
```

**What happens when budget exceeded:**
- Thread blocked with `ft_error=FT_INSUFFICIENT_BALANCE`
- Scheduler skips persona until daily reset
- Kanban task marked `KTASK_OVER_BUDGET`
- UI shows `errorbox-over_budget`

**Recovery:**
- Coin deposit auto-unblocks all affected threads
- Daily reset clears `persona_daily_coins`

### Workspace vs Group Hierarchy

```
Workspace (ws_id)
└── Root Group (ws_root_group_id)
    ├── Group A (fgroup_parent_id → root)
    │   ├── Persona 1 (located_fgroup_id → A)
    │   ├── Policy Doc (located_fgroup_id → A)
    │   └── Group A.1 (fgroup_parent_id → A)
    └── Group B
        └── Persona 2
```

**Permission Roles (bitmask):**
| Role | Bit | Inherits |
|------|-----|----------|
| READ | 1 | - |
| WRITE | 2 | READ |
| MODERATOR | 4 | WRITE |
| INVITE | 8 | MODERATOR |
| BILLING | 16 | INVITE |
| ADMIN | 63 | All |

**Sharing:**
- `owner_shared=false` → Only owner sees
- `owner_shared=true` → Group members with READ+ see
- No individual sharing - must use groups

### Multi-Modal Tool Results

Tools can return images and rich content:

```python
import base64

@rcx.on_tool_call("generate_chart")
async def handle_chart(toolcall, args):
    # Generate image bytes
    image_bytes = generate_chart_image(args["data"])

    # Return Python list directly - NOT json.dumps()!
    return [
        {"m_type": "text", "m_content": "Here's your chart:"},
        {"m_type": "image/png", "m_content": base64.b64encode(image_bytes).decode('ascii')},
    ]
```

**Supported types:**
- `text` - Plain text
- `image/jpeg`, `image/png`, `image/gif` - Base64 images

> ⚠️ **Gotcha**: Return a Python `list`, NOT `json.dumps([...])`. The framework handles serialization.
> If you return a JSON string, it gets double-encoded and images won't render.

### Error Handling Patterns

**Unexpected exceptions are hidden from LLM:**
```python
# Any unhandled exception in tool handler becomes:
# "Tool error, see logs for details"
# The LLM does NOT see the actual exception message!
```

**Best practices - return error strings for recoverable errors:**
```python
@rcx.on_tool_call("my_tool")
async def handle(toolcall, args) -> str:
    try:
        result = do_something(args)
        return f"Success: {result}"
    except SpecificError as e:
        # Return friendly error string - LLM can understand and recover
        return f"Error: {e}. Try with different parameters."
    except AnotherKnownError as e:
        # Same pattern - return error as string
        return f"Failed: {e}"
    # Unexpected errors: bubble up, but LLM only sees "Tool error, see logs"
    # Debug via pod logs or kubectl logs
```

> ⚠️ **Gotcha**: Unlike cloudtool services, inprocess tool exceptions do NOT expose error details
> to the LLM. For recoverable errors, **return error strings** instead of raising exceptions.

### Per-Bot MongoDB Storage

Each bot gets a dedicated MongoDB database:

```python
from pymongo import AsyncMongoClient
from flexus_client_kit import ckit_mongo

async def mybot_main_loop(fclient, rcx):
    # Get connection string for this bot's database
    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)

    # Database name is persona_id + "_db"
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    my_collection = mydb["my_data"]

    # Use MongoDB normally
    await my_collection.insert_one({"key": "value"})
```

**MongoDB vs Policy Documents:**
| Use Case | MongoDB | Policy Documents |
|----------|---------|------------------|
| Dynamic runtime data | ✅ | ❌ |
| User-editable config | ❌ | ✅ |
| Structured reports | ❌ | ✅ (with forms) |
| Large binary files | ✅ (GridFS) | ❌ |
| Audit trail needed | ❌ | ✅ |

### Bot Versioning

**Version format:** `x.y.z` → encoded as `x*100M + y*10K + z`
- Example: `1.23.2` → `123000200`

**When versions change:**
```
marketable_version changes
       │
       ▼
news_from_marketplace() trigger fires
       │
       ▼
pod_operator receives notification
       │
       ▼
Pod restarted with new code
```

**Dev vs Prod:**
- Dev: `marketplace_upsert_dev_bot()` auto-upgrades all dev personas
- Prod: `bot_install_from_marketplace()` pins exact version

### Debugging Bots

**Primary debug methods:**

1. **kubectl logs** (raw pod output):
   ```bash
   kubectl logs -f <pod-name> -n isolated
   ```

2. **GraphQL subscriptions** (real-time in UI):
   ```graphql
   subscription { mcp_pod_logs_stream(mcp_id: "...", fgroup_id: "...") }
   ```

3. **Redis buffer** (recent history):
   ```bash
   redis-cli LRANGE mcp:logs:<mcp_id> 0 -1
   ```

**Lark kernel logs:**
- `print()` in Lark → appears in `ftm_provenance.kernel1_logs`
- Kernel errors → `ft_error` with `flagged_by_kernel: true`

**Structured logging:**
```python
import logging
logger = logging.getLogger("bot_mybot")
logger.info("Processing task %s", task_id)  # → Pod logs
```

### Featured Actions

Featured actions create prominent buttons in the bot UI:

```python
marketable_featured_actions=[
    {
        "feat_question": "Set up Slack integration",
        "feat_run_as_setup": True,
        "feat_depends_on_setup": ["slack"],  # Disabled until slack group complete
    },
    {
        "feat_question": "Generate weekly report",
        "feat_run_as_setup": False,
        "feat_depends_on_setup": [],
    },
],
```

**Behavior:**
- Buttons disabled if `feat_depends_on_setup` items missing from setup
- Click → starts chat with `feat_question` as first message
- `feat_run_as_setup=True` → uses setup expert mode

### Thread Capturing (Messengers)

**Capture flow:**
```
User: slack(op="capture", args={"thread": "#general/1234567890"})
       │
       ▼
Bot creates Flexus thread with:
  ft_app_capture = "slack"           # Immutable - marks ownership
  ft_app_searchable = "#general"     # Mutable - for filtering
  ft_app_specific = {"ts": "..."}    # Mutable - app metadata
       │
       ▼
Messages sync bidirectionally:
  Slack → Flexus: posted as user messages
  Flexus → Slack: assistant messages auto-posted
```

**Uncapture:**
```python
slack(op="uncapture")  # Sets ft_app_searchable = ""
```

### External OAuth

Bots can use OAuth tokens for external services:

```python
# User authorizes via UI: external_auth_start(provider="google")
# Token stored encrypted in flexus_external_auth

# Bot retrieves token:
token = await external_auth_token(ws_id, provider="google")
# Use token to call Google APIs
```

**Supported providers:**
Google, GitHub, Dropbox, Slack, LinkedIn, Facebook, Notion, OneDrive, Box, Outlook, Atlassian

**Token refresh:** Automatic (120s before expiry) for providers with refresh support.

### Streaming Tool Output

For long-running tools, stream progress to UI:

```python
import websockets
import json

@rcx.on_tool_call("long_operation")
async def handle_long(toolcall, args) -> str:
    ws_url = rcx.fclient.base_url_ws + "/v1/delta/ws"
    async with websockets.connect(ws_url) as ws:
        for i, item in enumerate(items):
            # Process item
            result = process(item)

            # Stream progress
            await ws.send(json.dumps({
                "ftm_belongs_to_ft_id": toolcall.fcall_ft_id,
                "ftm_alt": toolcall.fcall_ftm_alt,
                "ftm_num": toolcall.fcall_result_ftm_num,
                "delta": {
                    "ftm_role": "tool",
                    "ftm_content": f"Processed {i+1}/{len(items)}\n",
                    "ftm_call_id": toolcall.fcall_id,
                },
            }))

    return "All items processed"
```

**When to stream:**
- Operations >2 seconds
- Progress updates
- LLM token generation

**When NOT to stream:**
- Fast operations (<1s)
- Atomic results
- Binary data

---

## Common Gotchas Summary

Quick reference for the most common issues when creating bots:

| Issue | Symptom | Solution |
|-------|---------|----------|
| **No `--group` CLI flag** | Bot doesn't connect | Use `FLEXUS_WORKSPACE` or `FLEXUS_GROUP` env vars |
| **Wrong pdoc op** | "Unknown op" error | Use `create`/`overwrite`, not `write` or `status+help` |
| **Multi-modal double-encoding** | Images don't render | Return Python `list`, not `json.dumps([...])` |
| **TOOLS↔handlers mismatch** | Bot silently dies | Every tool in `TOOLS` needs matching `@rcx.on_tool_call()` |
| **Exception not visible to LLM** | LLM can't recover | Return error strings, don't raise for recoverable errors |
| **`default__s1.yaml` crashes** | Assertion error | Use `<botname>__s1.yaml` for default expert |
| **pdoc/slack tool not working** | "Unknown tool" error | Must wire into `TOOLS` + add `@rcx.on_tool_call` handler |
| **Missing image files** | Install crashes | Create `mybot-1024x1536.webp` and `mybot-256x256.webp` |
| **Bot doesn't auto-install** | Bot not found | Need `FLEXUS_WORKSPACE` set, not just `FLEXUS_GROUP` |
| **Changes not taking effect** | Old behavior persists | Run install script after prompt/expert/schedule changes |

### Debugging Checklist

1. **Bot won't start?**
   - Check `FLEXUS_API_BASEURL` and `FLEXUS_API_KEY` are set
   - Check `FLEXUS_WORKSPACE` or `FLEXUS_GROUP` is set
   - Run install script first: `python -m mybot_install --ws=...`

2. **Bot starts then immediately stops?**
   - Check TOOLS list matches `@rcx.on_tool_call()` handlers exactly
   - Look for error in logs: "Whoops make sure you call on_tool_call()"

3. **Tool not working?**
   - Check tool name spelling matches between `CloudTool(name=...)` and `@rcx.on_tool_call("...")`
   - Check handler is registered before main loop starts

4. **LLM ignores errors?**
   - Return error as string: `return f"Error: {e}"`
   - Don't rely on exceptions being visible

5. **Scenario test fails unexpectedly?**
   - Check scenario filename matches expected skill
   - Run with `--no-cleanup` to inspect test group after failure
