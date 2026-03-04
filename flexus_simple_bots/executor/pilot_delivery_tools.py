import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_PILOT_CONTRACT_PACKET_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pilot_contract_packet",
    description="Write a completed pilot contract packet to a policy document. Call once all scope, terms, stakeholders and signatures are finalized.",
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

WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pilot_risk_clause_register",
    description="Write the risk clause register for a pilot contract. Call after reviewing all contract terms for risk exposure.",
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

WRITE_PILOT_GO_LIVE_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pilot_go_live_readiness",
    description="Write the go/no-go readiness gate for a pilot. Call when all pre-launch checks are complete.",
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

CONTRACTING_WRITE_TOOLS = [
    WRITE_PILOT_CONTRACT_PACKET_TOOL,
    WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL,
    WRITE_PILOT_GO_LIVE_READINESS_TOOL,
]

# =============================================================================
# =============================================================================

WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_first_value_delivery_plan",
    description="Write the first value delivery plan. Call once delivery steps, owners, timeline and risk controls are defined.",
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

WRITE_FIRST_VALUE_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_first_value_evidence",
    description="Write first value evidence after delivery outcomes are confirmed by stakeholders.",
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

WRITE_PILOT_EXPANSION_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pilot_expansion_readiness",
    description="Write the pilot expansion readiness assessment. Call after first value evidence is collected and expansion decision is due.",
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

DELIVERY_WRITE_TOOLS = [
    WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL,
    WRITE_FIRST_VALUE_EVIDENCE_TOOL,
    WRITE_PILOT_EXPANSION_READINESS_TOOL,
]

WRITE_TOOLS = [*CONTRACTING_WRITE_TOOLS, *DELIVERY_WRITE_TOOLS]


async def handle_write_pilot_contract_packet(
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
        return f"Written: {path}\n\nPilot contract packet saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot contract packet: {type(e).__name__}: {e}"


async def handle_write_pilot_risk_clause_register(
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
        return f"Written: {path}\n\nPilot risk clause register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot risk clause register: {type(e).__name__}: {e}"


async def handle_write_pilot_go_live_readiness(
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
        return f"Written: {path}\n\nPilot go-live readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot go-live readiness: {type(e).__name__}: {e}"


async def handle_write_first_value_delivery_plan(
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
        return f"Written: {path}\n\nFirst value delivery plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing first value delivery plan: {type(e).__name__}: {e}"


async def handle_write_first_value_evidence(
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
        return f"Written: {path}\n\nFirst value evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing first value evidence: {type(e).__name__}: {e}"


async def handle_write_pilot_expansion_readiness(
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
        return f"Written: {path}\n\nPilot expansion readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pilot expansion readiness: {type(e).__name__}: {e}"
