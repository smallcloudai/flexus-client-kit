import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_PRICE_CORRIDOR_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_preliminary_price_corridor",
    description="Write a preliminary price corridor artifact to a policy document. Call once after modeling corridor from research.",
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

WRITE_PRICE_SENSITIVITY_CURVE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_price_sensitivity_curve",
    description="Write a price sensitivity curve artifact to a policy document. Call after completing WTP analysis.",
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

WRITE_PRICING_ASSUMPTION_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pricing_assumption_register",
    description="Write a pricing assumption register artifact to a policy document. Call after cataloging and assessing assumptions.",
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

WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pricing_commitment_evidence",
    description="Write a pricing commitment evidence artifact to a policy document. Call once per evidence collection run.",
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

WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_validated_price_hypothesis",
    description="Write a validated price hypothesis artifact to a policy document. Call once per hypothesis tested.",
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

WRITE_PRICING_GO_NO_GO_GATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_pricing_go_no_go_gate",
    description="Write a pricing go/no-go gate artifact to a policy document. Call once after evaluating all commitment evidence.",
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
    WRITE_PRICE_CORRIDOR_TOOL,
    WRITE_PRICE_SENSITIVITY_CURVE_TOOL,
    WRITE_PRICING_ASSUMPTION_REGISTER_TOOL,
    WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL,
    WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL,
    WRITE_PRICING_GO_NO_GO_GATE_TOOL,
]


async def handle_write_price_corridor(
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
        return f"Written: {path}\n\nPrice corridor saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing price corridor: {type(e).__name__}: {e}"


async def handle_write_price_sensitivity_curve(
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
        return f"Written: {path}\n\nPrice sensitivity curve saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing price sensitivity curve: {type(e).__name__}: {e}"


async def handle_write_pricing_assumption_register(
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
        return f"Written: {path}\n\nPricing assumption register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing assumption register: {type(e).__name__}: {e}"


async def handle_write_pricing_commitment_evidence(
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
        return f"Written: {path}\n\nPricing commitment evidence saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing commitment evidence: {type(e).__name__}: {e}"


async def handle_write_validated_price_hypothesis(
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
        return f"Written: {path}\n\nValidated price hypothesis saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing validated price hypothesis: {type(e).__name__}: {e}"


async def handle_write_pricing_go_no_go_gate(
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
        return f"Written: {path}\n\nPricing go/no-go gate saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing pricing go/no-go gate: {type(e).__name__}: {e}"
