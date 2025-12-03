import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots import prompts_common
from flexus_simple_bots.rick import rick_bot, rick_prompts


BOT_DESCRIPTION = """
## Rick - The Deal King

A smart sales assistant that helps with lead generation, nurturing, and closing deals. Rick automatically monitors your CRM and sends personalized welcome emails to new contacts.

**Key Features:**
- **Automatic Welcome Emails**: Detects new CRM contacts and sends personalized welcome emails based on your templates
- **CRM Monitoring**: Watches for new contacts and tasks in real-time
- **Gmail Integration**: Seamlessly sends emails through your Gmail account
- **Policy-Based Templates**: Configure email templates and strategies using policy documents
- **Sales Pipeline Management**: Track and manage deals from lead to close

**Perfect for:**
- Sales teams looking to automate initial outreach
- Businesses that want consistent follow-up with new leads
- Teams using CRM systems who want intelligent email automation

Rick helps you never miss a new lead and ensures every contact gets a timely, personalized welcome!
"""


rick_setup_schema = [
    {
        "bs_name": "auto_welcome_email",
        "bs_type": "bool",
        "bs_default": True,
        "bs_group": "Automation",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Automatically send welcome emails to new CRM contacts without email tasks",
    },
]


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in rick_bot.TOOLS])
    pic_big = base64.b64encode(open(Path(__file__).with_name("rick-1024x1536.webp"), "rb").read()).decode("ascii")
    pic_small = base64.b64encode(open(Path(__file__).with_name("rick-256x256.webp"), "rb").read()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=rick_bot.BOT_NAME,
        marketable_version=rick_bot.BOT_VERSION,
        marketable_accent_color="#d9c093",
        marketable_title1="Rick",
        marketable_title2="The Deal King - Smart sales assistant for lead generation, nurturing, and closing deals.",
        marketable_author="Flexus",
        marketable_occupation="Sales Automation",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Sales",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.rick.rick_bot",
        marketable_setup_default=rick_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Check CRM status and help me set up welcome emails", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Show me recent contacts and their email status", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Rick, the Deal King. I monitor your CRM and automatically send personalized welcome emails to new contacts. How can I help you today?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=rick_prompts.rick_prompt_default,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
            )),
        ],
        marketable_tags=["Sales", "CRM", "Email", "Automation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m", "sched_first_question": "Sort inbox tasks according to priority and move them to todo."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Work on the assigned task."},
        ],
        marketable_forms={},
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("rick_install")
    asyncio.run(install(client, ws_id=args.ws))
