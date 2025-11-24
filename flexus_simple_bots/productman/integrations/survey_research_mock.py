import json
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("survey_research_mock")

mock_surveys = {}
mock_studies = {}
mock_responses = {}
mock_survey_counter = 10000
mock_study_counter = 1000


class MockSurveyResearchSession:
    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, url, **kwargs):
        return MockSurveyResearchResponse("post", url, **kwargs)

    def get(self, url, **kwargs):
        return MockSurveyResearchResponse("get", url, **kwargs)

    def patch(self, url, **kwargs):
        return MockSurveyResearchResponse("patch", url, **kwargs)


class MockSurveyResearchResponse:
    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.status = 200
        self._json_data = None

        if "surveymonkey.com" in url:
            self._handle_surveymonkey_request()
        elif "prolific.com" in url:
            self._handle_prolific_request()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception(f"HTTP {self.status}")

    async def json(self):
        return self._json_data

    def _handle_surveymonkey_request(self):
        if self.method == "post" and "/surveys" in self.url and "/collectors" not in self.url:
            self._handle_create_survey()
        elif self.method == "post" and "/collectors" in self.url:
            self._handle_create_collector()
        elif self.method == "patch" and "/collectors" in self.url:
            self._handle_update_collector()

    def _handle_prolific_request(self):
        if self.method == "post" and "/studies" in self.url:
            self._handle_create_study()

    def _handle_create_survey(self):
        global mock_survey_counter
        survey_data = self.kwargs.get("json", {})
        survey_id = str(mock_survey_counter)
        mock_survey_counter += 1

        mock_surveys[survey_id] = {
            "id": survey_id,
            "title": survey_data.get("title", "Mock Survey"),
            "pages": survey_data.get("pages", []),
            "href": f"https://api.surveymonkey.com/v3/surveys/{survey_id}"
        }

        self._json_data = mock_surveys[survey_id]
        logger.info(f"Created mock survey {survey_id}: {survey_data.get('title')}")

    def _handle_create_collector(self):
        survey_id = self.url.split("/surveys/")[1].split("/")[0]
        collector_data = self.kwargs.get("json", {})

        collector_id = f"{survey_id}_collector"
        self._json_data = {
            "id": collector_id,
            "type": collector_data.get("type", "weblink"),
            "name": collector_data.get("name", "Mock Collector"),
            "url": f"https://www.surveymonkey.com/r/MOCK{survey_id}"
        }
        logger.info(f"Created mock collector for survey {survey_id}")

    def _handle_update_collector(self):
        collector_id = self.url.split("/collectors/")[1]
        collector_data = self.kwargs.get("json", {})
        
        self._json_data = {
            "id": collector_id,
            "redirect_url": collector_data.get("redirect_url"),
            "redirect_type": collector_data.get("redirect_type")
        }
        logger.info(f"Updated mock collector {collector_id}")

    def _handle_create_study(self):
        global mock_study_counter
        study_data = self.kwargs.get("json", {})
        study_id = f"study_{mock_study_counter}"
        mock_study_counter += 1

        mock_studies[study_id] = {
            "id": study_id,
            "name": study_data.get("name", "Mock Study"),
            "status": "UNPUBLISHED",
            "external_study_url": study_data.get("external_study_url", ""),
            "total_available_places": study_data.get("total_available_places", 50),
            "places_taken": 0,
            "reward": study_data.get("reward", 100),
            "estimated_completion_time": study_data.get("estimated_completion_time", 5)
        }

        self._json_data = mock_studies[study_id]
        logger.info(f"Created mock study {study_id}: {study_data.get('name')}")


class MockAiohttp:
    class ClientSession:
        def __init__(self):
            pass

        async def __aenter__(self):
            return MockSurveyResearchSession()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class ClientTimeout:
        def __init__(self, total=30):
            self.total = total


def add_mock_survey_responses(survey_id: str, responses: List[Dict[str, Any]]):
    mock_responses[survey_id] = responses
    logger.info(f"Added {len(responses)} mock responses for survey {survey_id}")


def add_mock_study_submissions(study_id: str, submissions: List[Dict[str, Any]]):
    if study_id in mock_studies:
        mock_studies[study_id]["places_taken"] = len(submissions)
    logger.info(f"Added {len(submissions)} mock submissions for study {study_id}")


def clear_mock_data():
    global mock_survey_counter, mock_study_counter
    mock_surveys.clear()
    mock_studies.clear()
    mock_responses.clear()
    mock_survey_counter = 10000
    mock_study_counter = 1000
    logger.info("Cleared all mock data")
