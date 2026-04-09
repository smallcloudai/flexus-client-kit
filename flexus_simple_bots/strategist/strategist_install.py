import asyncio
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.strategist import strategist_bot
from flexus_simple_bots.strategist import strategist_prompts

TOOL_NAMESET = {t.name for t in strategist_bot.TOOLS}

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=strategist_prompts.DEFAULT_PROMPT,
        fexp_python_kernel="",
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_description="GTM Strategy operator — hypothesis design, channel strategy, MVP scoping, validation criteria, positioning, messaging, offer design, and pricing decisions.",
        fexp_builtin_skills=ckit_skills.read_name_description(strategist_bot.STRATEGIST_ROOTDIR, strategist_bot.STRATEGIST_SKILLS),
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=strategist_bot.STRATEGIST_ROOTDIR,
        marketable_accent_color="#8B4513",
        marketable_title1="Strategist",
        marketable_title2="GTM Strategy — from hypothesis to experiment to launch",
        marketable_author="Flexus",
        marketable_occupation="GTM Strategy Operator",
        marketable_description=(
            "Consolidates hypothesis design, channel strategy, MVP scoping, "
            "positioning, messaging, offer architecture, and pricing decisions "
            "into a single strategy operator. Load a skill to activate the relevant workflow."
        ),
        marketable_typical_group="GTM / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.strategist.strategist_bot",
        marketable_setup_default=strategist_bot.STRATEGIST_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Create strategy for my hypothesis", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Design the smallest MVP scope that can test our core risk", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Turn research into positioning, messaging, and pricing decisions", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I'm Strategist. Load a skill to activate a workflow: experiment-hypothesis, gtm-channel-strategy, mvp-scope, mvp-validation-criteria, offer-design, positioning-market-map, positioning-messaging, pricing-model-design, or pricing-pilot-packaging.",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.filter_tools(strategist_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=strategist_bot.STRATEGIST_INTEGRATIONS,
        marketable_tags=["GTM", "Strategy", "Experiments", "Growth"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M | {"sched_when": "EVERY:1m"}],
        marketable_forms={},
        marketable_auth_supported=["linkedin"],
        marketable_auth_scopes={
            "linkedin": ["r_profile_basicinfo", "email", "w_member_social"],
        },
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("strategist_install")
    asyncio.run(install(client))
