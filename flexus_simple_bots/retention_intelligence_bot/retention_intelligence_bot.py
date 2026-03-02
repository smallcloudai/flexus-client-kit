import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.retention_intelligence_bot import retention_intelligence_install
from flexus_simple_bots.retention_intelligence_bot import retention_intelligence_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_retention_intelligence")

BOT_NAME = "retention_intelligence_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *retention_intelligence_tools.API_TOOLS,
    *retention_intelligence_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def retention_intelligence_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(retention_intelligence_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(retention_intelligence_tools.RETENTION_REVENUE_EVENTS_TOOL.name)
    async def toolcall_retention_revenue_events(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await retention_intelligence_tools.handle_retention_tool_call(retention_intelligence_tools.RETENTION_REVENUE_EVENTS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(retention_intelligence_tools.RETENTION_PRODUCT_ANALYTICS_TOOL.name)
    async def toolcall_retention_product_analytics(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await retention_intelligence_tools.handle_retention_tool_call(retention_intelligence_tools.RETENTION_PRODUCT_ANALYTICS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(retention_intelligence_tools.RETENTION_FEEDBACK_RESEARCH_TOOL.name)
    async def toolcall_retention_feedback_research(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await retention_intelligence_tools.handle_retention_tool_call(retention_intelligence_tools.RETENTION_FEEDBACK_RESEARCH_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(retention_intelligence_tools.RETENTION_ACCOUNT_CONTEXT_TOOL.name)
    async def toolcall_retention_account_context(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await retention_intelligence_tools.handle_retention_tool_call(retention_intelligence_tools.RETENTION_ACCOUNT_CONTEXT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_COHORT_REVENUE_REVIEW_TOOL.name)
    async def toolcall_write_cohort_revenue_review(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_cohort_revenue_review(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_RETENTION_DRIVER_MATRIX_TOOL.name)
    async def toolcall_write_retention_driver_matrix(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_retention_driver_matrix(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_RETENTION_READINESS_GATE_TOOL.name)
    async def toolcall_write_retention_readiness_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_retention_readiness_gate(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_PMF_CONFIDENCE_SCORECARD_TOOL.name)
    async def toolcall_write_pmf_confidence_scorecard(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_pmf_confidence_scorecard(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_PMF_SIGNAL_EVIDENCE_TOOL.name)
    async def toolcall_write_pmf_signal_evidence(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_pmf_signal_evidence(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(retention_intelligence_tools.WRITE_PMF_RESEARCH_BACKLOG_TOOL.name)
    async def toolcall_write_pmf_research_backlog(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await retention_intelligence_tools.handle_write_pmf_research_backlog(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=retention_intelligence_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=retention_intelligence_install.install,
    ))


if __name__ == "__main__":
    main()
