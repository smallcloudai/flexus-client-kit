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

CREATIVE_ASSET_OPS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="creative_asset_ops_api",
    description="creative_asset_ops_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PAID_CHANNEL_EXECUTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="paid_channel_execution_api",
    description="paid_channel_execution_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

PAID_CHANNEL_MEASUREMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="paid_channel_measurement_api",
    description="paid_channel_measurement_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

CREATIVE_FEEDBACK_CAPTURE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="creative_feedback_capture_api",
    description="creative_feedback_capture_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    CREATIVE_ASSET_OPS_TOOL,
    PAID_CHANNEL_EXECUTION_TOOL,
    PAID_CHANNEL_MEASUREMENT_TOOL,
    CREATIVE_FEEDBACK_CAPTURE_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "creative_asset_ops_api": [
        "meta.adcreatives.create.v1",
        "meta.adimages.create.v1",
        "meta.adcreatives.list.v1",
        "google_ads.ad_group_ad.create.v1",
        "google_ads.asset.create.v1",
        "linkedin.creatives.create.v1",
        "linkedin.creatives.list.v1",
    ],
    "paid_channel_execution_api": [
        "meta.campaigns.create.v1",
        "meta.adsets.create.v1",
        "meta.ads_insights.get.v1",
        "google_ads.campaigns.mutate.v1",
        "google_ads.search_stream.query.v1",
        "linkedin.ad_campaign_groups.create.v1",
        "linkedin.ad_campaigns.create.v1",
        "linkedin.ad_analytics.get.v1",
        "x_ads.campaigns.create.v1",
        "x_ads.line_items.create.v1",
        "x_ads.stats.query.v1",
    ],
    "paid_channel_measurement_api": [
        "ga4.properties.run_report.v1",
        "posthog.insights.trend.query.v1",
        "posthog.insights.funnel.query.v1",
        "mixpanel.funnels.query.v1",
        "mixpanel.retention.query.v1",
        "amplitude.dashboardrest.chart.get.v1",
    ],
    "creative_feedback_capture_api": [
        "intercom.conversations.list.v1",
        "intercom.conversations.search.v1",
        "typeform.responses.list.v1",
        "surveymonkey.surveys.responses.list.v1",
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

WRITE_CREATIVE_VARIANT_PACK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_creative_variant_pack",
    description="Write a completed creative variant pack to a policy document. Call once per creative production run.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /creatives/variant-pack-2024-01-15"},
            "variant_pack": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["creative_variant_pack"]},
                    "version": {"type": "string"},
                    "hypothesis_ref": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "variants": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "variant_id": {"type": "string"},
                                "concept": {"type": "string"},
                                "hook": {"type": "string"},
                                "primary_message": {"type": "string"},
                                "cta": {"type": "string"},
                                "channels": {"type": "array", "items": {"type": "string"}},
                                "asset_specs": {
                                    "type": "object",
                                    "properties": {
                                        "format": {"type": "string"},
                                        "aspect_ratio": {"type": "string"},
                                        "duration_seconds": {"type": ["number", "null"]},
                                        "max_text_density": {"type": ["string", "null"]},
                                    },
                                    "required": ["format", "aspect_ratio", "duration_seconds", "max_text_density"],
                                    "additionalProperties": False,
                                },
                            },
                            "required": ["variant_id", "concept", "hook", "primary_message", "cta", "channels", "asset_specs"],
                            "additionalProperties": False,
                        },
                    },
                    "format_constraints": {"type": "array", "items": {"type": "string"}},
                    "tone_constraints": {"type": "array", "items": {"type": "string"}},
                    "disallowed_claims": {"type": "array", "items": {"type": "string"}},
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": [
                    "artifact_type", "version", "hypothesis_ref", "target_segment",
                    "variants", "format_constraints", "tone_constraints",
                    "disallowed_claims", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "variant_pack"],
        "additionalProperties": False,
    },
)

WRITE_CREATIVE_ASSET_MANIFEST_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_creative_asset_manifest",
    description="Write a creative asset manifest tracking QA status across all assets for a variant pack.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /creatives/asset-manifest-2024-01-15"},
            "asset_manifest": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["creative_asset_manifest"]},
                    "version": {"type": "string"},
                    "manifest_id": {"type": "string"},
                    "assets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "asset_id": {"type": "string"},
                                "variant_id": {"type": "string"},
                                "platform": {"type": "string"},
                                "asset_ref": {"type": "string"},
                                "status": {"type": "string", "enum": ["draft", "ready", "rejected"]},
                                "qa_checks": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["asset_id", "variant_id", "platform", "asset_ref", "status", "qa_checks"],
                            "additionalProperties": False,
                        },
                    },
                    "qa_status": {"type": "string", "enum": ["pass", "warn", "fail"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "manifest_id", "assets", "qa_status", "blocking_issues"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "asset_manifest"],
        "additionalProperties": False,
    },
)

WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_creative_claim_risk_register",
    description="Write a claim risk register documenting substantiation status for all creative claims.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /creatives/claim-risk-register-2024-01-15"},
            "claim_risk_register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["creative_claim_risk_register"]},
                    "version": {"type": "string"},
                    "claims": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim_id": {"type": "string"},
                                "claim_text": {"type": "string"},
                                "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
                                "substantiation_status": {"type": "string", "enum": ["verified", "partially_verified", "unverified"]},
                            },
                            "required": ["claim_id", "claim_text", "risk_level", "substantiation_status"],
                            "additionalProperties": False,
                        },
                    },
                    "high_risk_claims": {"type": "array", "items": {"type": "string"}},
                    "required_proofs": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "claims", "high_risk_claims", "required_proofs"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "claim_risk_register"],
        "additionalProperties": False,
    },
)

WRITE_PAID_CHANNEL_TEST_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_paid_channel_test_plan",
    description="Write a paid channel test plan before launching a campaign. One plan per platform per test.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /paid/test-plan-meta-2024-01-15"},
            "test_plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["paid_channel_test_plan"]},
                    "version": {"type": "string"},
                    "test_id": {"type": "string"},
                    "platform": {"type": "string", "enum": ["meta", "google_ads", "linkedin", "x_ads"]},
                    "campaign_structure": {
                        "type": "object",
                        "properties": {
                            "objective": {"type": "string"},
                            "campaign_name": {"type": "string"},
                            "adset_or_adgroup_strategy": {"type": "string"},
                        },
                        "required": ["objective", "campaign_name", "adset_or_adgroup_strategy"],
                        "additionalProperties": False,
                    },
                    "targeting": {"type": "array", "items": {"type": "string"}},
                    "budget_guardrails": {
                        "type": "object",
                        "properties": {
                            "daily_cap": {"type": "number"},
                            "total_cap": {"type": "number"},
                        },
                        "required": ["daily_cap", "total_cap"],
                        "additionalProperties": False,
                    },
                    "run_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "success_metrics": {"type": "array", "items": {"type": "string"}},
                    "stop_conditions": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "test_id", "platform",
                    "campaign_structure", "targeting", "budget_guardrails",
                    "run_window", "success_metrics", "stop_conditions",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "test_plan"],
        "additionalProperties": False,
    },
)

WRITE_PAID_CHANNEL_RESULT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_paid_channel_result",
    description="Write paid channel test results after a campaign run. Includes decision and next step.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /paid/result-meta-2024-01-15"},
            "channel_result": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["paid_channel_result"]},
                    "version": {"type": "string"},
                    "platform": {"type": "string"},
                    "campaign_ref": {"type": "string"},
                    "spend": {"type": "number"},
                    "performance_summary": {
                        "type": "object",
                        "properties": {
                            "impressions": {"type": "number"},
                            "clicks": {"type": "number"},
                            "ctr": {"type": "number"},
                            "cpc": {"type": "number"},
                            "conversions": {"type": "number"},
                            "cpa": {"type": "number"},
                        },
                        "required": ["impressions", "clicks", "ctr", "cpc", "conversions", "cpa"],
                        "additionalProperties": False,
                    },
                    "guardrail_status": {"type": "string", "enum": ["safe", "warning", "breached"]},
                    "decision": {"type": "string", "enum": ["continue", "iterate", "stop"]},
                    "decision_reason": {"type": "string"},
                    "next_step": {"type": "string"},
                    "sources": {"type": "array", "items": _SOURCE_ITEM},
                },
                "required": [
                    "artifact_type", "version", "platform", "campaign_ref",
                    "spend", "performance_summary", "guardrail_status",
                    "decision", "decision_reason", "next_step", "sources",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "channel_result"],
        "additionalProperties": False,
    },
)

WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_paid_channel_budget_guardrail",
    description="Write a budget guardrail record documenting planned vs actual spend and any breaches.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /paid/budget-guardrail-2024-01-15"},
            "budget_guardrail": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["paid_channel_budget_guardrail"]},
                    "version": {"type": "string"},
                    "campaign_ref": {"type": "string"},
                    "planned_budget": {
                        "type": "object",
                        "properties": {
                            "daily_cap": {"type": "number"},
                            "total_cap": {"type": "number"},
                        },
                        "required": ["daily_cap", "total_cap"],
                        "additionalProperties": False,
                    },
                    "actual_spend": {
                        "type": "object",
                        "properties": {
                            "daily_spend": {"type": "number"},
                            "total_spend": {"type": "number"},
                        },
                        "required": ["daily_spend", "total_spend"],
                        "additionalProperties": False,
                    },
                    "breaches": {"type": "array", "items": {"type": "string"}},
                    "recommended_controls": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "campaign_ref",
                    "planned_budget", "actual_spend", "breaches", "recommended_controls",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "budget_guardrail"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_CREATIVE_VARIANT_PACK_TOOL,
    WRITE_CREATIVE_ASSET_MANIFEST_TOOL,
    WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL,
    WRITE_PAID_CHANNEL_TEST_PLAN_TOOL,
    WRITE_PAID_CHANNEL_RESULT_TOOL,
    WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL,
]


async def handle_write_creative_variant_pack(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        variant_pack = args.get("variant_pack")
        if not path or variant_pack is None:
            return "Error: path and variant_pack are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"creative_variant_pack": variant_pack}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nCreative variant pack saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative variant pack: {type(e).__name__}: {e}"


async def handle_write_creative_asset_manifest(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        asset_manifest = args.get("asset_manifest")
        if not path or asset_manifest is None:
            return "Error: path and asset_manifest are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"creative_asset_manifest": asset_manifest}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nCreative asset manifest saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative asset manifest: {type(e).__name__}: {e}"


async def handle_write_creative_claim_risk_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        claim_risk_register = args.get("claim_risk_register")
        if not path or claim_risk_register is None:
            return "Error: path and claim_risk_register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"creative_claim_risk_register": claim_risk_register}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nCreative claim risk register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative claim risk register: {type(e).__name__}: {e}"


async def handle_write_paid_channel_test_plan(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        test_plan = args.get("test_plan")
        if not path or test_plan is None:
            return "Error: path and test_plan are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"paid_channel_test_plan": test_plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPaid channel test plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel test plan: {type(e).__name__}: {e}"


async def handle_write_paid_channel_result(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        channel_result = args.get("channel_result")
        if not path or channel_result is None:
            return "Error: path and channel_result are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"paid_channel_result": channel_result}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPaid channel result saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel result: {type(e).__name__}: {e}"


async def handle_write_paid_channel_budget_guardrail(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        budget_guardrail = args.get("budget_guardrail")
        if not path or budget_guardrail is None:
            return "Error: path and budget_guardrail are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"paid_channel_budget_guardrail": budget_guardrail}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPaid channel budget guardrail saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel budget guardrail: {type(e).__name__}: {e}"
