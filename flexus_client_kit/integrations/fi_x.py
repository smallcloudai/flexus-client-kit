import json
import logging
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("x")

PROVIDER_NAME = "x"
METHOD_IDS = [
    "x.users.me.v1",
    "x.users.by_username.v1",
    "x.users.by_id.v1",
    "x.tweets.create.v1",
    "x.tweets.delete.v1",
    "x.tweets.get.v1",
    "x.tweets.search_recent.v1",
    "x.timelines.user.v1",
    "x.timelines.reverse_chronological.v1",
    "x.likes.create.v1",
    "x.likes.delete.v1",
    "x.retweets.create.v1",
    "x.retweets.delete.v1",
    "x.bookmarks.create.v1",
    "x.bookmarks.delete.v1",
    "x.follows.create.v1",
    "x.follows.delete.v1",
]

REQUIRED_SCOPES = [
    "tweet.read",
    "tweet.write",
    "users.read",
    "offline.access",
    "like.read",
    "like.write",
    "follows.read",
    "follows.write",
    "bookmark.read",
    "bookmark.write",
]

_BASE_URL = "https://api.twitter.com/2"
_TIMEOUT = 30.0

X_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="x",
    auth_required="x",
    description="X (Twitter) API v2: post tweets, search, user lookup, follow, like, retweet, bookmark.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Use help, status, list_methods, or call."},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

X_SETUP_SCHEMA = []


class IntegrationX:
    def __init__(self, fclient=None, rcx=None):
        self.fclient = fclient
        self.rcx = rcx

    def _auth(self) -> Dict[str, Any]:
        return (self.rcx.external_auth.get("x") or {}) if self.rcx else {}

    def _access_token(self) -> str:
        auth = self._auth()
        token_obj = auth.get("token") or {}
        return str(token_obj.get("access_token", "") or auth.get("oauth_token", "")).strip()

    def _status(self) -> str:
        access_token = self._access_token()
        return json.dumps({
            "ok": bool(access_token),
            "provider": PROVIDER_NAME,
            "status": "ready" if access_token else "missing_credentials",
            "method_count": len(METHOD_IDS),
            "auth_provider": "x",
            "products": [
                "Post and read Tweets",
                "Search recent Tweets",
                "Manage likes, retweets, bookmarks, follows",
            ],
            "scopes_expected": ["tweet.read", "tweet.write", "users.read", "offline.access"],
            "has_access_token": bool(access_token),
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- All write methods require tweet.write/like.write/etc scopes plus offline.access for long-lived auth.\n"
            "- tweets.create body fields: text (required), reply_to_id, quote_tweet_id, poll_options, poll_minutes, media_ids.\n"
            "- search_recent uses Twitter v2 query language; pass `query` and optional `max_results` (10-100), `next_token`.\n"
            "- timelines.user requires `user_id` (numeric) — use users.by_username first if you only have a handle.\n"
            "- follows/likes/retweets/bookmarks require source_user_id (the authenticated user's id from users.me).\n"
        )

    def _headers(self, *, has_body: bool) -> Dict[str, str]:
        access_token = self._access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        if has_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _auth_missing(self, method_id: str) -> str:
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "AUTH_MISSING",
            "message": "Connect X in workspace settings and ensure an access token is present.",
        }, indent=2, ensure_ascii=False)

    def _invalid_args(self, method_id: str, message: str) -> str:
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "INVALID_ARGS",
            "message": message,
        }, indent=2, ensure_ascii=False)

    def _result(self, method_id: str, result: Any) -> str:
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "result": result,
        }, indent=2, ensure_ascii=False)

    def _provider_error(self, method_id: str, status_code: int, body: str) -> str:
        detail: Any = body[:500]
        try:
            detail = json.loads(body)
        except json.JSONDecodeError:
            pass
        logger.info("x api error method=%s status=%s body=%s", method_id, status_code, body[:300])
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "PROVIDER_ERROR",
            "http_status": status_code,
            "detail": detail,
        }, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
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
        if not self._access_token():
            return self._auth_missing(method_id)
        return await self._dispatch(method_id, call_args)

    async def _request(
        self,
        method_id: str,
        http_method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = _BASE_URL + path
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(has_body=False), params=params)
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(has_body=True), params=params, json=body)
                elif http_method == "DELETE":
                    response = await client.delete(url, headers=self._headers(has_body=False), params=params)
                else:
                    return json.dumps({"ok": False, "error_code": "UNSUPPORTED_HTTP_METHOD"}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            logger.error("x request failed", exc_info=e)
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "error_code": "HTTP_ERROR",
                "message": f"{type(e).__name__}: {e}",
            }, indent=2, ensure_ascii=False)

        if response.status_code >= 400:
            return self._provider_error(method_id, response.status_code, response.text)

        if not response.text.strip():
            return self._result(method_id, {})
        try:
            return self._result(method_id, response.json())
        except json.JSONDecodeError:
            return self._result(method_id, response.text)

    def _build_create_tweet_body(self, args: Dict[str, Any]) -> Dict[str, Any]:
        text = str(args.get("text", "")).strip()
        if not text and not args.get("media_ids"):
            raise ValueError("text or media_ids is required.")
        body: Dict[str, Any] = {}
        if text:
            body["text"] = text
        reply_to = str(args.get("reply_to_id", "")).strip()
        if reply_to:
            body["reply"] = {"in_reply_to_tweet_id": reply_to}
        quote = str(args.get("quote_tweet_id", "")).strip()
        if quote:
            body["quote_tweet_id"] = quote
        media_ids = args.get("media_ids") or []
        if media_ids:
            if not isinstance(media_ids, list):
                raise ValueError("media_ids must be a list of strings.")
            body["media"] = {"media_ids": [str(m) for m in media_ids]}
        poll_options = args.get("poll_options") or []
        poll_minutes = args.get("poll_minutes")
        if poll_options:
            if not isinstance(poll_options, list) or not (2 <= len(poll_options) <= 4):
                raise ValueError("poll_options must be a list of 2-4 strings.")
            if not poll_minutes:
                raise ValueError("poll_minutes is required when poll_options provided.")
            body["poll"] = {"options": [str(o) for o in poll_options], "duration_minutes": int(poll_minutes)}
        for_super_followers = bool(args.get("for_super_followers_only", False))
        if for_super_followers:
            body["for_super_followers_only"] = True
        reply_settings = str(args.get("reply_settings", "")).strip()
        if reply_settings:
            if reply_settings not in {"following", "mentionedUsers", "subscribers"}:
                raise ValueError("reply_settings must be one of following, mentionedUsers, subscribers.")
            body["reply_settings"] = reply_settings
        return body

    @staticmethod
    def _csv(value: Any) -> str:
        if not value:
            return ""
        if isinstance(value, (list, tuple, set)):
            return ",".join(str(v) for v in value if str(v).strip())
        return str(value).strip()

    def _expansion_params(self, args: Dict[str, Any]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for src, dst in [
            ("expansions", "expansions"),
            ("tweet_fields", "tweet.fields"),
            ("user_fields", "user.fields"),
            ("media_fields", "media.fields"),
            ("place_fields", "place.fields"),
            ("poll_fields", "poll.fields"),
        ]:
            v = self._csv(args.get(src))
            if v:
                out[dst] = v
        return out

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "x.users.me.v1":
                params = self._expansion_params(args)
                return await self._request(method_id, "GET", "/users/me", params=params or None)

            if method_id == "x.users.by_username.v1":
                username = str(args.get("username", "")).strip().lstrip("@")
                if not username:
                    raise ValueError("username is required.")
                return await self._request(method_id, "GET", f"/users/by/username/{username}", params=self._expansion_params(args) or None)

            if method_id == "x.users.by_id.v1":
                user_id = str(args.get("user_id", "")).strip()
                if not user_id:
                    raise ValueError("user_id is required.")
                return await self._request(method_id, "GET", f"/users/{user_id}", params=self._expansion_params(args) or None)

            if method_id == "x.tweets.create.v1":
                return await self._request(method_id, "POST", "/tweets", body=self._build_create_tweet_body(args))

            if method_id == "x.tweets.delete.v1":
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not tweet_id:
                    raise ValueError("tweet_id is required.")
                return await self._request(method_id, "DELETE", f"/tweets/{tweet_id}")

            if method_id == "x.tweets.get.v1":
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not tweet_id:
                    raise ValueError("tweet_id is required.")
                return await self._request(method_id, "GET", f"/tweets/{tweet_id}", params=self._expansion_params(args) or None)

            if method_id == "x.tweets.search_recent.v1":
                query = str(args.get("query", "")).strip()
                if not query:
                    raise ValueError("query is required.")
                params: Dict[str, Any] = {"query": query, **self._expansion_params(args)}
                for k in ("max_results", "next_token", "since_id", "until_id", "start_time", "end_time", "sort_order"):
                    v = args.get(k)
                    if v not in (None, ""):
                        params[k] = str(v)
                return await self._request(method_id, "GET", "/tweets/search/recent", params=params)

            if method_id == "x.timelines.user.v1":
                user_id = str(args.get("user_id", "")).strip()
                if not user_id:
                    raise ValueError("user_id is required.")
                params = self._expansion_params(args)
                for k in ("max_results", "pagination_token", "since_id", "until_id", "exclude"):
                    v = args.get(k)
                    if v not in (None, ""):
                        params[k] = self._csv(v) if k == "exclude" else str(v)
                return await self._request(method_id, "GET", f"/users/{user_id}/tweets", params=params or None)

            if method_id == "x.timelines.reverse_chronological.v1":
                user_id = str(args.get("user_id", "")).strip()
                if not user_id:
                    raise ValueError("user_id is required (the authenticated user's id from users.me).")
                params = self._expansion_params(args)
                for k in ("max_results", "pagination_token", "since_id", "until_id"):
                    v = args.get(k)
                    if v not in (None, ""):
                        params[k] = str(v)
                return await self._request(method_id, "GET", f"/users/{user_id}/timelines/reverse_chronological", params=params or None)

            if method_id == "x.likes.create.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "POST", f"/users/{source_user_id}/likes", body={"tweet_id": tweet_id})

            if method_id == "x.likes.delete.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "DELETE", f"/users/{source_user_id}/likes/{tweet_id}")

            if method_id == "x.retweets.create.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "POST", f"/users/{source_user_id}/retweets", body={"tweet_id": tweet_id})

            if method_id == "x.retweets.delete.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "DELETE", f"/users/{source_user_id}/retweets/{tweet_id}")

            if method_id == "x.bookmarks.create.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "POST", f"/users/{source_user_id}/bookmarks", body={"tweet_id": tweet_id})

            if method_id == "x.bookmarks.delete.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                tweet_id = str(args.get("tweet_id", "")).strip()
                if not source_user_id or not tweet_id:
                    raise ValueError("source_user_id and tweet_id are required.")
                return await self._request(method_id, "DELETE", f"/users/{source_user_id}/bookmarks/{tweet_id}")

            if method_id == "x.follows.create.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                target_user_id = str(args.get("target_user_id", "")).strip()
                if not source_user_id or not target_user_id:
                    raise ValueError("source_user_id and target_user_id are required.")
                return await self._request(method_id, "POST", f"/users/{source_user_id}/following", body={"target_user_id": target_user_id})

            if method_id == "x.follows.delete.v1":
                source_user_id = str(args.get("source_user_id", "")).strip()
                target_user_id = str(args.get("target_user_id", "")).strip()
                if not source_user_id or not target_user_id:
                    raise ValueError("source_user_id and target_user_id are required.")
                return await self._request(method_id, "DELETE", f"/users/{source_user_id}/following/{target_user_id}")

        except ValueError as e:
            return self._invalid_args(method_id, str(e))
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)
