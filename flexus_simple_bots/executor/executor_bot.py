import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.executor import executor_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_executor")

BOT_DIR = Path(__file__).parent
BOT_NAME = "executor"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


EXECUTOR_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    executor_install.EXECUTOR_ROOTDIR,
    [
        "flexus_policy_document", "skills", "print_widget",
        "linkedin", "facebook[campaign, adset, ad, account]",
        "calendly", "chargebee", "crossbeam", "delighted", "docusign",
        "fireflies", "ga4", "gong", "google_ads", "google_calendar",
        "meta", "mixpanel", "paddle", "pandadoc", "partnerstack",
        "pipedrive", "recurly", "salesforce", "surveymonkey", "typeform",
        "x_ads", "zendesk", "zoom",
    ],
    builtin_skills=executor_install.EXECUTOR_SKILLS,
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
    setup = ckit_bot_exec.official_setup_mixing_procedure(executor_install.EXECUTOR_SETUP_SCHEMA, rcx.persona.persona_setup)
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
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        await pdoc_integration.pdoc_overwrite(path, json.dumps(data, ensure_ascii=False), fuser_id)
        return f"Written: {path}"

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
        bot_main_loop=executor_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=executor_install.install,
    ))


if __name__ == "__main__":
    main()
