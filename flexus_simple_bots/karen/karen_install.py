import asyncio
import json
import base64
import argparse
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_bot_install
from flexus_client_kit.integrations import fi_slack


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


KAREN_BUDGET_WARNING = f"""
warning_text = "💿 Token budget is running low. Wrap up your current work, summarize the current chat thread, include what the original user's request was and the current status, and what to do next. Then call kanban_restart() with this summary to refresh context"

if coins > budget * 0.5 and not messages[-1]["tool_calls"]:
    for i, msg in enumerate(messages):
        warning_already_sent = False
        if msg["role"] == "kernel" and msg.get("content") and warning_text in str(msg["content"]):
            warning_already_sent = True
            break
    if not warning_already_sent:
        post_content = warning_text
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
        marketable_title1="Karen",
        marketable_title2="Your 24/7 customer support agent. Empathetic, accurate, and always keeps your users happy.",
        marketable_author="Flexus",
        marketable_occupation="Customer Support",
        marketable_description="## Karen - AI Customer Support Assistant\n\nA patient AI assistant that automates customer support workflows. Karen integrates with Slack and Discord to help users with technical issues, manages tasks through Kanban boards, and escalates complex problems to human engineers.\n\n**Key Features:**\n- **Multi-platform support**: Responds to users on Slack and Discord\n- **Smart task management**: Automatically sorts and prioritizes support requests\n- **Knowledge integration**: Searches company documentation to provide accurate solutions\n- **Issue tracking**: Files Jira tickets for bugs and complex problems\n- **Scheduled automation**: Processes inbox tasks every 15 minutes, works on assigned tasks every 5 minutes\n\n**Setup Requirements:**\n- Slack bot and app tokens for integration\n- Access to company knowledge base and Jira\n\nPerfect for teams looking to streamline their customer support process while maintaining a human touch.",
        marketable_typical_group="Development / Documentation",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.karen.karen_bot",
        marketable_setup_default=karen_setup_default,
        marketable_preferred_model_default="gpt-5-mini",
        marketable_daily_budget_default=1_000_000,
        marketable_default_inbox_default=100_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="karen_default",
            fexp_system_prompt=karen_prompts.short_prompt,
            fexp_python_kernel=KAREN_BUDGET_WARNING,
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="karen_setup",
            fexp_system_prompt=karen_prompts.karen_setup,
            fexp_python_kernel=KAREN_BUDGET_WARNING,
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["customer support"],
        marketable_picture_big_b64=big,
        marketable_picture_small_b64=small,
        marketable_schedule=[
            {
                "sched_type": "SCHED_TASK_SORT",  # this will also produce call flexus_bot_kanban()
                "sched_when": "EVERY:1m",
                "sched_first_question": "Look if there are any tasks in inbox, if there are then sort up to 20 of them according to the system prompt, and then say \"N tasks sorted\".",
            },
            {
                "sched_type": "SCHED_TODO",  # this will also produce call flexus_bot_kanban(op="assign_to_this_chat", args={"batch": ["task1337"]})
                "sched_when": "EVERY:1m",
                "sched_first_question": "Work on the assigned task.",
            },
        ],
        marketable_featured_actions=[
            ckit_bot_install.FeaturedAction(
                id="generate_task_report",
                label="Generate task completion report",  
                prompt="Generate a comprehensive report showing all completed tasks, their status, and performance metrics.",
                required_setup_groups=["Slack"],
                icon="file-pdf",
                icon_color="#ffffff",
                icon_bg_color="#22c55e"
            )
        ],
        marketable_featured_setup_categories=[
            ckit_bot_install.FeaturedSetupCategory(
                id="slack_setup",
                label="Manage your Slack integration",
                prompt="Help user to set up Slack integration, start from easiest. Guide them through creating a Slack app, getting bot tokens, and configuring channel access.",
                icon="slack",
                icon_color="#ffffff",
                icon_bg_color="#4A154B"
            )
        ],
        marketable_intro_message="Hey, happy to join your team!\nI'm ready to help you manage tasks and generate reports.\nLet me know what you need:\n• Set up your Slack integration to get started\n• I can help organize your team's workflow"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseurl", default="", help="Base URL for the Flexus API")
    parser.add_argument("--apikey", default="sk_alice_123456", help="API key for authentication")
    parser.add_argument("--ws", default="solarsystem", help="Workspace ID")
    args = parser.parse_args()
    client = ckit_client.FlexusClient("karen_install", base_url=args.baseurl, api_key=args.apikey)
    asyncio.run(install(client, ws_id=args.ws))
