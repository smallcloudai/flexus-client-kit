import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_PAIN_SIGNAL_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pain_signal_register",
    description="Write a pain signal register to a policy document. Call after gathering all pain evidence for a channel.",
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

WRITE_PAIN_ECONOMICS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pain_economics",
    description="Write a pain economics model to a policy document. Call after quantifying cost impact.",
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

WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pain_research_readiness_gate",
    description="Write a research readiness gate decision to a policy document. Call after reviewing coverage and confidence.",
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


# =============================================================================
# =============================================================================

WRITE_ALTERNATIVE_LANDSCAPE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_alternative_landscape",
    description="Write an alternative landscape to a policy document. Call after mapping all alternatives.",
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

WRITE_COMPETITIVE_GAP_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_competitive_gap_matrix",
    description="Write a competitive gap matrix to a policy document. Call after scoring alternatives on evaluation dimensions.",
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

WRITE_DISPLACEMENT_HYPOTHESES_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_displacement_hypotheses",
    description="Write displacement hypotheses to a policy document. Call after deriving ranked switch triggers.",
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
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
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = data
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nDisplacement hypotheses saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing displacement hypotheses: {type(e).__name__}: {e}"
