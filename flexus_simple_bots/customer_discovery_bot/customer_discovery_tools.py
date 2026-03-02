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

DISCOVERY_SURVEY_DESIGN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_survey_design_api",
    description="discovery_survey_design_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_SURVEY_COLLECTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_survey_collection_api",
    description="discovery_survey_collection_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_PANEL_RECRUITMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_panel_recruitment_api",
    description="discovery_panel_recruitment_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_CUSTOMER_PANEL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_customer_panel_api",
    description="discovery_customer_panel_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_TEST_RECRUITMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_test_recruitment_api",
    description="discovery_test_recruitment_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_INTERVIEW_SCHEDULING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_interview_scheduling_api",
    description="discovery_interview_scheduling_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_INTERVIEW_CAPTURE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_interview_capture_api",
    description="discovery_interview_capture_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_TRANSCRIPT_CODING_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_transcript_coding_api",
    description="discovery_transcript_coding_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

DISCOVERY_CONTEXT_IMPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="discovery_context_import_api",
    description="discovery_context_import_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].",
    parameters=_API_TOOL_PARAMS,
)

API_TOOLS = [
    DISCOVERY_SURVEY_DESIGN_TOOL,
    DISCOVERY_SURVEY_COLLECTION_TOOL,
    DISCOVERY_PANEL_RECRUITMENT_TOOL,
    DISCOVERY_CUSTOMER_PANEL_TOOL,
    DISCOVERY_TEST_RECRUITMENT_TOOL,
    DISCOVERY_INTERVIEW_SCHEDULING_TOOL,
    DISCOVERY_INTERVIEW_CAPTURE_TOOL,
    DISCOVERY_TRANSCRIPT_CODING_TOOL,
    DISCOVERY_CONTEXT_IMPORT_TOOL,
]

TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "discovery_survey_design_api": [
        "surveymonkey.surveys.create.v1",
        "surveymonkey.surveys.update.v1",
        "typeform.forms.create.v1",
        "typeform.forms.update.v1",
        "qualtrics.surveys.create.v1",
        "qualtrics.surveys.update.v1",
    ],
    "discovery_survey_collection_api": [
        "surveymonkey.collectors.create.v1",
        "surveymonkey.surveys.responses.list.v1",
        "typeform.responses.list.v1",
        "qualtrics.responseexports.start.v1",
        "qualtrics.responseexports.progress.get.v1",
        "qualtrics.responseexports.file.get.v1",
    ],
    "discovery_panel_recruitment_api": [
        "prolific.studies.create.v1",
        "prolific.studies.get.v1",
        "prolific.submissions.list.v1",
        "prolific.submissions.approve.v1",
        "prolific.submissions.reject.v1",
        "cint.projects.create.v1",
        "cint.projects.feasibility.get.v1",
        "cint.projects.launch.v1",
        "mturk.hits.create.v1",
        "mturk.hits.list.v1",
        "mturk.assignments.list.v1",
        "mturk.assignments.approve.v1",
    ],
    "discovery_customer_panel_api": [
        "qualtrics.mailinglists.list.v1",
        "qualtrics.contacts.create.v1",
        "qualtrics.contacts.list.v1",
        "qualtrics.distributions.create.v1",
        "userinterviews.participants.create.v1",
        "userinterviews.participants.update.v1",
        "userinterviews.participants.delete.v1",
    ],
    "discovery_test_recruitment_api": [
        "usertesting.tests.create.v1",
        "usertesting.tests.sessions.list.v1",
        "usertesting.results.transcript.get.v1",
        "prolific.studies.create.v1",
        "prolific.submissions.list.v1",
        "mturk.hits.create.v1",
        "mturk.assignments.list.v1",
    ],
    "discovery_interview_scheduling_api": [
        "calendly.scheduled_events.list.v1",
        "calendly.scheduled_events.invitees.list.v1",
        "google_calendar.events.insert.v1",
        "google_calendar.events.list.v1",
    ],
    "discovery_interview_capture_api": [
        "zoom.recordings.list.v1",
        "zoom.recordings.transcript.download.v1",
        "gong.calls.list.v1",
        "gong.calls.transcript.get.v1",
        "fireflies.transcript.get.v1",
    ],
    "discovery_transcript_coding_api": [
        "dovetail.insights.export.markdown.v1",
        "dovetail.projects.export.zip.v1",
    ],
    "discovery_context_import_api": [
        "hubspot.contacts.search.v1",
        "hubspot.notes.list.v1",
        "hubspot.calls.list.v1",
        "zendesk.incremental.ticket_events.comment_events.list.v1",
        "zendesk.tickets.audits.list.v1",
        "intercom.conversations.list.v1",
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
# WRITE TOOLS — discovery_instrument_designer
# =============================================================================

WRITE_INTERVIEW_INSTRUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_interview_instrument",
    description="Write a completed interview instrument to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/instruments/interview-2024-01-15"},
            "instrument": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["interview_instrument"]},
                    "version": {"type": "string"},
                    "instrument_id": {"type": "string"},
                    "research_goal": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
                    "interview_mode": {"type": "string", "enum": ["live_video", "live_audio", "async_text"]},
                    "question_blocks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question_id": {"type": "string"},
                                "question_text": {"type": "string"},
                                "evidence_objective": {"type": "string"},
                                "question_type": {"type": "string", "enum": ["past_behavior", "timeline", "switch_trigger", "decision_criteria", "objection_probe"]},
                                "forbidden_patterns": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["question_id", "question_text", "evidence_objective", "question_type", "forbidden_patterns"],
                            "additionalProperties": False,
                        },
                    },
                    "probe_bank": {"type": "array", "items": {"type": "string"}},
                    "bias_controls": {"type": "array", "items": {"type": "string"}},
                    "consent_protocol": {
                        "type": "object",
                        "properties": {
                            "consent_required": {"type": "boolean"},
                            "recording_policy": {"type": "string"},
                        },
                        "required": ["consent_required", "recording_policy"],
                        "additionalProperties": False,
                    },
                    "completion_criteria": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "instrument_id", "research_goal",
                    "target_segment", "hypothesis_refs", "interview_mode", "question_blocks",
                    "probe_bank", "bias_controls", "consent_protocol", "completion_criteria",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "instrument"],
        "additionalProperties": False,
    },
)

WRITE_SURVEY_INSTRUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_survey_instrument",
    description="Write a completed survey instrument to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/instruments/survey-2024-01-15"},
            "instrument": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["survey_instrument"]},
                    "version": {"type": "string"},
                    "instrument_id": {"type": "string"},
                    "survey_goal": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
                    "sample_plan": {
                        "type": "object",
                        "properties": {
                            "target_n": {"type": "integer", "minimum": 1},
                            "min_n_per_segment": {"type": "integer", "minimum": 1},
                        },
                        "required": ["target_n", "min_n_per_segment"],
                        "additionalProperties": False,
                    },
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question_id": {"type": "string"},
                                "question_text": {"type": "string"},
                                "response_type": {"type": "string", "enum": ["single_select", "multi_select", "likert", "numeric", "free_text"]},
                                "answer_scale": {"type": ["string", "null"]},
                            },
                            "required": ["question_id", "question_text", "response_type", "answer_scale"],
                            "additionalProperties": False,
                        },
                    },
                    "branching_rules": {"type": "array", "items": {"type": "string"}},
                    "quality_controls": {"type": "array", "items": {"type": "string"}},
                    "analysis_plan": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "instrument_id", "survey_goal",
                    "target_segment", "hypothesis_refs", "sample_plan", "questions",
                    "branching_rules", "quality_controls", "analysis_plan",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "instrument"],
        "additionalProperties": False,
    },
)

WRITE_INSTRUMENT_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_discovery_instrument_readiness",
    description="Write a discovery instrument readiness assessment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/readiness/instrument-id-2024-01-15"},
            "readiness": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["discovery_instrument_readiness"]},
                    "version": {"type": "string"},
                    "instrument_id": {"type": "string"},
                    "readiness_state": {"type": "string", "enum": ["ready", "revise", "blocked"]},
                    "blocking_issues": {"type": "array", "items": {"type": "string"}},
                    "recommended_fixes": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["artifact_type", "version", "instrument_id", "readiness_state", "blocking_issues", "recommended_fixes"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "readiness"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_INSTRUMENT = [
    WRITE_INTERVIEW_INSTRUMENT_TOOL,
    WRITE_SURVEY_INSTRUMENT_TOOL,
    WRITE_INSTRUMENT_READINESS_TOOL,
]


# =============================================================================
# WRITE TOOLS — participant_recruitment_operator
# =============================================================================

WRITE_RECRUITMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_participant_recruitment_plan",
    description="Write a participant recruitment plan to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/recruitment/plan-2024-01-15"},
            "plan": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["participant_recruitment_plan"]},
                    "version": {"type": "string"},
                    "plan_id": {"type": "string"},
                    "study_type": {"type": "string", "enum": ["survey", "interview", "usability_test", "mixed"]},
                    "target_segment": {"type": "string"},
                    "quota_cells": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cell_id": {"type": "string"},
                                "target_n": {"type": "integer", "minimum": 1},
                            },
                            "required": ["cell_id", "target_n"],
                            "additionalProperties": False,
                        },
                    },
                    "channels": {"type": "array", "items": {"type": "string"}},
                    "inclusion_criteria": {"type": "array", "items": {"type": "string"}},
                    "exclusion_criteria": {"type": "array", "items": {"type": "string"}},
                    "incentive_policy": {
                        "type": "object",
                        "properties": {
                            "currency": {"type": "string"},
                            "amount_range": {"type": "string"},
                        },
                        "required": ["currency", "amount_range"],
                        "additionalProperties": False,
                    },
                    "timeline": {
                        "type": "object",
                        "properties": {
                            "launch_date": {"type": "string"},
                            "target_close_date": {"type": "string"},
                        },
                        "required": ["launch_date", "target_close_date"],
                        "additionalProperties": False,
                    },
                },
                "required": [
                    "artifact_type", "version", "plan_id", "study_type", "target_segment",
                    "quota_cells", "channels", "inclusion_criteria", "exclusion_criteria",
                    "incentive_policy", "timeline",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "plan"],
        "additionalProperties": False,
    },
)

WRITE_RECRUITMENT_FUNNEL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_recruitment_funnel_snapshot",
    description="Write a recruitment funnel snapshot to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/recruitment/funnel-2024-01-15"},
            "snapshot": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["recruitment_funnel_snapshot"]},
                    "version": {"type": "string"},
                    "plan_id": {"type": "string"},
                    "snapshot_ts": {"type": "string"},
                    "provider_breakdown": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "provider": {"type": "string"},
                                "invited": {"type": "integer", "minimum": 0},
                                "started": {"type": "integer", "minimum": 0},
                                "qualified": {"type": "integer", "minimum": 0},
                                "completed": {"type": "integer", "minimum": 0},
                            },
                            "required": ["provider", "invited", "started", "qualified", "completed"],
                            "additionalProperties": False,
                        },
                    },
                    "overall_status": {"type": "string", "enum": ["on_track", "at_risk", "blocked"]},
                    "dropoff_reasons": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "plan_id", "snapshot_ts",
                    "provider_breakdown", "overall_status", "dropoff_reasons",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "snapshot"],
        "additionalProperties": False,
    },
)

WRITE_RECRUITMENT_COMPLIANCE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_recruitment_compliance_quality",
    description="Write a recruitment compliance quality assessment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/recruitment/compliance-2024-01-15"},
            "quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["recruitment_compliance_quality"]},
                    "version": {"type": "string"},
                    "plan_id": {"type": "string"},
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
                    "fraud_signals": {"type": "array", "items": {"type": "string"}},
                    "consent_traceability": {"type": "string", "enum": ["complete", "partial", "missing"]},
                    "pass_fail": {"type": "string", "enum": ["pass", "fail"]},
                },
                "required": [
                    "artifact_type", "version", "plan_id", "quality_checks",
                    "fraud_signals", "consent_traceability", "pass_fail",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "quality"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_RECRUITMENT = [
    WRITE_RECRUITMENT_PLAN_TOOL,
    WRITE_RECRUITMENT_FUNNEL_TOOL,
    WRITE_RECRUITMENT_COMPLIANCE_TOOL,
]


# =============================================================================
# WRITE TOOLS — jtbd_interview_operator
# =============================================================================

WRITE_INTERVIEW_CORPUS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_interview_corpus",
    description="Write an interview corpus to a policy document after coding all sessions.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/evidence/corpus-2024-01-15"},
            "corpus": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["interview_corpus"]},
                    "version": {"type": "string"},
                    "study_id": {"type": "string"},
                    "time_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "target_segment": {"type": "string"},
                    "interviews": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "interview_id": {"type": "string"},
                                "source_type": {"type": "string", "enum": ["live_call", "recording_import", "async_form"]},
                                "respondent_profile": {"type": "object"},
                                "transcript_ref": {"type": "string"},
                                "coded_events": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "event_id": {"type": "string"},
                                            "event_type": {"type": "string", "enum": ["struggle", "workaround", "trigger", "decision_criteria", "objection"]},
                                            "event_text": {"type": "string"},
                                            "evidence_strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                                        },
                                        "required": ["event_id", "event_type", "event_text", "evidence_strength"],
                                        "additionalProperties": False,
                                    },
                                },
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                            "required": ["interview_id", "source_type", "respondent_profile", "transcript_ref", "coded_events", "confidence"],
                            "additionalProperties": False,
                        },
                    },
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "insufficient"]},
                    "limitations": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "study_id", "time_window",
                    "target_segment", "interviews", "coverage_status", "limitations",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "corpus"],
        "additionalProperties": False,
    },
)

WRITE_JTBD_OUTCOMES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_jtbd_outcomes",
    description="Write a JTBD outcomes artifact to a policy document after synthesizing interview evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/evidence/jtbd-outcomes-2024-01-15"},
            "outcomes": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["jtbd_outcomes"]},
                    "version": {"type": "string"},
                    "study_id": {"type": "string"},
                    "job_map": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "step_id": {"type": "string"},
                                "step_name": {"type": "string"},
                            },
                            "required": ["step_id", "step_name"],
                            "additionalProperties": False,
                        },
                    },
                    "outcomes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "outcome_id": {"type": "string"},
                                "outcome_statement": {"type": "string"},
                                "underserved_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "supporting_interview_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["outcome_id", "outcome_statement", "underserved_score", "supporting_interview_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "forces": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "force_type": {"type": "string", "enum": ["push", "pull", "habit", "anxiety"]},
                                "summary": {"type": "string"},
                            },
                            "required": ["force_type", "summary"],
                            "additionalProperties": False,
                        },
                    },
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "study_id", "job_map",
                    "outcomes", "forces", "confidence", "next_checks",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "outcomes"],
        "additionalProperties": False,
    },
)

WRITE_EVIDENCE_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_discovery_evidence_quality",
    description="Write a discovery evidence quality assessment to a policy document.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /discovery/evidence/quality-2024-01-15"},
            "quality": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["discovery_evidence_quality"]},
                    "version": {"type": "string"},
                    "study_id": {"type": "string"},
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
                "required": ["artifact_type", "version", "study_id", "quality_checks", "pass_fail", "blocking_issues"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "quality"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS_INTERVIEW = [
    WRITE_INTERVIEW_CORPUS_TOOL,
    WRITE_JTBD_OUTCOMES_TOOL,
    WRITE_EVIDENCE_QUALITY_TOOL,
]

WRITE_TOOLS = [
    *WRITE_TOOLS_INSTRUMENT,
    *WRITE_TOOLS_RECRUITMENT,
    *WRITE_TOOLS_INTERVIEW,
]


# =============================================================================
# WRITE HANDLERS
# =============================================================================

async def handle_write_interview_instrument(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        instrument = args.get("instrument")
        if not path or instrument is None:
            return "Error: path and instrument are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"interview_instrument": instrument}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nInterview instrument saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing interview instrument: {type(e).__name__}: {e}"


async def handle_write_survey_instrument(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        instrument = args.get("instrument")
        if not path or instrument is None:
            return "Error: path and instrument are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"survey_instrument": instrument}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSurvey instrument saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing survey instrument: {type(e).__name__}: {e}"


async def handle_write_instrument_readiness(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        readiness = args.get("readiness")
        if not path or readiness is None:
            return "Error: path and readiness are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"discovery_instrument_readiness": readiness}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nInstrument readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing instrument readiness: {type(e).__name__}: {e}"


async def handle_write_recruitment_plan(
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
        doc = {"participant_recruitment_plan": plan}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRecruitment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment plan: {type(e).__name__}: {e}"


async def handle_write_recruitment_funnel(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        snapshot = args.get("snapshot")
        if not path or snapshot is None:
            return "Error: path and snapshot are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"recruitment_funnel_snapshot": snapshot}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRecruitment funnel snapshot saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment funnel snapshot: {type(e).__name__}: {e}"


async def handle_write_recruitment_compliance(
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
        doc = {"recruitment_compliance_quality": quality}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRecruitment compliance quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment compliance quality: {type(e).__name__}: {e}"


async def handle_write_interview_corpus(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        corpus = args.get("corpus")
        if not path or corpus is None:
            return "Error: path and corpus are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"interview_corpus": corpus}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nInterview corpus saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing interview corpus: {type(e).__name__}: {e}"


async def handle_write_jtbd_outcomes(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        outcomes = args.get("outcomes")
        if not path or outcomes is None:
            return "Error: path and outcomes are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"jtbd_outcomes": outcomes}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nJTBD outcomes saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing JTBD outcomes: {type(e).__name__}: {e}"


async def handle_write_evidence_quality(
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
        doc = {"discovery_evidence_quality": quality}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nDiscovery evidence quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing discovery evidence quality: {type(e).__name__}: {e}"
