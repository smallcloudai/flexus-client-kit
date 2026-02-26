import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.positioning_offer_bot import positioning_offer_install
from flexus_simple_bots.positioning_offer_bot import positioning_offer_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_positioning_offer")

BOT_NAME = "positioning_offer_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *positioning_offer_tools.API_TOOLS,
    *positioning_offer_tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def positioning_offer_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(positioning_offer_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(positioning_offer_tools.POSITIONING_MESSAGE_TEST_TOOL.name)
    async def toolcall_positioning_message_test(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await positioning_offer_tools.handle_api_tool_call(positioning_offer_tools.POSITIONING_MESSAGE_TEST_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(positioning_offer_tools.POSITIONING_COMPETITOR_INTEL_TOOL.name)
    async def toolcall_positioning_competitor_intel(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await positioning_offer_tools.handle_api_tool_call(positioning_offer_tools.POSITIONING_COMPETITOR_INTEL_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(positioning_offer_tools.OFFER_PACKAGING_BENCHMARK_TOOL.name)
    async def toolcall_offer_packaging_benchmark(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await positioning_offer_tools.handle_api_tool_call(positioning_offer_tools.OFFER_PACKAGING_BENCHMARK_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(positioning_offer_tools.POSITIONING_CHANNEL_PROBE_TOOL.name)
    async def toolcall_positioning_channel_probe(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await positioning_offer_tools.handle_api_tool_call(positioning_offer_tools.POSITIONING_CHANNEL_PROBE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_VALUE_PROPOSITION_TOOL.name)
    async def toolcall_write_value_proposition(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_value_proposition(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_OFFER_PACKAGING_TOOL.name)
    async def toolcall_write_offer_packaging(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_offer_packaging(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL.name)
    async def toolcall_write_positioning_narrative_brief(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_positioning_narrative_brief(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL.name)
    async def toolcall_write_messaging_experiment_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_messaging_experiment_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_POSITIONING_TEST_RESULT_TOOL.name)
    async def toolcall_write_positioning_test_result(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_positioning_test_result(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(positioning_offer_tools.WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL.name)
    async def toolcall_write_positioning_claim_risk_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await positioning_offer_tools.handle_write_positioning_claim_risk_register(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=positioning_offer_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=positioning_offer_install.install,
    ))


if __name__ == "__main__":
    main()
