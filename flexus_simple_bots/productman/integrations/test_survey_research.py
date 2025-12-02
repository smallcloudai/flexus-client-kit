import pytest
import json
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock

from flexus_simple_bots.productman.integrations import survey_research
from flexus_simple_bots.productman.integrations import survey_research_mock
from flexus_client_kit import ckit_cloudtool


@dataclass
class MockPdocItem:
    path: str
    is_folder: bool


@dataclass
class MockPdocDocument:
    pdoc_content: Dict[str, Any]


class MockPdocIntegration:
    def __init__(self):
        self.storage: Dict[str, Dict[str, Any]] = {}
        self.list_items: Dict[str, List[MockPdocItem]] = {}

    async def pdoc_overwrite(self, path: str, content: str, ft_id: str):
        self.storage[path] = json.loads(content)

    async def pdoc_cat(self, path: str) -> MockPdocDocument:
        if path not in self.storage:
            raise KeyError(f"Path not found: {path}")
        return MockPdocDocument(pdoc_content=self.storage[path])

    async def pdoc_list(self, base_path: str) -> List[MockPdocItem]:
        return self.list_items.get(base_path, [])

    def set_list_items(self, base_path: str, items: List[MockPdocItem]):
        self.list_items[base_path] = items


class MockFClient:
    async def use_http(self):
        return AsyncMock()


def make_toolcall(ft_id: str = "test_ft_123", confirmed: bool = False) -> ckit_cloudtool.FCloudtoolCall:
    return ckit_cloudtool.FCloudtoolCall(
        caller_fuser_id="test@example.com",
        located_fgroup_id="test_group",
        fcall_id="fcall_123",
        fcall_ft_id=ft_id,
        fcall_ft_btest_name="",
        fcall_ftm_alt=0,
        fcall_called_ftm_num=1,
        fcall_call_n=0,
        fcall_name="survey",
        fcall_arguments="{}",
        fcall_created_ts=time.time(),
        fcall_untrusted_key="key123",
        connected_persona_id="persona_123",
        ws_id="ws_123",
        subgroups_list=[],
        confirmed_by_human=confirmed,
    )


def make_valid_survey_content() -> Dict[str, Any]:
    return {
        "survey": {
            "meta": {
                "title": "Test Survey",
                "description": "A test survey for validation"
            }
        },
        "section01-screening": {
            "title": "Screening Questions",
            "questions": [
                {"q": "Are you a software developer?", "type": "yes_no", "required": True}
            ]
        },
        "section02-user-profile": {
            "title": "User Profile",
            "questions": [
                {"q": "What is your role?", "type": "single_choice", "choices": ["Developer", "Manager", "Designer"]}
            ]
        },
        "section03-problem": {
            "title": "Problem Discovery",
            "questions": [
                {"q": "What challenges do you face?", "type": "open_ended"}
            ]
        },
        "section04-current-behavior": {
            "title": "Current Behavior",
            "questions": [
                {"q": "How do you currently solve this?", "type": "open_ended"}
            ]
        },
        "section05-impact": {
            "title": "Impact Assessment",
            "questions": [
                {"q": "How severe is this problem?", "type": "single_choice", "choices": ["Low", "Medium", "High"]}
            ]
        },
        "section06-concept-validation": {
            "title": "Concept Validation",
            "questions": [
                {"q": "Would you use this solution?", "type": "yes_no"}
            ]
        }
    }


@pytest.fixture
def mock_pdoc():
    return MockPdocIntegration()


@pytest.fixture
def mock_fclient():
    return MockFClient()


@pytest.fixture
def integration(mock_pdoc, mock_fclient):
    return survey_research.IntegrationSurveyResearch(
        surveymonkey_token="",
        prolific_token="",
        pdoc_integration=mock_pdoc,
        fclient=mock_fclient,
    )


@pytest.fixture
def toolcall():
    return make_toolcall()


class TestHelp:
    @pytest.mark.asyncio
    async def test_help_returns_documentation(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {"op": "help"})
        assert "draft_survey" in result
        assert "draft_auditory" in result
        assert "run" in result
        assert "responses" in result

    @pytest.mark.asyncio
    async def test_empty_args_returns_help(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, None)
        assert "draft_survey" in result

    @pytest.mark.asyncio
    async def test_unknown_op_returns_error(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {"op": "unknown_operation"})
        assert "Unknown operation" in result
        assert "unknown_operation" in result


class TestDraftSurvey:
    @pytest.mark.asyncio
    async def test_missing_idea_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"hypothesis_name": "test-hyp", "survey_content": make_valid_survey_content()}
        })
        assert "Error: idea_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_hypothesis_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "survey_content": make_valid_survey_content()}
        })
        assert "Error: hypothesis_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_survey_content(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp"}
        })
        assert "Error: survey_content is required" in result

    @pytest.mark.asyncio
    async def test_missing_survey_meta(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {
                "idea_name": "test-idea",
                "hypothesis_name": "test-hyp",
                "survey_content": {"section01-screening": {"title": "Test", "questions": []}}
            }
        })
        assert "survey.meta" in result

    @pytest.mark.asyncio
    async def test_missing_survey_title(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {
                "idea_name": "test-idea",
                "hypothesis_name": "test-hyp",
                "survey_content": {"survey": {"meta": {"description": "no title"}}}
            }
        })
        assert "title is required" in result

    @pytest.mark.asyncio
    async def test_section_must_be_object(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"] = "not an object"
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "must be an object" in result

    @pytest.mark.asyncio
    async def test_section_must_have_questions_array(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"] = {"title": "Test", "questions": "not an array"}
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "'questions' array" in result

    @pytest.mark.asyncio
    async def test_section_must_have_title(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"] = {"questions": []}
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "must have 'title'" in result

    @pytest.mark.asyncio
    async def test_question_missing_q_field(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"]["questions"] = [{"type": "yes_no"}]
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "missing 'q' field" in result

    @pytest.mark.asyncio
    async def test_question_missing_type_field(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"]["questions"] = [{"q": "Test question"}]
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "missing 'type' field" in result

    @pytest.mark.asyncio
    async def test_choice_question_missing_choices(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"]["questions"] = [{"q": "Pick one", "type": "single_choice"}]
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "requires 'choices' array" in result

    @pytest.mark.asyncio
    async def test_multiple_choice_missing_choices(self, integration, toolcall):
        content = make_valid_survey_content()
        content["section01-screening"]["questions"] = [{"q": "Pick many", "type": "multiple_choice"}]
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp", "survey_content": content}
        })
        assert "requires 'choices' array" in result

    @pytest.mark.asyncio
    async def test_no_sections_error(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {
                "idea_name": "test-idea",
                "hypothesis_name": "test-hyp",
                "survey_content": {"survey": {"meta": {"title": "Test"}}}
            }
        })
        assert "must have section" in result

    @pytest.mark.asyncio
    async def test_successful_draft_survey(self, integration, toolcall, mock_pdoc):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {
                "idea_name": "test-idea",
                "hypothesis_name": "test-hyp",
                "survey_content": make_valid_survey_content()
            }
        })
        assert "✅ Survey draft created successfully" in result
        assert "/customer-research/test-idea/test-hyp/survey-draft" in result

        saved = mock_pdoc.storage["/customer-research/test-idea/test-hyp/survey-draft"]
        assert saved["survey"]["meta"]["title"] == "Test Survey"
        assert saved["survey"]["meta"]["idea"] == "test-idea"
        assert saved["survey"]["meta"]["hypothesis"] == "test-hyp"


class TestDraftAuditory:
    @pytest.mark.asyncio
    async def test_missing_idea_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"hypothesis_name": "h", "study_name": "s", "study_description": "d",
                     "estimated_minutes": 5, "reward_cents": 100, "total_participants": 50}
        })
        assert "Error: idea_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_hypothesis_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "study_name": "s", "study_description": "d",
                     "estimated_minutes": 5, "reward_cents": 100, "total_participants": 50}
        })
        assert "Error: hypothesis_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_study_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "hypothesis_name": "h", "study_description": "d",
                     "estimated_minutes": 5, "reward_cents": 100, "total_participants": 50}
        })
        assert "Error: study_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_study_description(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                     "estimated_minutes": 5, "reward_cents": 100, "total_participants": 50}
        })
        assert "Error: study_description is required" in result

    @pytest.mark.asyncio
    async def test_missing_estimated_minutes(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                     "study_description": "d", "reward_cents": 100, "total_participants": 50}
        })
        assert "Error: estimated_minutes is required" in result

    @pytest.mark.asyncio
    async def test_missing_reward_cents(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                     "study_description": "d", "estimated_minutes": 5, "total_participants": 50}
        })
        assert "Error: reward_cents is required" in result

    @pytest.mark.asyncio
    async def test_missing_total_participants(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {"idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                     "study_description": "d", "estimated_minutes": 5, "reward_cents": 100}
        })
        assert "Error: total_participants is required" in result

    @pytest.mark.asyncio
    async def test_unknown_filter(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"nonexistent_filter": "value"}
            }
        })
        assert "Error: Unknown filter" in result
        assert "nonexistent_filter" in result

    @pytest.mark.asyncio
    async def test_range_filter_out_of_bounds_min(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"age": {"min": 10, "max": 30}}
            }
        })
        assert "out of range" in result

    @pytest.mark.asyncio
    async def test_range_filter_out_of_bounds_max(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"age": {"min": 25, "max": 150}}
            }
        })
        assert "out of range" in result

    @pytest.mark.asyncio
    async def test_select_filter_invalid_value(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"children": ["invalid_choice"]}
            }
        })
        assert "Invalid value" in result

    @pytest.mark.asyncio
    async def test_successful_auditory_draft(self, integration, toolcall, mock_pdoc):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "test-idea",
                "hypothesis_name": "test-hyp",
                "study_name": "Test Study",
                "study_description": "A test study",
                "estimated_minutes": 10,
                "reward_cents": 150,
                "total_participants": 50,
                "filters": {"age": {"min": 25, "max": 45}}
            }
        })
        assert "✅ Audience targeting draft created" in result
        assert "/customer-research/test-idea/test-hyp/auditory-draft" in result

        saved = mock_pdoc.storage["/customer-research/test-idea/test-hyp/auditory-draft"]
        assert saved["prolific_auditory_draft"]["meta"]["study_name"] == "Test Study"
        assert saved["prolific_auditory_draft"]["parameters"]["estimated_minutes"] == 10
        assert saved["prolific_auditory_draft"]["parameters"]["reward_cents"] == 150
        assert saved["prolific_auditory_draft"]["parameters"]["total_participants"] == 50

    @pytest.mark.asyncio
    async def test_cost_calculation(self, integration, toolcall, mock_pdoc):
        await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 10,
                "reward_cents": 100, "total_participants": 100,
                "filters": {}
            }
        })
        saved = mock_pdoc.storage["/customer-research/i/h/auditory-draft"]
        cost = saved["prolific_auditory_draft"]["cost_estimate"]

        assert cost["rewards"] == 100 * 100
        service_fee = 100 * 100 * 0.33
        vat = service_fee * 0.20
        assert cost["service_fee"] == int(service_fee)
        assert cost["vat"] == int(vat)
        assert cost["total"] == int(10000 + service_fee + vat)


class TestSearchFilters:
    @pytest.mark.asyncio
    async def test_missing_search_pattern(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "search_filters",
            "args": {}
        })
        assert "Error: search_pattern is required" in result

    @pytest.mark.asyncio
    async def test_search_age_filter(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "search_filters",
            "args": {"search_pattern": "^age$"}
        })
        assert "age" in result.lower()
        assert "range" in result.lower()

    @pytest.mark.asyncio
    async def test_search_multiple_patterns(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "search_filters",
            "args": {"search_pattern": ["age", "children"]}
        })
        assert "age" in result.lower()
        assert "children" in result.lower()

    @pytest.mark.asyncio
    async def test_search_no_matches(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "search_filters",
            "args": {"search_pattern": "xyznonexistent123"}
        })
        assert "No filters found" in result

    @pytest.mark.asyncio
    async def test_invalid_regex_pattern(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "search_filters",
            "args": {"search_pattern": "[invalid(regex"}
        })
        assert "Invalid regex" in result


class TestList:
    @pytest.mark.asyncio
    async def test_missing_idea_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "list",
            "args": {}
        })
        assert "Error: idea_name is required" in result

    @pytest.mark.asyncio
    async def test_no_survey_files_found(self, integration, toolcall, mock_pdoc):
        mock_pdoc.set_list_items("/customer-research/empty-idea", [])
        result = await integration.handle_survey_research(toolcall, {
            "op": "list",
            "args": {"idea_name": "empty-idea"}
        })
        assert "No survey files found" in result

    @pytest.mark.asyncio
    async def test_list_survey_files(self, integration, toolcall, mock_pdoc):
        mock_pdoc.set_list_items("/customer-research/test-idea", [
            MockPdocItem("/customer-research/test-idea/hyp1", is_folder=True),
        ])
        mock_pdoc.set_list_items("/customer-research/test-idea/hyp1", [
            MockPdocItem("/customer-research/test-idea/hyp1/survey-draft", is_folder=False),
            MockPdocItem("/customer-research/test-idea/hyp1/auditory-draft", is_folder=False),
            MockPdocItem("/customer-research/test-idea/hyp1/survey-results", is_folder=False),
        ])

        result = await integration.handle_survey_research(toolcall, {
            "op": "list",
            "args": {"idea_name": "test-idea"}
        })
        assert "survey-draft" in result
        assert "auditory-draft" in result
        assert "survey-results" in result


class TestRun:
    @pytest.mark.asyncio
    async def test_missing_idea_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "run",
            "args": {"hypothesis_name": "h"}
        })
        assert "Error: idea_name and hypothesis_name are required" in result

    @pytest.mark.asyncio
    async def test_missing_hypothesis_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "run",
            "args": {"idea_name": "i"}
        })
        assert "Error: idea_name and hypothesis_name are required" in result

    @pytest.mark.asyncio
    async def test_run_requires_confirmation(self, integration, toolcall, mock_pdoc):
        mock_pdoc.storage["/customer-research/test-idea/test-hyp/auditory-draft"] = {
            "prolific_auditory_draft": {
                "meta": {"study_name": "Test", "status": "DRAFT"},
                "parameters": {"completion_codes": [{"code": "COMPLETE_123"}]},
                "cost_estimate": {"total": 15000}
            }
        }

        with pytest.raises(ckit_cloudtool.NeedsConfirmation) as exc:
            await integration.handle_survey_research(toolcall, {
                "op": "run",
                "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp"}
            })
        assert "£150.00" in exc.value.confirm_explanation

    @pytest.mark.asyncio
    async def test_run_with_confirmation(self, integration, mock_pdoc):
        toolcall = make_toolcall(confirmed=True)

        mock_pdoc.storage["/customer-research/test-idea/test-hyp/survey-draft"] = make_valid_survey_content()
        mock_pdoc.storage["/customer-research/test-idea/test-hyp/auditory-draft"] = {
            "prolific_auditory_draft": {
                "meta": {"study_name": "Test", "status": "DRAFT"},
                "parameters": {
                    "study_description": "Test description",
                    "estimated_minutes": 5,
                    "reward_cents": 100,
                    "total_participants": 50,
                    "filters": [],
                    "completion_codes": [{"code": "COMPLETE_123", "code_type": "COMPLETED", "actions": []}]
                },
                "cost_estimate": {"total": 8000}
            }
        }

        result = await integration.handle_survey_research(toolcall, {
            "op": "run",
            "args": {"idea_name": "test-idea", "hypothesis_name": "test-hyp"}
        })
        assert "Survey campaign" in result
        assert "SurveyMonkey" in result or "survey" in result.lower()


class TestResponses:
    @pytest.mark.asyncio
    async def test_missing_survey_id(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "responses",
            "args": {"target_responses": 50, "idea_name": "i", "hypothesis_name": "h"}
        })
        assert "Error: survey_id is required" in result

    @pytest.mark.asyncio
    async def test_missing_target_responses(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "responses",
            "args": {"survey_id": "123", "idea_name": "i", "hypothesis_name": "h"}
        })
        assert "Error: target_responses is required" in result

    @pytest.mark.asyncio
    async def test_missing_idea_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "responses",
            "args": {"survey_id": "123", "target_responses": 50, "hypothesis_name": "h"}
        })
        assert "Error: idea_name is required" in result

    @pytest.mark.asyncio
    async def test_missing_hypothesis_name(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "responses",
            "args": {"survey_id": "123", "target_responses": 50, "idea_name": "i"}
        })
        assert "Error: hypothesis_name is required" in result

    @pytest.mark.asyncio
    async def test_invalid_target_responses(self, integration, toolcall):
        result = await integration.handle_survey_research(toolcall, {
            "op": "responses",
            "args": {"survey_id": "123", "target_responses": 0, "idea_name": "i", "hypothesis_name": "h"}
        })
        assert "Error: target_responses is required and must be greater than 0" in result


class TestQuestionConversion:
    def test_yes_no_conversion(self, integration):
        q = {"q": "Test?", "type": "yes_no", "required": True}
        result = integration._convert_question_to_sm(q)
        assert result["family"] == "single_choice"
        assert len(result["answers"]["choices"]) == 2
        assert result["answers"]["choices"][0]["text"] == "Yes"
        assert result["answers"]["choices"][1]["text"] == "No"
        assert "required" in result

    def test_single_choice_conversion(self, integration):
        q = {"q": "Pick one", "type": "single_choice", "choices": ["A", "B", "C"]}
        result = integration._convert_question_to_sm(q)
        assert result["family"] == "single_choice"
        assert len(result["answers"]["choices"]) == 3

    def test_multiple_choice_conversion(self, integration):
        q = {"q": "Pick many", "type": "multiple_choice", "choices": ["X", "Y"]}
        result = integration._convert_question_to_sm(q)
        assert result["family"] == "multiple_choice"
        assert len(result["answers"]["choices"]) == 2

    def test_open_ended_conversion(self, integration):
        q = {"q": "Tell me more", "type": "open_ended"}
        result = integration._convert_question_to_sm(q)
        assert result["family"] == "open_ended"
        assert "answers" not in result


class TestMockIntegration:
    def test_mock_aiohttp_creates_surveys(self):
        survey_research_mock.clear_mock_data()
        mock = survey_research_mock.MockAiohttp()
        assert mock.ClientSession is not None
        assert mock.ClientTimeout is not None

    def test_clear_mock_data(self):
        survey_research_mock.mock_surveys["test"] = {"id": "test"}
        survey_research_mock.clear_mock_data()
        assert len(survey_research_mock.mock_surveys) == 0
        assert len(survey_research_mock.mock_studies) == 0
        assert len(survey_research_mock.mock_responses) == 0


class TestPathConstruction:
    @pytest.mark.asyncio
    async def test_survey_draft_path(self, integration, toolcall, mock_pdoc):
        await integration.handle_survey_research(toolcall, {
            "op": "draft_survey",
            "args": {
                "idea_name": "my-idea",
                "hypothesis_name": "my-hypothesis",
                "survey_content": make_valid_survey_content()
            }
        })
        assert "/customer-research/my-idea/my-hypothesis/survey-draft" in mock_pdoc.storage

    @pytest.mark.asyncio
    async def test_auditory_draft_path(self, integration, toolcall, mock_pdoc):
        await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "my-idea",
                "hypothesis_name": "my-hypothesis",
                "study_name": "Study",
                "study_description": "Desc",
                "estimated_minutes": 5,
                "reward_cents": 100,
                "total_participants": 50,
                "filters": {}
            }
        })
        assert "/customer-research/my-idea/my-hypothesis/auditory-draft" in mock_pdoc.storage


class TestFilterValidation:
    @pytest.mark.asyncio
    async def test_valid_age_range_filter(self, integration, toolcall, mock_pdoc):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"age": {"min": 25, "max": 45}}
            }
        })
        assert "✅" in result

    @pytest.mark.asyncio
    async def test_valid_select_filter(self, integration, toolcall, mock_pdoc):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"children": ["0"]}
            }
        })
        assert "✅" in result

    @pytest.mark.asyncio
    async def test_range_filter_single_value(self, integration, toolcall, mock_pdoc):
        result = await integration.handle_survey_research(toolcall, {
            "op": "draft_auditory",
            "args": {
                "idea_name": "i", "hypothesis_name": "h", "study_name": "s",
                "study_description": "d", "estimated_minutes": 5,
                "reward_cents": 100, "total_participants": 50,
                "filters": {"age": 30}
            }
        })
        assert "✅" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
