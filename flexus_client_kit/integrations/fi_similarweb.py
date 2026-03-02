import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("similarweb")

PROVIDER_NAME = "similarweb"
METHOD_IDS = [
    "similarweb.similar_sites.get.v1",
    "similarweb.traffic_and_engagement.get.v1",
    "similarweb.traffic_geography.get.v1",
    "similarweb.traffic_sources.get.v1",
    "similarweb.website.marketing_channel_sources.get.v1",
    "similarweb.website.similar_sites.get.v1",
    "similarweb.website.traffic_and_engagement.get.v1",
    "similarweb.website_ranking.get.v1",
]

_BASE_URL = "https://api.similarweb.com/v1"


def _default_dates(args: Dict[str, Any]) -> tuple:
    start = str(args.get("start_date", "")).strip()
    end = str(args.get("end_date", "")).strip()
    if not start or not end:
        now = datetime.utcnow()
        end = f"{now.year}-{now.month:02d}"
        three_ago = now - timedelta(days=90)
        start = f"{three_ago.year}-{three_ago.month:02d}"
    return start, end


def _get_domain(args: Dict[str, Any]) -> str:
    return str(args.get("domain", "") or args.get("query", "")).strip().lower()


class IntegrationSimilarweb:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("similarweb") or {}).get("api_key", "")
        return os.environ.get("SIMILARWEB_API_KEY", "")

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
            key = self._get_api_key()
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available",
                "method_count": len(METHOD_IDS),
                "auth": "configured" if key else "missing: SIMILARWEB_API_KEY",
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
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set SIMILARWEB_API_KEY env var."}, indent=2, ensure_ascii=False)
        domain = _get_domain(args)
        if not domain:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.domain or args.query (domain name) required"}, indent=2, ensure_ascii=False)

        if method_id in ("similarweb.traffic_and_engagement.get.v1", "similarweb.website.traffic_and_engagement.get.v1"):
            return await self._traffic_and_engagement(domain, api_key, args)
        if method_id == "similarweb.traffic_sources.get.v1":
            return await self._traffic_sources(domain, api_key, args)
        if method_id == "similarweb.website.marketing_channel_sources.get.v1":
            return await self._marketing_channels(domain, api_key, args)
        if method_id == "similarweb.traffic_geography.get.v1":
            return await self._traffic_geography(domain, api_key, args)
        if method_id == "similarweb.website_ranking.get.v1":
            return await self._website_ranking(domain, api_key)
        if method_id in ("similarweb.similar_sites.get.v1", "similarweb.website.similar_sites.get.v1"):
            return await self._similar_sites(domain, api_key)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _traffic_and_engagement(self, domain: str, api_key: str, args: Dict[str, Any]) -> str:
        start, end = _default_dates(args)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/total-traffic-and-engagement/visits",
                    params={
                        "api_key": api_key,
                        "country": args.get("geo", "world"),
                        "granularity": "monthly",
                        "main_domain_only": "false",
                        "startDate": start,
                        "endDate": end,
                    },
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            visits = data.get("visits", [])
            result = {"ok": True, "domain": domain, "start": start, "end": end, "visits": visits, "meta": data.get("meta", {})}
            return f"Found {len(visits)} month(s) of traffic data for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _traffic_sources(self, domain: str, api_key: str, args: Dict[str, Any]) -> str:
        start, end = _default_dates(args)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/traffic-sources/overview",
                    params={
                        "api_key": api_key,
                        "country": args.get("geo", "world"),
                        "granularity": "monthly",
                        "main_domain_only": "false",
                        "startDate": start,
                        "endDate": end,
                    },
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            overview = data.get("overview", data.get("traffic_sources", data))
            result = {"ok": True, "domain": domain, "sources": overview, "meta": data.get("meta", {})}
            return f"Traffic sources for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _marketing_channels(self, domain: str, api_key: str, args: Dict[str, Any]) -> str:
        start, end = _default_dates(args)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/traffic-sources/marketing-channels-overview",
                    params={
                        "api_key": api_key,
                        "country": args.get("geo", "world"),
                        "granularity": "monthly",
                        "main_domain_only": "false",
                        "startDate": start,
                        "endDate": end,
                    },
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            channels = data.get("channels", data.get("overview", data))
            result = {"ok": True, "domain": domain, "marketing_channels": channels, "meta": data.get("meta", {})}
            return f"Marketing channel sources for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _traffic_geography(self, domain: str, api_key: str, args: Dict[str, Any]) -> str:
        start, end = _default_dates(args)
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/geo/traffic-by-country/visits",
                    params={
                        "api_key": api_key,
                        "startDate": start,
                        "endDate": end,
                    },
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            geo = data.get("records", data.get("traffic", []))
            result = {"ok": True, "domain": domain, "geography": geo, "meta": data.get("meta", {})}
            return f"Geography data for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _website_ranking(self, domain: str, api_key: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/global-rank",
                    params={"api_key": api_key},
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            result = {"ok": True, "domain": domain, "global_rank": data.get("global_rank", data), "meta": data.get("meta", {})}
            return f"Global rank for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _similar_sites(self, domain: str, api_key: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(
                    _BASE_URL + f"/website/{domain}/similar-sites",
                    params={"api_key": api_key},
                )
            if r.status_code >= 400:
                logger.info("similarweb HTTP %s: %s", r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            sites = data.get("similar_sites", data.get("sites", []))
            result = {"ok": True, "domain": domain, "similar_sites": sites, "meta": data.get("meta", {})}
            return f"Found {len(sites) if isinstance(sites, list) else 1} similar site(s) for {domain}.\n\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
