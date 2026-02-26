import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.pilot_delivery_bot import pilot_delivery_install
from flexus_simple_bots.pilot_delivery_bot import pilot_delivery_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_pilot_delivery")

BOT_NAME = "pilot_delivery_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *pilot_delivery_tools.API_TOOLS,
    *pilot_delivery_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def pilot_delivery_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(pilot_delivery_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(pilot_delivery_tools.PILOT_CONTRACTING_TOOL.name)
    async def toolcall_pilot_contracting(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pilot_delivery_tools.handle_api_tool_call(pilot_delivery_tools.PILOT_CONTRACTING_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pilot_delivery_tools.PILOT_DELIVERY_OPS_TOOL.name)
    async def toolcall_pilot_delivery_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pilot_delivery_tools.handle_api_tool_call(pilot_delivery_tools.PILOT_DELIVERY_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pilot_delivery_tools.PILOT_USAGE_EVIDENCE_TOOL.name)
    async def toolcall_pilot_usage_evidence(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pilot_delivery_tools.handle_api_tool_call(pilot_delivery_tools.PILOT_USAGE_EVIDENCE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pilot_delivery_tools.PILOT_STAKEHOLDER_SYNC_TOOL.name)
    async def toolcall_pilot_stakeholder_sync(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pilot_delivery_tools.handle_api_tool_call(pilot_delivery_tools.PILOT_STAKEHOLDER_SYNC_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_PILOT_CONTRACT_PACKET_TOOL.name)
    async def toolcall_write_pilot_contract_packet(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_pilot_contract_packet(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL.name)
    async def toolcall_write_pilot_risk_clause_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_pilot_risk_clause_register(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_PILOT_GO_LIVE_READINESS_TOOL.name)
    async def toolcall_write_pilot_go_live_readiness(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_pilot_go_live_readiness(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL.name)
    async def toolcall_write_first_value_delivery_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_first_value_delivery_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_FIRST_VALUE_EVIDENCE_TOOL.name)
    async def toolcall_write_first_value_evidence(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_first_value_evidence(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pilot_delivery_tools.WRITE_PILOT_EXPANSION_READINESS_TOOL.name)
    async def toolcall_write_pilot_expansion_readiness(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pilot_delivery_tools.handle_write_pilot_expansion_readiness(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=pilot_delivery_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=pilot_delivery_install.install,
    ))


if __name__ == "__main__":
    main()
