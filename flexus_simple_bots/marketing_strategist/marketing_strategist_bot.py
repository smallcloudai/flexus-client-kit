"""
Marketing Strategist Bot

Reference implementation of the two-layer bot architecture:
- Persona Layer: defines bot identity and work pattern (marketing_strategist_persona.py)
- Skills Layer: isolated domain expertise modules (skills/*.py)

Key differences from legacy orchestrator pattern:
- No orchestrator tools (run_agent, save_input, rerun_agent, get_pipeline_status)
- No pipeline management logic
- User selects skills directly via UI buttons
- Each skill runs independently with its own system prompt and tools

Tool Architecture:
- TOOL_REGISTRY: centralized registry of all available tools
- Each skill declares SKILL_TOOLS = ["pdoc", ...] listing tools it needs
- install.py resolves tool names to actual tool objects via get_tools_for_skill()
- This enables per-skill tool access control with minimal code duplication

This file contains bot infrastructure, tool registry, and main loop.
"""

import asyncio
import logging
from typing import Dict, Any, List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.marketing_strategist import marketing_strategist_install

logger = logging.getLogger("bot_marketing_strategist")

BOT_NAME = "marketing_strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


# =============================================================================
# TOOL REGISTRY
# =============================================================================
# Centralized registry of all tools available to this bot.
# Each skill declares which tools it needs by name (SKILL_TOOLS = ["pdoc", ...]).
# install.py uses get_tools_for_skill() to resolve names to actual tool objects.
#
# To add a new tool:
# 1. Import the tool module
# 2. Add entry to TOOL_REGISTRY: "short_name": tool_module.TOOL_OBJECT
# 3. Add handler in main_loop for the new tool
# 4. Add "short_name" to SKILL_TOOLS in skills that need it
# =============================================================================

TOOL_REGISTRY: Dict[str, ckit_cloudtool.CloudTool] = {
    # Policy document tool -- read/write structured documents
    "pdoc": fi_pdoc.POLICY_DOCUMENT_TOOL,
    # Future tools (uncomment when implemented):
    # "web_search": web_research.SEARCH_TOOL,
    # "ad_platform": ad_platform.META_ADS_TOOL,
}


def get_tools_for_skill(skill_tools: List[str]) -> List[ckit_cloudtool.CloudTool]:
    """
    Resolve tool names to actual tool objects.

    Args:
        skill_tools: List of tool names from skill's SKILL_TOOLS

    Returns:
        List of CloudTool objects for the skill

    Raises:
        KeyError: If skill requests unknown tool (fail-fast, catches typos)
    """
    result = []
    for name in skill_tools:
        if name not in TOOL_REGISTRY:
            raise KeyError(f"Unknown tool '{name}' requested. Available: {list(TOOL_REGISTRY.keys())}")
        result.append(TOOL_REGISTRY[name])
    return result


# All tools for main loop -- need handlers for each
TOOLS = list(TOOL_REGISTRY.values())


async def marketing_strategist_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    """
    Main loop for Marketing Strategist bot.

    This is a minimal loop that only handles tool calls.
    No orchestration logic -- skills are accessed directly via UI.
    """
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    # Event handlers for database updates (required by framework)
    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    # Tool call handler for policy document operations
    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(
        toolcall: ckit_cloudtool.FCloudtoolCall,
        args: Dict[str, Any],
    ) -> str:
        return await pdoc_integration.called_by_model(toolcall, args)

    # Main event loop
    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    """Entry point for running the bot."""
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(
        ckit_client.bot_service_name(BOT_NAME, BOT_VERSION),
        endpoint="/v1/jailed-bot",
    )
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=marketing_strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=marketing_strategist_install.install,
    ))


if __name__ == "__main__":
    main()
