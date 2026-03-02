import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("grafana")

PROVIDER_NAME = "grafana"
METHOD_IDS = [
    "grafana.alerts.list.v1",
]


class IntegrationGrafana:
    def _check_credentials(self) -> str:
        token = os.environ.get("GRAFANA_API_TOKEN", "")
        base_url = os.environ.get("GRAFANA_BASE_URL", "")
        if not token or not base_url:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "NO_CREDENTIALS",
                    "provider": PROVIDER_NAME,
                    "message": "GRAFANA_API_TOKEN and GRAFANA_BASE_URL env vars required",
                },
                indent=2,
                ensure_ascii=False,
            )
        return ""

    def _base_url(self) -> str:
        return os.environ.get("GRAFANA_BASE_URL", "").rstrip("/")

    def _headers(self) -> Dict[str, str]:
        token = os.environ.get("GRAFANA_API_TOKEN", "")
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
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
                "op=help\n"
                "op=status\n"
                "op=list_methods\n"
                "op=call(args={method_id: ...})\n"
                f"known_method_ids={len(METHOD_IDS)}"
            )
        if op == "status":
            err = self._check_credentials()
            if err:
                return err
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available",
                    "method_count": len(METHOD_IDS),
                },
                indent=2,
                ensure_ascii=False,
            )
        if op == "list_methods":
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS},
                indent=2,
                ensure_ascii=False,
            )
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "grafana.alerts.list.v1":
            return await self._alerts_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _alerts_list(self, call_args: Dict[str, Any]) -> str:
        err = self._check_credentials()
        if err:
            return err
        active = call_args.get("active", True)
        if active is None:
            active = True
        silenced = call_args.get("silenced", False)
        if silenced is None:
            silenced = False
        inhibited = call_args.get("inhibited", False)
        if inhibited is None:
            inhibited = False
        filter_list = call_args.get("filter")
        if filter_list is None:
            filter_list = []
        elif isinstance(filter_list, str):
            filter_list = [filter_list] if filter_list.strip() else []
        limit = call_args.get("limit", 50)
        try:
            limit = min(max(int(limit), 1), 500)
        except (TypeError, ValueError):
            limit = 50
        base = self._base_url()
        url = f"{base}/api/alertmanager/grafana/api/v2/alerts"
        params: Dict[str, Any] = {
            "active": str(active).lower(),
            "silenced": str(silenced).lower(),
            "inhibited": str(inhibited).lower(),
        }
        for f in filter_list:
            if isinstance(f, str) and f.strip():
                params.setdefault("filter", []).append(f)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, headers=self._headers(), params=params)
                if resp.status_code != 200:
                    logger.info("Grafana alerts.list error %s: %s", resp.status_code, resp.text[:200])
                    return json.dumps(
                        {
                            "ok": False,
                            "error_code": "PROVIDER_ERROR",
                            "status": resp.status_code,
                            "detail": resp.text[:500],
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                raw = resp.json()
        except httpx.TimeoutException as e:
            logger.info("Grafana timeout alerts.list: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Grafana HTTP error alerts.list: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)},
                indent=2,
                ensure_ascii=False,
            )
        if not isinstance(raw, list):
            logger.info("Grafana alerts.list unexpected response type: %s", type(raw))
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized: List[Dict[str, Any]] = []
        for item in raw[:limit]:
            try:
                labels = item.get("labels") or {}
                annotations = item.get("annotations") or {}
                status = item.get("status") or {}
                name = labels.get("alertname", labels.get("__alert_rule_uid__", ""))
                state = status.get("state", "")
                summary = annotations.get("summary", annotations.get("description", ""))
                starts_at = item.get("startsAt", "")
                ends_at = item.get("endsAt", "")
                normalized.append({
                    "name": name,
                    "state": state,
                    "labels": labels,
                    "summary": summary,
                    "starts_at": starts_at,
                    "ends_at": ends_at,
                })
            except (KeyError, ValueError) as e:
                logger.info("Grafana alerts.list item parse error: %s", e)
                continue
        return json.dumps(
            {"ok": True, "alerts": normalized, "count": len(normalized)},
            indent=2,
            ensure_ascii=False,
        )
