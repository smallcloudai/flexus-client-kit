import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit import ckit_bot_version

logger = logging.getLogger("bot_executor")

BOT_DIR = Path(__file__).parent
BOT_NAME = "executor"

EXECUTOR_ROOTDIR = Path(__file__).parent
EXECUTOR_SKILLS = [
    s for s in ckit_skills.static_skills_find(EXECUTOR_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")
    if s != "botticelli"
]
EXECUTOR_SETUP_SCHEMA = json.loads((EXECUTOR_ROOTDIR / "setup_schema.json").read_text())
EXECUTOR_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    EXECUTOR_ROOTDIR,
    [
        "flexus_policy_document", "skills", "print_widget",
        "linkedin",
        "facebook[campaign, adset, ad, account]",
        "google_calendar",
    ],
    builtin_skills=EXECUTOR_SKILLS,
)

WRITE_ARTIFACT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="write_artifact",
    description="Write a structured artifact to the document store. Path and data shape are defined by the active skill.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Document path as specified by the active skill",
            },
            "data": {
                "type": "object",
                "description": "Artifact content as specified by the active skill",
            },
        },
        "required": ["path", "data"],
        "additionalProperties": False,
    },
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    WRITE_ARTIFACT_TOOL,
    *[t for rec in EXECUTOR_INTEGRATIONS for t in rec.integr_tools],
]


async def executor_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(EXECUTOR_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(EXECUTOR_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def _h_mongo(toolcall, args):
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, args)

    @rcx.on_tool_call(WRITE_ARTIFACT_TOOL.name)
    async def _h_write_artifact(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        await pdoc_integration.pdoc_overwrite(path, json.dumps(data, ensure_ascii=False), persona_id=rcx.persona.persona_id, fcall_untrusted_key=toolcall.fcall_untrusted_key)
        return f"Written: {path}"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    from flexus_simple_bots.executor import executor_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, bot_version), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        bot_main_loop=executor_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=executor_install.install,
    ))


if __name__ == "__main__":
    main()
