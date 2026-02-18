import asyncio
import sys
import logging
import importlib
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("no_special_code_bot")


TOOLS = [
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def bot_main_loop(install_mod, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    ckit_bot_exec.official_setup_mixing_procedure(install_mod.setup_schema, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("Usage: python -m flexus_client_kit.no_special_code_bot <bot_module>")
        print("Example: python -m flexus_client_kit.no_special_code_bot flexus_simple_bots.otter.otter_install")
        sys.exit(1)
    mod_name = sys.argv.pop(1)
    install_mod = importlib.import_module(mod_name)
    bot_name = install_mod.BOT_NAME
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(bot_name, SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=bot_name,
        marketable_version_str=SIMPLE_BOTS_COMMON_VERSION,
        bot_main_loop=lambda fc, rcx: bot_main_loop(install_mod, fc, rcx),
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=install_mod.install,
    ))


if __name__ == "__main__":
    main()
