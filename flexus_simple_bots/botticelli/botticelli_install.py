import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.botticelli import botticelli_prompts


BOTTICELLI_ROOTDIR = Path(__file__).parent
BOTTICELLI_SKILLS = ckit_skills.static_skills_find(BOTTICELLI_ROOTDIR, shared_skills_allowlist="")
BOTTICELLI_SETUP_SCHEMA = json.loads((BOTTICELLI_ROOTDIR / "setup_schema.json").read_text())


BOT_DESCRIPTION = """
**Job description**
Botticelli is an AI Creative Director who turns brand inputs into high-converting Meta ad creatives — without a design team. Point him at a website and he pulls the brand automatically: colors, fonts, logo, visual style. From there, he generates three distinct creative variations per brief, each built around a specific psychological trigger and optimized for the platform format you need. Every creative comes with copy, strategic rationale, and production-ready image files. Fast when you need speed. Precise when quality is the priority.

**How Botticelli can help you:**
- Scans any website to extract brand colors, fonts, logo, and visual identity automatically
- Generates 3 creative variations per brief, each optimized with a different cognitive bias (Social Proof, Scarcity, Authority, Anchoring, and more)
- Produces hyper-specific image generation prompts (200–300 words) for pixel-accurate results
- Writes complete ad copy for every variation — Primary Text, Headline, and Description
- Supports all Meta ad formats: Square (1:1), Portrait (4:5), Landscape (16:9), Stories (9:16)
- Runs two image generation backends — Nano Banana (Google Gemini) for speed and native aspect ratios, DALL-E 3 for high-quality output
- Handles image cropping and WebP optimization so creatives are ready to upload
- Explains the strategic rationale behind each variation so performance teams know what they're testing and why
"""


BOTTICELLI_DEFAULT_LARK = ""

# Lark kernel for meta_ads_creative skill - returns subchat result
# See AGENTS.md: outputs are "subchat_result", "post_cd_instruction", "error", "kill_tools"
META_ADS_LARK_KERNEL = """
msg = messages[-1]
if msg["role"] == "assistant" and len(msg.get("tool_calls", [])) == 0:
    # Subchat completed with no tool calls - return the content to parent
    subchat_result = msg.get("content", "Creative generation completed.")
"""


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=botticelli_prompts.botticelli_prompt,
        fexp_python_kernel=BOTTICELLI_DEFAULT_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Creates ad campaign pictures using style guides. Manages company style guides and generates images with picturegen().",
    )),
    ("meta_ads_creative", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=botticelli_prompts.meta_ads_creative_prompt,
        fexp_python_kernel=META_ADS_LARK_KERNEL,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((BOTTICELLI_ROOTDIR / "botticelli-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((BOTTICELLI_ROOTDIR / "botticelli-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#49cdc2",
        marketable_title1="Botticelli",
        marketable_title2="I create high-converting Meta Ads creatives with cognitive bias optimization",
        marketable_author="Flexus",
        marketable_occupation="Meta Ads Creative Director",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.botticelli.botticelli_bot",
        marketable_setup_default=BOTTICELLI_SETUP_SCHEMA,
        marketable_featured_actions=[],
        marketable_intro_message="Hello, I am Botticelli. I create high-converting Meta Ads creatives optimized with cognitive biases. Ready to generate stunning FB/IG ad campaigns?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Marketing", "Ads", "Creative", "Meta", "Facebook", "Instagram"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m"},
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.botticelli import botticelli_bot
    client = ckit_client.FlexusClient("botticelli_install")
    asyncio.run(install(client, bot_name=botticelli_bot.BOT_NAME, bot_version=botticelli_bot.BOT_VERSION, tools=botticelli_bot.TOOLS))
