"""
Stub tools for bots whose provider-backed execution is not yet implemented.
Each tool accepts op/args contract and returns a structured not-implemented response.
Used so builder can validate and scaffold all bots; runtime returns stub until real integration.
"""

import json
from typing import Any, Callable, Awaitable, Dict, Optional

from flexus_client_kit.core import ckit_cloudtool


_STUB_TOOL_NAMES: tuple[str, ...] = (
    "alternatives_market_scan_api",
    "alternatives_traction_benchmark_api",
    "channel_conflict_governance_api",
    "churn_feedback_capture_api",
    "churn_interview_ops_api",
    "churn_remediation_backlog_api",
    "churn_transcript_analysis_api",
    "creative_asset_ops_api",
    "creative_feedback_capture_api",
    "discovery_context_import_api",
    "discovery_customer_panel_api",
    "discovery_interview_capture_api",
    "discovery_interview_scheduling_api",
    "discovery_panel_recruitment_api",
    "discovery_survey_collection_api",
    "discovery_survey_design_api",
    "discovery_test_recruitment_api",
    "discovery_transcript_coding_api",
    "experiment_backlog_ops_api",
    "experiment_guardrail_metrics_api",
    "experiment_instrumentation_quality_api",
    "experiment_runtime_config_api",
    "gtm_media_efficiency_api",
    "gtm_unit_economics_api",
    "mvp_experiment_orchestration_api",
    "mvp_feedback_capture_api",
    "mvp_instrumentation_health_api",
    "mvp_telemetry_api",
    "offer_packaging_benchmark_api",
    "paid_channel_execution_api",
    "paid_channel_measurement_api",
    "pain_support_signal_api",
    "pain_voice_of_customer_api",
    "partner_account_mapping_api",
    "partner_enablement_execution_api",
    "partner_program_ops_api",
    "pilot_contracting_api",
    "pilot_delivery_ops_api",
    "pilot_stakeholder_sync_api",
    "pilot_usage_evidence_api",
    "pipeline_crm_api",
    "pipeline_engagement_signal_api",
    "pipeline_outreach_execution_api",
    "pipeline_prospecting_enrichment_api",
    "playbook_repo_api",
    "positioning_channel_probe_api",
    "positioning_competitor_intel_api",
    "positioning_message_test_api",
    "pricing_catalog_benchmark_api",
    "pricing_commitment_events_api",
    "pricing_research_ops_api",
    "pricing_sales_signal_api",
    "retention_account_context_api",
    "retention_feedback_research_api",
    "retention_product_analytics_api",
    "retention_revenue_events_api",
    "rtm_pipeline_finance_api",
    "rtm_territory_policy_api",
    "scale_change_execution_api",
    "scale_guardrail_monitoring_api",
    "scale_incident_response_api",
    "segment_crm_signal_api",
    "segment_firmographic_enrichment_api",
    "segment_intent_signal_api",
    "segment_market_traction_api",
    "segment_technographic_profile_api",
)


def _mk_stub_tool(name: str) -> ckit_cloudtool.CloudTool:
    try:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=name,
            description=f"{name}: stub. Provider-backed execution not wired yet. Use op=\"help\".",
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string"},
                    "args": {"type": "object"},
                },
            },
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot create stub CloudTool for {name}: {e}") from e


def _stub_help_text(name: str) -> str:
    return (
        f"{name}(op=\"help\")\n"
        f"{name}(op=\"status\")\n"
        f"{name}(op=\"<operation>\", args={{...}})\n\n"
        "Provider-backed execution is not implemented yet. Tool is registered for builder/scaffold."
    )


def _stub_handler(name: str) -> Callable[[ckit_cloudtool.FCloudtoolCall, Optional[Dict[str, Any]]], Awaitable[str]]:
    async def _handler(
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        _ = toolcall
        try:
            if not model_produced_args:
                return _stub_help_text(name)
            op = model_produced_args.get("op", "help")
            if op == "help":
                return _stub_help_text(name)
            if op == "status":
                return json.dumps({
                    "ok": True,
                    "tool_name": name,
                    "status": "stub",
                    "provider_execution": "not_implemented",
                }, indent=2)
            args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
            if args_error:
                return args_error
            payload = {
                "ok": False,
                "error_code": "NOT_IMPLEMENTED",
                "message": "Provider-backed execution is not wired in this runtime yet.",
                "tool_name": name,
                "op": op,
                "args": args,
            }
            return (
                "Execution contract accepted, but provider call path is not implemented yet.\n\n"
                + json.dumps(payload, indent=2)
            )
        except (TypeError, ValueError, KeyError) as e:
            return f"Error in {name}: {type(e).__name__}: {e}"

    return _handler


STUB_CLOUD_TOOLS: dict[str, ckit_cloudtool.CloudTool] = {
    name: _mk_stub_tool(name) for name in _STUB_TOOL_NAMES
}


def make_stub_handler(tool_name: str) -> Callable[[ckit_cloudtool.FCloudtoolCall, Optional[Dict[str, Any]]], Awaitable[str]]:
    try:
        if tool_name not in STUB_CLOUD_TOOLS:
            raise KeyError(tool_name)
        return _stub_handler(tool_name)
    except KeyError as e:
        raise RuntimeError(f"Unknown stub tool name: {tool_name}") from e
