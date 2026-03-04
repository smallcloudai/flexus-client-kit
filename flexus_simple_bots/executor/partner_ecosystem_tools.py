import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_partner_activation_scorecard",
    description="Write a completed partner activation scorecard artifact. Call once per activation cycle after gathering all funnel evidence.",
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

WRITE_PARTNER_ENABLEMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_partner_enablement_plan",
    description="Write a partner enablement plan artifact with tracks, owners, and completion criteria.",
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

WRITE_PARTNER_PIPELINE_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_partner_pipeline_quality",
    description="Write a partner pipeline quality artifact with stage conversion and SLA breach records.",
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

WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_channel_conflict_incident",
    description="Write a channel conflict incident artifact with incident records, resolution log, and policy updates.",
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

WRITE_DEAL_REGISTRATION_POLICY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_deal_registration_policy",
    description="Write a deal registration policy artifact with rules, approval flow, exception policy, and SLA targets.",
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

WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_conflict_resolution_audit",
    description="Write a conflict resolution audit artifact with resolved cases, SLA compliance, and required remediations.",
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
    WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL,
    WRITE_PARTNER_ENABLEMENT_PLAN_TOOL,
    WRITE_PARTNER_PIPELINE_QUALITY_TOOL,
    WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL,
    WRITE_DEAL_REGISTRATION_POLICY_TOOL,
    WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL,
]


async def handle_write_partner_activation_scorecard(
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
        return f"Written: {path}\n\nPartner activation scorecard saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner activation scorecard: {type(e).__name__}: {e}"


async def handle_write_partner_enablement_plan(
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
        return f"Written: {path}\n\nPartner enablement plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner enablement plan: {type(e).__name__}: {e}"


async def handle_write_partner_pipeline_quality(
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
        return f"Written: {path}\n\nPartner pipeline quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing partner pipeline quality: {type(e).__name__}: {e}"


async def handle_write_channel_conflict_incident(
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
        return f"Written: {path}\n\nChannel conflict incident saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing channel conflict incident: {type(e).__name__}: {e}"


async def handle_write_deal_registration_policy(
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
        return f"Written: {path}\n\nDeal registration policy saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing deal registration policy: {type(e).__name__}: {e}"


async def handle_write_conflict_resolution_audit(
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
        return f"Written: {path}\n\nConflict resolution audit saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing conflict resolution audit: {type(e).__name__}: {e}"
