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
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_productman")


BOT_NAME = "productman"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


IDEA_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_idea",
    description="Create skeleton idea file in pdoc. Ideas are the top-level concept, with multiple hypotheses exploring different customer segments or approaches. Path format: /customer-research/{idea-name}",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write idea template. Should be /customer-research/{idea-name} using kebab-case: '/customer-research/unicorn-horn-car-idea'"
            },
        },
        "required": ["path"],
    },
)

HYPOTHESIS_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    name="template_hypothesis",
    description="Create skeleton hypothesis file in pdoc. Hypotheses explore specific customer segments or approaches for an idea. Path format: /customer-research/{idea-name}-hypotheses/{hypothesis-name}",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where to write hypothesis template, such as '/customer-research/unicorn-horn-car-hypotheses/social-media-influencers'"
            },
        },
        "required": ["path"],
    },
)

TOOLS = [
    IDEA_TEMPLATE_TOOL,
    HYPOTHESIS_TEMPLATE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def productman_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(productman_install.productman_setup_schema, rcx.persona.persona_setup)

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.located_fgroup_id)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(IDEA_TEMPLATE_TOOL.name)
    async def toolcall_idea_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        if not path:
            return "Error: path required"
        if not path.startswith("/customer-research/"):
            return "Error: path must start with /customer-research/ (e.g. /customer-research/my-product-idea)"
        path_segments = path.strip("/").split("/")
        for segment in path_segments:
            if not segment:
                continue
            if not all(c.islower() or c.isdigit() or c == "-" for c in segment):
                return f"Error: Path segment '{segment}' must use kebab-case (lowercase letters, numbers, hyphens only). Example: 'unicorn-horn-car-idea'"

        skeleton = {
            "idea": {
                "meta": {
                    "author": "",
                    "date": "",
                    "status": "in_progress"
                },
                "section01": {
                    "section_title": "Idea Summary",
                    "question01": {
                        "q": "What is the idea in one sentence?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What problem does this solve?",
                        "a": ""
                    },
                    "question03": {
                        "q": "Who is the target audience?",
                        "a": ""
                    },
                    "question04": {
                        "q": "What value do you provide?",
                        "a": ""
                    }
                },
                "section02": {
                    "section_title": "Constraints & Context",
                    "question01": {
                        "q": "What constraints exist (budget, time, resources)?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What observations or evidence support this idea?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What are the key assumptions?",
                        "a": ""
                    },
                    "question04": {
                        "q": "What are the known risks?",
                        "a": ""
                    }
                }
            }
        }

        await pdoc_integration.pdoc_write(path, json.dumps(skeleton, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created idea template at {path}")
        return f"✍🏻 {path}\n\n✓ Created idea template with structured Q&A format"

    @rcx.on_tool_call(HYPOTHESIS_TEMPLATE_TOOL.name)
    async def toolcall_hypothesis_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        path = model_produced_args.get("path", "")
        if not path:
            return "Error: path required"
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

        skeleton = {
            "hypothesis": {
                "meta": {
                    "author": "",
                    "date": "",
                },
                "section01": {
                    "section_title": "Ideal Customer Profile",
                    "question01": {
                        "q": "Who are the clients?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What do they want to accomplish?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What can't they do today?",
                        "a": ""
                    },
                    "question04": {
                        "q": "Why can't they do it?",
                        "a": ""
                    }
                },
                "section02": {
                    "section_title": "Customer Context",
                    "question01": {
                        "q": "Where do they hang out (channels)?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What are their pains and frustrations?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What outcomes do they desire?",
                        "a": ""
                    },
                    "question04": {
                        "q": "Geography and languages?",
                        "a": ""
                    }
                },
                "section03": {
                    "section_title": "Solution Hypothesis",
                    "question01": {
                        "q": "What is the minimum viable solution for this segment?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What value metric matters most to them?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What would make them choose this over alternatives?",
                        "a": ""
                    }
                },
                "section04": {
                    "section_title": "Validation Strategy",
                    "question01": {
                        "q": "How can we test this hypothesis quickly?",
                        "a": ""
                    },
                    "question02": {
                        "q": "What evidence would prove/disprove this?",
                        "a": ""
                    },
                    "question03": {
                        "q": "What is the success metric?",
                        "a": ""
                    }
                }
            }
        }

        await pdoc_integration.pdoc_write(path, json.dumps(skeleton, indent=2), toolcall.fcall_ft_id)
        logger.info(f"Created hypothesis template at {path}")
        return f"✍🏻 {path}\n\n✓ Created hypothesis template for specific customer segment"

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
