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

SEGMENT_CRM_SIGNAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="segment_crm_signal_api",
    description="segment_crm_signal_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SEGMENT_FIRMOGRAPHIC_ENRICHMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="segment_firmographic_enrichment_api",
    description="segment_firmographic_enrichment_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SEGMENT_TECHNOGRAPHIC_PROFILE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="segment_technographic_profile_api",
    description="segment_technographic_profile_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SEGMENT_MARKET_TRACTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="segment_market_traction_api",
    description="segment_market_traction_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

SEGMENT_INTENT_SIGNAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="segment_intent_signal_api",
    description="segment_intent_signal_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    SEGMENT_CRM_SIGNAL_TOOL,
    SEGMENT_FIRMOGRAPHIC_ENRICHMENT_TOOL,
    SEGMENT_TECHNOGRAPHIC_PROFILE_TOOL,
    SEGMENT_MARKET_TRACTION_TOOL,
    SEGMENT_INTENT_SIGNAL_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "segment_crm_signal_api": [
        # HubSpot -> use MCP preset instead (mcp_presets/hubspot.json)
        "salesforce.query.soql.v1",
        "pipedrive.organizations.search.v1",
        "pipedrive.deals.search.v1",
    ],
    "segment_firmographic_enrichment_api": [
        "clearbit.company.enrich.v1",
        "apollo.organizations.enrich.v1",
        "apollo.organizations.bulk_enrich.v1",
        "pdl.company.enrich.v1",
    ],
    "segment_technographic_profile_api": [
        "builtwith.domain.api.v1",
        "builtwith.domain.live.v1",
        "wappalyzer.lookup.v2",
    ],
    "segment_market_traction_api": [
        "crunchbase.organizations.lookup.v1",
        "crunchbase.organizations.search.v1",
        # Similarweb -> use MCP preset instead (mcp_presets/similarweb.json)
        "google_ads.keywordplan.generate_historical_metrics.v1",
    ],
    "segment_intent_signal_api": [
        "sixsense.company.identification.v1",
        "sixsense.people.search.v1",
        "bombora.companysurge.topics.list.v1",
        "bombora.companysurge.company_scores.get.v1",
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

WRITE_SEGMENT_ENRICHMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_segment_enrichment",
    description="Write a completed segment enrichment artifact. Call once per enrichment run after gathering all candidate segment evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /segments/enrichment-2024-01-15"},
            "segment_enrichment": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["segment_enrichment"]},
                    "version": {"type": "string"},
                    "enrichment_run_id": {"type": "string"},
                    "candidate_segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "segment_name": {"type": "string"},
                                "source_refs": {
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
                                "firmographics": {
                                    "type": "object",
                                    "properties": {
                                        "employee_range": {"type": "string"},
                                        "revenue_range": {"type": "string"},
                                        "geo_focus": {"type": "array", "items": {"type": "string"}},
                                        "ownership_type": {"type": "string"},
                                    },
                                    "required": ["employee_range", "revenue_range", "geo_focus"],
                                    "additionalProperties": False,
                                },
                                "technographics": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "stack_name": {"type": "string"},
                                            "adoption_signal": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                                            "source_ref": {"type": "string"},
                                        },
                                        "required": ["stack_name", "adoption_signal", "source_ref"],
                                        "additionalProperties": False,
                                    },
                                },
                                "demand_signals": {
                                    "type": "object",
                                    "properties": {
                                        "search_demand_index": {"type": "number", "minimum": 0},
                                        "intent_surge_level": {"type": "string", "enum": ["low", "medium", "high"]},
                                        "intent_source_refs": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["search_demand_index", "intent_surge_level"],
                                    "additionalProperties": False,
                                },
                                "crm_signals": {
                                    "type": "object",
                                    "properties": {
                                        "open_pipeline_count": {"type": "integer", "minimum": 0},
                                        "win_rate_proxy": {"type": "number", "minimum": 0, "maximum": 1},
                                        "avg_sales_cycle_days": {"type": "number", "minimum": 0},
                                    },
                                    "required": ["open_pipeline_count", "win_rate_proxy", "avg_sales_cycle_days"],
                                    "additionalProperties": False,
                                },
                                "data_completeness": {"type": "number", "minimum": 0, "maximum": 1},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["segment_id", "segment_name", "source_refs", "firmographics", "technographics", "demand_signals", "crm_signals", "data_completeness", "confidence"],
                            "additionalProperties": False,
                        },
                    },
                    "data_coverage": {
                        "type": "object",
                        "properties": {
                            "segments_total": {"type": "integer", "minimum": 0},
                            "segments_with_full_minimum_data": {"type": "integer", "minimum": 0},
                        },
                        "required": ["segments_total", "segments_with_full_minimum_data"],
                        "additionalProperties": False,
                    },
                    "gaps": {"type": "array", "items": {"type": "string"}},
                    "next_refresh_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "enrichment_run_id", "candidate_segments", "data_coverage", "gaps", "next_refresh_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "segment_enrichment"],
        "additionalProperties": False,
    },
)

WRITE_SEGMENT_DATA_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_segment_data_quality",
    description="Write a segment data quality check result. Call after completing quality checks for an enrichment run.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /segments/quality-2024-01-15"},
            "segment_data_quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["segment_data_quality"]},
                    "version": {"type": "string"},
                    "enrichment_run_id": {"type": "string"},
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
                "required": ["artifact_type", "version", "enrichment_run_id", "quality_checks", "pass_fail", "blocking_issues"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "segment_data_quality"],
        "additionalProperties": False,
    },
)

WRITE_SEGMENT_PRIORITY_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_segment_priority_matrix",
    description="Write a segment priority matrix with weighted scores for all candidates.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /segments/priority-matrix-2024-01-15"},
            "segment_priority_matrix": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["segment_priority_matrix"]},
                    "version": {"type": "string"},
                    "evaluation_rule": {"type": "string", "enum": ["fit_x_pain_x_access_x_velocity"]},
                    "weights": {
                        "type": "object",
                        "properties": {
                            "fit": {"type": "number", "minimum": 0, "maximum": 1},
                            "pain": {"type": "number", "minimum": 0, "maximum": 1},
                            "access": {"type": "number", "minimum": 0, "maximum": 1},
                            "velocity": {"type": "number", "minimum": 0, "maximum": 1},
                        },
                        "required": ["fit", "pain", "access", "velocity"],
                        "additionalProperties": False,
                    },
                    "candidates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "fit_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "pain_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "access_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "velocity_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "weighted_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "risks": {"type": "array", "items": {"type": "string"}},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["segment_id", "fit_score", "pain_score", "access_score", "velocity_score", "weighted_score", "risks", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["artifact_type", "version", "evaluation_rule", "weights", "candidates"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "segment_priority_matrix"],
        "additionalProperties": False,
    },
)

WRITE_PRIMARY_SEGMENT_DECISION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_primary_segment_decision",
    description="Write the primary segment decision with selected segment, runner-up, rejections, and next validation steps.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /segments/decision-2024-01-15"},
            "primary_segment_decision": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["primary_segment_decision"]},
                    "version": {"type": "string"},
                    "selected_primary_segment": {
                        "type": "object",
                        "properties": {
                            "segment_id": {"type": "string"},
                            "why_now": {"type": "string"},
                            "entry_motion": {"type": "string", "enum": ["outbound", "inbound", "partner_led", "plg_assisted"]},
                            "risk_flags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["segment_id", "why_now", "entry_motion", "risk_flags"],
                        "additionalProperties": False,
                    },
                    "runner_up": {"type": "string"},
                    "decision_reason": {"type": "string"},
                    "rejections": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "rejection_reason": {"type": "string"},
                            },
                            "required": ["segment_id", "rejection_reason"],
                            "additionalProperties": False,
                        },
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "next_validation_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "selected_primary_segment", "runner_up", "decision_reason", "rejections", "confidence", "next_validation_steps"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "primary_segment_decision"],
        "additionalProperties": False,
    },
)

WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_primary_segment_go_no_go_gate",
    description="Write the go/no-go gate result for the primary segment decision. Call after scoring to record gate status.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /segments/go-no-go-2024-01-15"},
            "primary_segment_go_no_go_gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["primary_segment_go_no_go_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "override_required": {"type": "boolean"},
                },
                "required": ["artifact_type", "version", "gate_status", "blocking_issues", "override_required"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "primary_segment_go_no_go_gate"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_SEGMENT_ENRICHMENT_TOOL,
    WRITE_SEGMENT_DATA_QUALITY_TOOL,
    WRITE_SEGMENT_PRIORITY_MATRIX_TOOL,
    WRITE_PRIMARY_SEGMENT_DECISION_TOOL,
    WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL,
]


async def handle_write_segment_enrichment(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        payload = args.get("segment_enrichment")
        if not path or payload is None:
            return "Error: path and segment_enrichment are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"segment_enrichment": payload}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSegment enrichment saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing segment enrichment: {type(e).__name__}: {e}"


async def handle_write_segment_data_quality(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        payload = args.get("segment_data_quality")
        if not path or payload is None:
            return "Error: path and segment_data_quality are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"segment_data_quality": payload}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSegment data quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing segment data quality: {type(e).__name__}: {e}"


async def handle_write_segment_priority_matrix(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        payload = args.get("segment_priority_matrix")
        if not path or payload is None:
            return "Error: path and segment_priority_matrix are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"segment_priority_matrix": payload}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSegment priority matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing segment priority matrix: {type(e).__name__}: {e}"


async def handle_write_primary_segment_decision(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        payload = args.get("primary_segment_decision")
        if not path or payload is None:
            return "Error: path and primary_segment_decision are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"primary_segment_decision": payload}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPrimary segment decision saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing primary segment decision: {type(e).__name__}: {e}"


async def handle_write_primary_segment_go_no_go_gate(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        payload = args.get("primary_segment_go_no_go_gate")
        if not path or payload is None:
            return "Error: path and primary_segment_go_no_go_gate are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"primary_segment_go_no_go_gate": payload}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPrimary segment go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing primary segment go/no-go gate: {type(e).__name__}: {e}"
