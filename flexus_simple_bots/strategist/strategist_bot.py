import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool

from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_skills
from flexus_client_kit import ckit_bot_version

logger = logging.getLogger("bot_strategist")

BOT_DIR = Path(__file__).parent
STRATEGIST_ROOTDIR = BOT_DIR
STRATEGIST_SKILLS = ckit_skills.static_skills_find(STRATEGIST_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")
STRATEGIST_SETUP_SCHEMA = json.loads((STRATEGIST_ROOTDIR / "setup_schema.json").read_text())
STRATEGIST_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    STRATEGIST_ROOTDIR,
    [
        "flexus_policy_document", "skills", "print_widget",
        "linkedin",
        # "chargebee",
        # "crunchbase",
        # "datadog",
        # "ga4",
        # "gnews",
        # "google_ads",
        # "launchdarkly",
        # "meta",
        # "mixpanel",
        # "optimizely",
        # "paddle",
        # "pipedrive",
        # "qualtrics",
        # "recurly",
        # "salesforce",
        # "segment",
        # "statsig",
        # "surveymonkey",
        # "typeform",
        # "zendesk",
    ],
    builtin_skills=STRATEGIST_SKILLS,
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
    WRITE_ARTIFACT_TOOL,
    *[t for rec in STRATEGIST_INTEGRATIONS for t in rec.integr_tools],
]


async def strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(STRATEGIST_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(STRATEGIST_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

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
    from flexus_simple_bots.strategist import strategist_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(ckit_bot_version.bot_name_from_file(__file__), bot_version), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=strategist_install.install,
    ))


if __name__ == "__main__":
    main()
