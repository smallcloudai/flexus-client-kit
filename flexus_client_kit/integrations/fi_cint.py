import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("cint")

PROVIDER_NAME = "cint"
METHOD_IDS = [
    "cint.accounts.list.v1",
    "cint.accounts.users.list.v1",
    "cint.accounts.service_clients.list.v1",
    "cint.accounts.user_business_units.list.v1",
    "cint.projects.create.v1",
    "cint.projects.get.v1",
    "cint.projects.feasibility.get.v1",
    "cint.target_groups.create.v1",
    "cint.target_groups.list.v1",
    "cint.target_groups.get.v1",
    "cint.target_groups.details.get.v1",
    "cint.target_groups.quota_distribution.get.v1",
    "cint.target_groups.exclusions.list.v1",
    "cint.target_groups.price.get.v1",
    "cint.target_groups.price_prediction.get.v1",
    "cint.target_groups.supplier_quota_distribution.get.v1",
    "cint.target_groups.supplier_quota_distribution_draft.get.v1",
    "cint.fielding.launch.v1",
    "cint.fielding.job_status.get.v1",
]

_BASE_URL = "https://api.cint.com/v1"
_TIMEOUT = 30.0

# Cint Exchange Demand API uses an enterprise-issued API key.
# Required values:
# - CINT_API_KEY: bearer token issued by Cint for the account.
# - CINT_API_VERSION: optional header override if Flexus must pin a newer reviewed version.
# Runtime IDs such as account_id, project_id, target_group_id, business_unit_id, and profile_id
# are passed per call for now because different Cint accounts can expose different organizational
# structures and pricing models.
CINT_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationCint:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_key(self) -> str:
        try:
            return str(os.environ.get("CINT_API_KEY", "")).strip()
        except (TypeError, ValueError):
            return ""

    def _api_version(self) -> str:
        try:
            return str(os.environ.get("CINT_API_VERSION", "2025-12-18")).strip() or "2025-12-18"
        except (TypeError, ValueError):
            return "2025-12-18"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key()}",
            "Cint-API-Version": self._api_version(),
            "Content-Type": "application/json",
        }

    def _status(self) -> str:
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "ready" if self._api_key() else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "api_key",
                "required_env": ["CINT_API_KEY"],
                "optional_env": ["CINT_API_VERSION"],
                "products": [
                    "Accounts and users",
                    "Projects",
                    "Target Groups",
                    "Draft feasibility",
                    "Quota Distribution",
                    "Supplier Distribution",
                    "Pricing and Price Prediction",
                    "Fielding Jobs",
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
            "- Cint is an enterprise sample marketplace; API access must be approved by Cint.\n"
            "- account_id is required on all demand-side flows, and business_unit_id is required on pricing flows.\n"
            "- launch returns an async fielding job that should be polled until completion.\n"
            "- some pricing methods require Private Exchange to be enabled on the account.\n"
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

    def _result(self, method_id: str, result: Any) -> str:
        return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_id": method_id, "result": result}, indent=2, ensure_ascii=False)

    def _require_str(self, method_id: str, args: Dict[str, Any], key: str) -> str:
        value = str(args.get(key, "")).strip()
        if not value:
            raise ValueError(f"{key} is required for {method_id}.")
        return value

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
                return self._error(method_id, "METHOD_UNKNOWN", "Unknown Cint method.")
            if not self._api_key():
                return self._error(method_id, "AUTH_MISSING", "Set CINT_API_KEY in the runtime environment.")
            return await self._dispatch(method_id, call_args)
        except (TypeError, ValueError) as e:
            logger.error("cint called_by_model failed", exc_info=e)
            return self._error("cint.runtime", "RUNTIME_ERROR", f"{type(e).__name__}: {e}")

    async def _request(
        self,
        method_id: str,
        http_method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        idempotency_key: str = "",
    ) -> str:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                url = _BASE_URL + path
                headers = self._headers()
                if idempotency_key:
                    headers["Idempotency-Key"] = idempotency_key
                if http_method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif http_method == "POST":
                    response = await client.post(url, headers=headers, params=params, json=body)
                else:
                    return self._error(method_id, "UNSUPPORTED_HTTP_METHOD", f"Unsupported HTTP method {http_method}.")
        except httpx.TimeoutException:
            return self._error(method_id, "TIMEOUT", "Cint request timed out.")
        except httpx.HTTPError as e:
            logger.error("cint request failed", exc_info=e)
            return self._error(method_id, "HTTP_ERROR", f"{type(e).__name__}: {e}")

        if response.status_code >= 400:
            detail: Any = response.text[:1000]
            try:
                detail = response.json()
            except json.JSONDecodeError:
                pass
            logger.info("cint provider error method=%s status=%s body=%s", method_id, response.status_code, response.text[:300])
            return self._error(method_id, "PROVIDER_ERROR", "Cint returned an error.", http_status=response.status_code, detail=detail)

        result: Dict[str, Any] | str = {}
        if response.text.strip():
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = response.text
        location = response.headers.get("location", "")
        if location and isinstance(result, dict):
            result["job_status_url"] = location
        return self._result(method_id, result)

    def _project_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        name = self._require_str(method_id, args, "name")
        body: Dict[str, Any] = {"name": name}
        for key in [
            "target_completes",
            "country_code",
            "language_code",
            "category",
            "business_unit_id",
            "project_manager_id",
            "study_type",
            "industry_code",
        ]:
            value = args.get(key)
            if value not in (None, ""):
                body[key] = value
        return body

    def _target_group_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        for key in [
            "name",
            "business_unit_id",
            "project_manager_id",
            "study_type_code",
            "industry_code",
            "country_code",
            "language_code",
            "cost_per_interview",
            "estimated_incidence_rate",
            "expected_incidence_rate",
            "estimated_length_of_interview",
            "expected_length_of_interview_minutes",
            "target_completes",
            "fielding_start_date",
            "fielding_end_date",
            "survey_url",
            "fielding_specification",
            "filling_goal",
            "profile",
            "quota_sets",
            "profile_criteria",
            "supply_allocations",
        ]:
            value = args.get(key)
            if value not in (None, ""):
                body[key] = value
        if not body:
            raise ValueError(f"At least one target group field is required for {method_id}.")
        return body

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "cint.accounts.list.v1":
                return await self._request(method_id, "GET", "/accounts")

            account_id = self._require_str(method_id, args, "account_id")
            if method_id == "cint.accounts.users.list.v1":
                return await self._request(method_id, "GET", f"/accounts/{account_id}/users")
            if method_id == "cint.accounts.service_clients.list.v1":
                return await self._request(method_id, "GET", f"/accounts/{account_id}/service-clients")
            if method_id == "cint.accounts.user_business_units.list.v1":
                user_id = self._require_str(method_id, args, "user_id")
                return await self._request(method_id, "GET", f"/accounts/{account_id}/users/{user_id}/business-units")
            if method_id == "cint.projects.create.v1":
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/projects",
                    body=self._project_body(method_id, args),
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.projects.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}")
            if method_id == "cint.projects.feasibility.get.v1":
                project_id = str(args.get("project_id", "")).strip()
                if project_id:
                    return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}/feasibility")
                feasibility_body: Dict[str, Any] = {}
                for key in [
                    "country_code",
                    "language_code",
                    "target_completes",
                    "profile_criteria",
                    "quota_sets",
                    "business_unit_id",
                    "project_manager_id",
                    "study_type_code",
                    "industry_code",
                    "fielding_specification",
                    "cost_per_interview",
                    "expected_incidence_rate",
                    "expected_length_of_interview_minutes",
                    "filling_goal",
                    "profile",
                ]:
                    value = args.get(key)
                    if value not in (None, ""):
                        feasibility_body[key] = value
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/target-groups/calculate-feasibility",
                    body=feasibility_body,
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.target_groups.create.v1":
                project_id = self._require_str(method_id, args, "project_id")
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/projects/{project_id}/target-groups",
                    body=self._target_group_body(method_id, args),
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.target_groups.list.v1":
                project_id = self._require_str(method_id, args, "project_id")
                params: Dict[str, Any] = {}
                for key in ["name", "language_code", "country_code", "page", "page_size", "status"]:
                    value = args.get(key)
                    if value not in (None, ""):
                        params[key] = value
                return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}/target-groups", params=params)
            if method_id == "cint.target_groups.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}")
            if method_id == "cint.target_groups.details.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/details")
            if method_id == "cint.target_groups.quota_distribution.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                return await self._request(
                    method_id,
                    "GET",
                    f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/quota-distribution",
                )
            if method_id == "cint.target_groups.exclusions.list.v1":
                project_id = self._require_str(method_id, args, "project_id")
                return await self._request(method_id, "GET", f"/demand/accounts/{account_id}/projects/{project_id}/exclusions")
            if method_id == "cint.target_groups.price.get.v1":
                business_unit_id = self._require_str(method_id, args, "business_unit_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                return await self._request(
                    method_id,
                    "GET",
                    f"/demand/accounts/{account_id}/business-units/{business_unit_id}/target-groups/{target_group_id}/price",
                )
            if method_id == "cint.target_groups.price_prediction.get.v1":
                business_unit_id = self._require_str(method_id, args, "business_unit_id")
                price_prediction_body: Dict[str, Any] = {}
                for key in [
                    "study_type_code",
                    "industry_code",
                    "fielding_specification",
                    "expected_incidence_rate",
                    "expected_length_of_interview_minutes",
                    "filling_goal",
                    "profile",
                    "pricing_model",
                ]:
                    value = args.get(key)
                    if value not in (None, ""):
                        price_prediction_body[key] = value
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/business-units/{business_unit_id}/generate-price-prediction",
                    body=price_prediction_body,
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.target_groups.supplier_quota_distribution.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                profile_id = self._require_str(method_id, args, "profile_id")
                return await self._request(
                    method_id,
                    "GET",
                    f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/profiles/{profile_id}/supplier-quota-distribution",
                )
            if method_id == "cint.target_groups.supplier_quota_distribution_draft.get.v1":
                draft_supplier_distribution_body: Dict[str, Any] = {}
                for key in [
                    "business_unit_id",
                    "project_manager_id",
                    "study_type_code",
                    "industry_code",
                    "fielding_specification",
                    "expected_incidence_rate",
                    "expected_length_of_interview_minutes",
                    "filling_goal",
                    "profile",
                ]:
                    value = args.get(key)
                    if value not in (None, ""):
                        draft_supplier_distribution_body[key] = value
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/supplier-quota-distribution/draft",
                    body=draft_supplier_distribution_body,
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.fielding.launch.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                body: Dict[str, Any] = {}
                end_fielding_date = args.get("end_fielding_date")
                if end_fielding_date not in (None, ""):
                    body["end_fielding_date"] = end_fielding_date
                return await self._request(
                    method_id,
                    "POST",
                    f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/fielding-run-jobs/launch-from-draft",
                    body=body or None,
                    idempotency_key=str(args.get("idempotency_key", "")).strip(),
                )
            if method_id == "cint.fielding.job_status.get.v1":
                project_id = self._require_str(method_id, args, "project_id")
                target_group_id = self._require_str(method_id, args, "target_group_id")
                return await self._request(
                    method_id,
                    "GET",
                    f"/demand/accounts/{account_id}/projects/{project_id}/target-groups/{target_group_id}/fielding-run-jobs/launch-from-draft",
                )
        except ValueError as e:
            return self._error(method_id, "INVALID_ARGS", str(e))
        return self._error(method_id, "METHOD_UNIMPLEMENTED", "Method is declared but not implemented.")
