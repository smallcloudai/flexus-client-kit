import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.pipeline_qualification_bot import pipeline_qualification_install
from flexus_simple_bots.pipeline_qualification_bot import pipeline_qualification_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_pipeline_qualification")

BOT_NAME = "pipeline_qualification_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *pipeline_qualification_tools.API_TOOLS,
    *pipeline_qualification_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def pipeline_qualification_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(pipeline_qualification_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(pipeline_qualification_tools.PIPELINE_CRM_TOOL.name)
    async def toolcall_pipeline_crm(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pipeline_qualification_tools.handle_api_tool_call(pipeline_qualification_tools.PIPELINE_CRM_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pipeline_qualification_tools.PIPELINE_PROSPECTING_ENRICHMENT_TOOL.name)
    async def toolcall_pipeline_prospecting_enrichment(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pipeline_qualification_tools.handle_api_tool_call(pipeline_qualification_tools.PIPELINE_PROSPECTING_ENRICHMENT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pipeline_qualification_tools.PIPELINE_OUTREACH_EXECUTION_TOOL.name)
    async def toolcall_pipeline_outreach_execution(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pipeline_qualification_tools.handle_api_tool_call(pipeline_qualification_tools.PIPELINE_OUTREACH_EXECUTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pipeline_qualification_tools.PIPELINE_ENGAGEMENT_SIGNAL_TOOL.name)
    async def toolcall_pipeline_engagement_signal(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pipeline_qualification_tools.handle_api_tool_call(pipeline_qualification_tools.PIPELINE_ENGAGEMENT_SIGNAL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_PROSPECTING_BATCH_TOOL.name)
    async def toolcall_write_prospecting_batch(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_prospecting_batch(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_OUTREACH_EXECUTION_LOG_TOOL.name)
    async def toolcall_write_outreach_execution_log(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_outreach_execution_log(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_PROSPECT_DATA_QUALITY_TOOL.name)
    async def toolcall_write_prospect_data_quality(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_prospect_data_quality(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_QUALIFICATION_MAP_TOOL.name)
    async def toolcall_write_qualification_map(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_qualification_map(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_BUYING_COMMITTEE_COVERAGE_TOOL.name)
    async def toolcall_write_buying_committee_coverage(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_buying_committee_coverage(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pipeline_qualification_tools.WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL.name)
    async def toolcall_write_qualification_go_no_go_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pipeline_qualification_tools.handle_write_qualification_go_no_go_gate(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=pipeline_qualification_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=pipeline_qualification_install.install,
    ))


if __name__ == "__main__":
    main()
