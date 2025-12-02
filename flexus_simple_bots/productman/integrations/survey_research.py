import json
import logging
import time
import aiohttp
import random
import os
from typing import Dict, Any

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("survey_research")

SURVEY_RESEARCH_TOOL = ckit_cloudtool.CloudTool(
    name="survey",
    description="Survey research: draft surveys, draft audience targeting, run campaigns. Start with op=\"help\".",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation: help, draft_survey, draft_auditory, run, responses, list, search_filters",
                "order": 1
            },
            "args": {
                "type": "object",
                "description": "Operation-specific arguments",
                "order": 2,
                "properties": {
                    "idea_name": {"type": "string", "description": "Idea folder name (kebab-case)", "order": 1001},
                    "hypothesis_name": {"type": "string", "description": "Hypothesis folder name (kebab-case)", "order": 1002},
                    "survey_content": {"type": "object", "description": "Survey with meta and section01-06", "order": 1003},
                    "study_name": {"type": "string", "description": "Prolific study name", "order": 1004},
                    "study_description": {"type": "string", "description": "Description for participants", "order": 1005},
                    "estimated_minutes": {"type": "integer", "description": "Estimated completion time (required)", "order": 1006},
                    "reward_cents": {"type": "integer", "description": "Payment per participant in cents (required)", "order": 1007},
                    "total_participants": {"type": "integer", "description": "Number of participants (required)", "order": 1008},
                    "filters": {"type": "object", "description": "Prolific filters from search_filters", "order": 1009},
                    "survey_id": {"type": "string", "description": "SurveyMonkey survey ID", "order": 1010},
                    "target_responses": {"type": "integer", "description": "Target responses to collect", "order": 1011},
                    "search_pattern": {"type": "string", "description": "Regex or list of patterns for filter search", "order": 1012}
                }
            }
        },
        "required": ["op"]
    }
)

SURVEY_RESEARCH_HELP = """
survey(op="help")
    Shows this help.

survey(op="search_filters", args={"search_pattern": "age|country"})
    Search Prolific filters. ALWAYS DO THIS BEFORE draft_auditory.
    Can accept list: {"search_pattern": ["age", "country"]}

survey(op="draft_survey", args={"idea_name": "...", "hypothesis_name": "...", "survey_content": {...}})
    Create survey draft at /customer-research/{idea}/{hypothesis}/survey-draft
    survey_content must have: survey.meta.title, section01-screening through section06-concept-validation

survey(op="draft_auditory", args={"idea_name": "...", "hypothesis_name": "...", "study_name": "...", "estimated_minutes": 10, "reward_cents": 150, "total_participants": 50, "filters": {...}})
    Create audience draft at /customer-research/{idea}/{hypothesis}/auditory-draft
    All numeric params are REQUIRED, no defaults.

survey(op="run", args={"idea_name": "...", "hypothesis_name": "..."})
    Execute campaign: create SurveyMonkey survey, Prolific study, connect, publish.
    Reads drafts from /customer-research/{idea}/{hypothesis}/

survey(op="responses", args={"idea_name": "...", "hypothesis_name": "...", "survey_id": "123456", "target_responses": 50})
    Fetch responses, save to /customer-research/{idea}/{hypothesis}/survey-results

survey(op="list", args={"idea_name": "..."})
    List all survey files for an idea.

Example survey_content structure:
{
    "survey": {"meta": {"title": "Survey Title", "description": "..."}},
    "section01-screening": {
        "title": "Screening",
        "questions": [
            {"q": "Are you a project manager?", "type": "yes_no", "required": true}
        ]
    },
    "section02-user-profile": {...},
    "section03-problem": {...},
    "section04-current-behavior": {...},
    "section05-impact": {...},
    "section06-concept-validation": {...}
}

Question types: yes_no, single_choice, multiple_choice, open_ended
For single_choice/multiple_choice: include "choices": ["option1", "option2", ...]
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

        filters_file = os.path.join(os.path.dirname(__file__), 'prolific_filters.json')
        with open(filters_file, 'r') as f:
            self.prolific_filters = json.load(f)

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
        elif op == "responses":
            return await self._handle_responses(toolcall, args)
        elif op == "list":
            return await self._handle_list(toolcall, args)
        elif op == "search_filters":
            return await self._handle_search_filters(args)
        else:
            return f"Unknown operation '{op}'. Valid operations: help, draft_survey, draft_auditory, run, responses, list, search_filters"

    async def _handle_draft_survey(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")
        survey_content = args.get("survey_content")

        if not idea_name:
            return "Error: idea_name is required"
        if not hypothesis_name:
            return "Error: hypothesis_name is required"
        if not survey_content:
            return "Error: survey_content is required"

        if "survey" not in survey_content or "meta" not in survey_content.get("survey", {}):
            return "Error: survey_content must have survey.meta with title"
        if not survey_content["survey"]["meta"].get("title"):
            return "Error: survey.meta.title is required"

        survey_obj = survey_content["survey"]
        formatted_content = {"survey": {"meta": survey_obj["meta"]}}
        formatted_content["survey"]["meta"]["hypothesis"] = hypothesis_name
        formatted_content["survey"]["meta"]["idea"] = idea_name
        formatted_content["survey"]["meta"]["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        validation_errors = []
        for key, value in survey_obj.items():
            if not key.startswith("section"):
                continue
            if not isinstance(value, dict):
                validation_errors.append(f"{key} must be an object")
                continue
            if "questions" not in value or not isinstance(value["questions"], list):
                validation_errors.append(f"{key} must have 'questions' array")
                continue
            if not value.get("title"):
                validation_errors.append(f"{key} must have 'title'")
                continue
            for q_idx, q in enumerate(value["questions"]):
                if not q.get("q"):
                    validation_errors.append(f"{key}.questions[{q_idx}] missing 'q' field")
                if not q.get("type"):
                    validation_errors.append(f"{key}.questions[{q_idx}] missing 'type' field")
                if q.get("type") in ["single_choice", "multiple_choice"] and not q.get("choices"):
                    validation_errors.append(f"{key}.questions[{q_idx}] type={q['type']} requires 'choices' array")
            formatted_content["survey"][key] = value

        section_count = sum(1 for k in formatted_content["survey"].keys() if k.startswith("section"))
        if section_count == 0:
            return "Error: survey_content must have section01-screening through section06-concept-validation"

        if validation_errors:
            return "Survey validation failed:\n  - " + "\n  - ".join(validation_errors)

        question_count = sum(len(s.get("questions", [])) for k, s in formatted_content["survey"].items() if k.startswith("section"))
        pdoc_path = f"/customer-research/{idea_name}/{hypothesis_name}/survey-draft"

        await self.pdoc_integration.pdoc_overwrite(
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
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")
        study_name = args.get("study_name", "")
        study_description = args.get("study_description", "")
        estimated_minutes = args.get("estimated_minutes")
        reward_cents = args.get("reward_cents")
        total_participants = args.get("total_participants")
        filters = args.get("filters", {})

        if not idea_name:
            return "Error: idea_name is required"
        if not hypothesis_name:
            return "Error: hypothesis_name is required"
        if not study_name:
            return "Error: study_name is required"
        if not study_description:
            return "Error: study_description is required"
        if estimated_minutes is None:
            return "Error: estimated_minutes is required (no default)"
        if reward_cents is None:
            return "Error: reward_cents is required (no default)"
        if total_participants is None:
            return "Error: total_participants is required (no default)"

        prolific_filters = []
        for filter_key, filter_value in filters.items():
            if filter_key in self.prolific_filters:
                filter_info = self.prolific_filters[filter_key]
                if filter_info["type"] == "range":
                    range_filter = {"filter_id": filter_key, "selected_range": {}}
                    filter_min = filter_info.get("min", 0)
                    filter_max = filter_info.get("max", 100)
                    
                    if isinstance(filter_value, dict):
                        if "min" in filter_value:
                            if filter_value["min"] < filter_min or filter_value["min"] > filter_max:
                                return f"Error: Value {filter_value['min']} for '{filter_key}' min is out of range [{filter_min}, {filter_max}]"
                            range_filter["selected_range"]["lower"] = filter_value["min"]
                        if "max" in filter_value:
                            if filter_value["max"] < filter_min or filter_value["max"] > filter_max:
                                return f"Error: Value {filter_value['max']} for '{filter_key}' max is out of range [{filter_min}, {filter_max}]"
                            range_filter["selected_range"]["upper"] = filter_value["max"]
                    elif isinstance(filter_value, (int, float)):
                        if filter_value < filter_min or filter_value > filter_max:
                            return f"Error: Value {filter_value} for '{filter_key}' is out of range [{filter_min}, {filter_max}]"
                        range_filter["selected_range"]["lower"] = filter_value
                    prolific_filters.append(range_filter)
                elif filter_info["type"] == "select":
                    values = filter_value if isinstance(filter_value, list) else [filter_value]
                    valid_choices = set(filter_info.get("choices", {}).keys())
                    
                    for val in values:
                        if str(val) not in valid_choices:
                            error_msg = f"Error: Invalid value '{val}' for filter '{filter_key}'.\n\n"
                            error_msg += f"Valid options for {filter_info['title']}:\n"
                            choices = filter_info.get("choices", {})
                            if len(choices) <= 20:
                                for code, label in choices.items():
                                    error_msg += f"  {code} = {label}\n"
                            else:
                                for code, label in list(choices.items())[:10]:
                                    error_msg += f"  {code} = {label}\n"
                                error_msg += f"  ... and {len(choices) - 10} more\n"
                            error_msg += f"\nUse string values like: [\"{list(choices.keys())[0]}\"]\n"
                            return error_msg
                    
                    prolific_filters.append({
                        "filter_id": filter_key,
                        "selected_values": [str(v) for v in values]
                    })
            else:
                error_msg = f"Error: Unknown filter '{filter_key}'.\n\n"
                error_msg += f"Use survey(op='search_filters', args={{'search_pattern': '{filter_key}'}}) to find available filters.\n\n"

                import re
                pattern = re.compile(filter_key, re.IGNORECASE)
                suggestions = []
                for fid, finfo in self.prolific_filters.items():
                    if pattern.search(fid) or pattern.search(finfo.get("title", "")):
                        suggestions.append(fid)

                if suggestions:
                    error_msg += f"Did you mean one of these filters?\n"
                    for s in suggestions[:5]:
                        filter_info = self.prolific_filters[s]
                        error_msg += f"\n• {s}: {filter_info['title']} ({filter_info['type']})"
                        if filter_info['type'] == 'range':
                            error_msg += f"\n  Schema: {{'min': {filter_info.get('min', 0)}, 'max': {filter_info.get('max', 100)}}}"
                        elif filter_info['type'] == 'select':
                            choices = filter_info.get('choices', {})
                            if len(choices) <= 5:
                                error_msg += f"\n  Values (use strings!): {list(choices.keys())}"
                                error_msg += f"\n  Example: \"{s}\": [\"{list(choices.keys())[0]}\"]"
                            else:
                                error_msg += f"\n  Values (use strings!): {list(choices.keys())[:5]} ... ({len(choices)} total)"
                                error_msg += f"\n  Example: \"{s}\": [\"{list(choices.keys())[0]}\"]"

                return error_msg
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
                    "reject_fast_submissions": False,
                    "completion_codes": [{
                        "code": f"COMPLETE_{random.randint(10000000, 99999999)}",
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

        draft_path = f"/customer-research/{idea_name}/{hypothesis_name}/auditory-draft"

        await self.pdoc_integration.pdoc_overwrite(
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

    async def _handle_list(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")

        if not idea_name:
            return "Error: idea_name is required"

        if not self.pdoc_integration:
            return "Error: pdoc integration not configured"

        try:
            base_path = f"/customer-research/{idea_name}"
            items = await self.pdoc_integration.pdoc_list(base_path)

            survey_files = []
            for item in items:
                if item.is_folder:
                    hyp_items = await self.pdoc_integration.pdoc_list(item.path)
                    for hi in hyp_items:
                        if not hi.is_folder and ("survey-draft" in hi.path or "survey-results" in hi.path or "auditory-draft" in hi.path):
                            survey_files.append(hi.path)

            if not survey_files:
                return f"No survey files found for idea '{idea_name}'"

            result = f"📋 Survey files for '{idea_name}':\n\n"
            for p in sorted(survey_files):
                if "survey-draft" in p:
                    result += f"📝 {p}\n"
                elif "auditory-draft" in p:
                    result += f"🎯 {p}\n"
                elif "survey-results" in p:
                    result += f"📊 {p}\n"

            return result

        except KeyError as e:
            return f"Error listing surveys: missing key {e}"
        except json.JSONDecodeError as e:
            return f"Error listing surveys: invalid JSON - {e}"

    async def _handle_search_filters(self, args: Dict[str, Any]) -> str:
        import re
        search_patterns = args.get("search_pattern", "")

        if not search_patterns:
            return "Error: search_pattern is required"

        if isinstance(search_patterns, str):
            search_patterns = [search_patterns]

        all_matches = {}
        for search_pattern in search_patterns:
            try:
                pattern = re.compile(search_pattern, re.IGNORECASE)
            except re.error as e:
                return f"Error: Invalid regex pattern '{search_pattern}' - {e}"

            for filter_id, filter_info in self.prolific_filters.items():
                if pattern.search(filter_info.get("title", "")) or pattern.search(filter_id):
                    if filter_id not in all_matches:
                        all_matches[filter_id] = filter_info

        if not all_matches:
            return f"No filters found matching patterns: {', '.join(search_patterns)}"

        total_found = len(all_matches)
        max_display = 50
        
        result = f"Found {total_found} filters"
        if total_found > max_display:
            result += f" (showing first {max_display}, use more specific search to narrow results)"
        result += ":\n\n"
        
        for filter_id, filter_info in list(all_matches.items())[:max_display]:
            result += f"• {filter_id}: {filter_info.get('title', '')} ({filter_info.get('type', '')})\n"
            
            if filter_info["type"] == "range":
                min_val = filter_info.get("min", 0)
                max_val = filter_info.get("max", 100)
                result += f"  Range: {min_val} to {max_val}\n"

            elif filter_info["type"] == "select":
                choices = filter_info.get("choices", {})
                num_choices = len(choices)
                
                if num_choices <= 5:
                    result += f"  Options ({num_choices}):\n"
                    for code, label in choices.items():
                        result += f"    {code} = {label}\n"
                elif num_choices <= 15:
                    result += f"  Options ({num_choices}):\n"
                    for code, label in list(choices.items())[:10]:
                        result += f"    {code} = {label}\n"
                    if num_choices > 10:
                        result += f"    ... and {num_choices - 10} more\n"
                else:
                    result += f"  Options ({num_choices} total):\n"
                    for code, label in list(choices.items()):
                        result += f"    {code} = {label}\n"

            result += "\n"
        
        if total_found > max_display:
            result += f"\n⚠️ {total_found - max_display} more filters not shown.\n"
            result += "Tip: Use more specific search patterns to narrow results.\n"
            result += f'Example: survey(op="search_filters", args={{"search_pattern": "^age$|^sex$"}})\n'
        
        return result

    async def _prepare_run_confirmation(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")

        if not idea_name or not hypothesis_name:
            return "Error: idea_name and hypothesis_name are required"

        auditory_draft_path = f"/customer-research/{idea_name}/{hypothesis_name}/auditory-draft"
        auditory_doc = await self.pdoc_integration.pdoc_cat(auditory_draft_path)
        auditory_content = auditory_doc.pdoc_content

        if not auditory_content or "prolific_auditory_draft" not in auditory_content:
            return f"Error: Invalid auditory draft at {auditory_draft_path}"

        cost_estimate = auditory_content["prolific_auditory_draft"]["cost_estimate"]
        total_cost = cost_estimate["total"]

        raise ckit_cloudtool.NeedsConfirmation(
            confirm_setup_key="can_run_survey_campaign",
            confirm_command=f'run survey campaign £{total_cost / 100:.2f}',
            confirm_explanation=f"This will create SurveyMonkey survey and Prolific study costing £{total_cost / 100:.2f}. Please confirm.",
        )

    async def _handle_run(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")

        if not idea_name or not hypothesis_name:
            return "Error: idea_name and hypothesis_name are required"

        survey_draft_path = f"/customer-research/{idea_name}/{hypothesis_name}/survey-draft"
        auditory_draft_path = f"/customer-research/{idea_name}/{hypothesis_name}/auditory-draft"

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
            
            publish_result = await self._publish_prolific_study(study_id)

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

            if "error" in publish_result:
                result = f"⚠️ Survey campaign created but not published!\n\n"
                result += f"📋 SurveyMonkey URL: {survey_url}\n"
                result += f"🎯 Prolific Study ID: {study_id}\n"
                result += f"❌ Publishing error: {publish_result['error']}\n\n"
                result += f"The study was created but needs manual publishing in Prolific dashboard.\n\n"
            else:
                result = f"✅ Survey campaign launched and published successfully!\n\n"
                result += f"📋 SurveyMonkey URL: {survey_url}\n"
                result += f"🎯 Prolific Study ID: {study_id}\n"
                result += f"📊 Status: {publish_result.get('status', 'ACTIVE')}\n"
                result += f"✅ Participants are now being recruited!\n\n"
            
            result += f"📝 Survey draft: {survey_draft_path}\n"
            result += f"📝 Auditory draft: {auditory_draft_path}"

            return result

        except KeyError as e:
            return f"Error executing campaign: missing key {e}"
        except aiohttp.ClientError as e:
            return f"Error executing campaign: API request failed - {e}"

    async def _handle_responses(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        survey_id = args.get("survey_id", "")
        target_responses = args.get("target_responses", 0)
        idea_name = args.get("idea_name", "")
        hypothesis_name = args.get("hypothesis_name", "")

        if not survey_id:
            return "Error: survey_id is required"
        if not target_responses or target_responses <= 0:
            return "Error: target_responses is required and must be greater than 0"
        if not idea_name:
            return "Error: idea_name is required"
        if not hypothesis_name:
            return "Error: hypothesis_name is required"

        all_responses = []
        page, per_page, total = 1, 100, None

        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                        f"https://api.surveymonkey.com/v3/surveys/{survey_id}/responses/bulk",
                        headers=self._sm_headers(),
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

        completion_rate = (len(all_responses) / target_responses * 100) if target_responses > 0 else 0
        is_completed = target_responses > 0 and len(all_responses) >= target_responses

        result = f"📊 Survey Responses (Survey ID: {survey_id})\n"
        result += f"Total responses: {len(all_responses)} / {target_responses} ({completion_rate:.1f}%)\n"
        result += f"Status: {'COMPLETED ✅' if is_completed else 'IN_PROGRESS ⏳'}\n"
        result += "=" * 50 + "\n\n"

        if not all_responses:
            result += "No responses found yet.\n"

        responses_data = []
        for idx, r in enumerate(all_responses, 1):
            response_entry = {
                "response_id": r.get('id', 'N/A'),
                "status": r.get('response_status', 'N/A'),
                "submitted": r.get('date_modified') or r.get('date_created', 'N/A'),
                "answers": r
            }

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
            responses_data.append(response_entry)

        if self.pdoc_integration:
            results_path = f"/customer-research/{idea_name}/{hypothesis_name}/survey-results"
            results_content = {
                "survey_results": {
                    "meta": {
                        "survey_id": survey_id,
                        "total_responses": len(all_responses),
                        "target_responses": target_responses,
                        "completion_rate": completion_rate,
                        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "idea": idea_name,
                        "hypothesis": hypothesis_name,
                        "status": "COMPLETED" if is_completed else "IN_PROGRESS"
                    },
                    "responses": responses_data,
                    "summary": {
                        "total_collected": len(all_responses),
                        "completion_status": "COMPLETED" if is_completed else "IN_PROGRESS"
                    }
                }
            }

            try:
                await self.pdoc_integration.pdoc_overwrite(
                    results_path,
                    json.dumps(results_content, indent=2),
                    toolcall.fcall_ft_id
                )
                result += f"\n📁 Results saved to: {results_path}\n"
                result += f"✍️ {results_path}\n\n"
            except aiohttp.ClientError as e:
                result += f"\n⚠️ Failed to save results (API error): {e}\n\n"
            except json.JSONDecodeError as e:
                result += f"\n⚠️ Failed to save results (JSON error): {e}\n\n"

        if is_completed:
            result += "🎉 SURVEY COMPLETED! All target responses collected.\n"
            result += "✅ You should now move the kanban task to DONE state.\n"
        else:
            result += f"⏳ Survey still in progress. {target_responses - len(all_responses)} more responses needed.\n"
            result += "❌ DO NOT finish the task yet. Check again later for more responses.\n"

        return result

    def track_survey_task(self, task):
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

            except aiohttp.ClientError as e:
                logger.error(f"Error updating survey {survey_id}: API request failed", exc_info=e)
            except KeyError as e:
                logger.error(f"Error updating survey {survey_id}: missing key {e}")

    async def update_task_survey_status(self, task_id: str, survey_id: str, response_count: int, is_completed: bool, survey_status: str):
        from flexus_client_kit import ckit_kanban

        try:
            if survey_id not in self.tracked_surveys:
                logger.warning(f"Survey {survey_id} not in tracked surveys")
                return
                
            tracking_info = self.tracked_surveys[survey_id]
            target_responses = tracking_info.get("target_responses", 100)
            completion_rate = (response_count / target_responses * 100) if target_responses > 0 else 0
            
            details = {
                "survey_id": survey_id,
                "target_responses": target_responses,
                "survey_status": {
                    "responses": response_count,
                    "completion_rate": completion_rate,
                    "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_completed": is_completed,
                    "status": survey_status,
                    "completed_notified": tracking_info.get("completed_notified", False)
                }
            }

            await ckit_kanban.update_task_details(self.fclient, task_id, details)
            logger.info(f"Updated task {task_id} survey status: {response_count}/{target_responses} responses, completed={is_completed}")

        except aiohttp.ClientError as e:
            logger.error(f"Failed to update task survey status: API request failed", exc_info=e)
        except KeyError as e:
            logger.error(f"Failed to update task survey status: missing key {e}")

    async def _create_surveymonkey_survey(self, survey_content: Dict, completion_code: str) -> Dict:
        survey_obj = survey_content.get("survey", {})
        meta = survey_obj.get("meta", {})
        survey_title = meta.get("title", "Survey")
        survey_description = meta.get("description", "")

        questions = []
        for section_key in sorted(survey_obj.keys()):
            if not section_key.startswith("section"):
                continue
            section = survey_obj[section_key]
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
            }]
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
            "name": "Prolific Collector",
            "thank_you_message": (
                "Thank you for completing this survey!\n\n"
                f"IMPORTANT: Please copy this completion code and paste it in Prolific to receive your payment:\n\n{completion_code}"
            )
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
                "type": "at_least",
                "amount": "1"
            }

        return sm_q

    async def _create_prolific_study(self, auditory_content: Dict, survey_info: Dict) -> str:
        draft = auditory_content.get("prolific_auditory_draft", {})
        meta = draft.get("meta", {})
        params = draft.get("parameters", {})

        study_name = meta["study_name"]
        study_description = params["study_description"]
        estimated_minutes = params["estimated_minutes"]
        reward_cents = params["reward_cents"]
        total_participants = params["total_participants"]
        completion_codes = params["completion_codes"]

        filters = params.get("filters", [])
        survey_url = survey_info["url"]

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
            "filters": filters,
            "study_labels": ["survey"],
            "submissions_config": {
                "max_submissions_per_participant": 1
            }
        }

        study = await self._make_request(
            "POST",
            "https://api.prolific.com/api/v1/studies/",
            self._prolific_headers(),
            study_payload
        )

        return study["id"]
    
    async def _publish_prolific_study(self, study_id: str) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.prolific.com/api/v1/studies/{study_id}/",
                    headers=self._prolific_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    logger.error(f"Error getting study details: {error_body}")
                    return {"error": f"Error getting study details: {error_body}"}
                study_details = await resp.json()

            async with session.post(
                    f"https://api.prolific.com/api/v1/studies/{study_id}/transition/",
                    headers=self._prolific_headers(),
                    json={"action": "PUBLISH"},
                    timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status >= 400:
                    error_body = await resp.text()
                    logger.error(f"Prolific publish error: {error_body}")
                    return {"error": f"Error publishing study: {error_body}"}

                study = await resp.json()
                return {"status": study.get("status", "ACTIVE"), "published": True}
