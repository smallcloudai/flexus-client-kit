import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_EXPERIMENT_CARD_DRAFT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_card_draft",
    description="Write a completed experiment card draft to a policy document. Call once per batch of experiment cards.",
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

WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_measurement_spec",
    description="Write a measurement spec for one experiment to a policy document.",
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

WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_backlog_prioritization",
    description="Write a prioritized experiment backlog to a policy document.",
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

WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_reliability_report",
    description="Write a reliability report for one experiment to a policy document.",
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

WRITE_EXPERIMENT_APPROVAL_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_approval",
    description="Write an experiment approval decision to a policy document.",
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

WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_experiment_stop_rule_evaluation",
    description="Write a stop-rule evaluation for a running experiment to a policy document.",
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
    WRITE_EXPERIMENT_CARD_DRAFT_TOOL,
    WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL,
    WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL,
    WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL,
    WRITE_EXPERIMENT_APPROVAL_TOOL,
    WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL,
]


async def handle_write_experiment_card_draft(
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
        return f"Written: {path}\n\nExperiment card draft saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment card draft: {type(e).__name__}: {e}"


async def handle_write_experiment_measurement_spec(
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
        return f"Written: {path}\n\nExperiment measurement spec saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment measurement spec: {type(e).__name__}: {e}"


async def handle_write_experiment_backlog_prioritization(
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
        return f"Written: {path}\n\nExperiment backlog prioritization saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment backlog prioritization: {type(e).__name__}: {e}"


async def handle_write_experiment_reliability_report(
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
        return f"Written: {path}\n\nExperiment reliability report saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment reliability report: {type(e).__name__}: {e}"


async def handle_write_experiment_approval(
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
        return f"Written: {path}\n\nExperiment approval saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment approval: {type(e).__name__}: {e}"


async def handle_write_experiment_stop_rule_evaluation(
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
        return f"Written: {path}\n\nExperiment stop rule evaluation saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing experiment stop rule evaluation: {type(e).__name__}: {e}"
