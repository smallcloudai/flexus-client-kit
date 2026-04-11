import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.tasktopus import tasktopus_bot
from flexus_simple_bots.tasktopus import tasktopus_prompts


TOOL_NAMESET = {t.name for t in tasktopus_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=tasktopus_prompts.tasktopus_prompt,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=3600,
        fexp_description="Main expert that handles user interactions and task management.",
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=tasktopus_bot.TASKTOPUS_ROOTDIR,
        marketable_accent_color="#7B2D8E",
        marketable_title1="Tasktopus",
        marketable_title2="An eight-armed task manager that gets things done.",
        marketable_author="Flexus",
        marketable_occupation="Task Manager",
        marketable_description="Tasktopus manages your tasks through a kanban board. It triages incoming work, prioritizes tasks, and resolves them methodically.",
        marketable_typical_group="Productivity",
        marketable_setup_default=tasktopus_bot.TASKTOPUS_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "What's on my board?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hey! I'm Tasktopus. I'll keep your tasks moving. What needs doing?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(tasktopus_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=tasktopus_bot.TASKTOPUS_INTEGRATIONS,
        marketable_tags=["Productivity", "Tasks"],
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("tasktopus_install")
    asyncio.run(install(client))
