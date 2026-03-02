import asyncio
import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.owl import owl_install

logger = logging.getLogger("bot_owl")

BOT_NAME = "owl"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

PIPELINE = [
    "section01-calibration",
    "section02-diagnostic",
    "section03-metrics",
    "section04-segment",
    "section05-messaging",
    "section06-channels",
    "section07-tactics",
]
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
    name="update_strategy_section01_calibration",
    description="Collect initial input for marketing strategy: what we're testing and constraints. Creates strategy doc if needed.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string", "description": "Idea slug from discovery path"},
            "hyp_slug": {"type": "string", "description": "Hypothesis slug from discovery path"},
            "section01-calibration": {
                "type": "object",
                "properties": {
                    "budget": {"type": "string", "description": "Budget description including channels (e.g. digital, offline)", "ui:multiline": 3},
                    "timeline": {"type": "string", "description": "Timeline description with goals", "ui:multiline": 10},
                    "hypothesis": {"type": "string", "description": "Full hypothesis: segment, problem, solution, test goal", "ui:multiline": 10},
                    "additional_context": {"type": "string", "description": "Current state, test approach, constraints", "ui:multiline": 10},
                    "product_description": {"type": "string", "description": "What the product/service is", "ui:multiline": 10},
                },
                "required": ["budget", "timeline", "hypothesis", "additional_context", "product_description"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer", "description": "Updated score after this step"},
        },
        "required": ["idea_slug", "hyp_slug", "section01-calibration", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# DIAGNOSTIC
# =============================================================================

UPDATE_DIAGNOSTIC_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section02_diagnostic",
    description="Analyze hypothesis: classify type, identify unknowns, assess feasibility and test mechanisms. Requires section01-calibration.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section02-diagnostic": {
                "type": "object",
                "properties": {
                    "normalized_hypothesis": {"type": "string", "description": "Clear restatement of what we're testing", "ui:multiline": 3},
                    "primary_type": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion", "retention"]},
                    "primary_type_reasoning": {"type": "string", "description": "Why this type applies", "ui:multiline": 3},
                    "secondary_types": {"type": "array", "items": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion", "retention"]}},
                    "secondary_types_reasoning": {"type": "string", "description": "Why these secondary types apply", "ui:multiline": 3},
                    "testable_with_traffic": {"type": "boolean"},
                    "recommended_test_mechanisms": {"type": "array", "items": {"type": "string", "enum": ["paid_traffic", "content", "waitlist", "outbound", "partnerships"]}},
                    "uncertainty_level": {"type": "string", "enum": ["low", "medium", "high", "extreme"]},
                    "uncertainty_reasoning": {"type": "string", "description": "What makes it this uncertainty level", "ui:multiline": 3},
                    "key_unknowns": {"type": "array", "items": {"type": "string"}},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "needs_additional_methods": {"type": "array", "items": {"type": "string", "enum": ["none", "custdev", "desk_research", "product_experiment"]}},
                    "feasibility_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "feasibility_reasoning": {"type": "string", "description": "What makes it feasible or not", "ui:multiline": 3},
                    "detailed_analysis": {"type": "string", "description": "Rich markdown: what we're testing, why it matters, what the answer tells us", "ui:multiline": 10},
                    "key_decisions_ahead": {"type": "array", "items": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                    "questions_to_resolve": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "normalized_hypothesis", "primary_type", "primary_type_reasoning",
                    "secondary_types", "secondary_types_reasoning",
                    "testable_with_traffic", "recommended_test_mechanisms",
                    "uncertainty_level", "uncertainty_reasoning", "key_unknowns", "limitations",
                    "needs_additional_methods", "feasibility_score", "feasibility_reasoning",
                    "detailed_analysis", "key_decisions_ahead", "next_steps", "questions_to_resolve"
                ],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section02-diagnostic", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# METRICS
# =============================================================================

UPDATE_METRICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section03_metrics",
    description="Define success metrics: KPIs, targets, MDE, stop/accelerate rules with interpretation guide. Requires section02-diagnostic.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section03-metrics": {
                "type": "object",
                "properties": {
                    "primary_kpi": {"type": "string"},
                    "primary_kpi_reasoning": {"type": "string", "ui:multiline": 3},
                    "secondary_kpis": {"type": "array", "items": {"type": "string"}},
                    "target_values": {"type": "object", "additionalProperties": {"type": "number"}},
                    "target_values_reasoning": {"type": "string", "ui:multiline": 3},
                    "mde": {
                        "type": "object",
                        "properties": {
                            "relative_change": {"type": "number"},
                            "confidence": {"type": "number"},
                        },
                        "required": ["relative_change", "confidence"],
                        "additionalProperties": False,
                    },
                    "mde_reasoning": {"type": "string", "ui:multiline": 3},
                    "min_samples": {
                        "type": "object",
                        "properties": {
                            "impressions_per_cell": {"type": "integer"},
                            "clicks_per_cell": {"type": "integer"},
                            "conversions_per_cell": {"type": "integer"},
                        },
                        "required": ["impressions_per_cell", "clicks_per_cell", "conversions_per_cell"],
                        "additionalProperties": False,
                    },
                    "stop_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string", "ui:size": 2},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "min_events": {"type": "integer"},
                                "action": {"type": "string", "ui:size": 2},
                            },
                            "required": ["metric", "operator", "threshold", "min_events", "action"],
                            "additionalProperties": False,
                        },
                    },
                    "stop_rules_reasoning": {"type": "string", "ui:multiline": 3},
                    "accelerate_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string", "ui:size": 2},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "min_conversions": {"type": "integer"},
                                "action": {"type": "string", "ui:size": 2},
                            },
                            "required": ["metric", "operator", "threshold", "min_conversions", "action"],
                            "additionalProperties": False,
                        },
                    },
                    "accelerate_rules_reasoning": {"type": "string", "ui:multiline": 3},
                    "analysis_plan": {"type": "string", "ui:multiline": 5},
                    "detailed_analysis": {"type": "string", "ui:multiline": 10},
                    "interpretation_guide": {
                        "type": "object",
                        "properties": {
                            "success_scenario": {"type": "string", "ui:multiline": 3},
                            "failure_scenario": {"type": "string", "ui:multiline": 3},
                            "inconclusive_scenario": {"type": "string", "ui:multiline": 3},
                        },
                        "required": ["success_scenario", "failure_scenario", "inconclusive_scenario"],
                        "additionalProperties": False,
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "primary_kpi", "primary_kpi_reasoning", "secondary_kpis",
                    "target_values", "target_values_reasoning",
                    "mde", "mde_reasoning", "min_samples",
                    "stop_rules", "stop_rules_reasoning",
                    "accelerate_rules", "accelerate_rules_reasoning",
                    "analysis_plan", "detailed_analysis", "interpretation_guide", "next_steps"
                ],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section03-metrics", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# SEGMENT
# =============================================================================

UPDATE_SEGMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section04_segment",
    description="Define target audience: ICP, JTBD, journey moments, targeting implications. Requires section03-metrics.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section04-segment": {
                "type": "object",
                "properties": {
                    "segment_id": {"type": "string"},
                    "label": {"type": "string"},
                    "segment_reasoning": {"type": "string", "ui:multiline": 3},
                    "icp": {
                        "type": "object",
                        "properties": {
                            "b2x": {"type": "string", "enum": ["b2c", "b2b", "prosumer"]},
                            "company_size": {"type": "string"},
                            "roles": {"type": "array", "items": {"type": "string"}},
                            "industries": {"type": "array", "items": {"type": "string"}},
                            "geo": {"type": "array", "items": {"type": "string"}},
                            "income_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            "tech_savviness": {"type": "string", "enum": ["low", "medium", "high"]},
                            "decision_maker": {"type": "string"},
                        },
                        "required": ["b2x", "company_size", "roles", "industries", "geo", "income_level", "tech_savviness", "decision_maker"],
                        "additionalProperties": False,
                    },
                    "icp_reasoning": {"type": "string", "ui:multiline": 3},
                    "jtbds": {
                        "type": "object",
                        "properties": {
                            "functional_jobs": {"type": "array", "items": {"type": "string"}},
                            "emotional_jobs": {"type": "array", "items": {"type": "string"}},
                            "social_jobs": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["functional_jobs", "emotional_jobs", "social_jobs"],
                        "additionalProperties": False,
                    },
                    "jtbd_reasoning": {"type": "string", "ui:multiline": 3},
                    "current_solutions": {"type": "array", "items": {"type": "string"}},
                    "main_pains": {"type": "array", "items": {"type": "string"}},
                    "desired_gains": {"type": "array", "items": {"type": "string"}},
                    "discovery_channels": {"type": "array", "items": {"type": "string"}},
                    "journey_highlights": {
                        "type": "object",
                        "properties": {
                            "awareness": {"type": "array", "items": {"type": "string"}},
                            "consideration": {"type": "array", "items": {"type": "string"}},
                            "purchase_triggers": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["awareness", "consideration", "purchase_triggers"],
                        "additionalProperties": False,
                    },
                    "segment_risks": {"type": "array", "items": {"type": "string"}},
                    "detailed_analysis": {"type": "string", "ui:multiline": 10},
                    "persona_narrative": {"type": "string", "ui:multiline": 5},
                    "targeting_implications": {
                        "type": "object",
                        "properties": {
                            "easy_to_reach_via": {"type": "array", "items": {"type": "string"}},
                            "hard_to_reach_because": {"type": "array", "items": {"type": "string"}},
                            "best_hooks": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["easy_to_reach_via", "hard_to_reach_because", "best_hooks"],
                        "additionalProperties": False,
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "segment_id", "label", "segment_reasoning",
                    "icp", "icp_reasoning", "jtbds", "jtbd_reasoning",
                    "current_solutions", "main_pains", "desired_gains",
                    "discovery_channels", "journey_highlights", "segment_risks",
                    "detailed_analysis", "persona_narrative", "targeting_implications", "next_steps"
                ],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section04-segment", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# MESSAGING
# =============================================================================

UPDATE_MESSAGING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section05_messaging",
    description="Set messaging: value prop, angles, objections. Requires section04-segment.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section05-messaging": {
                "type": "object",
                "properties": {
                    "value_prop": {"type": "string", "ui:multiline": 3},
                    "positioning": {"type": "string", "ui:multiline": 3},
                    "angles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "hook": {"type": "string"},
                                "description": {"type": "string", "ui:size": 2},
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
                                "rebuttal": {"type": "string", "ui:size": 2},
                            },
                            "required": ["objection", "rebuttal"],
                            "additionalProperties": False,
                        },
                    },
                    "detailed_analysis": {"type": "string", "ui:multiline": 10},
                },
                "required": ["value_prop", "positioning", "angles", "objections", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section05-messaging", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# CHANNELS
# =============================================================================

UPDATE_CHANNELS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section06_channels",
    description="Set channels: selection, test cells, budget. Requires section05-messaging.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section06-channels": {
                "type": "object",
                "properties": {
                    "selected": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "budget_share": {"type": "number"},
                                "rationale": {"type": "string", "ui:size": 2},
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
                                "channel": {"type": "string"},
                                "angle": {"type": "string"},
                                "budget": {"type": "number"},
                                "hypothesis": {"type": "string", "ui:size": 2},
                            },
                            "required": ["channel", "angle", "budget", "hypothesis"],
                            "additionalProperties": False,
                        },
                    },
                    "total_budget": {"type": "number"},
                    "duration_days": {"type": "integer"},
                    "detailed_analysis": {"type": "string", "ui:multiline": 10},
                },
                "required": ["selected", "test_cells", "total_budget", "duration_days", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section06-channels", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# TACTICS
# =============================================================================

UPDATE_TACTICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="update_strategy_section07_tactics",
    description="Set tactics: campaigns, creatives, landing, tracking. Requires section06-channels. Final step.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hyp_slug": {"type": "string"},
            "section07-tactics": {
                "type": "object",
                "properties": {
                    "campaigns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "objective": {"type": "string", "ui:size": 2},
                                "daily_budget": {"type": "number"},
                            },
                            "required": ["channel", "objective", "daily_budget"],
                            "additionalProperties": False,
                        },
                    },
                    "creatives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "angle": {"type": "string"},
                                "headline": {"type": "string"},
                                "primary_text": {"type": "string", "ui:size": 2},
                                "cta": {"type": "string"},
                                "visual_brief": {"type": "string", "ui:size": 2},
                            },
                            "required": ["angle", "headline", "primary_text", "cta", "visual_brief"],
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
                    "detailed_analysis": {"type": "string", "ui:multiline": 10},
                },
                "required": ["campaigns", "creatives", "landing", "tracking", "detailed_analysis"],
                "additionalProperties": False,
            },
            "new_score": {"type": "integer"},
        },
        "required": ["idea_slug", "hyp_slug", "section07-tactics", "new_score"],
        "additionalProperties": False,
    },
)


# =============================================================================
# SCHEMA BUILDER
# =============================================================================

def build_schema_from_tools() -> Dict[str, Any]:
    """Extract schema from tool definitions for inclusion in strategy doc."""
    tool_map = {
        "section01-calibration": UPDATE_CALIBRATION_TOOL,
        "section02-diagnostic": UPDATE_DIAGNOSTIC_TOOL,
        "section03-metrics": UPDATE_METRICS_TOOL,
        "section04-segment": UPDATE_SEGMENT_TOOL,
        "section05-messaging": UPDATE_MESSAGING_TOOL,
        "section06-channels": UPDATE_CHANNELS_TOOL,
        "section07-tactics": UPDATE_TACTICS_TOOL,
    }
    schema = {}
    for step, tool in tool_map.items():
        step_schema = tool.parameters["properties"][step].copy()
        # XXX replace with a translation function
        step_schema["title"] = step.split("-", 1)[1].capitalize()
        step_schema["description"] = tool.description
        schema[step] = step_schema
    return schema


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
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    idea_slug = args.get("idea_slug")
    hyp_slug = args.get("hyp_slug")
    step_data = args.get(step)
    new_score = args.get("new_score")
    if idea_slug is None or hyp_slug is None or step_data is None or new_score is None:
        logger.error("Hmm it's a strict tool but have missing params anyway, idea_slug=%r, hyp_slug=%r, step_data=%r, new_score=%r",
                idea_slug, hyp_slug, type(step_data), new_score)
        return "Check if have provided all the parameters\n\nThe document was not changed, fix the parameters and call again.\n\n"

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/gtm/strategy/{idea_slug}--{hyp_slug}/strategy"

    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        doc = {
            "strategy": {
                "meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                "progress": {"score": 0, "step": "section01-calibration"},
                "schema": None,
                "section01-calibration": None,
                "section02-diagnostic": None,
                "section03-metrics": None,
                "section04-segment": None,
                "section05-messaging": None,
                "section06-channels": None,
                "section07-tactics": None,
            }
        }
    else:
        doc = existing.pdoc_content

    # Even if the doc is old with old data, overwrite schema, better than alternatives
    doc["strategy"]["schema"] = build_schema_from_tools()

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

    await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    # Build response
    filled = [s for s in PIPELINE if doc["strategy"].get(s) is not None]
    unfilled = [s for s in PIPELINE if doc["strategy"].get(s) is None]

    return make_tool_response(path, step, new_score, filled, unfilled)


# =============================================================================
# INTEGRATIONS & TOOLS
# =============================================================================

OWL_INTEGRATIONS = ckit_integrations_db.static_integrations_load(
    owl_install.OWL_ROOTDIR,
    allowlist=["flexus_policy_document"],
    builtin_skills=owl_install.OWL_SKILLS,
)

TOOLS = [
    UPDATE_CALIBRATION_TOOL,
    UPDATE_DIAGNOSTIC_TOOL,
    UPDATE_METRICS_TOOL,
    UPDATE_SEGMENT_TOOL,
    UPDATE_MESSAGING_TOOL,
    UPDATE_CHANNELS_TOOL,
    UPDATE_TACTICS_TOOL,
    *[t for rec in OWL_INTEGRATIONS for t in rec.integr_tools],
]


async def owl_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(OWL_INTEGRATIONS, rcx)
    pdoc_integration: fi_pdoc.IntegrationPdoc = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(UPDATE_CALIBRATION_TOOL.name)
    async def toolcall_calibration(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section01-calibration", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_DIAGNOSTIC_TOOL.name)
    async def toolcall_diagnostic(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section02-diagnostic", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_METRICS_TOOL.name)
    async def toolcall_metrics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section03-metrics", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_SEGMENT_TOOL.name)
    async def toolcall_segment(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section04-segment", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_MESSAGING_TOOL.name)
    async def toolcall_messaging(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section05-messaging", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_CHANNELS_TOOL.name)
    async def toolcall_channels(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section06-channels", toolcall, args, rcx, pdoc_integration)

    @rcx.on_tool_call(UPDATE_TACTICS_TOOL.name)
    async def toolcall_tactics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy("section07-tactics", toolcall, args, rcx, pdoc_integration)

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
