import json
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger("jira")

PROVIDER_NAME = "jira"
METHOD_IDS = [
    "jira.issues.create.v1",
    "jira.issues.search.v1",
    "jira.issues.transition.v1",
]

_BASE_URL_SUFFIX = "/rest/api/3"


class IntegrationJira:
    async def called_by_model(self, toolcall, model_produced_args):
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (f"provider={PROVIDER_NAME}\nop=help | status | list_methods | call\nmethods: {', '.join(METHOD_IDS)}")
        if op == "status":
            base_url = os.environ.get("JIRA_BASE_URL", "")
            email = os.environ.get("JIRA_EMAIL", "")
            token = os.environ.get("JIRA_API_TOKEN", "")
            has_creds = bool(base_url and email and token)
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available" if has_creds else "no_credentials", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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

    def _client(self):
        base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        email = os.environ.get("JIRA_EMAIL", "")
        api_token = os.environ.get("JIRA_API_TOKEN", "")
        return httpx.AsyncClient(
            base_url=base_url + _BASE_URL_SUFFIX,
            auth=(email, api_token),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )

    async def _dispatch(self, method_id, call_args):
        if method_id == "jira.issues.create.v1":
            return await self._issues_create(call_args)
        if method_id == "jira.issues.search.v1":
            return await self._issues_search(call_args)
        if method_id == "jira.issues.transition.v1":
            return await self._issues_transition(call_args)

    async def _issues_create(self, call_args):
        project_key = str(call_args.get("project_key", "")).strip()
        if not project_key:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "project_key"}, indent=2, ensure_ascii=False)
        summary = str(call_args.get("summary", "")).strip()
        if not summary:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "summary"}, indent=2, ensure_ascii=False)

        issue_type = str(call_args.get("issue_type", "Task")).strip() or "Task"
        description = call_args.get("description", "")
        priority = call_args.get("priority", "")
        labels = call_args.get("labels") or []
        assignee_account_id = call_args.get("assignee_account_id", "")

        fields: Dict[str, Any] = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}],
            }
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = labels
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}

        async with self._client() as client:
            resp = await client.post("/issue", content=json.dumps({"fields": fields}).encode())

        if resp.status_code not in (200, 201):
            logger.info("jira issues create failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        key = data.get("key", "")
        return json.dumps({"ok": True, "id": data.get("id"), "key": key, "url": f"{base_url}/browse/{key}"}, indent=2, ensure_ascii=False)

    async def _issues_search(self, call_args):
        jql = str(call_args.get("jql", "")).strip()
        if not jql:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "jql"}, indent=2, ensure_ascii=False)

        max_results = int(call_args.get("max_results", 20))
        fields = call_args.get("fields") or ["summary", "status", "assignee", "priority", "created"]

        body = {"jql": jql, "maxResults": max_results, "fields": fields}

        async with self._client() as client:
            resp = await client.post("/search", content=json.dumps(body).encode())

        if resp.status_code != 200:
            logger.info("jira issues search failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

        data = resp.json()
        issues = []
        for issue in data.get("issues", []):
            f = issue.get("fields", {})
            assignee_field = f.get("assignee") or {}
            issues.append({
                "id": issue.get("id"),
                "key": issue.get("key"),
                "summary": f.get("summary"),
                "status": (f.get("status") or {}).get("name"),
                "assignee": assignee_field.get("displayName"),
                "priority": (f.get("priority") or {}).get("name"),
                "created": f.get("created"),
            })
        return json.dumps({"ok": True, "total": data.get("total", len(issues)), "issues": issues}, indent=2, ensure_ascii=False)

    async def _issues_transition(self, call_args):
        issue_key = str(call_args.get("issue_key", "")).strip()
        if not issue_key:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "issue_key"}, indent=2, ensure_ascii=False)

        transition_id = str(call_args.get("transition_id", "")).strip()
        transition_name = str(call_args.get("transition_name", "")).strip()

        if not transition_id and not transition_name:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "arg": "transition_id or transition_name required"}, indent=2, ensure_ascii=False)

        try:
            async with self._client() as client:
                if transition_id:
                    resp = await client.post(
                        f"/issue/{issue_key}/transitions",
                        content=json.dumps({"transition": {"id": transition_id}}).encode(),
                    )
                else:
                    get_resp = await client.get(f"/issue/{issue_key}/transitions")
                    if get_resp.status_code != 200:
                        logger.info("jira transitions list failed: status=%d body=%s", get_resp.status_code, get_resp.text[:500])
                        return json.dumps({"ok": False, "error_code": "API_ERROR", "status": get_resp.status_code, "detail": get_resp.text[:500]}, indent=2, ensure_ascii=False)
                    data = get_resp.json()
                    transitions = data.get("transitions", [])
                    found = None
                    for t in transitions:
                        if (t.get("name") or "").strip().lower() == transition_name.lower():
                            found = t
                            break
                    if not found:
                        available = [{"id": t.get("id"), "name": t.get("name")} for t in transitions]
                        return json.dumps({"ok": False, "error_code": "TRANSITION_NOT_FOUND", "transition_name": transition_name, "available_transitions": available}, indent=2, ensure_ascii=False)
                    tid = found.get("id")
                    tname = found.get("name")
                    resp = await client.post(
                        f"/issue/{issue_key}/transitions",
                        content=json.dumps({"transition": {"id": tid}}).encode(),
                    )
                    transition_id = tid
                    transition_name = tname

            if resp.status_code != 204:
                logger.info("jira transition failed: status=%d body=%s", resp.status_code, resp.text[:500])
                return json.dumps({"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]}, indent=2, ensure_ascii=False)

            return json.dumps({"ok": True, "issue_key": issue_key, "transition": {"id": transition_id, "name": transition_name}}, indent=2, ensure_ascii=False)
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            logger.info("jira transition http error: %s", e)
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        except (KeyError, ValueError) as e:
            logger.info("jira transition parse error: %s", e)
            return json.dumps({"ok": False, "error_code": "PARSE_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
