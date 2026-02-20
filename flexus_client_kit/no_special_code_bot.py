import asyncio
import sys
import logging
import importlib
from typing import Dict, Any, Callable, Awaitable

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_kanban   # TODO add default reactions to messengers (post to inbox)
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("no_special_code_bot")


ToolCalledByModel = Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[str]]


def _setup_pdoc(rcx: ckit_bot_exec.RobotContext) -> ToolCalledByModel:
    integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    return integration.called_by_model


def _setup_widget(rcx: ckit_bot_exec.RobotContext) -> ToolCalledByModel:
    return fi_widget.handle_print_widget


TOOL_REGISTRY: dict[str, tuple[ckit_cloudtool.CloudTool, Callable]] = {
    "flexus_policy_document": (fi_pdoc.POLICY_DOCUMENT_TOOL, _setup_pdoc),
    "print_widget": (fi_widget.PRINT_WIDGET_TOOL, _setup_widget),
}


def tool_registry_lookup(tool_names: list[str]) -> list[ckit_cloudtool.CloudTool]:
    tools = []
    for name in tool_names:
        if name not in TOOL_REGISTRY:
            raise ValueError(f"Unknown tool {name!r}, available: {list(TOOL_REGISTRY.keys())}")
        tools.append(TOOL_REGISTRY[name][0])
    return tools


async def bot_main_loop(install_mod, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    ckit_bot_exec.official_setup_mixing_procedure(install_mod.SETUP_SCHEMA, rcx.persona.persona_setup)
    for name in install_mod.TOOLS:
        tool, setup_fn = TOOL_REGISTRY[name]
        handler = setup_fn(rcx)
        rcx.on_tool_call(tool.name)(handler)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("Usage: python -m flexus_client_kit.no_special_code_bot <mybot_install>")
        print("Example: python -m flexus_client_kit.no_special_code_bot flexus_simple_bots.otter.otter_install")
        print("Module must export: BOT_NAME, SETUP_SCHEMA, TOOLS, install()")
        sys.exit(1)
    mod_name = sys.argv.pop(1)
    install_mod = importlib.import_module(mod_name)
    bot_name = install_mod.BOT_NAME
    tools = tool_registry_lookup(install_mod.TOOLS)
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(bot_name, SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=bot_name,
        marketable_version_str=SIMPLE_BOTS_COMMON_VERSION,
        bot_main_loop=lambda fc, rcx: bot_main_loop(install_mod, fc, rcx),
        inprocess_tools=tools,
        scenario_fn=scenario_fn,
        install_func=install_mod.install,
    ))


if __name__ == "__main__":
    main()
