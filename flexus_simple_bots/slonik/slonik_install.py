import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots.slonik import slonik_prompts


SLONIK_ROOTDIR = Path(__file__).parent
SLONIK_SKILLS = ckit_skills.static_skills_find(SLONIK_ROOTDIR, shared_skills_allowlist="")
SLONIK_SETUP_SCHEMA = json.loads((SLONIK_ROOTDIR / "setup_schema.json").read_text())

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=slonik_prompts.slonik_prompt,
        fexp_python_kernel="",
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="PostgreSQL assistant that helps run queries, analyze data, and troubleshoot database connections using psql.",
    )),
]

async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((SLONIK_ROOTDIR / "slonik-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((SLONIK_ROOTDIR / "slonik-256x256.webp").read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#336791",
        marketable_title1="Slonik",
        marketable_title2="Database assistant for PostgreSQL operations.",
        marketable_author="Flexus",
        marketable_occupation="Database Assistant",
        marketable_description="Database assistant that helps with PostgreSQL queries and data analysis.",
        marketable_typical_group="Admin Tools",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.slonik.slonik_bot",
        marketable_setup_default=SLONIK_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Test whether database connection works", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Analyze database performance", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me write a SQL query", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Slonik, your PostgreSQL database assistant. I can help you run queries, analyze data, and optimize database performance.",
        marketable_preferred_model_default="grok-code-fast-1",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["database", "postgresql", "sql"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[]
    )


if __name__ == "__main__":
    from flexus_simple_bots.slonik import slonik_bot
    client = ckit_client.FlexusClient("slonik_install")
    asyncio.run(install(client, bot_name=slonik_bot.BOT_NAME, bot_version=slonik_bot.BOT_VERSION, tools=slonik_bot.TOOLS))
