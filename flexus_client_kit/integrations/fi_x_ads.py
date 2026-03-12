import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import requests
from requests_oauthlib import OAuth1

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("x_ads")

PROVIDER_NAME = "x_ads"
METHOD_IDS = [
    "x_ads.campaigns.create.v1",
    "x_ads.line_items.create.v1",
    "x_ads.stats.query.v1",
]

_BASE_URL = "https://ads-api.x.com/12"
_TIMEOUT = 30.0


class IntegrationXAds:
    def _get_oauth(self) -> OAuth1:
        return OAuth1(
            os.environ.get("X_ADS_CONSUMER_KEY", ""),
            os.environ.get("X_ADS_CONSUMER_SECRET", ""),
            os.environ.get("X_ADS_ACCESS_TOKEN", ""),
            os.environ.get("X_ADS_ACCESS_TOKEN_SECRET", ""),
        )

    def _get_account_id(self) -> str:
        return os.environ.get("X_ADS_ACCOUNT_ID", "")

    def _check_credentials(self) -> str:
        if not all([
            os.environ.get("X_ADS_CONSUMER_KEY"),
            os.environ.get("X_ADS_CONSUMER_SECRET"),
            os.environ.get("X_ADS_ACCESS_TOKEN"),
            os.environ.get("X_ADS_ACCESS_TOKEN_SECRET"),
            os.environ.get("X_ADS_ACCOUNT_ID"),
        ]):
            return json.dumps({
                "ok": False,
                "error_code": "NO_CREDENTIALS",
                "provider": PROVIDER_NAME,
                "message": "Set X_ADS_CONSUMER_KEY, X_ADS_CONSUMER_SECRET, X_ADS_ACCESS_TOKEN, X_ADS_ACCESS_TOKEN_SECRET, X_ADS_ACCOUNT_ID",
            }, indent=2, ensure_ascii=False)
        return ""

    def _api_error(self, method_id: str, status_code: int, body: str) -> str:
        try:
            data = json.loads(body)
            msg = data.get("errors", [{}])[0].get("message", body) if data.get("errors") else body
        except (json.JSONDecodeError, IndexError, KeyError):
            msg = body
        logger.info("x_ads api error method=%s status=%s msg=%s", method_id, status_code, msg)
        return json.dumps({
            "ok": False,
            "error_code": "API_ERROR",
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "http_status": status_code,
            "message": msg,
        }, indent=2, ensure_ascii=False)

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
            cred_err = self._check_credentials()
            if cred_err:
                return json.dumps({
                    "ok": False,
                    "provider": PROVIDER_NAME,
                    "status": "missing_credentials",
                    "method_count": len(METHOD_IDS),
                }, indent=2, ensure_ascii=False)
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available",
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
        cred_err = self._check_credentials()
        if cred_err:
            return cred_err
        if method_id == "x_ads.campaigns.create.v1":
            return await self._campaigns_create(method_id, args)
        if method_id == "x_ads.line_items.create.v1":
            return await self._line_items_create(method_id, args)
        if method_id == "x_ads.stats.query.v1":
            return await self._stats_query(method_id, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _campaigns_create(self, method_id: str, args: Dict[str, Any]) -> str:
        name = str(args.get("name", "")).strip()
        funding_instrument_id = str(args.get("funding_instrument_id", "")).strip()
        daily_budget_amount_local_micro = args.get("daily_budget_amount_local_micro")
        if not name:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"}, indent=2, ensure_ascii=False)
        if not funding_instrument_id:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "funding_instrument_id is required"}, indent=2, ensure_ascii=False)
        if daily_budget_amount_local_micro is None:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "daily_budget_amount_local_micro is required"}, indent=2, ensure_ascii=False)
        try:
            daily_budget_amount_local_micro = int(daily_budget_amount_local_micro)
        except (TypeError, ValueError):
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "daily_budget_amount_local_micro must be int"}, indent=2, ensure_ascii=False)

        entity_status = str(args.get("entity_status", "PAUSED")).strip()
        start_time = str(args.get("start_time", "")).strip()
        end_time = str(args.get("end_time", "")).strip()

        data: Dict[str, Any] = {
            "name": name,
            "funding_instrument_id": funding_instrument_id,
            "daily_budget_amount_local_micro": daily_budget_amount_local_micro,
            "entity_status": entity_status,
        }
        if start_time:
            data["start_time"] = start_time
        if end_time:
            data["end_time"] = end_time

        url = f"{_BASE_URL}/accounts/{self._get_account_id()}/campaigns"

        def _do_post() -> requests.Response:
            return requests.post(
                url,
                auth=self._get_oauth(),
                data=data,
                timeout=_TIMEOUT,
            )

        try:
            resp = await asyncio.to_thread(_do_post)
        except requests.Timeout as e:
            logger.info("x_ads timeout method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            logger.info("x_ads request error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            payload = resp.json()
            raw = payload.get("data", payload)
            if isinstance(raw, list):
                raw = raw[0] if raw else {}
            campaign_id = raw.get("id", "")
            campaign_name = raw.get("name", name)
            entity_status_res = raw.get("entity_status", entity_status)
            daily_budget = raw.get("daily_budget_amount_local_micro", daily_budget_amount_local_micro)
            currency = raw.get("currency", "")
            result = {
                "id": campaign_id,
                "name": campaign_name,
                "entity_status": entity_status_res,
                "daily_budget_amount_local_micro": daily_budget,
                "currency": currency,
            }
        except (KeyError, ValueError, IndexError) as e:
            logger.info("x_ads response parse error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "UNEXPECTED_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    async def _line_items_create(self, method_id: str, args: Dict[str, Any]) -> str:
        campaign_id = str(args.get("campaign_id", "")).strip()
        name = str(args.get("name", "")).strip()
        objective = str(args.get("objective", "")).strip()
        if not campaign_id:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "campaign_id is required"}, indent=2, ensure_ascii=False)
        if not name:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"}, indent=2, ensure_ascii=False)
        if not objective:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "objective is required"}, indent=2, ensure_ascii=False)

        product_type = str(args.get("product_type", "PROMOTED_TWEETS")).strip()
        placements = args.get("placements", ["ALL_ON_TWITTER"])
        if isinstance(placements, str):
            placements = [placements]
        bid_type = str(args.get("bid_type", "AUTO")).strip()
        entity_status = str(args.get("entity_status", "PAUSED")).strip()

        data: Dict[str, Any] = {
            "campaign_id": campaign_id,
            "name": name,
            "product_type": product_type,
            "bid_type": bid_type,
            "objective": objective,
            "entity_status": entity_status,
        }
        if placements:
            data["placements"] = ",".join(str(p) for p in placements)

        url = f"{_BASE_URL}/accounts/{self._get_account_id()}/line_items"

        def _do_post() -> requests.Response:
            return requests.post(
                url,
                auth=self._get_oauth(),
                data=data,
                timeout=_TIMEOUT,
            )

        try:
            resp = await asyncio.to_thread(_do_post)
        except requests.Timeout as e:
            logger.info("x_ads timeout method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            logger.info("x_ads request error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code not in (200, 201):
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            payload = resp.json()
            raw = payload.get("data", payload)
            if isinstance(raw, list):
                raw = raw[0] if raw else {}
            line_item_id = raw.get("id", "")
            line_item_name = raw.get("name", name)
            result = {
                "id": line_item_id,
                "name": line_item_name,
                "campaign_id": campaign_id,
                "product_type": raw.get("product_type", product_type),
                "placements": raw.get("placements", placements) if isinstance(raw.get("placements"), list) else placements,
                "bid_type": raw.get("bid_type", bid_type),
                "objective": raw.get("objective", objective),
                "entity_status": raw.get("entity_status", entity_status),
            }
        except (KeyError, ValueError, IndexError) as e:
            logger.info("x_ads response parse error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "UNEXPECTED_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    async def _stats_query(self, method_id: str, args: Dict[str, Any]) -> str:
        entity = str(args.get("entity", "")).strip()
        entity_ids = args.get("entity_ids")
        metric_groups = args.get("metric_groups")
        start_time = str(args.get("start_time", "")).strip()
        end_time = str(args.get("end_time", "")).strip()
        if not entity:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "entity is required"}, indent=2, ensure_ascii=False)
        if not entity_ids:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "entity_ids is required"}, indent=2, ensure_ascii=False)
        if not metric_groups:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "metric_groups is required"}, indent=2, ensure_ascii=False)
        if not start_time:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "start_time is required"}, indent=2, ensure_ascii=False)
        if not end_time:
            return json.dumps({"ok": False, "error_code": "INVALID_ARGS", "message": "end_time is required"}, indent=2, ensure_ascii=False)

        if isinstance(entity_ids, list):
            entity_ids_str = ",".join(str(x) for x in entity_ids)
        else:
            entity_ids_str = str(entity_ids)
        if isinstance(metric_groups, list):
            metric_groups_str = ",".join(str(x) for x in metric_groups)
        else:
            metric_groups_str = str(metric_groups)

        granularity = str(args.get("granularity", "DAY")).strip()

        params: Dict[str, str] = {
            "entity": entity,
            "entity_ids": entity_ids_str,
            "metric_groups": metric_groups_str,
            "start_time": start_time,
            "end_time": end_time,
            "granularity": granularity,
        }

        url = f"{_BASE_URL}/stats/accounts/{self._get_account_id()}"

        def _do_get() -> requests.Response:
            return requests.get(
                url,
                auth=self._get_oauth(),
                params=params,
                timeout=_TIMEOUT,
            )

        try:
            resp = await asyncio.to_thread(_do_get)
        except requests.Timeout as e:
            logger.info("x_ads timeout method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "method_id": method_id}, indent=2, ensure_ascii=False)
        except requests.RequestException as e:
            logger.info("x_ads request error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "method_id": method_id, "message": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            return self._api_error(method_id, resp.status_code, resp.text)

        try:
            payload = resp.json()
            raw_data = payload.get("data", [])
            if not isinstance(raw_data, list):
                raw_data = [raw_data] if raw_data else []

            result: List[Dict[str, Any]] = []
            for item in raw_data:
                row_id = item.get("id", "")
                id_data = item.get("id_data", [])
                metrics_obj = {}
                if id_data and isinstance(id_data[0], dict):
                    metrics_obj = id_data[0].get("metrics", {})
                elif isinstance(item.get("metrics"), dict):
                    metrics_obj = item.get("metrics", {})

                def _sum_or_first(val: Any) -> int:
                    if val is None:
                        return 0
                    if isinstance(val, list):
                        return sum(int(x) for x in val if x is not None) if val else 0
                    try:
                        return int(val)
                    except (TypeError, ValueError):
                        return 0

                impressions = _sum_or_first(metrics_obj.get("impressions"))
                clicks = _sum_or_first(metrics_obj.get("clicks"))
                spend_micro = _sum_or_first(metrics_obj.get("billed_charge_local_micro"))

                result.append({
                    "id": row_id,
                    "metrics": {
                        "impressions": impressions,
                        "clicks": clicks,
                        "spend_micro": spend_micro,
                    },
                })
        except (KeyError, ValueError, TypeError) as e:
            logger.info("x_ads response parse error method=%s: %s", method_id, e)
            return json.dumps({"ok": False, "error_code": "UNEXPECTED_RESPONSE", "method_id": method_id}, indent=2, ensure_ascii=False)

        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)
