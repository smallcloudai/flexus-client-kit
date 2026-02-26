import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.pain_alternatives_bot import pain_alternatives_install
from flexus_simple_bots.pain_alternatives_bot import pain_alternatives_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_pain_alternatives")

BOT_NAME = "pain_alternatives_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *pain_alternatives_tools.API_TOOLS,
    *pain_alternatives_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def pain_alternatives_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(pain_alternatives_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(pain_alternatives_tools.PAIN_VOICE_OF_CUSTOMER_TOOL.name)
    async def toolcall_pain_voice_of_customer(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pain_alternatives_tools.handle_api_tool_call(pain_alternatives_tools.PAIN_VOICE_OF_CUSTOMER_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pain_alternatives_tools.PAIN_SUPPORT_SIGNAL_TOOL.name)
    async def toolcall_pain_support_signal(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pain_alternatives_tools.handle_api_tool_call(pain_alternatives_tools.PAIN_SUPPORT_SIGNAL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pain_alternatives_tools.ALTERNATIVES_MARKET_SCAN_TOOL.name)
    async def toolcall_alternatives_market_scan(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pain_alternatives_tools.handle_api_tool_call(pain_alternatives_tools.ALTERNATIVES_MARKET_SCAN_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pain_alternatives_tools.ALTERNATIVES_TRACTION_BENCHMARK_TOOL.name)
    async def toolcall_alternatives_traction_benchmark(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pain_alternatives_tools.handle_api_tool_call(pain_alternatives_tools.ALTERNATIVES_TRACTION_BENCHMARK_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_PAIN_SIGNAL_REGISTER_TOOL.name)
    async def toolcall_write_pain_signal_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_pain_signal_register(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_PAIN_ECONOMICS_TOOL.name)
    async def toolcall_write_pain_economics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_pain_economics(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL.name)
    async def toolcall_write_pain_research_readiness_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_pain_research_readiness_gate(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_ALTERNATIVE_LANDSCAPE_TOOL.name)
    async def toolcall_write_alternative_landscape(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_alternative_landscape(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_COMPETITIVE_GAP_MATRIX_TOOL.name)
    async def toolcall_write_competitive_gap_matrix(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_competitive_gap_matrix(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pain_alternatives_tools.WRITE_DISPLACEMENT_HYPOTHESES_TOOL.name)
    async def toolcall_write_displacement_hypotheses(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pain_alternatives_tools.handle_write_displacement_hypotheses(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=pain_alternatives_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=pain_alternatives_install.install,
    ))


if __name__ == "__main__":
    main()
