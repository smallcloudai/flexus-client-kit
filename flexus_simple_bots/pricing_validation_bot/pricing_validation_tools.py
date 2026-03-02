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

PRICING_RESEARCH_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pricing_research_ops_api",
    description='pricing_research_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PRICING_COMMITMENT_EVENTS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pricing_commitment_events_api",
    description='pricing_commitment_events_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PRICING_SALES_SIGNAL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pricing_sales_signal_api",
    description='pricing_sales_signal_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

PRICING_CATALOG_BENCHMARK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="pricing_catalog_benchmark_api",
    description='pricing_catalog_benchmark_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    PRICING_RESEARCH_OPS_TOOL,
    PRICING_COMMITMENT_EVENTS_TOOL,
    PRICING_SALES_SIGNAL_TOOL,
    PRICING_CATALOG_BENCHMARK_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "pricing_research_ops_api": [
        "typeform.forms.create.v1",
        "typeform.responses.list.v1",
        "surveymonkey.surveys.create.v1",
        "surveymonkey.surveys.responses.list.v1",
        "qualtrics.surveys.create.v1",
        "qualtrics.responseexports.start.v1",
        "qualtrics.responseexports.progress.get.v1",
        "qualtrics.responseexports.file.get.v1",
    ],
    "pricing_commitment_events_api": [
        "stripe.checkout.sessions.list.v1",
        "stripe.payment_intents.list.v1",
        "stripe.subscriptions.list.v1",
        "stripe.invoices.list.v1",
        "paddle.transactions.list.v1",
        "paddle.transactions.get.v1",
        "chargebee.subscriptions.list.v1",
        "chargebee.invoices.list.v1",
    ],
    "pricing_sales_signal_api": [
        "hubspot.deals.search.v1",
        "salesforce.query.soql.v1",
        "pipedrive.deals.search.v1",
        "pipedrive.itemsearch.search.v1",
    ],
    "pricing_catalog_benchmark_api": [
        "stripe.products.list.v1",
        "stripe.prices.list.v1",
        "paddle.products.list.v1",
        "paddle.prices.list.v1",
        # serpapi → use SerpApi MCP preset instead (mcp_presets/serpapi.json)
        "gnews.search.v1",
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

WRITE_PRICE_CORRIDOR_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_preliminary_price_corridor",
    description="Write a preliminary price corridor artifact to a policy document. Call once after modeling corridor from research.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/corridor-2024-01-15"},
            "corridor": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["preliminary_price_corridor"]},
                    "version": {"type": "string"},
                    "currency": {"type": "string"},
                    "corridor": {
                        "type": "object",
                        "properties": {
                            "floor": {"type": "number", "minimum": 0},
                            "target": {"type": "number", "minimum": 0},
                            "ceiling": {"type": "number", "minimum": 0},
                        },
                        "required": ["floor", "target", "ceiling"],
                        "additionalProperties": False,
                    },
                    "segment_corridors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "floor": {"type": "number", "minimum": 0},
                                "target": {"type": "number", "minimum": 0},
                                "ceiling": {"type": "number", "minimum": 0},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["segment_id", "floor", "target", "ceiling", "confidence"],
                            "additionalProperties": False,
                        },
                    },
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "sources": _SOURCES_SCHEMA,
                },
                "required": ["artifact_type", "version", "currency", "corridor", "segment_corridors", "assumptions", "confidence", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "corridor"],
        "additionalProperties": False,
    },
)

WRITE_PRICE_SENSITIVITY_CURVE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_price_sensitivity_curve",
    description="Write a price sensitivity curve artifact to a policy document. Call after completing WTP analysis.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/sensitivity-2024-01-15"},
            "curve": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["price_sensitivity_curve"]},
                    "version": {"type": "string"},
                    "method": {"type": "string", "enum": ["van_westendorp", "gabor_granger", "hybrid"]},
                    "sample_size": {"type": "integer", "minimum": 1},
                    "curve_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "price": {"type": "number", "minimum": 0},
                                "too_cheap_share": {"type": "number", "minimum": 0, "maximum": 1},
                                "cheap_share": {"type": "number", "minimum": 0, "maximum": 1},
                                "expensive_share": {"type": "number", "minimum": 0, "maximum": 1},
                                "too_expensive_share": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["price", "too_cheap_share", "cheap_share", "expensive_share", "too_expensive_share"],
                            "additionalProperties": False,
                        },
                    },
                    "interpretation": {"type": "array", "items": {"type": "string"}},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "method", "sample_size", "curve_points", "interpretation", "limitations"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "curve"],
        "additionalProperties": False,
    },
)

WRITE_PRICING_ASSUMPTION_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pricing_assumption_register",
    description="Write a pricing assumption register artifact to a policy document. Call after cataloging and assessing assumptions.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/assumptions-2024-01-15"},
            "register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pricing_assumption_register"]},
                    "version": {"type": "string"},
                    "assumptions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "assumption_id": {"type": "string"},
                                "statement": {"type": "string"},
                                "impact_level": {"type": "string", "enum": ["low", "medium", "high"]},
                                "evidence_status": {"type": "string", "enum": ["supported", "partially_supported", "unsupported"]},
                            },
                            "required": ["assumption_id", "statement", "impact_level", "evidence_status"],
                            "additionalProperties": False,
                        },
                    },
                    "high_risk_assumptions": {"type": "array", "items": {"type": "string"}},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "assumptions", "high_risk_assumptions", "next_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "register"],
        "additionalProperties": False,
    },
)

WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pricing_commitment_evidence",
    description="Write a pricing commitment evidence artifact to a policy document. Call once per evidence collection run.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/commitment-2024-01-15"},
            "evidence": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pricing_commitment_evidence"]},
                    "version": {"type": "string"},
                    "time_window": {
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
                                "signal_id": {"type": "string"},
                                "signal_type": {"type": "string", "enum": ["checkout_start_rate", "checkout_completion_rate", "trial_to_paid_rate", "discount_acceptance_rate", "quote_acceptance_rate", "payment_failure_rate", "refund_rate"]},
                                "segment_id": {"type": "string"},
                                "observed_value": {"type": "number"},
                                "interpretation": {"type": "string"},
                                "supporting_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["signal_id", "signal_type", "segment_id", "observed_value", "interpretation", "supporting_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "sources": _SOURCES_SCHEMA,
                },
                "required": ["artifact_type", "version", "time_window", "signals", "coverage_status", "confidence", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "evidence"],
        "additionalProperties": False,
    },
)

WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_validated_price_hypothesis",
    description="Write a validated price hypothesis artifact to a policy document. Call once per hypothesis tested.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/hypothesis-2024-01-15"},
            "hypothesis": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["validated_price_hypothesis"]},
                    "version": {"type": "string"},
                    "hypothesis_status": {"type": "string", "enum": ["validated", "partially_validated", "rejected"]},
                    "tested_price_point": {"type": "number", "minimum": 0},
                    "segment_id": {"type": "string"},
                    "commitment_evidence": {"type": "array", "items": {"type": "string"}},
                    "counter_evidence": {"type": "array", "items": {"type": "string"}},
                    "recommended_next_step": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "hypothesis_status", "tested_price_point", "segment_id", "commitment_evidence", "counter_evidence", "recommended_next_step", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "hypothesis"],
        "additionalProperties": False,
    },
)

WRITE_PRICING_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_pricing_go_no_go_gate",
    description="Write a pricing go/no-go gate artifact to a policy document. Call once after evaluating all commitment evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /pricing/gate-2024-01-15"},
            "gate": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["pricing_go_no_go_gate"]},
                    "version": {"type": "string"},
                    "gate_status": {"type": "string", "enum": ["go", "no_go"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "override_required": {"type": "boolean"},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "gate_status", "blocking_issues", "override_required", "next_checks"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "gate"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_PRICE_CORRIDOR_TOOL,
    WRITE_PRICE_SENSITIVITY_CURVE_TOOL,
    WRITE_PRICING_ASSUMPTION_REGISTER_TOOL,
    WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL,
    WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL,
    WRITE_PRICING_GO_NO_GO_GATE_TOOL,
]


async def handle_write_price_corridor(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        corridor = args.get("corridor")
        if not path or corridor is None:
            return "Error: path and corridor are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"preliminary_price_corridor": corridor}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPrice corridor saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing price corridor: {type(e).__name__}: {e}"


async def handle_write_price_sensitivity_curve(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        curve = args.get("curve")
        if not path or curve is None:
            return "Error: path and curve are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"price_sensitivity_curve": curve}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPrice sensitivity curve saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing price sensitivity curve: {type(e).__name__}: {e}"


async def handle_write_pricing_assumption_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        register = args.get("register")
        if not path or register is None:
            return "Error: path and register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"pricing_assumption_register": register}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPricing assumption register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing assumption register: {type(e).__name__}: {e}"


async def handle_write_pricing_commitment_evidence(
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
        doc = {"pricing_commitment_evidence": evidence}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPricing commitment evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing commitment evidence: {type(e).__name__}: {e}"


async def handle_write_validated_price_hypothesis(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        hypothesis = args.get("hypothesis")
        if not path or hypothesis is None:
            return "Error: path and hypothesis are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"validated_price_hypothesis": hypothesis}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nValidated price hypothesis saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing validated price hypothesis: {type(e).__name__}: {e}"


async def handle_write_pricing_go_no_go_gate(
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
        doc = {"pricing_go_no_go_gate": gate}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPricing go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing go/no-go gate: {type(e).__name__}: {e}"
