import datetime
import json
import logging
import os
import time
from typing import Any, Dict, List

import httpx
import jwt

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("google_play")

PROVIDER_NAME = "google_play"
METHOD_IDS = [
    "google_play.reviews.list.v1",
]

_BASE_URL = "https://androidpublisher.googleapis.com/androidpublisher/v3"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
_TIMEOUT = 30.0


class IntegrationGooglePlay:
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
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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
        if method_id == "google_play.reviews.list.v1":
            return await self._reviews_list(call_args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        sa_json_str = os.environ.get("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON", "")
        if not sa_json_str:
            raise ValueError(
                "GOOGLE_PLAY_SERVICE_ACCOUNT_JSON env var not set. "
                "It should contain the full JSON content of a Google service account key file "
                "(download from GCP Console > IAM > Service Accounts > Keys). "
                "The service account must have Google Play Developer API access with androidpublisher scope."
            )
        sa = json.loads(sa_json_str)
        client_email = sa["client_email"]
        private_key = sa["private_key"].replace("\\n", "\n")
        token_uri = sa.get("token_uri", _TOKEN_URL)
        now = int(time.time())
        payload = {
            "iss": client_email,
            "scope": _SCOPE,
            "aud": token_uri,
            "iat": now,
            "exp": now + 3600,
        }
        signed = jwt.encode(payload, private_key, algorithm="RS256")
        resp = await client.post(
            token_uri,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": signed,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def _reviews_list(self, args: Dict[str, Any]) -> str:
        package_name = str(args.get("package_name", "")).strip()
        if not package_name:
            package_name = os.environ.get("GOOGLE_PLAY_PACKAGE_NAME", "").strip()
        if not package_name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.package_name required (or set GOOGLE_PLAY_PACKAGE_NAME env var)."}, indent=2, ensure_ascii=False)
        max_results = min(int(args.get("max_results", 50)), 100)
        start_index = int(args.get("start_index", 0))
        translation_language = str(args.get("translation_language", "")).strip()
        params: Dict[str, Any] = {"maxResults": max_results, "startIndex": start_index}
        if translation_language:
            params["translationLanguage"] = translation_language
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                access_token = await self._get_access_token(client)
                headers = {"Authorization": f"Bearer {access_token}"}
                url = f"{_BASE_URL}/applications/{package_name}/reviews"
                r = await client.get(url, params=params, headers=headers)
            if r.status_code == 401:
                logger.info("%s auth error for package %s: %s", PROVIDER_NAME, package_name, r.text[:200])
                return json.dumps({"ok": False, "error_code": "AUTH_ERROR", "message": "Google Play authentication failed. Check GOOGLE_PLAY_SERVICE_ACCOUNT_JSON and service account permissions."}, indent=2, ensure_ascii=False)
            if r.status_code == 403:
                logger.info("%s permission denied for package %s: %s", PROVIDER_NAME, package_name, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PERMISSION_DENIED", "message": f"Service account does not have permission to access reviews for {package_name}."}, indent=2, ensure_ascii=False)
            if r.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": f"App {package_name} not found in Google Play."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s for package %s: %s", PROVIDER_NAME, r.status_code, package_name, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            raw_reviews = data.get("reviews", [])
            page_info = data.get("pageInfo", {})
            total = page_info.get("totalResults", len(raw_reviews))
            reviews: List[Dict[str, Any]] = []
            for rev in raw_reviews:
                user_comment: Dict[str, Any] = {}
                for c in rev.get("comments", []):
                    if "userComment" in c:
                        user_comment = c["userComment"]
                        break
                seconds = int(user_comment.get("lastModified", {}).get("seconds", 0) or 0)
                date_str = (
                    datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    if seconds else ""
                )
                reviews.append({
                    "review_id": rev.get("reviewId"),
                    "author": rev.get("authorName"),
                    "text": user_comment.get("text"),
                    "rating": user_comment.get("starRating"),
                    "date": date_str,
                })
            out: Dict[str, Any] = {
                "ok": True,
                "package_name": package_name,
                "total": total,
                "count": len(reviews),
                "reviews": reviews,
            }
            summary = f"Retrieved {len(reviews)} reviews for {package_name} (total reported: {total})."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except ValueError as e:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "message": str(e)}, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            return json.dumps({"ok": False, "error_code": "CONFIG_ERROR", "message": f"Invalid GOOGLE_PLAY_SERVICE_ACCOUNT_JSON: {e}"}, indent=2, ensure_ascii=False)
        except KeyError as e:
            return json.dumps({"ok": False, "error_code": "CONFIG_ERROR", "message": f"Missing field in service account JSON: {e}"}, indent=2, ensure_ascii=False)
        except jwt.PyJWTError as e:
            return json.dumps({"ok": False, "error_code": "AUTH_ERROR", "message": f"JWT signing failed: {e}"}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
