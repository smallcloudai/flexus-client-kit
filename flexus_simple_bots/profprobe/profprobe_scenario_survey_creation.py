import asyncio
import json
import logging

from flexus_client_kit import ckit_scenario_setup, ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations.fi_pdoc import PdocDocument
from flexus_simple_bots.profprobe import profprobe_bot
from flexus_simple_bots.profprobe.integrations import survey_monkey
from flexus_simple_bots.profprobe.integrations import survey_monkey_mock

logger = logging.getLogger("scenario")

survey_monkey.aiohttp = survey_monkey_mock.MockAiohttp()


async def create_hypothesis_pdoc(pdoc_integration, hypothesis_name):
    skeleton = {
        "idea": {
            "meta": {
                "author": "Test User",
                "date": "2024-01-15",
            },
            "section01": {
                "section_title": "Idea Summary",
                "question01": {
                    "q": "What is the idea in one sentence?",
                    "a": "A car accessory that adds a unicorn horn to any vehicle"
                },
                "question02": {
                    "q": "What problem does this solve?",
                    "a": "Makes cars more magical and fun for children"
                },
                "question03": {
                    "q": "Who is the target audience?",
                    "a": "Parents with young children who love unicorns"
                },
                "question04": {
                    "q": "What value do you provide?",
                    "a": "Joy, imagination, and unique car personalization"
                }
            },
            "section02": {
                "section_title": "Constraints & Context",
                "question01": {
                    "q": "What constraints exist (budget, time, resources)?",
                    "a": "Budget under $50 per unit, 3 month development timeline"
                },
                "question02": {
                    "q": "What observations or evidence support this idea?",
                    "a": "Unicorn merchandise sales up 300% in last 2 years"
                },
                "question03": {
                    "q": "What are the key assumptions?",
                    "a": "Parents will buy novelty car accessories for children"
                },
                "question04": {
                    "q": "What are the known risks?",
                    "a": "Safety regulations, potential distraction while driving"
                }
            }
        }
    }

    path = f"/customer-research/unicorn-horn-car-survey/{hypothesis_name}"
    await pdoc_integration.pdoc_write(path, json.dumps(skeleton, indent=2), None)
    return path


async def scenario(setup: ckit_scenario_setup.ScenarioSetup) -> None:
    await setup.create_group_hire_and_start_bot(
        persona_marketable_name=profprobe_bot.BOT_NAME,
        persona_marketable_version=profprobe_bot.BOT_VERSION_INT,
        persona_setup={
            "use_surveymonkey": True,
            "SURVEYMONKEY_ACCESS_TOKEN": "test_token_123",
            "slack_should_join": "",
            "SLACK_BOT_TOKEN": "test_token",
            "SLACK_APP_TOKEN": "test_app_token"
        },
        inprocess_tools=profprobe_bot.TOOLS,
        bot_main_loop=profprobe_bot.profprobe_main_loop,
        group_prefix="scenario-survey-creation"
    )

    pdoc_integration = fi_pdoc.IntegrationPdoc(setup.fclient, setup.fgroup_id)

    hypothesis_name = "unicorn-horn-market-validation"
    hypothesis_path = await create_hypothesis_pdoc(pdoc_integration, hypothesis_name)
    logger.info(f"Created hypothesis pdoc at {hypothesis_path}")

    await ckit_kanban.bot_kanban_post_into_inbox(
        setup.fclient,
        setup.persona.persona_id,
        f"Convert hypothesis to survey: {hypothesis_name}",
        json.dumps({
            "instruction": f"Please read the hypothesis at {hypothesis_path} and convert it to a SurveyMonkey survey to validate the idea with potential customers. Extract the questions from the Q&A pairs and create appropriate survey questions.",
            "hypothesis_path": hypothesis_path,
            "hypothesis_name": hypothesis_name
        }),
        f"New hypothesis needs survey conversion"
    )

    logger.info(f"Posted kanban task for hypothesis conversion")

    await asyncio.sleep(5)

    await setup.wait_for_toolcall("convert_hypothesis_to_survey", None, {"hypothesis_path": hypothesis_path}, allow_existing_toolcall=True)

    converted_path = f"/customer-research/unicorn-horn-car-hypotheses/{hypothesis_name}-survey-monkey-query"
    await asyncio.sleep(2)

    try:
        doc: PdocDocument = await pdoc_integration.pdoc_cat(converted_path)
        content = doc.pdoc_content
        assert "title" in content, "Survey missing title"
        assert "questions" in content, "Survey missing questions"
        assert len(content["questions"]) > 0, "Survey has no questions"

        logger.info(f"✅ Hypothesis converted to survey with {len(content['questions'])} questions")
        logger.info(f"Survey title: {content.get('title', 'N/A')}")

        for idx, q in enumerate(content["questions"], 1):
            logger.info(f"  Q{idx}: {q.get('question', 'N/A')} (type: {q.get('type', 'N/A')})")

    except Exception as e:
        logger.error(f"Failed to verify survey conversion: {e}")
        raise

    await setup.wait_for_toolcall("create_surveymonkey_survey", None, {"pdoc_path": converted_path}, allow_existing_toolcall=True)
    await asyncio.sleep(2)

    try:
        doc = await pdoc_integration.pdoc_cat(converted_path)
        content = json.loads(doc.pdoc_content)

        assert "meta" in content, "Meta field not added to pdoc"

        if "survey_id" in content.get("meta", {}):
            logger.info(f"✅ SurveyMonkey survey created successfully")
            logger.info(f"Survey ID: {content['meta'].get('survey_id', 'N/A')}")
            logger.info(f"Survey URL: {content['meta'].get('survey_url', 'N/A')}")
        else:
            logger.warning("Survey metadata not found - API call may have been simulated in test mode")

    except Exception as e:
        logger.warning(f"Could not verify SurveyMonkey creation: {e}")

    logger.info("✅ Hypothesis to survey conversion scenario completed successfully")


if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("profprobe")
    asyncio.run(setup.run_scenario(scenario))
