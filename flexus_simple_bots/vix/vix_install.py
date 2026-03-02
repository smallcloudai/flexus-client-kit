import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_shopify

from flexus_simple_bots import prompts_common
from flexus_simple_bots.vix import vix_prompts


VIX_ROOTDIR = Path(__file__).parent
VIX_SKILLS = ckit_skills.static_skills_find(VIX_ROOTDIR, shared_skills_allowlist="")


BOT_DESCRIPTION = """
**Job description**
Vix is an integrated sales and marketing agent who covers the full revenue cycle — from first contact to closed deal. She manages your CRM, runs outreach through Gmail, nurtures leads with automated follow-ups, and sells consultatively using the C.L.O.S.E.R. framework. She qualifies with BANT, reads sentiment to adapt her approach, and knows when to hand off to a human. Whether you need marketing operations, active selling, or steady lead nurturing, Vix switches modes to match the job.

**How Vix can help you:**

*Marketing:*
- Manages your CRM and imports contacts from CSV files or landing pages
- Sends automatic welcome emails to new contacts the moment they come in
- Runs outreach campaigns through Gmail integration
- Builds CRM automations with custom triggers and actions
- Handles company and product setup so your CRM reflects your actual business

*Sales:*
- Sells consultatively using the C.L.O.S.E.R. Framework
- Qualifies leads with BANT (Budget, Authority, Need, Timeline)
- Detects sentiment in conversations and adapts her approach accordingly
- Executes smart handoffs to human agents when the moment calls for it

*Nurturing:*
- Runs lightweight automated tasks to keep leads warm between touchpoints
- Sends emails using pre-built templates for consistent, on-brand communication
- Triggers follow-ups based on CRM activity so no lead goes cold by accident

*Shopify (optional):*
- Connects your Shopify store and syncs products, orders, and payments automatically
- Creates draft orders with checkout links directly from conversations
"""


VIX_SETUP_SCHEMA = json.loads((VIX_ROOTDIR / "setup_schema.json").read_text())
VIX_SETUP_SCHEMA += fi_shopify.SHOPIFY_SETUP_SCHEMA + fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA + fi_resend.RESEND_SETUP_SCHEMA


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=vix_prompts.vix_prompt_marketing,
        fexp_python_kernel="",
        fexp_block_tools="shopify_cart",
        fexp_allow_tools="",
        fexp_inactivity_timeout=3600,
        fexp_description="Marketing assistant for CRM management, contact import, automated outreach, and company/product setup.",
    )),
    ("sales", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=vix_prompts.vix_prompt_sales,
        fexp_python_kernel="",
        fexp_block_tools="crm_automation,shopify,*setup",
        fexp_allow_tools="",
        fexp_inactivity_timeout=3600,
        fexp_description="Conducts sales conversations using C.L.O.S.E.R. Framework, qualifies leads with BANT, and handles objections with consultative approach.",
    )),
    ("nurturing", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=vix_prompts.vix_prompt_nurturing,
        fexp_python_kernel="",
        fexp_block_tools="crm_automation,shopify,*setup",
        fexp_allow_tools="",
        fexp_inactivity_timeout=600,
        fexp_description="Lightweight expert for automated tasks: sending templated emails, follow-ups, and simple CRM operations.",
        fexp_preferred_model_default="grok-4-1-fast-non-reasoning",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((VIX_ROOTDIR / "vix-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((VIX_ROOTDIR / "vix-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#645ff6",
        marketable_title1="Vix",
        marketable_title2="Sales & Marketing Agent - CRM, automations, and consultative selling with C.L.O.S.E.R. Framework.",
        marketable_author="Flexus",
        marketable_occupation="Sales & Marketing",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Sales",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.vix.vix_bot",
        marketable_setup_default=VIX_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Help me set up my company and sales pipeline", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me send contacts from my landing page to Flexus", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me set up welcome emails to new contacts", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Vix, your sales and marketing assistant. I can help with CRM management, email automations, contact imports, and sales conversations. What would you like to work on?",
        marketable_preferred_model_default="claude-opus-4-5-20251101",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Sales", "Marketing", "CRM", "Email", "Automation", "Shopify", "E-commerce"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:1m", "sched_fexp_name": "nurturing"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:1m"},
        ],
        marketable_forms={},
        marketable_auth_supported=["telegram", "shopify"],
        marketable_required_policydocs=["/company/summary", "/company/sales-strategy"],
    )


if __name__ == "__main__":
    from flexus_simple_bots.vix import vix_bot
    client = ckit_client.FlexusClient("vix_install")
    asyncio.run(install(client, bot_name=vix_bot.BOT_NAME, bot_version=vix_bot.BOT_VERSION, tools=vix_bot.TOOLS))
