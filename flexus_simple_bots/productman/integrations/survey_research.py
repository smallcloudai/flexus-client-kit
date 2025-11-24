import json
import logging
import time
import aiohttp
from typing import Dict, Any, List

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("survey_research")

SURVEY_RESEARCH_TOOL = ckit_cloudtool.CloudTool(
    name="survey",
    description="Unified survey research tool: draft surveys, draft audience targeting, and run complete campaigns. Start with op=\"help\".",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation: help, draft_survey, draft_auditory, run",
                "order": 1
            },
            "args": {
                "type": "object",
                "description": "Operation-specific arguments",
                "order": 2,
                "properties": {
                    "idea_name": {"type": "string", "description": "Name of the idea folder", "order": 1001},
                    "hypothesis_name": {"type": "string", "description": "Name of the hypothesis being tested", "order": 1002},
                    "survey_content": {"type": "object", "description": "Complete survey structure", "order": 1003},
                    "study_name": {"type": "string", "description": "Name for the Prolific study", "order": 1004},
                    "study_description": {"type": "string", "description": "Description for participants", "order": 1005},
                    "estimated_minutes": {"type": "integer", "description": "Estimated completion time", "order": 1006},
                    "reward_cents": {"type": "integer", "description": "Payment per participant in cents", "order": 1007},
                    "total_participants": {"type": "integer", "description": "Number of participants", "order": 1008},
                    "filters": {"type": "object", "description": "Demographic and behavioral filters", "order": 1009},
                    "survey_draft_path": {"type": "string", "description": "Path to survey draft", "order": 1010},
                    "auditory_draft_path": {"type": "string", "description": "Path to auditory draft", "order": 1011}
                }
            }
        },
        "required": ["op"]
    }
)

SURVEY_RESEARCH_HELP = """
survey()
    Shows this help.

survey(op="help")
    Shows detailed help with examples.

survey(op="draft_survey", args={"idea_name": "...", "hypothesis_name": "...", "survey_content": {...}})
    Create a survey draft as a policy document for review.

survey(op="draft_auditory", args={"study_name": "...", "estimated_minutes": 10, "reward_cents": 150, "total_participants": 50, "filters": {...}})
    Create an audience targeting draft for Prolific study.

survey(op="run", args={"survey_draft_path": "...", "auditory_draft_path": "..."})
    Execute complete workflow: create SurveyMonkey survey, create Prolific study, connect them.

Examples:
    # Draft survey
    survey(op="draft_survey", args={
        "idea_name": "task-tool",
        "hypothesis_name": "managers",
        "survey_content": {"survey": {"meta": {...}, "section01-screening": {...}}}
    })

    # Draft audience
    survey(op="draft_auditory", args={
        "study_name": "Task Management Survey",
        "study_description": "We are conducting research on task management practices and tools used by professionals",
        "estimated_minutes": 15,
        "reward_cents": 200,
        "total_participants": 100,
        "filters": {"age": {"min": 25, "max": 55}, "countries": ["1", "45"]}
    })

    # Run campaign
    survey(op="run", args={
        "survey_draft_path": "/customer-research/task-tool/managers-survey-draft",
        "auditory_draft_path": "/customer-research/task-tool/managers-auditory-draft"
    })
    
Survey creation rules.
RULE #0 — SACRED AND NON-NEGOTIABLE
Never ask about the future, intentions, or hypotheticals. Ask ONLY about past experience and real actions.
If a question refers to the future, rewrite it about past behavior or do not ask it. Otherwise, the data is junk.
Use ONLY canvas and the given hypothesis, do not use any other sources.

You MUST NOT ask about:
- how likely someone is to do something,
- whether they will use / buy / pay for something,
- how attractive an idea is,
- “would you…”, “what would you do if…”, or any hypothetical scenario,
- any future behavior or intentions.

You MAY ask only about:
- what the person has done in the past,
- how they previously solved the problem,
- situations they actually faced,
- experience that already happened,
- barriers that already occurred,
- metrics that were actually observed.

--------------------------------
SURVEY STRUCTURE (EXACTLY 6 SECTIONS)
--------------------------------
1. Screening (section01-screening)
2. User profile (section02-user-profile)
3. Problem (section03-problem) - frequency and pain intensity
4. Current behavior (section04-current-behavior) - existing solutions
5. Impact (section05-impact) - how the problem influenced past decisions
6. Concept validation (section06-concept-validation) - only via past experience, no forecasts

You MUST NOT create any additional sections.

Each question must have:
- "q": question text (required)
- "type": one of [yes_no, single_choice, multiple_choice, open_ended]
- "required": true/false
- "choices": array of strings (for single_choice, multiple_choice)

SUPPORTED QUESTION TYPES (currently implemented):
- yes_no: Simple Yes/No question
- single_choice: Select one option from a list (requires "choices" array)
- multiple_choice: Select multiple options from a list (requires "choices" array)
- open_ended: Free text response

--------------------------------
QUESTION RULES
--------------------------------

0. Only past experience
- If a question is about the future, intentions, or hypotheticals → rewrite it to the past or remove it.

1. One question — one idea
- No double questions or mixed meanings.

2. All scales are 1–5
- 1 = minimum (e.g. “not at all”, “never”, “no impact”)
- 5 = maximum (e.g. “very much”, “very often”, “strong impact”)

3. ~80% closed questions
Allowed closed types:
- single choice,
- multiple choice,
- 1–5 scale,
- ranges / intervals,
- factual actions (what they actually did),
- frequency (how often something happened).

Open questions:
- at most 1–2 per section,
- preferably at the end of the section,
- only when really needed.

4. Neutral wording
- No leading or suggestive phrasing.
- Do not push toward a specific answer or toward using the product.

5. No invented facts
- Use only what is in chat history, Canvas, or the hypothesis.
- If there is not enough data to create a specific question, write:
  “Skip — insufficient data.”

6. No invented features
- Use only solution features explicitly described in the materials.
- If a feature is not mentioned, it does not exist and cannot be used in questions.

7. Concept validation only through real experience
You may ask only about:
- whether they used analogs in the past,
- how they solved this problem before,
- what happened when they tried to solve it,
- what pains and barriers they actually faced,
- how similar tools or processes worked in practice.

Do NOT ask:
- “Would you use/buy this?”,
- “How likely are you to use/buy this?”,
- any future adoption questions.
"""


class IntegrationSurveyResearch:
    def __init__(self, surveymonkey_token: str, prolific_token: str, pdoc_integration, fclient):
        if not surveymonkey_token or not prolific_token:
            from flexus_simple_bots.productman.integrations import survey_research_mock
            global aiohttp
            aiohttp = survey_research_mock.MockAiohttp()
            logger.warning("Using mock aiohttp client for survey research")

        self.surveymonkey_token = surveymonkey_token
        self.prolific_token = prolific_token
        self.pdoc_integration = pdoc_integration
        self.fclient = fclient
        self.tracked_surveys = {}

    def _sm_headers(self):
        return {
            "Authorization": f"Bearer {self.surveymonkey_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _prolific_headers(self):
        return {
            "Authorization": f"Token {self.prolific_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _make_request(self, method: str, url: str, headers: dict, json_data=None, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_text = await resp.text()
                    logger.warning(f"API error {method} {url}: {resp.status} - {error_text}")
                    resp.raise_for_status()
                return await resp.json()

    async def handle_survey_research(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not model_produced_args:
            return SURVEY_RESEARCH_HELP

        op = model_produced_args.get("op", "help")
        args = model_produced_args.get("args", {})

        if op == "help":
            return SURVEY_RESEARCH_HELP
        elif op == "draft_survey":
            return await self._handle_draft_survey(toolcall, args)
        elif op == "draft_auditory":
            return await self._handle_draft_auditory(toolcall, args)
        elif op == "run":
            if toolcall.confirmed_by_human:
                return await self._handle_run(toolcall, args)
            else:
                return await self._prepare_run_confirmation(toolcall, args)
        else:
            return f"Unknown operation '{op}'. Valid operations: help, draft_survey, draft_auditory, run"

    async def _handle_draft_survey(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")
        survey_content = args.get("survey_content", {})

        if not idea_name or not hypothesis_name:
            return "Error: idea_name and hypothesis_name are required"

        formatted_content = {}
        
        if "survey" in survey_content and "meta" in survey_content["survey"]:
            formatted_content["survey"] = {
                "meta": survey_content["survey"]["meta"]
            }
        else:
            formatted_content["survey"] = {
                "meta": {
                    "title": "Survey",
                    "description": ""
                }
            }
        
        formatted_content["survey"]["meta"]["hypothesis"] = hypothesis_name
        formatted_content["survey"]["meta"]["idea"] = idea_name
        formatted_content["survey"]["meta"]["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_content["survey"]["meta"]["prolific_integration"] = True

        for key, value in survey_content.items():
            if key.startswith("section") and isinstance(value, dict):
                if "questions" not in value or not isinstance(value["questions"], list):
                    if "questions" in value:
                        value["questions"] = [value["questions"]] if not isinstance(value["questions"], list) else value["questions"]
                    else:
                        questions_list = []
                        for q_key in sorted(value.keys()):
                            if q_key.startswith("question") and isinstance(value[q_key], dict):
                                questions_list.append(value[q_key])
                        if questions_list:
                            value = {
                                "title": value.get("title", "Section"),
                                "questions": questions_list
                            }
                        else:
                            value = {
                                "title": value.get("title", "Section"),
                                "questions": []
                            }
                formatted_content[key] = value
            elif key != "survey" and isinstance(value, dict):
                formatted_content[key] = value

        section_count = sum(1 for k in formatted_content.keys() if k.startswith("section"))
        if section_count == 0:
            return "Error: Survey must contain at least one section (e.g., section01-screening)"
        
        question_count = sum(
            len(section.get("questions", [])) 
            for key, section in formatted_content.items() 
            if key.startswith("section") and isinstance(section, dict)
        )
        if question_count == 0:
            return "Error: Survey must contain at least one question"

        pdoc_path = f"/customer-research/{idea_name}/{hypothesis_name}-survey-draft"

        await self.pdoc_integration.pdoc_create(
            pdoc_path,
            json.dumps(formatted_content, indent=2),
            toolcall.fcall_ft_id
        )

        result = f"✅ Survey draft created successfully!\n\n"
        result += f"📝 Draft saved to: {pdoc_path}\n"
        result += f"✍️{pdoc_path}\n\n"
        result += f"📊 Survey contains {section_count} sections with {question_count} total questions\n\n"
        result += f"Next: Create audience targeting with survey(op=\"draft_auditory\", ...)"

        return result

    async def _handle_draft_auditory(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        study_name = args.get("study_name", "")
        study_description = args.get("study_description", "")
        estimated_minutes = args.get("estimated_minutes", 5)
        reward_cents = args.get("reward_cents", 100)
        total_participants = args.get("total_participants", 50)
        filters = args.get("filters", {})

        if not study_name:
            return "Error: study_name is required"
        
        if not study_description:
            return "Error: study_description is required"

        prolific_filters = await self._build_prolific_filters(filters)
        service_fee = reward_cents * total_participants * 0.33
        vat = service_fee * 0.20
        total_cost = (reward_cents * total_participants) + service_fee + vat

        draft_content = {
            "prolific_auditory_draft": {
                "meta": {
                    "study_name": study_name,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "DRAFT"
                },
                "parameters": {
                    "study_description": study_description,
                    "estimated_minutes": estimated_minutes,
                    "reward_cents": reward_cents,
                    "total_participants": total_participants,
                    "filters": prolific_filters,
                    "completion_codes": [{
                        "code": f"COMPLETE_{study_name.upper().replace(' ', '_').replace('-', '_')[:8]}",
                        "code_type": "COMPLETED",
                        "actions": [{"action": "AUTOMATICALLY_APPROVE"}]
                    }]
                },
                "cost_estimate": {
                    "rewards": reward_cents * total_participants,
                    "service_fee": int(service_fee),
                    "vat": int(vat),
                    "total": int(total_cost)
                }
            }
        }

        draft_path = f"/customer-research/auditory-drafts/{study_name.lower().replace(' ', '-')}-auditory-draft"

        await self.pdoc_integration.pdoc_create(
            draft_path,
            json.dumps(draft_content, indent=2),
            toolcall.fcall_ft_id
        )

        result = f"✅ Audience targeting draft created!\n\n"
        result += f"📝 Draft saved to: {draft_path}\n"
        result += f"✍️{draft_path}\n\n"
        result += f"Study: {study_name}\n"
        result += f"Participants: {total_participants}\n"
        result += f"Reward: £{reward_cents / 100:.2f} per participant\n\n"
        result += f"💰 Estimated Cost: £{total_cost / 100:.2f}\n\n"
        result += f"Next: Review both drafts and use survey(op=\"run\", ...) to execute"

        return result

    async def _build_prolific_filters(self, filters: Dict[str, Any]) -> List[Dict]:
        prolific_filters = []

        if "age" in filters:
            age_filter = {"filter_id": "age", "selected_range": {}}
            if "min" in filters["age"]:
                age_filter["selected_range"]["lower"] = filters["age"]["min"]
            if "max" in filters["age"]:
                age_filter["selected_range"]["upper"] = filters["age"]["max"]
            prolific_filters.append(age_filter)

        if "countries" in filters:
            prolific_filters.append({
                "filter_id": "current-country-of-residence",
                "selected_values": filters["countries"]
            })

        if "previous_studies" in filters:
            prolific_filters.append({
                "filter_id": "previous_studies",
                "selected_values": filters["previous_studies"]
            })

        return prolific_filters

    async def _prepare_run_confirmation(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_draft_path = args.get("survey_draft_path", "")
        auditory_draft_path = args.get("auditory_draft_path", "")

        if not survey_draft_path or not auditory_draft_path:
            return "Error: Both survey_draft_path and auditory_draft_path are required"

        auditory_doc = await self.pdoc_integration.pdoc_cat(auditory_draft_path)
        auditory_content = auditory_doc.pdoc_content

        if not auditory_content or "prolific_auditory_draft" not in auditory_content:
            return "Error: Invalid auditory draft format"

        cost_estimate = auditory_content["prolific_auditory_draft"]["cost_estimate"]
        total_cost = cost_estimate["total"]

        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="can_run_survey_campaign",
            confirm_command=f'run survey campaign £{total_cost / 100:.2f}',
            confirm_explanation=f"This will create SurveyMonkey survey and Prolific study costing £{total_cost / 100:.2f}. Please confirm.",
        )

    async def _handle_run(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_draft_path = args.get("survey_draft_path", "")
        auditory_draft_path = args.get("auditory_draft_path", "")

        try:
            survey_doc = await self.pdoc_integration.pdoc_cat(survey_draft_path)
            auditory_doc = await self.pdoc_integration.pdoc_cat(auditory_draft_path)

            survey_content = survey_doc.pdoc_content
            auditory_content = auditory_doc.pdoc_content
            
            draft = auditory_content.get("prolific_auditory_draft", {})
            completion_codes = draft.get("parameters", {}).get("completion_codes", [])
            completion_code = completion_codes[0]["code"] if completion_codes else "COMPLETE"

            survey_info = await self._create_surveymonkey_survey(survey_content, completion_code)
            study_id = await self._create_prolific_study(auditory_content, survey_info)

            survey_id = survey_info["survey_id"]
            survey_url = survey_info["url"]
            auditory_draft = auditory_content.get("prolific_auditory_draft", {})
            target_responses = auditory_draft.get("parameters", {}).get("total_participants", 0)

            if survey_id and toolcall.fcall_ft_id and self.fclient:
                from flexus_client_kit import ckit_kanban

                try:
                    tasks = await ckit_kanban.get_tasks_by_thread(self.fclient, toolcall.fcall_ft_id)

                    for task in tasks:
                        task_details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details or "{}")
                        task_details["survey_id"] = survey_id
                        task_details["target_responses"] = target_responses
                        task_details["prolific_study_id"] = study_id
                        task_details["survey_status"] = {
                            "responses": 0,
                            "completion_rate": 0.0,
                            "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "completed_notified": False
                        }

                        await ckit_kanban.update_task_details(self.fclient, task.ktask_id, task_details)
                        logger.info(f"Updated task {task.ktask_id} with survey tracking info")
                except Exception as e:
                    logger.error(f"Failed to update task with survey info: {e}")

            result = f"✅ Survey campaign launched successfully!\n\n"
            result += f"📋 SurveyMonkey URL: {survey_url}\n"
            result += f"🎯 Prolific Study ID: {study_id}\n"
            result += f"✅ Participants are now being recruited!\n\n"
            result += f"📝 Survey draft: {survey_draft_path}\n"
            result += f"📝 Auditory draft: {auditory_draft_path}"

            return result

        except Exception as e:
            return f"Error executing campaign: {str(e)}"

    def track_survey_task(self, task):
        """Track survey tasks for automatic status updates"""
        if not task.ktask_details:
            return

        details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details or "{}")
        survey_id = details.get("survey_id")

        if survey_id and task.ktask_done_ts == 0:
            if survey_id not in self.tracked_surveys:
                self.tracked_surveys[survey_id] = {
                    "task_id": task.ktask_id,
                    "thread_id": task.ktask_inprogress_ft_id,
                    "target_responses": details.get("target_responses", 0),
                    "last_response_count": details.get("survey_status", {}).get("responses", 0) if "survey_status" in details else 0,
                    "completed_notified": details.get("survey_status", {}).get("completed_notified", False) if "survey_status" in details else False
                }
                logger.info(f"Tracking survey {survey_id} for task {task.ktask_id}")

    async def update_active_surveys(self, fclient, update_task_callback):
        if not self.tracked_surveys:
            return

        for survey_id, tracking_info in list(self.tracked_surveys.items()):
            try:
                try:
                    response_data = await self._make_request(
                        "GET",
                        f"https://api.surveymonkey.com/v3/surveys/{survey_id}/responses/bulk",
                        self._sm_headers(),
                        params={"per_page": 1}
                    )
                except Exception as e:
                    logger.warn(f"Could not fetch survey {survey_id} status: {e}")
                    continue

                if not response_data:
                    continue

                response_count = response_data.get("total", 0)
                target_responses = tracking_info["target_responses"]
                is_completed = target_responses > 0 and response_count >= target_responses

                await update_task_callback(
                    fclient,
                    task_id=tracking_info["task_id"],
                    survey_id=survey_id,
                    response_count=response_count,
                    is_completed=is_completed,
                    survey_status="active"
                )

                if is_completed and not tracking_info["completed_notified"] and tracking_info["thread_id"]:
                    message = f"📊 Survey completed!\nSurvey ID: {survey_id}\nTotal responses: {response_count}\nTarget responses: {target_responses}"

                    from flexus_client_kit import ckit_ask_model
                    http = await fclient.use_http()
                    await ckit_ask_model.thread_add_user_message(
                        http=http,
                        ft_id=tracking_info["thread_id"],
                        content=message,
                        who_is_asking="survey_research_integration",
                        ftm_alt=100,
                        role="user"
                    )

                    tracking_info["completed_notified"] = True
                    logger.info(f"Posted completion message for survey {survey_id}")

                tracking_info["last_response_count"] = response_count

            except Exception as e:
                logger.error(f"🛑 Error updating survey {survey_id}: {e}")

    async def update_task_survey_status(self, fclient, task_id: str, survey_id: str, response_count: int, is_completed: bool, survey_status: str):
        from flexus_client_kit import ckit_kanban

        try:
            tasks = await ckit_kanban.bot_get_all_tasks(fclient, fclient.persona_id)
            task = next((t for t in tasks if t.ktask_id == task_id), None)
            if not task:
                logger.warning(f"No task found for task_id: {task_id}")
                return

            details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details or "{}")
            target_responses = details.get("target_responses", 1)
            completion_rate = response_count / target_responses if target_responses > 0 else 0

            details["survey_status"] = {
                "responses": response_count,
                "completion_rate": completion_rate,
                "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
                "completed_notified": details.get("survey_status", {}).get("completed_notified", False) or is_completed,
                "status": survey_status
            }

            await ckit_kanban.update_task_details(fclient, task_id, details)
            logger.info(f"Updated task {task_id} with survey status")

        except Exception as e:
            logger.error(f"Failed to update task survey status: {e}")

    async def _create_surveymonkey_survey(self, survey_content: Dict, completion_code: str) -> Dict:
        meta = survey_content.get("survey", {}).get("meta", {})
        survey_title = meta.get("title", "Survey")
        survey_description = meta.get("description", "")

        questions = []
        for section_key in sorted(survey_content.keys()):
            if not section_key.startswith("section"):
                continue
            section = survey_content[section_key]
            if not isinstance(section, dict):
                continue

            if isinstance(section.get("questions"), list):
                for q_data in section["questions"]:
                    if isinstance(q_data, dict):
                        questions.append(self._convert_question_to_sm(q_data))
            else:
                for question_key in sorted(section.keys()):
                    if not question_key.startswith("question"):
                        continue
                    q_data = section[question_key]
                    if isinstance(q_data, dict):
                        questions.append(self._convert_question_to_sm(q_data))

        survey_payload = {
            "title": survey_title,
            "pages": [{
                "title": "Page 1",
                "description": survey_description,
                "questions": questions
            }],
            "thank_you_page": {
                "is_enabled": True,
                "message": f"Thank you for completing this survey!\n\nIMPORTANT: Please copy this completion code and paste it in Prolific to receive your payment:\n\n{completion_code}"
            }
        }

        survey = await self._make_request(
            "POST",
            "https://api.surveymonkey.com/v3/surveys",
            self._sm_headers(),
            survey_payload
        )
        survey_id = survey["id"]

        collector_payload = {
            "type": "weblink",
            "name": "Prolific Collector"
        }

        collector = await self._make_request(
            "POST",
            f"https://api.surveymonkey.com/v3/surveys/{survey_id}/collectors",
            self._sm_headers(),
            collector_payload
        )

        return {
            "survey_id": survey_id,
            "collector_id": collector["id"],
            "url": collector.get("url", "")
        }

    def _convert_question_to_sm(self, q_data: Dict) -> Dict:
        question_text = q_data.get("q", "")
        q_type = q_data.get("type", "open_ended")
        choices = q_data.get("choices", [])
        required = q_data.get("required", False)

        question_mappings = {
            "yes_no": {
                "family": "single_choice",
                "subtype": "vertical",
                "answers": {"choices": [{"text": "Yes"}, {"text": "No"}]}
            },
            "single_choice": {
                "family": "single_choice",
                "subtype": "vertical",
                "answers": {"choices": [{"text": c} for c in choices]}
            },
            "multiple_choice": {
                "family": "multiple_choice",
                "subtype": "vertical",
                "answers": {"choices": [{"text": c} for c in choices]}
            },
            "open_ended": {
                "family": "open_ended",
                "subtype": "single"
            }
        }

        mapping = question_mappings.get(q_type, question_mappings["open_ended"])

        sm_q = {
            "headings": [{"heading": question_text}],
            "family": mapping["family"],
            "subtype": mapping.get("subtype", "single")
        }

        if "answers" in mapping:
            sm_q["answers"] = mapping["answers"]

        if required:
            sm_q["required"] = {
                "text": "This question requires an answer.",
                "type": "all",
                "amount": "1"
            }

        return sm_q

    async def _create_prolific_study(self, auditory_content: Dict, survey_info: Dict) -> str:
        draft = auditory_content.get("prolific_auditory_draft", {})
        meta = draft.get("meta", {})
        params = draft.get("parameters", {})

        study_name = meta.get("study_name", "Study")
        study_description = params.get("study_description", "")
        estimated_minutes = params.get("estimated_minutes", 5)
        reward_cents = params.get("reward_cents", 100)
        total_participants = params.get("total_participants", 50)
        filters = params.get("filters", [])
        completion_codes = params.get("completion_codes", [])

        survey_url = survey_info["url"]
        completion_code = completion_codes[0]["code"] if completion_codes else "COMPLETE"
        
        param_str = "PROLIFIC_PID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}"
        external_url = f"{survey_url}&{param_str}" if "?" in survey_url else f"{survey_url}?{param_str}"

        study_payload = {
            "name": study_name,
            "description": study_description,
            "external_study_url": external_url,
            "prolific_id_option": "url_parameters",
            "completion_option": "code",
            "completion_codes": completion_codes,
            "estimated_completion_time": estimated_minutes,
            "maximum_allowed_time": estimated_minutes * 5,
            "reward": reward_cents,
            "total_available_places": total_participants,
            "device_compatibility": ["desktop", "mobile", "tablet"],
            "filters": filters
        }

        study = await self._make_request(
            "POST",
            "https://api.prolific.com/api/v1/studies/",
            self._prolific_headers(),
            study_payload
        )
        
        return study["id"]


