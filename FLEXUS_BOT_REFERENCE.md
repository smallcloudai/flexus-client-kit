# Flexus Bot Reference

**Canonical example**: `flexus_client_kit/flexus_simple_bots/frog/` — read `frog_bot.py`, `frog_prompts.py`, `frog_install.py` for working code.

---

## How Flexus Works

### Backend Services

| Service | Purpose |
|---------|---------|
| `service_advancer.py` | LLM calls via LiteLLM, Lark kernel execution, message saving |
| `service_scheduler.py` | Bot activation based on schedules and kanban state |
| `service_pubsub_pump.py` | Routes DB changes to Redis pubsub channels |
| `service_cloudtool_kanban.py` | Handles `flexus_bot_kanban` tool calls |
| `service_cloudtool_web.py` | Handles `web` tool calls |
| `service_cloudtool_vecsearch.py` | Handles `flexus_vector_search` tool calls |
| `service_cloudtool_knowledge.py` | Handles knowledge base operations |
| `service_cloudtool_colleagues.py` | Handles `flexus_hand_over_task`, `flexus_colleagues` |

### Bot Installation (Two-Stage Process)

**Stage 1: Marketplace Publishing** (`marketplace_upsert_dev_bot`)
```
mybot_install.py --ws=workspace_id
       ↓
Creates in DB:
  - flexus_marketplace record (marketable_* fields, images, setup schema)
  - flexus_expert records (e.g., mybot_default, mybot_worker)
       ↓
Returns: FBotInstallOutput(marketable_name, marketable_version)
         ❌ No persona_id yet - bot is published but not running
```

**Stage 2: Hiring (Creating Persona Instance)** (`bot_install_from_marketplace`)
```
UI: /marketplace/mybot → "Hire" button
  OR
Code: ckit_bot_install.bot_install_from_marketplace(...)
       ↓
Creates in DB:
  - flexus_persona record (linked via persona_marketable_name/version)
  - flexus_persona_schedule records
       ↓
Returns: InstallationResult(fgroup_id, persona_id)
         ✅ persona_id obtained - bot can now run
```

**Complete Flow**:
```
mybot_install.py --ws=solarsystem     [Stage 1: publish to marketplace]
       ↓
UI "Hire" or bot_install_from_marketplace()  [Stage 2: create persona]
       ↓
mybot_bot.py connects via subscription  [Runtime: bot starts]
```

### Bot Runtime Flow

```
1. Bot subscribes via bot_threads_calls_tasks subscription
2. Events: persona/thread/message/task/toolcall updates arrive via Redis → parked in rcx
3. Main loop: unpark_collected_events() processes parked events sequentially
4. Tool calls: bot executes handler → posts result via cloudtool_post_result()
5. Advancement: backend receives tool result → continues LLM conversation
```

### Message Advancement (service_advancer.py)

```
User message arrives
       ↓
Lark Kernel #1 (pre-LLM)
  - Can inject cd_instruction
  - Can set error to stop
       ↓
LLM Call (via LiteLLM)
  - Uses ft_toolset from thread
  - Streams to /v1/delta/ws
       ↓
Lark Kernel #2 (post-LLM)
  - Can kill_tools to cancel
  - Can set subchat_result
       ↓
Save assistant message + tool_calls to DB
       ↓
If tool_calls exist → wait for tool results
If no tool_calls → thread ready for user
```

### Tool Call Routing

```
LLM generates tool_call in assistant message
              ↓
    ┌─────────────────────┐
    │ Tool name in bot's  │
    │ inprocess_tool_names? │
    └─────────────────────┘
        YES │         │ NO
            ↓         ↓
    Bot receives   Cloudtool service
    FCloudtoolCall subscribes and handles
            │         │
            ↓         ↓
    @rcx.on_tool_call  service_cloudtool_*.py
    handler runs       handler runs
            │         │
            └────┬────┘
                 ↓
    cloudtool_post_result() mutation
                 ↓
    Result saved as role="tool" message
                 ↓
    Advancer continues (next LLM call or finish)
```

### GraphQL Operations Used by Bots

**Subscriptions** (ckit_bot_exec.py):
| Operation | Purpose |
|-----------|---------|
| `bot_threads_calls_tasks` | Main event stream - receives personas, threads, messages, tool calls, tasks |

**Mutations** (ckit_*.py modules):
| Operation | Module | Purpose |
|-----------|--------|---------|
| `marketplace_upsert_dev_bot` | ckit_bot_install | Register bot in marketplace |
| `bot_install_from_marketplace` | ckit_bot_install | Create persona instance |
| `bot_activate` | ckit_ask_model | Start new conversation |
| `bot_subchat_create_multiple` | ckit_ask_model | Create parallel subchats |
| `bot_confirm_exists` | ckit_bot_exec | Keepalive (every 120s) |
| `cloudtool_post_result` | ckit_cloudtool | Post tool call result |
| `cloudtool_confirmation_request` | ckit_cloudtool | Request human confirmation |
| `thread_messages_create_multiple` | ckit_ask_model | Add messages to thread |

### Subscription Events (bot_threads_calls_tasks)

| Event Type | Payload | Bot Handler |
|------------|---------|-------------|
| `flexus_persona` | Persona config (setup, budget) | Creates/updates RobotContext |
| `flexus_thread` | Thread state (ft_id, ft_error) | `@rcx.on_updated_thread` |
| `flexus_thread_message` | Message content | `@rcx.on_updated_message` |
| `flexus_tool_call` | Tool invocation (only if in inprocess_tool_names) | `@rcx.on_tool_call("name")` |
| `flexus_persona_kanban_task` | Task state changes | `@rcx.on_updated_task` |
| `erp.*` | ERP table changes (if subscribed) | `@rcx.on_erp_change("table")` |

### Key Data Structures

**FCloudtoolCall** (received by tool handlers):
| Field | Purpose |
|-------|---------|
| `fcall_id` | Unique call ID |
| `fcall_ft_id` | Thread ID |
| `fcall_name` | Tool name |
| `fcall_arguments` | JSON arguments from LLM |
| `ws_id` | Workspace ID |
| `connected_persona_id` | Bot's persona ID |
| `confirmed_by_human` | For confirmation flow |

**RobotContext.persona** (FPersonaOutput):
| Field | Purpose |
|-------|---------|
| `persona_id` | Unique persona ID |
| `persona_setup` | Dict of user's setup values |
| `ws_id` | Workspace ID |
| `ws_root_group_id` | Root group for policy docs |
| `persona_marketable_name` | Bot type name |
| `persona_daily_budget` | Daily coin budget |
| `persona_daily_coins` | Coins spent today |

---

## Common Bot Patterns

### Pattern 1: Basic Bot (frog)
Simple tools + policy documents + MongoDB storage + ERP subscription.
```python
TOOLS = [CUSTOM_TOOL, fi_mongo_store.MONGO_STORE_TOOL, fi_pdoc.POLICY_DOCUMENT_TOOL]
# ERP subscription (optional): subscribe_to_erp_tables=["crm_contact"]
@rcx.on_erp_change("crm_contact")
async def on_change(action, new_record, old_record): ...
```

### Pattern 2: Messenger Bot (karen)
Reactive listener for Slack/Discord → kanban inbox.
```python
slack = fi_slack.IntegrationSlack(fclient, rcx, SLACK_BOT_TOKEN=..., SLACK_APP_TOKEN=...)
slack.set_activity_callback(lambda a, posted: ckit_kanban.bot_kanban_post_into_inbox(...))
await slack.join_channels(); await slack.start_reactive()
# In @on_updated_message: await slack.look_assistant_might_have_posted_something(msg)
# In finally: await slack.close()
```

### Pattern 3: Subchat-Delegating Bot (lawyerrat, productman)
Tools that delegate to subchats with same or different skill.
```python
@rcx.on_tool_call("complex_task")
async def handle(toolcall, args):
    subchats = await ckit_ask_model.bot_subchat_create_multiple(
        client=fclient, who_is_asking="bot_subtask", persona_id=rcx.persona.persona_id,
        first_question=[prompt], first_calls=["null"], title=["Task"],
        fcall_id=toolcall.fcall_id, skill="default")  # or skill="criticize_idea"
    raise ckit_cloudtool.WaitForSubchats(subchats)
```

### Pattern 4: Pipeline Bot (owl_strategist)
Sequential steps with dependency-enforced subchats, each step = separate expert.
```python
AGENT_REQUIRED_DOCS = {"diagnostic": ["input"], "metrics": ["input", "diagnostic"], ...}
@rcx.on_tool_call("run_agent")
async def handle(toolcall, args):
    agent = args["agent"]  # e.g., "diagnostic"
    if not step_exists(experiment_id, AGENT_REQUIRED_DOCS[agent]):
        return "Missing prerequisite"
    context = load_prior_docs(experiment_id, AGENT_REQUIRED_DOCS[agent])
    subchats = await ckit_ask_model.bot_subchat_create_multiple(..., skill=agent)
    raise ckit_cloudtool.WaitForSubchats(subchats)
# Subchat kernel detects "AGENT_COMPLETE" → sets subchat_result
```

### Pattern 5: Background Polling Bot (productman surveys)
Periodic updates in main loop for external API state.
```python
last_update, interval = 0, 60
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    if time.time() - last_update > interval:
        await integration.update_active_surveys(); last_update = time.time()
```

### Pattern 6: Management Bot (boss)
Cross-bot coordination with A2A resolution and colleague setup.
```python
# A2A resolution tool - approve/reject tasks from other bots
BOSS_A2A_RESOLUTION_TOOL = CloudTool(name="boss_a2a_resolution",
    parameters={"task_id": str, "resolution": ["approve","reject","rework"], "comment": str})
# Thread viewer - see context of handed-over tasks
THREAD_MESSAGES_PRINTED_TOOL = CloudTool(name="thread_messages_printed",
    parameters={"a2a_task_id": str, "ft_id": str})
# Confirmation for dangerous actions
if not toolcall.confirmed_by_human:
    raise ckit_cloudtool.NeedsConfirmation(confirm_setup_key="allow_...", ...)
```

### Expert Organization by Bot

| Bot | Experts | Purpose |
|-----|---------|---------|
| frog | `default`, `huntmode` | `huntmode` for parallel subchat (returns immediately) |
| karen | `default`, `setup` | `setup` for configuration help |
| boss | `default`, `setup` | `setup` for explaining capabilities |
| productman | `default`, `criticize_idea`, `survey` | Different tools per skill |
| owl_strategist | `default` + 7 pipeline skills | Each step: unique prompt + kernel |

### Lark Kernel Recipes

**Budget Warning** (karen):
```python
if coins > budget * 0.5 and not messages[-1]["tool_calls"]:
    if "warning_text" not in str(messages):
        post_cd_instruction = "💿 Token budget running low. Wrap up..."
```

**Immediate Subchat Return** (frog huntmode):
```python
subchat_result = "Insect!"  # Returns immediately, no LLM call needed
```

**Marker Detection** (productman criticize_idea):
```python
if "RATING-COMPLETED" in str(messages[-1]["content"]):
    subchat_result = "Read the file using flexus_policy_document..."
elif len(messages[-1].get("tool_calls", [])) == 0:
    post_cd_instruction = "Follow system prompt, end with RATING-COMPLETED"
```

**Safety Injection** (lawyerrat):
```python
if "malpractice" in str(messages[-1]["content"]).lower():
    post_cd_instruction = "Include appropriate disclaimers!"
```

---

## Files Structure

| File | Purpose | Change requires |
|------|---------|-----------------|
| `mybot_bot.py` | Runtime: tools, handlers, main loop | Auto-restart |
| `mybot_prompts.py` | System prompts | Reinstall |
| `mybot_install.py` | Marketplace registration, experts, schedules, setup schema | Reinstall |
| `mybot-1024x1536.webp` | Big marketplace picture | Reinstall |
| `mybot-256x256.webp` | Avatar | Reinstall |
| `forms/*.html` | Optional: custom forms for policy docs | Reinstall |

---

## Tools

### Cloudtools (Backend Services - No Handler Needed)
| Tool | Purpose |
|------|---------|
| `flexus_bot_kanban` | Kanban board operations |
| `web` | Web search and fetch |
| `flexus_vector_search` | Vector similarity search |
| `flexus_hand_over_task` | A2A communication (delegate to other bots) |
| `flexus_colleagues` | List available bots |
| `flexus_my_setup` | Read bot setup |

### Inprocess Tools (Require Handler)
Every tool in `TOOLS` list must have `@rcx.on_tool_call(TOOL.name)` handler. See `frog_bot.py` for examples.

**Tool definition rules** (strict mode):
- All params must be in `"required"` array
- Use `["type", "null"]` for optional params
- Must have `"additionalProperties": False`

**Handler return values**:
- Return `str` for success/error messages (LLM sees this)
- Return `List[{m_type, m_content}]` for multi-modal (images/files)
- Exceptions become "Tool error, see logs" (LLM doesn't see details)

---

## Experts (Skills)

Different experts = different system prompt + kernel + tool filters. Must include `"default"` expert.

**Key fields** (`FMarketplaceExpertInput`):
- `fexp_system_prompt` - LLM system prompt
- `fexp_python_kernel` - Lark script (runs on backend before/after LLM)
- `fexp_block_tools` / `fexp_allow_tools` - Glob patterns for cloudtools (mutually exclusive)
- `fexp_app_capture_tools` - JSON of inprocess tools (different tools per skill!)
- `fexp_inactivity_timeout` - Seconds before inactivity warning (e.g., 600)

**Different tools per skill** (productman pattern):
```python
TOOLS_DEFAULT = [IDEA_TEMPLATE_TOOL, HYPOTHESIS_TEMPLATE_TOOL, VERIFY_IDEA_TOOL, fi_pdoc.POLICY_DOCUMENT_TOOL]
TOOLS_SURVEY = [survey_research.SURVEY_RESEARCH_TOOL, fi_pdoc.POLICY_DOCUMENT_TOOL]
TOOLS_VERIFY_SUBCHAT = [fi_pdoc.POLICY_DOCUMENT_TOOL]  # Minimal toolset for focused work

marketable_experts=[
    ("default", FMarketplaceExpertInput(fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS_DEFAULT]), ...)),
    ("criticize_idea", FMarketplaceExpertInput(fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS_VERIFY_SUBCHAT]), ...)),
    ("survey", FMarketplaceExpertInput(fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in TOOLS_SURVEY]), ...)),
]
```

### Subchats
Use `ckit_ask_model.bot_subchat_create_multiple()` + `raise ckit_cloudtool.WaitForSubchats(subchats)`.

**Critical**: Subchat expert kernel **must** set `subchat_result` to complete. Options:
1. **Immediate return**: `subchat_result = "Done"` (no LLM call, frog huntmode)
2. **Marker detection**: Check for "AGENT_COMPLETE" in assistant content (owl_strategist)
3. **Default behavior**: Let LLM run, kernel returns result when done

---

## Lark Kernels

Starlark scripts run on backend before/after each LLM call. See `frog_install.py` for examples.

| Direction | Variables |
|-----------|-----------|
| **Inputs** | `messages` (list of {role, content, tool_calls, call_id}), `coins` (int), `budget` (int) |
| **Outputs** | `error` (str→stop), `kill_tools` (bool→cancel), `post_cd_instruction` (str→inject), `subchat_result` (any→finish subchat) |

`print()` output goes to `ftm_provenance.lark_logs1/2` (visible in bot logs).

---

## Schedules

| Type | Triggers When | What Happens |
|------|---------------|--------------|
| `SCHED_TASK_SORT` | Inbox has items | Bot sorts inbox to todo |
| `SCHED_TODO` | Todo has items | Assigns task, starts chat |
| `SCHED_ANY` | Time-based only | Runs `sched_first_question` |
| `SCHED_CREATE_TASK` | Time-based only | Creates and assigns task |

Use `prompts_common.SCHED_TASK_SORT_10M` and `prompts_common.SCHED_TODO_5M` as defaults.

---

## RobotContext (rcx)

**Key Fields**: `rcx.persona`, `rcx.latest_threads`, `rcx.latest_tasks`, `rcx.workdir`, `rcx.fclient`

**Handlers**:
| Decorator | Signature |
|-----------|-----------|
| `@rcx.on_updated_message` | `async def(msg: FThreadMessageOutput)` |
| `@rcx.on_updated_thread` | `async def(thread: FThreadOutput)` |
| `@rcx.on_updated_task` | `async def(task: FPersonaKanbanTaskOutput)` |
| `@rcx.on_tool_call("name")` | `async def(toolcall, args) -> str` |
| `@rcx.on_erp_change("table")` | `async def(action, new_record, old_record)` |

---

## Setup Schema

| bs_type | Python type |
|---------|-------------|
| `string_short` | str |
| `string_long` | str |
| `string_multiline` | str |
| `bool` | bool |
| `int` | int |
| `float` | float |
| `list_dict` | list |

Required fields: `bs_name`, `bs_type`, `bs_default`, `bs_group`
Optional: `bs_description`, `bs_order`, `bs_importance`, `bs_placeholder`

---

## Common Prompt Fragments

| Fragment | Purpose |
|----------|---------|
| `PROMPT_KANBAN` | Kanban board usage |
| `PROMPT_POLICY_DOCUMENTS` | Policy doc storage |
| `PROMPT_PRINT_WIDGET` | UI widgets |
| `PROMPT_A2A_COMMUNICATION` | Bot-to-bot delegation |
| `PROMPT_HERE_GOES_SETUP` | Setup message format |

---

## Available Integrations

| Module | Tool | Purpose | Example Bot |
|--------|------|---------|-------------|
| `fi_pdoc` | `POLICY_DOCUMENT_TOOL` | Policy document CRUD | frog, lawyerrat |
| `fi_mongo_store` | `MONGO_STORE_TOOL` | Personal MongoDB storage | frog, lawyerrat |
| `fi_slack` | `SLACK_TOOL` | Slack messenger (reactive) | karen |
| `fi_discord2` | `DISCORD_TOOL` | Discord messenger (reactive) | karen |
| `fi_telegram` | - | Telegram messenger | - |
| `fi_gmail` | - | Gmail integration | - |
| `fi_report` | - | Report generation (PDF) | adspy |
| `fi_widget` | `PRINT_WIDGET_TOOL` | UI widgets | lawyerrat |
| `fi_repo_reader` | `REPO_READER_TOOL` | Git repo browsing | karen |

### Integration Init Patterns

**MongoDB** (most bots):
```python
mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
mongo = AsyncMongoClient(mongo_conn_str)
mydb = mongo[rcx.persona.persona_id + "_db"]
personal_mongo = mydb["personal_mongo"]
```

**Policy Documents** (most bots):
```python
pdoc = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
```

**Slack** (messenger bots):
```python
slack = fi_slack.IntegrationSlack(fclient, rcx,
    SLACK_BOT_TOKEN=setup["SLACK_BOT_TOKEN"],
    SLACK_APP_TOKEN=setup["SLACK_APP_TOKEN"],
    should_join=setup["slack_should_join"])
slack.set_activity_callback(my_callback)
await slack.join_channels()
await slack.start_reactive()
# ... in finally: await slack.close()
```

**Discord** (messenger bots):
```python
discord = fi_discord2.IntegrationDiscord(fclient, rcx,
    DISCORD_BOT_TOKEN=setup["DISCORD_BOT_TOKEN"],
    watch_channels=setup["discord_watch_channels"])
discord.set_activity_callback(my_callback)
await discord.join_channels()
await discord.start_reactive()
# ... in finally: await discord.close()
```

---

## Custom Forms

Forms provide custom HTML editors for policy documents instead of JSON editor.

**Setup**:
```python
# In install.py:
marketable_forms=ckit_bot_install.load_form_bundles(__file__)

# Directory structure:
mybot/
  forms/
    pond_report.html  # For docs with {"pond_report": {"meta": {...}, ...}}
```

Form filename must match the top-level key containing a `meta` object.

**Protocol** (iframe ↔ parent):
- Parent → Form: `INIT` (content, themeCss), `CONTENT_UPDATE`, `FOCUS`
- Form → Parent: `FORM_READY`, `FORM_CONTENT_CHANGED` (content)

**Theme CSS variables** (auto-injected, use these not hardcoded colors):
- `--p-primary-contrast-color` (paper bg), `--p-primary-color` (paper text)
- `--p-content-hover-background` (desk/input bg), `--p-text-muted-color` (muted)

See `frog/forms/pond_report.html` for complete example.

---

## Testing

1. **Syntax**: `python -m py_compile mybot_bot.py mybot_prompts.py mybot_install.py`
2. **Imports**: `python -c 'import mybot_bot; import mybot_install; print("OK")'`
3. **Install**: `python mybot_install.py --ws=workspace_id`
4. **Scenario**: `python -m mybot.mybot_bot --scenario mybot/mybot__s1.yaml`

⚠️ Scenario files must be `botname__scenarioname.yaml`, NOT `default__*.yaml`

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Tool calls ignored | No handler | Add `@rcx.on_tool_call(TOOL.name)` for every tool in TOOLS |
| Changes don't work | Data in DB | Run install after changing prompts/experts/schedules |
| LLM doesn't see error | Exception | Return error string instead of raising |
| Subchat hangs | Missing result | Subchat expert kernel must set `subchat_result` |
| Images missing | File not found | Create both webp files before install |

---

## Environment

```bash
export FLEXUS_API_BASEURL=https://staging.flexus.team/
export FLEXUS_API_KEY=...
export FLEXUS_WORKSPACE=WnOQwTD2yL
```

---

## Marketplace Installation Parameters

Required fields for `marketplace_upsert_dev_bot`:

| Parameter | Validation |
|-----------|------------|
| `marketable_name` | snake_case, 1-40 chars |
| `marketable_version` | x.y.z semver, must be > existing |
| `marketable_title1` | ≤50 chars |
| `marketable_title2` | ≤200 chars |
| `marketable_occupation` | ≤100 chars |
| `marketable_author` | ≤200 chars |
| `marketable_description` | ≤10000 chars |
| `marketable_typical_group` | ≤100 chars, path like "Category / Subcategory" |
| `marketable_picture_big_b64` | WEBP, exactly 1024x1536 pixels |
| `marketable_picture_small_b64` | WEBP, exactly 256x256 pixels |
| `marketable_experts` | Must include "default" expert, ≤10 experts |
| `marketable_tags` | Each ≤100 chars |

---

## Dev Container Flow (BOB)

```
1. BOB calls bob_install_dev_bot mutation
       ↓
2. Backend looks up marketplace record by marketable_name
       ↓
3. Creates persona in "Test / {marketable_name}" group path
       ↓
4. Returns fgroup_id + persona_id
       ↓
5. Dev container starts with git repo cloned to /workspace
       ↓
6. Bot runs: python -m mybot.mybot_bot --group=fgroup_id
```

**Dev container requirements**:
- `flexus_client_kit` pre-installed in container
- If bot has `setup.py`, auto-runs `pip install -e /workspace`
- Images must be accessible from installed package location

---

## Confirmation Flow (Dangerous Actions)

For tools that need human approval before execution:

```python
@rcx.on_tool_call("dangerous_action")
async def handle(toolcall, args):
    if not toolcall.confirmed_by_human:
        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="allow_dangerous",      # Setup field that can auto-approve
            confirm_command="delete_everything",      # What action needs approval
            confirm_explanation="This will delete all data. Are you sure?",
        )
    # User confirmed, proceed with action
    return "Action completed"
```

---

## A2A Communication (Agent-to-Agent)

**Delegation** (async, via kanban):
- Bot calls `flexus_hand_over_task(to_bot="other_bot", description="...", skill="default")`
- Task created in other bot's inbox
- Original chat continues (doesn't wait)
- Result arrives later as 💿-message when task moves to "done"

**Subchats** (sync, within same bot):
- Use `bot_subchat_create_multiple()` + `raise WaitForSubchats()`
- Parent tool call waits for all subchats to complete
- Results collected automatically
- Timeout: 3600s (1 hour max)

---

## Message Roles

| Role | Source | Purpose |
|------|--------|---------|
| `user` | Human or scheduler | User input |
| `assistant` | LLM | Bot response, may include tool_calls |
| `tool` | Tool handler | Tool execution result |
| `cd_instruction` | Lark kernel | Injected instruction (💿-prefixed) |
| `context_file` | System | File/document context |

---

## Thread States

| Field | Meaning |
|-------|---------|
| `ft_need_assistant` | >0 = waiting for LLM to respond |
| `ft_need_tool_calls` | >0 = waiting for tool results |
| `ft_need_user` | >0 = waiting for user input |
| `ft_error` | Non-empty = thread has error (shown in UI) |
| `ft_coins` | Coins spent on this thread |
| `ft_budget` | Budget limit for this thread |
