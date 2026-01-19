import asyncio
import datetime
import json
import logging
from typing import Dict, Any, Optional, List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.owl import owl_install

logger = logging.getLogger("bot_owl")

BOT_NAME = "owl"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

PIPELINE = ["calibration", "diagnostic", "metrics", "segment", "messaging", "channels", "tactics"]
STEP_WEIGHT = 14  # ~14 points per step, 7 steps ≈ 100


def make_tool_response(path: str, step: str, score: int, filled: List[str], unfilled: List[str]) -> str:
    filled_str = ", ".join(filled) if filled else "none"
    unfilled_str = ", ".join(unfilled) if unfilled else "none"
    return f"""✍️ {path}

✓ Updated step: {step}

Score: {score}/100
Filled: {filled_str}
Unfilled: {unfilled_str}
"""


# =============================================================================
# CALIBRATION
# =============================================================================

UPDATE_CALIBRATION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_calibration",
    description="Set calibration: goal, budget, timeline. Creates strategy doc if needed.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string", "description": "Idea slug from discovery path"},
            "hyp_slug": {"type": "string", "description": "Hypothesis slug from discovery path"},
            "calibration": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "enum": ["waitlist", "leads", "demos", "paid_conversions"]},
                    "success_definition": {"type": "string", "description": "What counts as win"},
                    "learning_budget": {"type": "number", "description": "Budget in USD"},
                    "max_cpl": {"type": "number", "description": "Max cost per lead"},
                    "timeline_days": {"type": "integer", "description": "Days to run"},
                    "risk_acknowledgement": {"type": "boolean"},
                },
                "required": ["goal", "success_definition", "learning_budget", "max_cpl", "timeline_days", "risk_acknowledgement"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer", "description": "Updated score after this step"},
        },
        "required": ["idea_slug", "hyp_slug", "calibration", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# DIAGNOSTIC
# =============================================================================

UPDATE_DIAGNOSTIC_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_diagnostic",
    description="Set diagnostic: hypothesis classification, unknowns, feasibility. Requires calibration.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "diagnostic": {
                "type": "object",
                "properties": {
                    "normalized_hypothesis": {"type": "string"},
                    "primary_type": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion"]},
                    "uncertainty_level": {"type": "string", "enum": ["low", "medium", "high", "extreme"]},
                    "feasibility_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "key_unknowns": {"type": "array", "items": {"type": "string"}},
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["normalized_hypothesis", "primary_type", "uncertainty_level", "feasibility_score", "key_unknowns", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "diagnostic", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# METRICS
# =============================================================================

UPDATE_METRICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_metrics",
    description="Set metrics: KPIs, stop/accelerate rules. Requires diagnostic.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "metrics": {
                "type": "object",
                "properties": {
                    "primary_kpi": {"type": "string"},
                    "target_values": {"type": "object", "additionalProperties": {"type": "number"}},
                    "stop_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string"},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "action": {"type": "string"},
                            },
                            "required": ["metric", "operator", "threshold", "action"],
                            "additionalProperties": False,
                        },
                    },
                    "accelerate_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string"},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "action": {"type": "string"},
                            },
                            "required": ["metric", "operator", "threshold", "action"],
                            "additionalProperties": False,
                        },
                    },
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["primary_kpi", "target_values", "stop_rules", "accelerate_rules", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "metrics", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# SEGMENT
# =============================================================================

UPDATE_SEGMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_segment",
    description="Set segment: ICP, JTBD, journey. Requires metrics.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "segment": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "icp": {
                        "type": "object",
                        "properties": {
                            "roles": {"type": "array", "items": {"type": "string"}},
                            "company_size": {"type": "string"},
                            "industries": {"type": "array", "items": {"type": "string"}},
                            "geo": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["roles", "company_size", "industries", "geo"],
                        "additionalProperties": False,
                    },
                    "jtbd": {
                        "type": "object",
                        "properties": {
                            "functional": {"type": "array", "items": {"type": "string"}},
                            "emotional": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["functional", "emotional"],
                        "additionalProperties": False,
                    },
                    "pains": {"type": "array", "items": {"type": "string"}},
                    "gains": {"type": "array", "items": {"type": "string"}},
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["label", "icp", "jtbd", "pains", "gains", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "segment", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# MESSAGING
# =============================================================================

UPDATE_MESSAGING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_messaging",
    description="Set messaging: value prop, angles, objections. Requires segment.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "messaging": {
                "type": "object",
                "properties": {
                    "value_prop": {"type": "string"},
                    "positioning": {"type": "string"},
                    "angles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "hook": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["name", "hook", "description"],
                            "additionalProperties": False,
                        },
                    },
                    "objections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objection": {"type": "string"},
                                "rebuttal": {"type": "string"},
                            },
                            "required": ["objection", "rebuttal"],
                            "additionalProperties": False,
                        },
                    },
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["value_prop", "positioning", "angles", "objections", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "messaging", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# CHANNELS
# =============================================================================

UPDATE_CHANNELS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_channels",
    description="Set channels: selection, test cells, budget. Requires messaging.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "channels": {
                "type": "object",
                "properties": {
                    "selected": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "budget_share": {"type": "number"},
                                "rationale": {"type": "string"},
                            },
                            "required": ["channel", "budget_share", "rationale"],
                            "additionalProperties": False,
                        },
                    },
                    "test_cells": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cell_id": {"type": "string"},
                                "channel": {"type": "string"},
                                "angle": {"type": "string"},
                                "budget": {"type": "number"},
                                "hypothesis": {"type": "string"},
                            },
                            "required": ["cell_id", "channel", "angle", "budget", "hypothesis"],
                            "additionalProperties": False,
                        },
                    },
                    "total_budget": {"type": "number"},
                    "duration_days": {"type": "integer"},
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["selected", "test_cells", "total_budget", "duration_days", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "channels", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# TACTICS
# =============================================================================

UPDATE_TACTICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_tactics",
    description="Set tactics: campaigns, creatives, landing, tracking. Requires channels. Final step.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "tactics": {
                "type": "object",
                "properties": {
                    "campaigns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "campaign_id": {"type": "string"},
                                "channel": {"type": "string"},
                                "objective": {"type": "string"},
                                "daily_budget": {"type": "number"},
                            },
                            "required": ["campaign_id", "channel", "objective", "daily_budget"],
                            "additionalProperties": False,
                        },
                    },
                    "creatives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "creative_id": {"type": "string"},
                                "angle": {"type": "string"},
                                "headline": {"type": "string"},
                                "primary_text": {"type": "string"},
                                "cta": {"type": "string"},
                                "visual_brief": {"type": "string"},
                            },
                            "required": ["creative_id", "angle", "headline", "primary_text", "cta", "visual_brief"],
                            "additionalProperties": False,
                        },
                    },
                    "landing": {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string"},
                            "headline": {"type": "string"},
                            "structure": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["goal", "headline", "structure"],
                        "additionalProperties": False,
                    },
                    "tracking": {
                        "type": "object",
                        "properties": {
                            "events": {"type": "array", "items": {"type": "string"}},
                            "conversion_event": {"type": "string"},
                        },
                        "required": ["events", "conversion_event"],
                        "additionalProperties": False,
                    },
                    "detailed_analysis": {"type": "string"},
                },
                "required": ["campaigns", "creatives", "landing", "tracking", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "tactics", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# HANDLER
# =============================================================================

async def handle_update_strategy(
    step: str,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    idea_slug = args["idea_slug"]
    hyp_slug = args["hyp_slug"]
    step_data = args[step]
    new_score = args["new_score"]

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/gtm/strategy/{idea_slug}--{hyp_slug}/strategy"

    # Read existing doc or create new
    try:
        existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
        doc = json.loads(existing)
    except Exception:
        doc = {
            "strategy": {
                "meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                "progress": {"score": 0, "step": "calibration"},
                "calibration": None,
                "diagnostic": None,
                "metrics": None,
                "segment": None,
                "messaging": None,
                "channels": None,
                "tactics": None,
            }
        }

    # Validate gating
    step_idx = PIPELINE.index(step)
    if step_idx > 0:
        prev_step = PIPELINE[step_idx - 1]
        if doc["strategy"].get(prev_step) is None:
            return f"Error: Must complete {prev_step} before {step}"

    # Update
    doc["strategy"][step] = step_data
    doc["strategy"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc["strategy"]["progress"]["score"] = new_score
    doc["strategy"]["progress"]["step"] = PIPELINE[step_idx + 1] if step_idx + 1 < len(PIPELINE) else "complete"

    # Write
    try:
        await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)
    except Exception:
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    # Build response
    filled = [s for s in PIPELINE if doc["strategy"].get(s) is not None]
    unfilled = [s for s in PIPELINE if doc["strategy"].get(s) is None]

    return make_tool_response(path, step, new_score, filled, unfilled)


# =============================================================================
# MAIN LOOP
# =============================================================================

TOOLS = [
    UPDATE_CALIBRATION_TOOL,
    UPDATE_DIAGNOSTIC_TOOL,
    UPDATE_METRICS_TOOL,
    UPDATE_SEGMENT_TOOL,
    UPDATE_MESSAGING_TOOL,
    UPDATE_CHANNELS_TOOL,
    UPDATE_TACTICS_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def owl_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
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

    @rcx.on_tool_call(UPDATE_CALIBRATION_TOOL.name)
    async def toolcall_calibration(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("calibration", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_DIAGNOSTIC_TOOL.name)
    async def toolcall_diagnostic(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("diagnostic", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_METRICS_TOOL.name)
    async def toolcall_metrics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("metrics", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_SEGMENT_TOOL.name)
    async def toolcall_segment(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("segment", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_MESSAGING_TOOL.name)
    async def toolcall_messaging(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("messaging", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_CHANNELS_TOOL.name)
    async def toolcall_channels(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("channels", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_TACTICS_TOOL.name)
    async def toolcall_tactics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("tactics", toolcall, args, rcx, pdoc_integration)

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
        bot_main_loop=owl_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=owl_install.install,
    ))


if __name__ == "__main__":
    main()
