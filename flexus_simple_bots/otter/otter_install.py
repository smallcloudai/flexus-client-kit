import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit import no_special_code_bot
from flexus_simple_bots import prompts_common


BOT_NAME = "otter"
BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())
EXPERTS = ckit_experts_from_files.discover_experts(Path(__file__).parent / "prompts")
TOOLS = ["flexus_policy_document"]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
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
        marketable_setup_default=SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Everything is going wrong today", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "I'm stuck and don't know what to do next", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me reframe this problem", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hey! I'm Otter. Tell me what's on your mind -- I'll help you find the angle that gets you unstuck.",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Motivation", "Reframing", "Simple"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_PICK_ONE_5M,
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
    client = ckit_client.FlexusClient("otter_install")
    asyncio.run(install(client, bot_name=BOT_NAME, bot_version=SIMPLE_BOTS_COMMON_VERSION, tools=no_special_code_bot.tool_registry_lookup(TOOLS)))
