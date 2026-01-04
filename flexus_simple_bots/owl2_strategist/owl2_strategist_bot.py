import asyncio
import datetime
import json
import logging
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.owl2_strategist import owl2_strategist_install

logger = logging.getLogger("bot_owl2_strategist")


BOT_NAME = "owl2_strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

PIPELINE = ["input", "diagnostic", "metrics", "segment", "messaging", "channels", "tactics", "compliance"]

STEP_DESCRIPTIONS = {
    "input": "Input data collection — product, hypothesis, budget, timeline",
    "diagnostic": "Diagnostic Analysis — classifying hypothesis, identifying unknowns",
    "metrics": "Metrics Framework — defining KPIs, stop-rules, MDE",
    "segment": "Segment Analysis — ICP, JTBD, customer journey",
    "messaging": "Messaging Strategy — value proposition, angles",
    "channels": "Channel Strategy — channel selection, test cells",
    "tactics": "Tactical Spec — campaigns, creatives, landing",
    "compliance": "Risk & Compliance — policies, privacy, risks",
}


# =============================================================================
# SAVE INPUT — Step 1: Collect product, hypothesis, budget, timeline
# =============================================================================

SAVE_INPUT_TOOL = ckit_cloudtool.CloudTool(
    name="save_input",
    description="Save collected input data to start marketing experiment. Call after collecting product/hypothesis/budget/timeline from user.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{experiment-slug} e.g. hyp001-meta-ads-test"},
            "product_description": {"type": "string", "description": "What the product/service does"},
            "hypothesis": {"type": "string", "description": "What we want to test"},
            "stage": {"type": "string", "enum": ["idea", "mvp", "scaling"], "description": "Current stage"},
            "budget": {"type": "string", "description": "Budget constraints"},
            "timeline": {"type": "string", "description": "Timeline expectations"},
            "additional_context": {"type": "string", "description": "Any other relevant context"},
        },
        "required": ["experiment_id", "product_description", "hypothesis", "stage", "budget", "timeline", "additional_context"],
        "additionalProperties": False,
    },
)

SAVE_INPUT_RESPONSE_TEMPLATE = """✍️ {path}

✓ Input saved for experiment "{experiment_id}"

Pipeline status:
- Completed: {completed}
- Next step: {next_step}

Can now run diagnostic."""

async def handle_save_input(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status) -> str:
    experiment_id = args.get("experiment_id", "")
    if not experiment_id:
        return "Error: experiment_id is required (format: {hyp_id}-{slug}, e.g. hyp001-meta-ads-test)"

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)

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

    path = f"/marketing-experiments/{experiment_id}/input"
    await pdoc_integration.pdoc_create(path, json.dumps(input_doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return SAVE_INPUT_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        completed=', '.join(status['completed']) or 'none',
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE DIAGNOSTIC — Step 2: Classify hypothesis, identify unknowns
# =============================================================================

CREATE_DIAGNOSTIC_TOOL = ckit_cloudtool.CloudTool(
    name="create_diagnostic",
    description="Analyze hypothesis and classify testing approach. Call after input is saved. Reads /input document automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "diagnostic": {
                "type": "object",
                "description": "Complete diagnostic analysis",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "normalized_hypothesis": {"type": "string"},
                    "primary_type": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion", "retention"]},
                    "primary_type_reasoning": {"type": "string"},
                    "secondary_types": {"type": "array", "items": {"type": "string"}},
                    "secondary_types_reasoning": {"type": "string"},
                    "testable_with_traffic": {"type": "boolean"},
                    "recommended_test_mechanisms": {"type": "array", "items": {"type": "string"}},
                    "uncertainty_level": {"type": "string", "enum": ["low", "medium", "high", "extreme"]},
                    "uncertainty_reasoning": {"type": "string"},
                    "key_unknowns": {"type": "array", "items": {"type": "string"}},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "needs_additional_methods": {"type": "array", "items": {"type": "string"}},
                    "feasibility_score": {"type": "number", "minimum": 0, "maximum": 1},
                    "feasibility_reasoning": {"type": "string"},
                    "detailed_analysis": {"type": "string", "description": "Markdown summary"},
                    "key_decisions_ahead": {"type": "array", "items": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                    "questions_to_resolve": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "normalized_hypothesis", "primary_type", "primary_type_reasoning",
                            "secondary_types", "secondary_types_reasoning", "testable_with_traffic",
                            "recommended_test_mechanisms", "uncertainty_level", "uncertainty_reasoning",
                            "key_unknowns", "limitations", "needs_additional_methods", "feasibility_score",
                            "feasibility_reasoning", "detailed_analysis", "key_decisions_ahead",
                            "next_steps", "questions_to_resolve"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "diagnostic"],
        "additionalProperties": False
    }
)

DIAGNOSTIC_RESPONSE_TEMPLATE = """✍️ {path}

✓ Diagnostic complete for experiment "{experiment_id}"

Key findings:
- Type: {primary_type}
- Uncertainty: {uncertainty_level}
- Feasibility: {feasibility_pct}%

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_diagnostic(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    diagnostic_data = args["diagnostic"]

    error = await check_can_run_agent(experiment_id, "diagnostic")
    if error:
        return error

    if diagnostic_data["feasibility_score"] > 0.8 and diagnostic_data["uncertainty_level"] == "extreme":
        return "Error: High feasibility score (>0.8) conflicts with extreme uncertainty. Review your analysis."

    if diagnostic_data["testable_with_traffic"] and not diagnostic_data["recommended_test_mechanisms"]:
        return "Error: If testable with traffic, must provide recommended_test_mechanisms."

    doc = {"diagnostic": diagnostic_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/diagnostic"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return DIAGNOSTIC_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        primary_type=diagnostic_data["primary_type"],
        uncertainty_level=diagnostic_data["uncertainty_level"],
        feasibility_pct=int(diagnostic_data["feasibility_score"]*100),
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE METRICS — Step 3: Define KPIs, stop-rules, MDE
# =============================================================================

CREATE_METRICS_TOOL = ckit_cloudtool.CloudTool(
    name="create_metrics",
    description="Define KPIs, MDE, stop/accelerate rules. Call after diagnostic. Reads /input and /diagnostic automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "metrics": {
                "type": "object",
                "description": "Complete metrics framework",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "primary_kpi": {"type": "string"},
                    "primary_kpi_reasoning": {"type": "string"},
                    "secondary_kpis": {"type": "array", "items": {"type": "string"}},
                    "target_values": {"type": "object", "additionalProperties": {"type": "number"}},
                    "target_values_reasoning": {"type": "string"},
                    "mde": {
                        "type": "object",
                        "properties": {
                            "relative_change": {"type": "number"},
                            "confidence": {"type": "number"}
                        },
                        "required": ["relative_change", "confidence"],
                        "additionalProperties": False
                    },
                    "mde_reasoning": {"type": "string"},
                    "min_samples": {
                        "type": "object",
                        "properties": {
                            "impressions_per_cell": {"type": "integer"},
                            "clicks_per_cell": {"type": "integer"},
                            "conversions_per_cell": {"type": "integer"}
                        },
                        "required": ["impressions_per_cell", "clicks_per_cell", "conversions_per_cell"],
                        "additionalProperties": False
                    },
                    "stop_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string"},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "min_events": {"type": "integer"},
                                "action": {"type": "string"}
                            },
                            "required": ["metric", "operator", "threshold", "min_events", "action"],
                            "additionalProperties": False
                        }
                    },
                    "stop_rules_reasoning": {"type": "string"},
                    "accelerate_rules": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric": {"type": "string"},
                                "operator": {"type": "string"},
                                "threshold": {"type": "number"},
                                "min_conversions": {"type": "integer"},
                                "action": {"type": "string"}
                            },
                            "required": ["metric", "operator", "threshold", "min_conversions", "action"],
                            "additionalProperties": False
                        }
                    },
                    "accelerate_rules_reasoning": {"type": "string"},
                    "analysis_plan": {"type": "string"},
                    "detailed_analysis": {"type": "string"},
                    "interpretation_guide": {
                        "type": "object",
                        "properties": {
                            "success_scenario": {"type": "string"},
                            "failure_scenario": {"type": "string"},
                            "inconclusive_scenario": {"type": "string"}
                        },
                        "required": ["success_scenario", "failure_scenario", "inconclusive_scenario"],
                        "additionalProperties": False
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "primary_kpi", "primary_kpi_reasoning", "secondary_kpis",
                            "target_values", "target_values_reasoning", "mde", "mde_reasoning",
                            "min_samples", "stop_rules", "stop_rules_reasoning", "accelerate_rules",
                            "accelerate_rules_reasoning", "analysis_plan", "detailed_analysis",
                            "interpretation_guide", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "metrics"],
        "additionalProperties": False
    }
)

METRICS_RESPONSE_TEMPLATE = """✍️ {path}

✓ Metrics framework complete for experiment "{experiment_id}"

Key metrics:
- Primary KPI: {primary_kpi}
- MDE: {mde_pct}% @ {confidence_pct}% confidence
- Stop rules: {stop_rules_count}
- Accelerate rules: {accelerate_rules_count}

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_metrics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    metrics_data = args["metrics"]

    error = await check_can_run_agent(experiment_id, "metrics")
    if error:
        return error

    if metrics_data["mde"]["confidence"] not in [0.8, 0.9, 0.95, 0.99]:
        return "Error: MDE confidence should be 80%, 90%, 95%, or 99% (0.8, 0.9, 0.95, 0.99)"

    if metrics_data["min_samples"]["conversions_per_cell"] < 1:
        return "Error: min_samples conversions_per_cell must be at least 1"

    doc = {"metrics": metrics_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/metrics"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return METRICS_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        primary_kpi=metrics_data["primary_kpi"],
        mde_pct=int(metrics_data["mde"]["relative_change"]*100),
        confidence_pct=int(metrics_data["mde"]["confidence"]*100),
        stop_rules_count=len(metrics_data["stop_rules"]),
        accelerate_rules_count=len(metrics_data["accelerate_rules"]),
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE SEGMENT — Step 4: ICP, JTBD, customer journey
# =============================================================================

CREATE_SEGMENT_TOOL = ckit_cloudtool.CloudTool(
    name="create_segment",
    description="Define ICP, JTBD, customer journey. Call after diagnostic. Reads /input and /diagnostic automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "segment": {
                "type": "object",
                "description": "Complete segment analysis",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "segment_id": {"type": "string"},
                    "label": {"type": "string"},
                    "segment_reasoning": {"type": "string"},
                    "icp": {
                        "type": "object",
                        "properties": {
                            "b2x": {"type": "string"},
                            "company_size": {"type": "string"},
                            "roles": {"type": "array", "items": {"type": "string"}},
                            "industries": {"type": "array", "items": {"type": "string"}},
                            "geo": {"type": "array", "items": {"type": "string"}},
                            "income_level": {"type": "string"},
                            "tech_savviness": {"type": "string"},
                            "decision_maker": {"type": "string"}
                        },
                        "required": ["b2x", "company_size", "roles", "industries", "geo", "income_level", "tech_savviness", "decision_maker"],
                        "additionalProperties": False
                    },
                    "icp_reasoning": {"type": "string"},
                    "jtbds": {
                        "type": "object",
                        "properties": {
                            "functional_jobs": {"type": "array", "items": {"type": "string"}},
                            "emotional_jobs": {"type": "array", "items": {"type": "string"}},
                            "social_jobs": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["functional_jobs", "emotional_jobs", "social_jobs"],
                        "additionalProperties": False
                    },
                    "jtbd_reasoning": {"type": "string"},
                    "current_solutions": {"type": "array", "items": {"type": "string"}},
                    "main_pains": {"type": "array", "items": {"type": "string"}},
                    "desired_gains": {"type": "array", "items": {"type": "string"}},
                    "discovery_channels": {"type": "array", "items": {"type": "string"}},
                    "journey_highlights": {
                        "type": "object",
                        "properties": {
                            "awareness": {"type": "array", "items": {"type": "string"}},
                            "consideration": {"type": "array", "items": {"type": "string"}},
                            "purchase_triggers": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["awareness", "consideration", "purchase_triggers"],
                        "additionalProperties": False
                    },
                    "segment_risks": {"type": "array", "items": {"type": "string"}},
                    "detailed_analysis": {"type": "string"},
                    "persona_narrative": {"type": "string"},
                    "targeting_implications": {
                        "type": "object",
                        "properties": {
                            "easy_to_reach_via": {"type": "array", "items": {"type": "string"}},
                            "hard_to_reach_because": {"type": "array", "items": {"type": "string"}},
                            "best_hooks": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["easy_to_reach_via", "hard_to_reach_because", "best_hooks"],
                        "additionalProperties": False
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "segment_id", "label", "segment_reasoning", "icp", "icp_reasoning",
                            "jtbds", "jtbd_reasoning", "current_solutions", "main_pains", "desired_gains",
                            "discovery_channels", "journey_highlights", "segment_risks", "detailed_analysis",
                            "persona_narrative", "targeting_implications", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "segment"],
        "additionalProperties": False
    }
)

SEGMENT_RESPONSE_TEMPLATE = """✍️ {path}

✓ Segment analysis complete for experiment "{experiment_id}"

Segment: {label}
- Roles: {roles}
- Geo: {geo}
- Jobs: {functional_jobs_count} functional, {emotional_jobs_count} emotional

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_segment(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    segment_data = args["segment"]

    error = await check_can_run_agent(experiment_id, "segment")
    if error:
        return error

    jtbds = segment_data["jtbds"]
    if not jtbds["functional_jobs"] and not jtbds["emotional_jobs"]:
        return "Error: Must define at least one functional or emotional job"

    if not segment_data["icp"]["roles"] or not segment_data["icp"]["geo"]:
        return "Error: ICP must have at least one role and one geo specified"

    doc = {"segment": segment_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/segment"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return SEGMENT_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        label=segment_data["label"],
        roles=', '.join(segment_data["icp"]["roles"][:3]),
        geo=', '.join(segment_data["icp"]["geo"][:3]),
        functional_jobs_count=len(jtbds["functional_jobs"]),
        emotional_jobs_count=len(jtbds["emotional_jobs"]),
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE MESSAGING — Step 5: Value proposition, angles, objections
# =============================================================================

CREATE_MESSAGING_TOOL = ckit_cloudtool.CloudTool(
    name="create_messaging",
    description="Create value prop, angles, objections. Call after segment. Reads /input, /diagnostic, /segment automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "messaging": {
                "type": "object",
                "description": "Complete messaging strategy",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "core_value_prop": {"type": "string"},
                    "core_value_prop_reasoning": {"type": "string"},
                    "supporting_value_props": {"type": "array", "items": {"type": "string"}},
                    "positioning_statement": {"type": "string"},
                    "positioning_reasoning": {"type": "string"},
                    "key_messages": {"type": "array", "items": {"type": "string"}},
                    "angles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "hook": {"type": "string"},
                                "description": {"type": "string"},
                                "when_to_use": {"type": "string"}
                            },
                            "required": ["name", "hook", "description", "when_to_use"],
                            "additionalProperties": False
                        }
                    },
                    "angles_reasoning": {"type": "string"},
                    "objection_handling": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objection": {"type": "string"},
                                "rebuttal": {"type": "string"},
                                "when_this_comes_up": {"type": "string"}
                            },
                            "required": ["objection", "rebuttal", "when_this_comes_up"],
                            "additionalProperties": False
                        }
                    },
                    "tone": {"type": "string"},
                    "detailed_analysis": {"type": "string"},
                    "messaging_hierarchy": {
                        "type": "object",
                        "properties": {
                            "primary_message": {"type": "string"},
                            "supporting_proof": {"type": "string"},
                            "emotional_trigger": {"type": "string"}
                        },
                        "required": ["primary_message", "supporting_proof", "emotional_trigger"],
                        "additionalProperties": False
                    },
                    "test_priority": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "angle": {"type": "string"},
                                "priority": {"type": "integer"},
                                "why": {"type": "string"}
                            },
                            "required": ["angle", "priority", "why"],
                            "additionalProperties": False
                        }
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "core_value_prop", "core_value_prop_reasoning", "supporting_value_props",
                            "positioning_statement", "positioning_reasoning", "key_messages", "angles",
                            "angles_reasoning", "objection_handling", "tone", "detailed_analysis",
                            "messaging_hierarchy", "test_priority", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "messaging"],
        "additionalProperties": False
    }
)

MESSAGING_RESPONSE_TEMPLATE = """✍️ {path}

✓ Messaging strategy complete for experiment "{experiment_id}"

- Core value prop: {core_value_prop_preview}...
- Angles: {angles_count}
- Objections handled: {objections_count}

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_messaging(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    messaging_data = args["messaging"]

    error = await check_can_run_agent(experiment_id, "messaging")
    if error:
        return error

    if not messaging_data["angles"]:
        return "Error: Must define at least one messaging angle"

    if not messaging_data["core_value_prop"]:
        return "Error: core_value_prop cannot be empty"

    doc = {"messaging": messaging_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/messaging"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return MESSAGING_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        core_value_prop_preview=messaging_data["core_value_prop"][:80],
        angles_count=len(messaging_data["angles"]),
        objections_count=len(messaging_data["objection_handling"]),
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE CHANNELS — Step 6: Channel selection, test cells, budget allocation
# =============================================================================

CREATE_CHANNELS_TOOL = ckit_cloudtool.CloudTool(
    name="create_channels",
    description="Select channels, design test cells, allocate budget. Call after messaging. Reads /input, /diagnostic, /metrics, /segment, /messaging automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "channels": {
                "type": "object",
                "description": "Complete channel strategy",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "selected_channels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "role": {"type": "string"},
                                "budget_share": {"type": "number"},
                                "rationale": {"type": "string"}
                            },
                            "required": ["channel", "role", "budget_share", "rationale"],
                            "additionalProperties": False
                        }
                    },
                    "channel_selection_reasoning": {"type": "string"},
                    "excluded_channels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "reason": {"type": "string"}
                            },
                            "required": ["channel", "reason"],
                            "additionalProperties": False
                        }
                    },
                    "test_cells": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cell_id": {"type": "string"},
                                "channel": {"type": "string"},
                                "segment": {"type": "string"},
                                "angle": {"type": "string"},
                                "landing_variant": {"type": "string"},
                                "budget": {"type": "number"},
                                "hypothesis": {"type": "string"}
                            },
                            "required": ["cell_id", "channel", "segment", "angle", "landing_variant", "budget", "hypothesis"],
                            "additionalProperties": False
                        }
                    },
                    "test_design_reasoning": {"type": "string"},
                    "total_budget": {"type": "number"},
                    "budget_allocation_reasoning": {"type": "string"},
                    "test_duration_days": {"type": "integer"},
                    "duration_reasoning": {"type": "string"},
                    "expected_metrics": {"type": "object"},
                    "detailed_analysis": {"type": "string"},
                    "experiment_logic": {
                        "type": "object",
                        "properties": {
                            "primary_question": {"type": "string"},
                            "secondary_questions": {"type": "array", "items": {"type": "string"}},
                            "what_we_wont_learn": {"type": "string"}
                        },
                        "required": ["primary_question", "secondary_questions", "what_we_wont_learn"],
                        "additionalProperties": False
                    },
                    "decision_tree": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "selected_channels", "channel_selection_reasoning", "excluded_channels",
                            "test_cells", "test_design_reasoning", "total_budget", "budget_allocation_reasoning",
                            "test_duration_days", "duration_reasoning", "expected_metrics", "detailed_analysis",
                            "experiment_logic", "decision_tree", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "channels"],
        "additionalProperties": False
    }
)

CHANNELS_RESPONSE_TEMPLATE = """✍️ {path}

✓ Channel strategy complete for experiment "{experiment_id}"

- Channels: {channels_count}
- Test cells: {test_cells_count}
- Total budget: ${total_budget}
- Duration: {duration_days} days

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_channels(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    channels_data = args["channels"]

    error = await check_can_run_agent(experiment_id, "channels")
    if error:
        return error

    total_budget_share = sum(ch["budget_share"] for ch in channels_data["selected_channels"])
    if not (0.95 <= total_budget_share <= 1.05):
        return f"Error: Budget shares sum to {total_budget_share:.2f}, should be ~1.0 (95-105%)"

    if not channels_data["test_cells"]:
        return "Error: Must define at least one test cell"

    doc = {"channels": channels_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/channels"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return CHANNELS_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        channels_count=len(channels_data["selected_channels"]),
        test_cells_count=len(channels_data["test_cells"]),
        total_budget=channels_data["total_budget"],
        duration_days=channels_data["test_duration_days"],
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE TACTICS — Step 7: Campaign specs, creatives, landing, tracking
# =============================================================================

CREATE_TACTICS_TOOL = ckit_cloudtool.CloudTool(
    name="create_tactics",
    description="Generate campaign specs, creative briefs, landing structure, tracking. Call after channels. Reads all previous docs automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "tactics": {
                "type": "object",
                "description": "Complete tactical specification",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "campaigns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "campaign_id": {"type": "string"},
                                "channel": {"type": "string"},
                                "objective": {"type": "string"},
                                "daily_budget": {"type": "number"},
                                "start_date": {"type": "string"},
                                "duration_days": {"type": "integer"},
                                "campaign_reasoning": {"type": "string"},
                                "adsets": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "additionalProperties": True
                                    }
                                }
                            },
                            "required": ["campaign_id", "channel", "objective", "daily_budget", "start_date", "duration_days", "campaign_reasoning", "adsets"],
                            "additionalProperties": False
                        }
                    },
                    "creatives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "creative_id": {"type": "string"},
                                "channel": {"type": "string"},
                                "format": {"type": "string"},
                                "angle": {"type": "string"},
                                "primary_text": {"type": "string"},
                                "headline": {"type": "string"},
                                "description": {"type": "string"},
                                "cta": {"type": "string"},
                                "visual_brief": {"type": "string"},
                                "creative_reasoning": {"type": "string"}
                            },
                            "required": ["creative_id", "channel", "format", "angle", "primary_text", "headline", "description", "cta", "visual_brief", "creative_reasoning"],
                            "additionalProperties": False
                        }
                    },
                    "creatives_strategy": {"type": "string"},
                    "landing": {
                        "type": "object",
                        "properties": {
                            "primary_goal": {"type": "string"},
                            "structure": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                            "landing_reasoning": {"type": "string"},
                            "variants": {"type": "array", "items": {"type": "object", "additionalProperties": True}}
                        },
                        "required": ["primary_goal", "structure", "landing_reasoning"],
                        "additionalProperties": False
                    },
                    "tracking": {
                        "type": "object",
                        "properties": {
                            "events": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                            "pixels": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                            "utm_schema": {"type": "object", "additionalProperties": {"type": "string"}}
                        },
                        "required": ["events", "utm_schema"],
                        "additionalProperties": False
                    },
                    "detailed_analysis": {"type": "string"},
                    "execution_checklist": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task": {"type": "string"},
                                "owner": {"type": "string"},
                                "deadline": {"type": "string"}
                            },
                            "required": ["task", "owner", "deadline"],
                            "additionalProperties": False
                        }
                    },
                    "iteration_guide": {"type": "object", "additionalProperties": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "campaigns", "creatives", "creatives_strategy", "landing", "tracking",
                            "detailed_analysis", "execution_checklist", "iteration_guide", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "tactics"],
        "additionalProperties": False
    }
)

TACTICS_RESPONSE_TEMPLATE = """✍️ {path}

✓ Tactical spec complete for experiment "{experiment_id}"

- Campaigns: {campaigns_count}
- Creatives: {creatives_count}
- Landing variants: {landing_variants_count}
- Tracking events: {tracking_events_count}

Pipeline status:
- Completed: {completed}
- Next step: {next_step}"""

async def handle_tactics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    tactics_data = args["tactics"]

    error = await check_can_run_agent(experiment_id, "tactics")
    if error:
        return error

    if not tactics_data["campaigns"]:
        return "Error: Must define at least one campaign"

    if not tactics_data["creatives"]:
        return "Error: Must define at least one creative"

    if not tactics_data["tracking"]["utm_schema"]:
        return "Error: UTM schema is required for tracking"

    doc = {"tactics": tactics_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/tactics"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    return TACTICS_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        campaigns_count=len(tactics_data["campaigns"]),
        creatives_count=len(tactics_data["creatives"]),
        landing_variants_count=len(tactics_data["landing"].get("variants", [])),
        tracking_events_count=len(tactics_data["tracking"]["events"]),
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
    )


# =============================================================================
# CREATE COMPLIANCE — Step 8: Risk & compliance check
# =============================================================================

CREATE_COMPLIANCE_TOOL = ckit_cloudtool.CloudTool(
    name="create_compliance",
    description="Check risks, ad policies, privacy compliance. Call after tactics. Reads /input and /tactics automatically.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{slug}"},
            "compliance": {
                "type": "object",
                "description": "Complete compliance check",
                "properties": {
                    "meta": {
                        "type": "object",
                        "properties": {
                            "created_at": {"type": "string"},
                            "version": {"type": "string"},
                            "experiment_id": {"type": "string"}
                        },
                        "required": ["created_at", "version", "experiment_id"],
                        "additionalProperties": False
                    },
                    "risks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "risk_id": {"type": "string"},
                                "category": {"type": "string"},
                                "description": {"type": "string"},
                                "probability": {"type": "string", "enum": ["low", "medium", "high"]},
                                "impact": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "mitigation": {"type": "string"},
                                "if_ignored": {"type": "string"}
                            },
                            "required": ["risk_id", "category", "description", "probability", "impact", "mitigation", "if_ignored"],
                            "additionalProperties": False
                        }
                    },
                    "risk_assessment_reasoning": {"type": "string"},
                    "compliance_issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "issue_id": {"type": "string"},
                                "platform": {"type": "string"},
                                "policy": {"type": "string"},
                                "issue": {"type": "string"},
                                "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                                "recommendation": {"type": "string"},
                                "affected_creatives": {"type": "array", "items": {"type": "string"}},
                                "what_if_rejected": {"type": "string"}
                            },
                            "required": ["issue_id", "platform", "policy", "issue", "severity", "recommendation", "affected_creatives", "what_if_rejected"],
                            "additionalProperties": False
                        }
                    },
                    "compliance_reasoning": {"type": "string"},
                    "privacy_check": {
                        "type": "object",
                        "properties": {
                            "gdpr_compliant": {"type": "boolean"},
                            "ccpa_compliant": {"type": "boolean"},
                            "cookie_consent_required": {"type": "boolean"},
                            "notes": {"type": "string"}
                        },
                        "required": ["gdpr_compliant", "ccpa_compliant", "cookie_consent_required", "notes"],
                        "additionalProperties": False
                    },
                    "overall_assessment": {
                        "type": "object",
                        "properties": {
                            "ads_policies_ok": {"type": "boolean"},
                            "privacy_ok": {"type": "boolean"},
                            "business_risks_acceptable": {"type": "boolean"},
                            "recommendation": {"type": "string"},
                            "confidence_level": {"type": "string"}
                        },
                        "required": ["ads_policies_ok", "privacy_ok", "business_risks_acceptable", "recommendation", "confidence_level"],
                        "additionalProperties": False
                    },
                    "detailed_analysis": {"type": "string"},
                    "pre_launch_checklist": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "check": {"type": "string"},
                                "status": {"type": "string"}
                            },
                            "required": ["check", "status"],
                            "additionalProperties": False
                        }
                    },
                    "contingency_plans": {"type": "object", "additionalProperties": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["meta", "risks", "risk_assessment_reasoning", "compliance_issues", "compliance_reasoning",
                            "privacy_check", "overall_assessment", "detailed_analysis", "pre_launch_checklist",
                            "contingency_plans", "next_steps"],
                "additionalProperties": False
            }
        },
        "required": ["experiment_id", "compliance"],
        "additionalProperties": False
    }
)

COMPLIANCE_RESPONSE_TEMPLATE = """✍️ {path}

✓ Compliance check complete for experiment "{experiment_id}"

Assessment:
- Ads policies: {ads_policies_icon}
- Privacy: {privacy_icon}
- Business risks: {business_risks_icon}
- Recommendation: {recommendation}

Pipeline status:
- Completed: {completed}
- Next step: {next_step}

{completion_message}"""

async def handle_compliance(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], rcx: ckit_bot_exec.RobotContext, pdoc_integration: fi_pdoc.IntegrationPdoc, get_pipeline_status, check_can_run_agent) -> str:
    experiment_id = args["experiment_id"]
    compliance_data = args["compliance"]

    error = await check_can_run_agent(experiment_id, "compliance")
    if error:
        return error

    if not compliance_data["risks"] and not compliance_data["compliance_issues"]:
        return "Error: Must identify at least one risk or compliance issue, or explicitly state 'none' in detailed_analysis"

    for risk in compliance_data["risks"]:
        if risk["probability"] not in ["low", "medium", "high"]:
            return f"Error: Risk {risk['risk_id']} has invalid probability (must be low/medium/high)"
        if risk["impact"] not in ["low", "medium", "high", "critical"]:
            return f"Error: Risk {risk['risk_id']} has invalid impact (must be low/medium/high/critical)"

    doc = {"compliance": compliance_data}
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/marketing-experiments/{experiment_id}/compliance"
    await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    status = await get_pipeline_status(experiment_id)
    assessment = compliance_data["overall_assessment"]
    return COMPLIANCE_RESPONSE_TEMPLATE.format(
        path=path,
        experiment_id=experiment_id,
        ads_policies_icon='✓' if assessment["ads_policies_ok"] else '⚠',
        privacy_icon='✓' if assessment["privacy_ok"] else '⚠',
        business_risks_icon='✓' if assessment["business_risks_acceptable"] else '⚠',
        recommendation=assessment["recommendation"],
        completed=', '.join(status['completed']),
        next_step=status['next_step'] or 'all done',
        completion_message='✓ All steps completed! Strategy ready for Ad Monster.' if status['all_done'] else '',
    )


# =============================================================================
# GET PIPELINE STATUS — Query current pipeline state
# =============================================================================

GET_PIPELINE_STATUS_TOOL = ckit_cloudtool.CloudTool(
    name="get_pipeline_status",
    description="Get current pipeline status for marketing experiment — which steps are done, which is next.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {"type": "string", "description": "{hyp_id}-{experiment-slug}"},
        },
        "required": ["experiment_id"],
        "additionalProperties": False,
    },
)

async def handle_pipeline_status(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any], get_pipeline_status) -> str:
    experiment_id = args.get("experiment_id", "")
    if not experiment_id:
        return "Error: experiment_id is required (format: {hyp_id}-{slug})"

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


# =============================================================================
# MAIN LOOP
# =============================================================================

TOOLS = [
    SAVE_INPUT_TOOL,
    CREATE_DIAGNOSTIC_TOOL,
    CREATE_METRICS_TOOL,
    CREATE_SEGMENT_TOOL,
    CREATE_MESSAGING_TOOL,
    CREATE_CHANNELS_TOOL,
    CREATE_TACTICS_TOOL,
    CREATE_COMPLIANCE_TOOL,
    GET_PIPELINE_STATUS_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]

async def owl2_strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    owner_fuser_id = rcx.persona.owner_fuser_id

    async def get_pipeline_status(experiment_id: str) -> Dict[str, Any]:
        try:
            items = await pdoc_integration.pdoc_list(f"/marketing-experiments/{experiment_id}", owner_fuser_id)
            existing_steps = {item.path.split('/')[-1] for item in items if not item.is_folder}
        except Exception:
            existing_steps = set()

        completed = []
        for step in PIPELINE:
            if step in existing_steps:
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
        status = await get_pipeline_status(experiment_id)
        if prev_step not in status["completed"]:
            return f"Cannot run {agent} — must complete {prev_step} first. Order: {' → '.join(PIPELINE)}"
        return None

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
        return await handle_save_input(toolcall, args, rcx, pdoc_integration, get_pipeline_status)

    @rcx.on_tool_call(CREATE_DIAGNOSTIC_TOOL.name)
    async def toolcall_diagnostic(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_diagnostic(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_METRICS_TOOL.name)
    async def toolcall_metrics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_metrics(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_SEGMENT_TOOL.name)
    async def toolcall_segment(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_segment(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_MESSAGING_TOOL.name)
    async def toolcall_messaging(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_messaging(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_CHANNELS_TOOL.name)
    async def toolcall_channels(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_channels(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_TACTICS_TOOL.name)
    async def toolcall_tactics(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_tactics(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(CREATE_COMPLIANCE_TOOL.name)
    async def toolcall_compliance(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_compliance(toolcall, args, rcx, pdoc_integration, get_pipeline_status, check_can_run_agent)

    @rcx.on_tool_call(GET_PIPELINE_STATUS_TOOL.name)
    async def toolcall_pipeline_status(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_pipeline_status(toolcall, args, get_pipeline_status)

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
        bot_main_loop=owl2_strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=owl2_strategist_install.install,
    ))


if __name__ == "__main__":
    main()
