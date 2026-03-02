import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("linear")

PROVIDER_NAME = "linear"
METHOD_IDS = [
    "linear.issues.create.v1",
    "linear.issues.list.v1",
]

_GRAPHQL_URL = "https://api.linear.app/graphql"


class IntegrationLinear:
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
            key = os.environ.get("LINEAR_API_KEY", "")
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "available" if key else "no_credentials",
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
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return await self._dispatch(method_id, call_args)

    def _headers(self) -> Dict[str, str]:
        key = os.environ.get("LINEAR_API_KEY", "")
        return {"Authorization": key, "Content-Type": "application/json"}

    async def _gql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> httpx.Response:
        key = os.environ.get("LINEAR_API_KEY", "")
        if not key:
            raise ValueError("LINEAR_API_KEY not set")
        body: Dict[str, Any] = {"query": query}
        if variables:
            body["variables"] = variables
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                return await client.post(_GRAPHQL_URL, headers=self._headers(), json=body)
        except httpx.TimeoutException as e:
            logger.info("linear gql timeout: %s", e)
            raise
        except httpx.HTTPError as e:
            logger.info("linear gql http error: %s", e)
            raise

    async def _get_first_team_id(self) -> Optional[str]:
        resp = await self._gql("query { teams { nodes { id name } } }")
        if resp.status_code != 200:
            return None
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            logger.info("linear teams json decode error: %s", e)
            return None
        nodes = (data.get("data") or {}).get("teams", {}).get("nodes", [])
        return nodes[0]["id"] if nodes else None

    async def _dispatch(self, method_id: str, call_args: Dict[str, Any]) -> str:
        if method_id == "linear.issues.create.v1":
            return await self._issues_create(call_args)
        if method_id == "linear.issues.list.v1":
            return await self._issues_list(call_args)
        return json.dumps(
            {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
            indent=2,
            ensure_ascii=False,
        )

    async def _issues_create(self, call_args: Dict[str, Any]) -> str:
        key = os.environ.get("LINEAR_API_KEY", "")
        if not key:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        title = str(call_args.get("title", "")).strip()
        if not title:
            return json.dumps(
                {"ok": False, "error_code": "MISSING_ARG", "arg": "title"},
                indent=2,
                ensure_ascii=False,
            )
        team_id = str(call_args.get("team_id", "")).strip()
        if not team_id:
            try:
                team_id = await self._get_first_team_id() or ""
            except (httpx.TimeoutException, httpx.HTTPError):
                return json.dumps(
                    {"ok": False, "error_code": "API_ERROR", "message": "Failed to fetch teams"},
                    indent=2,
                    ensure_ascii=False,
                )
        if not team_id:
            return json.dumps(
                {"ok": False, "error_code": "NO_TEAM", "message": "No team_id provided and no teams found"},
                indent=2,
                ensure_ascii=False,
            )
        description = call_args.get("description", "")
        priority = call_args.get("priority")
        label_ids = call_args.get("label_ids") or []

        input_fields: Dict[str, Any] = {"title": title, "teamId": team_id}
        if description:
            input_fields["description"] = description
        if priority is not None:
            input_fields["priority"] = int(priority)
        if label_ids:
            input_fields["labelIds"] = label_ids

        mutation = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
    }
  }
}
"""
        try:
            resp = await self._gql(mutation, {"input": input_fields})
        except (httpx.TimeoutException, httpx.HTTPError):
            return json.dumps(
                {"ok": False, "error_code": "API_ERROR", "message": "Request failed"},
                indent=2,
                ensure_ascii=False,
            )
        if resp.status_code != 200:
            logger.info("linear issues create failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps(
                {"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            logger.info("linear issues create json decode error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "detail": resp.text[:500]},
                indent=2,
                ensure_ascii=False,
            )
        errors = data.get("errors")
        if errors:
            logger.info("linear issues create graphql errors: %s", errors)
            return json.dumps(
                {"ok": False, "error_code": "GRAPHQL_ERROR", "errors": errors},
                indent=2,
                ensure_ascii=False,
            )
        result = (data.get("data") or {}).get("issueCreate", {})
        if not result.get("success"):
            return json.dumps(
                {"ok": False, "error_code": "CREATE_FAILED", "result": result},
                indent=2,
                ensure_ascii=False,
            )
        issue = result.get("issue") or {}
        return json.dumps(
            {
                "ok": True,
                "id": issue.get("id"),
                "identifier": issue.get("identifier"),
                "title": issue.get("title"),
                "url": issue.get("url"),
            },
            indent=2,
            ensure_ascii=False,
        )

    async def _issues_list(self, call_args: Dict[str, Any]) -> str:
        key = os.environ.get("LINEAR_API_KEY", "")
        if not key:
            return json.dumps(
                {"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME},
                indent=2,
                ensure_ascii=False,
            )
        team_id = str(call_args.get("team_id", "")).strip()
        state_name = str(call_args.get("state_name", "")).strip()
        limit = int(call_args.get("limit", 20))

        filter_parts = []
        if team_id:
            filter_parts.append("team: {id: {eq: $teamId}}")
        if state_name:
            filter_parts.append("state: {name: {eq: $stateName}}")
        filter_str = ", ".join(filter_parts)
        filter_arg = f", filter: {{{filter_str}}}" if filter_parts else ""

        var_decls = "$first: Int"
        if team_id:
            var_decls += ", $teamId: ID"
        if state_name:
            var_decls += ", $stateName: String"

        query = f"""
query IssuesList({var_decls}) {{
  issues(first: $first{filter_arg}) {{
    nodes {{
      id
      identifier
      title
      state {{ name }}
      assignee {{ name }}
      priority
      createdAt
    }}
  }}
}}
"""
        variables: Dict[str, Any] = {"first": limit}
        if team_id:
            variables["teamId"] = team_id
        if state_name:
            variables["stateName"] = state_name

        try:
            resp = await self._gql(query, variables)
        except (httpx.TimeoutException, httpx.HTTPError):
            return json.dumps(
                {"ok": False, "error_code": "API_ERROR", "message": "Request failed"},
                indent=2,
                ensure_ascii=False,
            )
        if resp.status_code != 200:
            logger.info("linear issues list failed: status=%d body=%s", resp.status_code, resp.text[:500])
            return json.dumps(
                {"ok": False, "error_code": "API_ERROR", "status": resp.status_code, "detail": resp.text[:500]},
                indent=2,
                ensure_ascii=False,
            )
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            logger.info("linear issues list json decode error: %s", e)
            return json.dumps(
                {"ok": False, "error_code": "INVALID_JSON", "detail": resp.text[:500]},
                indent=2,
                ensure_ascii=False,
            )
        errors = data.get("errors")
        if errors:
            logger.info("linear issues list graphql errors: %s", errors)
            return json.dumps(
                {"ok": False, "error_code": "GRAPHQL_ERROR", "errors": errors},
                indent=2,
                ensure_ascii=False,
            )
        nodes = (data.get("data") or {}).get("issues", {}).get("nodes", [])
        issues = []
        for node in nodes:
            issues.append({
                "id": node.get("id"),
                "identifier": node.get("identifier"),
                "title": node.get("title"),
                "state": (node.get("state") or {}).get("name"),
                "assignee": (node.get("assignee") or {}).get("name"),
                "priority": node.get("priority"),
                "created_at": node.get("createdAt"),
            })
        return json.dumps({"ok": True, "issues": issues}, indent=2, ensure_ascii=False)
