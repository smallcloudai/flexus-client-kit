import logging
import time
from typing import Dict, Any, List

from flexus_client_kit import ckit_cloudtool
from flexus_simple_bots.productman.integrations import prolific_mock

# import aiohttp
aiohttp = prolific_mock.MockAiohttp()

logger = logging.getLogger("prolific")

PROLIFIC_BASE = "https://api.prolific.com/api/v1"

PROLIFIC_TOOL = ckit_cloudtool.CloudTool(
    name="prolific",
    description="Manage Prolific studies: create, publish, check status. Start with op=\"help\" to see all operations.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation to perform: help, create, publish, status",
                "order": 1
            },
            "args": {
                "type": "object",
                "description": "Operation-specific arguments",
                "order": 2,
                "properties": {
                    # create operation
                    "survey_url": {"type": "string", "description": "SurveyMonkey survey URL (for create)", "order": 1001},
                    "study_name": {"type": "string", "description": "Name for the Prolific study (for create)", "order": 1002},
                    "study_description": {"type": "string", "description": "Description for participants (for create)", "order": 1003},
                    "estimated_minutes": {"type": "integer", "description": "Estimated completion time in minutes (for create)", "order": 1004},
                    "reward_cents": {"type": "integer", "description": "Payment per participant in cents (for create)", "order": 1005},
                    "total_participants": {"type": "integer", "description": "Number of participants to recruit (for create)", "order": 1006},
                    "filters": {
                        "type": "object",
                        "description": "Demographic filters (for create)",
                        "order": 1007,
                        "properties": {
                            "min_age": {"type": "integer", "description": "Minimum age"},
                            "max_age": {"type": "integer", "description": "Maximum age"},
                            "countries": {"type": "array", "items": {"type": "string"}, "description": "List of country codes (temporarily disabled - needs mapping)"}
                        }
                    },
                    # publish operation
                    "study_id": {"type": "string", "description": "Prolific study ID (for publish/status)", "order": 1008},
                }
            }
        },
        "required": ["op"]
    }
)

PROLIFIC_HELP = """
prolific()
    Shows this help.

prolific(op="help")
    Shows this help with examples.

prolific(op="create", args={"survey_url": "...", "study_name": "...", "estimated_minutes": 10, "reward_cents": 150, "total_participants": 50})
    Create a Prolific study (UNPUBLISHED).
    Required: survey_url, study_name, estimated_minutes, reward_cents, total_participants
    Optional: study_description, filters (min_age, max_age, countries)
    Returns study ID and cost estimate.

prolific(op="publish", args={"study_id": "..."})
    Publish a study to start recruiting participants.

prolific(op="status", args={"study_id": "..."})
    Get current status and submission counts for a study.

Examples:
    # Create study
    prolific(op="create", args={
        "survey_url": "https://surveymonkey.com/r/ABC123",
        "study_name": "Task Management Survey",
        "study_description": "15-minute survey about task delegation",
        "estimated_minutes": 15,
        "reward_cents": 200,
        "total_participants": 100,
        "filters": {
            "min_age": 25,
            "max_age": 55
        }
    })

    # Publish after user approval
    prolific(op="publish", args={"study_id": "abc123"})

    # Check status
    prolific(op="status", args={"study_id": "abc123"})
"""


class IntegrationProlific:
    def __init__(self, api_token: str, surveymonkey_integration=None, pdoc_integration=None, fclient=None):
        self.api_token = api_token
        self.surveymonkey_integration = surveymonkey_integration
        self.pdoc_integration = pdoc_integration
        self.fclient = fclient

    def _headers(self):
        return {
            "Authorization": f"Token {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def handle_prolific(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not model_produced_args:
            return PROLIFIC_HELP

        op = model_produced_args.get("op", "help")
        args = model_produced_args.get("args", {})

        if op == "help":
            return PROLIFIC_HELP

        elif op == "create":
            return await self._handle_create(toolcall, args)

        elif op == "publish":
            if toolcall.confirmed_by_human:
                return await self._handle_publish(toolcall, args)
            else:
                raise ckit_cloudtool.NeedsConfirmation(
                    confirm_setup_key="can_start_prolific_campaign",
                    confirm_command=f'publish {args.get("study_id", "")}',
                    confirm_explanation="This command will spend money. Please confirm that you want to proceed.",
                )

        elif op == "status":
            return await self._handle_status(toolcall, args)

        else:
            return f"Unknown operation '{op}'. Valid operations: help, create, publish, status\n\n{PROLIFIC_HELP}"

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

        if "min_approval_rate" in filters:
            prolific_filters.append({
                "filter_id": "approval-rate",
                "selected_range": {
                    "lower": filters["min_approval_rate"]
                }
            })

        return prolific_filters

    async def _handle_create(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_url = args.get("survey_url", "")
        study_name = args.get("study_name", "")
        study_description = args.get("study_description", "")
        estimated_minutes = args.get("estimated_minutes", 5)
        reward_cents = args.get("reward_cents", 100)
        total_participants = args.get("total_participants", 50)
        filters = args.get("filters", {})

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
            "completion_option": "url",
            "completion_codes": [{
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "AUTOMATICALLY_APPROVE"}]
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

    async def _handle_publish(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        study_id = args.get("study_id", "")

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
                    return f"Error getting study details: {error_body}"
                study_details = await resp.json()

            survey_url = study_details.get("external_study_url", "")
            total_participants = study_details.get("total_available_places", 0)
            survey_id = ""
            if "surveymonkey.com/r/" in survey_url:
                survey_id = survey_url.split("/r/")[-1].split("?")[0].split("&")[0]

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

        if survey_id and toolcall.fcall_ft_id and self.fclient:
            from flexus_client_kit import ckit_kanban
            import json

            try:
                # XXX use rcx.tasks
                tasks = await ckit_kanban.get_tasks_by_thread(self.fclient, toolcall.fcall_ft_id)

                for task in tasks:
                    task_details = task.ktask_details if isinstance(task.ktask_details, dict) else json.loads(task.ktask_details)
                    task_details["survey_id"] = survey_id
                    task_details["target_responses"] = total_participants
                    task_details["prolific_study_id"] = study_id
                    task_details["survey_status"] = {
                        "responses": 0,
                        "completion_rate": 0.0,
                        "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "completed_notified": False
                    }

                    await ckit_kanban.update_task_details(self.fclient, task.ktask_id, task_details)
                    result += f"\n\n📋 Updated task {task.ktask_id} with survey tracking info"
            except Exception as e:
                logger.error(f"Failed to update task with survey info: {e}")

        return result

    async def _handle_status(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        study_id = args.get("study_id", "")
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
