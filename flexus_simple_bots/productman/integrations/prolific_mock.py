import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("prolific_mock")

mock_studies = {}
mock_submissions = {}
mock_study_counter = 1000


class MockProlificSession:
    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def post(self, url, **kwargs):
        return MockProlificResponse("post", url, **kwargs)

    def get(self, url, **kwargs):
        return MockProlificResponse("get", url, **kwargs)


class MockProlificResponse:
    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url
        self.kwargs = kwargs
        self.status = 200
        self._json_data = None

        if method == "post" and "/studies" in url and "/transition" not in url:
            self._handle_create_study()
        elif method == "post" and "/transition" in url:
            self._handle_transition_study()
        elif method == "get" and "/studies/" in url and "/submissions" not in url:
            self._handle_get_study()
        elif method == "get" and "/submissions" in url:
            self._handle_get_submissions()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def text(self):
        if self.status >= 400:
            return json.dumps({"error": "Mock error"})
        return json.dumps(self._json_data)

    async def json(self):
        return self._json_data

    def _handle_create_study(self):
        global mock_study_counter
        study_data = self.kwargs.get("json", {})
        study_id = f"study_{mock_study_counter}"
        mock_study_counter += 1

        mock_studies[study_id] = {
            "id": study_id,
            "name": study_data.get("name", "Test Study"),
            "status": "UNPUBLISHED",
            "external_study_url": study_data.get("external_study_url", ""),
            "total_available_places": study_data.get("total_available_places", 50),
            "places_taken": 0,
            "reward": study_data.get("reward", 100),
            "estimated_completion_time": study_data.get("estimated_completion_time", 5)
        }

        self._json_data = mock_studies[study_id]
        logger.info(f"Created mock study {study_id}: {study_data.get('name')}")

    def _handle_transition_study(self):
        study_id = self.url.split("/studies/")[1].split("/")[0]
        action = self.kwargs.get("json", {}).get("action", "")

        if study_id in mock_studies:
            if action == "PUBLISH":
                mock_studies[study_id]["status"] = "ACTIVE"
            elif action == "PAUSE":
                mock_studies[study_id]["status"] = "PAUSED"
            elif action == "STOP":
                mock_studies[study_id]["status"] = "COMPLETED"

            self._json_data = mock_studies[study_id]
            logger.info(f"Transitioned study {study_id} with action {action}")
        else:
            self.status = 404

    def _handle_get_study(self):
        study_id = self.url.split("/studies/")[1].split("/")[0]
        if study_id in mock_studies:
            self._json_data = mock_studies[study_id]
        else:
            self.status = 404

    def _handle_get_submissions(self):
        study_id = self.url.split("/studies/")[1].split("/")[0]
        submissions = mock_submissions.get(study_id, [])

        self._json_data = {
            "results": submissions,
            "total": len(submissions)
        }
        logger.info(f"Returning {len(submissions)} submissions for study {study_id}")


class MockAiohttp:
    class ClientSession:
        def __init__(self):
            pass

        async def __aenter__(self):
            return MockProlificSession()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class ClientTimeout:
        def __init__(self, total=30):
            self.total = total


def add_mock_submissions(study_id: str, submissions: List[Dict[str, Any]]):
    mock_submissions[study_id] = submissions
    if study_id in mock_studies:
        mock_studies[study_id]["places_taken"] = len(submissions)
    logger.info(f"Added {len(submissions)} mock submissions for study {study_id}")


def clear_mock_data():
    global mock_study_counter
    mock_studies.clear()
    mock_submissions.clear()
    mock_study_counter = 1000
    logger.info("Cleared all mock data")
