import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.clerkwing import clerkwing_prompts


CLERKWING_ROOTDIR = Path(__file__).parent
CLERKWING_SKILLS = ckit_skills.static_skills_find(CLERKWING_ROOTDIR, shared_skills_allowlist="")
CLERKWING_SETUP_SCHEMA = json.loads((CLERKWING_ROOTDIR / "setup_schema.json").read_text())

BOT_DESCRIPTION = """
**Job description**
Clerkwing is your secretary robot — efficient, warm, and always on top of the pile. She manages your inbox, calendar, and Jira board so you can start every day knowing exactly what needs attention and in what order. No inbox anxiety, no double-booked meetings, no tickets falling through the cracks. Clerkwing keeps things organized without being pushy — professional when it counts, personable the rest of the time.

**How Clerkwing can help you:**
- Summarizes unread emails and categorizes them by priority so you know what actually needs a reply
- Drafts email responses and applies labels to keep your inbox clean and structured
- Checks your calendar for upcoming meetings, finds free slots, and resolves scheduling conflicts
- Creates, updates, and moves Jira tickets — so your board reflects reality, not wishful thinking
- Searches Jira issues and surfaces progress updates across active tasks
- Runs daily inbox and calendar reviews to give you a clear picture of the day ahead
- Delivers quick status snapshots across email, calendar, and Jira without you having to switch between tools
"""

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=clerkwing_prompts.clerkwing_prompt,
        fexp_python_kernel="",
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Main secretary assistant for managing email, calendar, and Jira tasks with proactive organization and helpful suggestions.",
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=clerkwing_prompts.clerkwing_setup,
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="Configuration assistant for setting up Gmail, Google Calendar, and Jira OAuth connections.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((CLERKWING_ROOTDIR / "clerkwing-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((CLERKWING_ROOTDIR / "clerkwing-256x256.webp").read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#41b949",
        marketable_title1="Clerkwing",
        marketable_title2="Your helpful secretary robot for email, calendar, and Jira management.",
        marketable_author="Flexus",
        marketable_occupation="Secretary Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Productivity",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.clerkwing.clerkwing_bot",
        marketable_setup_default=CLERKWING_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Summarize my unread emails", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "What's on my calendar today?", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Show my Jira tasks", "feat_expert": "default", "feat_depends_on_setup": ["jira_instance_url"]},
        ],
        marketable_intro_message="Hello! I'm Clerkwing, your secretary robot. I can help you manage your email, calendar, and Jira tasks. What would you like me to help with today?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Productivity", "Email", "Calendar", "Jira"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ],
        marketable_auth_needed=["google"],
        marketable_auth_supported=["atlassian"],
        marketable_auth_scopes={
            "google": [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.labels",
                "https://www.googleapis.com/auth/calendar",
            ],
            "atlassian": [
                "read:jira-work",
                "write:jira-work",
                "read:jql:jira",
                "read:project:jira",
                "write:issue:jira",
            ],
        },
    )


if __name__ == "__main__":
    from flexus_simple_bots.clerkwing import clerkwing_bot
    client = ckit_client.FlexusClient("clerkwing_install")
    asyncio.run(install(client, bot_name=clerkwing_bot.BOT_NAME, bot_version=clerkwing_bot.BOT_VERSION, tools=clerkwing_bot.TOOLS))
