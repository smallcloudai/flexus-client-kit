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

CHURN_FEEDBACK_CAPTURE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="churn_feedback_capture_api",
    description="churn_feedback_capture_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

CHURN_INTERVIEW_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="churn_interview_ops_api",
    description="churn_interview_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

CHURN_TRANSCRIPT_ANALYSIS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="churn_transcript_analysis_api",
    description="churn_transcript_analysis_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

CHURN_REMEDIATION_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="churn_remediation_backlog_api",
    description="churn_remediation_backlog_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    CHURN_FEEDBACK_CAPTURE_TOOL,
    CHURN_INTERVIEW_OPS_TOOL,
    CHURN_TRANSCRIPT_ANALYSIS_TOOL,
    CHURN_REMEDIATION_BACKLOG_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "churn_feedback_capture_api": [
        "intercom.conversations.search.v1",
        "zendesk.tickets.search.v1",
        "stripe.subscriptions.list.v1",
        "stripe.invoices.list.v1",
        "chargebee.subscriptions.list.v1",
        "hubspot.deals.search.v1",
    ],
    "churn_interview_ops_api": [
        "calendly.scheduled_events.list.v1",
        "google_calendar.events.insert.v1",
        "google_calendar.events.list.v1",
        "zoom.meetings.recordings.get.v1",
    ],
    "churn_transcript_analysis_api": [
        "gong.calls.list.v1",
        "gong.calls.transcript.get.v1",
        "fireflies.transcript.get.v1",
        "zoom.meetings.recordings.get.v1",
    ],
    "churn_remediation_backlog_api": [
        "jira.issues.create.v1",
        "jira.issues.transition.v1",
        "asana.tasks.create.v1",
        "linear.issues.create.v1",
        "notion.pages.create.v1",
        "notion.pages.update.v1",
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

WRITE_INTERVIEW_CORPUS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_interview_corpus",
    description="Write a churn interview corpus artifact after completing interviews for a segment.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/interviews/corpus-2024-01-15"},
            "corpus": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_interview_corpus"]},
                    "version": {"type": "string"},
                    "analysis_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "segment_filters": {"type": "array", "items": {"type": "string"}},
                    "accounts": {"type": "array", "items": {"type": "string"}},
                    "interview_records": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "interview_id": {"type": "string"},
                                "account_ref": {"type": "string"},
                                "churn_event_ref": {"type": "string"},
                                "interview_date": {"type": "string"},
                                "participants": {"type": "array", "items": {"type": "string"}},
                                "transcript_ref": {"type": "string"},
                                "key_quotes": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["interview_id", "account_ref", "churn_event_ref", "interview_date", "participants", "transcript_ref", "key_quotes"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_summary": {
                        "type": "object",
                        "properties": {
                            "scheduled_count": {"type": "number", "minimum": 0},
                            "completed_count": {"type": "number", "minimum": 0},
                            "coverage_rate": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["scheduled_count", "completed_count", "coverage_rate"],
                        "additionalProperties": False,
                    },
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
                "required": ["artifact_type", "version", "analysis_window", "segment_filters", "accounts", "interview_records", "coverage_summary", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "corpus"],
        "additionalProperties": False,
    },
)

WRITE_INTERVIEW_COVERAGE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_interview_coverage",
    description="Write a churn interview coverage report tracking gaps and required follow-ups.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/interviews/coverage-2024-01-15"},
            "coverage": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_interview_coverage"]},
                    "version": {"type": "string"},
                    "target_segments": {"type": "array", "items": {"type": "string"}},
                    "completed_interviews": {"type": "array", "items": {"type": "string"}},
                    "coverage_gaps": {"type": "array", "items": {"type": "string"}},
                    "required_followups": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "target_segments", "completed_interviews", "coverage_gaps", "required_followups"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "coverage"],
        "additionalProperties": False,
    },
)

WRITE_SIGNAL_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_signal_quality",
    description="Write a churn signal quality report with pass/fail checks and remediation actions.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/quality/signal-2024-01-15"},
            "quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_signal_quality"]},
                    "version": {"type": "string"},
                    "quality_checks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "check_id": {"type": "string"},
                                "status": {"type": "string", "enum": ["pass", "fail"]},
                                "notes": {"type": ["string", "null"]},
                            },
                            "required": ["check_id", "status", "notes"],
                            "additionalProperties": False,
                        },
                    },
                    "failed_checks": {"type": "array", "items": {"type": "string"}},
                    "remediation_actions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "quality_checks", "failed_checks", "remediation_actions"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "quality"],
        "additionalProperties": False,
    },
)

WRITE_ROOTCAUSE_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_rootcause_backlog",
    description="Write the churn root-cause backlog with prioritized fix items linked to owners.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/rootcause/backlog-2024-01-15"},
            "backlog": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_rootcause_backlog"]},
                    "version": {"type": "string"},
                    "analysis_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "rootcauses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rootcause_id": {"type": "string"},
                                "theme": {"type": "string"},
                                "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "frequency": {"type": "number", "minimum": 0},
                                "evidence_refs": {"type": "array", "items": {"type": "string"}},
                                "affected_segments": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["rootcause_id", "theme", "severity", "frequency", "evidence_refs", "affected_segments"],
                            "additionalProperties": False,
                        },
                    },
                    "fix_backlog": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "fix_id": {"type": "string"},
                                "rootcause_id": {"type": "string"},
                                "owner": {"type": "string"},
                                "target_date": {"type": "string"},
                                "expected_retention_impact": {"type": "number", "minimum": 0},
                                "priority": {"type": "string", "enum": ["p0", "p1", "p2"]},
                            },
                            "required": ["fix_id", "rootcause_id", "owner", "target_date", "expected_retention_impact", "priority"],
                            "additionalProperties": False,
                        },
                    },
                    "confidence_notes": {"type": "array", "items": {"type": "string"}},
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
                "required": ["artifact_type", "version", "analysis_window", "rootcauses", "fix_backlog", "confidence_notes", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "backlog"],
        "additionalProperties": False,
    },
)

WRITE_FIX_EXPERIMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_fix_experiment_plan",
    description="Write a churn fix experiment plan with measurement criteria and stop conditions.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/experiments/plan-2024-01-15"},
            "plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_fix_experiment_plan"]},
                    "version": {"type": "string"},
                    "experiment_batch_id": {"type": "string"},
                    "experiments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "experiment_id": {"type": "string"},
                                "hypothesis": {"type": "string"},
                                "target_segment": {"type": "string"},
                                "owner": {"type": "string"},
                                "start_date": {"type": "string"},
                                "success_metric": {"type": "string"},
                            },
                            "required": ["experiment_id", "hypothesis", "target_segment", "owner", "start_date", "success_metric"],
                            "additionalProperties": False,
                        },
                    },
                    "measurement_plan": {"type": "array", "items": {"type": "string"}},
                    "stop_conditions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "experiment_batch_id", "experiments", "measurement_plan", "stop_conditions"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "plan"],
        "additionalProperties": False,
    },
)

WRITE_PREVENTION_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_churn_prevention_priority_gate",
    description="Write a churn prevention priority gate decision with go/conditional/no_go status.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /churn/gate/priority-2024-01-15"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["churn_prevention_priority_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "conditional", "no_go"]},
                    "must_fix_items": {"type": "array", "items": {"type": "string"}},
                    "deferred_items": {"type": "array", "items": {"type": "string"}},
                    "decision_owner": {"type": "string"},
                },
                "required": ["artifact_type", "version", "gate_status", "must_fix_items", "deferred_items", "decision_owner"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "gate"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_INTERVIEW_CORPUS_TOOL,
    WRITE_INTERVIEW_COVERAGE_TOOL,
    WRITE_SIGNAL_QUALITY_TOOL,
    WRITE_ROOTCAUSE_BACKLOG_TOOL,
    WRITE_FIX_EXPERIMENT_PLAN_TOOL,
    WRITE_PREVENTION_GATE_TOOL,
]


async def handle_write_interview_corpus(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        corpus = args.get("corpus")
        if not path or corpus is None:
            return "Error: path and corpus are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"churn_interview_corpus": corpus}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn interview corpus saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn interview corpus: {type(e).__name__}: {e}"


async def handle_write_interview_coverage(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        coverage = args.get("coverage")
        if not path or coverage is None:
            return "Error: path and coverage are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"churn_interview_coverage": coverage}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn interview coverage saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn interview coverage: {type(e).__name__}: {e}"


async def handle_write_signal_quality(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        quality = args.get("quality")
        if not path or quality is None:
            return "Error: path and quality are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"churn_signal_quality": quality}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn signal quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn signal quality: {type(e).__name__}: {e}"


async def handle_write_rootcause_backlog(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        backlog = args.get("backlog")
        if not path or backlog is None:
            return "Error: path and backlog are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"churn_rootcause_backlog": backlog}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn root-cause backlog saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn root-cause backlog: {type(e).__name__}: {e}"


async def handle_write_fix_experiment_plan(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        plan = args.get("plan")
        if not path or plan is None:
            return "Error: path and plan are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"churn_fix_experiment_plan": plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn fix experiment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn fix experiment plan: {type(e).__name__}: {e}"


async def handle_write_prevention_gate(
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
        doc = {"churn_prevention_priority_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChurn prevention priority gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn prevention priority gate: {type(e).__name__}: {e}"
