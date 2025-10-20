import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.boss import boss_bot, boss_prompts


boss_setup_schema = [
    {
        "bs_name": "approval_policy",
        "bs_type": "string_multiline",
        "bs_default": "Think critically, if the task is aligned with the company's strategy. Especially pay attention to technical bugs, agents running in circles and doing stupid things, don't allow that.",
        "bs_group": "Policy",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Policy for approving or rejecting tasks from colleague bots",
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
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in boss_bot.TOOLS])
    with open(Path(__file__).with_name("boss-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("boss-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=boss_bot.BOT_NAME,
        marketable_version=boss_bot.BOT_VERSION,
        marketable_accent_color=boss_bot.ACCENT_COLOR,
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
            {"feat_question": "Review recent task approvals", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Boss, a Chief Orchestration Officer, I review and improve other bot's work to ensure quality and alignment with your goals.",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_daily_budget_default=50_000_000,
        marketable_default_inbox_default=5_000_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="boss_default",
            fexp_system_prompt=boss_prompts.boss_prompt,
            fexp_python_kernel="",
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="boss_setup",
            fexp_system_prompt=boss_prompts.boss_setup,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["management", "orchestration"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[
            {
                "sched_type": "SCHED_TASK_SORT",
                "sched_when": "EVERY:5m",
                "sched_first_question": "Look if there are any tasks in inbox, if there are then sort them and say 'Tasks sorted'.",
            },
            {
                "sched_type": "SCHED_TODO",
                "sched_when": "EVERY:2m",
                "sched_first_question": "Work the assigned task.",
            },
        ]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("boss_install")
    asyncio.run(install(client, ws_id=args.ws))
