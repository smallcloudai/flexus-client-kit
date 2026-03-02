import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.churn_learning_bot import churn_learning_prompts
from flexus_simple_bots.churn_learning_bot import churn_learning_tools

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "churn_learning_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "churn_learning_bot-256x256.webp").read_bytes()).decode("ascii")

_INTERVIEW_OPERATOR_API_TOOL_NAMES = [
    churn_learning_tools.CHURN_FEEDBACK_CAPTURE_TOOL.name,
    churn_learning_tools.CHURN_INTERVIEW_OPS_TOOL.name,
    churn_learning_tools.CHURN_TRANSCRIPT_ANALYSIS_TOOL.name,
]

_ROOTCAUSE_CLASSIFIER_API_TOOL_NAMES = [
    churn_learning_tools.CHURN_FEEDBACK_CAPTURE_TOOL.name,
    churn_learning_tools.CHURN_TRANSCRIPT_ANALYSIS_TOOL.name,
    churn_learning_tools.CHURN_REMEDIATION_BACKLOG_TOOL.name,
]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *[t.name for t in churn_learning_tools.API_TOOLS],
    *[t.name for t in churn_learning_tools.WRITE_TOOLS],
])

FEXP_ALLOW_TOOLS_INTERVIEW_OPERATOR = ",".join([
    "flexus_policy_document", "print_widget",
    *_INTERVIEW_OPERATOR_API_TOOL_NAMES,
    churn_learning_tools.WRITE_INTERVIEW_CORPUS_TOOL.name,
    churn_learning_tools.WRITE_INTERVIEW_COVERAGE_TOOL.name,
    churn_learning_tools.WRITE_SIGNAL_QUALITY_TOOL.name,
])

FEXP_ALLOW_TOOLS_ROOTCAUSE_CLASSIFIER = ",".join([
    "flexus_policy_document", "print_widget",
    *_ROOTCAUSE_CLASSIFIER_API_TOOL_NAMES,
    churn_learning_tools.WRITE_ROOTCAUSE_BACKLOG_TOOL.name,
    churn_learning_tools.WRITE_FIX_EXPERIMENT_PLAN_TOOL.name,
    churn_learning_tools.WRITE_PREVENTION_GATE_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=churn_learning_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for churn learning operations.",
    )),
    ("churn_interview_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=churn_learning_prompts.churn_interview_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_INTERVIEW_OPERATOR,
        fexp_description="Run structured churn interviews and produce interview artifacts.",
    )),
    ("rootcause_classifier", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=churn_learning_prompts.rootcause_classifier_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ROOTCAUSE_CLASSIFIER,
        fexp_description="Classify churn drivers and prioritize fix backlog.",
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
            marketable_accent_color="#7C2D12",
            marketable_title1="Churn Learning",
            marketable_title2="Churn interviews and root-cause classification",
            marketable_author="Flexus",
            marketable_occupation="Churn Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Retention",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.churn_learning_bot.churn_learning_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Run churn interview and evidence capture",
                    "feat_expert": "churn_interview_operator",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Build root-cause fix backlog",
                    "feat_expert": "rootcause_classifier",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I extract churn root causes into prioritized fix artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Churn", "RootCause", "Fixes"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.churn_learning_bot import churn_learning_bot
    client = ckit_client.FlexusClient("churn_learning_bot_install")
    asyncio.run(install(client, bot_name=churn_learning_bot.BOT_NAME, bot_version=churn_learning_bot.BOT_VERSION, tools=churn_learning_bot.TOOLS))
