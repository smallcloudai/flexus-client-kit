import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("producthunt")

PROVIDER_NAME = "producthunt"
METHOD_IDS = [
    "producthunt.graphql.posts.v1",
    "producthunt.graphql.topics.v1",
]

_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"

_POSTS_QUERY = """
query Posts($first: Int, $after: String, $topic: String, $postedAfter: DateTime) {
  posts(first: $first, after: $after, topic: $topic, postedAfter: $postedAfter, featured: true, order: VOTES) {
    edges {
      node {
        id
        name
        tagline
        description
        votesCount
        commentsCount
        website
        url
        thumbnail { url }
        topics { edges { node { name } } }
        createdAt
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

_TOPICS_QUERY = """
query Topics($first: Int) {
  topics(first: $first) {
    edges {
      node {
        id
        name
        slug
        description
        followersCount
        postsCount
      }
    }
  }
}
"""


class IntegrationProducthunt:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("producthunt") or {}).get("api_key", "")
        return self._get_api_key()

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
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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
        api_key = self._get_api_key()
        if not api_key:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set PRODUCTHUNT_API_KEY env var (Developer Token from https://www.producthunt.com/v2/oauth/applications)."}, indent=2, ensure_ascii=False)

        if method_id == "producthunt.graphql.posts.v1":
            return await self._posts(api_key, args)
        if method_id == "producthunt.graphql.topics.v1":
            return await self._topics(api_key, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _graphql(self, api_key: str, query: str, variables: Dict) -> Dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                _GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        if r.status_code >= 400:
            logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
            return {"error": True, "status": r.status_code, "detail": r.text[:300]}
        return r.json()

    async def _posts(self, api_key: str, args: Dict) -> str:
        limit = int(args.get("limit", 20))
        cursor = args.get("cursor") or None
        query_slug = args.get("query") or None
        posted_after = args.get("posted_after") or None

        variables: Dict[str, Any] = {"first": limit}
        if cursor:
            variables["after"] = cursor
        if query_slug:
            variables["topic"] = query_slug
        if posted_after:
            variables["postedAfter"] = posted_after

        try:
            data = await self._graphql(api_key, _POSTS_QUERY, variables)
        except (httpx.TimeoutException,):
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if data.get("error"):
            return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": data.get("status"), "detail": data.get("detail")}, indent=2, ensure_ascii=False)

        errors = data.get("errors")
        if errors:
            return json.dumps({"ok": False, "error_code": "GRAPHQL_ERROR", "errors": errors}, indent=2, ensure_ascii=False)

        posts_data = data.get("data", {}).get("posts", {})
        edges = posts_data.get("edges", [])
        results = [e.get("node", e) for e in edges]
        page_info = posts_data.get("pageInfo", {})

        summary = f"Found {len(results)} post(s) from {PROVIDER_NAME}."
        payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results), "page_info": page_info}
        if args.get("include_raw"):
            payload["raw"] = data
        return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"

    async def _topics(self, api_key: str, args: Dict) -> str:
        limit = int(args.get("limit", 20))
        variables: Dict[str, Any] = {"first": limit}

        try:
            data = await self._graphql(api_key, _TOPICS_QUERY, variables)
        except (httpx.TimeoutException,):
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

        if data.get("error"):
            return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": data.get("status"), "detail": data.get("detail")}, indent=2, ensure_ascii=False)

        errors = data.get("errors")
        if errors:
            return json.dumps({"ok": False, "error_code": "GRAPHQL_ERROR", "errors": errors}, indent=2, ensure_ascii=False)

        topics_data = data.get("data", {}).get("topics", {})
        edges = topics_data.get("edges", [])
        results = [e.get("node", e) for e in edges]

        summary = f"Found {len(results)} topic(s) from {PROVIDER_NAME}."
        payload: Dict[str, Any] = {"ok": True, "results": results, "total": len(results)}
        if args.get("include_raw"):
            payload["raw"] = data
        return summary + "\n\n```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```"
