import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("pandadoc")
PROVIDER_NAME = "pandadoc"
METHOD_IDS = [
    "pandadoc.documents.create.v1",
    "pandadoc.documents.details.get.v1",
]
_BASE_URL = "https://api.pandadoc.com/public/v1"
_TIMEOUT_S = 30.0

_STATUS_MAP = {
    0: "draft",
    1: "sent",
    2: "completed",
    3: "expired",
    4: "declined",
    5: "viewed",
    6: "waiting_approval",
}


def _status_str(code: Any) -> str:
    if isinstance(code, int) and code in _STATUS_MAP:
        return _STATUS_MAP[code]
    return str(code) if code is not None else ""


class IntegrationPandadoc:
    def _headers(self, api_key: str) -> Dict[str, str]:
        return {
            "Authorization": f"API-Key {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _ensure_api_key(self) -> str:
        key = os.environ.get("PANDADOC_API_KEY", "")
        if not key:
            raise ValueError("NO_CREDENTIALS")
        return key

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
            key = os.environ.get("PANDADOC_API_KEY", "")
            status = "available" if key else "no_credentials"
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": status,
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
        if method_id == "pandadoc.documents.create.v1":
            return await self._documents_create(call_args)
        if method_id == "pandadoc.documents.details.get.v1":
            return await self._documents_details_get(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _documents_create(self, call_args: Dict[str, Any]) -> str:
        try:
            api_key = self._ensure_api_key()
        except ValueError:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        name = str(call_args.get("name", "")).strip()
        if not name:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "name required"},
                indent=2,
                ensure_ascii=False,
            )
        template_uuid = str(call_args.get("template_uuid", "")).strip()
        if not template_uuid:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "template_uuid required"},
                indent=2,
                ensure_ascii=False,
            )
        recipients_raw = call_args.get("recipients")
        if not isinstance(recipients_raw, list) or not recipients_raw:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "recipients required (list with at least one object)"},
                indent=2,
                ensure_ascii=False,
            )
        recipients: List[Dict[str, Any]] = []
        for r in recipients_raw:
            if not isinstance(r, dict):
                continue
            email = str(r.get("email", "")).strip()
            if not email:
                continue
            rec: Dict[str, Any] = {"email": email}
            fn = str(r.get("first_name", "")).strip()
            ln = str(r.get("last_name", "")).strip()
            role = str(r.get("role", "")).strip()
            if fn:
                rec["first_name"] = fn
            if ln:
                rec["last_name"] = ln
            if role:
                rec["role"] = role
            recipients.append(rec)
        if not recipients:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "recipients must have at least one object with email"},
                indent=2,
                ensure_ascii=False,
            )
        body: Dict[str, Any] = {
            "name": name,
            "template_uuid": template_uuid,
            "recipients": recipients,
        }
        tokens_raw = call_args.get("tokens")
        if isinstance(tokens_raw, list) and tokens_raw:
            tokens: List[Dict[str, str]] = []
            for t in tokens_raw:
                if not isinstance(t, dict):
                    continue
                tn = str(t.get("name", "")).strip()
                tv = str(t.get("value", "")).strip()
                if tn:
                    tokens.append({"name": tn, "value": tv})
            if tokens:
                body["tokens"] = tokens
        url = f"{_BASE_URL}/documents"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                response = await client.post(url, json=body, headers=self._headers(api_key))
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("PandaDoc timeout documents create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("PandaDoc HTTP error documents create status=%s: %s", e.response.status_code, e)
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
            logger.info("PandaDoc HTTP error documents create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PandaDoc JSON decode error documents create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        try:
            doc_id = payload.get("id")
            doc_name = payload.get("name", "")
            status_raw = payload.get("status")
            status = _status_str(status_raw)
            date_created = payload.get("date_created", "")
            expiration_date = payload.get("expiration_date", "")
            uuid_val = payload.get("uuid", "")
        except (KeyError, ValueError) as e:
            logger.info("PandaDoc response missing key documents create: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        normalized = {
            "ok": True,
            "id": doc_id,
            "name": doc_name,
            "status": status,
            "date_created": date_created,
            "expiration_date": expiration_date,
            "uuid": uuid_val,
        }
        return json.dumps(normalized, indent=2, ensure_ascii=False)

    async def _documents_details_get(self, call_args: Dict[str, Any]) -> str:
        try:
            api_key = self._ensure_api_key()
        except ValueError:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        document_id = str(call_args.get("document_id", "")).strip()
        if not document_id:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "document_id required"},
                indent=2,
                ensure_ascii=False,
            )
        url = f"{_BASE_URL}/documents/{document_id}/details"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                response = await client.get(url, headers=self._headers(api_key))
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("PandaDoc timeout documents details document_id=%s: %s", document_id, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME, "document_id": document_id},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("PandaDoc HTTP error documents details document_id=%s status=%s: %s", document_id, e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "provider": PROVIDER_NAME,
                    "document_id": document_id,
                    "status_code": e.response.status_code,
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("PandaDoc HTTP error documents details document_id=%s: %s", document_id, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "provider": PROVIDER_NAME, "document_id": document_id},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
        except json.JSONDecodeError as e:
            logger.info("PandaDoc JSON decode error documents details document_id=%s: %s", document_id, e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "provider": PROVIDER_NAME, "document_id": document_id},
                indent=2,
                ensure_ascii=False,
            )
        try:
            doc_id = payload.get("id")
            doc_name = payload.get("name", "")
            status_raw = payload.get("status")
            status = _status_str(status_raw)
            date_created = payload.get("date_created", "")
            date_modified = payload.get("date_modified", "")
            expiration_date = payload.get("expiration_date", "")
            recipients_raw = payload.get("recipients") or []
            recipients: List[Dict[str, Any]] = []
            for r in recipients_raw:
                if not isinstance(r, dict):
                    continue
                rec: Dict[str, Any] = {
                    "email": str(r.get("email", "")),
                    "first_name": str(r.get("first_name", "")),
                    "last_name": str(r.get("last_name", "")),
                    "role": str(r.get("role", "")),
                    "has_completed": bool(r.get("has_completed", False)),
                }
                recipients.append(rec)
        except (KeyError, ValueError) as e:
            logger.info("PandaDoc response missing key documents details document_id=%s: %s", document_id, e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "provider": PROVIDER_NAME, "document_id": document_id},
                indent=2,
                ensure_ascii=False,
            )
        normalized = {
            "ok": True,
            "id": doc_id,
            "name": doc_name,
            "status": status,
            "date_created": date_created,
            "date_modified": date_modified,
            "expiration_date": expiration_date,
            "recipients": recipients,
        }
        return json.dumps(normalized, indent=2, ensure_ascii=False)
