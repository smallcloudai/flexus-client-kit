import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install, ckit_client, ckit_cloudtool
from flexus_simple_bots import prompts_common
from flexus_simple_bots.telegram_groupmod import telegram_groupmod_bot, telegram_groupmod_prompts


BOT_DESCRIPTION = """
## Telegram GroupMod - Group Moderation Bot

Keeps your Telegram groups clean, safe, and on-topic.

**Features:**
- Delete messages matching word/phrase blocklist
- Block links except from whitelisted domains
- Detect spam and excessive forwarded messages
- Warn, mute, kick, or ban users with auto-escalation
- Challenge new members with captcha/questions
- Periodic buffer review for offtopic detection
- Daily moderation reports in MongoDB

**Requires:**
- Telegram bot token from @BotFather
- Bot must be added as admin to the group with delete/ban permissions
"""

TELEGRAM_GROUPMOD_SETUP_SCHEMA = [
    {
        "bs_name": "blocklist",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Message Filtering",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Words and phrases to block, one per line. Messages containing any of these will be deleted.",
    },
    {
        "bs_name": "whitelisted_domains",
        "bs_type": "string_multiline",
        "bs_default": "youtube.com\nyoutu.be\ntwitter.com\nx.com\ngithub.com\nwikipedia.org",
        "bs_group": "Message Filtering",
        "bs_order": 2,
        "bs_importance": 1,
        "bs_description": "Allowed link domains, one per line. Links to other domains will be deleted.",
    },
    {
        "bs_name": "block_all_links",
        "bs_type": "bool",
        "bs_default": False,
        "bs_group": "Message Filtering",
        "bs_order": 3,
        "bs_importance": 0,
        "bs_description": "Block ALL links regardless of whitelist. Useful for strict groups.",
    },
    {
        "bs_name": "group_topic",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Group Rules",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Description of what this group is about. Used to detect offtopic messages during buffer review.",
    },
    {
        "bs_name": "moderation_rules",
        "bs_type": "string_multiline",
        "bs_default": "Be respectful. No spam. Stay on topic. No hate speech.",
        "bs_group": "Group Rules",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Group rules shown to new members and used to judge violations.",
    },
    {
        "bs_name": "warns_before_mute",
        "bs_type": "int",
        "bs_default": 3,
        "bs_group": "Escalation",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Number of warnings before auto-muting a user.",
    },
    {
        "bs_name": "mutes_before_ban",
        "bs_type": "int",
        "bs_default": 2,
        "bs_group": "Escalation",
        "bs_order": 2,
        "bs_importance": 1,
        "bs_description": "Number of mutes before auto-banning a user.",
    },
    {
        "bs_name": "captcha_enabled",
        "bs_type": "bool",
        "bs_default": True,
        "bs_group": "New Members",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Challenge new members with a simple question before allowing them to chat.",
    },
    {
        "bs_name": "captcha_timeout_minutes",
        "bs_type": "int",
        "bs_default": 5,
        "bs_group": "New Members",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Minutes to wait for captcha answer before kicking.",
    },
    {
        "bs_name": "welcome_message",
        "bs_type": "string_multiline",
        "bs_default": "Welcome to the group! Please read the rules.",
        "bs_group": "New Members",
        "bs_order": 3,
        "bs_importance": 0,
        "bs_description": "Message sent after a new member passes verification.",
    },
]


REVIEWER_LARK = """
msg = messages[-1]
if msg["role"] == "assistant" and len(msg["tool_calls"]) == 0:
    post_cd_instruction = "This is a non-interactive chat, take actions or resolve the task, follow the system prompt."
"""


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    pic_big = base64.b64encode(open(Path(__file__).with_name(f"{bot_name}-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name(f"{bot_name}-256x256.webp"), "rb").read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#DC143C",
        marketable_title1="Telegram Group Mod",
        marketable_title2="Moderate Telegram groups: filter messages, manage members, enforce rules.",
        marketable_author="Flexus",
        marketable_occupation="Telegram Group Moderator",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Moderation",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.telegram_groupmod.telegram_groupmod_bot",
        marketable_setup_default=TELEGRAM_GROUPMOD_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Show moderation stats for today", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "List recent warnings", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Add me as admin to your Telegram group, I'll pick it up!",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_default,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Can both run moderation tasks and help to human admin interactively to do stuff.",
            )),
            ("review_messages", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_review_messages,
                fexp_python_kernel=REVIEWER_LARK,
                fexp_block_tools="*setup*,*colleagues*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_inactivity_timeout=600,  # actually REVIEWER_LARK will remind the model to continue immediately, but let scheduler remind too
                fexp_description="Reviews collected messages for offtopic, spam, and rule violations.",
            )),
            ("talk_in_dm", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=telegram_groupmod_prompts.prompt_groupmod_talk_in_dm,
                fexp_python_kernel="",
                fexp_block_tools="*setup*,*colleagues*",
                fexp_allow_tools="",
                fexp_app_capture_tools=json.dumps([t.openai_style_tool() for t in telegram_groupmod_bot.TOOLS_DM]),
                fexp_inactivity_timeout=600,
                fexp_description="Talks to people in Telegram DMs, answers questions, explains rules.",
            )),
        ],
        marketable_tags=["Moderation", "Telegram"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_needed=["telegram"],
    )


if __name__ == "__main__":
    client = ckit_client.FlexusClient("telegram_groupmod_install")
    asyncio.run(install(
        client,
        bot_name=telegram_groupmod_bot.BOT_NAME,
        bot_version=telegram_groupmod_bot.BOT_VERSION,
        tools=telegram_groupmod_bot.TOOLS_ALL,  # Careful here to give exactly the same list as will go into run_bots_in_this_group(inprocess_tools=)
    ))
