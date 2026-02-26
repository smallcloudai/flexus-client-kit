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

RETENTION_REVENUE_EVENTS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="retention_revenue_events_api",
    description='retention_revenue_events_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

RETENTION_PRODUCT_ANALYTICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="retention_product_analytics_api",
    description='retention_product_analytics_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

RETENTION_FEEDBACK_RESEARCH_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="retention_feedback_research_api",
    description='retention_feedback_research_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

RETENTION_ACCOUNT_CONTEXT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="retention_account_context_api",
    description='retention_account_context_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    RETENTION_REVENUE_EVENTS_TOOL,
    RETENTION_PRODUCT_ANALYTICS_TOOL,
    RETENTION_FEEDBACK_RESEARCH_TOOL,
    RETENTION_ACCOUNT_CONTEXT_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "retention_revenue_events_api": [
        "stripe.subscriptions.list.v1",
        "stripe.invoices.list.v1",
        "chargebee.subscriptions.list.v1",
        "chargebee.invoices.list.v1",
        "recurly.subscriptions.list.v1",
        "paddle.subscriptions.list.v1",
    ],
    "retention_product_analytics_api": [
        "posthog.insights.retention.query.v1",
        "posthog.insights.funnel.query.v1",
        "mixpanel.retention.query.v1",
        "mixpanel.funnels.query.v1",
        "ga4.properties.run_report.v1",
        "amplitude.dashboardrest.chart.get.v1",
    ],
    "retention_feedback_research_api": [
        "surveymonkey.responses.list.v1",
        "typeform.responses.list.v1",
        "delighted.metrics.get.v1",
        "intercom.conversations.search.v1",
        "zendesk.tickets.search.v1",
    ],
    "retention_account_context_api": [
        "hubspot.deals.search.v1",
        "hubspot.companies.search.v1",
        "pipedrive.deals.search.v1",
        "intercom.conversations.search.v1",
        "zendesk.tickets.search.v1",
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


async def handle_retention_tool_call(
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
# WRITE TOOLS — structured artifact output, schema enforced by strict=True
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

WRITE_COHORT_REVENUE_REVIEW_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_cohort_revenue_review",
    description="Write a cohort revenue review artifact after completing activation-retention-revenue diagnostics.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /retention/cohort-review-2024-01-15"},
            "review": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["cohort_revenue_review"]},
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
                    "retention_cohorts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cohort_id": {"type": "string"},
                                "period": {"type": "string"},
                                "retention_rate": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["cohort_id", "period", "retention_rate"],
                            "additionalProperties": False,
                        },
                    },
                    "revenue_movement": {
                        "type": "object",
                        "properties": {
                            "new_mrr": {"type": "number"},
                            "expansion_mrr": {"type": "number"},
                            "contraction_mrr": {"type": "number"},
                            "churn_mrr": {"type": "number"},
                            "net_mrr": {"type": "number"},
                        },
                        "required": ["new_mrr", "expansion_mrr", "contraction_mrr", "churn_mrr", "net_mrr"],
                        "additionalProperties": False,
                    },
                    "expansion_vs_churn": {
                        "type": "object",
                        "properties": {
                            "expansion_ratio": {"type": "number", "minimum": 0},
                            "churn_ratio": {"type": "number", "minimum": 0},
                        },
                        "required": ["expansion_ratio", "churn_ratio"],
                        "additionalProperties": False,
                    },
                    "risk_accounts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_ref": {"type": "string"},
                                "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "risk_reason": {"type": "string"},
                            },
                            "required": ["account_ref", "risk_level", "risk_reason"],
                            "additionalProperties": False,
                        },
                    },
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": [
                    "artifact_type", "version", "analysis_window", "segment_filters",
                    "retention_cohorts", "revenue_movement", "expansion_vs_churn",
                    "risk_accounts", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "review"],
        "additionalProperties": False,
    },
)

WRITE_RETENTION_DRIVER_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_retention_driver_matrix",
    description="Write a retention driver matrix artifact ranking activation, engagement, and commercial drivers by impact.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /retention/driver-matrix-2024-01-15"},
            "driver_matrix": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["retention_driver_matrix"]},
                    "version": {"type": "string"},
                    "driver_matrix": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "driver_id": {"type": "string"},
                                "driver_type": {"type": "string", "enum": ["activation", "engagement", "value_realization", "support_friction", "commercial"]},
                                "impact_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "evidence_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["driver_id", "driver_type", "impact_score", "evidence_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "priority_actions": {"type": "array", "items": {"type": "string"}},
                    "confidence_notes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "driver_matrix", "priority_actions", "confidence_notes"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "driver_matrix"],
        "additionalProperties": False,
    },
)

WRITE_RETENTION_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_retention_readiness_gate",
    description="Write a retention readiness gate artifact with go/conditional/no_go decision and blocking issues.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /retention/readiness-gate-2024-01-15"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["retention_readiness_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "conditional", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "required_actions": {"type": "array", "items": {"type": "string"}},
                    "decision_owner": {"type": "string"},
                },
                "required": ["artifact_type", "version", "gate_status", "blocking_issues", "required_actions", "decision_owner"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "gate"],
        "additionalProperties": False,
    },
)

WRITE_PMF_CONFIDENCE_SCORECARD_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pmf_confidence_scorecard",
    description="Write a PMF confidence scorecard artifact after interpreting survey and behavioral evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pmf/scorecard-2024-01-15"},
            "scorecard": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pmf_confidence_scorecard"]},
                    "version": {"type": "string"},
                    "measurement_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "target_segment": {"type": "string"},
                    "survey_quality": {
                        "type": "object",
                        "properties": {
                            "sample_size": {"type": "number", "minimum": 0},
                            "response_rate": {"type": "number", "minimum": 0, "maximum": 1},
                            "coverage_notes": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["sample_size", "response_rate", "coverage_notes"],
                        "additionalProperties": False,
                    },
                    "pmf_core_metric": {
                        "type": "object",
                        "properties": {
                            "metric_name": {"type": "string"},
                            "metric_value": {"type": "number", "minimum": 0, "maximum": 1},
                            "threshold": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["metric_name", "metric_value", "threshold"],
                        "additionalProperties": False,
                    },
                    "behavioral_corroboration": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "signal_name": {"type": "string"},
                                "signal_direction": {"type": "string", "enum": ["positive", "neutral", "negative"]},
                                "source_ref": {"type": "string"},
                            },
                            "required": ["signal_name", "signal_direction", "source_ref"],
                            "additionalProperties": False,
                        },
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "recommendation": {"type": "string", "enum": ["increase_investment", "targeted_fix", "hold", "pivot"]},
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": [
                    "artifact_type", "version", "measurement_window", "target_segment",
                    "survey_quality", "pmf_core_metric", "behavioral_corroboration",
                    "confidence", "recommendation", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "scorecard"],
        "additionalProperties": False,
    },
)

WRITE_PMF_SIGNAL_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pmf_signal_evidence",
    description="Write a PMF signal evidence artifact cataloguing positive and negative signals with evidence gaps.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pmf/signal-evidence-2024-01-15"},
            "evidence": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pmf_signal_evidence"]},
                    "version": {"type": "string"},
                    "signals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "signal_id": {"type": "string"},
                                "signal_type": {"type": "string", "enum": ["survey", "usage", "commercial", "support"]},
                                "strength": {"type": "number", "minimum": 0, "maximum": 1},
                                "evidence_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["signal_id", "signal_type", "strength", "evidence_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "negative_signals": {"type": "array", "items": {"type": "string"}},
                    "evidence_gaps": {"type": "array", "items": {"type": "string"}},
                    "next_research_actions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "signals", "negative_signals", "evidence_gaps", "next_research_actions"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "evidence"],
        "additionalProperties": False,
    },
)

WRITE_PMF_RESEARCH_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pmf_research_backlog",
    description="Write a PMF research backlog artifact with prioritized hypotheses and owner assignments.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pmf/research-backlog-2024-01-15"},
            "backlog": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pmf_research_backlog"]},
                    "version": {"type": "string"},
                    "backlog_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "hypothesis": {"type": "string"},
                                "required_evidence": {"type": "array", "items": {"type": "string"}},
                                "priority": {"type": "string", "enum": ["p0", "p1", "p2"]},
                            },
                            "required": ["item_id", "hypothesis", "required_evidence", "priority"],
                            "additionalProperties": False,
                        },
                    },
                    "priority_order": {"type": "array", "items": {"type": "string"}},
                    "owner_map": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "owner": {"type": "string"},
                            },
                            "required": ["item_id", "owner"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["artifact_type", "version", "backlog_items", "priority_order", "owner_map"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "backlog"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_COHORT_REVENUE_REVIEW_TOOL,
    WRITE_RETENTION_DRIVER_MATRIX_TOOL,
    WRITE_RETENTION_READINESS_GATE_TOOL,
    WRITE_PMF_CONFIDENCE_SCORECARD_TOOL,
    WRITE_PMF_SIGNAL_EVIDENCE_TOOL,
    WRITE_PMF_RESEARCH_BACKLOG_TOOL,
]


async def handle_write_cohort_revenue_review(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        review = args.get("review")
        if not path or review is None:
            return "Error: path and review are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"cohort_revenue_review": review}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nCohort revenue review saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing cohort revenue review: {type(e).__name__}: {e}"


async def handle_write_retention_driver_matrix(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        driver_matrix = args.get("driver_matrix")
        if not path or driver_matrix is None:
            return "Error: path and driver_matrix are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"retention_driver_matrix": driver_matrix}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRetention driver matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing retention driver matrix: {type(e).__name__}: {e}"


async def handle_write_retention_readiness_gate(
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
        doc = {"retention_readiness_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRetention readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing retention readiness gate: {type(e).__name__}: {e}"


async def handle_write_pmf_confidence_scorecard(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        scorecard = args.get("scorecard")
        if not path or scorecard is None:
            return "Error: path and scorecard are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pmf_confidence_scorecard": scorecard}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPMF confidence scorecard saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF confidence scorecard: {type(e).__name__}: {e}"


async def handle_write_pmf_signal_evidence(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        evidence = args.get("evidence")
        if not path or evidence is None:
            return "Error: path and evidence are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pmf_signal_evidence": evidence}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPMF signal evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF signal evidence: {type(e).__name__}: {e}"


async def handle_write_pmf_research_backlog(
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
        doc = {"pmf_research_backlog": backlog}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPMF research backlog saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF research backlog: {type(e).__name__}: {e}"
