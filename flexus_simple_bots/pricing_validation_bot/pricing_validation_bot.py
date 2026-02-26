import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.pricing_validation_bot import pricing_validation_install
from flexus_simple_bots.pricing_validation_bot import pricing_validation_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_pricing_validation")

BOT_NAME = "pricing_validation_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *pricing_validation_tools.API_TOOLS,
    *pricing_validation_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def pricing_validation_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(pricing_validation_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(pricing_validation_tools.PRICING_RESEARCH_OPS_TOOL.name)
    async def toolcall_pricing_research_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pricing_validation_tools.handle_api_tool_call(pricing_validation_tools.PRICING_RESEARCH_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pricing_validation_tools.PRICING_COMMITMENT_EVENTS_TOOL.name)
    async def toolcall_pricing_commitment_events(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pricing_validation_tools.handle_api_tool_call(pricing_validation_tools.PRICING_COMMITMENT_EVENTS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pricing_validation_tools.PRICING_SALES_SIGNAL_TOOL.name)
    async def toolcall_pricing_sales_signal(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pricing_validation_tools.handle_api_tool_call(pricing_validation_tools.PRICING_SALES_SIGNAL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pricing_validation_tools.PRICING_CATALOG_BENCHMARK_TOOL.name)
    async def toolcall_pricing_catalog_benchmark(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await pricing_validation_tools.handle_api_tool_call(pricing_validation_tools.PRICING_CATALOG_BENCHMARK_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_PRICE_CORRIDOR_TOOL.name)
    async def toolcall_write_price_corridor(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_price_corridor(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_PRICE_SENSITIVITY_CURVE_TOOL.name)
    async def toolcall_write_price_sensitivity_curve(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_price_sensitivity_curve(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_PRICING_ASSUMPTION_REGISTER_TOOL.name)
    async def toolcall_write_pricing_assumption_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_pricing_assumption_register(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL.name)
    async def toolcall_write_pricing_commitment_evidence(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_pricing_commitment_evidence(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL.name)
    async def toolcall_write_validated_price_hypothesis(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_validated_price_hypothesis(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(pricing_validation_tools.WRITE_PRICING_GO_NO_GO_GATE_TOOL.name)
    async def toolcall_write_pricing_go_no_go_gate(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pricing_validation_tools.handle_write_pricing_go_no_go_gate(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=pricing_validation_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=pricing_validation_install.install,
    ))


if __name__ == "__main__":
    main()
