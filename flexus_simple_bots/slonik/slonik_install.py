import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots.slonik import slonik_bot
from flexus_simple_bots.slonik import slonik_prompts


TOOL_NAMESET = {t.name for t in slonik_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=slonik_prompts.slonik_prompt,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="PostgreSQL assistant that helps run queries, analyze data, and troubleshoot database connections using psql.",
    )),
]

async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=slonik_bot.SLONIK_ROOTDIR,
        marketable_accent_color="#336791",
        marketable_title1="Slonik",
        marketable_title2="Database assistant for PostgreSQL operations.",
        marketable_author="Flexus",
        marketable_occupation="Database Assistant",
        marketable_description="Database assistant that helps with PostgreSQL queries and data analysis.",
        marketable_typical_group="Admin Tools",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit",
        marketable_run_this="python -m flexus_simple_bots.slonik.slonik_bot",
        marketable_setup_default=slonik_bot.SLONIK_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Test whether database connection works", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Analyze database performance", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Help me write a SQL query", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hi! I'm Slonik, your PostgreSQL database assistant. I can help you run queries, analyze data, and optimize database performance.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(slonik_bot.TOOLS)) for name, exp in EXPERTS],
        marketable_tags=["database", "postgresql", "sql"],
        marketable_schedule=[]
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("slonik_install")
    asyncio.run(install(client))
