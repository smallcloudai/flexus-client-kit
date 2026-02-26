import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.customer_discovery_bot import customer_discovery_install
from flexus_simple_bots.customer_discovery_bot import customer_discovery_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_customer_discovery")

BOT_NAME = "customer_discovery_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *customer_discovery_tools.API_TOOLS,
    *customer_discovery_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def customer_discovery_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(customer_discovery_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_SURVEY_DESIGN_TOOL.name)
    async def toolcall_survey_design(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_SURVEY_DESIGN_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_SURVEY_COLLECTION_TOOL.name)
    async def toolcall_survey_collection(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_SURVEY_COLLECTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_PANEL_RECRUITMENT_TOOL.name)
    async def toolcall_panel_recruitment(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_PANEL_RECRUITMENT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_CUSTOMER_PANEL_TOOL.name)
    async def toolcall_customer_panel(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_CUSTOMER_PANEL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_TEST_RECRUITMENT_TOOL.name)
    async def toolcall_test_recruitment(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_TEST_RECRUITMENT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_INTERVIEW_SCHEDULING_TOOL.name)
    async def toolcall_interview_scheduling(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_INTERVIEW_SCHEDULING_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_INTERVIEW_CAPTURE_TOOL.name)
    async def toolcall_interview_capture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_INTERVIEW_CAPTURE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_TRANSCRIPT_CODING_TOOL.name)
    async def toolcall_transcript_coding(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_TRANSCRIPT_CODING_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.DISCOVERY_CONTEXT_IMPORT_TOOL.name)
    async def toolcall_context_import(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await customer_discovery_tools.handle_api_tool_call(customer_discovery_tools.DISCOVERY_CONTEXT_IMPORT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_INTERVIEW_INSTRUMENT_TOOL.name)
    async def toolcall_write_interview_instrument(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_interview_instrument(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_SURVEY_INSTRUMENT_TOOL.name)
    async def toolcall_write_survey_instrument(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_survey_instrument(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_INSTRUMENT_READINESS_TOOL.name)
    async def toolcall_write_instrument_readiness(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_instrument_readiness(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_RECRUITMENT_PLAN_TOOL.name)
    async def toolcall_write_recruitment_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_recruitment_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_RECRUITMENT_FUNNEL_TOOL.name)
    async def toolcall_write_recruitment_funnel(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_recruitment_funnel(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_RECRUITMENT_COMPLIANCE_TOOL.name)
    async def toolcall_write_recruitment_compliance(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_recruitment_compliance(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_INTERVIEW_CORPUS_TOOL.name)
    async def toolcall_write_interview_corpus(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_interview_corpus(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_JTBD_OUTCOMES_TOOL.name)
    async def toolcall_write_jtbd_outcomes(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_jtbd_outcomes(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(customer_discovery_tools.WRITE_EVIDENCE_QUALITY_TOOL.name)
    async def toolcall_write_evidence_quality(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await customer_discovery_tools.handle_write_evidence_quality(toolcall, args, pdoc_integration, rcx)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=customer_discovery_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=customer_discovery_install.install,
    ))


if __name__ == "__main__":
    main()
