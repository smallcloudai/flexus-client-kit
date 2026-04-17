import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
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

TOOLS_SALES = {
    "flexus_policy_document", "mongo_store", "flexus_fetch_skill",
    "shopify_cart",
    "crm_contact_info", "verify_email",
    "email_reply",
    "magic_desk", "slack", "telegram", "discord",
} | ckit_cloudtool.KANBAN_PUBLIC | ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_MCP

TOOLS_POST_CONVERSATION = {
    "flexus_fetch_skill", "thread_read",
    "erp_table_meta", "erp_table_data", "erp_table_crud",
} | ckit_cloudtool.KANBAN_SAFE

TOOLS_NURTURING = {
    "flexus_policy_document", "mongo_store", "flexus_fetch_skill",
    "shopify_cart",
    "erp_table_meta", "erp_table_data", "erp_table_crud",
    "crm_contact_info",
    "email_send",
    "magic_desk", "slack", "telegram", "discord",
} | ckit_cloudtool.KANBAN_TRIAGE | ckit_cloudtool.CLOUDTOOLS_VECDB | ckit_cloudtool.CLOUDTOOLS_WEB | ckit_cloudtool.CLOUDTOOLS_MCP


SALES_DESC = (sales_bot.SALES_ROOTDIR / "README.md").read_text()


SALES_KERNEL = """
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
        fexp_description="Admin expert for pipeline setup, CRM management, contact import, and knowledge base configuration.",
        fexp_builtin_skills=ckit_skills.read_name_description(sales_bot.SALES_ROOTDIR, [
            "sales-pipeline-setup",
            "stall-deals",
            "welcome-email-setup",
        ]),
    )),
    ("messages_triage", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_TRIAGE,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(ckit_cloudtool.KANBAN_TRIAGE),
        fexp_nature="NATURE_NO_TASK",
        fexp_inactivity_timeout=0,
        fexp_model_class="cheap",
        fexp_description="Deals with messages in the inbox, picks relevant to work on.",
    )),
    ("very_limited", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_VERY_LIMITED,
        fexp_python_kernel=SALES_KERNEL,
        fexp_allow_tools=",".join(TOOLS_SALES),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_model_class="cheap",
        fexp_description="Customer-facing sales expert: qualifies leads with BANT, handles objections using C.L.O.S.E.R. framework, recommends products.",
    )),
    ("post_conversation", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_POST_CONVERSATION,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_POST_CONVERSATION),
        fexp_nature="NATURE_AUTONOMOUS",
        fexp_inactivity_timeout=300,
        fexp_model_class="cheap",
        fexp_description="Runs after sales conversations to log CRM activities, create/update contacts, and record BANT scores.",
    )),
    ("nurturing", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=sales_prompts.SALES_NURTURING,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOLS_NURTURING),
        fexp_nature="NATURE_SEMI_AUTONOMOUS",
        fexp_inactivity_timeout=600,
        fexp_description="Automated task executor: sends templated emails, follow-ups, stall deal recovery, and simple CRM operations.",
        fexp_model_class="cheap",
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
        marketable_accent_color="#2563EB",
        marketable_title1="Sales Assistant",
        marketable_title2="Consultative sales bot -- qualifies leads, handles objections, manages pipeline.",
        marketable_author="Flexus",
        marketable_occupation="Sales",
        marketable_description=SALES_DESC,
        marketable_typical_group="Sales",
        marketable_setup_default=sales_bot.SALES_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Set Up Sales Pipeline"},
            {"feat_question": "Set Up Welcome Emails"},
            {"feat_question": "Work on Stalled-Deal Strategy"},
            {"feat_question": "Connect Slack, Telegram, or Email"},
        ],
        marketable_intro_message="Hi! I'm your Sales Assistant. I qualify leads, handle objections, manage your CRM pipeline, and run follow-up automations. What would you like to work on?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=10_000_000,
        marketable_default_inbox_default=1_000_000,
        marketable_max_inprogress=10,
        marketable_experts=[(name, exp.filter_tools(sales_bot.TOOLS)) for name, exp in EXPERTS],
        marketable_tags=["Sales", "CRM", "Lead Qualification", "Pipeline", "Email", "Automation"],
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
        marketable_required_policydocs=["/company/summary", "/company/sales-strategy"],
        marketable_features=["magic_desk"],
        add_integrations_into_expert_system_prompt=sales_bot.SALES_INTEGRATIONS,
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("sales_install")
    asyncio.run(install(client))
