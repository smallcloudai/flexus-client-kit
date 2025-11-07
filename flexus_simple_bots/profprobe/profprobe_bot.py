import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.profprobe import profprobe_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_profprobe")


BOT_NAME = "profprobe"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


POST_TEST_QUESTIONNAIRE = ckit_cloudtool.CloudTool(
    name="create_test_questionnaire",
    description="For test, you can write an empty questionnaire to /interview-test/",
    parameters={
        "type": "object",
        "properties": {
            "qfile": {"type": "string", "description": "Randomly choose q1 or q2"},
            "name": {"type": "string", "description": "Respondent name in kebab-case (e.g., john-doe)"},
        },
        "required": ["qfile", "name"],
    },
)

TOOLS = [
    POST_TEST_QUESTIONNAIRE,
    fi_slack.SLACK_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def profprobe_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(profprobe_install.profprobe_setup_schema, rcx.persona.persona_setup)

    slack = fi_slack.IntegrationSlack(
        fclient,
        rcx,
        SLACK_BOT_TOKEN=setup["SLACK_BOT_TOKEN"],
        SLACK_APP_TOKEN=setup["SLACK_APP_TOKEN"],
        should_join=setup["slack_should_join"],
    )

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.ws_root_group_id)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        await slack.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(POST_TEST_QUESTIONNAIRE.name)
    async def toolcall_post_test_questionnaire(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        qfile = model_produced_args.get("qfile", "")
        name = model_produced_args.get("name", "")

        if not qfile:
            return "Error: qfile required (q1 or q2)"
        if not name:
            return "Error: name required (kebab-case, e.g., john-doe)"

        p = f"/interview-test/{qfile}-{name}"

        Q1_QUESTIONS = [
            "Do you prefer your coffee black, with milk, or with long-term emotional stability?",
            "How many pillows do you really sleep with?",
            "When you hear the word \"commitment,\" do you think of Wi-Fi contracts or something scarier?",
            "Are you married, hypothetically speaking, or in practice?",
            "If a penguin handed you a ring, would you accept it, or ask about its tax residency first?",
        ]

        Q2_QUESTIONS = [
            "When the doorbell rings unexpectedly, do you: a) open it, b) hide, or c) move to another country?",
            "How often do you make eye contact with your reflection and immediately regret it?",
            "Are you married, or do you just tell people your cat's name when asked about your partner?",
            "If invited to a party, how many backup excuses do you prepare?",
            "On a scale from 1 to \"please email me instead,\" how do you feel about phone calls?",
        ]

        questions = Q1_QUESTIONS if qfile == "q1" else Q2_QUESTIONS

        interview_data = {
            "interview": {
                "respondent": name,
                "questionnaire": qfile.upper(),
                "section01": {
                    "title": f"Questions from {qfile.upper()}",
                }
            }
        }

        for idx, q_text in enumerate(questions, 1):
            q_key = f"question{idx:02d}"
            interview_data["interview"]["section01"][q_key] = {
                "q": q_text,
                "a": ""
            }

        await pdoc_integration.pdoc_write(p, json.dumps(interview_data, indent=2), ft_id=toolcall.ft_id)
        return f"✍🏻 {p}\n\n✓ Created empty questionnaire with {len(questions)} questions"

    @rcx.on_tool_call(fi_slack.SLACK_TOOL.name)
    async def toolcall_slack(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await slack.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    try:
        await slack.join_channels()
        await slack.start_reactive()

        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await slack.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=profprobe_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
