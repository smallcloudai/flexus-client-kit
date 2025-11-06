import asyncio
import json
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_slack
from flexus_simple_bots.profprobe import profprobe_install
from flexus_simple_bots.profprobe.integrations import survey_monkey
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_profprobe")

BOT_NAME = "profprobe"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

TOOLS = [
    fi_slack.SLACK_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    survey_monkey.CREATE_SURVEY_TOOL,
    survey_monkey.GET_RESPONSES_TOOL,
    survey_monkey.CONVERT_HYPOTHESIS_TOOL,
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
    try:
        await slack.join_channels()
        await slack.start_reactive()
    except Exception as e:
        logger.error(f"Slack is not available: {e}")

    pdoc_integration = fi_pdoc.IntegrationPdoc(fclient, rcx.persona.located_fgroup_id)

    surveymonkey_integration = None
    if setup.get("SURVEYMONKEY_ACCESS_TOKEN"):
        surveymonkey_integration = survey_monkey.IntegrationSurveyMonkey(
            access_token=setup["SURVEYMONKEY_ACCESS_TOKEN"],
            pdoc_integration=pdoc_integration
        )

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        await slack.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(fi_slack.SLACK_TOOL.name)
    async def toolcall_slack(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await slack.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(survey_monkey.CREATE_SURVEY_TOOL.name)
    async def toolcall_create_survey(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not surveymonkey_integration:
            return "Error: SurveyMonkey integration not configured. Please set SURVEYMONKEY_ACCESS_TOKEN in bot settings."
        try:
            return await surveymonkey_integration.create_survey(toolcall, model_produced_args)
        except Exception as e:
            logger.info(f"toolcall_create_survey error: {e}")
            return f"Error: {e}"

    @rcx.on_tool_call(survey_monkey.GET_RESPONSES_TOOL.name)
    async def toolcall_get_responses(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not surveymonkey_integration:
            return "Error: SurveyMonkey integration not configured. Please set SURVEYMONKEY_ACCESS_TOKEN in bot settings."
        try:
            return await surveymonkey_integration.get_responses(toolcall, model_produced_args)
        except Exception as e:
            logger.info(f"toolcall_get_responses error: {e}")
            return f"Error: {e}"

    @rcx.on_tool_call(survey_monkey.CONVERT_HYPOTHESIS_TOOL.name)
    async def toolcall_convert_hypothesis(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not surveymonkey_integration:
            return "Error: SurveyMonkey integration not configured. Please set SURVEYMONKEY_ACCESS_TOKEN in bot settings."
        try:
            return await surveymonkey_integration.convert_hypothesis_to_survey(toolcall, model_produced_args)
        except Exception as e:
            logger.info(f"toolcall_convert_hypothesis error: {e}")
            return f"Error: {e}"

    async def check_surveys():
        if not surveymonkey_integration or not setup.get("use_surveymonkey", True):
            return
        try:
            survey_list = await pdoc_integration.pdoc_list("/customer-research/unicorn-horn-car-hypotheses/")
            for item in survey_list:
                survey_name = item.path.split("/")[-1]
                doc = await pdoc_integration.pdoc_cat(item.path)
                content = doc.pdoc_content if isinstance(doc.pdoc_content, dict) else json.loads(doc.pdoc_content)
                meta = content.get("meta", {})
                if survey_id := meta.get("survey_id"):
                    if await surveymonkey_integration.check_survey_has_responses(survey_id):
                        content["meta"]["responses_processed"] = True
                        await pdoc_integration.pdoc_write(item.path, json.dumps(content, indent=2), None)
                        await ckit_kanban.bot_kanban_post_into_inbox(
                            fclient,
                            rcx.persona.persona_id,
                            f"Process survey results: {survey_name}",
                            json.dumps({
                                "instruction": f"Get survey results from SurveyMonkey survey_id: {survey_id} and save them to /customer-research/unicorn-horn-car-survey-results/{survey_name}",
                                "survey_id": survey_id,
                                "survey_name": survey_name,
                                "target_path": f"/customer-research/unicorn-horn-car-survey-results/{survey_name}"
                            }),
                            f"Survey {survey_name} has responses"
                        )
                        logger.info(f"Posted kanban task for completed survey {survey_name}")
        except Exception as e:
            logger.error(f"Error checking surveys: {e}", stack_info=True)

    try:
        last_survey_check = 0
        survey_check_interval = 300

        while not ckit_shutdown.shutdown_event.is_set():
            current_time = asyncio.get_event_loop().time()

            if current_time - last_survey_check > survey_check_interval:
                await check_surveys()
                last_survey_check = current_time

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
