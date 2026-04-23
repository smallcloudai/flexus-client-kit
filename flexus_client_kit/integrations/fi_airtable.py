import asyncio
import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("airtable")

PROVIDER_NAME = "airtable"
AUTH_PROVIDER_NAME = "airtable"
AIRTABLE_BASE = "https://api.airtable.com/v0"
AIRTABLE_CONTENT_BASE = "https://content.airtable.com/v0"

METHOD_SPECS = {
    "airtable.bases.list.v1": {
        "method": "GET",
        "path": "/meta/bases",
        "required": [],
        "docs_url": "https://airtable.com/developers/web/api/list-bases",
        "query_keys": ["offset", "limit"],
    },
    "airtable.bases.schema.get.v1": {
        "method": "GET",
        "path": "/meta/bases/{base_id}/tables",
        "required": ["base_id"],
        "docs_url": "https://airtable.com/developers/web/api/get-base-schema",
        "query_keys": ["include"],
    },
    "airtable.bases.create.v1": {
        "method": "POST",
        "path": "/meta/bases",
        "required": ["name"],
        "docs_url": "https://airtable.com/developers/web/api/create-base",
        "query_keys": [],
    },
    "airtable.tables.create.v1": {
        "method": "POST",
        "path": "/meta/bases/{base_id}/tables",
        "required": ["base_id", "name"],
        "docs_url": "https://airtable.com/developers/web/api/create-table",
        "query_keys": [],
    },
    "airtable.tables.update.v1": {
        "method": "PATCH",
        "path": "/meta/bases/{base_id}/tables/{table_id}",
        "required": ["base_id", "table_id"],
        "docs_url": "https://airtable.com/developers/web/api/update-table",
        "query_keys": [],
    },
    "airtable.fields.create.v1": {
        "method": "POST",
        "path": "/meta/bases/{base_id}/tables/{table_id}/fields",
        "required": ["base_id", "table_id", "name", "type"],
        "docs_url": "https://airtable.com/developers/web/api/create-field",
        "query_keys": [],
    },
    "airtable.fields.update.v1": {
        "method": "PATCH",
        "path": "/meta/bases/{base_id}/tables/{table_id}/fields/{field_id}",
        "required": ["base_id", "table_id", "field_id"],
        "docs_url": "https://airtable.com/developers/web/api/update-field",
        "query_keys": [],
    },
    "airtable.records.list.v1": {
        "method": "GET",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name"],
        "docs_url": "https://airtable.com/developers/web/api/list-records",
        "query_keys": [
            "view", "pageSize", "maxRecords", "offset", "filterByFormula", "sort", "fields",
            "cellFormat", "timeZone", "userLocale", "returnFieldsByFieldId",
        ],
    },
    "airtable.records.list_post.v1": {
        "method": "POST",
        "path": "/{base_id}/{table_id_or_name}/listRecords",
        "required": ["base_id", "table_id_or_name"],
        "docs_url": "https://airtable.com/developers/web/api/list-records",
        "query_keys": [],
    },
    "airtable.records.get.v1": {
        "method": "GET",
        "path": "/{base_id}/{table_id_or_name}/{record_id}",
        "required": ["base_id", "table_id_or_name", "record_id"],
        "docs_url": "https://airtable.com/developers/web/api/get-record",
        "query_keys": ["cellFormat", "timeZone", "userLocale", "returnFieldsByFieldId"],
    },
    "airtable.records.create.v1": {
        "method": "POST",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name"],
        "docs_url": "https://airtable.com/developers/web/api/create-record",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.update.v1": {
        "method": "PATCH",
        "path": "/{base_id}/{table_id_or_name}/{record_id}",
        "required": ["base_id", "table_id_or_name", "record_id"],
        "docs_url": "https://airtable.com/developers/web/api/update-record",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.replace.v1": {
        "method": "PUT",
        "path": "/{base_id}/{table_id_or_name}/{record_id}",
        "required": ["base_id", "table_id_or_name", "record_id"],
        "docs_url": "https://airtable.com/developers/web/api/update-record",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.delete.v1": {
        "method": "DELETE",
        "path": "/{base_id}/{table_id_or_name}/{record_id}",
        "required": ["base_id", "table_id_or_name", "record_id"],
        "docs_url": "https://airtable.com/developers/web/api/delete-record",
        "query_keys": [],
    },
    "airtable.records.batch_create.v1": {
        "method": "POST",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name", "records"],
        "docs_url": "https://airtable.com/developers/web/api/create-records",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.batch_update.v1": {
        "method": "PATCH",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name", "records"],
        "docs_url": "https://airtable.com/developers/web/api/update-multiple-records",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.batch_replace.v1": {
        "method": "PUT",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name", "records"],
        "docs_url": "https://airtable.com/developers/web/api/update-multiple-records",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.records.batch_delete.v1": {
        "method": "DELETE",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name", "record_ids"],
        "docs_url": "https://airtable.com/developers/web/api/delete-multiple-records",
        "query_keys": [],
    },
    "airtable.records.batch_upsert.v1": {
        "method": "PATCH",
        "path": "/{base_id}/{table_id_or_name}",
        "required": ["base_id", "table_id_or_name", "records", "performUpsert"],
        "docs_url": "https://airtable.com/developers/web/api/update-multiple-records",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.comments.list.v1": {
        "method": "GET",
        "path": "/{base_id}/{table_id_or_name}/{record_id}/comments",
        "required": ["base_id", "table_id_or_name", "record_id"],
        "docs_url": "https://airtable.com/developers/web/api/list-comments",
        "query_keys": ["offset", "pageSize"],
    },
    "airtable.comments.create.v1": {
        "method": "POST",
        "path": "/{base_id}/{table_id_or_name}/{record_id}/comments",
        "required": ["base_id", "table_id_or_name", "record_id", "text"],
        "docs_url": "https://airtable.com/developers/web/api/create-comment",
        "query_keys": [],
    },
    "airtable.comments.update.v1": {
        "method": "PATCH",
        "path": "/{base_id}/{table_id_or_name}/{record_id}/comments/{comment_id}",
        "required": ["base_id", "table_id_or_name", "record_id", "comment_id", "text"],
        "docs_url": "https://airtable.com/developers/web/api/update-comment",
        "query_keys": [],
    },
    "airtable.comments.delete.v1": {
        "method": "DELETE",
        "path": "/{base_id}/{table_id_or_name}/{record_id}/comments/{comment_id}",
        "required": ["base_id", "table_id_or_name", "record_id", "comment_id"],
        "docs_url": "https://airtable.com/developers/web/api/delete-comment",
        "query_keys": [],
    },
    "airtable.attachments.attach_url.v1": {
        "method": "PATCH",
        "path": "/{base_id}/{table_id_or_name}/{record_id}",
        "required": ["base_id", "table_id_or_name", "record_id", "attachment_field_id_or_name"],
        "docs_url": "https://airtable.com/developers/web/api/field-model#multipleattachment",
        "query_keys": ["typecast", "returnFieldsByFieldId"],
    },
    "airtable.attachments.upload.v1": {
        "method": "POST",
        "path": "/{base_id}/{record_id}/{attachment_field_id_or_name}/uploadAttachment",
        "required": ["base_id", "record_id", "attachment_field_id_or_name", "filename", "contentType", "file"],
        "docs_url": "https://airtable.com/developers/web/api/upload-attachment",
        "query_keys": [],
        "host": "content",
    },
}

METHOD_IDS = list(METHOD_SPECS.keys())

WRITE_METHODS = {
    "airtable.bases.create.v1",
    "airtable.tables.create.v1",
    "airtable.tables.update.v1",
    "airtable.fields.create.v1",
    "airtable.fields.update.v1",
    "airtable.records.create.v1",
    "airtable.records.update.v1",
    "airtable.records.replace.v1",
    "airtable.records.delete.v1",
    "airtable.records.batch_create.v1",
    "airtable.records.batch_update.v1",
    "airtable.records.batch_replace.v1",
    "airtable.records.batch_delete.v1",
    "airtable.records.batch_upsert.v1",
    "airtable.comments.create.v1",
    "airtable.comments.update.v1",
    "airtable.comments.delete.v1",
    "airtable.attachments.attach_url.v1",
    "airtable.attachments.upload.v1",
}

DESTRUCTIVE_METHODS = {
    "airtable.records.delete.v1",
    "airtable.records.batch_delete.v1",
    "airtable.records.replace.v1",
    "airtable.records.batch_replace.v1",
    "airtable.comments.delete.v1",
}

AIRTABLE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="airtable",
    description='Interact with Airtable bases, tables, records, comments, and attachments. ops: help, status, list_methods, call. Example call: op="call", args={"method_id":"airtable.records.create.v1","base_id":"app...","table_id_or_name":"...","fields":{"Name":"value"}}',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation: help, status, list_methods, call"},
            "args": {"type": ["object", "null"], "description": "Arguments for the operation"},
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

class IntegrationAirtable:
    def __init__(self, rcx=None, api_key: str = ""):
        self.rcx = rcx
        self.api_key = (api_key or "").strip()

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is None:
            return {}
        return self.rcx.external_auth.get(PROVIDER_NAME) or self.rcx.external_auth.get(AUTH_PROVIDER_NAME) or {}

    def _get_token(self) -> str:
        auth = self._auth()
        token_obj = auth.get("token") if isinstance(auth.get("token"), dict) else {}
        return str(
            self.api_key
            or auth.get("api_key", "")
            or token_obj.get("access_token", "")
            or auth.get("access_token", "")
            or os.environ.get("AIRTABLE_API_KEY", "")
            or os.environ.get("AIRTABLE_TOKEN", "")
        ).strip()

    def _help(self) -> str:
        return (
            "provider=airtable\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus endpoint params/body fields\n"
            "for payload methods, pass body={...}; for query use query={...} or direct query keys\n"
            "Examples:\n"
            '  op="call", args={"method_id":"airtable.records.list.v1","base_id":"appXXX","table_id_or_name":"tblYYY"}\n'
            '  op="call", args={"method_id":"airtable.records.create.v1","base_id":"appXXX","table_id_or_name":"tblYYY","fields":{"Name":"Alice"}}\n'
            '  op="call", args={"method_id":"airtable.bases.schema.get.v1","base_id":"appXXX"}\n'
            "auth: use setup field airtable_api_key or external_auth['airtable']['api_key']\n"
            "readiness: do not use status as a full capability check; call the actual base/table/record method you need"
        )

    def _status(self) -> str:
        tok = self._get_token()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if tok else "missing_credentials",
            "has_api_key": bool(tok),
            "setup_required": not bool(tok),
            "ready_for_calls": bool(tok),
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
            # If the model omitted op but provided call arguments, default to call instead of help
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
        # Fallback: if args.args was empty but method_id was passed at the top level, use top-level keys
        if not call_args and "method_id" in args:
            call_args = {k: v for k, v in args.items() if k not in {"op", "args"}}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_SPECS:
            return self._error("METHOD_UNKNOWN", "Unknown method_id.", method_id=method_id)

        if method_id in DESTRUCTIVE_METHODS and not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="airtable_destructive",
                confirm_command=f"airtable {method_id}",
                confirm_explanation=f"This will permanently modify or delete data in Airtable: {method_id}",
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

        if method_id == "airtable.attachments.attach_url.v1":
            return await self._dispatch_attach_url(method_id, args)
        if method_id == "airtable.attachments.upload.v1":
            return await self._dispatch_upload(method_id, args)
        if method_id == "airtable.records.batch_delete.v1":
            return await self._dispatch_batch_delete(method_id, args)

        path = self._build_path(spec["path"], args)
        q = self._extract_query(args, spec)

        if method_id in {
            "airtable.records.batch_create.v1",
            "airtable.records.batch_update.v1",
            "airtable.records.batch_replace.v1",
            "airtable.records.batch_upsert.v1",
        }:
            err = self._validate_batch_records(method_id, b)
            if err:
                return err

        if method_id == "airtable.records.batch_upsert.v1":
            pu = (b or {}).get("performUpsert") if isinstance(b, dict) else None
            if not isinstance(pu, dict) or not isinstance(pu.get("fieldsToMergeOn"), list) or len(pu["fieldsToMergeOn"]) == 0:
                return self._error("INVALID_ARGS", "performUpsert.fieldsToMergeOn must be a non-empty array.", method_id=method_id)

        host = spec.get("host", "api")
        return await self._request_json(method_id, spec["method"], path, q, b, host=host)

    async def _dispatch_attach_url(self, method_id: str, args: Dict[str, Any]) -> str:
        path = self._build_path(METHOD_SPECS[method_id]["path"], args)
        q = self._extract_query(args, METHOD_SPECS[method_id])
        field = str(args.get("attachment_field_id_or_name", "")).strip()
        attachments = args.get("attachments")
        if attachments is None:
            one_url = str(args.get("url", "")).strip()
            if not one_url:
                return self._error("INVALID_ARGS", "Provide attachments array or url.", method_id=method_id)
            one = {"url": one_url}
            fn = str(args.get("filename", "")).strip()
            if fn:
                one["filename"] = fn
            attachments = [one]
        if not isinstance(attachments, list) or len(attachments) == 0:
            return self._error("INVALID_ARGS", "attachments must be a non-empty array.", method_id=method_id)
        body = {"fields": {field: attachments}}
        return await self._request_json(method_id, "PATCH", path, q, body, host="api")

    async def _dispatch_upload(self, method_id: str, args: Dict[str, Any]) -> str:
        path = self._build_path(METHOD_SPECS[method_id]["path"], args)
        body = {
            "filename": args.get("filename"),
            "contentType": args.get("contentType"),
            "file": args.get("file"),
        }
        return await self._request_json(method_id, "POST", path, {}, body, host="content")

    async def _dispatch_batch_delete(self, method_id: str, args: Dict[str, Any]) -> str:
        path = self._build_path(METHOD_SPECS[method_id]["path"], args)
        record_ids = args.get("record_ids")
        if not isinstance(record_ids, list) or len(record_ids) == 0:
            return self._error("INVALID_ARGS", "record_ids must be a non-empty array.", method_id=method_id)
        if len(record_ids) > 10:
            return self._error("INVALID_ARGS", "record_ids max length is 10.", method_id=method_id)
        query = {"records[]": [str(x) for x in record_ids]}
        return await self._request_json(method_id, "DELETE", path, query, None, host="api")

    def _extract_query(self, args: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(args.get("query") or {}) if isinstance(args.get("query"), dict) else {}
        for k in spec.get("query_keys", []):
            if k in args and args[k] is not None:
                q[k] = args[k]
        return q

    def _extract_body(self, method_id: str, args: Dict[str, Any]) -> Dict[str, Any] | None | str:
        if isinstance(args.get("body"), dict):
            return args["body"]

        if method_id == "airtable.bases.create.v1":
            return {"name": args.get("name")}
        if method_id == "airtable.tables.create.v1":
            body = {"name": args.get("name")}
            if isinstance(args.get("fields"), list):
                body["fields"] = args["fields"]
            if isinstance(args.get("description"), str):
                body["description"] = args["description"]
            return body
        if method_id == "airtable.tables.update.v1":
            body = {}
            for k in ("name", "description"):
                if k in args:
                    body[k] = args[k]
            return body if body else "Provide body or at least one updatable field (name/description)."
        if method_id == "airtable.fields.create.v1":
            body = {"name": args.get("name"), "type": args.get("type")}
            if isinstance(args.get("description"), str):
                body["description"] = args["description"]
            if isinstance(args.get("options"), dict):
                body["options"] = args["options"]
            return body
        if method_id == "airtable.fields.update.v1":
            body = {}
            for k in ("name", "description"):
                if k in args:
                    body[k] = args[k]
            if isinstance(args.get("options"), dict):
                body["options"] = args["options"]
            return body if body else "Provide body or at least one updatable field (name/description/options)."
        if method_id == "airtable.records.create.v1":
            if isinstance(args.get("fields"), dict):
                return {"fields": args["fields"]}
            return "Provide fields object or body for create record."
        if method_id in {"airtable.records.update.v1", "airtable.records.replace.v1"}:
            if isinstance(args.get("fields"), dict):
                return {"fields": args["fields"]}
            return "Provide fields object or body for record update/replace."
        if method_id in {
            "airtable.records.batch_create.v1",
            "airtable.records.batch_update.v1",
            "airtable.records.batch_replace.v1",
            "airtable.records.batch_upsert.v1",
        }:
            body = {}
            if isinstance(args.get("records"), list):
                body["records"] = args["records"]
            if isinstance(args.get("performUpsert"), dict):
                body["performUpsert"] = args["performUpsert"]
            return body if body else "Provide records list or body for batch operation."
        if method_id == "airtable.records.list_post.v1":
            payload = {}
            for k in (
                "view", "pageSize", "maxRecords", "offset", "filterByFormula", "sort", "fields",
                "cellFormat", "timeZone", "userLocale", "returnFieldsByFieldId",
            ):
                if k in args and args[k] is not None:
                    payload[k] = args[k]
            return payload
        if method_id in {"airtable.comments.create.v1", "airtable.comments.update.v1"}:
            return {"text": args.get("text")}

        return None

    def _validate_batch_records(self, method_id: str, body: Any) -> str | None:
        if not isinstance(body, dict):
            return self._error("INVALID_ARGS", "body must be an object.", method_id=method_id)
        records = body.get("records")
        if not isinstance(records, list) or len(records) == 0:
            return self._error("INVALID_ARGS", "records must be a non-empty array.", method_id=method_id)
        if len(records) > 10:
            return self._error("INVALID_ARGS", "records max length is 10.", method_id=method_id)
        return None

    def _build_path(self, path_tpl: str, args: Dict[str, Any]) -> str:
        path = path_tpl
        for key in (
            "base_id", "table_id_or_name", "table_id", "record_id", "field_id", "comment_id", "attachment_field_id_or_name",
        ):
            token = "{" + key + "}"
            if token in path:
                path = path.replace(token, str(args.get(key, "")).strip())
        return path

    async def _request_json(
        self,
        method_id: str,
        method: str,
        path: str,
        query: Dict[str, Any],
        body: Dict[str, Any] | None,
        *,
        host: str,
    ) -> str:
        tok = self._get_token()
        if not tok:
            return self._error("AUTH_MISSING", "Set airtable api_key in external auth or AIRTABLE_API_KEY env var.", method_id=method_id)

        headers = {
            "Authorization": f"Bearer {tok}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        base = AIRTABLE_CONTENT_BASE if host == "content" else AIRTABLE_BASE
        url = base + path

        try:
            async with httpx.AsyncClient(timeout=30.0) as cli:
                response = None
                for attempt in range(5):
                    response = await cli.request(
                        method,
                        url,
                        headers=headers,
                        params=query or None,
                        json=body if method in {"POST", "PATCH", "PUT"} else None,
                    )
                    if response.status_code != 429:
                        break
                    wait_s = min(2 ** attempt, 30)
                    logger.warning("airtable rate limited method=%s wait=%ss attempt=%s", method_id, wait_s, attempt + 1)
                    await asyncio.sleep(wait_s)
                assert response is not None
        except Exception as e:
            logger.exception("airtable request failed: %s", method_id)
            return self._error("REQUEST_FAILED", str(e), method_id=method_id)

        data: Any = {}
        if response.text:
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = response.text

        if response.status_code >= 400:
            error_code = "PROVIDER_ERROR"
            message = "Airtable request failed."
            if response.status_code == 401:
                error_code = "AUTH_REJECTED"
                message = "Airtable rejected the token. This usually means the PAT is invalid, expired, or missing required scopes/resources."
            elif response.status_code == 403:
                error_code = "INSUFFICIENT_PERMISSIONS"
                message = "Airtable accepted the token but denied this operation due to missing permissions or scopes."
            elif response.status_code == 404:
                error_code = "NOT_FOUND_OR_UNAVAILABLE"
                message = "The Airtable endpoint or requested resource is unavailable to this token. For base metadata, this is often missing data.bases scope or resource access."
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "status": response.status_code,
                "error_code": error_code,
                "message": message,
                "setup_required": False,
                "has_api_key": bool(tok),
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
                "records_count": len(data.get("records", [])) if isinstance(data.get("records"), list) else None,
                "has_offset": bool(data.get("offset")),
                "bases_count": len(data.get("bases", [])) if isinstance(data.get("bases"), list) else None,
                "tables_count": len(data.get("tables", [])) if isinstance(data.get("tables"), list) else None,
                "comments_count": len(data.get("comments", [])) if isinstance(data.get("comments"), list) else None,
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
