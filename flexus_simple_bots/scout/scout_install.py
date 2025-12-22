import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit.integrations import fi_crm_automations

from flexus_simple_bots import prompts_common
from flexus_simple_bots.scout import scout_bot, scout_prompts, scout_skills


BOT_DESCRIPTION = """
## Scout — The Discovery Partner

Helps early-stage founders have meaningful conversations with waitlist contacts.
Not mass emails — personalized outreach that gets responses and validated learnings.

**Key Features:**
- **Personalized Outreach**: Context-aware emails based on contact source and hypothesis
- **Email Conversations**: Async discovery through back-and-forth exchanges
- **Survey + Incentives**: Broader reach with perks for respondents
- **Insight Extraction**: Structured learnings linked to your hypotheses
- **Lightweight Orchestration**: Main chat stays simple, heavy work in subchats

**Discovery Modes:**
- Email conversation (async, 3-5 exchanges)
- Interview booking (sync, for deeper understanding)
- Survey + incentive (quantitative validation)

**Perfect for:**
- Early-stage founders validating ideas
- Teams with waitlist but no time to email everyone
- Anyone who wants to learn from customers, not just sell

Scout connects with ProductMan hypotheses and writes insights back for validation.
"""


scout_setup_schema = fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA + [
    {
        "bs_name": "email_language",
        "bs_type": "string_short",
        "bs_default": "en",
        "bs_group": "Communications",
        "bs_order": 10,
        "bs_importance": 1,
        "bs_description": "Language for email content (e.g., 'en', 'ru', 'de')",
    },
    {
        "bs_name": "sender_name",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Communications",
        "bs_order": 20,
        "bs_importance": 1,
        "bs_description": "Your name for email signature",
    },
    {
        "bs_name": "sender_title",
        "bs_type": "string_short",
        "bs_default": "Founder",
        "bs_group": "Communications",
        "bs_order": 30,
        "bs_importance": 0,
        "bs_description": "Your title for email signature",
    },
    {
        "bs_name": "default_incentive",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Communications",
        "bs_order": 40,
        "bs_importance": 0,
        "bs_description": "Default perk for survey respondents (e.g., '3 months free after launch')",
    },
    {
        "bs_name": "calendar_link",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Communications",
        "bs_order": 50,
        "bs_importance": 0,
        "bs_description": "Calendly/Cal.com link for interview booking (placeholder for now)",
    },
]


def _load_lark(name: str) -> str:
    return (Path(__file__).parent / "lark" / f"{name}.lark").read_text(encoding="utf-8")


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])
    tools_template = json.dumps([t.openai_style_tool() for t in scout_bot.TOOLS_TEMPLATE_BUILDER])
    tools_message = json.dumps([t.openai_style_tool() for t in scout_bot.TOOLS_MESSAGE_WRITER])
    tools_insight = json.dumps([t.openai_style_tool() for t in scout_bot.TOOLS_INSIGHT_EXTRACTOR])
    # XXX: Using Rick images for now, replace with Scout images later
    pic_big = base64.b64encode(open(Path(__file__).with_name("rick-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("rick-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#4A90D9",
        marketable_title1="Scout",
        marketable_title2="The Discovery Partner — Personalized outreach for validated learnings",
        marketable_author="Flexus",
        marketable_occupation="Customer Discovery",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Discovery",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.scout.scout_bot",
        marketable_setup_default=scout_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Help me set up outreach for my waitlist", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Show contacts and their conversation status", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Create an email template for discovery outreach", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Scout, your discovery partner. I help you have meaningful conversations with waitlist contacts to validate your ideas. What would you like to work on?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=scout_prompts.scout_prompt_default,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
            ("template_builder", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=scout_skills.TEMPLATE_BUILDER_PROMPT,
                fexp_python_kernel=_load_lark("template_builder"),
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=tools_template,
            )),
            ("message_writer", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=scout_skills.MESSAGE_WRITER_PROMPT,
                fexp_python_kernel=_load_lark("message_writer"),
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=tools_message,
            )),
            ("insight_extractor", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=scout_skills.INSIGHT_EXTRACTOR_PROMPT,
                fexp_python_kernel=_load_lark("insight_extractor"),
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=tools_insight,
            )),
        ],
        marketable_tags=["Discovery", "Outreach", "Email", "Validation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1h", "sched_first_question": "Check for new contacts needing outreach and prepare personalized messages."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:30m", "sched_first_question": "Check for email responses and continue conversations."},
        ],
        marketable_forms={
            "email-template": (Path(__file__).parent / "forms" / "email-template.html").read_text(encoding="utf-8"),
        },
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("scout_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=scout_bot.BOT_NAME, bot_version=scout_bot.BOT_VERSION, tools=scout_bot.TOOLS))

