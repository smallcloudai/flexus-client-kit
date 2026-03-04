import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_CREATIVE_VARIANT_PACK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_creative_variant_pack",
    description="Write a completed creative variant pack to a policy document. Call once per creative production run.",
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

WRITE_CREATIVE_ASSET_MANIFEST_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_creative_asset_manifest",
    description="Write a creative asset manifest tracking QA status across all assets for a variant pack.",
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

WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_creative_claim_risk_register",
    description="Write a claim risk register documenting substantiation status for all creative claims.",
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

WRITE_PAID_CHANNEL_TEST_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_paid_channel_test_plan",
    description="Write a paid channel test plan before launching a campaign. One plan per platform per test.",
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

WRITE_PAID_CHANNEL_RESULT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_paid_channel_result",
    description="Write paid channel test results after a campaign run. Includes decision and next step.",
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

WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_paid_channel_budget_guardrail",
    description="Write a budget guardrail record documenting planned vs actual spend and any breaches.",
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
    WRITE_CREATIVE_VARIANT_PACK_TOOL,
    WRITE_CREATIVE_ASSET_MANIFEST_TOOL,
    WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL,
    WRITE_PAID_CHANNEL_TEST_PLAN_TOOL,
    WRITE_PAID_CHANNEL_RESULT_TOOL,
    WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL,
]


async def handle_write_creative_variant_pack(
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
        return f"Written: {path}\n\nCreative variant pack saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative variant pack: {type(e).__name__}: {e}"


async def handle_write_creative_asset_manifest(
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
        return f"Written: {path}\n\nCreative asset manifest saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative asset manifest: {type(e).__name__}: {e}"


async def handle_write_creative_claim_risk_register(
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
        return f"Written: {path}\n\nCreative claim risk register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing creative claim risk register: {type(e).__name__}: {e}"


async def handle_write_paid_channel_test_plan(
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
        return f"Written: {path}\n\nPaid channel test plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel test plan: {type(e).__name__}: {e}"


async def handle_write_paid_channel_result(
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
        return f"Written: {path}\n\nPaid channel result saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel result: {type(e).__name__}: {e}"


async def handle_write_paid_channel_budget_guardrail(
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
        return f"Written: {path}\n\nPaid channel budget guardrail saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing paid channel budget guardrail: {type(e).__name__}: {e}"
