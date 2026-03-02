import datetime
import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fi_mturk")

PROVIDER_NAME = "mturk"
METHOD_IDS = [
    "mturk.hits.create.v1",
    "mturk.hits.list.v1",
    "mturk.assignments.list.v1",
    "mturk.assignments.approve.v1",
]

_PRODUCTION_URL = "https://mturk-requester.us-east-1.amazonaws.com"
_SANDBOX_URL = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
_SERVICE = "mturk-requester"
_REGION = "us-east-1"

_TARGETS = {
    "mturk.hits.create.v1": "MTurkRequesterServiceV20170117.CreateHIT",
    "mturk.hits.list.v1": "MTurkRequesterServiceV20170117.ListHITs",
    "mturk.assignments.list.v1": "MTurkRequesterServiceV20170117.ListAssignmentsForHIT",
    "mturk.assignments.approve.v1": "MTurkRequesterServiceV20170117.ApproveAssignment",
}


class IntegrationMturk:
    def _get_base_url(self) -> str:
        if os.environ.get("MTURK_SANDBOX", "").lower() == "true":
            return _SANDBOX_URL
        return _PRODUCTION_URL

    def _sign_request(self, target: str, payload_bytes: bytes) -> Dict[str, str]:
        access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

        now = datetime.datetime.utcnow()
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")

        content_type = "application/x-amz-json-1.1"
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()

        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = (
            f"content-type:{content_type}\n"
            f"host:mturk-requester.us-east-1.amazonaws.com\n"
            f"x-amz-date:{amz_date}\n"
            f"x-amz-target:{target}\n"
        )
        signed_headers = "content-type;host;x-amz-date;x-amz-target"

        canonical_request = "\n".join([
            "POST",
            canonical_uri,
            canonical_querystring,
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        credential_scope = f"{date_stamp}/{_REGION}/{_SERVICE}/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])

        def _hmac(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        signing_key = _hmac(
            _hmac(
                _hmac(
                    _hmac(
                        ("AWS4" + secret_key).encode("utf-8"),
                        date_stamp,
                    ),
                    _REGION,
                ),
                _SERVICE,
            ),
            "aws4_request",
        )

        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization = (
            f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        return {
            "Content-Type": content_type,
            "Content-Length": str(len(payload_bytes)),
            "X-Amz-Date": amz_date,
            "X-Amz-Target": target,
            "Authorization": authorization,
        }

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (
                f"provider={PROVIDER_NAME}\n"
                "op=help | status | list_methods | call\n"
                f"methods: {', '.join(METHOD_IDS)}"
            )
        if op == "status":
            has_key = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
            has_secret = bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
            status = "available" if (has_key and has_secret) else "unavailable"
            sandbox = os.environ.get("MTURK_SANDBOX", "").lower() == "true"
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": status,
                "method_count": len(METHOD_IDS),
                "sandbox": sandbox,
                "missing_env": [
                    v for v, present in [
                        ("AWS_ACCESS_KEY_ID", has_key),
                        ("AWS_SECRET_ACCESS_KEY", has_secret),
                    ] if not present
                ],
            }, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "mturk.hits.create.v1":
            return await self._hits_create(args)
        if method_id == "mturk.hits.list.v1":
            return await self._hits_list(args)
        if method_id == "mturk.assignments.list.v1":
            return await self._assignments_list(args)
        if method_id == "mturk.assignments.approve.v1":
            return await self._assignments_approve(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _check_creds(self) -> str:
        missing = [v for v in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY") if not os.environ.get(v)]
        if missing:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_CREDENTIALS",
                "missing_env": missing,
                "message": f"Set {' and '.join(missing)} environment variables.",
            }, indent=2, ensure_ascii=False)
        return ""

    async def _call_api(self, method_id: str, body: Dict[str, Any]) -> str:
        payload_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
        target = _TARGETS[method_id]
        headers = self._sign_request(target, payload_bytes)
        base_url = self._get_base_url()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(base_url, content=payload_bytes, headers=headers)
            if r.status_code >= 400:
                logger.info("%s HTTP %s target=%s: %s", PROVIDER_NAME, r.status_code, target, r.text[:300])
                return json.dumps({
                    "ok": False,
                    "error_code": "PROVIDER_ERROR",
                    "status": r.status_code,
                    "detail": r.text[:500],
                }, indent=2, ensure_ascii=False)
            return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _hits_create(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_creds()
        if cred_err:
            return cred_err
        required = ["title", "description", "reward", "assignment_duration_in_seconds", "lifetime_in_seconds", "question"]
        missing = [f for f in required if not args.get(f)]
        if missing:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARG",
                "missing": missing,
                "message": f"Required args: {', '.join(required)}",
            }, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {
            "Title": str(args["title"]),
            "Description": str(args["description"]),
            "Reward": str(args["reward"]),
            "AssignmentDurationInSeconds": int(args["assignment_duration_in_seconds"]),
            "LifetimeInSeconds": int(args["lifetime_in_seconds"]),
            "MaxAssignments": int(args.get("max_assignments", 1)),
            "Question": str(args["question"]),
        }
        raw = await self._call_api("mturk.hits.create.v1", body)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if not isinstance(data, dict) or "ok" in data:
            return raw
        hit = data.get("HIT", {})
        summary = f"Created HIT '{args['title']}' — ID: {hit.get('HITId', 'unknown')}"
        return summary + "\n\n```json\n" + json.dumps({"ok": True, "hit": hit}, indent=2, ensure_ascii=False) + "\n```"

    async def _hits_list(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_creds()
        if cred_err:
            return cred_err
        body: Dict[str, Any] = {
            "MaxResults": int(args.get("max_results", 10)),
        }
        next_token = str(args.get("next_token", "")).strip()
        if next_token:
            body["NextToken"] = next_token
        raw = await self._call_api("mturk.hits.list.v1", body)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if not isinstance(data, dict) or "ok" in data:
            return raw
        hits = data.get("HITs", [])
        summary = f"Found {len(hits)} HITs on MTurk."
        out: Dict[str, Any] = {
            "ok": True,
            "count": len(hits),
            "next_token": data.get("NextToken"),
            "hits": [
                {
                    "hit_id": h.get("HITId"),
                    "title": h.get("Title"),
                    "status": h.get("HITStatus"),
                    "reward": h.get("Reward"),
                    "max_assignments": h.get("MaxAssignments"),
                    "available_assignments": h.get("NumberOfAssignmentsAvailable"),
                    "completed_assignments": h.get("NumberOfAssignmentsCompleted"),
                    "expiration": h.get("Expiration"),
                }
                for h in hits
            ],
        }
        return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"

    async def _assignments_list(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_creds()
        if cred_err:
            return cred_err
        hit_id = str(args.get("hit_id", "")).strip()
        if not hit_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.hit_id required."}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"HITId": hit_id}
        status = str(args.get("assignment_status", "")).strip()
        if status:
            body["AssignmentStatuses"] = [status]
        raw = await self._call_api("mturk.assignments.list.v1", body)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if not isinstance(data, dict) or "ok" in data:
            return raw
        assignments = data.get("Assignments", [])
        summary = f"Found {len(assignments)} assignments for HIT {hit_id}."
        out: Dict[str, Any] = {
            "ok": True,
            "hit_id": hit_id,
            "count": len(assignments),
            "assignments": [
                {
                    "assignment_id": a.get("AssignmentId"),
                    "worker_id": a.get("WorkerId"),
                    "status": a.get("AssignmentStatus"),
                    "submit_time": a.get("SubmitTime"),
                    "answer": a.get("Answer"),
                }
                for a in assignments
            ],
        }
        return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"

    async def _assignments_approve(self, args: Dict[str, Any]) -> str:
        cred_err = self._check_creds()
        if cred_err:
            return cred_err
        assignment_id = str(args.get("assignment_id", "")).strip()
        if not assignment_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.assignment_id required."}, indent=2, ensure_ascii=False)
        body: Dict[str, Any] = {"AssignmentId": assignment_id}
        feedback = str(args.get("requester_feedback", "")).strip()
        if feedback:
            body["RequesterFeedback"] = feedback
        raw = await self._call_api("mturk.assignments.approve.v1", body)
        try:
            data = json.loads(raw)
        except (ValueError, KeyError):
            return raw
        if not isinstance(data, dict) or "ok" in data:
            return raw
        return json.dumps({"ok": True, "approved": True, "assignment_id": assignment_id}, indent=2, ensure_ascii=False)
