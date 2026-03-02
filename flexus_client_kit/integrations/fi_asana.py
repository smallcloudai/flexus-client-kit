import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("asana")
PROVIDER_NAME = "asana"
METHOD_IDS = [
    "asana.tasks.create.v1",
    "asana.tasks.update.v1",
]
_BASE_URL = "https://app.asana.com/api/1.0"


def _check_credentials() -> Optional[str]:
    token = os.environ.get("ASANA_ACCESS_TOKEN", "").strip()
    workspace = os.environ.get("ASANA_WORKSPACE_GID", "").strip()
    if not token or not workspace:
        return "NO_CREDENTIALS"
    return None


def _normalize_task(data: Dict[str, Any]) -> Dict[str, Any]:
    assignee = data.get("assignee")
    assignee_gid = assignee.get("gid") if isinstance(assignee, dict) else None
    return {
        "gid": data.get("gid"),
        "name": data.get("name"),
        "notes": data.get("notes"),
        "assignee_gid": assignee_gid,
        "due_on": data.get("due_on"),
        "completed": data.get("completed"),
        "created_at": data.get("created_at"),
        "modified_at": data.get("modified_at"),
        "permalink_url": data.get("permalink_url"),
    }


class IntegrationAsana:
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
            cred_err = _check_credentials()
            status = "available" if cred_err is None else cred_err
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
        cred_err = _check_credentials()
        if cred_err:
            return json.dumps(
                {"ok": False, "error_code": cred_err, "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "asana.tasks.create.v1":
            return await self._tasks_create(call_args)
        if method_id == "asana.tasks.update.v1":
            return await self._tasks_update(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _resolve_assignee(
        self,
        assignee: str,
        workspace_gid: str,
        headers: Dict[str, str],
    ) -> Optional[str]:
        assignee = str(assignee).strip()
        if not assignee:
            return None
        if assignee.lower() == "me":
            return "me"
        if "@" in assignee:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.get(
                        f"{_BASE_URL}/users",
                        params={"workspace": workspace_gid, "opt_fields": "email,gid"},
                        headers=headers,
                    )
                    r.raise_for_status()
                    users = (r.json()).get("data", [])
                    for u in users:
                        if (u.get("email") or "").lower() == assignee.lower():
                            return u.get("gid")
            except (httpx.TimeoutException, httpx.HTTPError, KeyError, ValueError) as e:
                logger.info("Asana user lookup by email failed: %s", e)
            return None
        return assignee

    async def _tasks_create(self, call_args: Dict[str, Any]) -> str:
        name = str(call_args.get("name", "")).strip()
        if not name:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "name is required"},
                indent=2,
                ensure_ascii=False,
            )
        workspace = str(call_args.get("workspace", "")).strip() or os.environ.get("ASANA_WORKSPACE_GID", "").strip()
        if not workspace:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "workspace is required"},
                indent=2,
                ensure_ascii=False,
            )
        token = os.environ.get("ASANA_ACCESS_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data: Dict[str, Any] = {"name": name, "workspace": workspace}
        notes = str(call_args.get("notes", "")).strip()
        if notes:
            data["notes"] = notes
        projects = call_args.get("projects")
        if isinstance(projects, list):
            data["projects"] = [str(p) for p in projects if str(p).strip()]
        elif isinstance(projects, str) and projects.strip():
            data["projects"] = [projects.strip()]
        due_on = str(call_args.get("due_on", "")).strip()
        if due_on:
            data["due_on"] = due_on
        assignee_raw = call_args.get("assignee")
        if assignee_raw is not None:
            assignee = await self._resolve_assignee(str(assignee_raw), workspace, headers)
            if assignee:
                data["assignee"] = assignee
        body = {"data": data}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{_BASE_URL}/tasks",
                    json=body,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Asana tasks create timeout: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "method_id": "asana.tasks.create.v1"},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Asana tasks create HTTP error status=%s: %s", e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "status_code": e.response.status_code,
                    "method_id": "asana.tasks.create.v1",
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Asana tasks create HTTP error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "method_id": "asana.tasks.create.v1"},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
            task_data = payload["data"]
        except (KeyError, json.JSONDecodeError) as e:
            logger.info("Asana tasks create response parse error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "method_id": "asana.tasks.create.v1"},
                indent=2,
                ensure_ascii=False,
            )
        normalized = _normalize_task(task_data)
        return json.dumps(
            {"ok": True, "task": normalized},
            indent=2,
            ensure_ascii=False,
        )

    async def _tasks_update(self, call_args: Dict[str, Any]) -> str:
        task_gid = str(call_args.get("task_gid", "")).strip()
        if not task_gid:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "task_gid is required"},
                indent=2,
                ensure_ascii=False,
            )
        token = os.environ.get("ASANA_ACCESS_TOKEN", "")
        workspace = os.environ.get("ASANA_WORKSPACE_GID", "")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data: Dict[str, Any] = {}
        if "name" in call_args:
            data["name"] = str(call_args["name"])
        if "notes" in call_args:
            data["notes"] = str(call_args["notes"])
        if "completed" in call_args:
            data["completed"] = bool(call_args["completed"])
        if "due_on" in call_args:
            val = call_args["due_on"]
            data["due_on"] = str(val) if val is not None else None
        if "assignee" in call_args:
            assignee_raw = call_args["assignee"]
            if assignee_raw is None or (isinstance(assignee_raw, str) and not assignee_raw.strip()):
                data["assignee"] = None
            else:
                assignee = await self._resolve_assignee(str(assignee_raw), workspace, headers)
                if assignee is not None:
                    data["assignee"] = assignee
        if not data:
            return json.dumps(
                {"ok": False, "error_code": "INVALID_ARGS", "message": "at least one of name, notes, completed, assignee, due_on required"},
                indent=2,
                ensure_ascii=False,
            )
        body = {"data": data}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(
                    f"{_BASE_URL}/tasks/{task_gid}",
                    json=body,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.info("Asana tasks update timeout task_gid=%s: %s", task_gid, e)
            return json.dumps(
                {"ok": False, "error_code": "TIMEOUT", "task_gid": task_gid, "method_id": "asana.tasks.update.v1"},
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPStatusError as e:
            logger.info("Asana tasks update HTTP error task_gid=%s status=%s: %s", task_gid, e.response.status_code, e)
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "HTTP_ERROR",
                    "task_gid": task_gid,
                    "status_code": e.response.status_code,
                    "method_id": "asana.tasks.update.v1",
                },
                indent=2,
                ensure_ascii=False,
            )
        except httpx.HTTPError as e:
            logger.info("Asana tasks update HTTP error task_gid=%s: %s", task_gid, e)
            return json.dumps(
                {"ok": False, "error_code": "HTTP_ERROR", "task_gid": task_gid, "method_id": "asana.tasks.update.v1"},
                indent=2,
                ensure_ascii=False,
            )
        try:
            payload = response.json()
            task_data = payload["data"]
        except (KeyError, json.JSONDecodeError) as e:
            logger.info("Asana tasks update response parse error task_gid=%s: %s", task_gid, e)
            return json.dumps(
                {"ok": False, "error_code": "UNEXPECTED_RESPONSE", "task_gid": task_gid, "method_id": "asana.tasks.update.v1"},
                indent=2,
                ensure_ascii=False,
            )
        normalized = _normalize_task(task_data)
        return json.dumps(
            {"ok": True, "task": normalized},
            indent=2,
            ensure_ascii=False,
        )
