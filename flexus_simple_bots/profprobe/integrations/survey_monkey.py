import json
import logging
from typing import Dict, Any

import aiohttp

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("survey_monkey")

SM_BASE = "https://api.surveymonkey.com/v3"

CREATE_SURVEY_TOOL = ckit_cloudtool.CloudTool(
    name="create_surveymonkey_survey",
    description="Create a SurveyMonkey survey from a pdoc survey definition",
    parameters={
        "type": "object",
        "properties": {
            "pdoc_path": {
                "type": "string",
                "description": "Path to the pdoc containing survey definition (e.g. /customer-research/unicorn-horn-car-survey-query/my-survey)"
            },
            "collector_name": {
                "type": "string",
                "description": "Name for the weblink collector",
                "default": "Survey link"
            }
        },
        "required": ["pdoc_path"]
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



def parse_pdoc_to_survey_questions(pdoc_content: dict) -> tuple[str, str, list]:
    title = pdoc_content.get("title", "Survey")
    description = pdoc_content.get("description", "")
    questions = []
    for section_key, section_data in pdoc_content.items():
        if section_key in ["title", "description", "meta"]:
            continue
        for q_key, q_data in section_data.items():
            q_dict = {
                "text": q_data["question"],
                "type": q_data.get("type", "open_ended"),
                "choices": q_data.get("choices", []),
                "required": q_data.get("required", False)
            }
            if "scale_min" in q_data:
                q_dict["scale_min"] = q_data["scale_min"]
            if "scale_max" in q_data:
                q_dict["scale_max"] = q_data["scale_max"]
            questions.append(q_dict)
    return title, description, questions


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
                "family": "matrix",
                "subtype": "rating",
                "answers": {
                    "rows": [{"text": ""}],
                    "choices": [{"text": str(i), "weight": i} for i in range(scale_min, scale_max + 1)]
                }
            },
            "nps": {
                "family": "matrix",
                "subtype": "nps",
                "answers": {
                    "rows": [{"text": ""}],
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
                "subtype": "date"
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

        pdoc_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "pdoc_path", "")
        collector_name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "collector_name", "Survey link")

        if not pdoc_path:
            return "Error: pdoc_path is required"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        doc = await self.pdoc_integration.pdoc_cat(pdoc_path)
        content = json.loads(doc.pdoc_content)
        title, description, questions = parse_pdoc_to_survey_questions(content)
        if not questions:
            return f"Error: No questions found in {pdoc_path}"

        sm_questions = [self.convert_question_to_sm(q) for q in questions]
        survey_payload = {
            "title": title,
            "pages": [
                {
                    "title": "Page 1",
                    "description": description,
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
                "name": collector_name,
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

        content["meta"] = content.get("meta", {})
        content["meta"]["survey_id"] = survey_id
        content["meta"]["survey_url"] = collector.get("url", "")
        content["meta"]["collector_id"] = collector["id"]
        await self.pdoc_integration.pdoc_write(pdoc_path, json.dumps(content, indent=2), None)

        result = f"✅ Survey created successfully!\n\n"
        result += f"📋 Survey ID: {survey_id}\n"
        result += f"🔗 Survey URL: {collector.get('url', 'N/A')}\n"
        result += f"📊 Collector ID: {collector['id']}\n\n"
        result += f"Survey '{title}' with {len(questions)} questions is ready to share.\n"
        result += f"✍🏻 {pdoc_path}"
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
