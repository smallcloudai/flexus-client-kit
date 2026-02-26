import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.scale_governance_bot import scale_governance_install
from flexus_simple_bots.scale_governance_bot import scale_governance_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_scale_governance")

BOT_NAME = "scale_governance_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *scale_governance_tools.API_TOOLS,
    *scale_governance_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def scale_governance_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(scale_governance_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(scale_governance_tools.PLAYBOOK_REPO_TOOL.name)
    async def toolcall_playbook_repo(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await scale_governance_tools.handle_api_tool_call(scale_governance_tools.PLAYBOOK_REPO_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(scale_governance_tools.SCALE_GUARDRAIL_MONITORING_TOOL.name)
    async def toolcall_scale_guardrail_monitoring(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await scale_governance_tools.handle_api_tool_call(scale_governance_tools.SCALE_GUARDRAIL_MONITORING_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(scale_governance_tools.SCALE_CHANGE_EXECUTION_TOOL.name)
    async def toolcall_scale_change_execution(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await scale_governance_tools.handle_api_tool_call(scale_governance_tools.SCALE_CHANGE_EXECUTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(scale_governance_tools.SCALE_INCIDENT_RESPONSE_TOOL.name)
    async def toolcall_scale_incident_response(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await scale_governance_tools.handle_api_tool_call(scale_governance_tools.SCALE_INCIDENT_RESPONSE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(scale_governance_tools.WRITE_PLAYBOOK_LIBRARY_TOOL.name)
    async def toolcall_write_playbook_library(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_playbook_library(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(scale_governance_tools.WRITE_PLAYBOOK_CHANGE_LOG_TOOL.name)
    async def toolcall_write_playbook_change_log(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_playbook_change_log(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(scale_governance_tools.WRITE_OPERATING_SOP_COMPLIANCE_TOOL.name)
    async def toolcall_write_operating_sop_compliance(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_operating_sop_compliance(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(scale_governance_tools.WRITE_SCALE_INCREMENT_PLAN_TOOL.name)
    async def toolcall_write_scale_increment_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_scale_increment_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(scale_governance_tools.WRITE_SCALE_ROLLBACK_DECISION_TOOL.name)
    async def toolcall_write_scale_rollback_decision(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_scale_rollback_decision(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(scale_governance_tools.WRITE_GUARDRAIL_BREACH_INCIDENT_TOOL.name)
    async def toolcall_write_guardrail_breach_incident(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await scale_governance_tools.handle_write_guardrail_breach_incident(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=scale_governance_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=scale_governance_install.install,
    ))


if __name__ == "__main__":
    main()
