import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.owl import owl_bot, owl_prompts


BOT_DESCRIPTION = """
## Owl — Growth Strategist

Turns validated hypotheses into clean experiment designs using strict structured tools.

**7-step pipeline:**
1. Calibration — goals, budget, timeline
2. Diagnostic — hypothesis classification
3. Metrics — KPIs, stop/accelerate rules
4. Segment — ICP, JTBD, journey
5. Messaging — value prop, angles
6. Channels — channel selection, test cells
7. Tactics — campaigns, creatives, landing

**Architecture:**
- Single accumulating document per strategy
- Progress score (0-100) tracks completion
- Strict tools guarantee format, no retries
- Human-in-the-loop at every step

**Requires:** Hypothesis from Productman first.
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
    pic_big_path = Path(__file__).parent / "owl_strategist-1024x1536.webp"
    pic_small_path = Path(__file__).parent / "owl_strategist-256x256.webp"
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
        marketable_title1="Owl",
        marketable_title2="Growth Strategist — hypothesis to experiment design",
        marketable_author="Flexus",
        marketable_occupation="Growth Strategy",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.owl.owl_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Create strategy for my hypothesis", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Owl. I turn hypotheses into experiment designs. Let me check what's available...",
        marketable_preferred_model_default="gpt-4.1",
        marketable_daily_budget_default=500_000,
        marketable_default_inbox_default=50_000,
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_prompts.DEFAULT_PROMPT,
                fexp_python_kernel="",
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_tools_json,
            )),
        ],
        marketable_tags=["Marketing", "Strategy", "Growth"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[],
        marketable_forms={},
    )


if __name__ == "__main__":
    from flexus_simple_bots.owl import owl_bot
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("owl_install")
    asyncio.run(install(client, ws_id=args.ws, bot_name=owl_bot.BOT_NAME, bot_version=owl_bot.BOT_VERSION, tools=owl_bot.TOOLS))
