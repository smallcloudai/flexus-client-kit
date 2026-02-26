import asyncio
import base64

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.pain_alternatives_bot import pain_alternatives_prompts
from flexus_simple_bots.pain_alternatives_bot import pain_alternatives_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = "## Pain and Alternatives Bot\n\nPain and Alternatives Bot quantifies pain and maps alternatives in structured artifacts."

SETUP_SCHEMA = []

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_PAIN_QUANTIFIER_WRITE_TOOL_NAMES = [
    pain_alternatives_tools.WRITE_PAIN_SIGNAL_REGISTER_TOOL.name,
    pain_alternatives_tools.WRITE_PAIN_ECONOMICS_TOOL.name,
    pain_alternatives_tools.WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL.name,
]

_ALTERNATIVE_MAPPER_WRITE_TOOL_NAMES = [
    pain_alternatives_tools.WRITE_ALTERNATIVE_LANDSCAPE_TOOL.name,
    pain_alternatives_tools.WRITE_COMPETITIVE_GAP_MATRIX_TOOL.name,
    pain_alternatives_tools.WRITE_DISPLACEMENT_HYPOTHESES_TOOL.name,
]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document",
    "print_widget",
    pain_alternatives_tools.PAIN_VOICE_OF_CUSTOMER_TOOL.name,
    pain_alternatives_tools.PAIN_SUPPORT_SIGNAL_TOOL.name,
    pain_alternatives_tools.ALTERNATIVES_MARKET_SCAN_TOOL.name,
    pain_alternatives_tools.ALTERNATIVES_TRACTION_BENCHMARK_TOOL.name,
])

FEXP_ALLOW_TOOLS_PAIN_QUANTIFIER = ",".join([
    "flexus_policy_document",
    "print_widget",
    pain_alternatives_tools.PAIN_VOICE_OF_CUSTOMER_TOOL.name,
    pain_alternatives_tools.PAIN_SUPPORT_SIGNAL_TOOL.name,
    pain_alternatives_tools.ALTERNATIVES_MARKET_SCAN_TOOL.name,
    *_PAIN_QUANTIFIER_WRITE_TOOL_NAMES,
])

FEXP_ALLOW_TOOLS_ALTERNATIVE_MAPPER = ",".join([
    "flexus_policy_document",
    "print_widget",
    pain_alternatives_tools.ALTERNATIVES_MARKET_SCAN_TOOL.name,
    pain_alternatives_tools.ALTERNATIVES_TRACTION_BENCHMARK_TOOL.name,
    pain_alternatives_tools.PAIN_VOICE_OF_CUSTOMER_TOOL.name,
    *_ALTERNATIVE_MAPPER_WRITE_TOOL_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pain_alternatives_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for pain quantification and alternative mapping.",
    )),
    ("pain_quantifier", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pain_alternatives_prompts.pain_quantifier_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_PAIN_QUANTIFIER,
        fexp_description="Convert multi-channel pain evidence into quantified impact ranges with confidence and source traceability.",
    )),
    ("alternative_mapper", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pain_alternatives_prompts.alternative_mapper_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ALTERNATIVE_MAPPER,
        fexp_description="Map direct, indirect, and status-quo alternatives with explicit adoption/failure drivers and benchmarked traction.",
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
            marketable_accent_color="#7C3AED",
            marketable_title1="Pain and Alternatives",
            marketable_title2="Pain quantification and alternative mapping",
            marketable_author="Flexus",
            marketable_occupation="Problem Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Qualification",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.pain_alternatives_bot.pain_alternatives_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Quantify top customer pains",
                    "feat_expert": "pain_quantifier",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Map alternative landscape",
                    "feat_expert": "alternative_mapper",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I quantify pain and map alternatives in structured artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Pain", "Alternatives", "Evidence"],
            marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.pain_alternatives_bot import pain_alternatives_bot
    client = ckit_client.FlexusClient("pain_alternatives_bot_install")
    asyncio.run(install(client, bot_name=pain_alternatives_bot.BOT_NAME, bot_version=pain_alternatives_bot.BOT_VERSION, tools=pain_alternatives_bot.TOOLS))
