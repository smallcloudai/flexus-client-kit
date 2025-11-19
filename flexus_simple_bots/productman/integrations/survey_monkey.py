import json
import logging
import time
from typing import Dict, Any

import aiohttp

from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.productman.integrations import survey_monkey_mock

logger = logging.getLogger("survey_monkey")

SM_BASE = "https://api.surveymonkey.com/v3"

SURVEY_TOOL = ckit_cloudtool.CloudTool(
    name="survey",
    description="Manage surveys: create drafts, push to SurveyMonkey, get responses. Start with op=\"help\" to see all operations.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation to perform: help, draft, push, responses, list",
                "order": 1
            },
            "args": {
                "type": "object",
                "description": "Operation-specific arguments",
                "order": 2,
                "properties": {
                    # draft operation
                    "idea_name": {"type": "string", "description": "Name of the idea folder (for draft/list)", "order": 1001},
                    "hypothesis_name": {"type": "string", "description": "Name of the hypothesis being tested (for draft)", "order": 1002},
                    "survey_content": {"type": "object", "description": "Complete survey structure with meta and sections (for draft)", "order": 1003},
                    # push operation
                    "survey_draft_path": {"type": "string", "description": "Path to survey draft document (for push)", "order": 1004},
                    # responses operation
                    "survey_id": {"type": "string", "description": "SurveyMonkey survey ID (for responses)", "order": 1005},
                }
            }
        },
        "required": ["op"]
    }
)

SURVEY_HELP = """
survey()
    Shows this help.

survey(op="help")
    Shows this help with examples.

survey(op="draft", args={"idea_name": "...", "hypothesis_name": "...", "survey_content": {...}})
    Create a survey draft as a policy document.
    Structure: {"survey": {"meta": {...}, "section01-screening": {"section_title": "...", "question01": {...}}}}
    Use exactly 6 sections: screening, user-profile, problem, current-behavior, impact, concept-validation
    Question types: single_choice, multiple_choice, open_ended, rating_scale, yes_no, likert, nps, dropdown, numeric, date
    
survey(op="push", args={"survey_draft_path": "/customer-research/idea/hypothesis-survey-draft"})
    Push a survey draft from policy document to SurveyMonkey.
    Returns survey URL and ID.

survey(op="responses", args={"survey_id": "123456"})
    Fetch all responses for a SurveyMonkey survey.
    
survey(op="list", args={"idea_name": "..."})
    List all surveys for an idea (drafts and live).

Examples:
    # Create draft
    survey(op="draft", args={
        "idea_name": "task-tool", 
        "hypothesis_name": "managers",
        "survey_content": {
            "survey": {
                "meta": {"title": "Task Management Survey", "description": "..."},
                "section01-screening": {
                    "section_title": "Screening",
                    "question01": {"q": "Do you manage a team?", "type": "yes_no", "required": true}
                }
            }
        }
    })
    
    # Push to SurveyMonkey
    survey(op="push", args={"survey_draft_path": "/customer-research/task-tool/managers-survey-draft"})
    
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
- "type": one of [single_choice, multiple_choice, open_ended, rating_scale, yes_no, likert, dropdown, numeric, date]
- "required": true/false
- "choices": array of strings (for single_choice, multiple_choice, dropdown)
- "scale_min", "scale_max": integers (for rating_scale)

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


class IntegrationSurveyMonkey:
    def __init__(self, access_token: str, pdoc_integration=None):
        self.access_token = access_token
        self.pdoc_integration = pdoc_integration
        self.tracked_surveys = {}

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def handle_survey(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not model_produced_args:
            return SURVEY_HELP

        op = model_produced_args.get("op", "help")
        args = model_produced_args.get("args", {})

        if op == "help":
            return SURVEY_HELP

        elif op == "draft":
            return await self._handle_draft(toolcall, args)

        elif op == "push":
            if toolcall.confirmed_by_human:
                return await self._handle_push(toolcall, args)
            else:
                raise ckit_cloudtool.NeedsConfirmation(
                    confirm_setup_key="can_create_surveymonkey_survey",
                    confirm_command=f'survey push {args.get("survey_draft_path", "")}',
                    confirm_explanation="This command will create a survey on surveymonkey.com"
                )

        elif op == "responses":
            return await self._handle_responses(toolcall, args)

        elif op == "list":
            return await self._handle_list(toolcall, args)

        else:
            return f"Unknown operation '{op}'. Valid operations: help, draft, push, responses, list\n\n{SURVEY_HELP}"

    async def _handle_list(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")

        if not idea_name:
            return "Error: idea_name is required for list operation"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        try:
            path = f"/customer-research/{idea_name}"
            items = await self.pdoc_integration.pdoc_list(path)

            surveys = []
            for item in items:
                if not item.is_folder and ("-survey-draft" in item.path or "-survey-live" in item.path):
                    surveys.append(item.path)

            if not surveys:
                return f"No surveys found for idea '{idea_name}'"

            result = f"📋 Surveys for idea '{idea_name}':\n\n"
            for survey_path in sorted(surveys):
                if "-survey-draft" in survey_path:
                    result += f"📝 Draft: {survey_path}\n"
                else:
                    result += f"🔗 Live: {survey_path}\n"

            return result

        except Exception as e:
            return f"Error listing surveys: {str(e)}"

    def validate_survey_structure(self, survey_content: dict) -> list:
        errors = []

        if not isinstance(survey_content, dict):
            return ["survey_content must be a dictionary"]

        if "survey" not in survey_content:
            return ["survey_content must have a 'survey' root key"]

        survey = survey_content["survey"]

        if "meta" not in survey:
            errors.append("Missing 'meta' section")
        else:
            meta = survey["meta"]
            if not meta.get("title"):
                errors.append("meta.title is required")
            if not meta.get("hypothesis"):
                errors.append("meta.hypothesis is required")
            if not meta.get("idea"):
                errors.append("meta.idea is required")

        section_count = 0
        question_count = 0

        for key, section in survey.items():
            if not key.startswith("section"):
                continue

            section_count += 1

            if not isinstance(section, dict):
                errors.append(f"Section {key} must be a dictionary")
                continue

            if not section.get("section_title"):
                errors.append(f"Section {key} missing section_title")

            for q_key, question in section.items():
                if not q_key.startswith("question"):
                    continue

                question_count += 1

                if not isinstance(question, dict):
                    errors.append(f"{key}.{q_key} must be a dictionary")
                    continue

                if not question.get("q"):
                    errors.append(f"{key}.{q_key} missing question text 'q'")

                q_type = question.get("type", "open_ended")
                valid_types = ["single_choice", "multiple_choice", "open_ended", "rating_scale",
                               "yes_no", "dropdown", "likert", "nps", "numeric", "date", "matrix"]

                if q_type not in valid_types:
                    errors.append(f"{key}.{q_key} invalid type '{q_type}'. Valid types: {', '.join(valid_types)}")

                if q_type in ["single_choice", "multiple_choice", "dropdown"]:
                    choices = question.get("choices", [])
                    if not choices or not isinstance(choices, list) or len(choices) < 2:
                        errors.append(f"{key}.{q_key} of type '{q_type}' must have at least 2 choices")

                if q_type == "rating_scale":
                    scale_min = question.get("scale_min", 1)
                    scale_max = question.get("scale_max", 5)
                    if not isinstance(scale_min, int) or not isinstance(scale_max, int):
                        errors.append(f"{key}.{q_key} scale_min and scale_max must be integers")
                    elif scale_min >= scale_max:
                        errors.append(f"{key}.{q_key} scale_min must be less than scale_max")

                if "required" in question and not isinstance(question.get("required"), bool):
                    errors.append(f"{key}.{q_key} 'required' must be a boolean")

        if section_count == 0:
            errors.append("No sections found. Sections must be named like 'section01-name'")

        if question_count == 0:
            errors.append("No questions found. Questions must be named like 'question01'")

        return errors

    async def _handle_draft(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")
        survey_content = args.get("survey_content", {})

        if not idea_name or not hypothesis_name:
            return "Error: idea_name and hypothesis_name are required"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        if not survey_content.get("survey", {}).get("meta"):
            survey_content = {
                "survey": {
                    "meta": {
                        "title": survey_content.get("survey", {}).get("meta", {}).get("title", "Survey"),
                        "description": survey_content.get("survey", {}).get("meta", {}).get("description", ""),
                        "hypothesis": hypothesis_name,
                        "idea": idea_name,
                        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    },
                    **survey_content.get("survey", {})
                }
            }
        else:
            survey_content["survey"]["meta"]["hypothesis"] = hypothesis_name
            survey_content["survey"]["meta"]["idea"] = idea_name
            survey_content["survey"]["meta"]["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        validation_errors = self.validate_survey_structure(survey_content)
        if validation_errors:
            error_msg = "Survey validation failed:\n"
            for error in validation_errors:
                error_msg += f"  - {error}\n"
            return error_msg

        for key, section in survey_content["survey"].items():
            if not key.startswith("section"):
                continue
            for q_key, question in section.items():
                if not q_key.startswith("question"):
                    continue

                q_type = question.get("type", "open_ended")
                if q_type in ["single_choice", "multiple_choice", "dropdown"] and question.get("choices"):
                    question["choices"] = [str(c) for c in question["choices"]]

                if q_type == "rating_scale":
                    question["scale_min"] = question.get("scale_min", 1)
                    question["scale_max"] = question.get("scale_max", 5)

                if "required" not in question:
                    question["required"] = False

        pdoc_path = f"/customer-research/{idea_name}/{hypothesis_name}-survey-draft"

        try:
            await self.pdoc_integration.pdoc_create(
                pdoc_path,
                json.dumps(survey_content, indent=2),
                toolcall.fcall_ft_id
            )
        except Exception as e:
            if "already exists" in str(e):
                return f"Error: Survey draft already exists at {pdoc_path}. Use the policy document editor to modify it."
            raise e

        section_count = sum(1 for k in survey_content["survey"].keys() if k.startswith("section"))
        question_count = sum(
            sum(1 for q in section.keys() if q.startswith("question"))
            for key, section in survey_content["survey"].items()
            if key.startswith("section") and isinstance(section, dict)
        )

        result = f"✅ Survey draft created successfully!\n\n"
        result += f"📝 Draft saved to: {pdoc_path}\n"
        result += f"✍🏻{pdoc_path}\n\n"
        result += f"📊 Created {question_count} questions across {section_count} sections\n\n"
        result += f"Please review and edit the questions if needed.\n"
        result += f"Once ready, use create_surveymonkey_survey(survey_draft_path=\"{pdoc_path}\") to push to SurveyMonkey."

        return result

    def parse_survey_draft(self, draft_content: dict) -> tuple[dict, list]:
        errors = []

        if not draft_content or not isinstance(draft_content, dict):
            errors.append("Invalid draft format: expected a dictionary")
            return {}, errors

        survey_root = draft_content.get("survey")
        if not survey_root:
            errors.append("Draft must have a 'survey' root key")
            return {}, errors

        meta = survey_root.get("meta", {})
        survey_title = meta.get("title", "Untitled Survey")
        survey_description = meta.get("description", "")

        questions = []

        for section_key in sorted(survey_root.keys()):
            if not section_key.startswith("section"):
                continue

            section = survey_root[section_key]
            if not isinstance(section, dict):
                errors.append(f"Section {section_key} must be a dictionary")
                continue

            section_title = section.get("section_title", "")

            for question_key in sorted(section.keys()):
                if not question_key.startswith("question"):
                    continue

                q_data = section[question_key]
                if not isinstance(q_data, dict):
                    errors.append(f"Question {section_key}.{question_key} must be a dictionary")
                    continue

                question_text = q_data.get("q", "")
                if not question_text:
                    errors.append(f"Question {section_key}.{question_key} missing 'q' field")
                    continue

                q_type = q_data.get("type", "open_ended")
                choices = q_data.get("choices", [])
                required = q_data.get("required", False)
                scale_min = q_data.get("scale_min", 1)
                scale_max = q_data.get("scale_max", 5)

                questions.append({
                    "section": section_title,
                    "question": question_text,
                    "type": q_type,
                    "choices": choices,
                    "required": required,
                    "scale_min": scale_min,
                    "scale_max": scale_max
                })

        if not questions:
            errors.append("No valid questions found in the draft")

        return {
            "title": survey_title,
            "description": survey_description,
            "questions": questions
        }, errors

    def convert_question_to_sm(self, q: dict) -> dict:
        q_type = q["type"]
        text = q["text"]
        required = q.get("required", False)
        choices = q.get("choices", [])
        scale_min = q.get("scale_min", 1)
        scale_max = q.get("scale_max", 5)

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
            "dropdown": {
                "family": "single_choice",
                "subtype": "menu",
                "answers": {"choices": [{"text": c} for c in choices]}
            },
            "multiple_choice": {
                "family": "multiple_choice",
                "subtype": "vertical",
                "answers": {"choices": [{"text": c} for c in choices]}
            },
            "rating_scale": {
                "family": "single_choice",
                "subtype": "rating",
                "answers": {
                    "choices": [{"text": str(i), "weight": i} for i in range(scale_min, scale_max + 1)]
                }
            },
            "nps": {
                "family": "matrix",
                "subtype": "nps",
                "answers": {
                    "rows": [{"text": "Our product"}],
                    "choices": [{"text": str(i), "weight": i} for i in range(0, 11)]
                }
            },
            "likert": {
                "family": "single_choice",
                "subtype": "vertical",
                "answers": {"choices": [
                    {"text": "Strongly disagree"},
                    {"text": "Disagree"},
                    {"text": "Neutral"},
                    {"text": "Agree"},
                    {"text": "Strongly agree"}
                ]}
            },
            "matrix": {
                "family": "matrix",
                "subtype": "single",
                "answers": {
                    "rows": [{"text": item} for item in (choices or ["Item"])],
                    "choices": [
                        {"text": "Very poor"},
                        {"text": "Poor"},
                        {"text": "Fair"},
                        {"text": "Good"},
                        {"text": "Excellent"}
                    ]
                }
            },
            "numeric": {
                "family": "open_ended",
                "subtype": "numerical"
            },
            "date": {
                "family": "datetime",
                "subtype": "date_only"
            },
            "open_ended": {
                "family": "open_ended",
                "subtype": "single"
            }
        }

        mapping = question_mappings.get(q_type, question_mappings["open_ended"])

        sm_q = {
            "headings": [{"heading": text}],
            "family": mapping["family"],
            "subtype": mapping.get("subtype", "single")
        }

        if "answers" in mapping:
            sm_q["answers"] = mapping["answers"]

        if required:
            sm_q.setdefault("validation", {})
            sm_q["validation"]["required"] = True

        return sm_q

    async def _handle_push(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_draft_path = args.get("survey_draft_path", "")

        if not survey_draft_path:
            return "Error: survey_draft_path is required"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        try:
            draft_doc = await self.pdoc_integration.pdoc_cat(survey_draft_path)
            draft_content = draft_doc.pdoc_content
        except Exception as e:
            return f"Error reading survey draft: {str(e)}"

        survey_data, parse_errors = self.parse_survey_draft(draft_content)

        if not survey_data or not survey_data.get("questions"):
            error_msg = "Error: Failed to parse survey draft\n"
            if parse_errors:
                error_msg += "Issues found:\n" + "\n".join(f"- {e}" for e in parse_errors)
            return error_msg

        survey_title = survey_data["title"]
        survey_description = survey_data.get("description", "")
        questions = survey_data["questions"]

        sm_questions = []
        for q in questions:
            q_dict = {
                "text": q.get("question", ""),
                "type": q.get("type", "open_ended"),
                "choices": q.get("choices", []),
                "required": q.get("required", False)
            }
            if "scale_min" in q:
                q_dict["scale_min"] = q["scale_min"]
            if "scale_max" in q:
                q_dict["scale_max"] = q["scale_max"]
            sm_questions.append(self.convert_question_to_sm(q_dict))

        survey_payload = {
            "title": survey_title,
            "pages": [
                {
                    "title": "Page 1",
                    "description": survey_description,
                    "questions": sm_questions
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{SM_BASE}/surveys",
                    headers=self._headers(),
                    json=survey_payload,
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                survey = await resp.json()
                survey_id = survey["id"]

            collector_payload = {
                "type": "weblink",
                "name": "Survey link",
                "thank_you_page": {
                    "is_enabled": True,
                    "message": "Thank you for your feedback!"
                }
            }
            async with session.post(
                    f"{SM_BASE}/surveys/{survey_id}/collectors",
                    headers=self._headers(),
                    json=collector_payload,
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as c_resp:
                c_resp.raise_for_status()
                collector = await c_resp.json()

        survey_url = collector.get("url", "")

        path_parts = survey_draft_path.rstrip('/').split('/')
        if len(path_parts) >= 3:
            idea_name = path_parts[-2]
            hypothesis_base = path_parts[-1].replace('-survey-draft', '')
        else:
            idea_name = "unknown"
            hypothesis_base = "survey"

        result_pdoc_path = f"/customer-research/{idea_name}/{hypothesis_base}-survey-monkey"

        live_survey_data = dict(
            survey_monkey={
                "title": survey_title,
                "description": survey_description,
                "questions": questions,
                "meta": {
                    "survey_id": survey_id,
                    "survey_url": survey_url,
                    "collector_id": collector["id"],
                    "created_from_draft": survey_draft_path,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        )

        await self.pdoc_integration.pdoc_create(result_pdoc_path, json.dumps(live_survey_data, indent=2), toolcall.fcall_ft_id)

        result = f"✅ Survey created successfully on SurveyMonkey!\n\n"
        result += f"📋 Survey ID: {survey_id}\n"
        result += f"🔗 Survey URL: {survey_url}\n"
        result += f"📊 {len(questions)} questions pushed\n"
        result += f"\n📁 Survey monkey raw data: {result_pdoc_path}\n"
        result += f"✍🏻{result_pdoc_path}\n"

        return result

    async def check_survey_has_responses(self, survey_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{SM_BASE}/surveys/{survey_id}/responses/bulk",
                    headers=self._headers(),
                    params={"per_page": 1},
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("total", 0) > 0

    async def _handle_responses(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_id = args.get("survey_id", "")
        if not survey_id:
            return "Error: survey_id is required"

        all_responses = []
        page, per_page, total = 1, 100, None

        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                        f"{SM_BASE}/surveys/{survey_id}/responses/bulk",
                        headers=self._headers(),
                        params={
                            "simple": "true",
                            "page": page,
                            "per_page": per_page,
                        },
                        timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()

                    if total is None:
                        total = data.get("total", 0)

                    page_responses = data.get("data", [])
                    all_responses.extend(page_responses)

                    if len(page_responses) < per_page or len(all_responses) >= total:
                        break

                    page += 1

        result = f"📊 Survey Responses (Survey ID: {survey_id})\n"
        result += f"Total responses retrieved: {len(all_responses)}\n"
        result += "=" * 50 + "\n\n"

        if not all_responses:
            result += "No responses found.\n"
            return result

        for idx, r in enumerate(all_responses, 1):
            result += f"Response #{idx} (ID: {r.get('id', 'N/A')})\n"
            result += f"Status: {r.get('response_status', 'N/A')}\n"
            result += f"Submitted: {r.get('date_modified') or r.get('date_created', 'N/A')}\n\n"

            for page_obj in r.get("pages", []):
                for q in page_obj.get("questions", []):
                    q_text = None
                    headings = q.get("headings", [])
                    if headings and isinstance(headings, list):
                        if isinstance(headings[0], dict):
                            q_text = headings[0].get("heading", "")

                    answers = q.get("answers", [])
                    if not answers:
                        continue

                    parts = []
                    for a in answers:
                        if "text" in a and a["text"]:
                            parts.append(a["text"])
                        elif "choice_id" in a:
                            parts.append(f"choice_id={a['choice_id']}")

                    if q_text and parts:
                        result += f"Q: {q_text}\n"
                        result += f"A: {', '.join(parts)}\n\n"

            result += "-" * 30 + "\n\n"

        return result

    def track_survey_task(self, task):
        if not task.ktask_details:
            return
        
        details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details)
        survey_id = details.get("survey_id")
        
        if survey_id and task.ktask_done_ts == 0:
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
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"{SM_BASE}/surveys/{survey_id}",
                            headers=self._headers(),
                            timeout=aiohttp.ClientTimeout(total=30),
                    ) as resp:
                        if resp.status >= 400:
                            continue
                        survey_data = await resp.json()
                    
                    async with session.get(
                            f"{SM_BASE}/surveys/{survey_id}/responses/bulk",
                            headers=self._headers(),
                            params={"per_page": 1},
                            timeout=aiohttp.ClientTimeout(total=30),
                    ) as resp:
                        if resp.status >= 400:
                            continue
                        response_data = await resp.json()
                
                survey_status = survey_data.get("response_status", "")
                is_closed = survey_status in ["closed", "ended"]
                response_count = response_data.get("total", 0)
                target_responses = tracking_info["target_responses"]
                
                is_completed = is_closed or (target_responses > 0 and response_count >= target_responses)
                
                await update_task_callback(
                    task_id=tracking_info["task_id"],
                    survey_id=survey_id,
                    response_count=response_count,
                    is_completed=is_completed,
                    survey_status=survey_status
                )
                
                if is_completed and not tracking_info["completed_notified"] and tracking_info["thread_id"]:
                    message = f"📊 Survey completed!\nSurvey ID: {survey_id}\nTotal responses: {response_count}\nTarget responses: {target_responses}\nStatus: {survey_status}"
                    
                    from flexus_client_kit import ckit_ask_model
                    http = await fclient.use_http()
                    await ckit_ask_model.thread_add_user_message(
                        http=http,
                        ft_id=tracking_info["thread_id"],
                        content=message,
                        who_is_asking="surveymonkey_integration",
                        ftm_alt=100,
                        role="user"
                    )
                    
                    tracking_info["completed_notified"] = True
                    logger.info(f"Posted completion message for survey {survey_id}")
                
                tracking_info["last_response_count"] = response_count
                
            except Exception as e:
                logger.error(f"Error updating survey {survey_id}: {e}")



