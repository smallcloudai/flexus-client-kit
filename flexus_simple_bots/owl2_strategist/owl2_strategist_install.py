import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.owl2_strategist import owl2_strategist_bot, owl2_strategist_prompts


BOT_DESCRIPTION = """
## Owl2 Strategist — AI Marketing Strategist (Strict Tools Edition)

Expert bot for hypothesis validation and go-to-market strategy creation using strict structured tool calls.

**7 analysis steps with strict schemas:**
- 🔍 Diagnostic — hypothesis classification, identifying unknowns
- 📊 Metrics — KPIs, stop-rules, MDE calculation
- 👥 Segment — ICP, JTBD, Customer Journey
- 💬 Messaging — value proposition, positioning
- 📡 Channels — channel selection, experiment design
- 🎯 Tactics — campaign specs, creatives, landing pages
- ⚖️ Compliance — risk assessment, platform policies

**Simplified Architecture:**
No subchats - all analysis generated directly via strict tool calls with OpenAI structured outputs.

**Human-in-the-Loop:**
Every step is discussed with you — no automation without your understanding and approval.

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
    bot_tools_json = json.dumps([t.openai_style_tool() for t in tools])

    pic_big = None
    pic_small = None
    pic_big_path = Path(__file__).with_name("owl_strategist-1024x1536.webp")
    pic_small_path = Path(__file__).with_name("owl_strategist-256x256.webp")
    if pic_big_path.exists():
        pic_big = base64.b64encode(pic_big_path.read_bytes()).decode("ascii")
    if pic_small_path.exists():
        pic_small = base64.b64encode(pic_small_path.read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Owl2 Strategist",
        marketable_title2="AI expert for marketing strategies using strict tool calls",
        marketable_author="Flexus",
        marketable_occupation="Marketing Strategist",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.owl2_strategist.owl2_strategist_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Help me create a strategy for my hypothesis", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Analyze my product idea", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Owl2 Strategist 🦉 I help founders validate hypotheses and create marketing strategies using direct structured outputs. Tell me about your product!",
        marketable_preferred_model_default="gpt-5.1",
        marketable_daily_budget_default=500_000,
        marketable_default_inbox_default=50_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl2_strategist_prompts.DEFAULT_PROMPT,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_tools_json,
            )),
        ],
        marketable_tags=["Marketing", "Strategy", "Hypothesis Validation", "Strict Tools"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
    )


if __name__ == "__main__":
    from flexus_simple_bots.owl2_strategist import owl2_strategist_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("owl2_strategist_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=owl2_strategist_bot.BOT_NAME, bot_version=owl2_strategist_bot.BOT_VERSION, tools=owl2_strategist_bot.TOOLS))
