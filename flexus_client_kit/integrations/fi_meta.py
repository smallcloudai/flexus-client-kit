import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("meta")

PROVIDER_NAME = "meta"
METHOD_IDS = [
    "meta.adcreatives.create.v1",
    "meta.adcreatives.list.v1",
    "meta.adimages.create.v1",
    "meta.ads_insights.get.v1",
    "meta.adsets.create.v1",
    "meta.campaigns.create.v1",
    "meta.insights.query.v1",
]

_BASE_URL = "https://graph.facebook.com/v19.0"
_TIMEOUT = 30.0


class IntegrationMeta:
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
                f"methods: {', '.join(METHOD_IDS)}\n"
                "note: Requires META_ACCESS_TOKEN and META_AD_ACCOUNT_ID env vars."
            )
        if op == "status":
            token = self._token()
            account = self._ad_account()
            ok = bool(token and account)
            return json.dumps({
                "ok": ok,
                "provider": PROVIDER_NAME,
                "status": "ready" if ok else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "has_token": bool(token),
                "has_ad_account": bool(account),
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

    def _token(self) -> str:
        return os.environ.get("META_ACCESS_TOKEN", "")

    def _ad_account(self) -> str:
        return os.environ.get("META_AD_ACCOUNT_ID", "")

    def _no_creds(self, method_id: str) -> str:
        return json.dumps({
            "ok": False,
            "error_code": "NO_CREDENTIALS",
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "message": "Set META_ACCESS_TOKEN and META_AD_ACCOUNT_ID environment variables.",
        }, indent=2, ensure_ascii=False)

    def _api_error(self, method_id: str, status_code: int, body: str) -> str:
        try:
            data = json.loads(body)
            fb_error = data.get("error", {})
            message = fb_error.get("message", body)
            code = fb_error.get("code", status_code)
        except json.JSONDecodeError:
            message = body
            code = status_code
        logger.info("meta api error method=%s status=%s code=%s msg=%s", method_id, status_code, code, message)
        return json.dumps({
            "ok": False,
            "error_code": "API_ERROR",
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "http_status": status_code,
            "fb_code": code,
            "message": message,
        }, indent=2, ensure_ascii=False)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "meta.adcreatives.create.v1":
            return await self._adcreatives_create(method_id, args)
        if method_id == "meta.adcreatives.list.v1":
            return await self._adcreatives_list(method_id, args)
        if method_id == "meta.adimages.create.v1":
            return await self._adimages_create(method_id, args)
        if method_id == "meta.ads_insights.get.v1":
            return await self._ads_insights_get(method_id, args)
        if method_id == "meta.adsets.create.v1":
            return await self._adsets_create(method_id, args)
        if method_id == "meta.campaigns.create.v1":
            return await self._campaigns_create(method_id, args)
        if method_id == "meta.insights.query.v1":
            return await self._insights_query(method_id, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    # ── meta.adcreatives.create.v1 ──────────────────────────────────────────

    async def _adcreatives_create(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        name = str(args.get("name", "")).strip()
        object_story_spec = args.get("object_story_spec")
        if not name:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"}, indent=2, ensure_ascii=False)
        if not isinstance(object_story_spec, dict):
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "object_story_spec (dict) is required"}, indent=2, ensure_ascii=False)

        status = str(args.get("status", "PAUSED")).upper()
        body: Dict[str, Any] = {
            "name": name,
            "object_story_spec": object_story_spec,
            "status": status,
            "access_token": token,
        }

        url = f"{_BASE_URL}/{account}/adcreatives"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(url, json=body)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.adcreatives.list.v1 ────────────────────────────────────────────

    async def _adcreatives_list(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        limit = int(args.get("limit", 25))
        fields = args.get("fields", ["id", "name", "status", "object_story_spec"])
        if isinstance(fields, list):
            fields_str = ",".join(fields)
        else:
            fields_str = str(fields)

        url = f"{_BASE_URL}/{account}/adcreatives"
        params: Dict[str, Any] = {
            "access_token": token,
            "fields": fields_str,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(url, params=params)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.adimages.create.v1 ─────────────────────────────────────────────

    async def _adimages_create(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        # image_url: fetch-and-upload via url param; or bytes (not supported here)
        image_url = str(args.get("image_url", "")).strip()
        filename = str(args.get("filename", "image.jpg")).strip()

        if not image_url:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "image_url is required"}, indent=2, ensure_ascii=False)

        url = f"{_BASE_URL}/{account}/adimages"
        body: Dict[str, Any] = {
            "filename": filename,
            "url": image_url,
            "access_token": token,
        }

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(url, json=body)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.ads_insights.get.v1 ────────────────────────────────────────────

    async def _ads_insights_get(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        default_fields = ["impressions", "clicks", "spend", "ctr", "cpc"]
        fields = args.get("fields", default_fields)
        if isinstance(fields, list):
            fields_str = ",".join(fields)
        else:
            fields_str = str(fields)

        date_preset: Optional[str] = args.get("date_preset")
        time_range: Optional[Dict[str, str]] = args.get("time_range")
        level: Optional[str] = args.get("level")
        limit = int(args.get("limit", 25))

        url = f"{_BASE_URL}/{account}/insights"
        params: Dict[str, Any] = {
            "access_token": token,
            "fields": fields_str,
            "limit": limit,
        }
        if date_preset:
            params["date_preset"] = date_preset
        if time_range and isinstance(time_range, dict):
            params["time_range"] = json.dumps(time_range, ensure_ascii=False)
        if level:
            params["level"] = level

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(url, params=params)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.adsets.create.v1 ───────────────────────────────────────────────

    async def _adsets_create(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        name = str(args.get("name", "")).strip()
        campaign_id = str(args.get("campaign_id", "")).strip()
        optimization_goal = str(args.get("optimization_goal", "REACH")).strip()
        billing_event = str(args.get("billing_event", "IMPRESSIONS")).strip()
        daily_budget = args.get("daily_budget")
        targeting = args.get("targeting")
        status = str(args.get("status", "PAUSED")).upper()

        if not name:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"}, indent=2, ensure_ascii=False)
        if not campaign_id:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "campaign_id is required"}, indent=2, ensure_ascii=False)

        body: Dict[str, Any] = {
            "name": name,
            "campaign_id": campaign_id,
            "optimization_goal": optimization_goal,
            "billing_event": billing_event,
            "status": status,
            "access_token": token,
        }
        if daily_budget is not None:
            body["daily_budget"] = int(daily_budget)
        if isinstance(targeting, dict):
            body["targeting"] = targeting

        url = f"{_BASE_URL}/{account}/adsets"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(url, json=body)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.campaigns.create.v1 ────────────────────────────────────────────

    async def _campaigns_create(self, method_id: str, args: Dict[str, Any]) -> str:
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        name = str(args.get("name", "")).strip()
        objective = str(args.get("objective", "OUTCOME_AWARENESS")).strip()
        status = str(args.get("status", "PAUSED")).upper()
        special_ad_categories = args.get("special_ad_categories", [])

        if not name:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"}, indent=2, ensure_ascii=False)

        body: Dict[str, Any] = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": special_ad_categories if isinstance(special_ad_categories, list) else [],
            "access_token": token,
        }

        url = f"{_BASE_URL}/{account}/campaigns"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(url, json=body)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)

    # ── meta.insights.query.v1 ──────────────────────────────────────────────

    async def _insights_query(self, method_id: str, args: Dict[str, Any]) -> str:
        """Flexible insights query: supports object_id override (campaign/adset/ad) and breakdowns."""
        token = self._token()
        account = self._ad_account()
        if not token or not account:
            return self._no_creds(method_id)

        # object_id: use specific campaign/adset/ad id, or fall back to ad account
        object_id = str(args.get("object_id", account)).strip()
        fields = args.get("fields", ["impressions", "clicks", "spend", "ctr", "cpc", "reach"])
        if isinstance(fields, list):
            fields_str = ",".join(fields)
        else:
            fields_str = str(fields)

        breakdowns = args.get("breakdowns")
        date_preset: Optional[str] = args.get("date_preset")
        time_range: Optional[Dict[str, str]] = args.get("time_range")
        level: Optional[str] = args.get("level")
        limit = int(args.get("limit", 25))

        url = f"{_BASE_URL}/{object_id}/insights"
        params: Dict[str, Any] = {
            "access_token": token,
            "fields": fields_str,
            "limit": limit,
        }
        if breakdowns:
            params["breakdowns"] = breakdowns if isinstance(breakdowns, str) else ",".join(breakdowns)
        if date_preset:
            params["date_preset"] = date_preset
        if time_range and isinstance(time_range, dict):
            params["time_range"] = json.dumps(time_range, ensure_ascii=False)
        if level:
            params["level"] = level

        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.get(url, params=params)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return json.dumps({"ok": False, "error_code": "INVALID_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": data}, indent=2, ensure_ascii=False)
