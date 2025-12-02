import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_owl_strategist")


BOT_NAME = "owl_strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

AGENTS = ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]

AGENT_DESCRIPTIONS = {
    "diagnostic": "Diagnostic Analysis — classifying hypothesis, identifying unknowns",
    "metrics": "Metrics Framework — defining KPIs, stop-rules, MDE",
    "segment": "Segment Analysis — ICP, JTBD, customer journey",
    "messaging": "Messaging Strategy — value proposition, angles",
    "channels": "Channel Strategy — channel selection, test cells",
    "tactics": "Tactical Spec — campaigns, creatives, landing",
    "compliance": "Risk & Compliance — policies, privacy, risks",
}


RUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    name="run_agent",
    description="Run specific agent. Call ONLY after discussing with user what will be done.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "kebab-case strategy name"},
            "agent": {
                "type": "string",
                "enum": AGENTS,
                "description": "Which agent to run",
            },
            "user_additions": {"type": "string", "description": "Important context from user to consider"},
        },
        "required": ["strategy_name", "agent"],
    },
)

RERUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    name="rerun_agent",
    description="Rerun agent with corrections after user feedback.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "Strategy name"},
            "agent": {
                "type": "string",
                "enum": AGENTS,
            },
            "feedback": {"type": "string", "description": "What to change based on user feedback"},
        },
        "required": ["strategy_name", "agent", "feedback"],
    },
)

TOOLS = [
    RUN_AGENT_TOOL,
    RERUN_AGENT_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]

# Tools for agent subchats — no orchestration tools (run_agent, rerun_agent)
AGENT_TOOLS = [
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def owl_strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
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

    @rcx.on_tool_call(RUN_AGENT_TOOL.name)
    async def toolcall_run_agent(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        strategy_name = args.get("strategy_name", "")
        agent = args.get("agent", "")
        user_additions = args.get("user_additions", "")

        if not strategy_name:
            return "Error: strategy_name is required"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"

        # Build first question for subchat
        q = f"Strategy: {strategy_name}\n\nAnalyze and save result to /strategies/{strategy_name}/{agent}.json"
        if user_additions:
            q += f"\n\nUser context to consider:\n{user_additions}"

        logger.info(f"Starting agent '{agent}' for strategy '{strategy_name}'")

        await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking=f"owl_{agent}",
            persona_id=rcx.persona.persona_id,
            first_question=[q],
            first_calls=["null"],
            title=[AGENT_DESCRIPTIONS.get(agent, agent)],
            fcall_id=toolcall.fcall_id,
            skill=agent,
        )
        raise ckit_cloudtool.WaitForSubchats()

    @rcx.on_tool_call(RERUN_AGENT_TOOL.name)
    async def toolcall_rerun_agent(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        strategy_name = args.get("strategy_name", "")
        agent = args.get("agent", "")
        feedback = args.get("feedback", "")

        if not strategy_name:
            return "Error: strategy_name is required"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"
        if not feedback:
            return "Error: feedback is required for rerun"

        # Build first question with feedback
        q = f"""Strategy: {strategy_name}

RERUN with corrections. Previous result needs changes:
{feedback}

Read previous result from /strategies/{strategy_name}/{agent}.json, apply the feedback, and save updated result to the same path."""

        logger.info(f"Rerunning agent '{agent}' for strategy '{strategy_name}' with feedback")

        await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking=f"owl_{agent}_rerun",
            persona_id=rcx.persona.persona_id,
            first_question=[q],
            first_calls=["null"],
            title=[f"Rerun: {AGENT_DESCRIPTIONS.get(agent, agent)}"],
            fcall_id=toolcall.fcall_id,
            skill=agent,
        )
        raise ckit_cloudtool.WaitForSubchats()

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group, scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(
        ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group),
        endpoint="/v1/jailed-bot",
    )
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=owl_strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
    ))


if __name__ == "__main__":
    main()
