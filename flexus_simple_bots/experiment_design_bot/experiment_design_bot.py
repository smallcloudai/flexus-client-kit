import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.experiment_design_bot import experiment_design_install
from flexus_simple_bots.experiment_design_bot import experiment_design_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_experiment_design")

BOT_NAME = "experiment_design_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *experiment_design_tools.API_TOOLS,
    *experiment_design_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def experiment_design_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(experiment_design_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(experiment_design_tools.EXPERIMENT_BACKLOG_OPS_TOOL.name)
    async def toolcall_backlog_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await experiment_design_tools.handle_api_tool_call(experiment_design_tools.EXPERIMENT_BACKLOG_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(experiment_design_tools.EXPERIMENT_RUNTIME_CONFIG_TOOL.name)
    async def toolcall_runtime_config(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await experiment_design_tools.handle_api_tool_call(experiment_design_tools.EXPERIMENT_RUNTIME_CONFIG_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(experiment_design_tools.EXPERIMENT_GUARDRAIL_METRICS_TOOL.name)
    async def toolcall_guardrail_metrics(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await experiment_design_tools.handle_api_tool_call(experiment_design_tools.EXPERIMENT_GUARDRAIL_METRICS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(experiment_design_tools.EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL.name)
    async def toolcall_instrumentation_quality(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await experiment_design_tools.handle_api_tool_call(experiment_design_tools.EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_CARD_DRAFT_TOOL.name)
    async def toolcall_write_card_draft(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_card_draft(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL.name)
    async def toolcall_write_measurement_spec(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_measurement_spec(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL.name)
    async def toolcall_write_backlog_prioritization(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_backlog_prioritization(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL.name)
    async def toolcall_write_reliability_report(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_reliability_report(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_APPROVAL_TOOL.name)
    async def toolcall_write_approval(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_approval(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(experiment_design_tools.WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL.name)
    async def toolcall_write_stop_rule_evaluation(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_design_tools.handle_write_experiment_stop_rule_evaluation(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=experiment_design_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=experiment_design_install.install,
    ))


if __name__ == "__main__":
    main()
