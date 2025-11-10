import asyncio
import logging
import json
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.productman import productman_install
from flexus_simple_bots.productman import productman_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_productman")


BOT_NAME = "productman"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


IDEA_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_idea",
    description="Create idea file in pdoc. Ideas are the top-level concept, with multiple hypotheses exploring different customer segments or approaches. Path format: /customer-research/{idea-name}",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write idea. Should be /customer-research/{idea-name} using kebab-case: '/customer-research/unicorn-horn-car-idea'"
            },
            "text": {
                "type": "string",
                "description": "JSON text of the idea document. Must match the structure of example_idea with exact keys. Only 'q' values can be translated."
            },
        },
        "required": ["path", "text"],
    },
)

HYPOTHESIS_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_hypothesis",
    description="Create hypothesis file in pdoc. Hypotheses explore specific customer segments or approaches for an idea. Path format: /customer-research/{idea-name}-hypotheses/{hypothesis-name}",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write hypothesis, such as '/customer-research/unicorn-horn-car-hypotheses/social-media-influencers'"
            },
            "text": {
                "type": "string",
                "description": "JSON text of the hypothesis document. Must match the structure of example_hypothesis with exact keys. Only 'q' and 'title' values can be translated."
            },
        },
        "required": ["path", "text"],
    },
)

TOOLS = [
    IDEA_TEMPLATE_TOOL,
    HYPOTHESIS_TEMPLATE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def productman_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(productman_install.productman_setup_schema, rcx.persona.persona_setup)

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.ws_root_group_id)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

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

    @rcx.on_tool_call(IDEA_TEMPLATE_TOOL.name)
    async def toolcall_idea_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        text = model_produced_args.get("text", "")
        if not path:
            return "Error: path required"
        if not text:
            return "Error: text required"
        if not path.startswith("/customer-research/"):
            return "Error: path must start with /customer-research/ (e.g. /customer-research/my-product-idea)"
        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'unicorn-horn-car-idea'"

        try:
            idea_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"

        validation_error = validate_idea_structure(idea_doc, productman_prompts.example_idea)
        if validation_error:
            return f"Error: Structure validation failed: {validation_error}"

        await pdoc_integration.pdoc_create(path, json.dumps(idea_doc, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created idea at {path}")
        return f"✍🏻 {path}\n\n✓ Created idea document"

    @rcx.on_tool_call(HYPOTHESIS_TEMPLATE_TOOL.name)
    async def toolcall_hypothesis_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        text = model_produced_args.get("text", "")
        if not path:
            return "Error: path required"
        if not text:
            return "Error: text required"
        if not path.startswith("/customer-research/"):
            return "Error: path must start with /customer-research/ (e.g. /customer-research/my-idea-hypotheses/segment-name)"
        if "-hypotheses/" not in path:
            return "Error: hypothesis path must include '-hypotheses/' (e.g. /customer-research/unicorn-horn-car-hypotheses/social-media-influencers)"
        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'social-media-influencers'"

        try:
            hypothesis_doc = json.loads(text)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON: {e}"

        validation_error = validate_idea_structure(hypothesis_doc, productman_prompts.example_hypothesis)
        if validation_error:
            return f"Error: Structure validation failed: {validation_error}"

        await pdoc_integration.pdoc_create(path, json.dumps(hypothesis_doc, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created hypothesis at {path}")
        return f"✍🏻 {path}\n\n✓ Created hypothesis document for specific customer segment"

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=productman_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
