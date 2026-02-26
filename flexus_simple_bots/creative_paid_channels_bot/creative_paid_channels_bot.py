import asyncio
import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.creative_paid_channels_bot import creative_paid_channels_install
from flexus_simple_bots.creative_paid_channels_bot import creative_paid_channels_tools as tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_creative_paid_channels")

BOT_NAME = "creative_paid_channels_bot"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

TOOLS = [
    *tools.API_TOOLS,
    *tools.WRITE_TOOLS,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_widget.PRINT_WIDGET_TOOL,
]


async def creative_paid_channels_bot_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    _ = ckit_bot_exec.official_setup_mixing_procedure(creative_paid_channels_install.SETUP_SCHEMA, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_widget.PRINT_WIDGET_TOOL.name)
    async def toolcall_print_widget(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_widget.handle_print_widget(toolcall, model_produced_args)

    @rcx.on_tool_call(tools.CREATIVE_ASSET_OPS_TOOL.name)
    async def toolcall_creative_asset_ops(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await tools.handle_api_tool_call(tools.CREATIVE_ASSET_OPS_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(tools.PAID_CHANNEL_EXECUTION_TOOL.name)
    async def toolcall_paid_channel_execution(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await tools.handle_api_tool_call(tools.PAID_CHANNEL_EXECUTION_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(tools.PAID_CHANNEL_MEASUREMENT_TOOL.name)
    async def toolcall_paid_channel_measurement(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await tools.handle_api_tool_call(tools.PAID_CHANNEL_MEASUREMENT_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(tools.CREATIVE_FEEDBACK_CAPTURE_TOOL.name)
    async def toolcall_creative_feedback_capture(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        return await tools.handle_api_tool_call(tools.CREATIVE_FEEDBACK_CAPTURE_TOOL.name, toolcall, model_produced_args)

    @rcx.on_tool_call(tools.WRITE_CREATIVE_VARIANT_PACK_TOOL.name)
    async def toolcall_write_creative_variant_pack(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_creative_variant_pack(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(tools.WRITE_CREATIVE_ASSET_MANIFEST_TOOL.name)
    async def toolcall_write_creative_asset_manifest(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_creative_asset_manifest(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(tools.WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL.name)
    async def toolcall_write_creative_claim_risk_register(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_creative_claim_risk_register(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(tools.WRITE_PAID_CHANNEL_TEST_PLAN_TOOL.name)
    async def toolcall_write_paid_channel_test_plan(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_paid_channel_test_plan(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(tools.WRITE_PAID_CHANNEL_RESULT_TOOL.name)
    async def toolcall_write_paid_channel_result(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_paid_channel_result(toolcall, args, pdoc_integration, rcx)

    @rcx.on_tool_call(tools.WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL.name)
    async def toolcall_write_paid_channel_budget_guardrail(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await tools.handle_write_paid_channel_budget_guardrail(toolcall, args, pdoc_integration, rcx)

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
        bot_main_loop=creative_paid_channels_bot_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=creative_paid_channels_install.install,
    ))


if __name__ == "__main__":
    main()
