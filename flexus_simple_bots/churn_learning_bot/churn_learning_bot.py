import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.churn_learning_bot import churn_learning_install
from flexus_simple_bots.churn_learning_bot import churn_learning_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_churn_learning")

BOT_NAME = "churn_learning_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *churn_learning_tools.API_TOOLS,
    *churn_learning_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def churn_learning_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(churn_learning_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(churn_learning_tools.CHURN_FEEDBACK_CAPTURE_TOOL.name)
    async def toolcall_feedback_capture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await churn_learning_tools.handle_api_tool_call(churn_learning_tools.CHURN_FEEDBACK_CAPTURE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(churn_learning_tools.CHURN_INTERVIEW_OPS_TOOL.name)
    async def toolcall_interview_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await churn_learning_tools.handle_api_tool_call(churn_learning_tools.CHURN_INTERVIEW_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(churn_learning_tools.CHURN_TRANSCRIPT_ANALYSIS_TOOL.name)
    async def toolcall_transcript_analysis(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await churn_learning_tools.handle_api_tool_call(churn_learning_tools.CHURN_TRANSCRIPT_ANALYSIS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(churn_learning_tools.CHURN_REMEDIATION_BACKLOG_TOOL.name)
    async def toolcall_remediation_backlog(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await churn_learning_tools.handle_api_tool_call(churn_learning_tools.CHURN_REMEDIATION_BACKLOG_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(churn_learning_tools.WRITE_INTERVIEW_CORPUS_TOOL.name)
    async def toolcall_write_interview_corpus(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_interview_corpus(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(churn_learning_tools.WRITE_INTERVIEW_COVERAGE_TOOL.name)
    async def toolcall_write_interview_coverage(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_interview_coverage(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(churn_learning_tools.WRITE_SIGNAL_QUALITY_TOOL.name)
    async def toolcall_write_signal_quality(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_signal_quality(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(churn_learning_tools.WRITE_ROOTCAUSE_BACKLOG_TOOL.name)
    async def toolcall_write_rootcause_backlog(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_rootcause_backlog(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(churn_learning_tools.WRITE_FIX_EXPERIMENT_PLAN_TOOL.name)
    async def toolcall_write_fix_experiment_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_fix_experiment_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(churn_learning_tools.WRITE_PREVENTION_GATE_TOOL.name)
    async def toolcall_write_prevention_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await churn_learning_tools.handle_write_prevention_gate(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=churn_learning_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=churn_learning_install.install,
    ))


if __name__ == "__main__":
    main()
