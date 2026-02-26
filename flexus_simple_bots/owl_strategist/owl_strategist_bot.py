import asyncio
import datetime
import json
import logging
from typing import Dict, Any, Optional

from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_bot_exec
from flexus_client_kit.core import ckit_shutdown
from flexus_client_kit.core import ckit_ask_model
from flexus_client_kit.core import ckit_kanban
from flexus_client_kit.core import ckit_external_auth
from flexus_client_kit.integrations.providers.request_response import fi_pdoc
from flexus_simple_bots.owl_strategist import owl_strategist_install
from flexus_simple_bots.owl_strategist.skills import diagnostic as skill_diagnostic
from flexus_simple_bots.owl_strategist.skills import tactics as skill_tactics
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_owl_strategist")

# Tactics produces 4 separate documents instead of 1 — model can't reliably generate huge single doc
TACTICS_DOCS = skill_tactics.TACTICS_DOCS


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
    "input": "Input data collection — product, hypothesis, budget, timeline",
    **AGENT_DESCRIPTIONS,
}


SAVE_INPUT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="save_input",
    description="Save collected input data to start marketing experiment. Call after collecting product/hypothesis/budget/timeline from user.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{idea-slug}/{hypothesis-slug}/experiments/{exp-slug} e.g. dental-samples/private-practice/experiments/meta-ads-test"},
            "product_description": {"type": "string", "description": "What the product/service does"},
            "hypothesis": {"type": "string", "description": "What we want to test"},
            "stage": {"type": "string", "enum": ["idea", "mvp", "scaling"], "description": "Current stage"},
            "budget": {"type": "string", "description": "Budget constraints"},
            "timeline": {"type": "string", "description": "Timeline expectations"},
            "additional_context": {"type": "string", "description": "Any other relevant context"},
        },
        "required": ["experiment_id", "product_description", "hypothesis", "stage"],
    },
)

RUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="run_agent",
    description="Run specific agent. Pipeline is strictly sequential: input → diagnostic → metrics → segment → messaging → channels → tactics → compliance. Each step requires previous step completed.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{idea-slug}/{hypothesis-slug}/experiments/{exp-slug} e.g. dental-samples/private-practice/experiments/meta-ads-test"},
            "agent": {
                "type": "string",
                "enum": AGENTS,
                "description": "Which agent to run",
            },
            "user_additions": {"type": "string", "description": "Important context from user to consider"},
        },
        "required": ["experiment_id", "agent"],
    },
)

RERUN_AGENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="rerun_agent",
    description="Rerun agent with corrections after user feedback. Does not change pipeline position.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{idea-slug}/{hypothesis-slug}/experiments/{exp-slug}"},
            "agent": {
                "type": "string",
                "enum": AGENTS,
            },
            "feedback": {"type": "string", "description": "What to change based on user feedback"},
        },
        "required": ["experiment_id", "agent", "feedback"],
    },
)

GET_PIPELINE_STATUS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="get_pipeline_status",
    description="Get current pipeline status for marketing experiment — which steps are done, which is next.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{idea-slug}/{hypothesis-slug}/experiments/{exp-slug}"},
        },
        "required": ["experiment_id"],
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

# Which previous docs each agent needs (all steps before it in pipeline)
# Note: compliance needs all 4 tactics documents, not just "tactics"
AGENT_REQUIRED_DOCS = {
    "diagnostic": ["input"],
    "metrics": ["input", "diagnostic"],
    "segment": ["input", "diagnostic", "metrics"],
    "messaging": ["input", "diagnostic", "segment"],
    "channels": ["input", "diagnostic", "metrics", "segment", "messaging"],
    "tactics": ["input", "diagnostic", "metrics", "segment", "messaging", "channels"],
    "compliance": ["input", "diagnostic", "metrics", "segment", "messaging", "channels"] + TACTICS_DOCS,
}


async def owl_strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    # owner_fuser_id — ID of the human who hired this bot, used for pdoc access checks
    owner_fuser_id = rcx.persona.owner_fuser_id

    async def step_exists(experiment_id: str, step: str) -> bool:
        # pdoc_cat returns None if document doesn't exist (no exception thrown!)
        # Must check return value, not catch exception
        if step == "tactics":
            # Tactics has 4 separate documents — all must exist for step to be "complete"
            for doc in TACTICS_DOCS:
                result = await pdoc_integration.pdoc_cat(f"/gtm/discovery/{experiment_id}/{doc}", owner_fuser_id)
                if result is None:
                    return False
            return True
        result = await pdoc_integration.pdoc_cat(f"/gtm/discovery/{experiment_id}/{step}", owner_fuser_id)
        return result is not None

    async def get_pipeline_status(experiment_id: str) -> Dict[str, Any]:
        completed = []
        for step in PIPELINE:
            if await step_exists(experiment_id, step):
                completed.append(step)
            else:
                break
        next_step = PIPELINE[len(completed)] if len(completed) < len(PIPELINE) else None
        return {
            "completed": completed,
            "next_step": next_step,
            "all_done": len(completed) == len(PIPELINE),
        }

    async def check_can_run_agent(experiment_id: str, agent: str) -> Optional[str]:
        agent_idx = PIPELINE.index(agent)
        if agent_idx == 0:
            return None
        prev_step = PIPELINE[agent_idx - 1]
        if not await step_exists(experiment_id, prev_step):
            return f"Cannot run {agent} — must complete {prev_step} first. Order: {' → '.join(PIPELINE)}"
        return None

    async def load_agent_context(experiment_id: str, agent: str, include_current: bool = False) -> str:
        """Load all required documents for an agent and format them for the first message."""
        required = list(AGENT_REQUIRED_DOCS.get(agent, []))
        if include_current:
            # For tactics, include all 4 docs; for others, include the single doc
            if agent == "tactics":
                for doc in TACTICS_DOCS:
                    if doc not in required:
                        required.append(doc)
            elif agent not in required:
                required.append(agent)

        docs = []
        for doc_name in required:
            try:
                content = await pdoc_integration.pdoc_cat(f"/gtm/discovery/{experiment_id}/{doc_name}", owner_fuser_id)
                docs.append(f"### {doc_name}\n```json\n{content}\n```")
            except Exception as e:
                logger.warning(f"Could not load {doc_name}: {e}")

        if not docs:
            return ""
        return "## Input Documents\n\n" + "\n\n".join(docs)

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
        experiment_id = args.get("experiment_id", "")
        if not experiment_id:
            return "Error: experiment_id is required (format: {idea-slug}/{hypothesis-slug}/experiments/{exp-slug})"

        # Get user ID from toolcall context, not bot persona
        caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)

        # Wrap in standard format for UI microfrontend
        input_doc = {
            "input": {
                "meta": {
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "version": "1.0"
                },
                "product_description": args.get("product_description", ""),
                "hypothesis": args.get("hypothesis", ""),
                "stage": args.get("stage", ""),
                "budget": args.get("budget", ""),
                "timeline": args.get("timeline", ""),
                "additional_context": args.get("additional_context", ""),
            }
        }

        path = f"/gtm/discovery/{experiment_id}/input"
        try:
            await pdoc_integration.pdoc_create(path, json.dumps(input_doc, ensure_ascii=False), caller_fuser_id)
        except Exception as e:
            if "already exists" in str(e).lower():
                await pdoc_integration.pdoc_overwrite(path, json.dumps(input_doc, ensure_ascii=False), caller_fuser_id)
            else:
                return f"Error saving input: {e}"

        status = await get_pipeline_status(experiment_id)
        return f"""✍️ {path}

✓ Input saved for experiment "{experiment_id}"

Pipeline status:
- Completed: {', '.join(status['completed']) or 'none'}
- Next step: {status['next_step'] or 'all done'}

Can now run diagnostic agent."""

    @rcx.on_tool_call(RUN_AGENT_TOOL.name)
    async def toolcall_run_agent(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        experiment_id = args.get("experiment_id", "")
        agent = args.get("agent", "")
        user_additions = args.get("user_additions", "")

        if not experiment_id:
            return "Error: experiment_id is required (format: {idea-slug}/{hypothesis-slug}/experiments/{exp-slug})"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"

        error = await check_can_run_agent(experiment_id, agent)
        if error:
            return error

        context = await load_agent_context(experiment_id, agent)
        # For tactics, output is 4 documents; for others, single doc
        if agent == "tactics":
            output_info = f"Output documents: {', '.join(TACTICS_DOCS)}"
        else:
            output_info = f"Output path: /gtm/discovery/{experiment_id}/{agent}"
        q = f"Experiment: {experiment_id}\n{output_info}\n\n{context}"
        if user_additions:
            q += f"\n\n## User Context\n{user_additions}"

        logger.info(f"Starting agent '{agent}' for experiment '{experiment_id}'")

        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking=f"owl_{agent}",
            persona_id=rcx.persona.persona_id,
            first_question=[q],
            first_calls=["null"],
            title=[AGENT_DESCRIPTIONS.get(agent, agent)],
            fcall_id=toolcall.fcall_id,
            fexp_name=agent,
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(RERUN_AGENT_TOOL.name)
    async def toolcall_rerun_agent(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        experiment_id = args.get("experiment_id", "")
        agent = args.get("agent", "")
        feedback = args.get("feedback", "")

        if not experiment_id:
            return "Error: experiment_id is required (format: {idea-slug}/{hypothesis-slug}/experiments/{exp-slug})"
        if agent not in AGENTS:
            return f"Error: agent must be one of {AGENTS}"
        if not feedback:
            return "Error: feedback is required for rerun"

        if not await step_exists(experiment_id, agent):
            return f"Error: {agent} has not been run yet, nothing to rerun. Use run_agent."

        # Load all docs including current one for rerun
        context = await load_agent_context(experiment_id, agent, include_current=True)
        # For tactics, output is 4 documents; for others, single doc
        if agent == "tactics":
            output_info = f"Output documents: {', '.join(TACTICS_DOCS)}"
        else:
            output_info = f"Output path: /gtm/discovery/{experiment_id}/{agent}"
        q = f"""Experiment: {experiment_id}
{output_info}

RERUN with corrections. Apply this feedback:
{feedback}

{context}"""

        logger.info(f"Rerunning agent '{agent}' for experiment '{experiment_id}' with feedback")

        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking=f"owl_{agent}_rerun",
            persona_id=rcx.persona.persona_id,
            first_question=[q],
            first_calls=["null"],
            title=[f"Rerun: {AGENT_DESCRIPTIONS.get(agent, agent)}"],
            fcall_id=toolcall.fcall_id,
            fexp_name=agent,
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(GET_PIPELINE_STATUS_TOOL.name)
    async def toolcall_get_pipeline_status(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        experiment_id = args.get("experiment_id", "")
        if not experiment_id:
            return "Error: experiment_id is required (format: {idea-slug}/{hypothesis-slug}/experiments/{exp-slug})"

        status = await get_pipeline_status(experiment_id)

        lines = [f"Pipeline status for \"{experiment_id}\":\n"]
        for step in PIPELINE:
            if step in status["completed"]:
                lines.append(f"  ✓ {step} — {STEP_DESCRIPTIONS.get(step, step)}")
            elif step == status["next_step"]:
                lines.append(f"  → {step} — {STEP_DESCRIPTIONS.get(step, step)} (NEXT)")
            else:
                lines.append(f"  ○ {step} — {STEP_DESCRIPTIONS.get(step, step)}")

        if status["all_done"]:
            lines.append("\n✓ All steps completed! Experiment ready for Ad Monster launch.")
        else:
            lines.append(f"\nNext step: {status['next_step']}")

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
