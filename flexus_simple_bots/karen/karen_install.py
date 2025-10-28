import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_discord2

from flexus_simple_bots import prompts_common
from flexus_simple_bots.karen import karen_bot, karen_prompts


karen_setup_default = [
    {
        "bs_name": "escalate_policy",
        "bs_type": "string_multiline",
        "bs_default": karen_prompts.escalate_policy,
        "bs_group": "Policy",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Tell the robot what issues should escalate to a human engineer",
    },
    {
        "bs_name": "escalate_technical_person",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Policy",
        "bs_placeholder": "tell Alice via slack",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Name or contact information of the technical person to escalate unresolved issues",
    },
]

karen_setup_default += fi_slack.SLACK_SETUP_SCHEMA
karen_setup_default += fi_discord2.DISCORD_SETUP_SCHEMA


KAREN_DESC = """
### Job description

Karen runs customer support like the best hire you ever made. She answers with precision and full context, and turns user feedback into actionable weekly reports for your team. Don't ever call her a chatbot: Karen learns from every interaction and provides support that goes beyond scripts, making each customer feel valued.

### How Karen can help you:
- Responds to support tickets instantly
- Maintains full customer conversation history
- Adjusts tone and replies based on customer sentiment
- Guides users through your help center and knowledge base
- Proactively detects patterns and flags repeated issues
- Summarizes insights into weekly reports for product & dev teams
- Learns from logs and user feedback to self-improve over time
"""


KAREN_BUDGET_KERNEL = f"""
warning_text = "💿 Token budget is running low. Wrap up your current work, summarize the current chat thread, include what the original user's request was and the current status, and what to do next. Then call kanban_restart() with this summary to refresh context"

if coins > budget * 0.5 and not messages[-1]["tool_calls"]:
    for i, msg in enumerate(messages):
        warning_already_sent = False
        if msg.get("content") and warning_text in str(msg["content"]):
            warning_already_sent = True
            break
    if not warning_already_sent:
        post_cd_instruction = warning_text
"""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in karen_bot.TOOLS])
    with open(Path(__file__).with_name("karen-1024x1536.webp"), "rb") as f:
        big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("karen-256x256.webp"), "rb") as f:
        small = base64.b64encode(f.read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=karen_bot.BOT_NAME,
        marketable_version=karen_bot.BOT_VERSION,
        marketable_accent_color="#23CCCC",
        marketable_title1="Karen",
        marketable_title2="Your 24/7 customer support agent. Empathetic, accurate, and always keeps your users happy.",
        marketable_author="Flexus",
        marketable_occupation="Customer Support",
        marketable_description=KAREN_DESC,
        marketable_typical_group="Development / Documentation",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.karen.karen_bot",
        marketable_setup_default=karen_setup_default,
        marketable_featured_actions=[
            {"feat_question": "What people ask for today?", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm here for your customers 24/7 — answering questions, remembering every detail, and always following up. I also deliver weekly feedback reports that help your team improve the product.",
        marketable_preferred_model_default="grok-4-fast",
        marketable_daily_budget_default=1_000_000,
        marketable_default_inbox_default=100_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="karen_default",
            fexp_system_prompt=karen_prompts.short_prompt,
            fexp_python_kernel=KAREN_BUDGET_KERNEL,
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="karen_setup",
            fexp_system_prompt=karen_prompts.karen_setup,
            fexp_python_kernel=KAREN_BUDGET_KERNEL,
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["Customer Support"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("karen_install")
    asyncio.run(install(client, ws_id=args.ws))
