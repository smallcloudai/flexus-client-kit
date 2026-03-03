import json
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

WRITE_INTERVIEW_INSTRUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_interview_instrument",
    description="Write a completed interview instrument to a policy document.",
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

WRITE_SURVEY_INSTRUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_survey_instrument",
    description="Write a completed survey instrument to a policy document.",
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

WRITE_INSTRUMENT_READINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_discovery_instrument_readiness",
    description="Write a discovery instrument readiness assessment to a policy document.",
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

WRITE_TOOLS_INSTRUMENT = [
    WRITE_INTERVIEW_INSTRUMENT_TOOL,
    WRITE_SURVEY_INSTRUMENT_TOOL,
    WRITE_INSTRUMENT_READINESS_TOOL,
]


# =============================================================================
# =============================================================================

WRITE_RECRUITMENT_PLAN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_participant_recruitment_plan",
    description="Write a participant recruitment plan to a policy document.",
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

WRITE_RECRUITMENT_FUNNEL_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_recruitment_funnel_snapshot",
    description="Write a recruitment funnel snapshot to a policy document.",
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

WRITE_RECRUITMENT_COMPLIANCE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_recruitment_compliance_quality",
    description="Write a recruitment compliance quality assessment to a policy document.",
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

WRITE_TOOLS_RECRUITMENT = [
    WRITE_RECRUITMENT_PLAN_TOOL,
    WRITE_RECRUITMENT_FUNNEL_TOOL,
    WRITE_RECRUITMENT_COMPLIANCE_TOOL,
]


# =============================================================================
# =============================================================================

WRITE_INTERVIEW_CORPUS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_interview_corpus",
    description="Write an interview corpus to a policy document after coding all sessions.",
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

WRITE_JTBD_OUTCOMES_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_jtbd_outcomes",
    description="Write a JTBD outcomes artifact to a policy document after synthesizing interview evidence.",
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

WRITE_EVIDENCE_QUALITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_discovery_evidence_quality",
    description="Write a discovery evidence quality assessment to a policy document.",
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

WRITE_TOOLS_INTERVIEW = [
    WRITE_INTERVIEW_CORPUS_TOOL,
    WRITE_JTBD_OUTCOMES_TOOL,
    WRITE_EVIDENCE_QUALITY_TOOL,
]

WRITE_TOOLS = [
    *WRITE_TOOLS_INSTRUMENT,
    *WRITE_TOOLS_RECRUITMENT,
    *WRITE_TOOLS_INTERVIEW,
]


# =============================================================================
# WRITE HANDLERS
# =============================================================================

async def handle_write_interview_instrument(
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
        return f"Written: {path}\n\nInterview instrument saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing interview instrument: {type(e).__name__}: {e}"


async def handle_write_survey_instrument(
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
        return f"Written: {path}\n\nSurvey instrument saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing survey instrument: {type(e).__name__}: {e}"


async def handle_write_instrument_readiness(
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
        return f"Written: {path}\n\nInstrument readiness saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing instrument readiness: {type(e).__name__}: {e}"


async def handle_write_recruitment_plan(
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
        return f"Written: {path}\n\nRecruitment plan saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment plan: {type(e).__name__}: {e}"


async def handle_write_recruitment_funnel(
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
        return f"Written: {path}\n\nRecruitment funnel snapshot saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment funnel snapshot: {type(e).__name__}: {e}"


async def handle_write_recruitment_compliance(
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
        return f"Written: {path}\n\nRecruitment compliance quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing recruitment compliance quality: {type(e).__name__}: {e}"


async def handle_write_interview_corpus(
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
        return f"Written: {path}\n\nInterview corpus saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing interview corpus: {type(e).__name__}: {e}"


async def handle_write_jtbd_outcomes(
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
        return f"Written: {path}\n\nJTBD outcomes saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing JTBD outcomes: {type(e).__name__}: {e}"


async def handle_write_evidence_quality(
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
        return f"Written: {path}\n\nDiscovery evidence quality saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing discovery evidence quality: {type(e).__name__}: {e}"
