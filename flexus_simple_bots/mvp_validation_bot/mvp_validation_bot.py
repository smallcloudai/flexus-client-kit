import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.mvp_validation_bot import mvp_validation_install
from flexus_simple_bots.mvp_validation_bot import mvp_validation_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_mvp_validation")

BOT_NAME = "mvp_validation_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *mvp_validation_tools.API_TOOLS,
    *mvp_validation_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def mvp_validation_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(mvp_validation_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(mvp_validation_tools.MVP_EXPERIMENT_ORCHESTRATION_TOOL.name)
    async def toolcall_mvp_experiment_orchestration(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await mvp_validation_tools.handle_api_tool_call(mvp_validation_tools.MVP_EXPERIMENT_ORCHESTRATION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(mvp_validation_tools.MVP_TELEMETRY_TOOL.name)
    async def toolcall_mvp_telemetry(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await mvp_validation_tools.handle_api_tool_call(mvp_validation_tools.MVP_TELEMETRY_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(mvp_validation_tools.MVP_FEEDBACK_CAPTURE_TOOL.name)
    async def toolcall_mvp_feedback_capture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await mvp_validation_tools.handle_api_tool_call(mvp_validation_tools.MVP_FEEDBACK_CAPTURE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(mvp_validation_tools.MVP_INSTRUMENTATION_HEALTH_TOOL.name)
    async def toolcall_mvp_instrumentation_health(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await mvp_validation_tools.handle_api_tool_call(mvp_validation_tools.MVP_INSTRUMENTATION_HEALTH_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_MVP_RUN_LOG_TOOL.name)
    async def toolcall_write_mvp_run_log(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_mvp_run_log(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_MVP_ROLLOUT_INCIDENT_TOOL.name)
    async def toolcall_write_mvp_rollout_incident(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_mvp_rollout_incident(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_MVP_FEEDBACK_DIGEST_TOOL.name)
    async def toolcall_write_mvp_feedback_digest(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_mvp_feedback_digest(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_TELEMETRY_QUALITY_REPORT_TOOL.name)
    async def toolcall_write_telemetry_quality_report(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_telemetry_quality_report(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_TELEMETRY_DECISION_MEMO_TOOL.name)
    async def toolcall_write_telemetry_decision_memo(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_telemetry_decision_memo(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(mvp_validation_tools.WRITE_MVP_SCALE_READINESS_GATE_TOOL.name)
    async def toolcall_write_mvp_scale_readiness_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await mvp_validation_tools.handle_write_mvp_scale_readiness_gate(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=mvp_validation_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=mvp_validation_install.install,
    ))


if __name__ == "__main__":
    main()
