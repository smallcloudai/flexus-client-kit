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

PIPELINE_CRM_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pipeline_crm_api",
    description='pipeline_crm_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PIPELINE_PROSPECTING_ENRICHMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pipeline_prospecting_enrichment_api",
    description='pipeline_prospecting_enrichment_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PIPELINE_OUTREACH_EXECUTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pipeline_outreach_execution_api",
    description='pipeline_outreach_execution_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PIPELINE_ENGAGEMENT_SIGNAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pipeline_engagement_signal_api",
    description='pipeline_engagement_signal_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PIPELINE_CRM_TOOL,
    PIPELINE_PROSPECTING_ENRICHMENT_TOOL,
    PIPELINE_OUTREACH_EXECUTION_TOOL,
    PIPELINE_ENGAGEMENT_SIGNAL_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "pipeline_crm_api": [
        "hubspot.contacts.search.v1",
        "hubspot.companies.search.v1",
        "hubspot.deals.search.v1",
        "salesforce.query.soql.v1",
        "pipedrive.itemsearch.search.v1",
        "pipedrive.deals.search.v1",
        "zendesk_sell.contacts.list.v1",
        "zendesk_sell.deals.list.v1",
    ],
    "pipeline_prospecting_enrichment_api": [
        "apollo.people.search.v1",
        "apollo.people.enrich.v1",
        "apollo.contacts.create.v1",
        "clearbit.company.enrich.v1",
        "pdl.person.enrich.v1",
    ],
    "pipeline_outreach_execution_api": [
        "apollo.sequences.contacts.add.v1",
        "outreach.prospects.list.v1",
        "outreach.prospects.create.v1",
        "outreach.sequences.list.v1",
        "salesloft.people.list.v1",
        "salesloft.cadence_memberships.create.v1",
    ],
    "pipeline_engagement_signal_api": [
        "outreach.prospects.list.v1",
        "salesloft.people.list.v1",
        "hubspot.calls.list.v1",
        "hubspot.notes.list.v1",
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
# WRITE TOOLS — structured output for pipeline artifacts, schema enforced by strict=True
# =============================================================================

WRITE_PROSPECTING_BATCH_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_prospecting_batch",
    description="Write a completed prospecting batch artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/prospecting-batch-2024-01-15"},
            "batch": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["prospecting_batch"]},
                    "version": {"type": "string"},
                    "batch_id": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "source_channels": {"type": "array", "items": {"type": "string"}},
                    "prospects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "prospect_id": {"type": "string"},
                                "full_name": {"type": "string"},
                                "company_name": {"type": "string"},
                                "role": {"type": "string"},
                                "fit_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "contactability_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "source_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["prospect_id", "full_name", "company_name", "role", "fit_score", "contactability_score", "source_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "batch_quality": {
                        "type": "object",
                        "properties": {
                            "total_candidates": {"type": "integer", "minimum": 0},
                            "accepted_candidates": {"type": "integer", "minimum": 0},
                            "dedupe_ratio": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["total_candidates", "accepted_candidates", "dedupe_ratio"],
                        "additionalProperties": False,
                    },
                    "limitations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "batch_id", "target_segment", "source_channels", "prospects", "batch_quality", "limitations"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "batch"],
        "additionalProperties": False,
    },
)

WRITE_OUTREACH_EXECUTION_LOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_outreach_execution_log",
    description="Write an outreach execution log artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/outreach-log-2024-01-15"},
            "log": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["outreach_execution_log"]},
                    "version": {"type": "string"},
                    "batch_id": {"type": "string"},
                    "sequence_plan": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "provider": {"type": "string"},
                                "sequence_id": {"type": "string"},
                                "segment_target": {"type": "string"},
                            },
                            "required": ["provider", "sequence_id", "segment_target"],
                            "additionalProperties": False,
                        },
                    },
                    "enrollment_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string"},
                                "prospect_id": {"type": "string"},
                                "provider": {"type": "string"},
                                "status": {"type": "string", "enum": ["enrolled", "skipped", "failed"]},
                                "reason": {"type": "string"},
                            },
                            "required": ["event_id", "prospect_id", "provider", "status", "reason"],
                            "additionalProperties": False,
                        },
                    },
                    "delivery_summary": {"type": "object", "additionalProperties": {"type": "number"}},
                    "blocked_items": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "batch_id", "sequence_plan", "enrollment_events", "delivery_summary", "blocked_items"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "log"],
        "additionalProperties": False,
    },
)

WRITE_PROSPECT_DATA_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_prospect_data_quality",
    description="Write a prospect data quality check artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/data-quality-2024-01-15"},
            "quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["prospect_data_quality"]},
                    "version": {"type": "string"},
                    "batch_id": {"type": "string"},
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
                    "pass_fail": {"type": "string", "enum": ["pass", "fail"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "batch_id", "quality_checks", "pass_fail", "blocking_issues"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "quality"],
        "additionalProperties": False,
    },
)

WRITE_QUALIFICATION_MAP_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_qualification_map",
    description="Write a qualification map artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/qualification-map-2024-01-15"},
            "qualification_map": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["qualification_map"]},
                    "version": {"type": "string"},
                    "rubric": {"type": "string", "enum": ["icp_fit_x_pain_x_authority_x_timing"]},
                    "accounts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string"},
                                "account_name": {"type": "string"},
                                "qualification_state": {"type": "string", "enum": ["unqualified", "qualified", "high_priority"]},
                                "qualification_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "buying_committee": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "role": {"type": "string"},
                                            "contact_ref": {"type": "string"},
                                            "coverage_status": {"type": "string", "enum": ["covered", "partial", "missing"]},
                                        },
                                        "required": ["role", "contact_ref", "coverage_status"],
                                        "additionalProperties": False,
                                    },
                                },
                                "blockers": {"type": "array", "items": {"type": "string"}},
                                "next_action": {"type": "string"},
                            },
                            "required": ["account_id", "account_name", "qualification_state", "qualification_score", "buying_committee", "blockers", "next_action"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "rubric", "accounts", "coverage_status", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "qualification_map"],
        "additionalProperties": False,
    },
)

WRITE_BUYING_COMMITTEE_COVERAGE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_buying_committee_coverage",
    description="Write a buying committee coverage artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/committee-coverage-2024-01-15"},
            "coverage": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["buying_committee_coverage"]},
                    "version": {"type": "string"},
                    "accounts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "account_id": {"type": "string"},
                                "required_roles": {"type": "array", "items": {"type": "string"}},
                                "covered_roles": {"type": "array", "items": {"type": "string"}},
                                "missing_roles": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["account_id", "required_roles", "covered_roles", "missing_roles"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_gaps": {"type": "array", "items": {"type": "string"}},
                    "recommended_fills": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "accounts", "coverage_gaps", "recommended_fills"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "coverage"],
        "additionalProperties": False,
    },
)

WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_qualification_go_no_go_gate",
    description="Write a qualification go/no-go gate artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pipeline/go-no-go-gate-2024-01-15"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["qualification_go_no_go_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "no_go"]},
                    "in_scope_accounts": {"type": "array", "items": {"type": "string"}},
                    "out_of_scope_accounts": {"type": "array", "items": {"type": "string"}},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "gate_status", "in_scope_accounts", "out_of_scope_accounts", "blocking_issues", "next_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "gate"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_PROSPECT_ACQUISITION = [
    WRITE_PROSPECTING_BATCH_TOOL,
    WRITE_OUTREACH_EXECUTION_LOG_TOOL,
    WRITE_PROSPECT_DATA_QUALITY_TOOL,
]

WRITE_TOOLS_QUALIFICATION_MAPPER = [
    WRITE_QUALIFICATION_MAP_TOOL,
    WRITE_BUYING_COMMITTEE_COVERAGE_TOOL,
    WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL,
]

WRITE_TOOLS = WRITE_TOOLS_PROSPECT_ACQUISITION + WRITE_TOOLS_QUALIFICATION_MAPPER


async def handle_write_prospecting_batch(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        batch = args.get("batch")
        if not path or batch is None:
            return "Error: path and batch are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"prospecting_batch": batch}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nProspecting batch saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing prospecting batch: {type(e).__name__}: {e}"


async def handle_write_outreach_execution_log(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        log = args.get("log")
        if not path or log is None:
            return "Error: path and log are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"outreach_execution_log": log}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nOutreach execution log saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing outreach execution log: {type(e).__name__}: {e}"


async def handle_write_prospect_data_quality(
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
        doc = {"prospect_data_quality": quality}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nProspect data quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing prospect data quality: {type(e).__name__}: {e}"


async def handle_write_qualification_map(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        qualification_map = args.get("qualification_map")
        if not path or qualification_map is None:
            return "Error: path and qualification_map are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"qualification_map": qualification_map}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nQualification map saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing qualification map: {type(e).__name__}: {e}"


async def handle_write_buying_committee_coverage(
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
        doc = {"buying_committee_coverage": coverage}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nBuying committee coverage saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing buying committee coverage: {type(e).__name__}: {e}"


async def handle_write_qualification_go_no_go_gate(
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
        doc = {"qualification_go_no_go_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nQualification go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing qualification go/no-go gate: {type(e).__name__}: {e}"
