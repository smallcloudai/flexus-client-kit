import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit.integrations import fi_slack

from flexus_simple_bots import prompts_common
from flexus_simple_bots.profprobe import profprobe_bot, profprobe_prompts

BOT_DESCRIPTION = """
## Prof. Probe - Inquisitive Interviewer

Runs structured questionnaires via Slack or Flexus UI. Ask questions one by one, record responses, track progress.

**Features:**
- Asks one question at a time, conversational style
- Can use common messagers for interviews
- Can use external services, such as SurveyMonkey
- Saves structured responses for analysis

**Use cases:**
- User interviews
- Research surveys
- Feedback collection
- Any structured Q&A sessions
"""

profprobe_setup_schema = [
    {
        "bs_name": "use_surveymonkey",
        "bs_type": "bool",
        "bs_default": True,
        "bs_group": "Customization",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Use SurveyMonkey for automated surveys (if False, will conduct manual interviews via Slack)",
    },
    {
        "bs_name": "additional_instructions",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Customization",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Additional interview style preferences or custom instructions",
    },
    {
        "bs_name": "SURVEYMONKEY_ACCESS_TOKEN",
        "bs_type": "string_multiline",
        "bs_default": "",
        "bs_group": "Customization",
        "bs_order": 3,
        "bs_importance": 1,
        "bs_description": "SurveyMonkey OAuth 2.0 access token (requires surveys_write, surveys_read, collectors_write, collectors_read, responses_read_detail scopes)",
    },
]

profprobe_setup_schema += fi_slack.SLACK_SETUP_SCHEMA


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in profprobe_bot.TOOLS])
    with open(Path(__file__).with_name("profprobe-1024x1536.webp"), "rb") as f:
        pic_big = base64.b64encode(f.read()).decode("ascii")
    with open(Path(__file__).with_name("profprobe-256x256.webp"), "rb") as f:
        pic_small = base64.b64encode(f.read()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=profprobe_bot.BOT_NAME,
        marketable_version=profprobe_bot.BOT_VERSION,
        marketable_accent_color="#6B46C1",
        marketable_title1="Prof. Probe",
        marketable_title2="Your customer development interviewer. Run structured questionnaires via Slack or Flexus UI.",
        marketable_author="Flexus",
        marketable_occupation="Customer Development Interviewer",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Research / Interviews",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.profprobe.profprobe_bot",
        marketable_setup_default=profprobe_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Run a test questionnaire on me!", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Prof. Probe. I can help you run interviews with people, customer development or any other topic.",
        marketable_preferred_model_default="grok-4-fast-non-reasoning",
        marketable_daily_budget_default=150_000,
        marketable_default_inbox_default=15_000,
        marketable_expert_default=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="profprobe_default",
            fexp_system_prompt=profprobe_prompts.profprobe_prompt,
            fexp_python_kernel="",
            fexp_block_tools="*setup*",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_expert_setup=ckit_bot_install.FMarketplaceExpertInput(
            fexp_name="profprobe_setup",
            fexp_system_prompt=profprobe_prompts.profprobe_setup,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_app_capture_tools=bot_internal_tools,
        ),
        marketable_tags=["Interviews", "Customer Development"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M,
            prompts_common.SCHED_TODO_5M,
        ]
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("profprobe_install")
    asyncio.run(install(client, ws_id=args.ws))
