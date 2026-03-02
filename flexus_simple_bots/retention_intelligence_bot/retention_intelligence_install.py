import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.retention_intelligence_bot import retention_intelligence_prompts
from flexus_simple_bots.retention_intelligence_bot import retention_intelligence_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_API_TOOL_NAMES = [t.name for t in retention_intelligence_tools.API_TOOLS]

# default: all api tools, no write tools (routing only)
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
])

# cohort_revenue_analyst: revenue + product_analytics + account_context + cohort write tools
FEXP_ALLOW_TOOLS_COHORT = ",".join([
    "flexus_policy_document", "print_widget",
    retention_intelligence_tools.RETENTION_REVENUE_EVENTS_TOOL.name,
    retention_intelligence_tools.RETENTION_PRODUCT_ANALYTICS_TOOL.name,
    retention_intelligence_tools.RETENTION_ACCOUNT_CONTEXT_TOOL.name,
    retention_intelligence_tools.WRITE_COHORT_REVENUE_REVIEW_TOOL.name,
    retention_intelligence_tools.WRITE_RETENTION_DRIVER_MATRIX_TOOL.name,
    retention_intelligence_tools.WRITE_RETENTION_READINESS_GATE_TOOL.name,
])

# pmf_survey_interpreter: feedback_research + product_analytics + account_context + pmf write tools
FEXP_ALLOW_TOOLS_PMF = ",".join([
    "flexus_policy_document", "print_widget",
    retention_intelligence_tools.RETENTION_FEEDBACK_RESEARCH_TOOL.name,
    retention_intelligence_tools.RETENTION_PRODUCT_ANALYTICS_TOOL.name,
    retention_intelligence_tools.RETENTION_ACCOUNT_CONTEXT_TOOL.name,
    retention_intelligence_tools.WRITE_PMF_CONFIDENCE_SCORECARD_TOOL.name,
    retention_intelligence_tools.WRITE_PMF_SIGNAL_EVIDENCE_TOOL.name,
    retention_intelligence_tools.WRITE_PMF_RESEARCH_BACKLOG_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=retention_intelligence_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for retention and PMF analysis.",
    )),
    ("cohort_revenue_analyst", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=retention_intelligence_prompts.cohort_revenue_analyst_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_COHORT,
        fexp_description="Diagnose activation-retention-revenue behavior.",
    )),
    ("pmf_survey_interpreter", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=retention_intelligence_prompts.pmf_survey_interpreter_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_PMF,
        fexp_description="Interpret PMF survey evidence with behavioral context.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
) -> None:
    try:
        await ckit_bot_install.marketplace_upsert_dev_bot(
            client,
            ws_id=client.ws_id,
            marketable_name=bot_name,
            marketable_version=bot_version,
            marketable_accent_color="#0E7490",
            marketable_title1="Retention Intelligence",
            marketable_title2="Cohort and PMF confidence synthesis",
            marketable_author="Flexus",
            marketable_occupation="Retention Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Retention",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.retention_intelligence_bot.retention_intelligence_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Run cohort retention and revenue review",
                    "feat_expert": "cohort_revenue_analyst",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Score PMF confidence from behavioral and survey evidence",
                    "feat_expert": "pmf_survey_interpreter",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I synthesize retention, revenue, and PMF confidence evidence.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Retention", "PMF", "Cohorts"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.retention_intelligence_bot import retention_intelligence_bot
    client = ckit_client.FlexusClient("retention_intelligence_bot_install")
    asyncio.run(install(client, bot_name=retention_intelligence_bot.BOT_NAME, bot_version=retention_intelligence_bot.BOT_VERSION, tools=retention_intelligence_bot.TOOLS))
