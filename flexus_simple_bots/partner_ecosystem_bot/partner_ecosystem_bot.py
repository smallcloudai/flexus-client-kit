import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.partner_ecosystem_bot import partner_ecosystem_install
from flexus_simple_bots.partner_ecosystem_bot import partner_ecosystem_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_partner_ecosystem")

BOT_NAME = "partner_ecosystem_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *partner_ecosystem_tools.API_TOOLS,
    *partner_ecosystem_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def partner_ecosystem_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(partner_ecosystem_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(partner_ecosystem_tools.PARTNER_PROGRAM_OPS_TOOL.name)
    async def toolcall_partner_program_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await partner_ecosystem_tools.handle_api_tool_call(partner_ecosystem_tools.PARTNER_PROGRAM_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(partner_ecosystem_tools.PARTNER_ACCOUNT_MAPPING_TOOL.name)
    async def toolcall_partner_account_mapping(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await partner_ecosystem_tools.handle_api_tool_call(partner_ecosystem_tools.PARTNER_ACCOUNT_MAPPING_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(partner_ecosystem_tools.PARTNER_ENABLEMENT_EXECUTION_TOOL.name)
    async def toolcall_partner_enablement_execution(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await partner_ecosystem_tools.handle_api_tool_call(partner_ecosystem_tools.PARTNER_ENABLEMENT_EXECUTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(partner_ecosystem_tools.CHANNEL_CONFLICT_GOVERNANCE_TOOL.name)
    async def toolcall_channel_conflict_governance(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await partner_ecosystem_tools.handle_api_tool_call(partner_ecosystem_tools.CHANNEL_CONFLICT_GOVERNANCE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL.name)
    async def toolcall_write_activation_scorecard(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_partner_activation_scorecard(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_PARTNER_ENABLEMENT_PLAN_TOOL.name)
    async def toolcall_write_enablement_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_partner_enablement_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_PARTNER_PIPELINE_QUALITY_TOOL.name)
    async def toolcall_write_pipeline_quality(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_partner_pipeline_quality(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL.name)
    async def toolcall_write_conflict_incident(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_channel_conflict_incident(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_DEAL_REGISTRATION_POLICY_TOOL.name)
    async def toolcall_write_deal_registration_policy(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_deal_registration_policy(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(partner_ecosystem_tools.WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL.name)
    async def toolcall_write_conflict_resolution_audit(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await partner_ecosystem_tools.handle_write_conflict_resolution_audit(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=partner_ecosystem_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=partner_ecosystem_install.install,
    ))


if __name__ == "__main__":
    main()
