import asyncio
import base64
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.partner_ecosystem_bot import partner_ecosystem_prompts
from flexus_simple_bots.partner_ecosystem_bot import partner_ecosystem_tools

BOT_DESCRIPTION = "## Partner Ecosystem\n\nPartner Ecosystem Bot runs partner lifecycle operations and conflict governance artifacts."

SETUP_SCHEMA = []

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "partner_ecosystem_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "partner_ecosystem_bot-256x256.webp").read_bytes()).decode("ascii")

_ACTIVATION_WRITE_TOOL_NAMES = [
    partner_ecosystem_tools.WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL.name,
    partner_ecosystem_tools.WRITE_PARTNER_ENABLEMENT_PLAN_TOOL.name,
    partner_ecosystem_tools.WRITE_PARTNER_PIPELINE_QUALITY_TOOL.name,
]

_CONFLICT_WRITE_TOOL_NAMES = [
    partner_ecosystem_tools.WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL.name,
    partner_ecosystem_tools.WRITE_DEAL_REGISTRATION_POLICY_TOOL.name,
    partner_ecosystem_tools.WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL.name,
]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    partner_ecosystem_tools.PARTNER_PROGRAM_OPS_TOOL.name,
    partner_ecosystem_tools.PARTNER_ACCOUNT_MAPPING_TOOL.name,
    partner_ecosystem_tools.PARTNER_ENABLEMENT_EXECUTION_TOOL.name,
    partner_ecosystem_tools.CHANNEL_CONFLICT_GOVERNANCE_TOOL.name,
    *_ACTIVATION_WRITE_TOOL_NAMES,
    *_CONFLICT_WRITE_TOOL_NAMES,
])

FEXP_ALLOW_TOOLS_ACTIVATION = ",".join([
    "flexus_policy_document", "print_widget",
    partner_ecosystem_tools.PARTNER_PROGRAM_OPS_TOOL.name,
    partner_ecosystem_tools.PARTNER_ACCOUNT_MAPPING_TOOL.name,
    partner_ecosystem_tools.PARTNER_ENABLEMENT_EXECUTION_TOOL.name,
    *_ACTIVATION_WRITE_TOOL_NAMES,
])

FEXP_ALLOW_TOOLS_CONFLICT = ",".join([
    "flexus_policy_document", "print_widget",
    partner_ecosystem_tools.CHANNEL_CONFLICT_GOVERNANCE_TOOL.name,
    partner_ecosystem_tools.PARTNER_ACCOUNT_MAPPING_TOOL.name,
    partner_ecosystem_tools.PARTNER_PROGRAM_OPS_TOOL.name,
    *_CONFLICT_WRITE_TOOL_NAMES,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=partner_ecosystem_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for partner lifecycle operations.",
    )),
    ("partner_activation_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=partner_ecosystem_prompts.partner_activation_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_ACTIVATION,
        fexp_description="Operate partner recruit/onboard/enable/activate cycle.",
    )),
    ("channel_conflict_governor", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=partner_ecosystem_prompts.channel_conflict_governor_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_CONFLICT,
        fexp_description="Enforce deal registration and channel conflict handling.",
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
            marketable_accent_color="#166534",
            marketable_title1="Partner Ecosystem",
            marketable_title2="Partner activation and channel conflict governance",
            marketable_author="Flexus",
            marketable_occupation="Partner Program Operator",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="GTM / Partners",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.partner_ecosystem_bot.partner_ecosystem_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Run partner activation and enablement cycle",
                    "feat_expert": "partner_activation_operator",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Resolve channel conflict incidents",
                    "feat_expert": "channel_conflict_governor",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I run partner lifecycle operations and conflict governance artifacts.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Partners", "PRM", "Channel"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.partner_ecosystem_bot import partner_ecosystem_bot
    client = ckit_client.FlexusClient("partner_ecosystem_bot_install")
    asyncio.run(install(client, bot_name=partner_ecosystem_bot.BOT_NAME, bot_version=partner_ecosystem_bot.BOT_VERSION, tools=partner_ecosystem_bot.TOOLS))
