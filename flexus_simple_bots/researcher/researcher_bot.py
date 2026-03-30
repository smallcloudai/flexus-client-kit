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
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_researcher")

BOT_DIR = Path(__file__).parent
BOT_NAME = "researcher"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

RESEARCHER_ROOTDIR = Path(__file__).parent
RESEARCHER_SKILLS = ckit_skills.static_skills_find(RESEARCHER_ROOTDIR, shared_skills_allowlist="")
RESEARCHER_SETUP_SCHEMA = json.loads((RESEARCHER_ROOTDIR / "setup_schema.json").read_text())

RESEARCHER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    RESEARCHER_ROOTDIR,
    [
        "flexus_policy_document", "skills", "print_widget",
        "linkedin",
        "google_calendar",
        # "amazon",
        # "apollo",
        # "appstoreconnect",
        # "bing_webmaster",
        # "bombora",
        # "builtwith",
        # "calendly",
        # "capterra",
        # "cint",
        # "clearbit",
        # "coresignal",
        # "crunchbase",
        # "dataforseo",
        # "dovetail",
        # "ebay",
        # "event_registry",
        # "fireflies",
        # "g2",
        # "gdelt",
        # "glassdoor",
        # "gnews",
        # "gong",
        # "google_ads",
        # "google_play",
        # "google_search_console",
        # "google_shopping",
        # "hasdata",
        # "instagram",
        # "levelsfyi",
        # "linkedin_jobs",
        # "mediastack",
        # "newsapi",
        # "newscatcher",
        # "newsdata",
        # "outreach",
        # "oxylabs",
        # "pdl",
        # "perigon",
        # "pinterest",
        # "pipedrive",
        # "producthunt",
        # "prolific",
        # "qualtrics",
        # "reddit",
        # "salesforce",
        # "salesloft",
        # "sixsense",
        # "stackexchange",
        # "surveymonkey",
        # "theirstack",
        # "tiktok",
        # "trustpilot",
        # "typeform",
        # "userinterviews",
        # "usertesting",
        # "wappalyzer",
        # "wikimedia",
        # "x",
        # "yelp",
        # "youtube",
        # "zendesk",
        # "zendesk_sell",
        # "zoom",
    ],
    builtin_skills=RESEARCHER_SKILLS,
)


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


def validate_path_kebab(path: str) -> str:
    for segment in path.strip("/").split("/"):
        if segment and not all(c.islower() or c.isdigit() or c == "-" for c in segment):
            return f"Path segment '{segment}' must be kebab-case (lowercase, numbers, hyphens)"
    return ""


TOOLS = [
    WRITE_ARTIFACT_TOOL,
    TEMPLATE_IDEA_TOOL,
    TEMPLATE_HYPOTHESIS_TOOL,
    *[t for rec in RESEARCHER_INTEGRATIONS for t in rec.integr_tools],
]


async def researcher_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(RESEARCHER_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(RESEARCHER_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(WRITE_ARTIFACT_TOOL.name)
    async def _h_write_artifact(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        path = str(args.get("path", "")).strip()
        data = args.get("data")
        if not path or data is None:
            return "Error: path and data are required."
        await pdoc_integration.pdoc_overwrite(path, json.dumps(data, ensure_ascii=False), persona_id=rcx.persona.persona_id, fcall_untrusted_key=toolcall.fcall_untrusted_key)
        return f"Written: {path}"

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
        await pdoc_integration.pdoc_create(path, json.dumps(idea_doc, indent=2, ensure_ascii=False), persona_id=rcx.persona.persona_id, fcall_untrusted_key=toolcall.fcall_untrusted_key)
        return f"✍️ {path}\n\n✓ Created idea document"

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
            persona_id=rcx.persona.persona_id,
            fcall_untrusted_key=toolcall.fcall_untrusted_key,
        )
        return f"✍️ {path}\n\n✓ Created hypothesis document"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    from flexus_simple_bots.researcher import researcher_install
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
