import json
import logging
from typing import Dict, Any

import aiohttp

from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.productman.integrations import survey_monkey_mock

aiohttp = survey_monkey_mock.MockAiohttp()


logger = logging.getLogger("survey_monkey")

SM_BASE = "https://api.surveymonkey.com/v3"

CREATE_SURVEY_TOOL = ckit_cloudtool.CloudTool(
    name="create_surveymonkey_survey",
    description="Create a SurveyMonkey survey from idea documents",
    parameters={
        "type": "object",
        "properties": {
            "idea_name": {
                "type": "string",
                "description": "Name of the idea folder containing documents"
            },
            "survey_title": {
                "type": "string",
                "description": "Title for the survey"
            },
            "survey_description": {
                "type": "string",
                "description": "Description of the survey"
            },
            "questions": {
                "type": "array",
                "description": "List of survey questions",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "type": {"type": "string", "enum": ["single_choice", "multiple_choice", "open_ended", "rating_scale", "nps"]},
                        "choices": {"type": "array", "items": {"type": "string"}},
                        "required": {"type": "boolean"}
                    }
                }
            }
        },
        "required": ["idea_name", "survey_title", "questions"]
    }
)

GET_RESPONSES_TOOL = ckit_cloudtool.CloudTool(
    name="get_surveymonkey_responses",
    description="Fetch all SurveyMonkey responses for a survey",
    parameters={
        "type": "object",
        "properties": {
            "survey_id": {
                "type": "string",
                "description": "SurveyMonkey survey ID"
            }
        },
        "required": ["survey_id"]
    }
)


class IntegrationSurveyMonkey:
    def __init__(self, access_token: str, pdoc_integration=None):
        self.access_token = access_token
        self.pdoc_integration = pdoc_integration

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

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

    async def create_survey(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        idea_name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "idea_name", "")
        survey_title = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "survey_title", "")
        survey_description = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "survey_description", "")
        questions = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "questions", [])

        if not idea_name or not survey_title or not questions:
            return "Error: idea_name, survey_title, and questions are required"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        survey_data = {
            "title": survey_title,
            "description": survey_description,
            "questions": questions
        }

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

        pdoc_path = f"/customer-research/{idea_name}/{survey_title.lower().replace(' ', '-')}-survey-monkey-query"
        survey_data["meta"] = {
            "survey_id": survey_id,
            "survey_url": survey_url,
            "collector_id": collector["id"]
        }
        await self.pdoc_integration.pdoc_create(pdoc_path, json.dumps(survey_data, indent=2), toolcall.fcall_ft_id)

        result = f"✅ Survey created successfully!\n\n"
        result += f"📋 Survey ID: {survey_id}\n"
        result += f"🔗 Survey URL: {survey_url}\n"
        result += f"📊 {len(questions)} questions\n"
        result += f"📁 Saved to: {pdoc_path}\n"
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

    async def get_responses(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        survey_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "survey_id", "")
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
