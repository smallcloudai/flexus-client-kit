import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.creative_paid_channels_bot import creative_paid_channels_prompts
from flexus_simple_bots.creative_paid_channels_bot import creative_paid_channels_tools as tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "creative_paid_channels_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "creative_paid_channels_bot-256x256.webp").read_bytes()).decode("ascii")

_CREATIVE_WRITE_TOOL_NAMES = [
    tools.WRITE_CREATIVE_VARIANT_PACK_TOOL.name,
    tools.WRITE_CREATIVE_ASSET_MANIFEST_TOOL.name,
    tools.WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL.name,
]
_PAID_WRITE_TOOL_NAMES = [
    tools.WRITE_PAID_CHANNEL_TEST_PLAN_TOOL.name,
    tools.WRITE_PAID_CHANNEL_RESULT_TOOL.name,
    tools.WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL.name,
]

# default: all API tools + all write tools
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *[t.name for t in tools.API_TOOLS],
    *_CREATIVE_WRITE_TOOL_NAMES,
    *_PAID_WRITE_TOOL_NAMES,
])

# creative_producer: creative + feedback + measurement APIs + creative write tools only
FEXP_ALLOW_TOOLS_CREATIVE_PRODUCER = ",".join([
    "flexus_policy_document", "print_widget",
    tools.CREATIVE_ASSET_OPS_TOOL.name,
    tools.CREATIVE_FEEDBACK_CAPTURE_TOOL.name,
    tools.PAID_CHANNEL_MEASUREMENT_TOOL.name,
    *_CREATIVE_WRITE_TOOL_NAMES,
])

# paid_channel_operator: execution + measurement + asset APIs + paid write tools only
FEXP_ALLOW_TOOLS_PAID_CHANNEL_OPERATOR = ",".join([
    "flexus_policy_document", "print_widget",
    tools.PAID_CHANNEL_EXECUTION_TOOL.name,
    tools.PAID_CHANNEL_MEASUREMENT_TOOL.name,
    tools.CREATIVE_ASSET_OPS_TOOL.name,
    *_PAID_WRITE_TOOL_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=creative_paid_channels_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for creative and paid channel operations.",
    )),
    ("creative_producer", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=creative_paid_channels_prompts.creative_producer_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_CREATIVE_PRODUCER,
        fexp_description="Generate and version creative variants.",
    )),
    ("paid_channel_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=creative_paid_channels_prompts.paid_channel_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_PAID_CHANNEL_OPERATOR,
        fexp_description="Run one-platform paid tests with guardrails.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools_list: list[ckit_cloudtool.CloudTool],
) -> None:
    try:
        await ckit_bot_install.marketplace_upsert_dev_bot(
            client,
            ws_id=client.ws_id,
            marketable_name=bot_name,
            marketable_version=bot_version,
            marketable_accent_color="#BE185D",
            marketable_title1="Creative and Paid Channels",
            marketable_title2="Creative variants and one-platform paid tests",
            marketable_author="Flexus",
            marketable_occupation="Paid Growth Operator",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Demand",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.creative_paid_channels_bot.creative_paid_channels_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Generate creative variant pack",
                    "feat_expert": "creative_producer",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Launch one-platform paid test",
                    "feat_expert": "paid_channel_operator",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I create testable creatives and run controlled paid-channel tests.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools_list)) for name, exp in EXPERTS],
            marketable_tags=["Creative", "Paid", "Acquisition"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.creative_paid_channels_bot import creative_paid_channels_bot
    client = ckit_client.FlexusClient("creative_paid_channels_bot_install")
    asyncio.run(install(client, bot_name=creative_paid_channels_bot.BOT_NAME, bot_version=creative_paid_channels_bot.BOT_VERSION, tools_list=creative_paid_channels_bot.TOOLS))
