import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_MVP_RUN_LOG_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_mvp_run_log",
    description="Write a completed MVP run log to a policy document. Call once per run to record lifecycle, delivery events, and guardrail status.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_MVP_ROLLOUT_INCIDENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_mvp_rollout_incident",
    description="Write a rollout incident report to a policy document. Call when guardrail breach or critical issue is detected.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_MVP_FEEDBACK_DIGEST_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_mvp_feedback_digest",
    description="Write a synthesized feedback digest to a policy document. Call after aggregating user feedback for a run.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_TELEMETRY_QUALITY_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_telemetry_quality_report",
    description="Write a telemetry quality audit report to a policy document. Call after validating event coverage, metric lineage, and instrumentation health.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_TELEMETRY_DECISION_MEMO_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_telemetry_decision_memo",
    description="Write a telemetry-based decision memo (scale/iterate/stop) to a policy document. Call after completing telemetry integrity analysis.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_MVP_SCALE_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_mvp_scale_readiness_gate",
    description="Write a scale readiness gate verdict to a policy document. Call as the final go/no-go decision before scaling.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "data": {"type": "object"},
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_MVP_RUN_LOG_TOOL,
    WRITE_MVP_ROLLOUT_INCIDENT_TOOL,
    WRITE_MVP_FEEDBACK_DIGEST_TOOL,
    WRITE_TELEMETRY_QUALITY_REPORT_TOOL,
    WRITE_TELEMETRY_DECISION_MEMO_TOOL,
    WRITE_MVP_SCALE_READINESS_GATE_TOOL,
]


async def handle_write_mvp_run_log(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nMVP run log saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_run_log: {type(e).__name__}: {e}"


async def handle_write_mvp_rollout_incident(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nRollout incident report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_rollout_incident: {type(e).__name__}: {e}"


async def handle_write_mvp_feedback_digest(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nFeedback digest saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_feedback_digest: {type(e).__name__}: {e}"


async def handle_write_telemetry_quality_report(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nTelemetry quality report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing telemetry_quality_report: {type(e).__name__}: {e}"


async def handle_write_telemetry_decision_memo(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nTelemetry decision memo saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing telemetry_decision_memo: {type(e).__name__}: {e}"


async def handle_write_mvp_scale_readiness_gate(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nScale readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing mvp_scale_readiness_gate: {type(e).__name__}: {e}"
