import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool

from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations.facebook.fi_facebook import IntegrationFacebook, FACEBOOK_TOOL
from flexus_simple_bots.executor import executor_install
from flexus_simple_bots.executor import experiment_execution
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_executor")

BOT_DIR = Path(__file__).parent
BOT_NAME = "executor"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


def load_artifact_schemas() -> Dict[str, Any]:
    """Read JSON artifact schemas from each skill's SKILL.md."""
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
                "description": "Document path, e.g. /campaigns/meta/q1-2024-pilot",
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

EXECUTOR_INTEGRATIONS = executor_install.EXECUTOR_INTEGRATIONS

TOOLS = [
    FACEBOOK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    experiment_execution.LAUNCH_EXPERIMENT_TOOL,
    WRITE_ARTIFACT_TOOL,
    *[t for rec in EXECUTOR_INTEGRATIONS for t in rec.integr_tools],
]


async def executor_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(executor_install.EXECUTOR_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(EXECUTOR_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]
    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    facebook_integration = IntegrationFacebook(fclient=fclient, rcx=rcx, ad_account_id="", pdoc_integration=pdoc_integration)
    experiment_integr = experiment_execution.IntegrationExperimentExecution(
        pdoc_integration=pdoc_integration,
        fclient=fclient,
        facebook_integration=facebook_integration,
    )

    @rcx.on_tool_call(FACEBOOK_TOOL.name)
    async def _h_facebook(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await facebook_integration.called_by_model(toolcall, args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def _h_mongo(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, args)

    @rcx.on_tool_call(experiment_execution.LAUNCH_EXPERIMENT_TOOL.name)
    async def _h_launch(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await experiment_integr.launch_experiment(toolcall, args)

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

    @rcx.on_updated_task
    async def _on_updated_task(t: ckit_kanban.FPersonaKanbanTaskOutput) -> None:
        experiment_integr.track_experiment_task(t)

    initial_tasks = await ckit_kanban.bot_get_all_tasks(fclient, rcx.persona.persona_id)
    for t in [x for x in initial_tasks if x.ktask_done_ts == 0]:
        experiment_integr.track_experiment_task(t)

    last_experiment_check = 0
    experiment_check_interval = 3600

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
            current_time = time.time()
            if current_time - last_experiment_check > experiment_check_interval:
                await experiment_integr.update_active_experiments()
                last_experiment_check = current_time
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=executor_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=executor_install.install,
    ))


if __name__ == "__main__":
    main()
