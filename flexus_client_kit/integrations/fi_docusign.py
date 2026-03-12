import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("docusign")

PROVIDER_NAME = "docusign"
METHOD_IDS = [
    "docusign.envelopes.create.v1",
    "docusign.envelopes.get.v1",
    "docusign.envelopes.list_status_changes.v1",
]
_DEFAULT_BASE_URL = "https://demo.docusign.net/restapi/v2.1"


def _base_url() -> str:
    return os.environ.get("DOCUSIGN_BASE_URL", "").strip() or _DEFAULT_BASE_URL


def _api_base() -> str:
    account_id = os.environ.get("DOCUSIGN_ACCOUNT_ID", "").strip()
    base = _base_url()
    return f"{base}/accounts/{account_id}"


def _check_credentials() -> bool:
    token = os.environ.get("DOCUSIGN_ACCESS_TOKEN", "").strip()
    account_id = os.environ.get("DOCUSIGN_ACCOUNT_ID", "").strip()
    return bool(token and account_id)


def _headers() -> Dict[str, str]:
    token = os.environ.get("DOCUSIGN_ACCESS_TOKEN", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _normalize_envelope_create(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "envelope_id": p.get("envelopeId"),
        "status": p.get("status"),
        "created_date_time": p.get("createdDateTime"),
        "email_subject": p.get("emailSubject"),
    }


def _normalize_envelope_get(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "envelope_id": p.get("envelopeId"),
        "status": p.get("status"),
        "email_subject": p.get("emailSubject"),
        "created_date_time": p.get("createdDateTime"),
        "sent_date_time": p.get("sentDateTime"),
        "completed_date_time": p.get("completedDateTime"),
        "declined_date_time": p.get("declinedDateTime"),
    }


def _normalize_envelope_list_item(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "envelope_id": p.get("envelopeId"),
        "status": p.get("status"),
        "email_subject": p.get("emailSubject"),
        "created_date_time": p.get("createdDateTime"),
        "sent_date_time": p.get("sentDateTime"),
        "completed_date_time": p.get("completedDateTime"),
    }


class IntegrationDocusign:
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
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if _check_credentials() else "no_credentials",
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
            return "Error: unknown op."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "docusign.envelopes.create.v1":
            return await self._envelopes_create(call_args)
        if method_id == "docusign.envelopes.get.v1":
            return await self._envelopes_get(call_args)
        if method_id == "docusign.envelopes.list_status_changes.v1":
            return await self._envelopes_list_status_changes(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _envelopes_create(self, call_args: Dict[str, Any]) -> str:
        if not _check_credentials():
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        template_id = str(call_args.get("template_id", "")).strip()
        email_subject = str(call_args.get("email_subject", "")).strip()
        recipients = call_args.get("recipients")
        if not template_id:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "template_id required"},
                indent=2,
                ensure_ascii=False,
            )
        if not email_subject:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "email_subject required"},
                indent=2,
                ensure_ascii=False,
            )
        if not isinstance(recipients, list) or not recipients:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "recipients (list with name+email) required"},
                indent=2,
                ensure_ascii=False,
            )
        status = str(call_args.get("status", "sent")).strip() or "sent"
        if status not in ("sent", "created"):
            status = "sent"
        template_roles: List[Dict[str, Any]] = []
        for r in recipients:
            if not isinstance(r, dict):
                continue
            email = str(r.get("email", "")).strip()
            name = str(r.get("name", "")).strip()
            if not email:
                continue
            template_roles.append({
                "email": email,
                "name": name or email,
                "roleName": "signer",
            })
        if not template_roles:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "recipients must have at least one with email"},
                indent=2,
                ensure_ascii=False,
            )
        body: Dict[str, Any] = {
            "status": status,
            "emailSubject": email_subject,
            "templateId": template_id,
            "templateRoles": template_roles,
        }
        url = f"{_api_base()}/envelopes"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("DocuSign envelopes.create timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("DocuSign envelopes.create HTTP status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("DocuSign envelopes.create HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("DocuSign envelopes.create JSON decode: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        result = _normalize_envelope_create(payload)
        return json.dumps({"ok": True, **result}, indent=2, ensure_ascii=False)

    async def _envelopes_get(self, call_args: Dict[str, Any]) -> str:
        if not _check_credentials():
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        envelope_id = str(call_args.get("envelope_id", "")).strip()
        if not envelope_id:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "envelope_id required"},
                indent=2,
                ensure_ascii=False,
            )
        url = f"{_api_base()}/envelopes/{envelope_id}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("DocuSign envelopes.get timeout envelope_id=%s: %s", envelope_id, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("DocuSign envelopes.get HTTP status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("DocuSign envelopes.get HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("DocuSign envelopes.get JSON decode: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        result = _normalize_envelope_get(payload)
        return json.dumps({"ok": True, **result}, indent=2, ensure_ascii=False)

    async def _envelopes_list_status_changes(self, call_args: Dict[str, Any]) -> str:
        if not _check_credentials():
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        from_date = str(call_args.get("from_date", "")).strip()
        if not from_date:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARGS", "message": "from_date (ISO8601) required"},
                indent=2,
                ensure_ascii=False,
            )
        to_date = str(call_args.get("to_date", "")).strip() or None
        status = str(call_args.get("status", "")).strip() or None
        count_raw = call_args.get("count", 20)
        try:
            count = int(count_raw) if count_raw is not None else 20
        except (TypeError, ValueError):
            count = 20
        if count < 1:
            count = 20
        if count > 100:
            count = 100
        params: Dict[str, Any] = {
            "from_date": from_date,
            "count": count,
        }
        if to_date:
            params["to_date"] = to_date
        if status:
            params["status"] = status
        url = f"{_api_base()}/envelopes"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("DocuSign envelopes.list_status_changes timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("DocuSign envelopes.list_status_changes HTTP status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("DocuSign envelopes.list_status_changes HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except ValueError as e:
            logger.info("DocuSign envelopes.list_status_changes JSON decode: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            envelopes_raw = payload.get("envelopes") or []
        except (KeyError, ValueError) as e:
            logger.info("DocuSign envelopes.list_status_changes response structure: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        envelopes = [_normalize_envelope_list_item(e) for e in envelopes_raw if isinstance(e, dict)]
        return json.dumps({"ok": True, "envelopes": envelopes}, indent=2, ensure_ascii=False)
