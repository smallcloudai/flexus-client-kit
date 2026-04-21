import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.tasktopus import tasktopus_bot
from flexus_simple_bots.tasktopus import tasktopus_prompts


TOOL_NAMESET = {t.name for t in tasktopus_bot.TOOLS}

ONE_ON_ONE_CAPTURE_KERNEL = """
captured = False
warn_text = "You have not captured any messenger chat yet. Anything you write will go nowhere until you call capture. Call the messenger tool with op=capture for the person you are addressing."
warn_have = False

for msg in messages:
    s = str(msg["content"])
    if "📌CAPTURED" in s:
        captured = True
    if warn_text in s:
        warn_have = True

if not captured and not warn_have and messages[-1]["role"] == "assistant" and not messages[-1]["tool_calls"]:
    post_cd_instruction = warn_text
"""

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=tasktopus_prompts.TASKTOPUS_DEFAULT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=3600,
        fexp_description="Main expert that handles user interactions and task management.",
    )),
    ("one_on_one_messenger", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=tasktopus_prompts.ONE_ON_ONE_MESSENGER_PROMPT,
        fexp_python_kernel=ONE_ON_ONE_CAPTURE_KERNEL,
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=3600,
        fexp_description="Handles a single messenger 1:1 conversation with a specific person (morning briefings, check-ins, follow-ups).",
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
        marketable_description=(tasktopus_bot.TASKTOPUS_ROOTDIR / "README.md").read_text(),
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
        marketable_auth_supported=["slack", "fibery"],
        marketable_auth_scopes={
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
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("tasktopus_install")
    asyncio.run(install(client))
