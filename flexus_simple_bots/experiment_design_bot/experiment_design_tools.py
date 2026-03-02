import importlib
import json
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

_API_TOOL_PARAMS = {
    "type": "object",
    "properties": {
        "op": {"type": "string", "enum": ["help", "status", "list_providers", "list_methods", "call"]},
        "args": {"type": ["object", "null"]},
    },
    "required": ["op", "args"],
    "additionalProperties": False,
}

EXPERIMENT_BACKLOG_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="experiment_backlog_ops_api",
    description="experiment_backlog_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

EXPERIMENT_RUNTIME_CONFIG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="experiment_runtime_config_api",
    description="experiment_runtime_config_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

EXPERIMENT_GUARDRAIL_METRICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="experiment_guardrail_metrics_api",
    description="experiment_guardrail_metrics_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="experiment_instrumentation_quality_api",
    description="experiment_instrumentation_quality_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    EXPERIMENT_BACKLOG_OPS_TOOL,
    EXPERIMENT_RUNTIME_CONFIG_TOOL,
    EXPERIMENT_GUARDRAIL_METRICS_TOOL,
    EXPERIMENT_INSTRUMENTATION_QUALITY_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "experiment_backlog_ops_api": [
        "jira.issues.create.v1",
        "jira.issues.search.v1",
        "linear.issues.create.v1",
        "linear.issues.list.v1",
        "notion.pages.create.v1",
        "notion.pages.search.v1",
    ],
    "experiment_runtime_config_api": [
        "launchdarkly.flags.get.v1",
        "launchdarkly.flags.patch.v1",
        "statsig.experiments.create.v1",
        "statsig.experiments.update.v1",
        "optimizely.experiments.create.v1",
        "optimizely.experiments.get.v1",
    ],
    "experiment_guardrail_metrics_api": [
        "posthog.insights.trend.query.v1",
        "posthog.insights.funnel.query.v1",
        "mixpanel.retention.query.v1",
        "mixpanel.frequency.query.v1",
        "amplitude.dashboardrest.chart.get.v1",
        "ga4.properties.run_report.v1",
    ],
    "experiment_instrumentation_quality_api": [
        "segment.tracking_plans.list.v1",
        "segment.tracking_plans.get.v1",
        "sentry.organizations.issues.list.v1",
    ],
}


def _tool_call_help(tool_name: str) -> str:
    try:
        return (
            f"{tool_name}(op=\"help\")\n"
            f"{tool_name}(op=\"status\")\n"
            f"{tool_name}(op=\"list_providers\")\n"
            f"{tool_name}(op=\"list_methods\", args={{\"provider\": \"<provider>\"}})\n"
            f"{tool_name}(op=\"call\", args={{\"method_id\": \"<provider>.<resource>.<action>.v1\"}})"
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build help for {tool_name}: {e}") from e


def _tool_allowed_methods(tool_name: str) -> list[str]:
    try:
        return TOOL_ALLOWED_METHOD_IDS.get(tool_name, [])
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot get method list for {tool_name}: {e}") from e


def _tool_allowed_providers(tool_name: str) -> list[str]:
    try:
        providers: set[str] = set()
        for method_id in _tool_allowed_methods(tool_name):
            providers.add(method_id.split(".", 1)[0])
        return sorted(providers)
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot get provider list for {tool_name}: {e}") from e


def _sanitize_args(model_produced_args: Optional[Dict[str, Any]]) -> tuple[dict[str, Any], str]:
    try:
        if not model_produced_args:
            return {}, ""
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return {}, args_error
        if args is None:
            return {}, ""
        if not isinstance(args, dict):
            return {}, "Error: args must be an object."
        return args, ""
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        return {}, f"Error: cannot sanitize args: {type(e).__name__}: {e}"


async def handle_api_tool_call(
    tool_name: str,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    """Entry point called by each API tool handler in the bot main loop."""
    try:
        if tool_name not in TOOL_ALLOWED_METHOD_IDS:
            return "Error: unknown tool."

        allowed_method_ids = set(_tool_allowed_methods(tool_name))
        allowed_providers = _tool_allowed_providers(tool_name)

        if not model_produced_args:
            return _tool_call_help(tool_name)

        op = str(model_produced_args.get("op", "help")).strip()
        args, args_error = _sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if op == "help":
            return _tool_call_help(tool_name)

        if op == "status":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "status": "available",
                "providers_count": len(allowed_providers),
                "method_count": len(allowed_method_ids),
            }, indent=2, ensure_ascii=False)

        if op == "list_providers":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "providers": allowed_providers,
            }, indent=2, ensure_ascii=False)

        if op == "list_methods":
            provider = str(args.get("provider", "")).strip()
            if not provider:
                return "Error: args.provider is required for op=list_methods."
            if provider not in allowed_providers:
                return "Error: unknown provider for this tool."
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "provider": provider,
                "method_ids": [x for x in _tool_allowed_methods(tool_name) if x.startswith(provider + ".")],
            }, indent=2, ensure_ascii=False)

        if op != "call":
            return "Error: unsupported op. Use help/status/list_providers/list_methods/call."

        method_id = str(args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id is required for op=call."
        if "." not in method_id:
            return "Error: invalid method_id format."
        if method_id not in allowed_method_ids:
            return "Error: method_id is not allowed for this tool."

        provider = method_id.split(".", 1)[0]
        if provider not in allowed_providers:
            return "Error: provider is not allowed for this tool."

        try:
            mod = importlib.import_module(f"flexus_client_kit.integrations.fi_{provider}")
        except ModuleNotFoundError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        class_name = "Integration" + "".join(w.capitalize() for w in provider.split("_"))
        integration_class = getattr(mod, class_name, None)
        if integration_class is None:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        try:
            integration = integration_class()
        except TypeError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        return await integration.called_by_model(toolcall, model_produced_args)
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        return f"Error in {tool_name}: {type(e).__name__}: {e}"


# =============================================================================
# WRITE TOOLS — structured output, schema enforced by strict=True
# =============================================================================

_SOURCE_ITEM = {
    "type": "object",
    "properties": {
        "source_type": {"type": "string", "enum": ["api", "artifact", "tool_output", "event_stream", "expert_handoff", "user_directive"]},
        "source_ref": {"type": "string"},
    },
    "required": ["source_type", "source_ref"],
    "additionalProperties": False,
}

WRITE_EXPERIMENT_CARD_DRAFT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_card_draft",
    description="Write a completed experiment card draft to a policy document. Call once per batch of experiment cards.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/card-draft-2024-01-15"},
            "experiment_card_draft": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_card_draft"]},
                    "version": {"type": "string"},
                    "prioritization_rule": {"type": "string", "enum": ["impact_x_confidence_x_reversibility"]},
                    "experiment_cards": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "experiment_id": {"type": "string"},
                                "hypothesis": {"type": "string"},
                                "target_segment": {"type": "string"},
                                "primary_metric": {"type": "string"},
                                "guardrail_metrics": {"type": "array", "items": {"type": "string"}},
                                "sample_definition": {
                                    "type": "object",
                                    "properties": {
                                        "unit": {"type": "string"},
                                        "target_n": {"type": "integer", "minimum": 1},
                                        "allocation": {"type": "string"},
                                    },
                                    "required": ["unit", "target_n", "allocation"],
                                    "additionalProperties": False,
                                },
                                "runbook": {"type": "array", "items": {"type": "string"}},
                                "stop_conditions": {"type": "array", "items": {"type": "string"}},
                                "owner": {"type": "string"},
                                "priority_rank": {"type": "integer", "minimum": 1},
                            },
                            "required": [
                                "experiment_id", "hypothesis", "target_segment", "primary_metric",
                                "guardrail_metrics", "sample_definition", "runbook",
                                "stop_conditions", "owner", "priority_rank",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": ["artifact_type", "version", "experiment_cards", "prioritization_rule", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_card_draft"],
        "additionalProperties": False,
    },
)

WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_measurement_spec",
    description="Write a measurement spec for one experiment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/measurement-spec-exp-001"},
            "experiment_measurement_spec": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_measurement_spec"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "metrics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric_id": {"type": "string"},
                                "metric_name": {"type": "string"},
                                "metric_type": {"type": "string", "enum": ["primary", "guardrail", "diagnostic"]},
                                "formula": {"type": "string"},
                                "data_source": {"type": "string"},
                            },
                            "required": ["metric_id", "metric_name", "metric_type", "formula", "data_source"],
                            "additionalProperties": False,
                        },
                    },
                    "event_requirements": {"type": "array", "items": {"type": "string"}},
                    "quality_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "experiment_id", "metrics", "event_requirements", "quality_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_measurement_spec"],
        "additionalProperties": False,
    },
)

WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_backlog_prioritization",
    description="Write a prioritized experiment backlog to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/backlog-2024-01-15"},
            "experiment_backlog_prioritization": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_backlog_prioritization"]},
                    "version": {"type": "string"},
                    "backlog": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "experiment_id": {"type": "string"},
                                "impact_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "reversibility_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "priority_score": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["experiment_id", "impact_score", "confidence_score", "reversibility_score", "priority_score"],
                            "additionalProperties": False,
                        },
                    },
                    "top_candidates": {"type": "array", "items": {"type": "string"}},
                    "deferred_items": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "backlog", "top_candidates", "deferred_items"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_backlog_prioritization"],
        "additionalProperties": False,
    },
)

WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_reliability_report",
    description="Write a reliability report for one experiment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/reliability-report-exp-001"},
            "experiment_reliability_report": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_reliability_report"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "reliability_checks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "check_id": {"type": "string"},
                                "result": {"type": "string", "enum": ["pass", "warn", "fail"]},
                                "notes": {"type": "string"},
                            },
                            "required": ["check_id", "result", "notes"],
                            "additionalProperties": False,
                        },
                    },
                    "pass_fail": {"type": "string", "enum": ["pass", "fail"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": ["artifact_type", "version", "experiment_id", "reliability_checks", "pass_fail", "blocking_issues", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_reliability_report"],
        "additionalProperties": False,
    },
)

WRITE_EXPERIMENT_APPROVAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_approval",
    description="Write an experiment approval decision to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/approval-exp-001"},
            "experiment_approval": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_approval"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "approval_state": {"type": "string", "enum": ["approved", "revise", "rejected"]},
                    "approval_reason": {"type": "string"},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "required_fixes": {"type": "array", "items": {"type": "string"}},
                    "go_live_constraints": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "experiment_id", "approval_state",
                    "approval_reason", "blocking_issues", "required_fixes", "go_live_constraints",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_approval"],
        "additionalProperties": False,
    },
)

WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_experiment_stop_rule_evaluation",
    description="Write a stop-rule evaluation for a running experiment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /experiments/stop-rule-exp-001-2024-01-15"},
            "experiment_stop_rule_evaluation": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["experiment_stop_rule_evaluation"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "evaluation_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "stop_rule_status": {"type": "string", "enum": ["not_triggered", "triggered_guardrail", "triggered_success", "inconclusive"]},
                    "triggered_rules": {"type": "array", "items": {"type": "string"}},
                    "recommended_action": {"type": "string", "enum": ["continue", "pause", "stop", "ship_variant"]},
                },
                "required": [
                    "artifact_type", "version", "experiment_id", "evaluation_window",
                    "stop_rule_status", "triggered_rules", "recommended_action",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "experiment_stop_rule_evaluation"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_EXPERIMENT_CARD_DRAFT_TOOL,
    WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL,
    WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL,
    WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL,
    WRITE_EXPERIMENT_APPROVAL_TOOL,
    WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL,
]


async def handle_write_experiment_card_draft(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        card_draft = args.get("experiment_card_draft")
        if not path or card_draft is None:
            return "Error: path and experiment_card_draft are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_card_draft": card_draft}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment card draft saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment card draft: {type(e).__name__}: {e}"


async def handle_write_experiment_measurement_spec(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        spec = args.get("experiment_measurement_spec")
        if not path or spec is None:
            return "Error: path and experiment_measurement_spec are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_measurement_spec": spec}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment measurement spec saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment measurement spec: {type(e).__name__}: {e}"


async def handle_write_experiment_backlog_prioritization(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        backlog = args.get("experiment_backlog_prioritization")
        if not path or backlog is None:
            return "Error: path and experiment_backlog_prioritization are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_backlog_prioritization": backlog}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment backlog prioritization saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment backlog prioritization: {type(e).__name__}: {e}"


async def handle_write_experiment_reliability_report(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        report = args.get("experiment_reliability_report")
        if not path or report is None:
            return "Error: path and experiment_reliability_report are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_reliability_report": report}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment reliability report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment reliability report: {type(e).__name__}: {e}"


async def handle_write_experiment_approval(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        approval = args.get("experiment_approval")
        if not path or approval is None:
            return "Error: path and experiment_approval are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_approval": approval}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment approval saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment approval: {type(e).__name__}: {e}"


async def handle_write_experiment_stop_rule_evaluation(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        evaluation = args.get("experiment_stop_rule_evaluation")
        if not path or evaluation is None:
            return "Error: path and experiment_stop_rule_evaluation are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"experiment_stop_rule_evaluation": evaluation}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nExperiment stop rule evaluation saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment stop rule evaluation: {type(e).__name__}: {e}"
