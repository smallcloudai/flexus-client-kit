import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.mvp_validation_bot import mvp_validation_prompts
from flexus_simple_bots.mvp_validation_bot import mvp_validation_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

# mvp_flow_operator: experiment orchestration + telemetry + feedback capture + its write tools
FEXP_ALLOW_TOOLS_OPERATOR = ",".join([
    "flexus_policy_document", "print_widget",
    mvp_validation_tools.MVP_EXPERIMENT_ORCHESTRATION_TOOL.name,
    mvp_validation_tools.MVP_TELEMETRY_TOOL.name,
    mvp_validation_tools.MVP_FEEDBACK_CAPTURE_TOOL.name,
    mvp_validation_tools.WRITE_MVP_RUN_LOG_TOOL.name,
    mvp_validation_tools.WRITE_MVP_ROLLOUT_INCIDENT_TOOL.name,
    mvp_validation_tools.WRITE_MVP_FEEDBACK_DIGEST_TOOL.name,
])

# telemetry_integrity_analyst: telemetry + instrumentation health + feedback capture + its write tools
FEXP_ALLOW_TOOLS_ANALYST = ",".join([
    "flexus_policy_document", "print_widget",
    mvp_validation_tools.MVP_TELEMETRY_TOOL.name,
    mvp_validation_tools.MVP_INSTRUMENTATION_HEALTH_TOOL.name,
    mvp_validation_tools.MVP_FEEDBACK_CAPTURE_TOOL.name,
    mvp_validation_tools.WRITE_TELEMETRY_QUALITY_REPORT_TOOL.name,
    mvp_validation_tools.WRITE_TELEMETRY_DECISION_MEMO_TOOL.name,
    mvp_validation_tools.WRITE_MVP_SCALE_READINESS_GATE_TOOL.name,
])

# default: full access across all API tools and all write tools
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *[t.name for t in mvp_validation_tools.API_TOOLS],
    *[t.name for t in mvp_validation_tools.WRITE_TOOLS],
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mvp_validation_prompts.mvp_flow_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for MVP validation operations.",
    )),
    ("mvp_flow_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mvp_validation_prompts.mvp_flow_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_OPERATOR,
        fexp_description="Execute approved MVP rollout on bounded cohorts with strict guardrails and rollback controls.",
    )),
    ("telemetry_integrity_analyst", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=mvp_validation_prompts.telemetry_integrity_analyst_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ANALYST,
        fexp_description="Validate telemetry quality and produce threshold-based decision memos.",
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
            marketable_accent_color="#1D4ED8",
            marketable_title1="MVP Validation",
            marketable_title2="MVP run operations and telemetry integrity",
            marketable_author="Flexus",
            marketable_occupation="MVP Operator",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Validation",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.mvp_validation_bot.mvp_validation_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Run approved MVP test",
                    "feat_expert": "mvp_flow_operator",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Issue telemetry decision memo",
                    "feat_expert": "telemetry_integrity_analyst",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I run MVP tests and produce auditable decision artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["MVP", "Telemetry", "Validation"],
            marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.mvp_validation_bot import mvp_validation_bot
    client = ckit_client.FlexusClient("mvp_validation_bot_install")
    asyncio.run(install(client, bot_name=mvp_validation_bot.BOT_NAME, bot_version=mvp_validation_bot.BOT_VERSION, tools=mvp_validation_bot.TOOLS))
