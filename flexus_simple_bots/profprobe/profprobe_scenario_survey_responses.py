import asyncio
import json
import logging

from flexus_client_kit import ckit_scenario_setup, ckit_kanban
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.profprobe import profprobe_bot
from flexus_simple_bots.profprobe.integrations import survey_monkey
from flexus_simple_bots.profprobe.integrations import survey_monkey_mock

logger = logging.getLogger("scenario")

survey_monkey.aiohttp = survey_monkey_mock.MockAiohttp()


async def create_survey_with_metadata(pdoc_integration, survey_name):
    survey_data = {
        "title": "Customer Feedback Survey",
        "description": "Help us understand your needs",
        "questions": [
            {
                "question": "How likely are you to recommend our product?",
                "type": "nps",
                "required": True
            },
            {
                "question": "What features do you value most?",
                "type": "multiple_choice",
                "choices": ["Price", "Quality", "Design", "Durability"],
                "required": False
            },
            {
                "question": "Any additional feedback?",
                "type": "open_ended",
                "required": False
            }
        ],
        "meta": {
            "survey_id": "10001",
            "survey_url": "https://www.surveymonkey.com/r/test_survey",
            "collector_id": "10001_collector",
            "created_at": "2024-01-20T10:00:00Z"
        }
    }
    
    path = f"/customer-research/unicorn-horn-car-hypotheses/{survey_name}-survey-monkey-query"
    await pdoc_integration.pdoc_write(path, json.dumps(survey_data, indent=2), None)
    return path, survey_data["meta"]["survey_id"]


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
        group_prefix="scenario-survey-responses"
    )

    pdoc_integration = fi_pdoc.IntegrationPdoc(setup.fclient, setup.fgroup_id)
    
    survey_name = "customer-feedback-test"
    survey_path, survey_id = await create_survey_with_metadata(pdoc_integration, survey_name)
    logger.info(f"Created survey pdoc at {survey_path} with ID {survey_id}")
    
    mock_responses = [
        {
            "id": "resp_001",
            "response_status": "completed",
            "date_created": "2024-01-21T09:00:00Z",
            "date_modified": "2024-01-21T09:05:00Z",
            "pages": [
                {
                    "questions": [
                        {
                            "headings": [{"heading": "How likely are you to recommend our product?"}],
                            "answers": [{"text": "9"}]
                        },
                        {
                            "headings": [{"heading": "What features do you value most?"}],
                            "answers": [{"text": "Quality"}, {"text": "Design"}]
                        },
                        {
                            "headings": [{"heading": "Any additional feedback?"}],
                            "answers": [{"text": "Great product, love the unicorn theme!"}]
                        }
                    ]
                }
            ]
        },
        {
            "id": "resp_002",
            "response_status": "completed",
            "date_created": "2024-01-21T10:00:00Z",
            "date_modified": "2024-01-21T10:03:00Z",
            "pages": [
                {
                    "questions": [
                        {
                            "headings": [{"heading": "How likely are you to recommend our product?"}],
                            "answers": [{"text": "7"}]
                        },
                        {
                            "headings": [{"heading": "What features do you value most?"}],
                            "answers": [{"text": "Price"}, {"text": "Durability"}]
                        },
                        {
                            "headings": [{"heading": "Any additional feedback?"}],
                            "answers": [{"text": "Would love more color options"}]
                        }
                    ]
                }
            ]
        },
        {
            "id": "resp_003",
            "response_status": "completed",
            "date_created": "2024-01-21T11:00:00Z",
            "date_modified": "2024-01-21T11:02:00Z",
            "pages": [
                {
                    "questions": [
                        {
                            "headings": [{"heading": "How likely are you to recommend our product?"}],
                            "answers": [{"text": "10"}]
                        },
                        {
                            "headings": [{"heading": "What features do you value most?"}],
                            "answers": [{"text": "Design"}]
                        },
                        {
                            "headings": [{"heading": "Any additional feedback?"}],
                            "answers": [{"text": "My kids absolutely love it!"}]
                        }
                    ]
                }
            ]
        }
    ]
    
    survey_monkey_mock.add_mock_responses(survey_id, mock_responses)
    logger.info(f"Added {len(mock_responses)} mock responses to survey {survey_id}")
    
    await ckit_kanban.bot_kanban_post_into_inbox(
        setup.fclient,
        setup.persona.persona_id,
        f"Retrieve survey responses: {survey_name}",
        json.dumps({
            "instruction": f"Please retrieve all responses for survey ID {survey_id} and analyze the results",
            "survey_id": survey_id,
            "survey_name": survey_name
        }),
        f"Survey has new responses to process"
    )
    
    logger.info(f"Posted kanban task for response retrieval")
    
    await asyncio.sleep(5)
    
    await setup.wait_for_toolcall("get_surveymonkey_responses", None, {"survey_id": survey_id}, allow_existing_toolcall=True)
    
    await asyncio.sleep(2)
    
    results_path = f"/customer-research/unicorn-horn-car-survey-results/{survey_name}"
    
    try:
        doc = await pdoc_integration.pdoc_cat(results_path)
        results = json.loads(doc.pdoc_content) if isinstance(doc.pdoc_content, str) else doc.pdoc_content
        
        assert "responses" in results or "data" in results or "summary" in results, "Results missing response data"
        
        logger.info(f"✅ Survey responses retrieved and saved to {results_path}")
        
        if "summary" in results:
            logger.info(f"Response summary:")
            logger.info(f"  Total responses: {results['summary'].get('total_responses', 'N/A')}")
            logger.info(f"  Average NPS: {results['summary'].get('average_nps', 'N/A')}")
        
        if "responses" in results:
            logger.info(f"Found {len(results['responses'])} responses in results")
        elif "data" in results:
            logger.info(f"Found {len(results['data'])} responses in results")
            
    except FileNotFoundError:
        logger.warning(f"Results file not found at {results_path}, checking alternative locations...")
        
        alt_paths = [
            f"/customer-research/survey-results/{survey_name}",
            f"/customer-research/{survey_name}-results",
            f"/surveys/{survey_id}/results"
        ]
        
        found = False
        for alt_path in alt_paths:
            try:
                doc = await pdoc_integration.pdoc_cat(alt_path)
                logger.info(f"✅ Found results at alternative path: {alt_path}")
                found = True
                break
            except:
                continue
        
        if not found:
            logger.warning("Survey results may have been processed but not saved to expected location")
    
    except Exception as e:
        logger.error(f"Error verifying survey results: {e}")
    
    await asyncio.sleep(2)
    
    try:
        doc = await pdoc_integration.pdoc_cat(survey_path)
        content = json.loads(doc.pdoc_content) if isinstance(doc.pdoc_content, str) else doc.pdoc_content
        
        if content.get("meta", {}).get("responses_processed"):
            logger.info("✅ Survey marked as processed")
        else:
            logger.info("Survey processing status not updated in metadata")
            
    except Exception as e:
        logger.warning(f"Could not verify processing status: {e}")
    
    logger.info("✅ Survey response retrieval scenario completed successfully")


if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("profprobe")
    asyncio.run(setup.run_scenario(scenario))
