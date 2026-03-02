import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.segment_qualification_bot import segment_qualification_prompts
from flexus_simple_bots.segment_qualification_bot import segment_qualification_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_ENRICHER_API_TOOL_NAMES = [t.name for t in segment_qualification_tools.API_TOOLS]
_DECISION_API_TOOL_NAMES = [
    segment_qualification_tools.SEGMENT_CRM_SIGNAL_TOOL.name,
    segment_qualification_tools.SEGMENT_MARKET_TRACTION_TOOL.name,
    segment_qualification_tools.SEGMENT_INTENT_SIGNAL_TOOL.name,
]

# segment_data_enricher: pdoc + widget + all API tools + enrichment write tools
FEXP_ALLOW_TOOLS_ENRICHER = ",".join([
    "flexus_policy_document", "print_widget",
    *_ENRICHER_API_TOOL_NAMES,
    segment_qualification_tools.WRITE_SEGMENT_ENRICHMENT_TOOL.name,
    segment_qualification_tools.WRITE_SEGMENT_DATA_QUALITY_TOOL.name,
])

# primary_segment_decision_analyst: pdoc + widget + CRM/traction/intent tools + decision write tools
FEXP_ALLOW_TOOLS_DECISION_ANALYST = ",".join([
    "flexus_policy_document", "print_widget",
    *_DECISION_API_TOOL_NAMES,
    segment_qualification_tools.WRITE_SEGMENT_PRIORITY_MATRIX_TOOL.name,
    segment_qualification_tools.WRITE_PRIMARY_SEGMENT_DECISION_TOOL.name,
    segment_qualification_tools.WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=segment_qualification_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ENRICHER,
        fexp_description="Default route for segment qualification.",
    )),
    ("segment_data_enricher", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=segment_qualification_prompts.segment_data_enricher_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ENRICHER,
        fexp_description="Build segment evidence packs from first-party CRM and external firmographic/technographic/intent sources.",
    )),
    ("primary_segment_decision_analyst", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=segment_qualification_prompts.primary_segment_decision_analyst_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DECISION_ANALYST,
        fexp_description="Select one primary segment using explicit weighted scoring, risk controls, and rejection rationale.",
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
            marketable_accent_color="#0284C7",
            marketable_title1="Segment Qualification",
            marketable_title2="Enrichment and primary segment selection",
            marketable_author="Flexus",
            marketable_occupation="Segment Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Qualification",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.segment_qualification_bot.segment_qualification_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Enrich candidate segments",
                    "feat_expert": "segment_data_enricher",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Produce primary segment decision",
                    "feat_expert": "primary_segment_decision_analyst",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I enrich segment candidates and produce one explicit primary segment decision.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["ICP", "Segmentation", "PrimarySegment"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.segment_qualification_bot import segment_qualification_bot
    client = ckit_client.FlexusClient("segment_qualification_bot_install")
    asyncio.run(install(client, bot_name=segment_qualification_bot.BOT_NAME, bot_version=segment_qualification_bot.BOT_VERSION, tools=segment_qualification_bot.TOOLS))
