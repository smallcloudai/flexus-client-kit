import asyncio
import logging
import json
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_simple_bots.productman import productman_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_productman")


BOT_NAME = "productman"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


HYPOTHESIS_FORMATTER_TOOL = ckit_cloudtool.CloudTool(
    name="format_hypothesis",
    description="Format freeform problem text into structured hypothesis with fields: client, wants, cannot, because",
    parameters={
        "type": "object",
        "properties": {
            "freeform_text": {
                "type": "string",
                "description": "Freeform problem description to structure"
            },
        },
        "required": ["freeform_text"],
    },
)

PRIORITIZATION_SCORER_TOOL = ckit_cloudtool.CloudTool(
    name="score_hypotheses",
    description="Score hypotheses on 4 dimensions (impact, evidence, urgency, feasibility) and calculate weighted total",
    parameters={
        "type": "object",
        "properties": {
            "hypotheses": {
                "type": "array",
                "description": "List of hypothesis objects to score",
                "items": {"type": "object"}
            },
            "criteria_weights": {
                "type": "object",
                "description": "Weights for each dimension (should sum to 1.0)",
                "properties": {
                    "impact": {"type": "number"},
                    "evidence": {"type": "number"},
                    "urgency": {"type": "number"},
                    "feasibility": {"type": "number"},
                }
            },
            "scores": {
                "type": "array",
                "description": "Score arrays for each hypothesis, each containing [impact, evidence, urgency, feasibility]",
                "items": {
                    "type": "array",
                    "items": {"type": "number"}
                }
            }
        },
        "required": ["hypotheses", "scores"],
    },
)

EXPERIMENT_TEMPLATES_TOOL = ckit_cloudtool.CloudTool(
    name="get_experiment_templates",
    description="Get experiment design templates for testing product hypotheses",
    parameters={
        "type": "object",
        "properties": {
            "experiment_type": {
                "type": "string",
                "enum": ["landing_page", "survey", "interviews", "concierge_mvp", "prototype", "all"],
                "description": "Type of experiment template to retrieve"
            },
        },
        "required": ["experiment_type"],
    },
)

TOOLS = [
    HYPOTHESIS_FORMATTER_TOOL,
    PRIORITIZATION_SCORER_TOOL,
    EXPERIMENT_TEMPLATES_TOOL,
]


async def productman_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(productman_install.productman_setup_schema, rcx.persona.persona_setup)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(HYPOTHESIS_FORMATTER_TOOL.name)
    async def toolcall_format_hypothesis(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        freeform = model_produced_args.get("freeform_text", "")

        # Simple parsing logic - this could be enhanced with regex or LLM call
        # For now, return a template that guides the model to fill it properly
        result = {
            "client": "<extracted or ask user>",
            "wants": "<extracted or ask user>",
            "cannot": "<extracted or ask user>",
            "because": "<extracted or ask user>",
            "evidence": "",
            "source_text": freeform
        }

        logger.info(f"Formatted hypothesis from: {freeform[:100]}...")
        return json.dumps(result, indent=2)

    @rcx.on_tool_call(PRIORITIZATION_SCORER_TOOL.name)
    async def toolcall_score_hypotheses(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        hypotheses = model_produced_args.get("hypotheses", [])
        scores = model_produced_args.get("scores", [])
        weights = model_produced_args.get("criteria_weights", {
            "impact": 0.3,
            "evidence": 0.3,
            "urgency": 0.2,
            "feasibility": 0.2
        })

        if len(hypotheses) != len(scores):
            return "Error: Number of hypotheses must match number of score arrays"

        results = []
        for i, hyp in enumerate(hypotheses):
            score_arr = scores[i]
            if len(score_arr) != 4:
                return f"Error: Score array {i} must have exactly 4 values [impact, evidence, urgency, feasibility]"

            total = (
                score_arr[0] * weights.get("impact", 0.3) +
                score_arr[1] * weights.get("evidence", 0.3) +
                score_arr[2] * weights.get("urgency", 0.2) +
                score_arr[3] * weights.get("feasibility", 0.2)
            )

            results.append({
                "hypothesis": hyp,
                "scores": {
                    "impact": score_arr[0],
                    "evidence": score_arr[1],
                    "urgency": score_arr[2],
                    "feasibility": score_arr[3],
                    "total": round(total, 2)
                }
            })

        # Sort by total score descending
        results.sort(key=lambda x: x["scores"]["total"], reverse=True)

        logger.info(f"Scored {len(hypotheses)} hypotheses")
        return json.dumps(results, indent=2)

    @rcx.on_tool_call(EXPERIMENT_TEMPLATES_TOOL.name)
    async def toolcall_experiment_templates(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        exp_type = model_produced_args.get("experiment_type", "all")

        templates = {
            "landing_page": {
                "name": "Landing Page Test",
                "description": "Create a landing page to test value proposition and measure interest",
                "what_to_do": "Build simple landing page with headline, 3 benefits, CTA button",
                "what_to_measure": "Sign-ups, email captures, time on page, bounce rate",
                "success_criteria": "10%+ conversion rate, >2min avg time on page",
                "effort": "Low (1-3 days)",
                "tools": "Carrd, Webflow, Framer, Tilda"
            },
            "survey": {
                "name": "Quantitative Survey",
                "description": "Deploy structured survey to target audience to validate problem and willingness to pay",
                "what_to_do": "Design 8-12 questions (60% closed, 40% open), deploy to 50-100 respondents",
                "what_to_measure": "Problem frequency, current solutions, willingness to pay, demographics",
                "success_criteria": "70%+ experience problem frequently, 40%+ willing to pay",
                "effort": "Medium (1 week)",
                "tools": "SurveyMonkey, Typeform, Google Forms"
            },
            "interviews": {
                "name": "Customer Interviews",
                "description": "Conduct 10-15 deep interviews with target audience",
                "what_to_do": "Script 5-7 open-ended questions, record sessions, extract quotes",
                "what_to_measure": "Pain intensity, current workarounds, willingness to change",
                "success_criteria": "8+ of 10 interviewees describe problem unprompted",
                "effort": "Medium (2 weeks)",
                "tools": "Calendly, Zoom, Otter.ai"
            },
            "concierge_mvp": {
                "name": "Concierge MVP",
                "description": "Manually deliver the solution to 5-10 customers to test value",
                "what_to_do": "Do the work manually behind the scenes, charge real money",
                "what_to_measure": "Time to deliver, customer satisfaction, retention rate, referrals",
                "success_criteria": "4+ of 5 customers renew, NPS >40",
                "effort": "High (4+ weeks)",
                "tools": "Manual process, spreadsheets, email"
            },
            "prototype": {
                "name": "Interactive Prototype",
                "description": "Build clickable prototype to test core user flow",
                "what_to_do": "Design 3-5 key screens, make clickable, test with 10 users",
                "what_to_measure": "Task completion rate, time to complete, confusion points",
                "success_criteria": "80%+ complete primary task without help",
                "effort": "Medium (1-2 weeks)",
                "tools": "Figma, Balsamiq, Marvel"
            }
        }

        if exp_type == "all":
            return json.dumps(templates, indent=2)
        elif exp_type in templates:
            return json.dumps({exp_type: templates[exp_type]}, indent=2)
        else:
            return f"Unknown experiment type: {exp_type}"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=productman_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
