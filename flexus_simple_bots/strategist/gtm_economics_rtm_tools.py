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

GTM_UNIT_ECONOMICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="gtm_unit_economics_api",
    description="gtm_unit_economics_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

GTM_MEDIA_EFFICIENCY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="gtm_media_efficiency_api",
    description="gtm_media_efficiency_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

RTM_PIPELINE_FINANCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="rtm_pipeline_finance_api",
    description="rtm_pipeline_finance_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

RTM_TERRITORY_POLICY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="rtm_territory_policy_api",
    description="rtm_territory_policy_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    GTM_UNIT_ECONOMICS_TOOL,
    GTM_MEDIA_EFFICIENCY_TOOL,
    RTM_PIPELINE_FINANCE_TOOL,
    RTM_TERRITORY_POLICY_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "gtm_unit_economics_api": [
        # Stripe -> use MCP preset instead (mcp_presets/stripe.json)
        "chargebee.invoices.list.v1",
        "chargebee.subscriptions.list.v1",
        "recurly.subscriptions.list.v1",
    ],
    "gtm_media_efficiency_api": [
        "meta.insights.query.v1",
        "google_ads.googleads.search_stream.v1",
        "linkedin.ad_analytics.query.v1",
    ],
    "rtm_pipeline_finance_api": [
        # HubSpot -> use MCP preset instead (mcp_presets/hubspot.json)
        "salesforce.query.opportunity.v1",
        "salesforce.query.account.v1",
        "pipedrive.deals.search.v1",
        "pipedrive.deals.list.v1",
    ],
    "rtm_territory_policy_api": [
        "salesforce.query.opportunity.v1",
        "salesforce.query.user.v1",
        # Notion -> use MCP preset instead (mcp_presets/notion.json)
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
# WRITE TOOLS — unit_economics_modeler artifacts
# =============================================================================

WRITE_UNIT_ECONOMICS_REVIEW_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_unit_economics_review",
    description="Write a completed unit economics review artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /economics/unit-review-2024-01-15"},
            "review": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["unit_economics_review"]},
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
                    "segments": {"type": "array", "items": {"type": "string"}},
                    "unit_economics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment": {"type": "string"},
                                "cac": {"type": "number", "minimum": 0},
                                "ltv": {"type": "number", "minimum": 0},
                                "ltv_cac_ratio": {"type": "number", "minimum": 0},
                            },
                            "required": ["segment", "cac", "ltv", "ltv_cac_ratio"],
                            "additionalProperties": False,
                        },
                    },
                    "payback_profile": {
                        "type": "object",
                        "properties": {
                            "median_months": {"type": "number", "minimum": 0},
                            "p75_months": {"type": "number", "minimum": 0},
                        },
                        "required": ["median_months", "p75_months"],
                        "additionalProperties": False,
                    },
                    "margin_profile": {
                        "type": "object",
                        "properties": {
                            "gross_margin": {"type": "number"},
                            "contribution_margin": {"type": "number"},
                        },
                        "required": ["gross_margin", "contribution_margin"],
                        "additionalProperties": False,
                    },
                    "readiness_state": {"type": "string", "enum": ["ready", "conditional", "not_ready"]},
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
                "required": ["artifact_type", "version", "analysis_window", "segments", "unit_economics", "payback_profile", "margin_profile", "readiness_state", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "review"],
        "additionalProperties": False,
    },
)

WRITE_CHANNEL_MARGIN_STACK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_channel_margin_stack",
    description="Write a channel margin stack artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /economics/margin-stack-2024-01-15"},
            "stack": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["channel_margin_stack"]},
                    "version": {"type": "string"},
                    "channels": {"type": "array", "items": {"type": "string"}},
                    "cost_layers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "layer_name": {"type": "string"},
                                "cost_value": {"type": "number"},
                            },
                            "required": ["layer_name", "cost_value"],
                            "additionalProperties": False,
                        },
                    },
                    "margin_waterfall": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step": {"type": "string"},
                                "value": {"type": "number"},
                            },
                            "required": ["step", "value"],
                            "additionalProperties": False,
                        },
                    },
                    "alerts": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "channels", "cost_layers", "margin_waterfall", "alerts"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "stack"],
        "additionalProperties": False,
    },
)

WRITE_PAYBACK_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_payback_readiness_gate",
    description="Write a payback readiness gate decision to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /economics/readiness-gate-2024-01-15"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["payback_readiness_gate"]},
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

# =============================================================================
# WRITE TOOLS — rtm_rules_architect artifacts
# =============================================================================

WRITE_RTM_RULES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_rtm_rules",
    description="Write RTM ownership and engagement rules artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /rtm/rules-2024-01-15"},
            "rules": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["rtm_rules"]},
                    "version": {"type": "string"},
                    "target_segments": {"type": "array", "items": {"type": "string"}},
                    "channel_roles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "channel": {"type": "string"},
                                "owner_role": {"type": "string"},
                                "scope": {"type": "string"},
                            },
                            "required": ["channel", "owner_role", "scope"],
                            "additionalProperties": False,
                        },
                    },
                    "ownership_rules": {"type": "array", "items": {"type": "string"}},
                    "deal_registration_rules": {"type": "array", "items": {"type": "string"}},
                    "conflict_resolution_sla": {"type": "string"},
                    "exceptions_policy": {"type": "array", "items": {"type": "string"}},
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
                "required": ["artifact_type", "version", "target_segments", "channel_roles", "ownership_rules", "deal_registration_rules", "conflict_resolution_sla", "exceptions_policy", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "rules"],
        "additionalProperties": False,
    },
)

WRITE_DEAL_OWNERSHIP_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_deal_ownership_matrix",
    description="Write a deal ownership matrix artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /rtm/ownership-matrix-2024-01-15"},
            "matrix": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["deal_ownership_matrix"]},
                    "version": {"type": "string"},
                    "matrix_rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment": {"type": "string"},
                                "territory": {"type": "string"},
                                "owner_team": {"type": "string"},
                                "fallback_owner": {"type": "string"},
                            },
                            "required": ["segment", "territory", "owner_team", "fallback_owner"],
                            "additionalProperties": False,
                        },
                    },
                    "unassigned_cases": {"type": "array", "items": {"type": "string"}},
                    "escalation_path": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "matrix_rows", "unassigned_cases", "escalation_path"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "matrix"],
        "additionalProperties": False,
    },
)

WRITE_RTM_CONFLICT_PLAYBOOK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_rtm_conflict_resolution_playbook",
    description="Write an RTM conflict resolution playbook artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /rtm/conflict-playbook-2024-01-15"},
            "playbook": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["rtm_conflict_resolution_playbook"]},
                    "version": {"type": "string"},
                    "incident_types": {"type": "array", "items": {"type": "string"}},
                    "decision_rules": {"type": "array", "items": {"type": "string"}},
                    "sla_targets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "incident_type": {"type": "string"},
                                "target_hours": {"type": "number", "minimum": 0},
                            },
                            "required": ["incident_type", "target_hours"],
                            "additionalProperties": False,
                        },
                    },
                    "audit_requirements": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "incident_types", "decision_rules", "sla_targets", "audit_requirements"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "playbook"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_ECONOMICS = [
    WRITE_UNIT_ECONOMICS_REVIEW_TOOL,
    WRITE_CHANNEL_MARGIN_STACK_TOOL,
    WRITE_PAYBACK_READINESS_GATE_TOOL,
]

WRITE_TOOLS_RTM = [
    WRITE_RTM_RULES_TOOL,
    WRITE_DEAL_OWNERSHIP_MATRIX_TOOL,
    WRITE_RTM_CONFLICT_PLAYBOOK_TOOL,
]

WRITE_TOOLS = [
    *WRITE_TOOLS_ECONOMICS,
    *WRITE_TOOLS_RTM,
]


async def handle_write_unit_economics_review(
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
        doc = {"unit_economics_review": review}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nUnit economics review saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing unit economics review: {type(e).__name__}: {e}"


async def handle_write_channel_margin_stack(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        stack = args.get("stack")
        if not path or stack is None:
            return "Error: path and stack are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"channel_margin_stack": stack}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChannel margin stack saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing channel margin stack: {type(e).__name__}: {e}"


async def handle_write_payback_readiness_gate(
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
        doc = {"payback_readiness_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPayback readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing payback readiness gate: {type(e).__name__}: {e}"


async def handle_write_rtm_rules(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        rules = args.get("rules")
        if not path or rules is None:
            return "Error: path and rules are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"rtm_rules": rules}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRTM rules saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing RTM rules: {type(e).__name__}: {e}"


async def handle_write_deal_ownership_matrix(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        matrix = args.get("matrix")
        if not path or matrix is None:
            return "Error: path and matrix are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"deal_ownership_matrix": matrix}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nDeal ownership matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing deal ownership matrix: {type(e).__name__}: {e}"


async def handle_write_rtm_conflict_playbook(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        playbook = args.get("playbook")
        if not path or playbook is None:
            return "Error: path and playbook are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"rtm_conflict_resolution_playbook": playbook}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRTM conflict resolution playbook saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing RTM conflict resolution playbook: {type(e).__name__}: {e}"
