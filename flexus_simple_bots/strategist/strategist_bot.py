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
from flexus_simple_bots.strategist import strategist_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_strategist")

BOT_DIR = Path(__file__).parent
BOT_NAME = "strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


def load_artifact_schemas() -> Dict[str, Any]:
    """Read JSON artifact schemas from each skill's SKILL.md; skip filling-* dirs (pipeline templates, not artifacts)."""
    skills_dir = BOT_DIR / "skills"
    schemas: Dict[str, Any] = {}
    for skill_dir in sorted(d for d in skills_dir.iterdir() if not d.name.startswith("filling-")):
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
                "description": "Document path, e.g. /experiments/cards/exp001-2024-01-15",
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

STRATEGIST_INTEGRATIONS = strategist_install.STRATEGIST_INTEGRATIONS

TOOLS = [
    WRITE_ARTIFACT_TOOL,
    *[t for rec in STRATEGIST_INTEGRATIONS for t in rec.integr_tools],
]


async def strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(STRATEGIST_INTEGRATIONS, rcx)
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
        bot_main_loop=strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=strategist_install.install,
    ))


if __name__ == "__main__":
    main()
