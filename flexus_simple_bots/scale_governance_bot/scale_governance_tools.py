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

PLAYBOOK_REPO_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="playbook_repo_api",
    description="playbook_repo_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SCALE_GUARDRAIL_MONITORING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="scale_guardrail_monitoring_api",
    description="scale_guardrail_monitoring_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SCALE_CHANGE_EXECUTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="scale_change_execution_api",
    description="scale_change_execution_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SCALE_INCIDENT_RESPONSE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="scale_incident_response_api",
    description="scale_incident_response_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PLAYBOOK_REPO_TOOL,
    SCALE_GUARDRAIL_MONITORING_TOOL,
    SCALE_CHANGE_EXECUTION_TOOL,
    SCALE_INCIDENT_RESPONSE_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "playbook_repo_api": [
        # Notion -> use MCP preset instead (mcp_presets/notion.json)
        # Atlassian Confluence -> use MCP preset instead (mcp_presets/atlassian.json)
        "gdrive.files.export.v1",
    ],
    "scale_guardrail_monitoring_api": [
        "datadog.metrics.query.v1",
        "grafana.alerts.list.v1",
    ],
    "scale_change_execution_api": [
        # Asana -> use MCP preset instead (mcp_presets/asana.json)
        # Linear -> use MCP preset instead (mcp_presets/linear.json)
    ],
    "scale_incident_response_api": [
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
# WRITE TOOLS — playbook_codifier write artifacts
# =============================================================================

WRITE_PLAYBOOK_LIBRARY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_playbook_library",
    description="Write a versioned playbook library artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/playbooks-2024-01-15"},
            "library": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["playbook_library"]},
                    "version": {"type": "string"},
                    "playbooks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "playbook_id": {"type": "string"},
                                "scope": {"type": "string"},
                                "trigger_conditions": {"type": "array", "items": {"type": "string"}},
                                "steps": {"type": "array", "items": {"type": "string"}},
                                "owner": {"type": "string"},
                                "version": {"type": "string"},
                                "status": {"type": "string", "enum": ["draft", "active", "deprecated"]},
                                "guardrails": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["playbook_id", "scope", "trigger_conditions", "steps", "owner", "version", "status", "guardrails"],
                            "additionalProperties": False,
                        },
                    },
                    "owners": {"type": "array", "items": {"type": "string"}},
                    "last_validation_cycle": {"type": "string"},
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
                "required": ["artifact_type", "version", "playbooks", "owners", "last_validation_cycle", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "library"],
        "additionalProperties": False,
    },
)

WRITE_PLAYBOOK_CHANGE_LOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_playbook_change_log",
    description="Write an auditable playbook change log artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/changelog-2024-01-15"},
            "change_log": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["playbook_change_log"]},
                    "version": {"type": "string"},
                    "change_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "playbook_id": {"type": "string"},
                                "change_type": {"type": "string", "enum": ["add", "update", "deprecate"]},
                                "changed_by": {"type": "string"},
                                "change_reason": {"type": "string"},
                            },
                            "required": ["playbook_id", "change_type", "changed_by", "change_reason"],
                            "additionalProperties": False,
                        },
                    },
                    "approval_log": {"type": "array", "items": {"type": "string"}},
                    "rollback_notes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "change_window", "changes", "approval_log", "rollback_notes"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "change_log"],
        "additionalProperties": False,
    },
)

WRITE_OPERATING_SOP_COMPLIANCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_operating_sop_compliance",
    description="Write an SOP compliance report artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/sop-compliance-2024-01-15"},
            "compliance": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["operating_sop_compliance"]},
                    "version": {"type": "string"},
                    "compliance_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "required_processes": {"type": "array", "items": {"type": "string"}},
                    "compliance_rate": {"type": "number", "minimum": 0, "maximum": 1},
                    "violations": {"type": "array", "items": {"type": "string"}},
                    "remediations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "compliance_window", "required_processes", "compliance_rate", "violations", "remediations"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "compliance"],
        "additionalProperties": False,
    },
)

# =============================================================================
# WRITE TOOLS — scale_guardrail_controller write artifacts
# =============================================================================

WRITE_SCALE_INCREMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_scale_increment_plan",
    description="Write a guardrail-controlled scale increment plan artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/increment-plan-2024-01-15"},
            "plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["scale_increment_plan"]},
                    "version": {"type": "string"},
                    "increment_id": {"type": "string"},
                    "analysis_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "capacity_delta": {
                        "type": "object",
                        "properties": {
                            "current_capacity": {"type": "number", "minimum": 0},
                            "target_capacity": {"type": "number", "minimum": 0},
                        },
                        "required": ["current_capacity", "target_capacity"],
                        "additionalProperties": False,
                    },
                    "guardrails": {"type": "array", "items": {"type": "string"}},
                    "verification_steps": {"type": "array", "items": {"type": "string"}},
                    "rollback_triggers": {"type": "array", "items": {"type": "string"}},
                    "owner": {"type": "string"},
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
                "required": ["artifact_type", "version", "increment_id", "analysis_window", "capacity_delta", "guardrails", "verification_steps", "rollback_triggers", "owner", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "plan"],
        "additionalProperties": False,
    },
)

WRITE_SCALE_ROLLBACK_DECISION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_scale_rollback_decision",
    description="Write a scale rollback decision record artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/rollback-decision-2024-01-15"},
            "decision": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["scale_rollback_decision"]},
                    "version": {"type": "string"},
                    "increment_id": {"type": "string"},
                    "decision": {"type": "string", "enum": ["continue", "pause", "rollback"]},
                    "decision_time": {"type": "string"},
                    "triggering_guardrails": {"type": "array", "items": {"type": "string"}},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "owner": {"type": "string"},
                    "actions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "increment_id", "decision", "decision_time", "triggering_guardrails", "evidence", "owner", "actions"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "decision"],
        "additionalProperties": False,
    },
)

WRITE_GUARDRAIL_BREACH_INCIDENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_guardrail_breach_incident",
    description="Write a guardrail breach incident record artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /governance/incident-2024-01-15"},
            "incident": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["guardrail_breach_incident"]},
                    "version": {"type": "string"},
                    "incident_id": {"type": "string"},
                    "opened_at": {"type": "string"},
                    "breached_guardrails": {"type": "array", "items": {"type": "string"}},
                    "impact_assessment": {"type": "array", "items": {"type": "string"}},
                    "containment_actions": {"type": "array", "items": {"type": "string"}},
                    "resolution_state": {"type": "string", "enum": ["open", "mitigated", "resolved", "postmortem_required"]},
                    "resolver": {"type": "string"},
                },
                "required": ["artifact_type", "version", "incident_id", "opened_at", "breached_guardrails", "impact_assessment", "containment_actions", "resolution_state", "resolver"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "incident"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_PLAYBOOK = [
    WRITE_PLAYBOOK_LIBRARY_TOOL,
    WRITE_PLAYBOOK_CHANGE_LOG_TOOL,
    WRITE_OPERATING_SOP_COMPLIANCE_TOOL,
]

WRITE_TOOLS_CONTROLLER = [
    WRITE_SCALE_INCREMENT_PLAN_TOOL,
    WRITE_SCALE_ROLLBACK_DECISION_TOOL,
    WRITE_GUARDRAIL_BREACH_INCIDENT_TOOL,
]

WRITE_TOOLS = WRITE_TOOLS_PLAYBOOK + WRITE_TOOLS_CONTROLLER


async def handle_write_playbook_library(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        library = args.get("library")
        if not path or library is None:
            return "Error: path and library are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"playbook_library": library}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPlaybook library saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing playbook library: {type(e).__name__}: {e}"


async def handle_write_playbook_change_log(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        change_log = args.get("change_log")
        if not path or change_log is None:
            return "Error: path and change_log are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"playbook_change_log": change_log}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPlaybook change log saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing playbook change log: {type(e).__name__}: {e}"


async def handle_write_operating_sop_compliance(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        compliance = args.get("compliance")
        if not path or compliance is None:
            return "Error: path and compliance are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"operating_sop_compliance": compliance}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nOperating SOP compliance saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing operating SOP compliance: {type(e).__name__}: {e}"


async def handle_write_scale_increment_plan(
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
        doc = {"scale_increment_plan": plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nScale increment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing scale increment plan: {type(e).__name__}: {e}"


async def handle_write_scale_rollback_decision(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        decision = args.get("decision")
        if not path or decision is None:
            return "Error: path and decision are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"scale_rollback_decision": decision}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nScale rollback decision saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing scale rollback decision: {type(e).__name__}: {e}"


async def handle_write_guardrail_breach_incident(
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
        doc = {"guardrail_breach_incident": incident}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nGuardrail breach incident saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing guardrail breach incident: {type(e).__name__}: {e}"
