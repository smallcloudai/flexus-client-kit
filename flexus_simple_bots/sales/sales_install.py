import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots.sales import sales_bot
from flexus_simple_bots.sales import sales_prompts


TOOLS_DEFAULT = {
    "flexus_policy_document",
    "mongo_store",
    "flexus_fetch_skill",
    "print_widget",
    "crm_automation",
    "flexus_schedule",
    "shopify",
    "shopify_cart",
    "erp_table_meta",
    "erp_table_data",
    "erp_table_crud",
    "erp_csv_import",
    "slack",
    "telegram",
    "discord",
    "email_send",
    "email_setup_domain",
} | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT

TOOLS_VERY_LIMITED = {
    "flexus_policy_document",
    "mongo_store",
    "flexus_fetch_skill",
    "shopify_cart",
    "crm_contact_info",
    "verify_email",
    "email_reply",
    "magic_desk",
    "slack",
    "telegram",
    "discord",
} | ckit_cloudtool.KANBAN_PUBLIC | ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_MCP

TOOLS_POST_CONVERSATION = {
    "flexus_fetch_skill",
    "thread_read",
    "erp_table_meta",
    "erp_table_data",
    "erp_table_crud",
} | ckit_cloudtool.KANBAN_SAFE

# Kernel for very_limited: warn if bot hasn't captured anything after responding
SALES_VERY_LIMITED_KERNEL = """
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


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_DEFAULT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_DEFAULT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=3600,
        fexp_description="Admin expert: CRM pipeline management, deal setup, Shopify, knowledge base configuration, and automation rules.",
        fexp_builtin_skills=ckit_skills.read_name_description(sales_bot.SALES_ROOTDIR, [
            "sales-pipeline-setup",
            "stall-deals",
            "welcome-email-setup",
        ]),
    )),
    ("very_limited", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_VERY_LIMITED,
        fexp_python_kernel=SALES_VERY_LIMITED_KERNEL,
        fexp_allow_tools=",".join(TOOLS_VERY_LIMITED),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_model_class="cheap",
        fexp_description="Customer-facing expert: consultative sales conversations using C.L.O.S.E.R. framework, BANT qualification, vector-search grounded answers.",
    )),
    ("post_conversation", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_POST_CONVERSATION,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_POST_CONVERSATION),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=300,
        fexp_model_class="cheap",
        fexp_description="Runs after sales conversations: logs CRM activities, creates/updates contacts, records BANT scores, advances deal stages.",
        fexp_builtin_skills=ckit_skills.read_name_description(sales_bot.SALES_ROOTDIR, [
            "stall-recovery",
        ]),
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=sales_bot.SALES_ROOTDIR,
        marketable_accent_color="#1D6F42",
        marketable_title1="Sales",
        marketable_title2="Your consultative sales agent — qualifies leads, manages pipeline, and closes.",
        marketable_author="Flexus",
        marketable_occupation="Sales",
        marketable_description="Handles inbound sales conversations using the C.L.O.S.E.R. framework, qualifies leads with BANT, manages your CRM pipeline, and runs automated follow-ups.",
        marketable_typical_group="Sales",
        marketable_setup_default=sales_bot.SALES_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Set Up Sales Pipeline"},
            {"feat_question": "Set Up Stall Deal Recovery"},
            {"feat_question": "Set Up Welcome Email"},
            {"feat_question": "Connect Telegram or Slack"},
        ],
        marketable_intro_message="Hi! I'm Sales — your consultative sales assistant. I can handle inbound sales conversations, qualify leads, manage your CRM pipeline, and run follow-up automations. What would you like to work on?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=10_000_000,
        marketable_default_inbox_default=1_000_000,
        marketable_max_inprogress=10,
        marketable_experts=[(name, exp.filter_tools(sales_bot.TOOLS)) for name, exp in EXPERTS],
        marketable_tags=["Sales", "CRM", "Lead Qualification", "Pipeline", "BANT", "CLOSER"],
        marketable_schedule=[],
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
        marketable_required_policydocs=["/company/summary", "/company/sales-strategy"],
        marketable_features=["magic_desk"],
        add_integrations_into_expert_system_prompt=sales_bot.SALES_INTEGRATIONS,
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("sales_install")
    asyncio.run(install(client))
