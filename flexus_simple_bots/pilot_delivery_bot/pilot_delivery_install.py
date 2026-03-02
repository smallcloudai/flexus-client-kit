import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.pilot_delivery_bot import pilot_delivery_prompts
from flexus_simple_bots.pilot_delivery_bot import pilot_delivery_tools
from flexus_simple_bots import prompts_common

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

ONE_PIXEL_PNG_B64 = base64.b64encode(
    bytes.fromhex("89504E470D0A1A0A0000000D4948445200000001000000010804000000B51C0C020000000B4944415478DA63FCFF1F00030302EFD79FD90000000049454E44AE426082")
).decode("ascii")

_API_TOOL_NAMES = [t.name for t in pilot_delivery_tools.API_TOOLS]
_CONTRACTING_WRITE_NAMES = [t.name for t in pilot_delivery_tools.CONTRACTING_WRITE_TOOLS]
_DELIVERY_WRITE_NAMES = [t.name for t in pilot_delivery_tools.DELIVERY_WRITE_TOOLS]

# default: all API tools + all write tools — most permissive routing
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
    *_CONTRACTING_WRITE_NAMES,
    *_DELIVERY_WRITE_NAMES,
])

# pilot_contracting_operator: contracting + delivery ops APIs + contracting write tools only
FEXP_ALLOW_TOOLS_CONTRACTING = ",".join([
    "flexus_policy_document", "print_widget",
    pilot_delivery_tools.PILOT_CONTRACTING_TOOL.name,
    pilot_delivery_tools.PILOT_DELIVERY_OPS_TOOL.name,
    *_CONTRACTING_WRITE_NAMES,
])

# first_value_delivery_operator: delivery ops + usage evidence + stakeholder sync APIs + delivery write tools only
FEXP_ALLOW_TOOLS_DELIVERY = ",".join([
    "flexus_policy_document", "print_widget",
    pilot_delivery_tools.PILOT_DELIVERY_OPS_TOOL.name,
    pilot_delivery_tools.PILOT_USAGE_EVIDENCE_TOOL.name,
    pilot_delivery_tools.PILOT_STAKEHOLDER_SYNC_TOOL.name,
    *_DELIVERY_WRITE_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pilot_delivery_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for pilot delivery operations.",
    )),
    ("pilot_contracting_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pilot_delivery_prompts.pilot_contracting_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_CONTRACTING,
        fexp_description="Define and finalize paid pilot terms.",
    )),
    ("first_value_delivery_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=pilot_delivery_prompts.first_value_delivery_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DELIVERY,
        fexp_description="Drive first value delivery and collect proof artifacts.",
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
            marketable_accent_color="#15803D",
            marketable_title1="Pilot Delivery",
            marketable_title2="Paid pilot contracting and first value delivery",
            marketable_author="Flexus",
            marketable_occupation="Pilot Delivery Manager",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Delivery",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.pilot_delivery_bot.pilot_delivery_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Prepare pilot contracting packet",
                    "feat_expert": "pilot_contracting_operator",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Execute first value delivery",
                    "feat_expert": "first_value_delivery_operator",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I convert qualified opportunities into paid pilot outcomes.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=ONE_PIXEL_PNG_B64,
            marketable_picture_small_b64=ONE_PIXEL_PNG_B64,
            marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Pilot", "Delivery", "Activation"],
            marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.pilot_delivery_bot import pilot_delivery_bot
    client = ckit_client.FlexusClient("pilot_delivery_bot_install")
    asyncio.run(install(client, bot_name=pilot_delivery_bot.BOT_NAME, bot_version=pilot_delivery_bot.BOT_VERSION, tools=pilot_delivery_bot.TOOLS))
