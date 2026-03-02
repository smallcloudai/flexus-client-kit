import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("wikimedia")

PROVIDER_NAME = "wikimedia"
METHOD_IDS = [
    "wikimedia.pageviews.per_article.v1",
    "wikimedia.pageviews.aggregate.v1",
]

_BASE_URL = "https://wikimedia.org/api/rest_v1"
_HEADERS = {"User-Agent": "Flexus-Market-Signal/1.0 (contact@flexus.app)"}


class IntegrationWikimedia:
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
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "wikimedia.pageviews.per_article.v1":
            return await self._per_article(args)
        if method_id == "wikimedia.pageviews.aggregate.v1":
            return await self._aggregate(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _date_range(self, args: Dict[str, Any], granularity: str) -> tuple[str, str]:
        fmt_daily = "%Y%m%d"
        fmt_monthly = "%Y%m01"
        fmt = fmt_daily if granularity == "daily" else fmt_monthly

        start_arg = str(args.get("start_date", ""))
        end_arg = str(args.get("end_date", ""))

        if start_arg and end_arg:
            return start_arg, end_arg

        now = datetime.utcnow()
        time_window = str(args.get("time_window", "90d"))
        days = 90
        if time_window.endswith("d"):
            days = int(time_window[:-1])
        elif time_window.endswith("m"):
            days = int(time_window[:-1]) * 30

        start = now - timedelta(days=days)
        return start.strftime(fmt), now.strftime(fmt)

    async def _per_article(self, args: Dict[str, Any]) -> str:
        article = str(args.get("article", args.get("query", ""))).strip()
        if not article:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "message": "args.article required (Wikipedia article title)."}, indent=2, ensure_ascii=False)

        article_encoded = article.replace(" ", "_")
        project = str(args.get("project", "en.wikipedia.org"))
        granularity = str(args.get("granularity", "monthly"))
        if granularity not in ("daily", "monthly"):
            granularity = "monthly"

        start, end = self._date_range(args, granularity)
        url = f"{_BASE_URL}/metrics/pageviews/per-article/{project}/all-access/all-agents/{article_encoded}/{granularity}/{start}/{end}"

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, headers=_HEADERS)
            if r.status_code == 404:
                return json.dumps({"ok": False, "error_code": "NOT_FOUND", "message": f"Article '{article}' not found on {project}."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            total_views = sum(i.get("views", 0) for i in items)
            include_raw = bool(args.get("include_raw"))
            out: Dict[str, Any] = {
                "ok": True,
                "article": article,
                "project": project,
                "granularity": granularity,
                "period": {"start": start, "end": end},
                "total_views": total_views,
                "data_points": items if include_raw else [
                    {"timestamp": i.get("timestamp"), "views": i.get("views")}
                    for i in items
                ],
            }
            summary = f"Pageviews for '{article}' on {project}: {total_views:,} total views ({granularity})."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _aggregate(self, args: Dict[str, Any]) -> str:
        project = str(args.get("project", "en.wikipedia.org"))
        granularity = str(args.get("granularity", "monthly"))
        if granularity not in ("daily", "monthly", "hourly"):
            granularity = "monthly"

        start, end = self._date_range(args, granularity)
        url = f"{_BASE_URL}/metrics/pageviews/aggregate/{project}/all-access/all-agents/{granularity}/{start}/{end}"

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, headers=_HEADERS)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            data = r.json()
            items = data.get("items", [])
            total_views = sum(i.get("views", 0) for i in items)
            out: Dict[str, Any] = {
                "ok": True,
                "project": project,
                "granularity": granularity,
                "period": {"start": start, "end": end},
                "total_views": total_views,
                "data_points": [
                    {"timestamp": i.get("timestamp"), "views": i.get("views")}
                    for i in items
                ],
            }
            summary = f"Aggregate pageviews for {project}: {total_views:,} total views ({granularity})."
            return summary + "\n\n```json\n" + json.dumps(out, indent=2, ensure_ascii=False) + "\n```"
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)
