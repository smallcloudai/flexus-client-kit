import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_INTERVIEW_CORPUS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_interview_corpus",
    description="Write a churn interview corpus artifact after completing interviews for a segment.",
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

WRITE_INTERVIEW_COVERAGE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_interview_coverage",
    description="Write a churn interview coverage report tracking gaps and required follow-ups.",
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

WRITE_SIGNAL_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_signal_quality",
    description="Write a churn signal quality report with pass/fail checks and remediation actions.",
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

WRITE_ROOTCAUSE_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_rootcause_backlog",
    description="Write the churn root-cause backlog with prioritized fix items linked to owners.",
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

WRITE_FIX_EXPERIMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_fix_experiment_plan",
    description="Write a churn fix experiment plan with measurement criteria and stop conditions.",
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

WRITE_PREVENTION_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_churn_prevention_priority_gate",
    description="Write a churn prevention priority gate decision with go/conditional/no_go status.",
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
    WRITE_INTERVIEW_CORPUS_TOOL,
    WRITE_INTERVIEW_COVERAGE_TOOL,
    WRITE_SIGNAL_QUALITY_TOOL,
    WRITE_ROOTCAUSE_BACKLOG_TOOL,
    WRITE_FIX_EXPERIMENT_PLAN_TOOL,
    WRITE_PREVENTION_GATE_TOOL,
]


async def handle_write_interview_corpus(
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
        return f"Written: {path}\n\nChurn interview corpus saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn interview corpus: {type(e).__name__}: {e}"


async def handle_write_interview_coverage(
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
        return f"Written: {path}\n\nChurn interview coverage saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn interview coverage: {type(e).__name__}: {e}"


async def handle_write_signal_quality(
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
        return f"Written: {path}\n\nChurn signal quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn signal quality: {type(e).__name__}: {e}"


async def handle_write_rootcause_backlog(
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
        return f"Written: {path}\n\nChurn root-cause backlog saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn root-cause backlog: {type(e).__name__}: {e}"


async def handle_write_fix_experiment_plan(
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
        return f"Written: {path}\n\nChurn fix experiment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn fix experiment plan: {type(e).__name__}: {e}"


async def handle_write_prevention_gate(
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
        return f"Written: {path}\n\nChurn prevention priority gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing churn prevention priority gate: {type(e).__name__}: {e}"
