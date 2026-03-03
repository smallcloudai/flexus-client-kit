import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

# =============================================================================

WRITE_PROSPECTING_BATCH_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_prospecting_batch",
    description="Write a completed prospecting batch artifact to a policy document.",
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

WRITE_OUTREACH_EXECUTION_LOG_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_outreach_execution_log",
    description="Write an outreach execution log artifact to a policy document.",
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

WRITE_PROSPECT_DATA_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_prospect_data_quality",
    description="Write a prospect data quality check artifact to a policy document.",
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

WRITE_QUALIFICATION_MAP_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_qualification_map",
    description="Write a qualification map artifact to a policy document.",
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

WRITE_BUYING_COMMITTEE_COVERAGE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_buying_committee_coverage",
    description="Write a buying committee coverage artifact to a policy document.",
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

WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_qualification_go_no_go_gate",
    description="Write a qualification go/no-go gate artifact to a policy document.",
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

WRITE_TOOLS_PROSPECT_ACQUISITION = [
    WRITE_PROSPECTING_BATCH_TOOL,
    WRITE_OUTREACH_EXECUTION_LOG_TOOL,
    WRITE_PROSPECT_DATA_QUALITY_TOOL,
]

WRITE_TOOLS_QUALIFICATION_MAPPER = [
    WRITE_QUALIFICATION_MAP_TOOL,
    WRITE_BUYING_COMMITTEE_COVERAGE_TOOL,
    WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL,
]

WRITE_TOOLS = WRITE_TOOLS_PROSPECT_ACQUISITION + WRITE_TOOLS_QUALIFICATION_MAPPER


async def handle_write_prospecting_batch(
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
        return f"Written: {path}\n\nProspecting batch saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing prospecting batch: {type(e).__name__}: {e}"


async def handle_write_outreach_execution_log(
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
        return f"Written: {path}\n\nOutreach execution log saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing outreach execution log: {type(e).__name__}: {e}"


async def handle_write_prospect_data_quality(
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
        return f"Written: {path}\n\nProspect data quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing prospect data quality: {type(e).__name__}: {e}"


async def handle_write_qualification_map(
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
        return f"Written: {path}\n\nQualification map saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing qualification map: {type(e).__name__}: {e}"


async def handle_write_buying_committee_coverage(
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
        return f"Written: {path}\n\nBuying committee coverage saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing buying committee coverage: {type(e).__name__}: {e}"


async def handle_write_qualification_go_no_go_gate(
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
        return f"Written: {path}\n\nQualification go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing qualification go/no-go gate: {type(e).__name__}: {e}"
