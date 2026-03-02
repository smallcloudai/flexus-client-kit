import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.experiment_design_bot import experiment_design_prompts
from flexus_simple_bots.experiment_design_bot import experiment_design_tools

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "experiment_design_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "experiment_design_bot-256x256.webp").read_bytes()).decode("ascii")

_HYPOTHESIS_WRITE_TOOL_NAMES = ",".join([
    experiment_design_tools.WRITE_EXPERIMENT_CARD_DRAFT_TOOL.name,
    experiment_design_tools.WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL.name,
    experiment_design_tools.WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL.name,
])

_RELIABILITY_WRITE_TOOL_NAMES = ",".join([
    experiment_design_tools.WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL.name,
    experiment_design_tools.WRITE_EXPERIMENT_APPROVAL_TOOL.name,
    experiment_design_tools.WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL.name,
])

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document",
    "print_widget",
    experiment_design_tools.EXPERIMENT_BACKLOG_OPS_TOOL.name,
    experiment_design_tools.EXPERIMENT_RUNTIME_CONFIG_TOOL.name,
    experiment_design_tools.EXPERIMENT_GUARDRAIL_METRICS_TOOL.name,
    experiment_design_tools.EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL.name,
])

# hypothesis_architect: backlog ops + guardrail metrics + instrumentation quality + its own write tools
FEXP_ALLOW_TOOLS_HYPOTHESIS = ",".join([
    "flexus_policy_document",
    "print_widget",
    experiment_design_tools.EXPERIMENT_BACKLOG_OPS_TOOL.name,
    experiment_design_tools.EXPERIMENT_GUARDRAIL_METRICS_TOOL.name,
    experiment_design_tools.EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL.name,
    _HYPOTHESIS_WRITE_TOOL_NAMES,
])

# reliability_checker: runtime config + guardrail metrics + instrumentation quality + its own write tools
FEXP_ALLOW_TOOLS_RELIABILITY = ",".join([
    "flexus_policy_document",
    "print_widget",
    experiment_design_tools.EXPERIMENT_RUNTIME_CONFIG_TOOL.name,
    experiment_design_tools.EXPERIMENT_GUARDRAIL_METRICS_TOOL.name,
    experiment_design_tools.EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL.name,
    _RELIABILITY_WRITE_TOOL_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=experiment_design_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for experiment design and reliability workflows.",
    )),
    ("hypothesis_architect", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=experiment_design_prompts.hypothesis_architect_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_HYPOTHESIS,
        fexp_description="Convert risk backlog into high-quality, executable experiment cards with explicit metrics and stop rules.",
    )),
    ("reliability_checker", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=experiment_design_prompts.reliability_checker_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_RELIABILITY,
        fexp_description="Validate reliability conditions before experiment execution.",
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
            marketable_accent_color="#475569",
            marketable_title1="Experiment Design",
            marketable_title2="Test-design and reliability checks",
            marketable_author="Flexus",
            marketable_occupation="Experiment Architect",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Experiments",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.experiment_design_bot.experiment_design_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Draft experiment card",
                    "feat_expert": "hypothesis_architect",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Run reliability approval",
                    "feat_expert": "reliability_checker",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I turn key GTM risks into executable experiments with guardrails and explicit approval criteria.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Experiment", "Hypothesis", "Reliability"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.experiment_design_bot import experiment_design_bot
    client = ckit_client.FlexusClient("experiment_design_bot_install")
    asyncio.run(install(client, bot_name=experiment_design_bot.BOT_NAME, bot_version=experiment_design_bot.BOT_VERSION, tools=experiment_design_bot.TOOLS))
