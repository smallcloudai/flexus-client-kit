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

MVP_EXPERIMENT_ORCHESTRATION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="mvp_experiment_orchestration_api",
    description="mvp_experiment_orchestration_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

MVP_TELEMETRY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="mvp_telemetry_api",
    description="mvp_telemetry_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

MVP_FEEDBACK_CAPTURE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="mvp_feedback_capture_api",
    description="mvp_feedback_capture_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

MVP_INSTRUMENTATION_HEALTH_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="mvp_instrumentation_health_api",
    description="mvp_instrumentation_health_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    MVP_EXPERIMENT_ORCHESTRATION_TOOL,
    MVP_TELEMETRY_TOOL,
    MVP_FEEDBACK_CAPTURE_TOOL,
    MVP_INSTRUMENTATION_HEALTH_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "mvp_experiment_orchestration_api": [
        "launchdarkly.flags.get.v1",
        "launchdarkly.flags.patch.v1",
        "statsig.experiments.create.v1",
        "statsig.experiments.update.v1",
        "jira.issues.create.v1",
        "jira.issues.transition.v1",
    ],
    "mvp_telemetry_api": [
        "posthog.insights.trend.query.v1",
        "posthog.insights.funnel.query.v1",
        "mixpanel.funnels.query.v1",
        "mixpanel.retention.query.v1",
        "amplitude.dashboardrest.chart.get.v1",
        "ga4.properties.run_report.v1",
        "datadog.metrics.timeseries.query.v1",
    ],
    "mvp_feedback_capture_api": [
        "intercom.conversations.list.v1",
        "intercom.conversations.search.v1",
        "typeform.responses.list.v1",
        "zendesk.tickets.search.v1",
        "zendesk.ticket_comments.list.v1",
    ],
    "mvp_instrumentation_health_api": [
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
# WRITE TOOLS — owl-style structured output, schema enforced by strict=True
# =============================================================================

WRITE_MVP_RUN_LOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_mvp_run_log",
    description="Write a completed MVP run log to a policy document. Call once per run to record lifecycle, delivery events, and guardrail status.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/run-log-{run_id}"},
            "run_log": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["mvp_run_log"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "hypothesis_ref": {"type": "string"},
                    "cohort_definition": {
                        "type": "object",
                        "properties": {
                            "segment_id": {"type": "string"},
                            "target_n": {"type": "integer", "minimum": 1},
                            "allocation": {"type": "string"},
                        },
                        "required": ["segment_id", "target_n", "allocation"],
                        "additionalProperties": False,
                    },
                    "rollout_plan": {"type": "array", "items": {"type": "string"}},
                    "activation_path": {"type": "array", "items": {"type": "string"}},
                    "delivery_log": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ts": {"type": "string"},
                                "event": {"type": "string"},
                                "status": {"type": "string", "enum": ["ok", "warn", "fail"]},
                                "notes": {"type": ["string", "null"]},
                            },
                            "required": ["ts", "event", "status", "notes"],
                            "additionalProperties": False,
                        },
                    },
                    "guardrail_events": {"type": "array", "items": {"type": "string"}},
                    "status": {"type": "string", "enum": ["planned", "running", "paused", "rolled_back", "completed"]},
                },
                "required": [
                    "artifact_type", "version", "run_id", "hypothesis_ref",
                    "cohort_definition", "rollout_plan", "activation_path",
                    "delivery_log", "guardrail_events", "status",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "run_log"],
        "additionalProperties": False,
    },
)

WRITE_MVP_ROLLOUT_INCIDENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_mvp_rollout_incident",
    description="Write a rollout incident report to a policy document. Call when guardrail breach or critical issue is detected.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/incident-{run_id}"},
            "incident": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["mvp_rollout_incident"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "incidents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "incident_id": {"type": "string"},
                                "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "description": {"type": "string"},
                                "mitigation": {"type": "string"},
                            },
                            "required": ["incident_id", "severity", "description", "mitigation"],
                            "additionalProperties": False,
                        },
                    },
                    "impact_summary": {"type": "array", "items": {"type": "string"}},
                    "resolved": {"type": "boolean"},
                },
                "required": ["artifact_type", "version", "run_id", "incidents", "impact_summary", "resolved"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "incident"],
        "additionalProperties": False,
    },
)

WRITE_MVP_FEEDBACK_DIGEST_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_mvp_feedback_digest",
    description="Write a synthesized feedback digest to a policy document. Call after aggregating user feedback for a run.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/feedback-{run_id}"},
            "digest": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["mvp_feedback_digest"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "feedback_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "themes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "theme_id": {"type": "string"},
                                "theme_summary": {"type": "string"},
                                "evidence_count": {"type": "integer", "minimum": 0},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["theme_id", "theme_summary", "evidence_count", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "critical_quotes": {"type": "array", "items": {"type": "string"}},
                    "sentiment_distribution": {
                        "type": "object",
                        "properties": {
                            "positive": {"type": ["number", "null"]},
                            "negative": {"type": ["number", "null"]},
                            "neutral": {"type": ["number", "null"]},
                            "mixed": {"type": ["number", "null"]},
                        },
                        "required": ["positive", "negative", "neutral", "mixed"],
                        "additionalProperties": False,
                    },
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "run_id", "feedback_window",
                    "themes", "critical_quotes", "sentiment_distribution", "next_checks",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "digest"],
        "additionalProperties": False,
    },
)

WRITE_TELEMETRY_QUALITY_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_telemetry_quality_report",
    description="Write a telemetry quality audit report to a policy document. Call after validating event coverage, metric lineage, and instrumentation health.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/telemetry-quality-{run_id}"},
            "report": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["telemetry_quality_report"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "quality_checks": {
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
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "lineage_status": {"type": "string", "enum": ["verified", "partial", "unknown"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "artifact_type", "version", "run_id", "quality_checks",
                    "coverage_status", "lineage_status", "blocking_issues", "confidence",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "report"],
        "additionalProperties": False,
    },
)

WRITE_TELEMETRY_DECISION_MEMO_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_telemetry_decision_memo",
    description="Write a telemetry-based decision memo (scale/iterate/stop) to a policy document. Call after completing telemetry integrity analysis.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/decision-memo-{run_id}"},
            "memo": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["telemetry_decision_memo"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "metric_summary": {
                        "type": "object",
                        "properties": {
                            "primary_metric": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "value": {"type": "number"},
                                    "unit": {"type": "string"},
                                },
                                "required": ["name", "value", "unit"],
                                "additionalProperties": False,
                            },
                            "guardrails": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "number"},
                                        "threshold": {"type": "number"},
                                        "status": {"type": "string", "enum": ["ok", "warn", "fail"]},
                                    },
                                    "required": ["name", "value", "threshold", "status"],
                                    "additionalProperties": False,
                                },
                            },
                            "window": {"type": "string"},
                        },
                        "required": ["primary_metric", "guardrails", "window"],
                        "additionalProperties": False,
                    },
                    "decision": {"type": "string", "enum": ["scale", "iterate", "stop"]},
                    "decision_reason": {"type": "string"},
                    "next_step": {"type": "string"},
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_type": {"type": "string", "enum": ["api", "artifact", "tool_output", "event_stream", "expert_handoff", "user_directive"]},
                                "source_ref": {"type": "string"},
                            },
                            "required": ["source_type", "source_ref"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "artifact_type", "version", "run_id", "metric_summary",
                    "decision", "decision_reason", "next_step", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "memo"],
        "additionalProperties": False,
    },
)

WRITE_MVP_SCALE_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_mvp_scale_readiness_gate",
    description="Write a scale readiness gate verdict to a policy document. Call as the final go/no-go decision before scaling.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /mvp/scale-gate-{run_id}"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["mvp_scale_readiness_gate"]},
                    "version": {"type": "string"},
                    "run_id": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "override_required": {"type": "boolean"},
                    "recommended_action": {"type": "string", "enum": ["scale", "iterate", "stop"]},
                },
                "required": [
                    "artifact_type", "version", "run_id", "gate_status",
                    "blocking_issues", "override_required", "recommended_action",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "gate"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_MVP_RUN_LOG_TOOL,
    WRITE_MVP_ROLLOUT_INCIDENT_TOOL,
    WRITE_MVP_FEEDBACK_DIGEST_TOOL,
    WRITE_TELEMETRY_QUALITY_REPORT_TOOL,
    WRITE_TELEMETRY_DECISION_MEMO_TOOL,
    WRITE_MVP_SCALE_READINESS_GATE_TOOL,
]


async def handle_write_mvp_run_log(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        run_log = args.get("run_log")
        if not path or run_log is None:
            return "Error: path and run_log are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"mvp_run_log": run_log}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nMVP run log saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_run_log: {type(e).__name__}: {e}"


async def handle_write_mvp_rollout_incident(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        incident = args.get("incident")
        if not path or incident is None:
            return "Error: path and incident are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"mvp_rollout_incident": incident}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRollout incident report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_rollout_incident: {type(e).__name__}: {e}"


async def handle_write_mvp_feedback_digest(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        digest = args.get("digest")
        if not path or digest is None:
            return "Error: path and digest are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"mvp_feedback_digest": digest}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nFeedback digest saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_feedback_digest: {type(e).__name__}: {e}"


async def handle_write_telemetry_quality_report(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        report = args.get("report")
        if not path or report is None:
            return "Error: path and report are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"telemetry_quality_report": report}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nTelemetry quality report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing telemetry_quality_report: {type(e).__name__}: {e}"


async def handle_write_telemetry_decision_memo(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        memo = args.get("memo")
        if not path or memo is None:
            return "Error: path and memo are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"telemetry_decision_memo": memo}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nTelemetry decision memo saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing telemetry_decision_memo: {type(e).__name__}: {e}"


async def handle_write_mvp_scale_readiness_gate(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        gate = args.get("gate")
        if not path or gate is None:
            return "Error: path and gate are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"mvp_scale_readiness_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nScale readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_scale_readiness_gate: {type(e).__name__}: {e}"
