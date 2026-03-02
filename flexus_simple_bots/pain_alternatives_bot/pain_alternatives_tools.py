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

PAIN_VOICE_OF_CUSTOMER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pain_voice_of_customer_api",
    description="pain_voice_of_customer_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PAIN_SUPPORT_SIGNAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pain_support_signal_api",
    description="pain_support_signal_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

ALTERNATIVES_MARKET_SCAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="alternatives_market_scan_api",
    description="alternatives_market_scan_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

ALTERNATIVES_TRACTION_BENCHMARK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="alternatives_traction_benchmark_api",
    description="alternatives_traction_benchmark_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PAIN_VOICE_OF_CUSTOMER_TOOL,
    PAIN_SUPPORT_SIGNAL_TOOL,
    ALTERNATIVES_MARKET_SCAN_TOOL,
    ALTERNATIVES_TRACTION_BENCHMARK_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "pain_voice_of_customer_api": [
        "trustpilot.reviews.list.v1",
        "g2.reviews.list.v1",
        "reddit.search.posts.v1",
        "appstoreconnect.customer_reviews.list.v1",
        "google_play.reviews.list.v1",
    ],
    "pain_support_signal_api": [
        "intercom.conversations.list.v1",
        "intercom.conversations.search.v1",
        "zendesk.tickets.list.v1",
        "zendesk.ticket_comments.list.v1",
        "hubspot.tickets.search.v1",
    ],
    "alternatives_market_scan_api": [
        # serpapi → use SerpApi MCP preset instead (mcp_presets/serpapi.json)
        "gnews.search.v1",
        "producthunt.graphql.posts.v1",
        "crunchbase.organizations.search.v1",
        "crunchbase.organizations.lookup.v1",
    ],
    "alternatives_traction_benchmark_api": [
        "similarweb.website.traffic_and_engagement.get.v1",
        "similarweb.website.marketing_channel_sources.get.v1",
        "builtwith.domain.live.v1",
        "wappalyzer.lookup.v2",
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
# WRITE TOOLS — pain_quantifier expert output schemas
# =============================================================================

WRITE_PAIN_SIGNAL_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pain_signal_register",
    description="Write a pain signal register to a policy document. Call after gathering all pain evidence for a channel.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pain/saas-smb-2024-01-15"},
            "pain_signal_register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pain_signal_register"]},
                    "version": {"type": "string"},
                    "channel_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "signals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pain_id": {"type": "string"},
                                "pain_statement": {"type": "string"},
                                "affected_segment": {"type": "string"},
                                "frequency_signal": {"type": "string", "enum": ["low", "medium", "high"]},
                                "severity_signal": {"type": "string", "enum": ["low", "medium", "high"]},
                                "evidence_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["pain_id", "pain_statement", "affected_segment", "frequency_signal", "severity_signal", "evidence_refs"],
                            "additionalProperties": False,
                        },
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
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "channel_window", "signals", "sources", "coverage_status", "limitations", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pain_signal_register"],
        "additionalProperties": False,
    },
)

WRITE_PAIN_ECONOMICS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pain_economics",
    description="Write a pain economics model to a policy document. Call after quantifying cost impact.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pain/economics-2024-01-15"},
            "pain_economics": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pain_economics"]},
                    "version": {"type": "string"},
                    "model_id": {"type": "string"},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "pain_register": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "pain_id": {"type": "string"},
                                "estimated_cost_per_period": {"type": "number", "minimum": 0},
                                "cost_unit": {"type": "string", "enum": ["usd_per_month", "usd_per_quarter", "hours_per_month", "other"]},
                                "sensitivity_level": {"type": "string", "enum": ["low", "medium", "high"]},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["pain_id", "estimated_cost_per_period", "cost_unit", "sensitivity_level", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "total_cost_range": {
                        "type": "object",
                        "properties": {
                            "floor": {"type": "number", "minimum": 0},
                            "target": {"type": "number", "minimum": 0},
                            "ceiling": {"type": "number", "minimum": 0},
                        },
                        "required": ["floor", "target", "ceiling"],
                        "additionalProperties": False,
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "model_id", "assumptions", "pain_register", "total_cost_range", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pain_economics"],
        "additionalProperties": False,
    },
)

WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pain_research_readiness_gate",
    description="Write a research readiness gate decision to a policy document. Call after reviewing coverage and confidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pain/gate-2024-01-15"},
            "pain_research_readiness_gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pain_research_readiness_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "revise", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "gate_status", "blocking_issues", "next_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "pain_research_readiness_gate"],
        "additionalProperties": False,
    },
)


# =============================================================================
# WRITE TOOLS — alternative_mapper expert output schemas
# =============================================================================

WRITE_ALTERNATIVE_LANDSCAPE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_alternative_landscape",
    description="Write an alternative landscape to a policy document. Call after mapping all alternatives.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /alternatives/landscape-2024-01-15"},
            "alternative_landscape": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["alternative_landscape"]},
                    "version": {"type": "string"},
                    "target_problem": {"type": "string"},
                    "alternatives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "alternative_id": {"type": "string"},
                                "alternative_name": {"type": "string"},
                                "alternative_type": {"type": "string", "enum": ["direct_competitor", "adjacent_tool", "status_quo_internal", "outsourcing_service"]},
                                "positioning_claim": {"type": "string"},
                                "pricing_model": {"type": "string"},
                                "adoption_reasons": {"type": "array", "items": {"type": "string"}},
                                "failure_reasons": {"type": "array", "items": {"type": "string"}},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["alternative_id", "alternative_name", "alternative_type", "positioning_claim", "pricing_model", "adoption_reasons", "failure_reasons", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "target_problem", "alternatives", "coverage_status", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "alternative_landscape"],
        "additionalProperties": False,
    },
)

WRITE_COMPETITIVE_GAP_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_competitive_gap_matrix",
    description="Write a competitive gap matrix to a policy document. Call after scoring alternatives on evaluation dimensions.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /alternatives/gap-matrix-2024-01-15"},
            "competitive_gap_matrix": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["competitive_gap_matrix"]},
                    "version": {"type": "string"},
                    "evaluation_dimensions": {"type": "array", "items": {"type": "string"}},
                    "matrix": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "alternative_id": {"type": "string"},
                                "dimension_scores": {
                                    "type": "object",
                                    "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1},
                                },
                                "overall_gap_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "risk_flags": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["alternative_id", "dimension_scores", "overall_gap_score", "risk_flags"],
                            "additionalProperties": False,
                        },
                    },
                    "recommended_attack_surfaces": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "evaluation_dimensions", "matrix", "recommended_attack_surfaces"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "competitive_gap_matrix"],
        "additionalProperties": False,
    },
)

WRITE_DISPLACEMENT_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_displacement_hypotheses",
    description="Write displacement hypotheses to a policy document. Call after deriving ranked switch triggers.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /alternatives/hypotheses-2024-01-15"},
            "displacement_hypotheses": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["displacement_hypotheses"]},
                    "version": {"type": "string"},
                    "prioritization_rule": {"type": "string", "enum": ["impact_x_confidence_x_reversibility"]},
                    "hypotheses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "hypothesis_id": {"type": "string"},
                                "statement": {"type": "string"},
                                "target_alternative": {"type": "string"},
                                "expected_switch_trigger": {"type": "string"},
                                "test_signal": {"type": "string"},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["hypothesis_id", "statement", "target_alternative", "expected_switch_trigger", "test_signal", "confidence", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["artifact_type", "version", "prioritization_rule", "hypotheses"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "displacement_hypotheses"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_PAIN_SIGNAL_REGISTER_TOOL,
    WRITE_PAIN_ECONOMICS_TOOL,
    WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL,
    WRITE_ALTERNATIVE_LANDSCAPE_TOOL,
    WRITE_COMPETITIVE_GAP_MATRIX_TOOL,
    WRITE_DISPLACEMENT_HYPOTHESES_TOOL,
]


async def handle_write_pain_signal_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pain_signal_register")
        if not path or artifact is None:
            return "Error: path and pain_signal_register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pain_signal_register": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPain signal register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pain signal register: {type(e).__name__}: {e}"


async def handle_write_pain_economics(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pain_economics")
        if not path or artifact is None:
            return "Error: path and pain_economics are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pain_economics": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPain economics saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pain economics: {type(e).__name__}: {e}"


async def handle_write_pain_research_readiness_gate(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("pain_research_readiness_gate")
        if not path or artifact is None:
            return "Error: path and pain_research_readiness_gate are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pain_research_readiness_gate": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nResearch readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing research readiness gate: {type(e).__name__}: {e}"


async def handle_write_alternative_landscape(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("alternative_landscape")
        if not path or artifact is None:
            return "Error: path and alternative_landscape are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"alternative_landscape": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nAlternative landscape saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing alternative landscape: {type(e).__name__}: {e}"


async def handle_write_competitive_gap_matrix(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("competitive_gap_matrix")
        if not path or artifact is None:
            return "Error: path and competitive_gap_matrix are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"competitive_gap_matrix": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nCompetitive gap matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing competitive gap matrix: {type(e).__name__}: {e}"


async def handle_write_displacement_hypotheses(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        artifact = args.get("displacement_hypotheses")
        if not path or artifact is None:
            return "Error: path and displacement_hypotheses are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"displacement_hypotheses": artifact}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nDisplacement hypotheses saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing displacement hypotheses: {type(e).__name__}: {e}"
