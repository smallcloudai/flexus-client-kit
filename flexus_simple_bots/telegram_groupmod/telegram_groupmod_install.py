import asyncio
from flexus_client_kit import ckit_bot_install, ckit_client, ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.telegram_groupmod import telegram_groupmod_bot
from flexus_simple_bots.telegram_groupmod import telegram_groupmod_prompts


TOOL_NAMESET = {t.name for t in telegram_groupmod_bot.TOOLS_ALL}

BOT_DESCRIPTION = """
**Job description**
Telegram GroupMod is the admin your group actually needs. He keeps communities clean, safe, and on-topic — 24/7, without moderator burnout. Spam gets caught, bad actors get escalated, and new members are vetted before they can cause trouble. Every moderation action is logged, and daily reports keep you in the loop without requiring you to read every message. Set the rules once; GroupMod enforces them consistently.

**How Telegram GroupMod can help you:**
- Deletes messages containing blocked words or phrases automatically
- Blocks links from non-whitelisted domains to stop spam and unwanted promotions
- Detects spam patterns and flags excessive forwarded messages before they flood the chat
- Warns, mutes, kicks, or bans users with auto-escalation — consequences match the behavior
- Challenges new members with captcha or custom questions to filter bots and bad-faith joiners
- Runs periodic buffer reviews to catch off-topic content that slips through keyword filters
- Generates daily moderation reports stored in MongoDB so you always know what happened and why

**What you need to get started:**
- A Telegram bot token from @BotFather
- GroupMod added as admin to your group with delete and ban permissions enabled
"""


REVIEWER_LARK = """
msg = messages[-1]
if msg["role"] == "assistant" and len(msg["tool_calls"]) == 0:
    post_cd_instruction = "This is a non-interactive chat, take actions or resolve the task, follow the system prompt."
"""


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_default,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="Can both run moderation tasks and help to human admin interactively to do stuff.",
    )),
    ("review_messages", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_review_messages,
        fexp_python_kernel=REVIEWER_LARK,
        fexp_allow_tools=",".join(ckit_cloudtool.CLOUDTOOLS_SAFE),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_description="Reviews collected messages for offtopic, spam, and rule violations.",
    )),
    ("talk_in_dm", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_talk_in_dm,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(ckit_cloudtool.CLOUDTOOLS_SAFE | ckit_cloudtool.CLOUDTOOLS_VECDB | {"telegram", "flexus_policy_document"}),
        fexp_nature="NATURE_SEMI_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_description="Talks to people in Telegram DMs, answers questions, explains rules.",
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=telegram_groupmod_bot.TELEGRAM_GROUPMOD_ROOTDIR,
        marketable_accent_color="#ff66ae",
        marketable_title1="Telegram Group Mod",
        marketable_title2="Moderate Telegram groups: filter messages, manage members, enforce rules.",
        marketable_author="Flexus",
        marketable_occupation="Telegram Group Moderator",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Moderation",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.telegram_groupmod.telegram_groupmod_bot",
        marketable_setup_default=telegram_groupmod_bot.TELEGRAM_GROUPMOD_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Show moderation stats for today", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "List recent warnings", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Add me as admin to your Telegram group, I'll pick it up!",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(telegram_groupmod_bot.TOOLS_ALL)) for name, exp in EXPERTS],
        marketable_tags=["Moderation", "Telegram"],
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_needed=["telegram"],
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("telegram_groupmod_install")
    asyncio.run(install(client))
