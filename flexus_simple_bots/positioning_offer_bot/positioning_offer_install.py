import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.positioning_offer_bot import positioning_offer_prompts
from flexus_simple_bots.positioning_offer_bot import positioning_offer_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "positioning_offer_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "positioning_offer_bot-256x256.webp").read_bytes()).decode("ascii")

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document",
    "print_widget",
    positioning_offer_tools.POSITIONING_MESSAGE_TEST_TOOL.name,
    positioning_offer_tools.POSITIONING_COMPETITOR_INTEL_TOOL.name,
    positioning_offer_tools.OFFER_PACKAGING_BENCHMARK_TOOL.name,
    positioning_offer_tools.POSITIONING_CHANNEL_PROBE_TOOL.name,
])

FEXP_ALLOW_TOOLS_VALUE_PROP = ",".join([
    "flexus_policy_document",
    "print_widget",
    positioning_offer_tools.POSITIONING_COMPETITOR_INTEL_TOOL.name,
    positioning_offer_tools.OFFER_PACKAGING_BENCHMARK_TOOL.name,
    positioning_offer_tools.POSITIONING_MESSAGE_TEST_TOOL.name,
    positioning_offer_tools.WRITE_VALUE_PROPOSITION_TOOL.name,
    positioning_offer_tools.WRITE_OFFER_PACKAGING_TOOL.name,
    positioning_offer_tools.WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL.name,
])

FEXP_ALLOW_TOOLS_TEST_OPERATOR = ",".join([
    "flexus_policy_document",
    "print_widget",
    positioning_offer_tools.POSITIONING_MESSAGE_TEST_TOOL.name,
    positioning_offer_tools.POSITIONING_CHANNEL_PROBE_TOOL.name,
    positioning_offer_tools.POSITIONING_COMPETITOR_INTEL_TOOL.name,
    positioning_offer_tools.WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL.name,
    positioning_offer_tools.WRITE_POSITIONING_TEST_RESULT_TOOL.name,
    positioning_offer_tools.WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=positioning_offer_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for positioning and offer tasks.",
    )),
    ("value_proposition_synthesizer", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=positioning_offer_prompts.value_proposition_synthesizer_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_VALUE_PROP,
        fexp_description="Synthesize segment-specific value proposition and offer packaging boundaries from evidence and market context.",
    )),
    ("positioning_test_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=positioning_offer_prompts.positioning_test_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_TEST_OPERATOR,
        fexp_description="Run positioning and messaging experiments across research and paid channel probes, then select winner with confidence.",
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
            marketable_accent_color="#0F766E",
            marketable_title1="Positioning and Offer",
            marketable_title2="Value proposition and package architecture",
            marketable_author="Flexus",
            marketable_occupation="Positioning Architect",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Messaging",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.positioning_offer_bot.positioning_offer_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Draft value proposition",
                    "feat_expert": "value_proposition_synthesizer",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Run positioning test",
                    "feat_expert": "positioning_test_operator",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I turn validated pains into positioning and offer artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Positioning", "Offer", "Messaging"],
            marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.positioning_offer_bot import positioning_offer_bot
    client = ckit_client.FlexusClient("positioning_offer_bot_install")
    asyncio.run(install(client, bot_name=positioning_offer_bot.BOT_NAME, bot_version=positioning_offer_bot.BOT_VERSION, tools=positioning_offer_bot.TOOLS))
