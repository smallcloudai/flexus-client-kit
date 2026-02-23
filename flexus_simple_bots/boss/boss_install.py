import asyncio
import json
import base64
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.boss import boss_prompts


boss_setup_schema = [
    {
        "bs_name": "behavior_tune",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Policy",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Write your personal preferences how you want Boss to behave",
    },
    {
        "bs_name": "sample_rate_success",
        "bs_type": "float",
        "bs_default": 0.1,
        "bs_group": "Quality Assurance",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Sample rate for successful tasks from all bots to be sent to boss for quality assurance",
    },
    {
        "bs_name": "sample_rate_failure",
        "bs_type": "float",
        "bs_default": 0.2,
        "bs_group": "Quality Assurance",
        "bs_order": 3,
        "bs_importance": 0,
        "bs_description": "Sample rate for failed tasks from all bots to be sent to boss for quality assurance",
    },
    {
        "bs_name": "orchestration_max_iterations",
        "bs_type": "int",
        "bs_default": 5,
        "bs_group": "Orchestration",
        "bs_order": 4,
        "bs_importance": 0,
        "bs_description": "Maximum requirements->feedback loop iterations before escalation to user feedback",
    },
    {
        "bs_name": "orchestration_max_rework_per_task",
        "bs_type": "int",
        "bs_default": 3,
        "bs_group": "Orchestration",
        "bs_order": 5,
        "bs_importance": 0,
        "bs_description": "Maximum review reworks per task before forcing escalation",
    },
]


BOSS_DESCRIPTION = """
## I Boss Other Agents Around

I micromanage other agents so you don't have to. Explain your strategy, and I will make
sure all agents on your team are successful performing their tasks, and the tasks are aligned
with your vision.


### Capabilities
- All agent-to-agent communication goes through my approval
- A finished task goes through my review
- I will offer you improvements in agents' setup
"""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    with open(Path(__file__).with_name("boss-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("boss-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Boss",
        marketable_title2="The Boss manages your bot army - keeps them focused, productive, and on-strategy",
        marketable_author="Flexus",
        marketable_occupation="Chief of Bots",
        marketable_description=BOSS_DESCRIPTION,
        marketable_typical_group="/",  # install at root
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.boss.boss_bot",
        marketable_setup_default=boss_setup_schema,
        marketable_featured_actions=[
            # {"feat_question": "Review recent task approvals", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Boss, a Chief Orchestration Officer, I review and improve other bot's work to ensure quality and alignment with your goals.",
        marketable_preferred_model_default="gpt-5.2",
        marketable_daily_budget_default=999_999_999,
        marketable_default_inbox_default=999_999_999,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=boss_prompts.boss_default,
                fexp_python_kernel="",
                fexp_block_tools="*setup",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Helps hire bots and create tasks to accomplish goals, ensuring work aligns with company strategy and vision.",
            )),
            ("uihelp", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=boss_prompts.boss_uihelp,
                fexp_python_kernel="",
                fexp_block_tools="*setup",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Assists users in navigating Flexus UI, including highlighting elements, document uploads, EDS, and MCP configuration.",
            )),
        ],
        marketable_tags=["management", "orchestration"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[
            prompts_common.SCHED_PICK_ONE_5M | {"sched_when": "EVERY:2m"},
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.boss import boss_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("boss_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=boss_bot.BOT_NAME, bot_version=boss_bot.BOT_VERSION, tools=boss_bot.TOOLS))
