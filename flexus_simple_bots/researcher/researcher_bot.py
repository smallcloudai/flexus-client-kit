import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool

from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_shutdown
from flexus_simple_bots.researcher import researcher_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_researcher")

BOT_DIR = Path(__file__).parent
BOT_NAME = "researcher"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


def load_artifact_schemas() -> Dict[str, Any]:
    """Read JSON artifact schemas from each skill's SKILL.md at startup."""
    skills_dir = BOT_DIR / "skills"
    schemas: Dict[str, Any] = {}
    for skill_dir in sorted(d for d in skills_dir.iterdir() if not d.name.startswith("_")):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        md = skill_md.read_text(encoding="utf-8")
        m = re.search(r"```json\s*(\{.*?\})\s*```", md, re.DOTALL)
        if not m:
            continue
        parsed = json.loads(m.group(1))
        schemas.update(parsed)
    return schemas


ARTIFACT_SCHEMAS = load_artifact_schemas()
ARTIFACT_TYPES = sorted(ARTIFACT_SCHEMAS.keys())

TEMPLATE_IDEA_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="template_idea",
    description="Create idea document at /gtm/discovery/{idea_slug}/idea",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "text": {"type": "string"},
        },
        "required": ["idea_slug", "text"],
        "additionalProperties": False,
    },
)

TEMPLATE_HYPOTHESIS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="template_hypothesis",
    description="Create hypothesis document at /gtm/discovery/{idea_slug}/{hypothesis_slug}/hypothesis",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string"},
            "hypothesis_slug": {"type": "string"},
            "hypothesis": {"type": "object"},
            "text": {"type": "string"},
        },
        "required": ["idea_slug", "hypothesis_slug"],
        "additionalProperties": False,
    },
)

WRITE_ARTIFACT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_artifact",
    description="Write a structured artifact to the document store. Artifact type and schema are defined by the active skill.",
    parameters={
        "type": "object",
        "properties": {
            "artifact_type": {
                "type": "string",
                "enum": ARTIFACT_TYPES,
                "description": "Artifact type as specified by the active skill",
            },
            "path": {
                "type": "string",
                "description": "Document path, e.g. /signals/search-demand-2024-01-15",
            },
            "data": {
                "type": "object",
                "description": "Artifact content matching the schema for this artifact_type",
            },
        },
        "required": ["artifact_type", "path", "data"],
        "additionalProperties": False,
    },
)


def validate_path_kebab(path: str) -> str:
    """Validates that all segments of a path are kebab-case."""
    for segment in path.strip("/").split("/"):
        if segment and not all(c.islower() or c.isdigit() or c == "-" for c in segment):
            return f"Path segment '{segment}' must be kebab-case (lowercase, numbers, hyphens)"
    return ""


RESEARCHER_INTEGRATIONS = researcher_install.RESEARCHER_INTEGRATIONS

TOOLS = [
    WRITE_ARTIFACT_TOOL,
    TEMPLATE_IDEA_TOOL,
    TEMPLATE_HYPOTHESIS_TOOL,
    *[t for rec in RESEARCHER_INTEGRATIONS for t in rec.integr_tools],
]


async def researcher_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(RESEARCHER_INTEGRATIONS, rcx)
    pdoc_integration = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(WRITE_ARTIFACT_TOOL.name)
    async def _h_write_artifact(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        artifact_type = str(args.get("artifact_type", "")).strip()
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not artifact_type or not path or data is None:
            return "Error: artifact_type, path, and data are required."
        if artifact_type not in ARTIFACT_SCHEMAS:
            return f"Error: unknown artifact_type {artifact_type!r}. Must be one of: {', '.join(ARTIFACT_TYPES)}"
        doc = dict(data)
        doc["schema"] = ARTIFACT_SCHEMAS[artifact_type]
        await pdoc_integration.pdoc_overwrite(
            path,
            json.dumps(doc, ensure_ascii=False),
            fcall_untrusted_key=toolcall.fcall_untrusted_key,
        )
        return f"Written: {path}\n\nArtifact {artifact_type} saved."

    @rcx.on_tool_call(TEMPLATE_IDEA_TOOL.name)
    async def _h_template_idea(toolcall, args):
        idea_slug = str(args.get("idea_slug", "")).strip()
        text = str(args.get("text", "")).strip()
        if not idea_slug:
            return "Error: idea_slug required."
        if not text:
            return "Error: text required."
        if err := validate_path_kebab(idea_slug):
            return f"Error: {err}"
        try:
            idea_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"
        path = f"/gtm/discovery/{idea_slug}/idea"
        await pdoc_integration.pdoc_create(
            path,
            json.dumps(idea_doc, indent=2, ensure_ascii=False),
            fcall_untrusted_key=toolcall.fcall_untrusted_key,
        )
        return f"Written: {path}\n\nCreated idea document"

    @rcx.on_tool_call(TEMPLATE_HYPOTHESIS_TOOL.name)
    async def _h_template_hypothesis(toolcall, args):
        idea_slug = str(args.get("idea_slug", "")).strip()
        hypothesis_slug = str(args.get("hypothesis_slug", "")).strip()
        if not idea_slug:
            return "Error: idea_slug required."
        if not hypothesis_slug:
            return "Error: hypothesis_slug required."
        if err := validate_path_kebab(idea_slug):
            return f"Error: {err}"
        if err := validate_path_kebab(hypothesis_slug):
            return f"Error: {err}"
        hypothesis_data = args.get("hypothesis")
        if hypothesis_data is None:
            text = str(args.get("text", "")).strip()
            if not text:
                return "Error: either hypothesis or text must be provided."
            try:
                hypothesis_data = json.loads(text)
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON: {e}"
        if not isinstance(hypothesis_data, dict):
            return "Error: hypothesis must be an object."
        path = f"/gtm/discovery/{idea_slug}/{hypothesis_slug}/hypothesis"
        await pdoc_integration.pdoc_create(
            path,
            json.dumps({"hypothesis": hypothesis_data}, indent=2, ensure_ascii=False),
            fcall_untrusted_key=toolcall.fcall_untrusted_key,
        )
        return f"Written: {path}\n\nCreated hypothesis document"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=researcher_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=researcher_install.install,
    ))


if __name__ == "__main__":
    main()
