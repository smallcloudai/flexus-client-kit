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

PILOT_CONTRACTING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pilot_contracting_api",
    description="pilot_contracting_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PILOT_DELIVERY_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pilot_delivery_ops_api",
    description="pilot_delivery_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PILOT_USAGE_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pilot_usage_evidence_api",
    description="pilot_usage_evidence_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PILOT_STAKEHOLDER_SYNC_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pilot_stakeholder_sync_api",
    description="pilot_stakeholder_sync_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PILOT_CONTRACTING_TOOL,
    PILOT_DELIVERY_OPS_TOOL,
    PILOT_USAGE_EVIDENCE_TOOL,
    PILOT_STAKEHOLDER_SYNC_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "pilot_contracting_api": [
        "docusign.envelopes.create.v1",
        "docusign.envelopes.get.v1",
        "docusign.envelopes.list_status_changes.v1",
        "pandadoc.documents.create.v1",
        "pandadoc.documents.details.get.v1",
        "stripe.payment_links.create.v1",
        "stripe.invoices.create.v1",
        "hubspot.deals.update.v1",
    ],
    "pilot_delivery_ops_api": [
        "jira.issues.create.v1",
        "jira.issues.transition.v1",
        "asana.tasks.create.v1",
        "notion.pages.create.v1",
        "notion.pages.update.v1",
        "calendly.scheduled_events.list.v1",
        "google_calendar.events.insert.v1",
        "google_calendar.events.list.v1",
    ],
    "pilot_usage_evidence_api": [
        "posthog.insights.trend.query.v1",
        "posthog.insights.funnel.query.v1",
        "mixpanel.funnels.query.v1",
        "mixpanel.retention.query.v1",
        "ga4.properties.run_report.v1",
        "amplitude.dashboardrest.chart.get.v1",
    ],
    "pilot_stakeholder_sync_api": [
        "intercom.conversations.list.v1",
        "intercom.conversations.search.v1",
        "zendesk.tickets.search.v1",
        "zendesk.ticket_comments.list.v1",
        "google_calendar.events.list.v1",
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
# WRITE TOOLS — pilot_contracting_operator artifacts
# =============================================================================

WRITE_PILOT_CONTRACT_PACKET_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pilot_contract_packet",
    description="Write a completed pilot contract packet to a policy document. Call once all scope, terms, stakeholders and signatures are finalized.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/contract-acme-2024-01-15"},
            "pilot_contract_packet": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pilot_contract_packet"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "account_ref": {"type": "string"},
                    "scope": {"type": "array", "items": {"type": "string"}},
                    "commercial_terms": {
                        "type": "object",
                        "properties": {
                            "contract_value": {"type": "number", "minimum": 0},
                            "currency": {"type": "string"},
                            "billing_model": {"type": "string"},
                            "payment_terms": {"type": "string"},
                        },
                        "required": ["contract_value", "currency", "billing_model"],
                        "additionalProperties": False,
                    },
                    "success_criteria": {"type": "array", "items": {"type": "string"}},
                    "stakeholders": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "role": {"type": "string"},
                                "decision_authority": {"type": "string"},
                            },
                            "required": ["name", "role", "decision_authority"],
                            "additionalProperties": False,
                        },
                    },
                    "signature_status": {"type": "string", "enum": ["draft", "sent", "viewed", "completed", "declined"]},
                    "payment_commitment": {"type": "string", "enum": ["none", "pending", "confirmed"]},
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
                    "artifact_type", "version", "pilot_id", "account_ref", "scope",
                    "commercial_terms", "success_criteria", "stakeholders",
                    "signature_status", "payment_commitment", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pilot_contract_packet"],
        "additionalProperties": False,
    },
)

WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pilot_risk_clause_register",
    description="Write the risk clause register for a pilot contract. Call after reviewing all contract terms for risk exposure.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/risk-clauses-acme-2024-01-15"},
            "pilot_risk_clause_register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pilot_risk_clause_register"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "risk_clauses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "clause_id": {"type": "string"},
                                "clause_text": {"type": "string"},
                                "risk_level": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "owner": {"type": "string"},
                            },
                            "required": ["clause_id", "clause_text", "risk_level", "owner"],
                            "additionalProperties": False,
                        },
                    },
                    "high_risk_items": {"type": "array", "items": {"type": "string"}},
                    "required_mitigations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "pilot_id", "risk_clauses", "high_risk_items", "required_mitigations"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pilot_risk_clause_register"],
        "additionalProperties": False,
    },
)

WRITE_PILOT_GO_LIVE_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pilot_go_live_readiness",
    description="Write the go/no-go readiness gate for a pilot. Call when all pre-launch checks are complete.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/go-live-acme-2024-01-15"},
            "pilot_go_live_readiness": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pilot_go_live_readiness"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "required_actions": {"type": "array", "items": {"type": "string"}},
                    "target_start_date": {"type": "string"},
                },
                "required": ["artifact_type", "version", "pilot_id", "gate_status", "blocking_issues", "required_actions", "target_start_date"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pilot_go_live_readiness"],
        "additionalProperties": False,
    },
)

CONTRACTING_WRITE_TOOLS = [
    WRITE_PILOT_CONTRACT_PACKET_TOOL,
    WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL,
    WRITE_PILOT_GO_LIVE_READINESS_TOOL,
]

# =============================================================================
# WRITE TOOLS — first_value_delivery_operator artifacts
# =============================================================================

WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_first_value_delivery_plan",
    description="Write the first value delivery plan. Call once delivery steps, owners, timeline and risk controls are defined.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/delivery-plan-acme-2024-01-15"},
            "first_value_delivery_plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["first_value_delivery_plan"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "delivery_plan": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_id": {"type": "string"},
                                "step_name": {"type": "string"},
                                "expected_outcome": {"type": "string"},
                                "acceptance_check": {"type": "string"},
                            },
                            "required": ["step_id", "step_name", "expected_outcome"],
                            "additionalProperties": False,
                        },
                    },
                    "owners": {"type": "array", "items": {"type": "string"}},
                    "timeline": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "target_first_value_date": {"type": "string"},
                        },
                        "required": ["start_date", "target_first_value_date"],
                        "additionalProperties": False,
                    },
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "risk_controls": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "pilot_id", "delivery_plan", "owners", "timeline", "dependencies", "risk_controls"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "first_value_delivery_plan"],
        "additionalProperties": False,
    },
)

WRITE_FIRST_VALUE_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_first_value_evidence",
    description="Write first value evidence after delivery outcomes are confirmed by stakeholders.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/evidence-acme-2024-01-15"},
            "first_value_evidence": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["first_value_evidence"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "time_to_first_value": {"type": "string"},
                    "delivered_outcomes": {"type": "array", "items": {"type": "string"}},
                    "proof_artifacts": {"type": "array", "items": {"type": "string"}},
                    "usage_signals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "signal_name": {"type": "string"},
                                "signal_value": {"type": "number"},
                                "source_ref": {"type": "string"},
                            },
                            "required": ["signal_name", "signal_value", "source_ref"],
                            "additionalProperties": False,
                        },
                    },
                    "stakeholder_confirmation": {
                        "type": "object",
                        "properties": {
                            "confirmed": {"type": "boolean"},
                            "confirmed_by": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["confirmed", "confirmed_by"],
                        "additionalProperties": False,
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "pilot_id", "time_to_first_value",
                    "delivered_outcomes", "proof_artifacts", "usage_signals",
                    "stakeholder_confirmation", "confidence", "risk_flags", "next_steps",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "first_value_evidence"],
        "additionalProperties": False,
    },
)

WRITE_PILOT_EXPANSION_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pilot_expansion_readiness",
    description="Write the pilot expansion readiness assessment. Call after first value evidence is collected and expansion decision is due.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pilots/expansion-readiness-acme-2024-01-15"},
            "pilot_expansion_readiness": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pilot_expansion_readiness"]},
                    "version": {"type": "string"},
                    "pilot_id": {"type": "string"},
                    "readiness_status": {"type": "string", "enum": ["ready", "conditional", "not_ready"]},
                    "expansion_hypothesis": {"type": "string"},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "recommended_action": {"type": "string", "enum": ["expand", "stabilize", "stop"]},
                },
                "required": ["artifact_type", "version", "pilot_id", "readiness_status", "expansion_hypothesis", "blocking_issues", "recommended_action"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pilot_expansion_readiness"],
        "additionalProperties": False,
    },
)

DELIVERY_WRITE_TOOLS = [
    WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL,
    WRITE_FIRST_VALUE_EVIDENCE_TOOL,
    WRITE_PILOT_EXPANSION_READINESS_TOOL,
]

WRITE_TOOLS = [*CONTRACTING_WRITE_TOOLS, *DELIVERY_WRITE_TOOLS]


async def handle_write_pilot_contract_packet(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pilot_contract_packet")
        if not path or artifact is None:
            return "Error: path and pilot_contract_packet are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pilot_contract_packet": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPilot contract packet saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot contract packet: {type(e).__name__}: {e}"


async def handle_write_pilot_risk_clause_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pilot_risk_clause_register")
        if not path or artifact is None:
            return "Error: path and pilot_risk_clause_register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pilot_risk_clause_register": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPilot risk clause register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot risk clause register: {type(e).__name__}: {e}"


async def handle_write_pilot_go_live_readiness(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pilot_go_live_readiness")
        if not path or artifact is None:
            return "Error: path and pilot_go_live_readiness are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pilot_go_live_readiness": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPilot go-live readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot go-live readiness: {type(e).__name__}: {e}"


async def handle_write_first_value_delivery_plan(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("first_value_delivery_plan")
        if not path or artifact is None:
            return "Error: path and first_value_delivery_plan are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"first_value_delivery_plan": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nFirst value delivery plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing first value delivery plan: {type(e).__name__}: {e}"


async def handle_write_first_value_evidence(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("first_value_evidence")
        if not path or artifact is None:
            return "Error: path and first_value_evidence are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"first_value_evidence": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nFirst value evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing first value evidence: {type(e).__name__}: {e}"


async def handle_write_pilot_expansion_readiness(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pilot_expansion_readiness")
        if not path or artifact is None:
            return "Error: path and pilot_expansion_readiness are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pilot_expansion_readiness": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPilot expansion readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot expansion readiness: {type(e).__name__}: {e}"
