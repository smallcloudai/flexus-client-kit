import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_COHORT_REVENUE_REVIEW_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_cohort_revenue_review",
    description="Write a cohort revenue review artifact after completing activation-retention-revenue diagnostics.",
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

WRITE_RETENTION_DRIVER_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_retention_driver_matrix",
    description="Write a retention driver matrix artifact ranking activation, engagement, and commercial drivers by impact.",
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

WRITE_RETENTION_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_retention_readiness_gate",
    description="Write a retention readiness gate artifact with go/conditional/no_go decision and blocking issues.",
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

WRITE_PMF_CONFIDENCE_SCORECARD_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pmf_confidence_scorecard",
    description="Write a PMF confidence scorecard artifact after interpreting survey and behavioral evidence.",
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

WRITE_PMF_SIGNAL_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pmf_signal_evidence",
    description="Write a PMF signal evidence artifact cataloguing positive and negative signals with evidence gaps.",
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

WRITE_PMF_RESEARCH_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pmf_research_backlog",
    description="Write a PMF research backlog artifact with prioritized hypotheses and owner assignments.",
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
    WRITE_COHORT_REVENUE_REVIEW_TOOL,
    WRITE_RETENTION_DRIVER_MATRIX_TOOL,
    WRITE_RETENTION_READINESS_GATE_TOOL,
    WRITE_PMF_CONFIDENCE_SCORECARD_TOOL,
    WRITE_PMF_SIGNAL_EVIDENCE_TOOL,
    WRITE_PMF_RESEARCH_BACKLOG_TOOL,
]


async def handle_write_cohort_revenue_review(
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
        return f"Written: {path}\n\nCohort revenue review saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing cohort revenue review: {type(e).__name__}: {e}"


async def handle_write_retention_driver_matrix(
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
        return f"Written: {path}\n\nRetention driver matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing retention driver matrix: {type(e).__name__}: {e}"


async def handle_write_retention_readiness_gate(
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
        return f"Written: {path}\n\nRetention readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing retention readiness gate: {type(e).__name__}: {e}"


async def handle_write_pmf_confidence_scorecard(
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
        return f"Written: {path}\n\nPMF confidence scorecard saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF confidence scorecard: {type(e).__name__}: {e}"


async def handle_write_pmf_signal_evidence(
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
        return f"Written: {path}\n\nPMF signal evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF signal evidence: {type(e).__name__}: {e}"


async def handle_write_pmf_research_backlog(
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
        return f"Written: {path}\n\nPMF research backlog saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing PMF research backlog: {type(e).__name__}: {e}"
