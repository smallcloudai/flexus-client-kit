import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("x")

PROVIDER_NAME = "x"
METHOD_IDS = [
    # Basic plan — tweets
    "x.tweets.counts_recent.v1",
    "x.tweets.search_recent.v1",
    "x.tweets.lookup.v1",
    "x.tweets.lookup_single.v1",
    "x.tweets.quote_tweets.v1",
    "x.tweets.liking_users.v1",
    "x.tweets.retweeted_by.v1",
    # Basic plan — users
    "x.users.lookup_by_ids.v1",
    "x.users.lookup_by_usernames.v1",
    "x.users.lookup_single.v1",
    "x.users.lookup_by_username.v1",
    "x.users.tweets_timeline.v1",
    "x.users.mentions_timeline.v1",
    "x.users.liked_tweets.v1",
    "x.users.followers.v1",
    "x.users.following.v1",
    "x.users.owned_lists.v1",
    "x.users.list_memberships.v1",
    "x.users.pinned_lists.v1",
    # Basic plan — lists
    "x.lists.lookup.v1",
    "x.lists.tweets.v1",
    "x.lists.members.v1",
    "x.lists.followers.v1",
    # Basic plan — spaces (Bearer Token supported)
    "x.spaces.lookup.v1",
    "x.spaces.lookup_single.v1",
    "x.spaces.by_creator_ids.v1",
    "x.spaces.search.v1",
    # Pro plan only
    "x.tweets.search_all.v1",
    "x.tweets.counts_all.v1",
    "x.users.search.v1",
    "x.trends.by_woeid.v1",
]

_BASE_URL = "https://api.twitter.com/2"


class IntegrationX:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _get_api_key(self) -> str:
        if self.rcx is not None:
            return (self.rcx.external_auth.get("x") or {}).get("api_key", "")
        return os.environ.get("X_BEARER_TOKEN", "")

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
        bearer_token = self._get_api_key()
        if not bearer_token:
            return json.dumps({"ok": False, "error_code": "AUTH_MISSING", "message": "Set X_BEARER_TOKEN env var or configure api_key in integrations."}, indent=2, ensure_ascii=False)

        headers = {"Authorization": f"Bearer {bearer_token}"}

        if method_id == "x.tweets.counts_recent.v1":
            return await self._counts_recent(headers, str(args.get("query", "")), args)
        if method_id == "x.tweets.search_recent.v1":
            return await self._search_recent(headers, str(args.get("query", "")), int(args.get("limit", 10)), args)
        if method_id == "x.tweets.lookup.v1":
            return await self._tweets_lookup(headers, args)
        if method_id == "x.tweets.lookup_single.v1":
            return await self._tweet_lookup_single(headers, args)
        if method_id == "x.tweets.quote_tweets.v1":
            return await self._tweet_quote_tweets(headers, args)
        if method_id == "x.tweets.liking_users.v1":
            return await self._tweet_liking_users(headers, args)
        if method_id == "x.tweets.retweeted_by.v1":
            return await self._tweet_retweeted_by(headers, args)
        if method_id == "x.users.lookup_by_ids.v1":
            return await self._users_lookup_by_ids(headers, args)
        if method_id == "x.users.lookup_by_usernames.v1":
            return await self._users_lookup_by_usernames(headers, args)
        if method_id == "x.users.lookup_single.v1":
            return await self._user_lookup_single(headers, args)
        if method_id == "x.users.lookup_by_username.v1":
            return await self._user_lookup_by_username(headers, args)
        if method_id == "x.users.tweets_timeline.v1":
            return await self._user_tweets_timeline(headers, args)
        if method_id == "x.users.mentions_timeline.v1":
            return await self._user_mentions_timeline(headers, args)
        if method_id == "x.users.liked_tweets.v1":
            return await self._user_liked_tweets(headers, args)
        if method_id == "x.users.followers.v1":
            return await self._user_followers(headers, args)
        if method_id == "x.users.following.v1":
            return await self._user_following(headers, args)
        if method_id == "x.users.owned_lists.v1":
            return await self._user_owned_lists(headers, args)
        if method_id == "x.users.list_memberships.v1":
            return await self._user_list_memberships(headers, args)
        if method_id == "x.users.pinned_lists.v1":
            return await self._user_pinned_lists(headers, args)
        if method_id == "x.lists.lookup.v1":
            return await self._list_lookup(headers, args)
        if method_id == "x.lists.tweets.v1":
            return await self._list_tweets(headers, args)
        if method_id == "x.lists.members.v1":
            return await self._list_members(headers, args)
        if method_id == "x.lists.followers.v1":
            return await self._list_followers(headers, args)
        if method_id == "x.spaces.lookup.v1":
            return await self._spaces_lookup(headers, args)
        if method_id == "x.spaces.lookup_single.v1":
            return await self._space_lookup_single(headers, args)
        if method_id == "x.spaces.by_creator_ids.v1":
            return await self._spaces_by_creator_ids(headers, args)
        if method_id == "x.spaces.search.v1":
            return await self._spaces_search(headers, args)
        if method_id == "x.tweets.search_all.v1":
            return await self._tweets_search_all(headers, args)
        if method_id == "x.tweets.counts_all.v1":
            return await self._tweets_counts_all(headers, args)
        if method_id == "x.users.search.v1":
            return await self._users_search(headers, args)
        if method_id == "x.trends.by_woeid.v1":
            return await self._trends_by_woeid(headers, args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    # ─── helpers ───────────────────────────────────────────────────────────────

    async def _get(self, headers: Dict, url: str, params: Dict) -> str:
        """Generic GET with standard error handling. Returns raw JSON string or error JSON."""
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url, params=params, headers=headers)
            if r.status_code == 403:
                logger.info("%s HTTP 403: %s", PROVIDER_NAME, r.text[:200])
                body = {}
                try:
                    body = r.json()
                except Exception:
                    pass
                detail = body.get("detail") or r.text[:300]
                if "pro" in detail.lower() or "subscription" in detail.lower() or "access" in detail.lower():
                    return json.dumps({"ok": False, "error_code": "PRO_PLAN_REQUIRED", "message": "This endpoint requires X API Pro plan or higher.", "detail": detail}, indent=2, ensure_ascii=False)
                return json.dumps({"ok": False, "error_code": "FORBIDDEN", "detail": detail}, indent=2, ensure_ascii=False)
            if r.status_code == 429:
                logger.info("%s HTTP 429 rate limit", PROVIDER_NAME)
                return json.dumps({"ok": False, "error_code": "RATE_LIMIT", "message": "Rate limit exceeded. Retry after a moment."}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s HTTP %s: %s", PROVIDER_NAME, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError, KeyError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    def _ok(self, data: Any, meta: Any = None, summary: str = "") -> str:
        payload: Dict[str, Any] = {"ok": True, "data": data}
        if meta is not None:
            payload["meta"] = meta
        result = json.dumps(payload, indent=2, ensure_ascii=False)
        return (summary + "\n\n" + result) if summary else result

    # ─── existing methods ───────────────────────────────────────────────────────

    async def _counts_recent(self, headers: Dict, query: str, args: Dict) -> str:
        params = {"query": query, "granularity": str(args.get("granularity", "day"))}
        raw = await self._get(headers, _BASE_URL + "/tweets/counts/recent", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        summary = f"Found {len(results)} day(s) of tweet counts. Total tweets: {meta.get('total_tweet_count', 'N/A')}."
        return self._ok(results, meta, summary)

    async def _search_recent(self, headers: Dict, query: str, limit: int, args: Dict) -> str:
        max_results = max(10, min(limit, 100))
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,author_id,public_metrics,lang")),
        }
        raw = await self._get(headers, _BASE_URL + "/tweets/search/recent", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        summary = f"Found {len(results)} tweet(s) matching '{query}'."
        return self._ok(results, meta, summary)

    # ─── tweets lookup ─────────────────────────────────────────────────────────

    async def _tweets_lookup(self, headers: Dict, args: Dict) -> str:
        ids = str(args.get("ids", "")).strip()
        if not ids:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.ids required (comma-separated tweet IDs)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"ids": ids}
        if args.get("tweet.fields"):
            params["tweet.fields"] = str(args["tweet.fields"])
        raw = await self._get(headers, _BASE_URL + "/tweets", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} tweet(s).")

    async def _tweet_lookup_single(self, headers: Dict, args: Dict) -> str:
        tweet_id = str(args.get("id", "")).strip()
        if not tweet_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("tweet.fields"):
            params["tweet.fields"] = str(args["tweet.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/tweets/{tweet_id}", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        return self._ok(data.get("data"), summary=f"Retrieved tweet {tweet_id}.")

    # ─── users lookup ──────────────────────────────────────────────────────────

    async def _users_lookup_by_ids(self, headers: Dict, args: Dict) -> str:
        ids = str(args.get("ids", "")).strip()
        if not ids:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.ids required (comma-separated user IDs)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"ids": ids}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, _BASE_URL + "/users", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} user(s).")

    async def _users_lookup_by_usernames(self, headers: Dict, args: Dict) -> str:
        usernames = str(args.get("usernames", "")).strip()
        if not usernames:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.usernames required (comma-separated handles, without @)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"usernames": usernames}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, _BASE_URL + "/users/by", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} user(s).")

    async def _user_lookup_single(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        return self._ok(data.get("data"), summary=f"Retrieved user {user_id}.")

    async def _user_lookup_by_username(self, headers: Dict, args: Dict) -> str:
        username = str(args.get("username", "")).strip().lstrip("@")
        if not username:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.username required (handle without @)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/users/by/username/{username}", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        return self._ok(data.get("data"), summary=f"Retrieved user @{username}.")

    # ─── timelines ─────────────────────────────────────────────────────────────

    async def _user_tweets_timeline(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(5, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,public_metrics,lang")),
        }
        if args.get("start_time"):
            params["start_time"] = str(args["start_time"])
        if args.get("end_time"):
            params["end_time"] = str(args["end_time"])
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/tweets", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} tweet(s) from user {user_id}.")

    async def _user_mentions_timeline(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(5, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,public_metrics,lang")),
        }
        if args.get("start_time"):
            params["start_time"] = str(args["start_time"])
        if args.get("end_time"):
            params["end_time"] = str(args["end_time"])
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/mentions", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} mention(s) for user {user_id}.")

    # ─── lists ─────────────────────────────────────────────────────────────────

    async def _list_lookup(self, headers: Dict, args: Dict) -> str:
        list_id = str(args.get("id", "")).strip()
        if not list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (list ID)."}, indent=2, ensure_ascii=False)
        raw = await self._get(headers, f"{_BASE_URL}/lists/{list_id}", {})
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        return self._ok(data.get("data"), summary=f"Retrieved list {list_id}.")

    async def _list_tweets(self, headers: Dict, args: Dict) -> str:
        list_id = str(args.get("id", "")).strip()
        if not list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (list ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,author_id,public_metrics")),
        }
        raw = await self._get(headers, f"{_BASE_URL}/lists/{list_id}/tweets", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} tweet(s) from list {list_id}.")

    # ─── tweet engagement ──────────────────────────────────────────────────────

    async def _tweet_quote_tweets(self, headers: Dict, args: Dict) -> str:
        tweet_id = str(args.get("id", "")).strip()
        if not tweet_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (tweet ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,author_id,public_metrics")),
        }
        raw = await self._get(headers, f"{_BASE_URL}/tweets/{tweet_id}/quote_tweets", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} quote tweet(s) for tweet {tweet_id}.")

    async def _tweet_liking_users(self, headers: Dict, args: Dict) -> str:
        tweet_id = str(args.get("id", "")).strip()
        if not tweet_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (tweet ID)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/tweets/{tweet_id}/liking_users", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} user(s) who liked tweet {tweet_id}.")

    async def _tweet_retweeted_by(self, headers: Dict, args: Dict) -> str:
        tweet_id = str(args.get("id", "")).strip()
        if not tweet_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (tweet ID)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/tweets/{tweet_id}/retweeted_by", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} user(s) who retweeted tweet {tweet_id}.")

    # ─── user liked / social graph ─────────────────────────────────────────────

    async def _user_liked_tweets(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,author_id,public_metrics")),
        }
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/liked_tweets", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} tweet(s) liked by user {user_id}.")

    async def _user_followers(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 1000))
        params: Dict[str, Any] = {"max_results": max_results}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/followers", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} follower(s) of user {user_id}.")

    async def _user_following(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 1000))
        params: Dict[str, Any] = {"max_results": max_results}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/following", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} account(s) followed by user {user_id}.")

    # ─── user list relations ────────────────────────────────────────────────────

    async def _user_owned_lists(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 100))
        params: Dict[str, Any] = {"max_results": max_results}
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/owned_lists", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} list(s) owned by user {user_id}.")

    async def _user_list_memberships(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 100))
        params: Dict[str, Any] = {"max_results": max_results}
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/list_memberships", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} list(s) user {user_id} is member of.")

    async def _user_pinned_lists(self, headers: Dict, args: Dict) -> str:
        user_id = str(args.get("id", "")).strip()
        if not user_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (numeric user ID)."}, indent=2, ensure_ascii=False)
        raw = await self._get(headers, f"{_BASE_URL}/users/{user_id}/pinned_lists", {})
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} pinned list(s) for user {user_id}.")

    # ─── additional list endpoints ─────────────────────────────────────────────

    async def _list_members(self, headers: Dict, args: Dict) -> str:
        list_id = str(args.get("id", "")).strip()
        if not list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (list ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 100))
        params: Dict[str, Any] = {"max_results": max_results}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/lists/{list_id}/members", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} member(s) of list {list_id}.")

    async def _list_followers(self, headers: Dict, args: Dict) -> str:
        list_id = str(args.get("id", "")).strip()
        if not list_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (list ID)."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 100)), 100))
        params: Dict[str, Any] = {"max_results": max_results}
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/lists/{list_id}/followers", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"Retrieved {len(results)} follower(s) of list {list_id}.")

    # ─── spaces ────────────────────────────────────────────────────────────────

    async def _spaces_lookup(self, headers: Dict, args: Dict) -> str:
        ids = str(args.get("ids", "")).strip()
        if not ids:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.ids required (comma-separated space IDs, up to 100)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"ids": ids}
        if args.get("space.fields"):
            params["space.fields"] = str(args["space.fields"])
        raw = await self._get(headers, _BASE_URL + "/spaces", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} space(s).")

    async def _space_lookup_single(self, headers: Dict, args: Dict) -> str:
        space_id = str(args.get("id", "")).strip()
        if not space_id:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.id required (space ID)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {}
        if args.get("space.fields"):
            params["space.fields"] = str(args["space.fields"])
        raw = await self._get(headers, f"{_BASE_URL}/spaces/{space_id}", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        return self._ok(data.get("data"), summary=f"Retrieved space {space_id}.")

    async def _spaces_by_creator_ids(self, headers: Dict, args: Dict) -> str:
        creator_ids = str(args.get("creator_ids", "")).strip()
        if not creator_ids:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.creator_ids required (comma-separated user IDs)."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"user_ids": creator_ids}
        if args.get("space.fields"):
            params["space.fields"] = str(args["space.fields"])
        raw = await self._get(headers, _BASE_URL + "/spaces/by/creator_ids", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Retrieved {len(results)} space(s) by creator IDs.")

    async def _spaces_search(self, headers: Dict, args: Dict) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query required."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {"query": query}
        state = str(args.get("state", "all")).strip()
        if state in ("live", "scheduled", "all"):
            params["state"] = state
        if args.get("space.fields"):
            params["space.fields"] = str(args["space.fields"])
        raw = await self._get(headers, _BASE_URL + "/spaces/search", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"Found {len(results)} space(s) matching '{query}'.")

    # ─── Pro-tier methods ───────────────────────────────────────────────────────

    async def _tweets_search_all(self, headers: Dict, args: Dict) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query required."}, indent=2, ensure_ascii=False)
        max_results = max(10, min(int(args.get("max_results", 10)), 500))
        params: Dict[str, Any] = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": str(args.get("tweet.fields", "created_at,author_id,public_metrics,lang")),
        }
        if args.get("start_time"):
            params["start_time"] = str(args["start_time"])
        if args.get("end_time"):
            params["end_time"] = str(args["end_time"])
        raw = await self._get(headers, _BASE_URL + "/tweets/search/all", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        return self._ok(results, meta, summary=f"[Pro] Found {len(results)} tweet(s) (full archive) matching '{query}'.")

    async def _tweets_counts_all(self, headers: Dict, args: Dict) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query required."}, indent=2, ensure_ascii=False)
        params: Dict[str, Any] = {
            "query": query,
            "granularity": str(args.get("granularity", "day")),
        }
        if args.get("start_time"):
            params["start_time"] = str(args["start_time"])
        if args.get("end_time"):
            params["end_time"] = str(args["end_time"])
        raw = await self._get(headers, _BASE_URL + "/tweets/counts/all", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        meta = data.get("meta", {})
        summary = f"[Pro] Found {len(results)} period(s) of tweet counts. Total: {meta.get('total_tweet_count', 'N/A')}."
        return self._ok(results, meta, summary)

    async def _users_search(self, headers: Dict, args: Dict) -> str:
        query = str(args.get("query", "")).strip()
        if not query:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.query required."}, indent=2, ensure_ascii=False)
        max_results = max(1, min(int(args.get("max_results", 10)), 100))
        params: Dict[str, Any] = {
            "query": query,
            "max_results": max_results,
        }
        if args.get("user.fields"):
            params["user.fields"] = str(args["user.fields"])
        raw = await self._get(headers, _BASE_URL + "/users/search", params)
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"[Pro] Found {len(results)} user(s) matching '{query}'.")

    async def _trends_by_woeid(self, headers: Dict, args: Dict) -> str:
        woeid = args.get("woeid")
        if woeid is None:
            return json.dumps({"ok": False, "error_code": "MISSING_PARAM", "message": "args.woeid required (e.g. 1=worldwide, 23424977=USA, 26062=London)."}, indent=2, ensure_ascii=False)
        raw = await self._get(headers, f"{_BASE_URL}/trends/by/woeid/{woeid}", {})
        try:
            data = json.loads(raw)
        except Exception:
            return raw
        if not data.get("ok", True):
            return raw
        results = data.get("data", [])
        return self._ok(results, summary=f"[Pro] Retrieved {len(results)} trend(s) for WOEID {woeid}.")
