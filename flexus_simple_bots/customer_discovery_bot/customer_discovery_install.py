import asyncio
import base64

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.customer_discovery_bot import customer_discovery_prompts
from flexus_simple_bots.customer_discovery_bot import customer_discovery_tools

SETUP_SCHEMA = []

_PIC_BIG_B64 = base64.b64encode((Path(__file__).parent / "customer_discovery_bot-1024x1536.webp").read_bytes()).decode("ascii")
_PIC_SMALL_B64 = base64.b64encode((Path(__file__).parent / "customer_discovery_bot-256x256.webp").read_bytes()).decode("ascii")

_API_TOOL_NAMES = [t.name for t in customer_discovery_tools.API_TOOLS]

# default: survey design, survey collection, context import — no write tools
FEXP_ALLOW_TOOLS_DEFAULT = ",".join([
    "flexus_policy_document", "print_widget",
    "discovery_survey_design_api",
    "discovery_survey_collection_api",
    "discovery_context_import_api",
])

# discovery_instrument_designer: survey design + collection + context import + instrument write tools
FEXP_ALLOW_TOOLS_INSTRUMENT_DESIGNER = ",".join([
    "flexus_policy_document", "print_widget",
    "discovery_survey_design_api",
    "discovery_survey_collection_api",
    "discovery_context_import_api",
    customer_discovery_tools.WRITE_INTERVIEW_INSTRUMENT_TOOL.name,
    customer_discovery_tools.WRITE_SURVEY_INSTRUMENT_TOOL.name,
    customer_discovery_tools.WRITE_INSTRUMENT_READINESS_TOOL.name,
])

# participant_recruitment_operator: panel + customer panel + test + scheduling + collection + context import + recruitment write tools
FEXP_ALLOW_TOOLS_RECRUITMENT = ",".join([
    "flexus_policy_document", "print_widget",
    "discovery_panel_recruitment_api",
    "discovery_customer_panel_api",
    "discovery_test_recruitment_api",
    "discovery_interview_scheduling_api",
    "discovery_survey_collection_api",
    "discovery_context_import_api",
    customer_discovery_tools.WRITE_RECRUITMENT_PLAN_TOOL.name,
    customer_discovery_tools.WRITE_RECRUITMENT_FUNNEL_TOOL.name,
    customer_discovery_tools.WRITE_RECRUITMENT_COMPLIANCE_TOOL.name,
])

# jtbd_interview_operator: capture + coding + context import + interview evidence write tools (no print_widget)
FEXP_ALLOW_TOOLS_JTBD = ",".join([
    "flexus_policy_document",
    "discovery_interview_capture_api",
    "discovery_transcript_coding_api",
    "discovery_context_import_api",
    customer_discovery_tools.WRITE_INTERVIEW_CORPUS_TOOL.name,
    customer_discovery_tools.WRITE_JTBD_OUTCOMES_TOOL.name,
    customer_discovery_tools.WRITE_EVIDENCE_QUALITY_TOOL.name,
])

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=customer_discovery_prompts.default_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_DEFAULT,
        fexp_description="Default route for discovery operations.",
    )),
    ("discovery_instrument_designer", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=customer_discovery_prompts.discovery_instrument_designer_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_INSTRUMENT_DESIGNER,
        fexp_description="Design high-quality interview and survey instruments.",
    )),
    ("participant_recruitment_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=customer_discovery_prompts.participant_recruitment_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_RECRUITMENT,
        fexp_description="Recruit participants for surveys, interviews, and usability tests across panel providers.",
    )),
    ("jtbd_interview_operator", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=customer_discovery_prompts.jtbd_interview_operator_prompt(),
        fexp_python_kernel="",
        fexp_block_tools="",
        fexp_allow_tools=FEXP_ALLOW_TOOLS_JTBD,
        fexp_description="Operate JTBD interviews and produce coded evidence artifacts.",
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
            marketable_accent_color="#0D9488",
            marketable_title1="Customer Discovery",
            marketable_title2="Interview and survey evidence operations",
            marketable_author="Flexus",
            marketable_occupation="Discovery Operator",
            marketable_description="## Customer Discovery Bot\n\nCustomer Discovery Bot runs structured discovery workflows and keeps evidence quality high. It designs interview and survey instruments, recruits participants, and operates JTBD interviews to produce coded evidence artifacts.",
            marketable_typical_group="GTM / Discovery",
            marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
            marketable_run_this="python -m flexus_simple_bots.customer_discovery_bot.customer_discovery_bot",
            marketable_setup_default=SETUP_SCHEMA,
            marketable_featured_actions=[
                {
                    "feat_question": "Prepare next interview instrument",
                    "feat_expert": "discovery_instrument_designer",
                    "feat_depends_on_setup": [],
                },
                {
                    "feat_question": "Recruit participants for interviews/tests",
                    "feat_expert": "participant_recruitment_operator",
                    "feat_depends_on_setup": [],
                },
            ],
            marketable_intro_message="I run structured discovery workflows and keep evidence quality high.",
            marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
            marketable_daily_budget_default=100_000,
            marketable_default_inbox_default=10_000,
            marketable_picture_big_b64=_PIC_BIG_B64,
            marketable_picture_small_b64=_PIC_SMALL_B64,
            marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
            marketable_tags=["Discovery", "JTBD", "Research"],
            marketable_schedule=[],
            marketable_forms=ckit_bot_install.load_form_bundles(__file__),
            marketable_auth_supported=[],
            marketable_auth_scopes={},
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


if __name__ == "__main__":
    from flexus_simple_bots.customer_discovery_bot import customer_discovery_bot
    client = ckit_client.FlexusClient("customer_discovery_bot_install")
    asyncio.run(install(client, bot_name=customer_discovery_bot.BOT_NAME, bot_version=customer_discovery_bot.BOT_VERSION, tools=customer_discovery_bot.TOOLS))
