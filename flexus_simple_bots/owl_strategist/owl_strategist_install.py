import asyncio
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots.owl_strategist import owl_strategist_prompts
from flexus_simple_bots.owl_strategist.skills import diagnostic as skill_diagnostic
from flexus_simple_bots.owl_strategist.skills import metrics as skill_metrics
from flexus_simple_bots.owl_strategist.skills import segment as skill_segment
from flexus_simple_bots.owl_strategist.skills import messaging as skill_messaging
from flexus_simple_bots.owl_strategist.skills import channels as skill_channels
from flexus_simple_bots.owl_strategist.skills import tactics as skill_tactics
from flexus_simple_bots.owl_strategist.skills import compliance as skill_compliance


OWL_STRATEGIST_ROOTDIR = Path(__file__).parent
OWL_STRATEGIST_SKILLS = ckit_skills.skill_find_all(OWL_STRATEGIST_ROOTDIR, shared_skills_allowlist="")

BOT_DESCRIPTION = """
## Owl Strategist — AI Marketing Strategist

Expert bot for hypothesis validation and go-to-market strategy creation.

**7 specialized agents:**
- 🔍 Diagnostic — hypothesis classification, identifying unknowns
- 📊 Metrics — KPIs, stop-rules, MDE calculation
- 👥 Segment — ICP, JTBD, Customer Journey
- 💬 Messaging — value proposition, positioning
- 📡 Channels — channel selection, experiment design
- 🎯 Tactics — campaign specs, creatives, landing pages
- ⚖️ Compliance — risk assessment, platform policies

**Human-in-the-Loop:**
Every step is discussed with you — no automation without your understanding and approval.

**Who it's for:**
- Startups at validation stage
- Product managers exploring new markets
- Marketers planning experiments
"""

# Agents only need flexus_policy_document, block orchestrator tools
AGENT_BLOCK_TOOLS = "save_input,run_agent,rerun_agent,get_pipeline_status,*setup*"

EXPERTS = [
    # Orchestrator — talks to human, manages pipeline
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=owl_strategist_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
    )),
    # Agent A: Diagnostic — classify hypothesis, identify unknowns
    ("diagnostic", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_diagnostic.SYSTEM_PROMPT,
        fexp_python_kernel=skill_diagnostic.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent G: Metrics — KPI, MDE, stop/accelerate rules
    ("metrics", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_metrics.SYSTEM_PROMPT,
        fexp_python_kernel=skill_metrics.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent B: Segment — ICP, JTBD, customer journey
    ("segment", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_segment.SYSTEM_PROMPT,
        fexp_python_kernel=skill_segment.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent C: Messaging — value prop, angles, objections
    ("messaging", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_messaging.SYSTEM_PROMPT,
        fexp_python_kernel=skill_messaging.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent D: Channels — channel selection, test cells, budget
    ("channels", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_channels.SYSTEM_PROMPT,
        fexp_python_kernel=skill_channels.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent E: Tactics — campaigns, creatives, landing, tracking
    ("tactics", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_tactics.SYSTEM_PROMPT,
        fexp_python_kernel=skill_tactics.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
    # Agent F: Compliance — risks, ads policies, privacy
    ("compliance", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=skill_compliance.SYSTEM_PROMPT,
        fexp_python_kernel=skill_compliance.LARK_KERNEL,
        fexp_block_tools=AGENT_BLOCK_TOOLS,
        fexp_allow_tools="",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((OWL_STRATEGIST_ROOTDIR / "owl_strategist-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((OWL_STRATEGIST_ROOTDIR / "owl_strategist-256x256.webp").read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Owl Strategist",
        marketable_title2="AI expert for marketing strategies and hypothesis validation",
        marketable_author="Flexus",
        marketable_occupation="Marketing Strategist",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.owl_strategist.owl_strategist_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Help me create a strategy for my hypothesis", "feat_depends_on_setup": [], "feat_expert": "default"},
            {"feat_question": "Analyze my product idea", "feat_depends_on_setup": [], "feat_expert": "default"},
        ],
        marketable_intro_message="Hi! I'm Owl Strategist 🦉 I help founders validate hypotheses and create marketing strategies. Tell me about your product — what do you want to test?",
        marketable_preferred_model_default="gpt-5.1",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Marketing", "Strategy", "Hypothesis Validation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.owl_strategist import owl_strategist_bot
    client = ckit_client.FlexusClient("owl_strategist_install")
    asyncio.run(install(client, bot_name=owl_strategist_bot.BOT_NAME, bot_version=owl_strategist_bot.BOT_VERSION, tools=owl_strategist_bot.TOOLS))
