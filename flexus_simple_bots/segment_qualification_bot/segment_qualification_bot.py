import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.segment_qualification_bot import segment_qualification_install
from flexus_simple_bots.segment_qualification_bot import segment_qualification_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_segment_qualification")

BOT_NAME = "segment_qualification_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *segment_qualification_tools.API_TOOLS,
    *segment_qualification_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def segment_qualification_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(segment_qualification_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.SEGMENT_CRM_SIGNAL_TOOL.name)
    async def toolcall_segment_crm_signal(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await segment_qualification_tools.handle_api_tool_call(segment_qualification_tools.SEGMENT_CRM_SIGNAL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.SEGMENT_FIRMOGRAPHIC_ENRICHMENT_TOOL.name)
    async def toolcall_segment_firmographic_enrichment(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await segment_qualification_tools.handle_api_tool_call(segment_qualification_tools.SEGMENT_FIRMOGRAPHIC_ENRICHMENT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.SEGMENT_TECHNOGRAPHIC_PROFILE_TOOL.name)
    async def toolcall_segment_technographic_profile(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await segment_qualification_tools.handle_api_tool_call(segment_qualification_tools.SEGMENT_TECHNOGRAPHIC_PROFILE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.SEGMENT_MARKET_TRACTION_TOOL.name)
    async def toolcall_segment_market_traction(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await segment_qualification_tools.handle_api_tool_call(segment_qualification_tools.SEGMENT_MARKET_TRACTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.SEGMENT_INTENT_SIGNAL_TOOL.name)
    async def toolcall_segment_intent_signal(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await segment_qualification_tools.handle_api_tool_call(segment_qualification_tools.SEGMENT_INTENT_SIGNAL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(segment_qualification_tools.WRITE_SEGMENT_ENRICHMENT_TOOL.name)
    async def toolcall_write_segment_enrichment(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await segment_qualification_tools.handle_write_segment_enrichment(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(segment_qualification_tools.WRITE_SEGMENT_DATA_QUALITY_TOOL.name)
    async def toolcall_write_segment_data_quality(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await segment_qualification_tools.handle_write_segment_data_quality(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(segment_qualification_tools.WRITE_SEGMENT_PRIORITY_MATRIX_TOOL.name)
    async def toolcall_write_segment_priority_matrix(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await segment_qualification_tools.handle_write_segment_priority_matrix(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(segment_qualification_tools.WRITE_PRIMARY_SEGMENT_DECISION_TOOL.name)
    async def toolcall_write_primary_segment_decision(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await segment_qualification_tools.handle_write_primary_segment_decision(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(segment_qualification_tools.WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL.name)
    async def toolcall_write_primary_segment_go_no_go_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await segment_qualification_tools.handle_write_primary_segment_go_no_go_gate(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=segment_qualification_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=segment_qualification_install.install,
    ))


if __name__ == "__main__":
    main()
