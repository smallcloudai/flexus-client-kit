import asyncio
import json
import base64
import io
from pathlib import Path
from typing import List

from PIL import Image

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.lawyerrat import lawyerrat_prompts


BOT_DESCRIPTION = """
## LawyerRat - Legal Research & Document Assistant

A thorough and diligent legal assistant bot that helps with legal research, document drafting, and contract analysis. LawyerRat combines professional legal expertise with persistent attention to detail.

**Key Features:**
- **Legal Research**: Conducts comprehensive research on legal topics and precedents
- **Document Drafting**: Creates professional legal documents and contracts
- **Contract Analysis**: Reviews agreements for potential issues and risks
- **Detail-Oriented**: Catches important clauses and potential problems
- **Customizable**: Adjust legal specialty and formality level to match your needs

**Perfect for:**
- Legal research and analysis
- Drafting standard legal documents
- Reviewing contracts and agreements
- Legal information gathering

**Important**: LawyerRat provides legal information and analysis, not legal advice. Always consult with a licensed attorney for actual legal advice.
"""


lawyerrat_setup_schema = [
    {
        "bs_name": "legal_specialty",
        "bs_type": "string_short",
        "bs_default": "general",
        "bs_group": "Legal Focus",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Primary legal specialty (general, corporate, contract, employment, intellectual-property, real-estate)",
    },
    {
        "bs_name": "formality_level",
        "bs_type": "string_short",
        "bs_default": "professional",
        "bs_group": "Communication",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Communication style (casual, professional, formal)",
    },
    {
        "bs_name": "citation_style",
        "bs_type": "string_short",
        "bs_default": "bluebook",
        "bs_group": "Legal Focus",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Preferred legal citation format (bluebook, alwd, universal)",
    },
    {
        "bs_name": "jurisdiction",
        "bs_type": "string_short",
        "bs_default": "US-Federal",
        "bs_group": "Legal Focus",
        "bs_order": 3,
        "bs_importance": 1,
        "bs_description": "Primary jurisdiction for legal research (e.g., US-Federal, US-CA, UK, EU)",
    },
    {
        "bs_name": "max_research_depth",
        "bs_type": "int",
        "bs_default": 3,
        "bs_group": "Research Settings",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Maximum depth for legal research (1-5, higher means more thorough)",
    },
]


LAWYERRAT_DEFAULT_LARK = f"""
print("LawyerRat processing %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    assistant_content = str(msg["content"])
    if "malpractice" in assistant_content.lower():
        post_cd_instruction = "Remember to include appropriate disclaimers about not providing legal advice!"
"""


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    bot_internal_tools = json.dumps([t.openai_style_tool() for t in tools])

    pic_big_path = Path(__file__).with_name("lawyerrat-1024x1536.webp")
    pic_small_path = Path(__file__).with_name("lawyerrat-256x256.webp")

    def create_placeholder_webp(width: int, height: int) -> str:
        img = Image.new('RGB', (width, height), color=(139, 69, 19))
        buf = io.BytesIO()
        img.save(buf, format='WEBP')
        return base64.b64encode(buf.getvalue()).decode("ascii")

    if pic_big_path.exists():
        pic_big = base64.b64encode(open(pic_big_path, "rb").read()).decode("ascii")
    else:
        pic_big = create_placeholder_webp(1024, 1536)
        print(f"Warning: {pic_big_path} not found, using placeholder")

    if pic_small_path.exists():
        pic_small = base64.b64encode(open(pic_small_path, "rb").read()).decode("ascii")
    else:
        pic_small = create_placeholder_webp(256, 256)
        print(f"Warning: {pic_small_path} not found, using placeholder")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="LawyerRat",
        marketable_title2="A thorough legal research and document assistant with meticulous attention to detail.",
        marketable_author="Flexus",
        marketable_occupation="Legal Research Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Legal / Professional",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.lawyerrat.lawyerrat_bot",
        marketable_setup_default=lawyerrat_setup_schema,
        marketable_featured_actions=[
            {"feat_question": "Research contract law basics", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Draft a simple NDA", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Analyze this agreement for potential issues", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hello! I'm LawyerRat, your thorough legal research assistant. I can help with legal research, document drafting, and contract analysis. What legal matter can I assist you with today? (Remember: I provide legal information, not legal advice - always consult a licensed attorney for actual legal advice.)",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.short_prompt,
                fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Main legal assistant for research, document drafting, and contract analysis with thorough attention to detail.",
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_setup,
                fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_internal_tools,
                fexp_description="Setup assistant that helps users configure the bot's legal specialty, formality level, and other preferences.",
            )),
        ],
        marketable_tags=["Legal", "Research", "Professional", "Documents"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:10m", "sched_first_question": "Look if there are any legal research tasks in inbox. If so, sort them by priority and complexity."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:5m", "sched_first_question": "Work on the assigned legal task with thorough attention to detail."},
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.lawyerrat import lawyerrat_bot
    client = ckit_client.FlexusClient("lawyerrat_install")
    asyncio.run(install(client, bot_name=lawyerrat_bot.BOT_NAME, bot_version=lawyerrat_bot.BOT_VERSION, tools=lawyerrat_bot.TOOLS))
