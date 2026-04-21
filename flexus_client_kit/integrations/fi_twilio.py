import asyncio
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("twilio")

PROVIDER_NAME = "twilio"
AUTH_PROVIDER_NAME = "twilio_manual"

# Twilio has multiple API bases depending on the product
API_BASE = "https://api.twilio.com"
VERIFY_BASE = "https://verify.twilio.com"
LOOKUP_BASE = "https://lookups.twilio.com"

METHOD_SPECS = {
    # -- Messaging API --
    "twilio.messages.send.v1": {
        "method": "POST",
        "path": "/2010-04-01/Accounts/{AccountSid}/Messages.json",
        "required": ["To", "Body"],
        "docs_url": "https://www.twilio.com/docs/messaging/api/message-resource#create-a-message-resource",
        "query_keys": [],
        "base": API_BASE,
    },
    "twilio.messages.list.v1": {
        "method": "GET",
        "path": "/2010-04-01/Accounts/{AccountSid}/Messages.json",
        "required": [],
        "docs_url": "https://www.twilio.com/docs/messaging/api/message-resource#read-multiple-message-resources",
        "query_keys": ["To", "From", "DateSent", "PageSize", "Page", "PageToken"],
        "base": API_BASE,
    },
    "twilio.messages.get.v1": {
        "method": "GET",
        "path": "/2010-04-01/Accounts/{AccountSid}/Messages/{Sid}.json",
        "required": ["Sid"],
        "docs_url": "https://www.twilio.com/docs/messaging/api/message-resource#fetch-a-message-resource",
        "query_keys": [],
        "base": API_BASE,
    },
    "twilio.messages.delete.v1": {
        "method": "DELETE",
        "path": "/2010-04-01/Accounts/{AccountSid}/Messages/{Sid}.json",
        "required": ["Sid"],
        "docs_url": "https://www.twilio.com/docs/messaging/api/message-resource#delete-a-message-resource",
        "query_keys": [],
        "base": API_BASE,
    },
    # -- Verify API --
    "twilio.verify.services.list.v2": {
        "method": "GET",
        "path": "/v2/Services",
        "required": [],
        "docs_url": "https://www.twilio.com/docs/verify/api/service#read-multiple-service-resources",
        "query_keys": ["PageSize", "Page", "PageToken"],
        "base": VERIFY_BASE,
    },
    "twilio.verify.create.v2": {
        "method": "POST",
        "path": "/v2/Services/{ServiceSid}/Verifications",
        "required": ["ServiceSid", "To"],
        "docs_url": "https://www.twilio.com/docs/verify/api/verification#create-a-verification-resource",
        "query_keys": [],
        "base": VERIFY_BASE,
    },
    "twilio.verify.check.v2": {
        "method": "POST",
        "path": "/v2/Services/{ServiceSid}/VerificationCheck",
        "required": ["ServiceSid", "To", "Code"],
        "docs_url": "https://www.twilio.com/docs/verify/api/verification-check#create-a-verificationcheck-resource",
        "query_keys": [],
        "base": VERIFY_BASE,
    },
    # -- Lookup API --
    "twilio.lookup.phone.v2": {
        "method": "GET",
        "path": "/v2/PhoneNumbers/{PhoneNumber}",
        "required": ["PhoneNumber"],
        "docs_url": "https://www.twilio.com/docs/lookup/v2-api",
        "query_keys": ["Fields"],
        "base": LOOKUP_BASE,
    },
    # -- Phone Numbers API --
    "twilio.phone.available.list.v1": {
        "method": "GET",
        "path": "/2010-04-01/Accounts/{AccountSid}/AvailablePhoneNumbers/{CountryCode}/Local.json",
        "required": ["CountryCode"],
        "docs_url": "https://www.twilio.com/docs/phone-numbers/api/availablephonenumberlocal-resource",
        "query_keys": ["AreaCode", "Contains", "SmsEnabled", "VoiceEnabled", "PageSize", "Page", "PageToken"],
        "base": API_BASE,
    },
    "twilio.phone.incoming.list.v1": {
        "method": "GET",
        "path": "/2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json",
        "required": [],
        "docs_url": "https://www.twilio.com/docs/phone-numbers/api/incomingphonenumber-resource#read-multiple-incomingphonenumber-resources",
        "query_keys": ["PhoneNumber", "FriendlyName", "PageSize", "Page", "PageToken"],
        "base": API_BASE,
    },
}

METHOD_IDS = list(METHOD_SPECS.keys())

WRITE_METHODS = {
    "twilio.messages.send.v1",
    "twilio.messages.delete.v1",
    "twilio.verify.create.v2",
    "twilio.verify.check.v2",
}

DESTRUCTIVE_METHODS = {
    "twilio.messages.delete.v1",
}

TWILIO_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name=PROVIDER_NAME,
    description='Interact with Twilio: send SMS, verify phone numbers (2FA), lookup numbers, manage phone numbers. ops: help, status, list_methods, call. Example: op="call", args={"method_id":"twilio.messages.send.v1","To":"+15558675310","From":"+15017122661","Body":"Hello!"}',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation: help, status, list_methods, call"},
            "args": {"type": "object", "description": "Arguments for the operation"},
        },
        "required": ["op"],
    },
)

TWILIO_PROMPT = (
    "Twilio integration available for SMS, verification, and phone number management. "
    "Phone numbers must be in E.164 format (e.g. +15558675310). "
    "For sending messages, provide either From (phone number) or MessagingServiceSid. "
    "For 2FA/verification, first list services with twilio.verify.services.list.v2 to get a ServiceSid, "
    "then use twilio.verify.create.v2 to send a code and twilio.verify.check.v2 to validate it. "
    "Common use cases: appointment reminders, order updates, two-factor authentication, phone number validation."
)


class IntegrationTwilio:
    def __init__(self, rcx=None, account_sid: str = "", auth_token: str = ""):
        self.rcx = rcx
        self.account_sid = (account_sid or "").strip()
        self.auth_token = (auth_token or "").strip()

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is None:
            return {}
        return self.rcx.external_auth.get(AUTH_PROVIDER_NAME) or {}

    def _get_creds(self) -> tuple[str, str]:
        auth = self._auth()
        sid = (
            self.account_sid
            or auth.get("account_sid", "")
            or auth.get("api_key", "")
            or os.environ.get("TWILIO_ACCOUNT_SID", "")
        ).strip()
        tok = (
            self.auth_token
            or auth.get("auth_token", "")
            or auth.get("api_secret", "")
            or os.environ.get("TWILIO_AUTH_TOKEN", "")
        ).strip()
        return sid, tok

    def _help(self) -> str:
        return (
            "provider=twilio\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus endpoint params/body fields\n"
            "for payload methods, pass body={...}; for pagination use PageSize/Page/PageToken\n"
            "Phone numbers must be in E.164 format (+15558675310)\n"
            "\n"
            "Examples:\n"
            '  op="call", args={"method_id":"twilio.messages.send.v1","To":"+15558675310","From":"+15017122661","Body":"Your appointment is tomorrow at 3PM"}\n'
            '  op="call", args={"method_id":"twilio.messages.send.v1","To":"+15558675310","MessagingServiceSid":"MGxxx","Body":"Order #123 has shipped"}\n'
            '  op="call", args={"method_id":"twilio.messages.list.v1","To":"+15558675310","PageSize":20}\n'
            '  op="call", args={"method_id":"twilio.verify.services.list.v2"}\n'
            '  op="call", args={"method_id":"twilio.verify.create.v2","ServiceSid":"VAxxx","To":"+15558675310","Channel":"sms"}\n'
            '  op="call", args={"method_id":"twilio.verify.check.v2","ServiceSid":"VAxxx","To":"+15558675310","Code":"123456"}\n'
            '  op="call", args={"method_id":"twilio.lookup.phone.v2","PhoneNumber":"+15558675310"}\n'
            '  op="call", args={"method_id":"twilio.phone.available.list.v1","CountryCode":"US","AreaCode":415}\n'
            '  op="call", args={"method_id":"twilio.phone.incoming.list.v1","PageSize":20}\n'
            "auth: use setup field account_sid/auth_token or external_auth['twilio_manual'] or TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN env vars"
        )

    def _status(self) -> str:
        sid, tok = self._get_creds()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if (sid and tok) else "missing_credentials",
            "has_account_sid": bool(sid),
            "has_auth_token": bool(tok),
            "setup_required": not (sid and tok),
            "ready_for_calls": bool(sid and tok),
            "method_count": len(METHOD_IDS),
        }, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error
        op = str(args.get("op", "")).strip()
        if not op:
            if args.get("method_id") or (isinstance(args.get("args"), dict) and args["args"].get("method_id")):
                op = "call"
            else:
                op = "help"
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_ids": METHOD_IDS,
                "methods": METHOD_SPECS,
            }, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."

        raw = args.get("args") or {}
        if not isinstance(raw, dict):
            return self._error("INVALID_ARGS", "args must be an object.")
        nested = raw.get("params")
        if nested is not None and not isinstance(nested, dict):
            return self._error("INVALID_ARGS", "args.params must be an object when provided.")

        call_args = dict(nested or {})
        call_args.update({k: v for k, v in raw.items() if k != "params"})
        if not call_args and "method_id" in args:
            call_args = {k: v for k, v in args.items() if k not in {"op", "args"}}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_SPECS:
            return self._error("METHOD_UNKNOWN", "Unknown method_id.", method_id=method_id)

        if method_id in DESTRUCTIVE_METHODS and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="twilio_destructive",
                confirm_command=f"twilio {method_id}",
                confirm_explanation=f"This will permanently delete a Twilio resource: {method_id}",
            )

        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        spec = METHOD_SPECS[method_id]
        b = self._extract_body(method_id, args)
        if isinstance(b, str):
            return self._error("INVALID_ARGS", b, method_id=method_id)
        for key in spec["required"]:
            v = args.get(key)
            if v is None and isinstance(b, dict):
                v = b.get(key)
            if v is None or (isinstance(v, str) and not v.strip()):
                return self._error("MISSING_REQUIRED", f"Missing required argument: {key}", method_id=method_id, missing=key)

        path = self._build_path(spec["path"], args)
        q = self._extract_query(args, spec)

        return await self._request_json(method_id, spec["method"], spec["base"], path, q, b)

    def _extract_query(self, args: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(args.get("query") or {}) if isinstance(args.get("query"), dict) else {}
        for k in spec.get("query_keys", []):
            if k in args and args[k] is not None:
                q[k] = args[k]
        return q

    def _extract_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any] | None | str:
        if isinstance(args.get("body"), dict):
            return args["body"]

        if method_id == "twilio.messages.send.v1":
            payload = {}
            for k in ("To", "From", "Body", "MediaUrl", "MessagingServiceSid", "StatusCallback"):
                if k in args and args[k] is not None:
                    payload[k] = args[k]
            if not payload.get("To") or not payload.get("Body"):
                return "Provide To and Body for message send."
            if not payload.get("From") and not payload.get("MessagingServiceSid"):
                return "Provide either From (phone number) or MessagingServiceSid for message send."
            return payload

        if method_id == "twilio.verify.create.v2":
            payload = {}
            for k in ("To", "Channel", "Locale", "CustomCode", "SendDigits"):
                if k in args and args[k] is not None:
                    payload[k] = args[k]
            return payload

        if method_id == "twilio.verify.check.v2":
            payload = {}
            for k in ("To", "Code"):
                if k in args and args[k] is not None:
                    payload[k] = args[k]
            return payload

        return None

    def _build_path(self, path_tpl: str, args: Dict[str, Any]) -> str:
        sid, _ = self._get_creds()
        path = path_tpl
        for key in ("AccountSid", "Sid", "ServiceSid", "CountryCode", "PhoneNumber"):
            token = "{" + key + "}"
            if token in path:
                if key == "AccountSid":
                    path = path.replace(token, sid)
                else:
                    path = path.replace(token, str(args.get(key, "")).strip())
        return path

    async def _request_json(
        self,
        method_id: str,
        method: str,
        base: str,
        path: str,
        query: Dict[str, Any],
        body: Dict[str, Any] | None,
    ) -> str:
        sid, tok = self._get_creds()
        if not sid or not tok:
            return self._error("AUTH_MISSING", "Set Twilio account_sid and auth_token in external auth or TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN env vars.", method_id=method_id)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        url = base + path

        try:
            async with httpx.AsyncClient(timeout=30.0) as cli:
                response = None
                for attempt in range(4):
                    response = await cli.request(
                        method,
                        url,
                        headers=headers,
                        auth=(sid, tok),
                        params=query or None,
                        data=body if method in {"POST", "PUT", "PATCH", "DELETE"} else None,
                    )
                    if response.status_code != 429:
                        break
                    wait_s = min(2 ** attempt, 30)
                    logger.warning("twilio rate limited method=%s wait=%ss attempt=%s", method_id, wait_s, attempt + 1)
                    await asyncio.sleep(wait_s)
                assert response is not None
        except Exception as e:
            logger.exception("twilio request failed: %s", method_id)
            return self._error("REQUEST_FAILED", str(e), method_id=method_id)

        data: Any = {}
        if response.text:
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text

        if response.status_code >= 400:
            error_code = "PROVIDER_ERROR"
            message = "Twilio request failed."
            if response.status_code == 401:
                error_code = "AUTH_REJECTED"
                message = "Twilio rejected the credentials. Check that Account SID and Auth Token are valid."
            elif response.status_code == 403:
                error_code = "INSUFFICIENT_PERMISSIONS"
                message = "Twilio accepted the credentials but denied this operation due to missing permissions."
            elif response.status_code == 404:
                error_code = "NOT_FOUND"
                message = "The requested Twilio resource was not found."
            elif response.status_code == 429:
                error_code = "RATE_LIMITED"
                message = "Twilio rate limit exceeded after retries."
            elif response.status_code == 400:
                error_code = "BAD_REQUEST"
                message = "Twilio reported a bad request. Check parameters and formatting."
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "status": response.status_code,
                "error_code": error_code,
                "message": message,
                "setup_required": False,
                "has_account_sid": bool(sid),
                "has_auth_token": bool(tok),
                "error": data,
            }, indent=2, ensure_ascii=False)

        result = {
            "ok": True,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "status": response.status_code,
            "result": data,
        }
        if isinstance(data, dict):
            result["result_preview"] = {
                "results_count": len(data.get("messages", [])) if isinstance(data.get("messages"), list) else None,
                "has_more": bool(data.get("next_page_uri")),
                "next_page_uri": data.get("next_page_uri"),
                "sid": data.get("sid"),
                "status": data.get("status"),
                "to": data.get("to"),
                "from": data.get("from"),
                "valid": data.get("valid"),
                "total": data.get("total"),
            }
        return json.dumps(result, indent=2, ensure_ascii=False)

    def _error(self, code: str, message: str, **extra) -> str:
        payload = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "error_code": code,
            "message": message,
            "setup_required": code == "AUTH_MISSING",
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)
