import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_UNIT_ECONOMICS_REVIEW_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_unit_economics_review",
    description="Write a completed unit economics review artifact to a policy document.",
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

WRITE_CHANNEL_MARGIN_STACK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_channel_margin_stack",
    description="Write a channel margin stack artifact to a policy document.",
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

WRITE_PAYBACK_READINESS_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_payback_readiness_gate",
    description="Write a payback readiness gate decision to a policy document.",
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

WRITE_RTM_RULES_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_rtm_rules",
    description="Write RTM ownership and engagement rules artifact to a policy document.",
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

WRITE_DEAL_OWNERSHIP_MATRIX_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_deal_ownership_matrix",
    description="Write a deal ownership matrix artifact to a policy document.",
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

WRITE_RTM_CONFLICT_PLAYBOOK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_rtm_conflict_resolution_playbook",
    description="Write an RTM conflict resolution playbook artifact to a policy document.",
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

WRITE_TOOLS_ECONOMICS = [
    WRITE_UNIT_ECONOMICS_REVIEW_TOOL,
    WRITE_CHANNEL_MARGIN_STACK_TOOL,
    WRITE_PAYBACK_READINESS_GATE_TOOL,
]

WRITE_TOOLS_RTM = [
    WRITE_RTM_RULES_TOOL,
    WRITE_DEAL_OWNERSHIP_MATRIX_TOOL,
    WRITE_RTM_CONFLICT_PLAYBOOK_TOOL,
]

WRITE_TOOLS = [
    *WRITE_TOOLS_ECONOMICS,
    *WRITE_TOOLS_RTM,
]


async def handle_write_unit_economics_review(
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
        return f"Written: {path}\n\nUnit economics review saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing unit economics review: {type(e).__name__}: {e}"


async def handle_write_channel_margin_stack(
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
        return f"Written: {path}\n\nChannel margin stack saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing channel margin stack: {type(e).__name__}: {e}"


async def handle_write_payback_readiness_gate(
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
        return f"Written: {path}\n\nPayback readiness gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing payback readiness gate: {type(e).__name__}: {e}"


async def handle_write_rtm_rules(
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
        return f"Written: {path}\n\nRTM rules saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing RTM rules: {type(e).__name__}: {e}"


async def handle_write_deal_ownership_matrix(
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
        return f"Written: {path}\n\nDeal ownership matrix saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing deal ownership matrix: {type(e).__name__}: {e}"


async def handle_write_rtm_conflict_playbook(
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
        return f"Written: {path}\n\nRTM conflict resolution playbook saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing RTM conflict resolution playbook: {type(e).__name__}: {e}"
