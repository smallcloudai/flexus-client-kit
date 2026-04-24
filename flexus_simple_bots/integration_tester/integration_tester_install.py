import asyncio
import json
import logging
from typing import List

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool, ckit_integrations_db, ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.integration_tester import integration_tester_bot
from flexus_simple_bots.integration_tester import integration_tester_prompts

logger = logging.getLogger("integration_tester")

INTEGRATION_TESTER_SKILLS = ckit_skills.static_skills_find(integration_tester_bot.INTEGRATION_TESTER_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")


def _build_experts(tools):
    builtin_skills = ckit_skills.read_name_description(integration_tester_bot.INTEGRATION_TESTER_ROOTDIR, INTEGRATION_TESTER_SKILLS)
    tool_names = {t.name for rec in integration_tester_bot.INTEGRATION_TESTER_INTEGRATIONS for t in rec.integr_tools}
    tool_names.add(integration_tester_bot.PLAN_BATCHES_TOOL.name)
    allow_tools = ",".join(tool_names | ckit_cloudtool.KANBAN_ADVANCED | {"flexus_hand_over_task"})

    return [
        ("default", ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=integration_tester_prompts.DEFAULT_PROMPT,
            fexp_python_kernel="",
            fexp_allow_tools=allow_tools,
            fexp_nature="NATURE_INTERACTIVE",
            fexp_builtin_skills=builtin_skills,
            fexp_description="Test API key integrations",
        )),
        ("autonomous", ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=integration_tester_prompts.AUTONOMOUS_PROMPT,
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
It only tests integrations that are explicitly allowed for this bot.

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
    pic_big_path = integration_tester_bot.INTEGRATION_TESTER_ROOTDIR / "integration_tester-1024x1536.webp"
    pic_small_path = integration_tester_bot.INTEGRATION_TESTER_ROOTDIR / "integration_tester-256x256.webp"
    fallback_big_path = integration_tester_bot.INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-1024x1536.webp"
    fallback_small_path = integration_tester_bot.INTEGRATION_TESTER_ROOTDIR.parent / "bob" / "bob-256x256.webp"

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
    setup_schema_path = integration_tester_bot.INTEGRATION_TESTER_ROOTDIR / "setup_schema.json"
    integration_tester_setup_default = json.loads(setup_schema_path.read_text())

    _ensure_marketplace_images()

    experts = _build_experts(tools)

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=integration_tester_bot.INTEGRATION_TESTER_ROOTDIR,
        marketable_title1="Integration Tester",
        marketable_title2="Test API key integrations",
        marketable_author="Flexus",
        marketable_accent_color="#4CAF50",
        marketable_occupation="QA Engineer",
        marketable_description=INTEGRATION_TESTER_DESC,
        marketable_typical_group="Development",
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {
                "sched_when": "EVERY:1m",
                "sched_fexp_name": "default",
                "sched_first_question": "If there are tasks in Inbox, move exactly one task from Inbox to Todo using op=inbox_to_todo with a single task id. Never join multiple tasks together. Then respond with \"1 task sorted\" or \"0 tasks sorted\". Do nothing else.",
            },
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m", "sched_fexp_name": "autonomous"},
        ],
        marketable_setup_default=integration_tester_setup_default,
        marketable_featured_actions=[
            {"feat_question": "Test all integrations", "feat_expert": "default"},
            {"feat_question": "Test gmail", "feat_expert": "default"},
            {"feat_question": "Test google_sheets", "feat_expert": "default"},
            {"feat_question": "Test telegram", "feat_expert": "default"},
            {"feat_question": "Test slack", "feat_expert": "default"},
            {"feat_question": "Test notion", "feat_expert": "default"},
            {"feat_question": "Test airtable", "feat_expert": "default"},
            {"feat_question": "Test hubspot", "feat_expert": "default"},
            {"feat_question": "Test twilio", "feat_expert": "default"},
        ],
        marketable_intro_message="Hi! I'm Integration Tester. I create deterministic kanban batch tasks and resolve them autonomously.",
        marketable_preferred_model_expensive="gpt-5.4-mini",
        marketable_preferred_model_cheap="gpt-5.4-mini",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in experts],
        add_integrations_into_expert_system_prompt=integration_tester_bot.INTEGRATION_TESTER_INTEGRATIONS,
        marketable_tags=["testing", "integrations", "qa"],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_supported=[
            "gmail",
            "google_business",
            "google_ads",
            "google",
            "notion",
            "notion_manual",
            "airtable",
            "hubspot",
            "slack",
            "telegram",
            "twilio_manual",
        ],
        marketable_auth_scopes={
            "gmail": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.labels",
            ],
            "google_business": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/business.manage",
            ],
            "google_ads": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/adwords",
            ],
            "google": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/spreadsheets",
            ],
            "slack": [
                "channels:read",
                "chat:write",
                "chat:write.customize",
                "files:read",
                "users:read",
                "im:read",
            ],
        },
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    client = ckit_client.FlexusClient("integration_tester_install")
    asyncio.run(install(client, bot_name="integration_tester", bot_version="dev", tools=integration_tester_bot.TOOLS))
