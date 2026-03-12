import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("youtube")

PROVIDER_NAME = "youtube"
_BASE_URL = "https://www.googleapis.com/youtube/v3"

# These require multipart binary file upload — not feasible via JSON integration
_BINARY_UPLOAD_METHODS = {
    "youtube.captions.insert.v1",
    "youtube.channel_banners.insert.v1",
    "youtube.thumbnails.set.v1",
    "youtube.videos.insert.v1",
    "youtube.watermarks.set.v1",
}

METHOD_IDS = [
    # Read — API key sufficient
    "youtube.activities.list.v1",
    "youtube.captions.list.v1",
    "youtube.channel_sections.list.v1",
    "youtube.channels.list.v1",
    "youtube.comment_threads.list.v1",
    "youtube.comments.list.v1",
    "youtube.i18n_languages.list.v1",
    "youtube.i18n_regions.list.v1",
    "youtube.playlist_items.list.v1",
    "youtube.playlists.list.v1",
    "youtube.search.list.v1",
    "youtube.subscriptions.list.v1",
    "youtube.video_abuse_report_reasons.list.v1",
    "youtube.video_categories.list.v1",
    "youtube.videos.list.v1",
    # Read — OAuth required
    "youtube.captions.download.v1",
    "youtube.members.list.v1",
    "youtube.memberships_levels.list.v1",
    "youtube.videos.get_rating.v1",
    # Write — OAuth required (JSON body)
    "youtube.activities.insert.v1",
    "youtube.captions.delete.v1",
    "youtube.captions.update.v1",
    "youtube.channel_sections.delete.v1",
    "youtube.channel_sections.insert.v1",
    "youtube.channel_sections.update.v1",
    "youtube.channels.update.v1",
    "youtube.comment_threads.insert.v1",
    "youtube.comments.delete.v1",
    "youtube.comments.insert.v1",
    "youtube.comments.set_moderation_status.v1",
    "youtube.comments.update.v1",
    "youtube.playlist_items.delete.v1",
    "youtube.playlist_items.insert.v1",
    "youtube.playlist_items.update.v1",
    "youtube.playlists.delete.v1",
    "youtube.playlists.insert.v1",
    "youtube.playlists.update.v1",
    "youtube.subscriptions.delete.v1",
    "youtube.subscriptions.insert.v1",
    "youtube.videos.delete.v1",
    "youtube.videos.rate.v1",
    "youtube.videos.report_abuse.v1",
    "youtube.videos.update.v1",
    "youtube.watermarks.unset.v1",
    # Write — OAuth required (binary file upload, not executable via JSON integration)
    "youtube.captions.insert.v1",
    "youtube.channel_banners.insert.v1",
    "youtube.thumbnails.set.v1",
    "youtube.videos.insert.v1",
    "youtube.watermarks.set.v1",
]


class IntegrationYoutube:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _auth(self) -> Dict:
        return (self.rcx.external_auth.get("youtube") or {}) if self.rcx else {}

    def _pick(self, args: Dict, keys: List[str]) -> Dict:
        return {k: args[k] for k in keys if args.get(k) is not None}

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
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
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
        if method_id in _BINARY_UPLOAD_METHODS:
            return json.dumps({
                "ok": False,
                "error_code": "BINARY_UPLOAD_REQUIRED",
                "message": (
                    f"{method_id} requires multipart binary file upload. "
                    "Use the YouTube Data API directly with a resumable upload session."
                ),
            }, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _req(
        self,
        http_method: str,
        endpoint: str,
        params: Dict,
        body: Optional[Dict] = None,
        oauth: bool = False,
    ) -> str:
        auth = self._auth()
        api_key = auth.get("api_key", "")
        token = auth.get("oauth_token", "")

        if oauth:
            if not token:
                return json.dumps({
                    "ok": False,
                    "error_code": "OAUTH_REQUIRED",
                    "message": "This method requires an OAuth 2.0 token. Set oauth_token in youtube auth.",
                }, indent=2, ensure_ascii=False)
            headers: Dict = {"Authorization": f"Bearer {token}"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            req_params = params
        else:
            if not api_key:
                return json.dumps({
                    "ok": False,
                    "error_code": "AUTH_MISSING",
                    "message": "Set api_key in youtube auth.",
                }, indent=2, ensure_ascii=False)
            headers = {}
            req_params = {**params, "key": api_key}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                if http_method == "GET":
                    r = await client.get(_BASE_URL + endpoint, params=req_params, headers=headers)
                elif http_method == "POST":
                    r = await client.post(_BASE_URL + endpoint, params=req_params, json=body, headers=headers)
                elif http_method == "PUT":
                    r = await client.put(_BASE_URL + endpoint, params=req_params, json=body, headers=headers)
                elif http_method == "DELETE":
                    r = await client.delete(_BASE_URL + endpoint, params=req_params, headers=headers)
                else:
                    return json.dumps({"ok": False, "error_code": "UNSUPPORTED_HTTP_METHOD"}, indent=2, ensure_ascii=False)
            if r.status_code == 204:
                return json.dumps({"ok": True, "result": "success"}, indent=2, ensure_ascii=False)
            if r.status_code >= 400:
                logger.info("%s %s %s HTTP %s: %s", PROVIDER_NAME, http_method, endpoint, r.status_code, r.text[:200])
                return json.dumps({"ok": False, "error_code": "PROVIDER_ERROR", "status": r.status_code, "detail": r.text[:300]}, indent=2, ensure_ascii=False)
            return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _dispatch(self, method_id: str, args: Dict) -> str:  # noqa: C901
        # === Activities ===
        if method_id == "youtube.activities.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "channelId", "home", "mine", "maxResults", "pageToken",
                "publishedAfter", "publishedBefore", "regionCode",
            ])}
            return await self._req("GET", "/activities", params)

        if method_id == "youtube.activities.insert.v1":
            params = {"part": args.get("part", "snippet")}
            return await self._req("POST", "/activities", params, body=args.get("body"), oauth=True)

        # === Captions ===
        if method_id == "youtube.captions.list.v1":
            params = {"part": args.get("part", "snippet"), "videoId": args.get("videoId", ""), **self._pick(args, [
                "id", "onBehalfOf", "onBehalfOfContentOwner",
            ])}
            return await self._req("GET", "/captions", params)

        if method_id == "youtube.captions.download.v1":
            caption_id = args.get("id", "")
            params = self._pick(args, ["onBehalfOf", "onBehalfOfContentOwner", "tfmt", "tlang"])
            return await self._req("GET", f"/captions/{caption_id}", params, oauth=True)

        if method_id == "youtube.captions.delete.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOf", "onBehalfOfContentOwner"])}
            return await self._req("DELETE", "/captions", params, oauth=True)

        if method_id == "youtube.captions.update.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "onBehalfOf", "onBehalfOfContentOwner", "sync",
            ])}
            return await self._req("PUT", "/captions", params, body=args.get("body"), oauth=True)

        # === ChannelBanners — insert is binary upload, handled above ===

        # === ChannelSections ===
        if method_id == "youtube.channel_sections.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "channelId", "hl", "id", "mine", "onBehalfOfContentOwner",
            ])}
            return await self._req("GET", "/channelSections", params)

        if method_id == "youtube.channel_sections.insert.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("POST", "/channelSections", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.channel_sections.update.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("PUT", "/channelSections", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.channel_sections.delete.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("DELETE", "/channelSections", params, oauth=True)

        # === Channels ===
        if method_id == "youtube.channels.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "categoryId", "forHandle", "forUsername", "hl", "id",
                "managedByMe", "maxResults", "mine", "mySubscribers",
                "onBehalfOfContentOwner", "pageToken",
            ])}
            return await self._req("GET", "/channels", params)

        if method_id == "youtube.channels.update.v1":
            params = {"part": args.get("part", "brandingSettings"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("PUT", "/channels", params, body=args.get("body"), oauth=True)

        # === CommentThreads ===
        if method_id == "youtube.comment_threads.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "allThreadsRelatedToChannelId", "channelId", "id", "maxResults",
                "moderationStatus", "order", "pageToken", "searchTerms", "videoId",
            ])}
            return await self._req("GET", "/commentThreads", params)

        if method_id == "youtube.comment_threads.insert.v1":
            params = {"part": args.get("part", "snippet")}
            return await self._req("POST", "/commentThreads", params, body=args.get("body"), oauth=True)

        # === Comments ===
        if method_id == "youtube.comments.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "id", "maxResults", "pageToken", "parentId", "textFormat",
            ])}
            return await self._req("GET", "/comments", params)

        if method_id == "youtube.comments.insert.v1":
            params = {"part": args.get("part", "snippet")}
            return await self._req("POST", "/comments", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.comments.update.v1":
            params = {"part": args.get("part", "snippet")}
            return await self._req("PUT", "/comments", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.comments.delete.v1":
            return await self._req("DELETE", "/comments", {"id": args.get("id", "")}, oauth=True)

        if method_id == "youtube.comments.set_moderation_status.v1":
            params = {
                "id": args.get("id", ""),
                "moderationStatus": args.get("moderationStatus", ""),
                **self._pick(args, ["banAuthor"]),
            }
            return await self._req("POST", "/comments/setModerationStatus", params, oauth=True)

        # === I18n ===
        if method_id == "youtube.i18n_languages.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["hl"])}
            return await self._req("GET", "/i18nLanguages", params)

        if method_id == "youtube.i18n_regions.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["hl"])}
            return await self._req("GET", "/i18nRegions", params)

        # === Members ===
        if method_id == "youtube.members.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "filterByMemberChannelId", "hasAccessToLevel", "maxResults", "mode", "pageToken",
            ])}
            return await self._req("GET", "/members", params, oauth=True)

        if method_id == "youtube.memberships_levels.list.v1":
            params = {"part": args.get("part", "id,snippet")}
            return await self._req("GET", "/membershipsLevels", params, oauth=True)

        # === PlaylistItems ===
        if method_id == "youtube.playlist_items.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "id", "maxResults", "onBehalfOfContentOwner", "pageToken", "playlistId", "videoId",
            ])}
            return await self._req("GET", "/playlistItems", params)

        if method_id == "youtube.playlist_items.insert.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("POST", "/playlistItems", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.playlist_items.update.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("PUT", "/playlistItems", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.playlist_items.delete.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("DELETE", "/playlistItems", params, oauth=True)

        # === Playlists ===
        if method_id == "youtube.playlists.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "channelId", "hl", "id", "maxResults", "mine", "onBehalfOfContentOwner", "pageToken",
            ])}
            return await self._req("GET", "/playlists", params)

        if method_id == "youtube.playlists.insert.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("POST", "/playlists", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.playlists.update.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("PUT", "/playlists", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.playlists.delete.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("DELETE", "/playlists", params, oauth=True)

        # === Search ===
        if method_id == "youtube.search.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "q", "type", "channelId", "channelType", "eventType",
                "forContentOwner", "forDeveloper", "forMine", "location", "locationRadius",
                "maxResults", "onBehalfOfContentOwner", "order", "pageToken",
                "publishedAfter", "publishedBefore", "regionCode", "relatedToVideoId",
                "relevanceLanguage", "safeSearch", "topicId", "videoCaption",
                "videoCategoryId", "videoDefinition", "videoDimension", "videoDuration",
                "videoEmbeddable", "videoLicense", "videoSyndicated", "videoType",
            ])}
            return await self._req("GET", "/search", params)

        # === Subscriptions ===
        if method_id == "youtube.subscriptions.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, [
                "channelId", "forChannelId", "id", "maxResults", "mine",
                "myRecentSubscribers", "mySubscribers", "onBehalfOfContentOwner",
                "order", "pageToken",
            ])}
            return await self._req("GET", "/subscriptions", params)

        if method_id == "youtube.subscriptions.insert.v1":
            params = {"part": args.get("part", "snippet")}
            return await self._req("POST", "/subscriptions", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.subscriptions.delete.v1":
            return await self._req("DELETE", "/subscriptions", {"id": args.get("id", "")}, oauth=True)

        # === VideoAbuseReportReasons ===
        if method_id == "youtube.video_abuse_report_reasons.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["hl"])}
            return await self._req("GET", "/videoAbuseReportReasons", params)

        # === VideoCategories ===
        if method_id == "youtube.video_categories.list.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["hl", "id", "regionCode"])}
            return await self._req("GET", "/videoCategories", params)

        # === Videos ===
        if method_id == "youtube.videos.list.v1":
            params = {"part": args.get("part", "snippet,statistics"), **self._pick(args, [
                "chart", "hl", "id", "locale", "maxHeight", "maxResults", "maxWidth",
                "myRating", "onBehalfOfContentOwner", "pageToken", "regionCode", "videoCategoryId",
            ])}
            return await self._req("GET", "/videos", params)

        if method_id == "youtube.videos.get_rating.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("GET", "/videos/getRating", params, oauth=True)

        if method_id == "youtube.videos.update.v1":
            params = {"part": args.get("part", "snippet"), **self._pick(args, ["onBehalfOfContentOwner", "stabilize"])}
            return await self._req("PUT", "/videos", params, body=args.get("body"), oauth=True)

        if method_id == "youtube.videos.delete.v1":
            params = {"id": args.get("id", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("DELETE", "/videos", params, oauth=True)

        if method_id == "youtube.videos.rate.v1":
            params = {"id": args.get("id", ""), "rating": args.get("rating", "")}
            return await self._req("POST", "/videos/rate", params, oauth=True)

        if method_id == "youtube.videos.report_abuse.v1":
            params = self._pick(args, ["onBehalfOfContentOwner"])
            return await self._req("POST", "/videos/reportAbuse", params, body=args.get("body"), oauth=True)

        # === Watermarks ===
        if method_id == "youtube.watermarks.unset.v1":
            params = {"channelId": args.get("channelId", ""), **self._pick(args, ["onBehalfOfContentOwner"])}
            return await self._req("POST", "/watermarks/unset", params, oauth=True)

        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)
