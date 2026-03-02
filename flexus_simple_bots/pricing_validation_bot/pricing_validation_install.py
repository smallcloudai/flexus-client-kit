import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.pricing_validation_bot import pricing_validation_prompts
from flexus_simple_bots.pricing_validation_bot import pricing_validation_tools

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "pricing_validation_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "pricing_validation_bot-256x256.webp").read_bytes()).decode("ascii")

_API_TOOL_NAMES = [t.name for t in pricing_validation_tools.API_TOOLS]

# default: all API tools + all write tools
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
    *[t.name for t in pricing_validation_tools.WRITE_TOOLS],
])

# price_corridor_modeler: research + sales + catalog; no commitment events
FEXP_ALLOW_TOOLS_CORRIDOR = ",".join([
    "flexus_policy_document", "print_widget",
    pricing_validation_tools.PRICING_RESEARCH_OPS_TOOL.name,
    pricing_validation_tools.PRICING_SALES_SIGNAL_TOOL.name,
    pricing_validation_tools.PRICING_CATALOG_BENCHMARK_TOOL.name,
    pricing_validation_tools.WRITE_PRICE_CORRIDOR_TOOL.name,
    pricing_validation_tools.WRITE_PRICE_SENSITIVITY_CURVE_TOOL.name,
    pricing_validation_tools.WRITE_PRICING_ASSUMPTION_REGISTER_TOOL.name,
])

# commitment_evidence_verifier: commitment + sales + research; no catalog benchmark
FEXP_ALLOW_TOOLS_COMMITMENT = ",".join([
    "flexus_policy_document", "print_widget",
    pricing_validation_tools.PRICING_COMMITMENT_EVENTS_TOOL.name,
    pricing_validation_tools.PRICING_SALES_SIGNAL_TOOL.name,
    pricing_validation_tools.PRICING_RESEARCH_OPS_TOOL.name,
    pricing_validation_tools.WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL.name,
    pricing_validation_tools.WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL.name,
    pricing_validation_tools.WRITE_PRICING_GO_NO_GO_GATE_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pricing_validation_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for pricing validation.",
    )),
    ("price_corridor_modeler", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pricing_validation_prompts.price_corridor_modeler_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_CORRIDOR,
        fexp_description="Estimate floor-target-ceiling pricing corridor from stated willingness-to-pay, segment fit, and benchmark context.",
    )),
    ("commitment_evidence_verifier", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pricing_validation_prompts.commitment_evidence_verifier_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_COMMITMENT,
        fexp_description="Verify pricing hypotheses against observed commitment signals from billing and sales pipelines.",
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
            marketable_accent_color="#B45309",
            marketable_title1="Pricing Validation",
            marketable_title2="Price corridor and commitment evidence",
            marketable_author="Flexus",
            marketable_occupation="Pricing Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Pricing",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.pricing_validation_bot.pricing_validation_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Estimate initial price corridor",
                    "feat_expert": "price_corridor_modeler",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Verify commitment evidence",
                    "feat_expert": "commitment_evidence_verifier",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I validate pricing hypotheses with structured evidence artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Pricing", "WTP", "Validation"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.pricing_validation_bot import pricing_validation_bot
    client = ckit_client.FlexusClient("pricing_validation_bot_install")
    asyncio.run(install(client, bot_name=pricing_validation_bot.BOT_NAME, bot_version=pricing_validation_bot.BOT_VERSION, tools=pricing_validation_bot.TOOLS))
