import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.gtm_economics_rtm_bot import gtm_economics_rtm_install
from flexus_simple_bots.gtm_economics_rtm_bot import gtm_economics_rtm_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_gtm_economics_rtm")

BOT_NAME = "gtm_economics_rtm_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *gtm_economics_rtm_tools.API_TOOLS,
    *gtm_economics_rtm_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def gtm_economics_rtm_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(gtm_economics_rtm_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(gtm_economics_rtm_tools.GTM_UNIT_ECONOMICS_TOOL.name)
    async def toolcall_gtm_unit_economics(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await gtm_economics_rtm_tools.handle_api_tool_call(gtm_economics_rtm_tools.GTM_UNIT_ECONOMICS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(gtm_economics_rtm_tools.GTM_MEDIA_EFFICIENCY_TOOL.name)
    async def toolcall_gtm_media_efficiency(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await gtm_economics_rtm_tools.handle_api_tool_call(gtm_economics_rtm_tools.GTM_MEDIA_EFFICIENCY_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(gtm_economics_rtm_tools.RTM_PIPELINE_FINANCE_TOOL.name)
    async def toolcall_rtm_pipeline_finance(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await gtm_economics_rtm_tools.handle_api_tool_call(gtm_economics_rtm_tools.RTM_PIPELINE_FINANCE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(gtm_economics_rtm_tools.RTM_TERRITORY_POLICY_TOOL.name)
    async def toolcall_rtm_territory_policy(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await gtm_economics_rtm_tools.handle_api_tool_call(gtm_economics_rtm_tools.RTM_TERRITORY_POLICY_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_UNIT_ECONOMICS_REVIEW_TOOL.name)
    async def toolcall_write_unit_economics_review(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_unit_economics_review(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_CHANNEL_MARGIN_STACK_TOOL.name)
    async def toolcall_write_channel_margin_stack(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_channel_margin_stack(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_PAYBACK_READINESS_GATE_TOOL.name)
    async def toolcall_write_payback_readiness_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_payback_readiness_gate(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_RTM_RULES_TOOL.name)
    async def toolcall_write_rtm_rules(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_rtm_rules(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_DEAL_OWNERSHIP_MATRIX_TOOL.name)
    async def toolcall_write_deal_ownership_matrix(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_deal_ownership_matrix(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(gtm_economics_rtm_tools.WRITE_RTM_CONFLICT_PLAYBOOK_TOOL.name)
    async def toolcall_write_rtm_conflict_playbook(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await gtm_economics_rtm_tools.handle_write_rtm_conflict_playbook(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=gtm_economics_rtm_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=gtm_economics_rtm_install.install,
    ))


if __name__ == "__main__":
    main()
