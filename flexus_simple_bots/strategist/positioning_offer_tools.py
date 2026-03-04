import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_VALUE_PROPOSITION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_value_proposition",
    description="Write a completed value proposition artifact to a policy document.",
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

WRITE_OFFER_PACKAGING_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_offer_packaging",
    description="Write a completed offer packaging artifact to a policy document.",
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

WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_positioning_narrative_brief",
    description="Write a completed positioning narrative brief artifact to a policy document.",
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

WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_messaging_experiment_plan",
    description="Write a messaging experiment plan artifact to a policy document.",
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

WRITE_POSITIONING_TEST_RESULT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_positioning_test_result",
    description="Write a positioning test result artifact to a policy document.",
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

WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_positioning_claim_risk_register",
    description="Write a positioning claim risk register artifact to a policy document.",
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
    WRITE_VALUE_PROPOSITION_TOOL,
    WRITE_OFFER_PACKAGING_TOOL,
    WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL,
    WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL,
    WRITE_POSITIONING_TEST_RESULT_TOOL,
    WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL,
]


async def handle_write_value_proposition(
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
        return f"Written: {path}\n\nValue proposition saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing value proposition: {type(e).__name__}: {e}"


async def handle_write_offer_packaging(
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
        return f"Written: {path}\n\nOffer packaging saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing offer packaging: {type(e).__name__}: {e}"


async def handle_write_positioning_narrative_brief(
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
        return f"Written: {path}\n\nPositioning narrative brief saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning narrative brief: {type(e).__name__}: {e}"


async def handle_write_messaging_experiment_plan(
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
        return f"Written: {path}\n\nMessaging experiment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing messaging experiment plan: {type(e).__name__}: {e}"


async def handle_write_positioning_test_result(
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
        return f"Written: {path}\n\nPositioning test result saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning test result: {type(e).__name__}: {e}"


async def handle_write_positioning_claim_risk_register(
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
        return f"Written: {path}\n\nPositioning claim risk register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing positioning claim risk register: {type(e).__name__}: {e}"
