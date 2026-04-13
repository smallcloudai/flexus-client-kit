import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool, ckit_skills, ckit_integrations_db
from flexus_simple_bots import prompts_common
from flexus_client_kit.integrations import fi_newsapi, fi_resend

logger = logging.getLogger("integration_tester")

INTEGRATION_TESTER_ROOTDIR = Path(__file__).parent
INTEGRATION_TESTER_SKILLS = ckit_skills.static_skills_find(INTEGRATION_TESTER_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")

from flexus_simple_bots.integration_tester.integration_tester_bot import (
    INTEGRATION_REGISTRY,
    PLAN_BATCHES_TOOL,
)

INTEGRATION_TESTER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    INTEGRATION_TESTER_ROOTDIR,
    allowlist=["newsapi", "resend"],
    builtin_skills=[],
)


def get_available_integrations() -> List[Dict[str, Any]]:
    result = []
    for rec in INTEGRATION_TESTER_INTEGRATIONS:
        name = rec.integr_name
        reg = INTEGRATION_REGISTRY.get(name)
        if not reg:
            continue
        key = os.environ.get(reg["env_var"])
        if not key and "alt_env_vars" in reg:
            for alt in reg["alt_env_vars"]:
                key = os.environ.get(alt)
                if key:
                    break
        if key:
            result.append({
                "name": name,
                "env_var": reg["env_var"],
                "has_key": True,
                "key_hint": key[-4:] if len(key) > 4 else "***",
            })
        else:
            result.append({
                "name": name,
                "env_var": reg["env_var"],
                "has_key": False,
                "key_hint": None,
            })
    return result


def _build_experts(tools):
    builtin_skills = ckit_skills.read_name_description(INTEGRATION_TESTER_ROOTDIR, INTEGRATION_TESTER_SKILLS)
    tool_names = {reg["tool"].name for reg in INTEGRATION_REGISTRY.values()}
    tool_names.add(PLAN_BATCHES_TOOL.name)
    allow_tools = ",".join(tool_names | ckit_cloudtool.KANBAN_ADVANCED | {"flexus_hand_over_task"})

    available = get_available_integrations()
    available_list = "\n".join([
        f"- {item['name']} ({item['env_var']}: ***{item['key_hint']})" if item['has_key']
        else f"- {item['name']} ({item['env_var']}: NOT SET)"
        for item in available
    ])

    default_prompt = f"""You are Integration Tester. Test API key-based integrations via kanban fan-out.

== AVAILABLE INTEGRATIONS ==
{available_list}

== RULES ==
- Parse user request into integration list: "all", "newsapi", "resend".
- First call integration_plan_batches(requested="...", batch_size=5, configured_only=true).
- Use returned task_specs and create tasks with flexus_hand_over_task(to_bot="Integration Tester", title=..., description=..., fexp_name="autonomous").
- Do not execute test tools in this interactive chat after fan-out.
- After creating tasks, reply with a clean queue summary in this exact style:

  Queued {{N}} batch covering {{X}} integrations: {{name1}} and {{name2}}.

  Detailed per-integration results (API key checks, method lists, counts) will appear here shortly from the autonomous worker.

- Note any unsupported integrations if they were requested.
- 💿-messages inform you when a handed-over task completes. When you see one, extract the resolution_summary and present it to the user as a markdown table (or plain summary if it is not a table). Do not just dump raw text.
- If no supported integrations were requested, explain supported options and stop.
"""

    autonomous_prompt = f"""You are Integration Tester autonomous worker.

== AVAILABLE INTEGRATIONS ==
{available_list}

== TASK MODE ==
- You are running with one assigned kanban task.
- Read assigned task title + description.
- Parse integration names from description line: "Integrations: name1,name2,...".
- If parsing fails, resolve task as FAILED with reason "Batch parse error".

== EXECUTION ==
For each integration in the batch:
1. You may call op="help" once to learn available operations, but do NOT treat help as the test result.
2. You MUST run a real read-only test afterwards.
   - Best choices: list_methods, status, list, call a simple method.
   - Never treat help, op="help", or documentation text as a successful test.
   - If list/status returns 403/401/error, that integration FAILED.
3. Each tool result includes api_key_hint — include it.
4. Collect one concise details string per integration (operation + key metrics or error).

== REPORT FORMAT ==
When resolving, use a markdown table for the resolution_summary and final reply:

| Integration | Status | Details |
|-------------|--------|---------|
| newsapi     | PASSED | list_methods: api_key_hint=***dc9, method_ids=[newsapi.everything.v1, ...], total=126 |
| resend      | FAILED | list: api_key_hint=***oGH, 403: dev bots must use their own Resend account |

- Use PASSED only if all integrations in the batch passed; otherwise FAILED.
- Keep Details concise but informative (mention operation, api_key_hint, counts, method names, or error).
- After building the table, call flexus_kanban_advanced(op="resolve", args={{"task_id":"<current_task_id>", "resolution_code":"PASSED"|"FAILED", "resolution_summary":"<markdown table>"}}).
- Do not wait for user input.
"""

    return [
        ("default", ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=default_prompt,
            fexp_python_kernel="",
            fexp_allow_tools=allow_tools,
            fexp_nature="NATURE_INTERACTIVE",
            fexp_builtin_skills=builtin_skills,
            fexp_description="Test API key integrations",
        )),
        ("autonomous", ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=autonomous_prompt,
            fexp_python_kernel="",
            fexp_allow_tools=allow_tools,
            fexp_nature="NATURE_AUTONOMOUS",
            fexp_inactivity_timeout=600,
            fexp_builtin_skills=builtin_skills,
            fexp_description="Autonomous integration testing",
        )),
    ]


INTEGRATION_TESTER_DESC = """
**Job description**

Integration Tester validates that Flexus API key-based integrations are properly configured and functional.
It tests newsapi and resend integrations using API keys from ENV_CONFIG.

**How it works:**
1. User starts a test session via "Test Integrations" button
2. Bot checks which API keys are configured
3. User selects what to test (all or specific)
4. Bot creates deterministic kanban batch tasks in inbox
5. Autonomous worker resolves assigned batch tasks

**What it tests:**
- newsapi: Calls sources endpoint to verify API key works
- resend: Lists domains to verify API key works

**Results:**
- PASSED: Integration responds correctly
- FAILED: API key invalid or integration unreachable
"""


def _ensure_marketplace_images() -> None:
    pic_big_path = INTEGRATION_TESTER_ROOTDIR / "integration_tester-1024x1536.webp"
    pic_small_path = INTEGRATION_TESTER_ROOTDIR / "integration_tester-256x256.webp"
    fallback_big_path = INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-1024x1536.webp"
    fallback_small_path = INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-256x256.webp"

    if not pic_big_path.exists() and fallback_big_path.exists():
        pic_big_path.write_bytes(fallback_big_path.read_bytes())
    if not pic_small_path.exists() and fallback_small_path.exists():
        pic_small_path.write_bytes(fallback_small_path.read_bytes())


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    setup_schema_path = INTEGRATION_TESTER_ROOTDIR / "setup_schema.json"
    integration_tester_setup_default = json.loads(setup_schema_path.read_text())

    _ensure_marketplace_images()

    experts = _build_experts(tools)

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=INTEGRATION_TESTER_ROOTDIR,
        marketable_title1="Integration Tester",
        marketable_title2="Test API key integrations",
        marketable_author="Flexus",
        marketable_accent_color="#4CAF50",
        marketable_occupation="QA Engineer",
        marketable_description=INTEGRATION_TESTER_DESC,
        marketable_typical_group="Development",
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m", "sched_fexp_name": "default"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m", "sched_fexp_name": "autonomous"},
        ],
        marketable_setup_default=integration_tester_setup_default,
        marketable_featured_actions=[
            {"feat_question": "Test all integrations", "feat_expert": "default"},
            {"feat_question": "Test newsapi", "feat_expert": "default"},
            {"feat_question": "Test resend", "feat_expert": "default"},
        ],
        marketable_intro_message="Hi! I'm Integration Tester. I create deterministic kanban batch tasks and resolve them autonomously.",
        marketable_preferred_model_expensive="gpt-5.4-mini",
        marketable_preferred_model_cheap="gpt-5.4-mini",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in experts],
        marketable_tags=["testing", "integrations", "qa"],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from flexus_simple_bots.integration_tester import integration_tester_bot
    client = ckit_client.FlexusClient(f"{integration_tester_bot.BOT_NAME}_install")
    asyncio.run(install(client, bot_name=integration_tester_bot.BOT_NAME, bot_version=integration_tester_bot.BOT_VERSION, tools=integration_tester_bot.TOOLS))
