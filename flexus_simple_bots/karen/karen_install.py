import asyncio
import json
import base64

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.karen import karen_bot
from flexus_simple_bots.karen import karen_prompts


TOOLS_DEFAULT = {
    "flexus_policy_document", "mongo_store", "flexus_fetch_skill", "print_widget",
    "crm_automation", "flexus_schedule",
    "shopify", "shopify_cart",
    "erp_table_meta", "erp_table_data", "erp_table_crud", "erp_csv_import",
    "repo_reader", "support_collection_status", "explore_a_question",
    "slack", "telegram", "discord",
    "email_send", "email_setup_domain",
} | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT

TOOLS_EXPLORE = ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_WEB

TOOLS_SUPPORT_AND_SALES = {
    "flexus_policy_document", "mongo_store", "flexus_fetch_skill",
    "shopify_cart",
    "manage_crm_contact", "manage_crm_deal", "log_crm_activity", "verify_email",
    "email_reply",
    "magic_desk", "slack", "telegram", "discord",
} | ckit_cloudtool.CLOUDTOOLS_PUBLIC | ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_WEB | ckit_cloudtool.CLOUDTOOLS_MCP

TOOLS_NURTURING = {
    "flexus_policy_document", "mongo_store", "flexus_fetch_skill",
    "shopify_cart",
    "erp_table_meta", "erp_table_data", "erp_table_crud",
    "manage_crm_contact", "manage_crm_deal", "log_crm_activity",
    "email_send",
    "magic_desk", "slack", "telegram", "discord",
} | ckit_cloudtool.CLOUDTOOLS_TRIAGE | ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_WEB | ckit_cloudtool.CLOUDTOOLS_MCP


KAREN_DESC = (karen_bot.KAREN_ROOTDIR / "README.md").read_text()


KAREN_SUPPORT_AND_SALES_KERNEL = """
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
"""


KAREN_EXPLORE_KERNEL = """
steps = len([m for m in messages if m["role"] == "assistant"])
msg = messages[-1]
if msg["role"] == "assistant" and "EXPLORE_RESULT_READY" in str(msg["content"]):
    subchat_result = str(msg["content"])
elif steps >= 50:
    subchat_result = "Forced close after 50 steps. " + str(msg["content"])
elif steps >= 40 and msg["role"] == "assistant" and not msg["tool_calls"]:
    post_cd_instruction = "You have used 40+ steps. Wrap up NOW: write your final report with sourced findings and end with EXPLORE_RESULT_READY."
"""




EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.KAREN_DEFAULT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_DEFAULT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=3600,
        fexp_description="Marketing assistant for CRM management, contact import, automated outreach, company/product setup, and support knowledge base configuration.",
        fexp_builtin_skills=ckit_skills.read_name_description(karen_bot.KAREN_ROOTDIR, karen_bot.KAREN_SKILLS_DEFAULT),
    )),
    ("messages_triage", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.KAREN_DEAL_WITH_INBOX,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(ckit_cloudtool.CLOUDTOOLS_TRIAGE),    # no access to messengers
        fexp_nature="NATURE_NO_TASK",
        fexp_inactivity_timeout=0,
        fexp_model_class="cheap",
        fexp_description="Deals with messages in the inbox, picks relevant to work on.",
    )),
    ("very_limited", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.VERY_LIMITED,
        fexp_python_kernel=KAREN_SUPPORT_AND_SALES_KERNEL,
        fexp_allow_tools=",".join(TOOLS_SUPPORT_AND_SALES),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=3600,
        fexp_model_class="cheap",
        fexp_description="Customer-facing expert: answers support questions from knowledge base, conducts sales conversations using C.L.O.S.E.R. framework, qualifies leads with BANT.",
    )),
    ("nurturing", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.KAREN_NURTURING,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_NURTURING),
        fexp_nature="NATURE_SEMI_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_description="Lightweight expert for automated tasks: sending templated emails, follow-ups, stall deal recovery, and simple CRM operations.",
        fexp_model_class="cheap",
        fexp_builtin_skills=ckit_skills.read_name_description(karen_bot.KAREN_ROOTDIR, karen_bot.KAREN_SKILLS_NURTURING),
    )),
    ("explore", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=karen_prompts.EXPLORE_PROMPT,
        fexp_python_kernel=KAREN_EXPLORE_KERNEL,
        fexp_allow_tools=",".join(TOOLS_EXPLORE | ckit_cloudtool.CLOUDTOOLS_WEB),
        fexp_nature="NATURE_NO_TASK",
        fexp_description="Subchat expert for researching EDS and URLs, returns sourced findings.",
        fexp_subchat_only=True,
        fexp_model_class="cheap",
        fexp_activation_options=json.dumps({"no_policydoc_first_message": True}),
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((karen_bot.KAREN_ROOTDIR / "karen-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((karen_bot.KAREN_ROOTDIR / "karen-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#6252A4",
        marketable_title1="Karen",
        marketable_title2="Your 24/7 support, sales & marketing agent — empathetic, accurate, and always closing.",
        marketable_author="Flexus",
        marketable_occupation="Support, Sales & Marketing",
        marketable_description=KAREN_DESC,
        marketable_typical_group="Sales",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.karen.karen_bot",
        marketable_setup_default=karen_bot.KAREN_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Set Up Sales Pipeline"},
            {"feat_question": "Collect Support Knowledge Base"},
            {"feat_question": "Put Widget on My Landing Page"},
            {"feat_question": "Set Up Welcome Emails"},
            {"feat_question": "Work on Stalled-Deal Strategy"},
        ],
        marketable_intro_message="Hi! I'm Karen — your support, sales, and marketing assistant. I can answer customer questions, manage your CRM, run email automations, import contacts, and handle sales conversations. What would you like to work on?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=10_000_000,
        marketable_default_inbox_default=1_000_000,
        marketable_max_inprogress=10,
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Customer Support", "Sales", "Marketing", "CRM", "Email", "Automation", "Shopify", "E-commerce"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m", "sched_fexp_name": "messages_triage"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms={},
        marketable_auth_supported=["slack", "telegram", "discord_manual", "shopify", "resend"],
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
        marketable_required_policydocs=["/company/summary", "/company/sales-strategy", "/support/summary"],
        marketable_features=["magic_desk"],
    )


if __name__ == "__main__":
    client = ckit_client.FlexusClient("karen_install")
    asyncio.run(install(client, bot_name=karen_bot.BOT_NAME, bot_version=karen_bot.BOT_VERSION, tools=karen_bot.TOOLS))
