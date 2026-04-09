import asyncio
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.researcher import researcher_bot
from flexus_simple_bots.researcher import researcher_prompts


TOOL_NAMESET = {t.name for t in researcher_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=researcher_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="GTM Research operator - discovery recruitment, interview capture, alternatives mapping, WTP research, search signals, firmographics, ICP scoring, and contact enrichment.",
        fexp_builtin_skills=ckit_skills.read_name_description(researcher_bot.RESEARCHER_ROOTDIR, researcher_bot.RESEARCHER_SKILLS),
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=researcher_bot.RESEARCHER_ROOTDIR,
        marketable_accent_color="#0F766E",
        marketable_title1="Researcher",
        marketable_title2="GTM Research - signals, discovery, validation",
        marketable_author="Flexus",
        marketable_occupation="GTM Research Operator",
        marketable_description=(
            "Consolidates customer discovery, alternatives and pricing research, "
            "search signal analysis, segment profiling, ICP scoring, and contact enrichment "
            "into a single research operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Research",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.researcher.researcher_bot",
        marketable_setup_default=researcher_bot.RESEARCHER_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Recruit qualified participants for discovery interviews", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Map buyer alternatives and switching triggers from evidence", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Enrich and score target accounts and contacts before outreach", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Researcher. Load a skill to activate a workflow: discovery-recruitment, discovery-interview-capture, pain-alternatives-landscape, pain-wtp-research, signal-search-seo, segment-firmographic, segment-icp-scoring, or pipeline-contact-enrichment.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(researcher_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=researcher_bot.RESEARCHER_INTEGRATIONS,
        marketable_tags=["GTM", "Research", "Discovery", "Signals", "ICP"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_forms={},
        marketable_auth_supported=["linkedin", "google"],
        marketable_auth_scopes={
            "linkedin": ["r_profile_basicinfo", "email", "w_member_social"],
            "google": [],
        },
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("researcher_install")
    asyncio.run(install(client))
