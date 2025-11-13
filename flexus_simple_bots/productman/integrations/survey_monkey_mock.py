import logging
from typing import Dict, Any, List

logger = logging.getLogger("survey_monkey_mock")

mock_surveys = {}
mock_responses = {}
mock_survey_counter = 10000


class MockSurveyMonkeySession:
    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, url, **kwargs):
        return MockSurveyMonkeyResponse("post", url, **kwargs)

    def get(self, url, **kwargs):
        return MockSurveyMonkeyResponse("get", url, **kwargs)


class MockSurveyMonkeyResponse:
    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.status = 200
        self._json_data = None

        if method == "post" and "/surveys" in url and "/collectors" not in url:
            self._handle_create_survey()
        elif method == "post" and "/collectors" in url:
            self._handle_create_collector()
        elif method == "get" and "/responses/bulk" in url:
            self._handle_get_responses()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception(f"HTTP {self.status}")

    async def json(self):
        return self._json_data

    def _handle_create_survey(self):
        global mock_survey_counter
        survey_data = self.kwargs.get("json", {})
        survey_id = str(mock_survey_counter)
        mock_survey_counter += 1

        mock_surveys[survey_id] = {
            "id": survey_id,
            "title": survey_data.get("title", "Test Survey"),
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
            "name": collector_data.get("name", "Test Collector"),
            "url": f"https://www.surveymonkey.com/r/{collector_id}"
        }
        logger.info(f"Created mock collector for survey {survey_id}")

    def _handle_get_responses(self):
        survey_id = self.url.split("/surveys/")[1].split("/")[0]
        params = self.kwargs.get("params", {})
        page = params.get("page", 1)
        per_page = params.get("per_page", 100)

        responses = mock_responses.get(survey_id, [])

        start = (page - 1) * per_page
        end = start + per_page
        page_responses = responses[start:end]

        self._json_data = {
            "total": len(responses),
            "page": page,
            "per_page": per_page,
            "data": page_responses
        }
        logger.info(f"Returning {len(page_responses)} responses for survey {survey_id}")


class MockAiohttp:
    class ClientSession:
        def __init__(self):
            pass

        async def __aenter__(self):
            return MockSurveyMonkeySession()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class ClientTimeout:
        def __init__(self, total=30):
            self.total = total

    class ClientResponseError(Exception):
        pass


def add_mock_responses(survey_id: str, responses: List[Dict[str, Any]]):
    mock_responses[survey_id] = responses
    logger.info(f"Added {len(responses)} mock responses for survey {survey_id}")


def clear_mock_data():
    global mock_survey_counter
    mock_surveys.clear()
    mock_responses.clear()
    mock_survey_counter = 10000
    logger.info("Cleared all mock data")
