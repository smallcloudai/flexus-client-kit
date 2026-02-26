import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.market_signal_bot import market_signal_prompts
from flexus_simple_bots.market_signal_bot import market_signal_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

# 1x1 image placeholder to keep install robust even if no art assets exist.
ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_SIGNAL_TOOL_NAMES = [t.name for t in market_signal_tools.SIGNAL_TOOLS]
# market_signal_detector: all signal tools + its own write tool
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_SIGNAL_TOOL_NAMES,
    market_signal_tools.WRITE_SNAPSHOT_TOOL.name,
])
# signal_boundary_analyst: reads pdoc artifacts, writes register + backlog (no signal tools, no print_widget)
FEXP_ALLOW_TOOLS_ANALYST = ",".join([
    "flexus_policy_document",
    market_signal_tools.WRITE_SIGNAL_REGISTER_TOOL.name,
    market_signal_tools.WRITE_HYPOTHESIS_BACKLOG_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=market_signal_prompts.market_signal_detector_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for channel signal detection.",
    )),
    ("market_signal_detector", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=market_signal_prompts.market_signal_detector_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Detect and normalize market signals for one channel per run.",
    )),
    ("signal_boundary_analyst", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=market_signal_prompts.signal_boundary_analyst_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="print_widget",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ANALYST,
        fexp_description="Aggregate channel snapshots into signal register and prioritized hypotheses.",
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
            marketable_accent_color="#2563EB",
            marketable_title1="Market Signal",
            marketable_title2="Channel-specific signal detection and normalization",
            marketable_author="Flexus",
            marketable_occupation="Market Signal Analyst",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Discovery",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.market_signal_bot.market_signal_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Detect market signals for one channel",
                    "feat_expert": "market_signal_detector",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I detect and normalize market signals into structured artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["GTM", "Signals", "Discovery"],
            marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.market_signal_bot import market_signal_bot
    client = ckit_client.FlexusClient("market_signal_bot_install")
    asyncio.run(install(client, bot_name=market_signal_bot.BOT_NAME, bot_version=market_signal_bot.BOT_VERSION, tools=market_signal_bot.TOOLS))
