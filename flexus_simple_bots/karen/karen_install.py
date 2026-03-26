import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_mcp

from flexus_simple_bots import prompts_common
from flexus_simple_bots.karen import karen_prompts


KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.static_skills_find(KAREN_ROOTDIR, shared_skills_allowlist="setting-up-external-knowledge-base")
KAREN_MCPS = []
KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += fi_discord2.DISCORD_SETUP_SCHEMA
KAREN_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(KAREN_MCPS))

KAREN_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    KAREN_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "slack",
        "telegram",
        "discord",
        "skills",
        "magic_desk",
    ],
    builtin_skills=KAREN_SKILLS,
)


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


KAREN_BUDGET_KERNEL = """
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

KAREN_VERY_LIMITED_KERNEL = """
captured = False
warn1_text = "You have not captured any chat or thread. No one can see your messages. Capture something and repeat whatever you are trying to say. Disregard if you are just thinking aloud."
warn1_have = False
warn2_text = "The token budget is running low. Close the current task with a good summary, the next message will go to kanban inbox, your previous summary will be visible to you."
warn2_have = False

for msg in messages:
    s = str(msg["content"])
    if "📌CAPTURED" in s:
        captured = True
    if warn1_text in s:
        warn1_have = True
    if warn2_text in s:
        warn2_have = True

post_cd_instruction = ""
if not messages[-1]["tool_calls"]:
    if not captured and not warn1_have and messages[-1]["role"] == "assistant":
        post_cd_instruction = warn1_text
    elif not warn2_have and coins > budget * 0.5 and not messages[-1]["tool_calls"]:
        post_cd_instruction = warn2_text

# print("warn1_have", warn1_have)
# print("warn2_have", warn2_have)
# print("post_cd_instruction", post_cd_instruction)
"""


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.karen_setup,
        fexp_python_kernel=KAREN_BUDGET_KERNEL,
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_inactivity_timeout=3600,
        fexp_description="Flexus expert: triages inbox, has a full access to kanban and setup tools.",
        fexp_builtin_skills=ckit_skills.read_name_description(KAREN_ROOTDIR, KAREN_SKILLS),
    )),
    ("very_limited", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.very_limited,
        fexp_python_kernel=KAREN_VERY_LIMITED_KERNEL,
        fexp_block_tools="",
        fexp_allow_tools="slack,telegram,discord,magic_desk,flexus_bot_kanban,flexus_vector_search,flexus_read_original",
        fexp_inactivity_timeout=600,
        fexp_description="Customer-facing worker: captures messenger threads, searches knowledge base, responds to users. No access potentially dangerous tools.",
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
        marketable_accent_color="#524214",
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
            {"feat_question": "Collect/improve company info"},
            {"feat_question": "What people asked today?"},
        ],
        marketable_intro_message="I'm here for your customers 24/7 — answering questions, remembering every detail, and always following up. I also deliver weekly feedback reports that help your team improve the product.",
        marketable_preferred_model_default="gpt-5.4-nano",
        marketable_max_inprogress=10,
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=KAREN_INTEGRATIONS,
        marketable_tags=["Customer Support"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m", "sched_fexp_name": "very_limited"},
        ],
        marketable_required_policydocs=[
            "/company/summary",
            "/support/summary",
        ],
        marketable_auth_supported=["slack", "telegram", "discord_manual"],
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
        marketable_features=["magic_desk"],
    )


if __name__ == "__main__":
    from flexus_simple_bots.karen import karen_bot
    client = ckit_client.FlexusClient("karen_install")
    asyncio.run(install(client, bot_name=karen_bot.BOT_NAME, bot_version=karen_bot.BOT_VERSION, tools=karen_bot.TOOLS))
