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

PARTNER_PROGRAM_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="partner_program_ops_api",
    description='partner_program_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PARTNER_ACCOUNT_MAPPING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="partner_account_mapping_api",
    description='partner_account_mapping_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PARTNER_ENABLEMENT_EXECUTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="partner_enablement_execution_api",
    description='partner_enablement_execution_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

CHANNEL_CONFLICT_GOVERNANCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="channel_conflict_governance_api",
    description='channel_conflict_governance_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PARTNER_PROGRAM_OPS_TOOL,
    PARTNER_ACCOUNT_MAPPING_TOOL,
    PARTNER_ENABLEMENT_EXECUTION_TOOL,
    CHANNEL_CONFLICT_GOVERNANCE_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "partner_program_ops_api": [
        "partnerstack.partnerships.list.v1",
        "partnerstack.partners.list.v1",
        "partnerstack.transactions.list.v1",
        "partnerstack.transactions.create.v1",
        "partnerstack.payouts.list.v1",
    ],
    "partner_account_mapping_api": [
        "crossbeam.partners.list.v1",
        "crossbeam.account_mapping.overlaps.list.v1",
        "crossbeam.exports.records.get.v1",
        "salesforce.query.account.v1",
        # HubSpot -> use MCP preset instead (mcp_presets/hubspot.json)
    ],
    "partner_enablement_execution_api": [
        # Asana -> use MCP preset instead (mcp_presets/asana.json)
        # Notion -> use MCP preset instead (mcp_presets/notion.json)
    ],
    "channel_conflict_governance_api": [
        "salesforce.query.opportunity.v1",
        "pipedrive.deals.search.v1",
        # Atlassian Jira -> use MCP preset instead (mcp_presets/atlassian.json)
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
# WRITE TOOLS — structured artifact output, schema enforced by strict=True
# =============================================================================

_SOURCES_SCHEMA = {
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
}

WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_partner_activation_scorecard",
    description="Write a completed partner activation scorecard artifact. Call once per activation cycle after gathering all funnel evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /partners/activation-scorecard-2024-01-15"},
            "scorecard": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["partner_activation_scorecard"]},
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
                    "partner_batches": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "batch_id": {"type": "string"},
                                "partner_count": {"type": "number", "minimum": 0},
                                "tier": {"type": "string"},
                            },
                            "required": ["batch_id", "partner_count", "tier"],
                            "additionalProperties": False,
                        },
                    },
                    "activation_funnel": {
                        "type": "object",
                        "properties": {
                            "recruited": {"type": "number", "minimum": 0},
                            "onboarded": {"type": "number", "minimum": 0},
                            "enabled": {"type": "number", "minimum": 0},
                            "activated": {"type": "number", "minimum": 0},
                        },
                        "required": ["recruited", "onboarded", "enabled", "activated"],
                        "additionalProperties": False,
                    },
                    "enablement_coverage": {"type": "number", "minimum": 0, "maximum": 1},
                    "pipeline_contribution": {
                        "type": "object",
                        "properties": {
                            "sourced_pipeline": {"type": "number", "minimum": 0},
                            "influenced_pipeline": {"type": "number", "minimum": 0},
                        },
                        "required": ["sourced_pipeline", "influenced_pipeline"],
                        "additionalProperties": False,
                    },
                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                    "sources": _SOURCES_SCHEMA,
                },
                "required": [
                    "artifact_type", "version", "analysis_window", "partner_batches",
                    "activation_funnel", "enablement_coverage", "pipeline_contribution",
                    "risk_flags", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "scorecard"],
        "additionalProperties": False,
    },
)

WRITE_PARTNER_ENABLEMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_partner_enablement_plan",
    description="Write a partner enablement plan artifact with tracks, owners, and completion criteria.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /partners/enablement-plan-2024-01-15"},
            "plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["partner_enablement_plan"]},
                    "version": {"type": "string"},
                    "program_id": {"type": "string"},
                    "enablement_tracks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "track_id": {"type": "string"},
                                "track_name": {"type": "string"},
                                "target_tier": {"type": "string"},
                            },
                            "required": ["track_id", "track_name", "target_tier"],
                            "additionalProperties": False,
                        },
                    },
                    "owners": {"type": "array", "items": {"type": "string"}},
                    "timeline": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "target_activation_date": {"type": "string"},
                        },
                        "required": ["start_date", "target_activation_date"],
                        "additionalProperties": False,
                    },
                    "completion_criteria": {"type": "array", "items": {"type": "string"}},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "program_id", "enablement_tracks",
                    "owners", "timeline", "completion_criteria", "dependencies",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "plan"],
        "additionalProperties": False,
    },
)

WRITE_PARTNER_PIPELINE_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_partner_pipeline_quality",
    description="Write a partner pipeline quality artifact with stage conversion and SLA breach records.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /partners/pipeline-quality-2024-01-15"},
            "quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["partner_pipeline_quality"]},
                    "version": {"type": "string"},
                    "pipeline_snapshot": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "partner_ref": {"type": "string"},
                                "open_deals": {"type": "number", "minimum": 0},
                                "pipeline_value": {"type": "number", "minimum": 0},
                            },
                            "required": ["partner_ref", "open_deals", "pipeline_value"],
                            "additionalProperties": False,
                        },
                    },
                    "stage_conversion": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "stage": {"type": "string"},
                                "conversion_rate": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["stage", "conversion_rate"],
                            "additionalProperties": False,
                        },
                    },
                    "sla_breaches": {"type": "array", "items": {"type": "string"}},
                    "recommended_actions": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "pipeline_snapshot",
                    "stage_conversion", "sla_breaches", "recommended_actions",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "quality"],
        "additionalProperties": False,
    },
)

WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_channel_conflict_incident",
    description="Write a channel conflict incident artifact with incident records, resolution log, and policy updates.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /conflicts/incident-2024-01-15"},
            "incident": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["channel_conflict_incident"]},
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
                    "incidents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "incident_id": {"type": "string"},
                                "deal_ref": {"type": "string"},
                                "accounts_involved": {"type": "array", "items": {"type": "string"}},
                                "conflict_type": {"type": "string", "enum": ["ownership_overlap", "registration_collision", "pricing_conflict", "territory_conflict"]},
                                "opened_at": {"type": "string"},
                                "resolution_state": {"type": "string", "enum": ["open", "in_review", "resolved", "escalated"]},
                                "owner": {"type": "string"},
                            },
                            "required": ["incident_id", "deal_ref", "accounts_involved", "conflict_type", "opened_at", "resolution_state", "owner"],
                            "additionalProperties": False,
                        },
                    },
                    "resolution_log": {"type": "array", "items": {"type": "string"}},
                    "policy_updates": {"type": "array", "items": {"type": "string"}},
                    "sources": _SOURCES_SCHEMA,
                },
                "required": [
                    "artifact_type", "version", "analysis_window", "incidents",
                    "resolution_log", "policy_updates", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "incident"],
        "additionalProperties": False,
    },
)

WRITE_DEAL_REGISTRATION_POLICY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_deal_registration_policy",
    description="Write a deal registration policy artifact with rules, approval flow, exception policy, and SLA targets.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /conflicts/deal-registration-policy"},
            "policy": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["deal_registration_policy"]},
                    "version": {"type": "string"},
                    "registration_rules": {"type": "array", "items": {"type": "string"}},
                    "approval_flow": {"type": "array", "items": {"type": "string"}},
                    "exception_policy": {"type": "array", "items": {"type": "string"}},
                    "sla_targets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "stage": {"type": "string"},
                                "target_hours": {"type": "number", "minimum": 0},
                            },
                            "required": ["stage", "target_hours"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "artifact_type", "version", "registration_rules",
                    "approval_flow", "exception_policy", "sla_targets",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "policy"],
        "additionalProperties": False,
    },
)

WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_conflict_resolution_audit",
    description="Write a conflict resolution audit artifact with resolved cases, SLA compliance, and required remediations.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /conflicts/resolution-audit-2024-01-15"},
            "audit": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["conflict_resolution_audit"]},
                    "version": {"type": "string"},
                    "audit_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "resolved_cases": {"type": "array", "items": {"type": "string"}},
                    "sla_compliance": {"type": "number", "minimum": 0, "maximum": 1},
                    "repeat_conflict_patterns": {"type": "array", "items": {"type": "string"}},
                    "required_remediations": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "audit_window", "resolved_cases",
                    "sla_compliance", "repeat_conflict_patterns", "required_remediations",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "audit"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL,
    WRITE_PARTNER_ENABLEMENT_PLAN_TOOL,
    WRITE_PARTNER_PIPELINE_QUALITY_TOOL,
    WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL,
    WRITE_DEAL_REGISTRATION_POLICY_TOOL,
    WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL,
]


async def handle_write_partner_activation_scorecard(
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
        doc = {"partner_activation_scorecard": scorecard}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPartner activation scorecard saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner activation scorecard: {type(e).__name__}: {e}"


async def handle_write_partner_enablement_plan(
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
        doc = {"partner_enablement_plan": plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPartner enablement plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner enablement plan: {type(e).__name__}: {e}"


async def handle_write_partner_pipeline_quality(
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
        doc = {"partner_pipeline_quality": quality}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPartner pipeline quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner pipeline quality: {type(e).__name__}: {e}"


async def handle_write_channel_conflict_incident(
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
        doc = {"channel_conflict_incident": incident}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nChannel conflict incident saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing channel conflict incident: {type(e).__name__}: {e}"


async def handle_write_deal_registration_policy(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        policy = args.get("policy")
        if not path or policy is None:
            return "Error: path and policy are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"deal_registration_policy": policy}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nDeal registration policy saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing deal registration policy: {type(e).__name__}: {e}"


async def handle_write_conflict_resolution_audit(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        audit = args.get("audit")
        if not path or audit is None:
            return "Error: path and audit are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"conflict_resolution_audit": audit}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nConflict resolution audit saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing conflict resolution audit: {type(e).__name__}: {e}"
