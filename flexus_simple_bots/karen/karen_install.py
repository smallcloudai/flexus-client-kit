import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_discord2

from flexus_simple_bots import prompts_common
from flexus_simple_bots.karen import karen_prompts


KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.skill_find_all(KAREN_ROOTDIR, shared_skills_allowlist="")
KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += fi_slack.SLACK_SETUP_SCHEMA
KAREN_SETUP_SCHEMA += fi_discord2.DISCORD_SETUP_SCHEMA


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


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.short_prompt,
        fexp_python_kernel=KAREN_BUDGET_KERNEL,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_inactivity_timeout=600,
        fexp_description="Handles customer support tickets by searching knowledge base, providing helpful responses, and escalating unresolved issues.",
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.karen_setup,
        fexp_python_kernel=KAREN_BUDGET_KERNEL,
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="Guides users through bot configuration, helping set up information sources like MCP servers or Flexus hotstorage for support queries.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((KAREN_ROOTDIR / "karen-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((KAREN_ROOTDIR / "karen-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#23CCCC",
        marketable_title1="Karen",
        marketable_title2="Your 24/7 customer support agent. Empathetic, accurate, and always keeps your users happy.",
        marketable_author="Flexus",
        marketable_occupation="Customer Support",
        marketable_description=KAREN_DESC,
        marketable_typical_group="Development / Documentation",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.karen.karen_bot",
        marketable_setup_default=KAREN_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "What people ask for today?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm here for your customers 24/7 — answering questions, remembering every detail, and always following up. I also deliver weekly feedback reports that help your team improve the product.",
        marketable_preferred_model_default="grok-4-fast",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Customer Support"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_auth_supported=["slack", "slack_manual", "discord_manual"],
        marketable_auth_scopes={
            "slack": [
                "channels:read",
                "chat:write",
                "files:read",
                "users:read",
                "im:read"
            ],
        },
    )


if __name__ == "__main__":
    from flexus_simple_bots.karen import karen_bot
    client = ckit_client.FlexusClient("karen_install")
    asyncio.run(install(client, bot_name=karen_bot.BOT_NAME, bot_version=karen_bot.BOT_VERSION, tools=karen_bot.TOOLS))
