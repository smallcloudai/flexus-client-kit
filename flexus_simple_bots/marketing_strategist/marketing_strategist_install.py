"""
Marketing Strategist Installation

Registers the bot and all its skills in Flexus marketplace.

Key differences from legacy orchestrator pattern:
- All skills have fexp_ui_hidden=False (visible for direct access)
- No orchestrator tools in default skill
- Each skill has UI presentation fields (title, icon, first_message)
- Each skill declares SKILL_TOOLS, resolved via get_tools_for_skill()

Tool Architecture:
- Skills declare SKILL_TOOLS = ["pdoc", ...] -- list of tool names
- install.py calls get_tools_for_skill() to resolve to actual tool objects
- This enables per-skill tool access control
"""

import asyncio
import json
import base64
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.marketing_strategist import marketing_strategist_bot
from flexus_simple_bots.marketing_strategist import marketing_strategist_prompts
from flexus_simple_bots.marketing_strategist.skills import diagnostic as skill_diagnostic
from flexus_simple_bots.marketing_strategist.skills import metrics as skill_metrics
from flexus_simple_bots.marketing_strategist.skills import segment as skill_segment
from flexus_simple_bots.marketing_strategist.skills import messaging as skill_messaging
from flexus_simple_bots.marketing_strategist.skills import channels as skill_channels
from flexus_simple_bots.marketing_strategist.skills import tactics as skill_tactics
from flexus_simple_bots.marketing_strategist.skills import compliance as skill_compliance


# Default tools for free-talk skill (uses all common tools)
DEFAULT_SKILL_TOOLS = ["pdoc"]


def _tools_json_for_skill(skill_tools: List[str]) -> str:
    """Convert skill's SKILL_TOOLS list to JSON for fexp_app_capture_tools."""
    tools = marketing_strategist_bot.get_tools_for_skill(skill_tools)
    return json.dumps([t.openai_style_tool() for t in tools])


BOT_DESCRIPTION = """
## Marketing Strategist -- AI Marketing Strategy Expert

Expert bot for hypothesis validation and go-to-market strategy creation.

**7 specialized skills accessible directly:**
- Diagnostic Analysis -- classify hypothesis, identify unknowns
- Metrics & KPIs -- define success metrics, stop/accelerate rules
- Segment Analysis -- ICP, JTBD, customer journey
- Messaging Strategy -- value proposition, angles, objections
- Channel Strategy -- channel selection, test cell design
- Tactical Specs -- campaign briefs, creatives, landing pages
- Risk & Compliance -- policy check, privacy, risk assessment

**New Architecture:**
Each skill is accessible directly via UI button. No orchestrator overhead.
Start a chat with the skill you need, get focused expertise.

**Who it's for:**
- Startups at validation stage
- Product managers exploring new markets
- Marketers planning experiments
"""


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list,
):
    """
    Install Marketing Strategist bot to marketplace.

    All skills are registered with fexp_ui_hidden=False for direct UI access.
    Each skill gets tools based on its SKILL_TOOLS declaration.
    """
    # Tools JSON for default skill
    default_tools_json = _tools_json_for_skill(DEFAULT_SKILL_TOOLS)

    # Load bot pictures if available
    pic_big = None
    pic_small = None
    pic_big_path = Path(__file__).with_name("marketing_strategist-1024x1536.webp")
    pic_small_path = Path(__file__).with_name("marketing_strategist-256x256.webp")
    if pic_big_path.exists():
        pic_big = base64.b64encode(pic_big_path.read_bytes()).decode("ascii")
    if pic_small_path.exists():
        pic_small = base64.b64encode(pic_small_path.read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#2E86AB",  # Professional blue
        marketable_title1="Marketing Strategist",
        marketable_title2="AI expert for marketing strategies and hypothesis validation",
        marketable_author="Flexus",
        marketable_occupation="Marketing Strategist",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.marketing_strategist.marketing_strategist_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {
                "feat_question": "Help me validate my hypothesis",
                "feat_run_as_setup": False,
                "feat_depends_on_setup": [],
            },
            {
                "feat_question": "Create a marketing strategy for my product",
                "feat_run_as_setup": False,
                "feat_depends_on_setup": [],
            },
        ],
        marketable_intro_message=(
            "Hi! I'm Marketing Strategist. I help founders validate hypotheses "
            "and create marketing strategies. Choose a skill to get started, "
            "or just tell me about your product."
        ),
        marketable_preferred_model_default="gpt-5.1",
        marketable_daily_budget_default=500_000,
        marketable_default_inbox_default=50_000,
        marketable_experts=[
            # Default skill: free-talk mode (not hidden but not prominent)
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=marketing_strategist_prompts.DEFAULT_PROMPT,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=default_tools_json,
                fexp_ui_hidden=False,
                fexp_ui_title="Free Talk",
                fexp_ui_icon="pi pi-comments",
                fexp_ui_first_message="How can I help with your marketing strategy?",
                fexp_ui_description="Open conversation about marketing strategy",
                fexp_description="Open conversation about marketing strategy without structured workflow.",
            )),
            # Skill 1: Diagnostic Analysis
            ("diagnostic", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_diagnostic.SYSTEM_PROMPT,
                fexp_python_kernel=skill_diagnostic.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_diagnostic.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_diagnostic.SKILL_UI_TITLE,
                fexp_ui_icon=skill_diagnostic.SKILL_UI_ICON,
                fexp_ui_first_message=skill_diagnostic.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_diagnostic.SKILL_UI_DESCRIPTION,
                fexp_description="Classifies hypothesis type, identifies key unknowns, and assesses feasibility for traffic testing.",
            )),
            # Skill 2: Metrics & KPIs
            ("metrics", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_metrics.SYSTEM_PROMPT,
                fexp_python_kernel=skill_metrics.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_metrics.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_metrics.SKILL_UI_TITLE,
                fexp_ui_icon=skill_metrics.SKILL_UI_ICON,
                fexp_ui_first_message=skill_metrics.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_metrics.SKILL_UI_DESCRIPTION,
                fexp_description="Defines success metrics, calculates minimum sample sizes, and sets stop/accelerate rules for experiments.",
            )),
            # Skill 3: Segment Analysis
            ("segment", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_segment.SYSTEM_PROMPT,
                fexp_python_kernel=skill_segment.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_segment.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_segment.SKILL_UI_TITLE,
                fexp_ui_icon=skill_segment.SKILL_UI_ICON,
                fexp_ui_first_message=skill_segment.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_segment.SKILL_UI_DESCRIPTION,
                fexp_description="Defines ideal customer profile, maps jobs-to-be-done, and analyzes customer journey and discovery channels.",
            )),
            # Skill 4: Messaging Strategy
            ("messaging", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_messaging.SYSTEM_PROMPT,
                fexp_python_kernel=skill_messaging.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_messaging.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_messaging.SKILL_UI_TITLE,
                fexp_ui_icon=skill_messaging.SKILL_UI_ICON,
                fexp_ui_first_message=skill_messaging.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_messaging.SKILL_UI_DESCRIPTION,
                fexp_description="Crafts value propositions, defines testable messaging angles, and prepares objection handling strategies.",
            )),
            # Skill 5: Channel Strategy
            ("channels", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_channels.SYSTEM_PROMPT,
                fexp_python_kernel=skill_channels.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_channels.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_channels.SKILL_UI_TITLE,
                fexp_ui_icon=skill_channels.SKILL_UI_ICON,
                fexp_ui_first_message=skill_channels.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_channels.SKILL_UI_DESCRIPTION,
                fexp_description="Selects marketing channels, designs test cell structure, and allocates budget across experiments.",
            )),
            # Skill 6: Tactical Specs
            ("tactics", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_tactics.SYSTEM_PROMPT,
                fexp_python_kernel=skill_tactics.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_tactics.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_tactics.SKILL_UI_TITLE,
                fexp_ui_icon=skill_tactics.SKILL_UI_ICON,
                fexp_ui_first_message=skill_tactics.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_tactics.SKILL_UI_DESCRIPTION,
                fexp_description="Creates detailed campaign specs, creative briefs, landing page structure, and tracking requirements.",
            )),
            # Skill 7: Risk & Compliance
            ("compliance", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_compliance.SYSTEM_PROMPT,
                fexp_python_kernel=skill_compliance.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=_tools_json_for_skill(skill_compliance.SKILL_TOOLS),
                fexp_ui_hidden=False,
                fexp_ui_title=skill_compliance.SKILL_UI_TITLE,
                fexp_ui_icon=skill_compliance.SKILL_UI_ICON,
                fexp_ui_first_message=skill_compliance.SKILL_UI_FIRST_MESSAGE,
                fexp_ui_description=skill_compliance.SKILL_UI_DESCRIPTION,
                fexp_description="Checks ad platform policies, assesses business and statistical risks, and verifies privacy compliance.",
            )),
        ],
        marketable_tags=["Marketing", "Strategy", "Hypothesis Validation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.marketing_strategist import marketing_strategist_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("marketing_strategist_install")
    asyncio.run(install(
        client,
        ws_id=args.ws,
        bot_name=marketing_strategist_bot.BOT_NAME,
        bot_version=marketing_strategist_bot.BOT_VERSION,
        tools=marketing_strategist_bot.TOOLS,
    ))
