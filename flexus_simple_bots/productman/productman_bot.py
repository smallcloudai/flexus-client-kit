import asyncio
import logging
import json
import os
import time
from typing import Dict, Any
from pathlib import Path

from flexus_client_kit import ckit_client, ckit_kanban
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.productman import productman_install
from flexus_simple_bots.productman import productman_prompts
from flexus_simple_bots.productman.integrations import survey_research
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_productman")


BOT_NAME = "productman"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


IDEA_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="template_idea",
    description="Create idea document at /gtm/discovery/{idea_slug}/idea",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {
                "type": "string",
                "description": "Idea name in kebab-case, 2-4 words (e.g. 'dental-samples', 'unicorn-horn-car')",
                "order": 1
            },
            "text": {
                "type": "string",
                "description": "JSON matching example_idea structure. Only 'q' values can be translated.",
                "order": 2
            },
        },
        "required": ["idea_slug", "text"],
    },
)

HYPOTHESIS_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="template_hypothesis",
    description="Create hypothesis document at /gtm/discovery/{idea_slug}/{hypothesis_slug}/hypothesis",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {
                "type": "string",
                "description": "Parent idea slug (e.g. 'unicorn-horn-car')",
                "order": 1
            },
            "hypothesis_slug": {
                "type": "string",
                "description": "Hypothesis name in kebab-case, 2-4 words capturing customer segment (e.g. 'social-influencers')",
                "order": 2
            },
            "text": {
                "type": "string",
                "description": "JSON matching example_hypothesis structure. Only 'q' and 'title' can be translated.",
                "order": 3
            },
        },
        "required": ["idea_slug", "hypothesis_slug", "text"],
    },
)

VERIFY_IDEA_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="verify_idea",
    description="Launch subchat to rate idea as PASS/PASS-WITH-WARNINGS/FAIL per question.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {
                "type": "string",
                "description": "Idea slug (e.g. 'dental-samples')",
                "order": 1
            },
            "language": {
                "type": "string",
                "description": "Language for comments (same as conversation language)",
                "order": 2
            },
        },
        "required": ["idea_slug", "language"],
    },
)

TOOLS_VERIFY_SUBCHAT = [
    fi_pdoc.POLICY_DOCUMENT_TOOL
]

TOOLS_SURVEY = [
    survey_research.SURVEY_RESEARCH_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL
]

TOOLS_DEFAULT = [
    IDEA_TEMPLATE_TOOL,
    HYPOTHESIS_TEMPLATE_TOOL,
    VERIFY_IDEA_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]

TOOLS_ALL = [
    *TOOLS_DEFAULT,
    survey_research.SURVEY_RESEARCH_TOOL
]




async def productman_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(productman_install.productman_setup_schema, rcx.persona.persona_setup)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    survey_research_integration = survey_research.IntegrationSurveyResearch(
        surveymonkey_token=os.getenv("SURVEYMONKEY_ACCESS_TOKEN", ""),
        prolific_token=os.getenv("PROLIFIC_API_TOKEN", ""),
        pdoc_integration=pdoc_integration,
        fclient=fclient
    )

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        survey_research_integration.track_survey_task(t)

    def validate_idea_structure(provided: Dict, expected: Dict, path: str = "root") -> str:
        if type(provided) != type(expected):
            return f"Type mismatch at {path}: expected {type(expected).__name__}, got {type(provided).__name__}"
        if isinstance(expected, dict):
            expected_keys = set(expected.keys())
            provided_keys = set(provided.keys())
            if expected_keys != provided_keys:
                missing = expected_keys - provided_keys
                extra = provided_keys - expected_keys
                errors = []
                if missing:
                    errors.append(f"missing keys: {missing}")
                if extra:
                    errors.append(f"unexpected keys: {extra}")
                return f"Key mismatch at {path}: {', '.join(errors)}"
            for key in expected_keys:
                if key == "q":
                    continue
                if key == "a":
                    continue
                if key == "title":
                    continue
                error = validate_idea_structure(provided[key], expected[key], f"{path}.{key}")
                if error:
                    return error
        return ""

    def validate_path_kebab(path: str) -> str:
        for segment in path.strip("/").split("/"):
            if segment and not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Path segment '{segment}' must be kebab-case (lowercase, numbers, hyphens)"
        return ""

    @rcx.on_tool_call(IDEA_TEMPLATE_TOOL.name)
    async def toolcall_idea_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        idea_slug = model_produced_args.get("idea_slug", "")
        text = model_produced_args.get("text", "")
        if not idea_slug:
            return "Error: idea_slug required"
        if not text:
            return "Error: text required"
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(fclient, toolcall, Path(__file__).read_text())
        if err := validate_path_kebab(idea_slug):
            return f"Error: idea_slug must be kebab-case: {err}"

        try:
            idea_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"

        validation_error = validate_idea_structure(idea_doc, productman_prompts.example_idea)
        if validation_error:
            return f"Error: {validation_error}"

        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        path = f"/gtm/discovery/{idea_slug}/idea"

        await pdoc_integration.pdoc_create(path, json.dumps(idea_doc, indent=2), fuser_id)
        logger.info(f"Created idea at {path}")
        return f"✍️ {path}\n\n✓ Created idea document"

    @rcx.on_tool_call(HYPOTHESIS_TEMPLATE_TOOL.name)
    async def toolcall_hypothesis_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        idea_slug = model_produced_args.get("idea_slug", "")
        hypothesis_slug = model_produced_args.get("hypothesis_slug", "")
        text = model_produced_args.get("text", "")
        if not idea_slug:
            return "Error: idea_slug required"
        if not hypothesis_slug:
            return "Error: hypothesis_slug required"
        if not text:
            return "Error: text required"
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(fclient, toolcall, Path(__file__).read_text())
        if err := validate_path_kebab(idea_slug):
            return f"Error: idea_slug must be kebab-case: {err}"
        if err := validate_path_kebab(hypothesis_slug):
            return f"Error: hypothesis_slug must be kebab-case: {err}"

        try:
            hypothesis_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"

        validation_error = validate_idea_structure(hypothesis_doc, productman_prompts.example_hypothesis)
        if validation_error:
            return f"Error: {validation_error}"

        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        path = f"/gtm/discovery/{idea_slug}/{hypothesis_slug}/hypothesis"

        await pdoc_integration.pdoc_create(path, json.dumps(hypothesis_doc, indent=2), fuser_id)
        logger.info(f"Created hypothesis at {path}")
        return f"✍️ {path}\n\n✓ Created hypothesis document"

    @rcx.on_tool_call(VERIFY_IDEA_TOOL.name)
    async def toolcall_verify_idea(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        idea_slug = model_produced_args.get("idea_slug", "")
        language = model_produced_args.get("language", "")
        if not idea_slug:
            return "Error: idea_slug required"
        if not language:
            return "Error: language required"
        if err := validate_path_kebab(idea_slug):
            return f"Error: idea_slug must be kebab-case: {err}"

        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(fclient, toolcall, Path(__file__).read_text())

        path = f"/gtm/discovery/{idea_slug}/idea"

        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="productman_verify_idea",
            persona_id=rcx.persona.persona_id,
            first_question=[f"Rate this idea document in {language}:\n{path}"],
            first_calls=["null"],
            title=[f"Verifying Idea {idea_slug}"],
            fcall_id=toolcall.fcall_id,
            fexp_name="criticize_idea",
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(survey_research.SURVEY_RESEARCH_TOOL.name)
    async def toolcall_survey(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await survey_research_integration.handle_survey_research(toolcall, model_produced_args)

    initial_tasks = await ckit_kanban.bot_get_all_tasks(fclient, rcx.persona.persona_id)
    active_tasks = [t for t in initial_tasks if t.ktask_done_ts == 0]
    for t in active_tasks:
        survey_research_integration.track_survey_task(t)
    logger.info(f"Initialized survey tracking for {len(active_tasks)} active tasks")

    last_survey_update = 0
    survey_update_interval = 60

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

            current_time = time.time()
            if current_time - last_survey_update > survey_update_interval:
                await survey_research_integration.update_active_surveys(
                    fclient,
                    survey_research_integration.update_task_survey_status
                )
                last_survey_update = current_time

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=productman_main_loop,
        inprocess_tools=TOOLS_ALL,
        scenario_fn=scenario_fn,
        install_func=productman_install.install,
    ))


if __name__ == "__main__":
    main()
