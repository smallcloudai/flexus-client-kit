import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_simple_bots import prompts_common


BOT_NAME = "otter"

BOT_DESCRIPTION = """
## Otter Optimist

A grounded reframing companion that acknowledges what's hard, then helps you see what's
actionable and suggests a concrete next move.

**Not a toxic positivity bot.** Otter listens first, validates your frustration, then gently
pivots to what you can actually do about it.

**Good for:**
- Processing setbacks and frustrations
- Getting unstuck on decisions
- Turning vague complaints into actionable plans
- Team morale without the cringe
"""

setup_schema = [
    {
        "bs_name": "reframe_style",
        "bs_type": "string_short",
        "bs_default": "balanced",
        "bs_group": "Personality",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "How aggressively to reframe: gentle, balanced, or direct",
    },
]


def load_prompt(name: str) -> str:
    return (Path(__file__).parent / "otter_prompts" / name).read_text()


def build_expert_prompt(expert_name: str) -> str:
    return (
        load_prompt("personality.md")
        + "\n"
        + load_prompt(f"expert_{expert_name}.md")
        + "\n"
        + prompts_common.PROMPT_KANBAN
        + prompts_common.PROMPT_PRINT_WIDGET
        + prompts_common.PROMPT_POLICY_DOCUMENTS
        + prompts_common.PROMPT_A2A_COMMUNICATION
        + prompts_common.PROMPT_HERE_GOES_SETUP
    )


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(Path(__file__).with_name("otter-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode(Path(__file__).with_name("otter-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#6B8E6B",
        marketable_title1="Otter",
        marketable_title2="Reframes setbacks into next moves.",
        marketable_author="Flexus",
        marketable_occupation="Optimist Reframer",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Fun / Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_client_kit.no_special_code_bot flexus_simple_bots.otter.otter_install",
        marketable_setup_default=setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Everything is going wrong today", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "I'm stuck and don't know what to do next", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me reframe this problem", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hey! I'm Otter. Tell me what's on your mind -- I'll help you find the angle that gets you unstuck.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=build_expert_prompt("default"),
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Conversational reframing expert. Listens, validates, reframes, suggests next move.",
            )),
        ],
        marketable_tags=["Motivation", "Reframing", "Simple"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Reframe the assigned task and suggest a next move."},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
    from flexus_client_kit.integrations import fi_pdoc
    client = ckit_client.FlexusClient("otter_install")
    asyncio.run(install(client, bot_name=BOT_NAME, bot_version=SIMPLE_BOTS_COMMON_VERSION, tools=[fi_pdoc.POLICY_DOCUMENT_TOOL]))
