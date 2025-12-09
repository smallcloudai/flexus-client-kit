import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.owl_strategist import owl_strategist_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.owl_strategist import owl_strategist_install
from flexus_simple_bots.owl_strategist.skills import diagnostic as skill_diagnostic

logger = logging.getLogger("bot_owl_strategist")


BOT_NAME = "owl_strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

# Pipeline: strict sequential order
PIPELINE = ["input", "diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]

AGENTS = ["diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]

# Import descriptions from skill modules
AGENT_DESCRIPTIONS = {
    "diagnostic": skill_diagnostic.SKILL_DESCRIPTION,
    "metrics": "Metrics Framework — defining KPIs, stop-rules, MDE",
    "segment": "Segment Analysis — ICP, JTBD, customer journey",
    "messaging": "Messaging Strategy — value proposition, angles",
    "channels": "Channel Strategy — channel selection, test cells",
    "tactics": "Tactical Spec — campaigns, creatives, landing",
    "compliance": "Risk & Compliance — policies, privacy, risks",
}

STEP_DESCRIPTIONS = {
    "input": "Сбор входных данных — продукт, гипотеза, бюджет, сроки",
    **AGENT_DESCRIPTIONS,
}


SAVE_INPUT_TOOL = ckit_cloudtool.CloudTool(
    name="save_input",
    description="Save collected input data to start the strategy pipeline. Call after collecting product/hypothesis/budget/timeline from user.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "kebab-case strategy name, should relate to hypothesis source"},
            "product_description": {"type": "string", "description": "What the product/service does"},
            "hypothesis": {"type": "string", "description": "What we want to test"},
            "stage": {"type": "string", "enum": ["idea", "mvp", "scaling"], "description": "Current stage"},
            "budget": {"type": "string", "description": "Budget constraints"},
            "timeline": {"type": "string", "description": "Timeline expectations"},
            "additional_context": {"type": "string", "description": "Any other relevant context"},
            "hypothesis_source": {"type": "string", "description": "Path to source doc if hypothesis came from /customer-research/, e.g. /customer-research/b2b-saas/hypothesis"},
        },
        "required": ["strategy_name", "product_description", "hypothesis", "stage"],
    },
)

RUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    name="run_agent",
    description="Run specific agent. Pipeline is strictly sequential: input → diagnostic → metrics → segment → messaging → channels → tactics → compliance. Each step requires previous step completed.",
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
    description="Rerun agent with corrections after user feedback. Does not change pipeline position.",
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

GET_PIPELINE_STATUS_TOOL = ckit_cloudtool.CloudTool(
    name="get_pipeline_status",
    description="Get current pipeline status for a strategy — which steps are done, which is next.",
    parameters={
        "type": "object",
        "properties": {
            "strategy_name": {"type": "string", "description": "Strategy name"},
        },
        "required": ["strategy_name"],
    },
)

TOOLS = [
    SAVE_INPUT_TOOL,
    RUN_AGENT_TOOL,
    RERUN_AGENT_TOOL,
    GET_PIPELINE_STATUS_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]

AGENT_TOOLS = [
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def owl_strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    fuser_id = rcx.persona.persona_id

    # Protection against duplicate tool call processing (race condition fix)
    processed_fcalls: set = set()

    async def step_exists(strategy_name: str, step: str) -> bool:
        try:
            await pdoc_integration.pdoc_cat(f"/strategies/{strategy_name}/{step}", fuser_id)
            return True
        except Exception:
            return False

    async def get_pipeline_status(strategy_name: str) -> Dict[str, Any]:
        completed = []
        for step in PIPELINE:
            if await step_exists(strategy_name, step):
                completed.append(step)
            else:
                break
        next_step = PIPELINE[len(completed)] if len(completed) < len(PIPELINE) else None
        return {
            "completed": completed,
            "next_step": next_step,
            "all_done": len(completed) == len(PIPELINE),
        }

    async def check_can_run_agent(strategy_name: str, agent: str) -> Optional[str]:
        agent_idx = PIPELINE.index(agent)
        if agent_idx == 0:
            return None
        prev_step = PIPELINE[agent_idx - 1]
        if not await step_exists(strategy_name, prev_step):
            return f"Нельзя запустить {agent} — сначала нужно завершить {prev_step}. Порядок: {' → '.join(PIPELINE)}"
        return None

    # What documents each agent needs as input
    AGENT_REQUIRED_DOCS = {
        "diagnostic": ["input"],
        "metrics": ["input", "diagnostic"],
        "segment": ["input", "diagnostic"],
        "messaging": ["input", "diagnostic", "segment"],
        "channels": ["input", "diagnostic", "metrics", "segment", "messaging"],
        "tactics": ["input", "diagnostic", "metrics", "segment", "messaging", "channels"],
        "compliance": ["input", "tactics"],
    }

    async def _load_agent_context(pdoc: fi_pdoc.IntegrationPdoc, fuser_id: str, strategy_name: str, agent: str) -> Dict[str, Any]:
        required = AGENT_REQUIRED_DOCS.get(agent, ["input"])
        docs = {}
        for doc_name in required:
            try:
                content = await pdoc.pdoc_cat(f"/strategies/{strategy_name}/{doc_name}", fuser_id)
                docs[doc_name] = content
            except Exception as e:
                return {"error": f"Cannot run {agent}: missing required document '{doc_name}'. Error: {e}"}

        # Format as readable context
        lines = ["## Input Documents"]
        for doc_name, content in docs.items():
            lines.append(f"\n### {doc_name}\n```json\n{content}\n```")
        return {"content": "\n".join(lines)}

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_tool_call(SAVE_INPUT_TOOL.name)
    async def toolcall_save_input(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        strategy_name = args.get("strategy_name", "")
        if not strategy_name:
            return "Error: strategy_name is required"

        input_doc = {
            "product_description": args.get("product_description", ""),
            "hypothesis": args.get("hypothesis", ""),
            "stage": args.get("stage", ""),
            "budget": args.get("budget", ""),
            "timeline": args.get("timeline", ""),
            "additional_context": args.get("additional_context", ""),
            "hypothesis_source": args.get("hypothesis_source", ""),  # link to /customer-research/... doc
        }

        path = f"/strategies/{strategy_name}/input"
        try:
            await pdoc_integration.pdoc_create(path, json.dumps(input_doc, ensure_ascii=False), fuser_id)
        except Exception as e:
            if "already exists" in str(e).lower():
                await pdoc_integration.pdoc_overwrite(path, json.dumps(input_doc, ensure_ascii=False), fuser_id)
            else:
                return f"Error saving input: {e}"

        status = await get_pipeline_status(strategy_name)
        return f"""✍️ {path}

✓ Input сохранён для стратегии "{strategy_name}"

Pipeline status:
- Завершено: {', '.join(status['completed']) or 'ничего'}
- Следующий шаг: {status['next_step'] or 'все готово'}

Теперь можно запустить diagnostic агента."""

    @rcx.on_tool_call(RUN_AGENT_TOOL.name)
    async def toolcall_run_agent(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        age = time.time() - toolcall.fcall_created_ts
        logger.info("run_agent ENTRY: fcall_id=%s age=%.1fs processed_count=%d args=%s",
            toolcall.fcall_id, age, len(processed_fcalls), args)

        # Dedupe: prevent processing same tool call multiple times (race condition)
        if toolcall.fcall_id in processed_fcalls:
            logger.warning("DEDUPE BLOCK: run_agent call %s already in processed_fcalls", toolcall.fcall_id)
            return "Already processing this request"
        processed_fcalls.add(toolcall.fcall_id)
        logger.info("run_agent ACCEPTED: fcall_id=%s, now processed_fcalls=%s", toolcall.fcall_id, processed_fcalls)

        strategy_name = args.get("strategy_name", "")
        agent = args.get("agent", "")
        user_additions = args.get("user_additions", "")

        if not strategy_name:
            return "Error: strategy_name is required"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"

        error = await check_can_run_agent(strategy_name, agent)
        if error:
            return error

        # Load required context for the agent
        context_docs = await _load_agent_context(pdoc_integration, fuser_id, strategy_name, agent)
        if context_docs.get("error"):
            return context_docs["error"]

        q = f"""Strategy: {strategy_name}
Output path: /strategies/{strategy_name}/{agent}

{context_docs["content"]}"""
        if user_additions:
            q += f"\n\nAdditional context from user:\n{user_additions}"

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
        # Reject stale tool calls from previous bot runs
        age = time.time() - toolcall.fcall_created_ts
        if age > 60:
            logger.warning("Stale rerun_agent call %s ignored (age=%.1fs)", toolcall.fcall_id, age)
            return f"Stale request ignored (created {age:.0f}s ago). Please retry."

        # Dedupe: prevent processing same tool call multiple times
        if toolcall.fcall_id in processed_fcalls:
            logger.warning("Duplicate rerun_agent call %s ignored", toolcall.fcall_id)
            return "Already processing this request"
        processed_fcalls.add(toolcall.fcall_id)

        strategy_name = args.get("strategy_name", "")
        agent = args.get("agent", "")
        feedback = args.get("feedback", "")

        if not strategy_name:
            return "Error: strategy_name is required"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"
        if not feedback:
            return "Error: feedback is required for rerun"

        if not await step_exists(strategy_name, agent):
            return f"Error: {agent} ещё не был запущен, нечего перезапускать. Используй run_agent."

        q = f"""Strategy: {strategy_name}

RERUN with corrections. Previous result needs changes:
{feedback}

Read previous result from /strategies/{strategy_name}/{agent}, apply the feedback, and save updated result to the same path."""

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

    @rcx.on_tool_call(GET_PIPELINE_STATUS_TOOL.name)
    async def toolcall_get_pipeline_status(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        strategy_name = args.get("strategy_name", "")
        if not strategy_name:
            return "Error: strategy_name is required"

        status = await get_pipeline_status(strategy_name)

        lines = [f"Pipeline status for \"{strategy_name}\":\n"]
        for step in PIPELINE:
            if step in status["completed"]:
                lines.append(f"  ✓ {step} — {STEP_DESCRIPTIONS.get(step, step)}")
            elif step == status["next_step"]:
                lines.append(f"  → {step} — {STEP_DESCRIPTIONS.get(step, step)} (NEXT)")
            else:
                lines.append(f"  ○ {step} — {STEP_DESCRIPTIONS.get(step, step)}")

        if status["all_done"]:
            lines.append("\n✓ Все шаги завершены! Стратегия готова к передаче Ad Monster.")
        else:
            lines.append(f"\nСледующий шаг: {status['next_step']}")

        return "\n".join(lines)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, args)

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
        bot_main_loop=owl_strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=owl_strategist_install.install,
    ))


if __name__ == "__main__":
    main()
