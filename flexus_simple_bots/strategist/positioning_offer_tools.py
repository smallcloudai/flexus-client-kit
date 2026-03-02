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

POSITIONING_MESSAGE_TEST_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="positioning_message_test_api",
    description="positioning_message_test_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

POSITIONING_COMPETITOR_INTEL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="positioning_competitor_intel_api",
    description="positioning_competitor_intel_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

OFFER_PACKAGING_BENCHMARK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="offer_packaging_benchmark_api",
    description="offer_packaging_benchmark_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

POSITIONING_CHANNEL_PROBE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="positioning_channel_probe_api",
    description="positioning_channel_probe_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    POSITIONING_MESSAGE_TEST_TOOL,
    POSITIONING_COMPETITOR_INTEL_TOOL,
    OFFER_PACKAGING_BENCHMARK_TOOL,
    POSITIONING_CHANNEL_PROBE_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "positioning_message_test_api": [
        "typeform.forms.create.v1",
        "typeform.responses.list.v1",
        "surveymonkey.surveys.create.v1",
        "surveymonkey.surveys.responses.list.v1",
        "qualtrics.surveys.create.v1",
        "qualtrics.responseexports.start.v1",
        "qualtrics.responseexports.progress.get.v1",
        "qualtrics.responseexports.file.get.v1",
    ],
    "positioning_competitor_intel_api": [
        # serpapi → use SerpApi MCP preset instead (mcp_presets/serpapi.json)
        "gnews.search.v1",
        "crunchbase.organizations.search.v1",
        "crunchbase.organizations.lookup.v1",
        # Similarweb -> use MCP preset instead (mcp_presets/similarweb.json)
    ],
    "offer_packaging_benchmark_api": [
        # Stripe -> use MCP preset instead (mcp_presets/stripe.json)
        "paddle.products.list.v1",
        "paddle.prices.list.v1",
    ],
    "positioning_channel_probe_api": [
        "meta.adcreatives.create.v1",
        "meta.ads_insights.get.v1",
        "linkedin.ad_campaigns.create.v1",
        "linkedin.ad_analytics.get.v1",
        "google_ads.ad_group_ad.create.v1",
        "google_ads.search_stream.query.v1",
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
# WRITE TOOLS — value_proposition_synthesizer outputs
# =============================================================================

WRITE_VALUE_PROPOSITION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_value_proposition",
    description="Write a completed value proposition artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/smb-value-prop-2024-01-15"},
            "value_proposition": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["value_proposition"]},
                    "version": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "core_claim": {"type": "string"},
                    "proof_points": {"type": "array", "items": {"type": "string"}},
                    "differentiators": {"type": "array", "items": {"type": "string"}},
                    "objection_handling": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "objection": {"type": "string"},
                                "response": {"type": "string"},
                            },
                            "required": ["objection", "response"],
                            "additionalProperties": False,
                        },
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
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
                "required": ["artifact_type", "version", "target_segment", "core_claim", "proof_points", "differentiators", "objection_handling", "confidence", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "value_proposition"],
        "additionalProperties": False,
    },
)

WRITE_OFFER_PACKAGING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_offer_packaging",
    description="Write a completed offer packaging artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/smb-offer-packaging-2024-01-15"},
            "offer_packaging": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["offer_packaging"]},
                    "version": {"type": "string"},
                    "pricing_model_type": {"type": "string", "enum": ["subscription", "usage_based", "hybrid", "one_time"]},
                    "packages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "package_id": {"type": "string"},
                                "package_name": {"type": "string"},
                                "intended_segment": {"type": "string"},
                                "included_outcomes": {"type": "array", "items": {"type": "string"}},
                                "pricing_anchor": {"type": "string"},
                                "feature_fences": {"type": "array", "items": {"type": "string"}},
                                "optional_add_ons": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["package_id", "package_name", "intended_segment", "included_outcomes", "pricing_anchor", "feature_fences"],
                            "additionalProperties": False,
                        },
                    },
                    "guardrails": {"type": "array", "items": {"type": "string"}},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["artifact_type", "version", "pricing_model_type", "packages", "guardrails", "assumptions", "confidence"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "offer_packaging"],
        "additionalProperties": False,
    },
)

WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_positioning_narrative_brief",
    description="Write a completed positioning narrative brief artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/narrative-brief-v1"},
            "positioning_narrative_brief": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["positioning_narrative_brief"]},
                    "version": {"type": "string"},
                    "narrative_id": {"type": "string"},
                    "problem_statement": {"type": "string"},
                    "old_way": {"type": "string"},
                    "new_way": {"type": "string"},
                    "reason_to_believe": {"type": "array", "items": {"type": "string"}},
                    "tone_constraints": {"type": "array", "items": {"type": "string"}},
                    "disallowed_claims": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "narrative_id", "problem_statement", "old_way", "new_way", "reason_to_believe", "tone_constraints", "disallowed_claims"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "positioning_narrative_brief"],
        "additionalProperties": False,
    },
)

# =============================================================================
# WRITE TOOLS — positioning_test_operator outputs
# =============================================================================

WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_messaging_experiment_plan",
    description="Write a messaging experiment plan artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/experiment-plan-exp-001"},
            "messaging_experiment_plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["messaging_experiment_plan"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "variants": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "variant_id": {"type": "string"},
                                "headline": {"type": "string"},
                                "value_claim": {"type": "string"},
                                "cta": {"type": "string"},
                            },
                            "required": ["variant_id", "headline", "value_claim"],
                            "additionalProperties": False,
                        },
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["survey_panel", "meta_ads", "linkedin_ads", "google_ads", "email_probe"]},
                    },
                    "success_metrics": {"type": "array", "items": {"type": "string"}},
                    "stop_conditions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "experiment_id", "target_segment", "variants", "channels", "success_metrics", "stop_conditions"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "messaging_experiment_plan"],
        "additionalProperties": False,
    },
)

WRITE_POSITIONING_TEST_RESULT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_positioning_test_result",
    description="Write a positioning test result artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/test-result-exp-001"},
            "positioning_test_result": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["positioning_test_result"]},
                    "version": {"type": "string"},
                    "experiment_id": {"type": "string"},
                    "variants_tested": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "variant_id": {"type": "string"},
                                "channel_results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "channel": {"type": "string"},
                                            "metric": {"type": "string"},
                                            "value": {"type": "number"},
                                        },
                                        "required": ["channel", "metric", "value"],
                                        "additionalProperties": False,
                                    },
                                },
                                "aggregate_score": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["variant_id", "channel_results", "aggregate_score"],
                            "additionalProperties": False,
                        },
                    },
                    "winner_variant_id": {"type": "string"},
                    "result_summary": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "decision_reason": {"type": "string"},
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
                "required": ["artifact_type", "version", "experiment_id", "variants_tested", "winner_variant_id", "result_summary", "confidence", "decision_reason", "sources"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "positioning_test_result"],
        "additionalProperties": False,
    },
)

WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_positioning_claim_risk_register",
    description="Write a positioning claim risk register artifact to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /positioning/claim-risk-register-2024-01-15"},
            "positioning_claim_risk_register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["positioning_claim_risk_register"]},
                    "version": {"type": "string"},
                    "claims": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim_id": {"type": "string"},
                                "claim_text": {"type": "string"},
                                "substantiation_status": {"type": "string", "enum": ["verified", "partially_verified", "unverified"]},
                                "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            },
                            "required": ["claim_id", "claim_text", "substantiation_status", "risk_level"],
                            "additionalProperties": False,
                        },
                    },
                    "compliance_flags": {"type": "array", "items": {"type": "string"}},
                    "high_risk_claims": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "claims", "compliance_flags", "high_risk_claims"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "positioning_claim_risk_register"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_VALUE_PROPOSITION_TOOL,
    WRITE_OFFER_PACKAGING_TOOL,
    WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL,
    WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL,
    WRITE_POSITIONING_TEST_RESULT_TOOL,
    WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL,
]


async def handle_write_value_proposition(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        value_proposition = args.get("value_proposition")
        if not path or value_proposition is None:
            return "Error: path and value_proposition are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"value_proposition": value_proposition}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nValue proposition saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing value proposition: {type(e).__name__}: {e}"


async def handle_write_offer_packaging(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        offer_packaging = args.get("offer_packaging")
        if not path or offer_packaging is None:
            return "Error: path and offer_packaging are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"offer_packaging": offer_packaging}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nOffer packaging saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing offer packaging: {type(e).__name__}: {e}"


async def handle_write_positioning_narrative_brief(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        positioning_narrative_brief = args.get("positioning_narrative_brief")
        if not path or positioning_narrative_brief is None:
            return "Error: path and positioning_narrative_brief are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"positioning_narrative_brief": positioning_narrative_brief}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPositioning narrative brief saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning narrative brief: {type(e).__name__}: {e}"


async def handle_write_messaging_experiment_plan(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        messaging_experiment_plan = args.get("messaging_experiment_plan")
        if not path or messaging_experiment_plan is None:
            return "Error: path and messaging_experiment_plan are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"messaging_experiment_plan": messaging_experiment_plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nMessaging experiment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing messaging experiment plan: {type(e).__name__}: {e}"


async def handle_write_positioning_test_result(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        positioning_test_result = args.get("positioning_test_result")
        if not path or positioning_test_result is None:
            return "Error: path and positioning_test_result are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"positioning_test_result": positioning_test_result}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPositioning test result saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning test result: {type(e).__name__}: {e}"


async def handle_write_positioning_claim_risk_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        positioning_claim_risk_register = args.get("positioning_claim_risk_register")
        if not path or positioning_claim_risk_register is None:
            return "Error: path and positioning_claim_risk_register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"positioning_claim_risk_register": positioning_claim_risk_register}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPositioning claim risk register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning claim risk register: {type(e).__name__}: {e}"
