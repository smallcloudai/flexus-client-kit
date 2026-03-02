import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.pipeline_qualification_bot import pipeline_qualification_prompts
from flexus_simple_bots.pipeline_qualification_bot import pipeline_qualification_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_API_TOOL_NAMES = [t.name for t in pipeline_qualification_tools.API_TOOLS]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
])

FEXP_ALLOW_TOOLS_PROSPECT_ACQUISITION = ",".join([
    "flexus_policy_document", "print_widget",
    pipeline_qualification_tools.PIPELINE_PROSPECTING_ENRICHMENT_TOOL.name,
    pipeline_qualification_tools.PIPELINE_OUTREACH_EXECUTION_TOOL.name,
    pipeline_qualification_tools.PIPELINE_CRM_TOOL.name,
    pipeline_qualification_tools.WRITE_PROSPECTING_BATCH_TOOL.name,
    pipeline_qualification_tools.WRITE_OUTREACH_EXECUTION_LOG_TOOL.name,
    pipeline_qualification_tools.WRITE_PROSPECT_DATA_QUALITY_TOOL.name,
])

FEXP_ALLOW_TOOLS_QUALIFICATION_MAPPER = ",".join([
    "flexus_policy_document", "print_widget",
    pipeline_qualification_tools.PIPELINE_CRM_TOOL.name,
    pipeline_qualification_tools.PIPELINE_ENGAGEMENT_SIGNAL_TOOL.name,
    pipeline_qualification_tools.PIPELINE_OUTREACH_EXECUTION_TOOL.name,
    pipeline_qualification_tools.WRITE_QUALIFICATION_MAP_TOOL.name,
    pipeline_qualification_tools.WRITE_BUYING_COMMITTEE_COVERAGE_TOOL.name,
    pipeline_qualification_tools.WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pipeline_qualification_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for pipeline qualification and prospecting.",
    )),
    ("prospect_acquisition_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pipeline_qualification_prompts.prospect_acquisition_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_PROSPECT_ACQUISITION,
        fexp_description="Source, enrich, and enroll ICP-aligned prospects into controlled outbound motions.",
    )),
    ("qualification_mapper", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pipeline_qualification_prompts.qualification_mapper_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_QUALIFICATION_MAPPER,
        fexp_description="Map qualification state and buying blockers.",
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
            marketable_accent_color="#0369A1",
            marketable_title1="Pipeline Qualification",
            marketable_title2="Prospecting and qualification mapping",
            marketable_author="Flexus",
            marketable_occupation="Pipeline Operator",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Pipeline",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.pipeline_qualification_bot.pipeline_qualification_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Run prospecting batch",
                    "feat_expert": "prospect_acquisition_operator",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Build qualification map",
                    "feat_expert": "qualification_mapper",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I generate qualified early pipeline and qualification artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Pipeline", "Prospecting", "Qualification"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.pipeline_qualification_bot import pipeline_qualification_bot
    client = ckit_client.FlexusClient("pipeline_qualification_bot_install")
    asyncio.run(install(client, bot_name=pipeline_qualification_bot.BOT_NAME, bot_version=pipeline_qualification_bot.BOT_VERSION, tools=pipeline_qualification_bot.TOOLS))
