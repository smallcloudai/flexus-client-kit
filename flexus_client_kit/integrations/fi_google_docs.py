import asyncio
import json
import logging
from typing import Dict, Any, Optional

import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client

logger = logging.getLogger("google_docs")

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/documents"]


GOOGLE_DOCS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="google_docs",
    auth_required="google_docs",
    description="Access Google Docs to create, read, and edit documents. Call with op=\"help\" to see all available ops.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation name: help, status, or any docs op",
                "order": 0
            },
            "args": {
                "type": "object",
                "order": 1
            },
        },
        "required": ["op"]
    },
)


def _extract_plain_text(doc: dict) -> str:
    out = []
    for el in (doc.get("body") or {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            # XXX tables, sectionBreak, tableOfContents not extracted
            continue
        for run in para.get("elements", []):
            tr = run.get("textRun")
            if tr:
                out.append(tr.get("content", ""))
    return "".join(out)


class IntegrationGoogleDocs:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self._last_access_token = None
        self._service = None
        self.op_map = {
            "create":           (self._create,           "Create a new doc. args: {title}"),
            "get":              (self._get,              "Fetch full doc structure (raw JSON). args: {document_id}"),
            "get_text":         (self._get_text,         "Fetch doc body as plain text. args: {document_id}"),
            "append_text":      (self._append_text,      "Append text at end of doc. args: {document_id, text}"),
            "insert_text":      (self._insert_text,      "Insert text at given index. args: {document_id, text, index}"),
            "replace_all_text": (self._replace_all_text, "Find/replace all occurrences. args: {document_id, find, replace, match_case?}"),
            "delete_range":     (self._delete_range,     "Delete characters in range. args: {document_id, start_index, end_index}"),
            "batch_update":     (self._batch_update,     "Raw Docs API batchUpdate. args: {document_id, requests: [...]}"),
        }

    async def _ensure_service(self) -> bool:
        google_auth = self.rcx.external_auth.get("google_docs") or {}
        access_token = (google_auth.get("token") or {}).get("access_token", "")
        if not access_token:
            self._service = None
            self._last_access_token = None
            return False
        if access_token == self._last_access_token and self._service:
            return True
        creds = google.oauth2.credentials.Credentials(token=access_token)
        self._service = googleapiclient.discovery.build("docs", "v1", credentials=creds)
        self._last_access_token = access_token
        logger.info("Initialized Google Docs service")
        return True

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if not model_produced_args:
            return self._all_commands_help()

        op = model_produced_args.get("op", "")
        if not op:
            return self._all_commands_help()

        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        op_lower = op.lower()
        print_help = op_lower == "help" or op_lower == "status+help"
        print_status = op_lower == "status" or op_lower == "status+help"

        authenticated = await self._ensure_service()

        if print_status:
            status_msg = await self._status(authenticated)
            if print_help and authenticated:
                return status_msg + "\n\n" + self._all_commands_help()
            return status_msg

        if print_help:
            if authenticated:
                return self._all_commands_help()
            return await self._status(authenticated)

        if not authenticated:
            return await self._status(authenticated)

        entry = self.op_map.get(op)
        if not entry:
            return self._all_commands_help()
        op_fn, _desc = entry

        try:
            return await op_fn(args)
        except googleapiclient.errors.HttpError as e:
            if e.resp.status in (401, 403):
                self._last_access_token = None
                return "❌ Authentication error. Please reconnect Google Docs in Integrations tab.\n\nThen retry."
            logger.info("Docs API error %s: %s", op, e, exc_info=True)
            return f"❌ Google Docs API error: {e.resp.status} {e._get_reason()}"

    def _all_commands_help(self) -> str:
        lines = ["Google Docs - All Available Operations:\n"]
        for name, (_fn, desc) in self.op_map.items():
            lines.append(f"  {name}: {desc}")
        lines.append("")
        lines.append("Examples:")
        lines.append('  google_docs({"op": "create", "args": {"title": "My Doc"}})')
        lines.append('  google_docs({"op": "get_text", "args": {"document_id": "1aBcDeFg..."}})')
        lines.append('  google_docs({"op": "append_text", "args": {"document_id": "1aBcDeFg...", "text": "Hello\\n"}})')
        lines.append('  google_docs({"op": "replace_all_text", "args": {"document_id": "...", "find": "TODO", "replace": "DONE"}})')
        return "\n".join(lines)

    async def _status(self, authenticated: bool) -> str:
        r = "Google Docs integration status:\n"
        r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
        r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
        r += f"  Workspace: {self.rcx.persona.ws_id}\n"
        if authenticated:
            r += f"  Available ops: {', '.join(self.op_map.keys())}\n"
        else:
            r += "\n❌ Not authenticated. Please connect Google Docs in Integrations tab.\n"
        return r

    async def _create(self, args):
        title = args.get("title", "")
        doc = await asyncio.to_thread(
            lambda: self._service.documents().create(body={"title": title}).execute()
        )
        return f"Created document_id={doc['documentId']} title={doc.get('title','')}"

    async def _get(self, args):
        doc = await asyncio.to_thread(
            lambda: self._service.documents().get(documentId=args["document_id"]).execute()
        )
        return json.dumps(doc, indent=2)

    async def _get_text(self, args):
        doc = await asyncio.to_thread(
            lambda: self._service.documents().get(documentId=args["document_id"]).execute()
        )
        return _extract_plain_text(doc)

    async def _append_text(self, args):
        doc_id = args["document_id"]
        doc = await asyncio.to_thread(
            lambda: self._service.documents().get(
                documentId=doc_id,
                fields="body(content(endIndex))",
            ).execute()
        )
        # last segment endIndex points past final newline; insert before it
        end_index = doc["body"]["content"][-1]["endIndex"] - 1
        return await self._do_batch_update(doc_id, [
            {"insertText": {"location": {"index": end_index}, "text": args["text"]}},
        ])

    async def _insert_text(self, args):
        return await self._do_batch_update(args["document_id"], [
            {"insertText": {"location": {"index": args["index"]}, "text": args["text"]}},
        ])

    async def _replace_all_text(self, args):
        return await self._do_batch_update(args["document_id"], [{
            "replaceAllText": {
                "containsText": {"text": args["find"], "matchCase": bool(args.get("match_case", False))},
                "replaceText": args["replace"],
            },
        }])

    async def _delete_range(self, args):
        return await self._do_batch_update(args["document_id"], [{
            "deleteContentRange": {
                "range": {"startIndex": args["start_index"], "endIndex": args["end_index"]},
            },
        }])

    async def _batch_update(self, args):
        return await self._do_batch_update(args["document_id"], args["requests"])

    async def _do_batch_update(self, document_id: str, requests: list) -> str:
        resp = await asyncio.to_thread(
            lambda: self._service.documents().batchUpdate(
                documentId=document_id,
                body={"requests": requests},
            ).execute()
        )
        replies = resp.get("replies", [])
        return json.dumps(replies, indent=2) if replies else "OK"
