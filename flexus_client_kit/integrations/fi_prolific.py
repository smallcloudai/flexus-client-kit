import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("prolific")

PROVIDER_NAME = "prolific"
METHOD_IDS = [
    "prolific.studies.list.v1",
    "prolific.studies.create.v1",
    "prolific.studies.get.v1",
    "prolific.participant_groups.list.v1",
    "prolific.participant_groups.create.v1",
    "prolific.participant_groups.participants.list.v1",
    "prolific.participant_groups.participants.add.v1",
    "prolific.participant_groups.participants.remove.v1",
    "prolific.submissions.list.v1",
    "prolific.submissions.approve.v1",
    "prolific.submissions.reject.v1",
    "prolific.bonuses.create.v1",
    "prolific.webhooks.list.v1",
    "prolific.webhooks.create.v1",
    "prolific.webhooks.delete.v1",
]

_BASE_URL = "https://api.prolific.com/api/v1"
_TIMEOUT = 30.0

# Prolific uses a server-side API token, not OAuth.
# Required value:
# - PROLIFIC_API_TOKEN: generated in the Prolific researcher workspace / API settings.
# Where Flexus colleagues register it:
# - environment or secret manager consumed by the runtime hosting this integration.
# This integration does not own token provisioning and does not expose bot setup fields for secrets.
PROLIFIC_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationProlific:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_token(self) -> str:
        try:
            return str(os.environ.get("PROLIFIC_API_TOKEN", "")).strip()
        except (TypeError, ValueError):
            return ""

    def _status(self) -> str:
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if self._api_token() else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "api_token",
                "required_env": ["PROLIFIC_API_TOKEN"],
                "products": [
                    "Studies",
                    "Participant Groups",
                    "Submissions",
                    "Bonuses",
                    "Webhooks",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- Prolific credentials come from PROLIFIC_API_TOKEN.\n"
            "- Participant groups support allowlists and blocklists across studies.\n"
            "- Webhooks are preferred over polling when the platform setup allows inbound delivery.\n"
        )

    def _result(self, method_id: str, result: Any) -> str:
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "result": result,
            },
            indent=2,
            ensure_ascii=False,
        )

    def _error(self, method_id: str, code: str, message: str, **extra: Any) -> str:
        payload: Dict[str, Any] = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": code,
            "message": message,
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Token {self._api_token()}",
            "Content-Type": "application/json",
        }

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        try:
            args = model_produced_args or {}
            op = str(args.get("op", "help")).strip()
            if op == "help":
                return self._help()
            if op == "status":
                return self._status()
            if op == "list_methods":
                return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
            if op != "call":
                return "Error: unknown op. Use help/status/list_methods/call."
            call_args = args.get("args") or {}
            method_id = str(call_args.get("method_id", "")).strip()
            if not method_id:
                return "Error: args.method_id required for op=call."
            if method_id not in METHOD_IDS:
                return self._error(method_id, "METHOD_UNKNOWN", "Unknown Prolific method.")
            if not self._api_token():
                return self._error(method_id, "AUTH_MISSING", "Set PROLIFIC_API_TOKEN in the runtime environment.")
            return await self._dispatch(method_id, call_args)
        except (TypeError, ValueError) as e:
            logger.error("prolific called_by_model failed", exc_info=e)
            return self._error("prolific.runtime", "RUNTIME_ERROR", f"{type(e).__name__}: {e}")

    async def _request(
        self,
        method_id: str,
        http_method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = _BASE_URL + path
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(), params=params)
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(), params=params, json=body)
                elif http_method == "DELETE":
                    response = await client.delete(url, headers=self._headers(), params=params)
                else:
                    return self._error(method_id, "UNSUPPORTED_HTTP_METHOD", f"Unsupported HTTP method {http_method}.")
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "Prolific request timed out.")
        except httpx.HTTPError as e:
            logger.error("prolific request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")

        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("prolific provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "Prolific returned an error.", http_status=response.status_code, detail=detail)

        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    def _require_str(self, method_id: str, args: Dict[str, Any], key: str) -> str:
        value = str(args.get(key, "")).strip()
        if not value:
            raise ValueError(f"{key} is required for {method_id}.")
        return value

    def _study_create_body(self, args: Dict[str, Any]) -> Dict[str, Any]:
        name = self._require_str("prolific.studies.create.v1", args, "name")
        description = self._require_str("prolific.studies.create.v1", args, "description")
        total_available_places = int(args.get("total_available_places"))
        reward = int(args.get("reward"))
        estimated_completion_time = int(args.get("estimated_completion_time"))
        body: Dict[str, Any] = {
            "name": name,
            "description": description,
            "total_available_places": total_available_places,
            "reward": reward,
            "estimated_completion_time": estimated_completion_time,
        }
        for optional_key in [
            "internal_name",
            "external_study_url",
            "completion_code",
            "completion_option",
            "prolific_id_option",
        ]:
            value = args.get(optional_key)
            if value not in (None, ""):
                body[optional_key] = value
        if isinstance(args.get("eligibility_requirements"), list):
            body["eligibility_requirements"] = args["eligibility_requirements"]
        if isinstance(args.get("filters"), list):
            body["filters"] = args["filters"]
        return body

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "prolific.studies.list.v1":
                return await self._request(method_id, "GET", "/studies/", params={"workspace_id": args.get("workspace_id", "") or None})
            if method_id == "prolific.studies.create.v1":
                return await self._request(method_id, "POST", "/studies/", body=self._study_create_body(args))
            if method_id == "prolific.studies.get.v1":
                study_id = self._require_str(method_id, args, "study_id")
                return await self._request(method_id, "GET", f"/studies/{study_id}/")
            if method_id == "prolific.participant_groups.list.v1":
                return await self._request(method_id, "GET", "/participant-groups/")
            if method_id == "prolific.participant_groups.create.v1":
                name = self._require_str(method_id, args, "name")
                body: Dict[str, Any] = {"name": name}
                description = str(args.get("description", "")).strip()
                if description:
                    body["description"] = description
                return await self._request(method_id, "POST", "/participant-groups/", body=body)
            if method_id == "prolific.participant_groups.participants.list.v1":
                participant_group_id = self._require_str(method_id, args, "participant_group_id")
                return await self._request(method_id, "GET", f"/participant-groups/{participant_group_id}/participants/")
            if method_id == "prolific.participant_groups.participants.add.v1":
                participant_group_id = self._require_str(method_id, args, "participant_group_id")
                participant_ids = args.get("participant_ids")
                if not isinstance(participant_ids, list) or not participant_ids:
                    return self._error(method_id, "INVALID_ARGS", "participant_ids must be a non-empty list.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/participant-groups/{participant_group_id}/participants/",
                    body={"participant_ids": participant_ids},
                )
            if method_id == "prolific.participant_groups.participants.remove.v1":
                participant_group_id = self._require_str(method_id, args, "participant_group_id")
                participant_ids = args.get("participant_ids")
                if not isinstance(participant_ids, list) or not participant_ids:
                    return self._error(method_id, "INVALID_ARGS", "participant_ids must be a non-empty list.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/participant-groups/{participant_group_id}/participants/remove/",
                    body={"participant_ids": participant_ids},
                )
            if method_id == "prolific.submissions.list.v1":
                study_id = self._require_str(method_id, args, "study_id")
                return await self._request(method_id, "GET", f"/studies/{study_id}/submissions/")
            if method_id == "prolific.submissions.approve.v1":
                submission_id = self._require_str(method_id, args, "submission_id")
                return await self._request(method_id, "POST", f"/submissions/{submission_id}/transition/", body={"action": "APPROVE"})
            if method_id == "prolific.submissions.reject.v1":
                submission_id = self._require_str(method_id, args, "submission_id")
                body: Dict[str, Any] = {"action": "REJECT"}
                rejection_category = str(args.get("rejection_category", "")).strip()
                if rejection_category:
                    body["rejection_category"] = rejection_category
                return await self._request(method_id, "POST", f"/submissions/{submission_id}/transition/", body=body)
            if method_id == "prolific.bonuses.create.v1":
                submission_id = self._require_str(method_id, args, "submission_id")
                amount = int(args.get("amount"))
                reason = self._require_str(method_id, args, "reason")
                return await self._request(method_id, "POST", "/bonuses/", body={"submission_id": submission_id, "amount": amount, "reason": reason})
            if method_id == "prolific.webhooks.list.v1":
                return await self._request(method_id, "GET", "/webhooks/")
            if method_id == "prolific.webhooks.create.v1":
                target_url = self._require_str(method_id, args, "target_url")
                events = args.get("events")
                if not isinstance(events, list) or not events:
                    return self._error(method_id, "INVALID_ARGS", "events must be a non-empty list.")
                return await self._request(method_id, "POST", "/webhooks/", body={"target_url": target_url, "events": events})
            if method_id == "prolific.webhooks.delete.v1":
                webhook_id = self._require_str(method_id, args, "webhook_id")
                return await self._request(method_id, "DELETE", f"/webhooks/{webhook_id}/")
        except ValueError as e:
            return self._error(method_id, "INVALID_ARGS", str(e))
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
