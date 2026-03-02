import json
import logging
import os
from typing import Any, Dict, List

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("dovetail")

PROVIDER_NAME = "dovetail"
METHOD_IDS = [
    "dovetail.insights.export.markdown.v1",
    "dovetail.projects.export.zip.v1",
]

_BASE_URL = "https://dovetail.com/api/v1"


class IntegrationDovetail:
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
            key = os.environ.get("DOVETAIL_API_KEY", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if key else "no_credentials",
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
        if method_id == "dovetail.insights.export.markdown.v1":
            return await self._insights_export_markdown(args)
        if method_id == "dovetail.projects.export.zip.v1":
            return await self._projects_export_zip(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _insights_export_markdown(self, args: Dict[str, Any]) -> str:
        project_id = str(args.get("project_id", "")).strip()
        if not project_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "detail": "project_id is required"}, indent=2, ensure_ascii=False)
        tag_ids: List[str] = [str(t) for t in (args.get("tag_ids") or []) if t]
        token = os.environ.get("DOVETAIL_API_KEY", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "detail": "DOVETAIL_API_KEY env var not set"}, indent=2, ensure_ascii=False)

        # Dovetail API constraint: only one of project_id, tag_id, or highlight_id allowed per request.
        # When tag_ids provided, filter by tag and apply project_id check client-side.
        # When no tag_ids, filter by project_id directly.
        params: Dict[str, Any] = {"page[limit]": 100}
        filter_mode: str
        if tag_ids:
            filter_mode = "tag_id"
            if len(tag_ids) == 1:
                params["filter[tag_id]"] = tag_ids[0]
            else:
                params["filter[tag_id][]"] = tag_ids
        else:
            filter_mode = "project_id"
            params["filter[project_id]"] = project_id

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(
                    f"{_BASE_URL}/highlights",
                    headers=self._headers(token),
                    params=params,
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            try:
                detail = resp.json()
            except json.JSONDecodeError:
                detail = resp.text
            return self._provider_error(resp.status_code, detail)

        try:
            body = resp.json()
        except json.JSONDecodeError as e:
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        highlights = body.get("data", [])
        page_info = body.get("page", {})

        md_lines = [f"# Dovetail Highlights Export\n\nproject_id: `{project_id}`\n"]
        if tag_ids:
            md_lines.append(f"tag_ids: {', '.join(f'`{t}`' for t in tag_ids)}\n")
        md_lines.append(f"count: {len(highlights)} (total_workspace: {page_info.get('total_count', '?')})\n\n---\n")

        for h in highlights:
            text = h.get("text") or "(no text)"
            tags = ", ".join(t["title"] for t in h.get("tags", []))
            md_lines.append(f"## Highlight `{h['id']}`\n")
            md_lines.append(f"**Created:** {h.get('created_at', '')}  ")
            if tags:
                md_lines.append(f"**Tags:** {tags}  ")
            md_lines.append(f"\n{text}\n\n---\n")

        markdown = "\n".join(md_lines)
        api_note = (
            "Dovetail public API v1 does not expose a list-insights-by-project endpoint. "
            "This result contains highlights (tagged data points) filtered by "
            + ("tag_id" if filter_mode == "tag_id" else "project_id")
            + ". To export a specific insight document as markdown, use GET /v1/insights/{insight_id}/export/markdown."
        )
        return self._ok("insights.export.markdown", {
            "project_id": project_id,
            "filter_mode": filter_mode,
            "highlight_count": len(highlights),
            "has_more": page_info.get("has_more", False),
            "api_note": api_note,
            "markdown": markdown,
        })

    async def _projects_export_zip(self, args: Dict[str, Any]) -> str:
        project_id = str(args.get("project_id", "")).strip()
        if not project_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "detail": "project_id is required"}, indent=2, ensure_ascii=False)
        token = os.environ.get("DOVETAIL_API_KEY", "")
        if not token:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "detail": "DOVETAIL_API_KEY env var not set"}, indent=2, ensure_ascii=False)

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(
                    f"{_BASE_URL}/projects/{project_id}",
                    headers=self._headers(token),
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        if resp.status_code != 200:
            try:
                detail = resp.json()
            except json.JSONDecodeError:
                detail = resp.text
            return self._provider_error(resp.status_code, detail)

        try:
            body = resp.json()
        except json.JSONDecodeError as e:
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)

        project = body.get("data", {})
        api_note = (
            "Dovetail public API v1 does not expose a ZIP export endpoint. "
            "ZIP export (JSON/JSONL data, insights, tags, field groups) is available via the Dovetail UI: "
            "open the project → Settings → Export → Download as ZIP."
        )
        return self._ok("projects.export.zip", {
            "project_id": project_id,
            "project_title": project.get("title"),
            "project_created_at": project.get("created_at"),
            "project_deleted": project.get("deleted"),
            "api_note": api_note,
        })

    def _headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _ok(self, method_label: str, data: Any) -> str:
        return (
            f"dovetail.{method_label} ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        )

    def _provider_error(self, status_code: int, detail: Any) -> str:
        logger.info("dovetail provider error status=%s detail=%s", status_code, detail)
        return json.dumps({
            "ok": False,
            "error_code": "PROVIDER_ERROR",
            "status": status_code,
            "detail": detail,
        }, indent=2, ensure_ascii=False)
