import logging
from typing import Dict, Any, List

import aiohttp

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("prolific")

PROLIFIC_BASE = "https://api.prolific.com/api/v1"

CREATE_STUDY_TOOL = ckit_cloudtool.CloudTool(
    name="create_prolific_study",
    description="Create a Prolific study for participant recruitment",
    parameters={
        "type": "object",
        "properties": {
            "survey_url": {
                "type": "string",
                "description": "SurveyMonkey survey URL"
            },
            "study_name": {
                "type": "string",
                "description": "Name for the Prolific study"
            },
            "study_description": {
                "type": "string",
                "description": "Description for participants"
            },
            "estimated_minutes": {
                "type": "integer",
                "description": "Estimated completion time",
                "minimum": 1
            },
            "reward_cents": {
                "type": "integer",
                "description": "Payment per participant in cents",
                "minimum": 1
            },
            "total_participants": {
                "type": "integer",
                "description": "Number of participants",
                "minimum": 1
            },
            "filters": {
                "type": "object",
                "description": "Demographic filters",
                "properties": {
                    "min_age": {"type": "integer"},
                    "max_age": {"type": "integer"},
                    "countries": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "required": ["survey_url", "study_name", "estimated_minutes", "reward_cents", "total_participants"]
    }
)
PUBLISH_PROLIFIC_STUDY_TOOL = ckit_cloudtool.CloudTool(
    name="publish_prolific_study",
    description="""Publish a Prolific study to start recruiting participants.
    WARNING: This spends real money! Requires explicit user approval.""",
    parameters={
        "type": "object",
        "properties": {
            "study_id": {
                "type": "string",
                "description": "Prolific study ID to publish"
            },
            "user_approved": {
                "type": "boolean",
                "description": "Has the user explicitly approved the cost?"
            }
        },
        "required": ["study_id", "user_approved"]
    }
)

GET_STUDY_STATUS_TOOL = ckit_cloudtool.CloudTool(
    name="get_prolific_study_status",
    description="Get the current status and submission counts for a Prolific study",
    parameters={
        "type": "object",
        "properties": {
            "study_id": {
                "type": "string",
                "description": "Prolific study ID"
            }
        },
        "required": ["study_id"]
    }
)


class IntegrationProlific:
    def __init__(self, api_token: str, surveymonkey_integration=None, pdoc_integration=None):
        self.api_token = api_token
        self.surveymonkey_integration = surveymonkey_integration
        self.pdoc_integration = pdoc_integration

    def _headers(self):
        return {
            "Authorization": f"Token {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _build_filters(self, filters: Dict[str, Any]) -> List[Dict]:
        prolific_filters = []

        if "min_age" in filters or "max_age" in filters:
            age_filter = {
                "filter_id": "age",
                "selected_range": {}
            }
            if "min_age" in filters:
                age_filter["selected_range"]["lower"] = filters["min_age"]
            if "max_age" in filters:
                age_filter["selected_range"]["upper"] = filters["max_age"]
            prolific_filters.append(age_filter)

        if "countries" in filters and filters["countries"]:
            prolific_filters.append({
                "filter_id": "current_country_of_residence",
                "selected_values": filters["countries"]
            })

        if "min_approval_rate" in filters:
            prolific_filters.append({
                "filter_id": "approval_rate",
                "selected_range": {
                    "lower": filters["min_approval_rate"]
                }
            })

        return prolific_filters

    async def create_study(self, toolcall: ckit_cloudtool.FCloudtoolCall,
                           model_produced_args: Dict[str, Any]) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        survey_url = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "survey_url", "")
        study_name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "study_name", "")
        study_description = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "study_description", "")
        estimated_minutes = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "estimated_minutes", 5)
        reward_cents = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "reward_cents", 100)
        total_participants = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "total_participants", 50)
        filters = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "filters", {})

        if not all([survey_url, study_name]):
            return "Error: survey_url and study_name are required"

        if "?" in survey_url:
            survey_url += "&participant_id={{%PROLIFIC_PID%}}"
        else:
            survey_url += "?participant_id={{%PROLIFIC_PID%}}"

        completion_code = f"COMPLETE_{study_name[:6].upper()}"

        study_payload = {
            "name": study_name,
            "description": study_description,
            "external_study_url": survey_url,
            "prolific_id_option": "url_parameters",
            "completion_codes": [{
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "MANUALLY_REVIEW"}]
            }],
            "estimated_completion_time": int(estimated_minutes),
            "maximum_allowed_time": int(estimated_minutes) * 5,
            "reward": int(reward_cents),
            "total_available_places": int(total_participants),
            "device_compatibility": ["desktop", "mobile", "tablet"],
            "peripheral_requirements": [],
            "filters": self._build_filters(filters),
            "submissions_config": {
                "max_submissions_per_participant": 1
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{PROLIFIC_BASE}/studies/",
                    headers=self._headers(),
                    json=study_payload,
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    logger.error(f"Prolific API error: {error_body}")
                    return f"Error creating Prolific study: {error_body}"

                study = await resp.json()
                study_id = study["id"]

        service_fee = reward_cents * total_participants * 0.33
        vat = service_fee * 0.20
        total_cost = (reward_cents * total_participants) + service_fee + vat

        result = f"""✅ Prolific Study Created (UNPUBLISHED)

Study ID: {study_id}
Status: UNPUBLISHED
Participants: {total_participants}
Reward: £{reward_cents / 100:.2f} per participant
Completion Code: {completion_code}

💰 Estimated Cost:
  Rewards: £{(reward_cents * total_participants) / 100:.2f}
  Service Fee: £{service_fee / 100:.2f}
  VAT: £{vat / 100:.2f}
  TOTAL: £{total_cost / 100:.2f}

⚠️ Next: Use 'publish_prolific_study' with user approval to start recruiting."""

        return result

    async def publish_study(self, toolcall: ckit_cloudtool.FCloudtoolCall,
                            model_produced_args: Dict[str, Any]) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        study_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "study_id", "")
        user_approved = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "user_approved", False)

        if not study_id:
            return "Error: study_id is required"

        if not user_approved:
            return """❌ Cannot publish study without user approval!
            
Please confirm with the user:
- They understand the cost
- They approve spending the money
- Their account has sufficient balance

Then call this tool again with user_approved=true"""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{PROLIFIC_BASE}/studies/{study_id}/transition/",
                    headers=self._headers(),
                    json={"action": "PUBLISH"},
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    logger.error(f"Prolific publish error: {error_body}")
                    return f"Error publishing study: {error_body}"

                study = await resp.json()

        result = f"""🚀 Study Published Successfully!

Study ID: {study_id}
Status: {study.get('status', 'ACTIVE')}

✅ Participants are now being recruited!
Monitor progress with 'get_prolific_study_status'"""

        return result

    async def get_study_status(self, toolcall: ckit_cloudtool.FCloudtoolCall,
                               model_produced_args: Dict[str, Any]) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        study_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "study_id", "")
        if not study_id:
            return "Error: study_id is required"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{PROLIFIC_BASE}/studies/{study_id}/",
                    headers=self._headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    return f"Error getting study: {error_body}"
                study = await resp.json()

            async with session.get(
                    f"{PROLIFIC_BASE}/studies/{study_id}/submissions/",
                    headers=self._headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    return f"Error getting submissions: {error_body}"
                submissions_data = await resp.json()

        submissions = submissions_data.get("results", [])
        status_counts = {}
        for sub in submissions:
            status = sub.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1

        result = f"""📊 Prolific Study Status

Study ID: {study_id}
Status: {study.get('status', 'UNKNOWN')}
Total Places: {study.get('total_available_places', 0)}
Places Taken: {study.get('places_taken', 0)}

Submission Status:
"""
        for status, count in status_counts.items():
            result += f"  • {status}: {count}\n"

        if study.get('status') == 'COMPLETED':
            result += "\n✅ Study is complete! All places filled."
        elif study.get('status') == 'ACTIVE':
            remaining = study.get('total_available_places', 0) - study.get('places_taken', 0)
            result += f"\n⏳ Recruiting... {remaining} places remaining"

        return result
