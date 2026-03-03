import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_SEGMENT_ENRICHMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_segment_enrichment",
    description="Write a completed segment enrichment artifact. Call once per enrichment run after gathering all candidate segment evidence.",
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

WRITE_SEGMENT_DATA_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_segment_data_quality",
    description="Write a segment data quality check result. Call after completing quality checks for an enrichment run.",
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

WRITE_SEGMENT_PRIORITY_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_segment_priority_matrix",
    description="Write a segment priority matrix with weighted scores for all candidates.",
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

WRITE_PRIMARY_SEGMENT_DECISION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_primary_segment_decision",
    description="Write the primary segment decision with selected segment, runner-up, rejections, and next validation steps.",
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

WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_primary_segment_go_no_go_gate",
    description="Write the go/no-go gate result for the primary segment decision. Call after scoring to record gate status.",
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nPrimary segment go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing primary segment go/no-go gate: {type(e).__name__}: {e}"
