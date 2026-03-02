import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.gtm_economics_rtm_bot import gtm_economics_rtm_prompts
from flexus_simple_bots.gtm_economics_rtm_bot import gtm_economics_rtm_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "gtm_economics_rtm_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "gtm_economics_rtm_bot-256x256.webp").read_bytes()).decode("ascii")

_API_TOOL_NAMES = [t.name for t in gtm_economics_rtm_tools.API_TOOLS]
_WRITE_ECON_NAMES = [t.name for t in gtm_economics_rtm_tools.WRITE_TOOLS_ECONOMICS]
_WRITE_RTM_NAMES = [t.name for t in gtm_economics_rtm_tools.WRITE_TOOLS_RTM]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
])

FEXP_ALLOW_TOOLS_UNIT_ECONOMICS = ",".join([
    "flexus_policy_document", "print_widget",
    gtm_economics_rtm_tools.GTM_UNIT_ECONOMICS_TOOL.name,
    gtm_economics_rtm_tools.GTM_MEDIA_EFFICIENCY_TOOL.name,
    gtm_economics_rtm_tools.RTM_PIPELINE_FINANCE_TOOL.name,
    *_WRITE_ECON_NAMES,
])

FEXP_ALLOW_TOOLS_RTM = ",".join([
    "flexus_policy_document", "print_widget",
    gtm_economics_rtm_tools.RTM_PIPELINE_FINANCE_TOOL.name,
    gtm_economics_rtm_tools.RTM_TERRITORY_POLICY_TOOL.name,
    gtm_economics_rtm_tools.GTM_UNIT_ECONOMICS_TOOL.name,
    *_WRITE_RTM_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=gtm_economics_rtm_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for GTM economics and RTM.",
    )),
    ("unit_economics_modeler", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=gtm_economics_rtm_prompts.unit_economics_modeler_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_UNIT_ECONOMICS,
        fexp_description="Model payback and margin viability.",
    )),
    ("rtm_rules_architect", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=gtm_economics_rtm_prompts.rtm_rules_architect_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_RTM,
        fexp_description="Define enforceable RTM ownership and engagement rules.",
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
            marketable_accent_color="#334155",
            marketable_title1="GTM Economics and RTM",
            marketable_title2="Unit economics and route-to-market rules",
            marketable_author="Flexus",
            marketable_occupation="GTM Economist",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Economics",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.gtm_economics_rtm_bot.gtm_economics_rtm_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Evaluate unit economics readiness",
                    "feat_expert": "unit_economics_modeler",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Codify RTM ownership and conflict rules",
                    "feat_expert": "rtm_rules_architect",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I lock viable GTM economics and codify RTM rules.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["UnitEconomics", "RTM", "GTM"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.gtm_economics_rtm_bot import gtm_economics_rtm_bot
    client = ckit_client.FlexusClient("gtm_economics_rtm_bot_install")
    asyncio.run(install(client, bot_name=gtm_economics_rtm_bot.BOT_NAME, bot_version=gtm_economics_rtm_bot.BOT_VERSION, tools=gtm_economics_rtm_bot.TOOLS))
