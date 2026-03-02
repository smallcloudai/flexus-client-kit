import json
import logging
import os
import time
from typing import Any, Dict

import httpx
import jwt

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("appstoreconnect")

PROVIDER_NAME = "appstoreconnect"
METHOD_IDS = [
    "appstoreconnect.customer_reviews.list.v1",
]

_BASE_URL = "https://api.appstoreconnect.apple.com/v1"


def _no_creds() -> str:
    return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)


class IntegrationAppstoreconnect:
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
            key_id = os.environ.get("APPSTORECONNECT_KEY_ID", "")
            issuer_id = os.environ.get("APPSTORECONNECT_ISSUER_ID", "")
            private_key = os.environ.get("APPSTORECONNECT_PRIVATE_KEY", "")
            has_creds = bool(key_id and issuer_id and private_key)
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if has_creds else "no_credentials",
                "method_count": len(METHOD_IDS),
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
        if method_id == "appstoreconnect.customer_reviews.list.v1":
            return await self._customer_reviews_list(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _ok(self, method_label: str, data: Any) -> str:
        return f"appstoreconnect.{method_label} ok\n\n```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("appstoreconnect provider error status=%s detail=%s", status_code, detail)
        return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": status_code, "detail": detail}, indent=2, ensure_ascii=False)

    def _has_creds(self) -> bool:
        return bool(
            os.environ.get("APPSTORECONNECT_KEY_ID", "")
            and os.environ.get("APPSTORECONNECT_ISSUER_ID", "")
            and os.environ.get("APPSTORECONNECT_PRIVATE_KEY", "")
        )

    def _make_token(self) -> str:
        key_id = os.environ.get("APPSTORECONNECT_KEY_ID", "")
        issuer_id = os.environ.get("APPSTORECONNECT_ISSUER_ID", "")
        private_key_raw = os.environ.get("APPSTORECONNECT_PRIVATE_KEY", "")
        private_key = private_key_raw.replace("\\n", "\n")
        now = int(time.time())
        payload = {
            "iss": issuer_id,
            "iat": now,
            "exp": now + 1200,
            "aud": "appstoreconnect-v1",
        }
        token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": key_id})
        return token

    async def _customer_reviews_list(self, args: Dict[str, Any]) -> str:
        if not self._has_creds():
            return _no_creds()
        app_id = str(args.get("app_id", "")).strip()
        if not app_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "app_id"}, indent=2, ensure_ascii=False)
        limit = min(int(args.get("limit", 25)), 200)
        sort = str(args.get("sort", "-createdDate"))
        params: Dict[str, Any] = {"sort": sort, "limit": limit}
        min_rating = args.get("min_rating")
        if min_rating is not None:
            params["filter[rating]"] = int(min_rating)
        territory = args.get("territory")
        if territory:
            params["filter[territory]"] = str(territory)
        try:
            token = self._make_token()
        except jwt.PyJWTError as e:
            return json.dumps({"ok": False, "error_code": "JWT_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    f"{_BASE_URL}/apps/{app_id}/customerReviews",
                    params=params,
                    headers=headers,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        raw_items = data.get("data", [])
        reviews = []
        for item in raw_items:
            try:
                attrs = item["attributes"]
                reviews.append({
                    "id": item["id"],
                    "title": attrs.get("title"),
                    "body": attrs.get("body"),
                    "rating": attrs.get("rating"),
                    "date": attrs.get("createdDate"),
                    "reviewer": attrs.get("reviewerNickname"),
                })
            except KeyError:
                continue
        result = {
            "reviews": reviews,
            "total": len(reviews),
            "links": data.get("links"),
        }
        return self._ok("customer_reviews.list.v1", result)
