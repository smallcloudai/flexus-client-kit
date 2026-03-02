import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.market_signal_bot import market_signal_install
from flexus_simple_bots.market_signal_bot import market_signal_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_market_signal")

BOT_NAME = "market_signal_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *market_signal_tools.SIGNAL_TOOLS,
    *market_signal_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def market_signal_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(market_signal_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_SEARCH_DEMAND_TOOL.name)
    async def toolcall_signal_search_demand(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_SEARCH_DEMAND_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_SOCIAL_TRENDS_TOOL.name)
    async def toolcall_signal_social_trends(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_SOCIAL_TRENDS_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_NEWS_EVENTS_TOOL.name)
    async def toolcall_signal_news_events(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_NEWS_EVENTS_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_REVIEW_VOICE_TOOL.name)
    async def toolcall_signal_review_voice(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_REVIEW_VOICE_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_MARKETPLACE_DEMAND_TOOL.name)
    async def toolcall_signal_marketplace_demand(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_MARKETPLACE_DEMAND_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_WEB_TRAFFIC_INTEL_TOOL.name)
    async def toolcall_signal_web_traffic_intel(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_WEB_TRAFFIC_INTEL_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_JOBS_DEMAND_TOOL.name)
    async def toolcall_signal_jobs_demand(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_JOBS_DEMAND_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_DEV_ECOSYSTEM_TOOL.name)
    async def toolcall_signal_dev_ecosystem(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_DEV_ECOSYSTEM_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_PUBLIC_INTEREST_TOOL.name)
    async def toolcall_signal_public_interest(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_PUBLIC_INTEREST_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.SIGNAL_PROFESSIONAL_NETWORK_TOOL.name)
    async def toolcall_signal_professional_network(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await market_signal_tools.handle_signal_tool_call(market_signal_tools.SIGNAL_PROFESSIONAL_NETWORK_TOOL.name, toolcall, model_produced_args, rcx)

    @rcx.on_tool_call(market_signal_tools.WRITE_SNAPSHOT_TOOL.name)
    async def toolcall_write_snapshot(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await market_signal_tools.handle_write_snapshot(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(market_signal_tools.WRITE_SIGNAL_REGISTER_TOOL.name)
    async def toolcall_write_signal_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await market_signal_tools.handle_write_signal_register(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(market_signal_tools.WRITE_HYPOTHESIS_BACKLOG_TOOL.name)
    async def toolcall_write_hypothesis_backlog(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await market_signal_tools.handle_write_hypothesis_backlog(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=market_signal_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=market_signal_install.install,
    ))


if __name__ == "__main__":
    main()
