import asyncio
import json
import logging
import os
from typing import List

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool, ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.integration_tester import integration_tester_shared as shared

logger = logging.getLogger("integration_tester")

INTEGRATION_TESTER_SKILLS = ckit_skills.static_skills_find(shared.INTEGRATION_TESTER_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")


def _build_experts(tools):
    builtin_skills = ckit_skills.read_name_description(shared.INTEGRATION_TESTER_ROOTDIR, INTEGRATION_TESTER_SKILLS)
    tool_names = {reg["tool"].name for reg in shared.INTEGRATION_REGISTRY.values()}
    tool_names.add(shared.PLAN_BATCHES_TOOL.name)
    allow_tools = ",".join(tool_names | ckit_cloudtool.KANBAN_ADVANCED | {"flexus_hand_over_task"})

    default_prompt = """You are Integration Tester. Your job is to queue autonomous smoke tests for supported API-key integrations and then report the finished results clearly.

Rules:
- Supported requests are: "all" or a comma-separated list of supported integration names.
- First call integration_plan_batches(requested="...", batch_size=5, configured_only=true).
- Use every returned task_spec to create a task with flexus_hand_over_task(to_bot="Integration Tester", title=..., description=..., fexp_name="autonomous").
- Do not run integration tools in this interactive chat. This chat only plans work and reports completed task results.
- If nothing supported/configured was selected, explain that briefly and stop.
- Mention unsupported requested names if any.

After queueing tasks, reply in this format:
Queued {{N}} batch covering {{X}} integrations: {{name1}} and {{name2}}.

Detailed per-integration results will appear here after the autonomous worker finishes.

When a completed-task message arrives:
- read resolution_summary
- present it as a markdown table if it is a table, otherwise give a short plain summary
- do not dump raw task metadata
"""

    autonomous_prompt = """You are Integration Tester smoke test orchestrator. You own one kanban task.

Parse integrations from task description "Integrations: name1,name2,..." and optional "Tool mapping: ..." line.

For each integration:
1. Call op=help to discover available operations
2. Call op=list_methods to see the method catalog
3. Pick 3 different read-only operations that return real provider data (not help, not local status like has_api_key, ready, configured, method_count)
4. Execute all 3 calls and collect results

Classification:
- PASSED: at least 1 of the 3 calls succeeded with real provider data
- FAILED: all 3 calls failed or errored
- Build a markdown table: Integration | Status | Details

Resolve with flexus_kanban_advanced:
- resolution_code=PASSED only if ALL integrations PASSED
- resolution_summary=<the markdown table>

Do not hand over, delegate, or wait for user input.
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
It only tests integrations that are explicitly allowed for this bot and have API keys provided through ENV_CONFIG.

**How it works:**
1. User starts a test session via "Test Integrations" button
2. Bot checks which supported integrations are configured
3. User selects what to test (all or specific supported integrations)
4. Bot creates deterministic kanban batch tasks in inbox
5. Autonomous worker discovers safe operations, runs at least one real read-only API call per integration, and resolves the task with a table of results

**What it tests:**
- Any integration included in this bot's supported allowlist
- Real read-only operations only
- No create/update/delete/send actions

**Results:**
- PASSED: A real non-help read-only call succeeded
- FAILED: A real non-help call failed
- UNTESTED: Only discovery calls were made, so the integration was not actually tested
"""


def _ensure_marketplace_images() -> None:
    pic_big_path = shared.INTEGRATION_TESTER_ROOTDIR / "integration_tester-1024x1536.webp"
    pic_small_path = shared.INTEGRATION_TESTER_ROOTDIR / "integration_tester-256x256.webp"
    fallback_big_path = shared.INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-1024x1536.webp"
    fallback_small_path = shared.INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-256x256.webp"

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
    setup_schema_path = shared.INTEGRATION_TESTER_ROOTDIR / "setup_schema.json"
    integration_tester_setup_default = json.loads(setup_schema_path.read_text())

    _ensure_marketplace_images()

    experts = _build_experts(tools)

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=shared.INTEGRATION_TESTER_ROOTDIR,
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

    client = ckit_client.FlexusClient("integration_tester_install")
    asyncio.run(install(client, bot_name="integration_tester", bot_version="dev", tools=shared.TOOLS))
