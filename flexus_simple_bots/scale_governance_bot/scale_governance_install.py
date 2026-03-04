import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.scale_governance_bot import scale_governance_prompts
from flexus_simple_bots.scale_governance_bot import scale_governance_tools

BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text(encoding="utf-8"))

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "scale_governance_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "scale_governance_bot-256x256.webp").read_bytes()).decode("ascii")

_API_TOOL_NAMES = [t.name for t in scale_governance_tools.API_TOOLS]

FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    *_API_TOOL_NAMES,
    *[t.name for t in scale_governance_tools.WRITE_TOOLS],
])

FEXP_ALLOW_TOOLS_PLAYBOOK_CODIFIER = ",".join([
    "flexus_policy_document", "print_widget",
    scale_governance_tools.PLAYBOOK_REPO_TOOL.name,
    scale_governance_tools.SCALE_CHANGE_EXECUTION_TOOL.name,
    *[t.name for t in scale_governance_tools.WRITE_TOOLS_PLAYBOOK],
])

FEXP_ALLOW_TOOLS_SCALE_GUARDRAIL_CONTROLLER = ",".join([
    "flexus_policy_document", "print_widget",
    scale_governance_tools.SCALE_GUARDRAIL_MONITORING_TOOL.name,
    scale_governance_tools.SCALE_CHANGE_EXECUTION_TOOL.name,
    scale_governance_tools.SCALE_INCIDENT_RESPONSE_TOOL.name,
    *[t.name for t in scale_governance_tools.WRITE_TOOLS_CONTROLLER],
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=scale_governance_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for scale governance operations.",
    )),
    ("playbook_codifier", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=scale_governance_prompts.playbook_codifier_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_PLAYBOOK_CODIFIER,
        fexp_description="Convert proven operations into versioned playbooks.",
    )),
    ("scale_guardrail_controller", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=scale_governance_prompts.scale_guardrail_controller_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_SCALE_GUARDRAIL_CONTROLLER,
        fexp_description="Operate scale increments with explicit guardrail criteria.",
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
            marketable_accent_color="#1E293B",
            marketable_title1="Scale Governance",
            marketable_title2="Playbooks, guardrails, and controlled scaling",
            marketable_author="Flexus",
            marketable_occupation="Operations Governor",
            marketable_description=BOT_DESCRIPTION,
            marketable_typical_group="Ops / Governance",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.scale_governance_bot.scale_governance_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Generate and version playbook set",
                    "feat_expert": "playbook_codifier",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Approve guarded scale increment",
                    "feat_expert": "scale_guardrail_controller",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I codify operating playbooks and guardrail-controlled scale increments.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Scale", "Governance", "Playbooks"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.scale_governance_bot import scale_governance_bot
    client = ckit_client.FlexusClient("scale_governance_bot_install")
    asyncio.run(install(client, bot_name=scale_governance_bot.BOT_NAME, bot_version=scale_governance_bot.BOT_VERSION, tools=scale_governance_bot.TOOLS))
