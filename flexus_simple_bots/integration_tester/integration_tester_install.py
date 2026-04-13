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

    autonomous_prompt = """You are Integration Tester autonomous worker. You own one kanban task and must finish it without asking the user anything.

Task handling:
- Read the assigned task.
- Parse integration names from the description line: "Integrations: name1,name2,...".
- Read the optional mapping line: "Tool mapping: integration1->tool_name1, integration2->tool_name2".
- If a mapping line is present, use that tool name literally for the matching integration.
- Example: integration `resend` may map to tool `email_setup_domain`.
- If parsing fails, resolve the task as FAILED with summary "Batch parse error".
- You must finish this batch in the current task/thread.
- Do not hand over, delegate, split, or create sibling tasks for individual integrations.
- A delegated or promised future test does not count as a test result for this task.

For each integration:
1. Call op="help" once to discover safe operations.
2. If available, you may call list_methods to inspect method names.
3. Then run at least one more real non-discovery read-only call.
3. Never use create, update, delete, send, or other state-changing operations.
4. Prefer status, list, get, search, or a simple call with harmless arguments.

Operation classes:
- discovery/local ops: help, list_methods, and any status op that only reports local readiness, configured credentials, or known method counts
- provider-check ops: call, list, get, search, or a status op only when it clearly performs a real provider/API check instead of local metadata reporting
- prefer provider-check ops over discovery/local ops
- when using op="call", method_id must be copied literally from list_methods or help output
- never invent or guess method_id values
- op names such as help, status, list, or search are not valid method_id values unless they appear literally in the method list

What counts as a real test:
- help is not a test
- list_methods is discovery, not a test
- a local/status readiness check is not a test if it only reports local metadata such as has_api_key, ready, configured, or method_count
- tool output starting with [HELP OUTPUT - NOT A TEST] is not a test
- you must not stop after help or list_methods
- the first call that can count as a test must be a provider-check op
- every integration listed in the task must get its own real non-discovery call
- the real non-discovery call must happen in this task/thread, not in another task
- the integration is UNTESTED if you only called help/list_methods or never made a non-discovery call
- if you skipped a listed integration, it is UNTESTED
- if you delegated a listed integration instead of testing it here, it is UNTESTED
- do not invent reasons such as "no safe method available" unless the tool itself explicitly told you that
- the integration is FAILED if a non-help call returns an error, including 401/403/auth problems
- the integration is PASSED if a provider-check op succeeds and returns concrete provider data or provider-backed metadata
- if op="call" fails with METHOD_UNKNOWN because you guessed method_id, read list_methods and retry once with a literal listed method_id before deciding the final status

Report requirements:
- Build a markdown table with exactly these columns: Integration | Status | Details
- Status must be one of: PASSED, FAILED, UNTESTED
- Details must include the real provider-check operation you used, api_key_hint if present, and one concrete result such as count, returned object type, key fields, or error text
- Keep details concise and factual

Resolve the task with flexus_kanban_advanced using:
- resolution_code=PASSED only if every listed integration is PASSED
- if any integration is FAILED or UNTESTED, resolution_code must be FAILED
- resolution_summary=<the markdown table>

Do not wait for user input. Do not leave the task unresolved.
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
