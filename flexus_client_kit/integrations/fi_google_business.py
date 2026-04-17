import asyncio
import logging
import time
from typing import Dict, Any, Optional

import httpx

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import erp_schema

logger = logging.getLogger("google_business")

GOOGLE_BUSINESS_SCOPES = ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
    "https://www.googleapis.com/auth/business.manage",
]

GOOGLE_BUSINESS_PROMPT = """
## Google Business Profile

You have access to `google_business` tool for managing Google Business Profile reviews.
Use `google_business(op="listAccounts")` then `listLocations` to discover the right location.
Use `listNewReviews` to check for new reviews since the last check.
When replying to reviews, be professional and empathetic. Acknowledge negative feedback constructively.
Use `replyToReview` to post a response. Confirm with the user before replying to negative reviews (1-2 stars).
"""

GOOGLE_BUSINESS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="google_business",
    auth_required="google_business",
    description='Manage Google Business Profile reviews, call with op="help" for usage',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

HELP = """
Help:

google_business(op="status")
    Show connection status.

# Account / Location Discovery
google_business(op="listAccounts")
    List all Google Business Profile accounts.

google_business(op="listLocations", args={"accountId": "123456789"})
    List locations for an account.

# Review Operations
google_business(op="listReviews", args={
    "locationName": "accounts/123/locations/456",
    "pageSize": 20,        # Optional, default 20, max 50
    "pageToken": "..."     # Optional, for pagination
})

google_business(op="getReview", args={
    "reviewName": "accounts/123/locations/456/reviews/789"
})

google_business(op="replyToReview", args={
    "reviewName": "accounts/123/locations/456/reviews/789",
    "comment": "Thank you for your feedback!"
})

google_business(op="updateReply", args={
    "reviewName": "accounts/123/locations/456/reviews/789",
    "comment": "Updated reply text"
})

google_business(op="deleteReply", args={
    "reviewName": "accounts/123/locations/456/reviews/789"
})

google_business(op="listNewReviews", args={
    "locationName": "accounts/123/locations/456",
    "sinceTs": 1711929600  # Unix timestamp, returns reviews updated after this time
})
"""

_ACCOUNTS_URL = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
_LOCATIONS_BASE = "https://mybusinessbusinessinformation.googleapis.com/v1"
_REVIEWS_BASE = "https://mybusiness.googleapis.com/v4"
_TIMEOUT = 30.0


class IntegrationGoogleBusiness:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,
    ):
        self.fclient = fclient
        self.rcx = rcx

    def _access_token(self) -> str:
        auth = self.rcx.external_auth.get("google_business") or {}
        return (auth.get("token") or {}).get("access_token", "")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._access_token()}",
            "Content-Type": "application/json",
        }

    async def _request(self, method: str, url: str, **kwargs) -> dict:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            for attempt in range(4):
                resp = await client.request(method, url, headers=self._headers(), **kwargs)
                if resp.status_code == 429:
                    wait = min(2 ** attempt, 15)
                    logger.warning("GBP rate limited, retrying in %ds (attempt %d)", wait, attempt + 1)
                    await asyncio.sleep(wait)
                    continue
                break
            if resp.status_code in (401, 403):
                raise _AuthError(f"{resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
            if resp.status_code == 204:
                return {}
            return resp.json()

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        access_token = self._access_token()
        authenticated = bool(access_token)

        if print_status:
            r = "Google Business Profile integration status:\n"
            r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
            r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
            r += f"  Workspace: {self.rcx.persona.ws_id}\n"
            if not authenticated:
                r += "\n⚠️  Not connected. Please connect Google Business Profile in bot Integrations tab.\n"
            return r

        if print_help:
            return HELP

        if not authenticated:
            return "Google Business Profile not connected. Please connect in bot Integrations tab."

        try:
            if op == "listAccounts":
                return await self._list_accounts(args)
            elif op == "listLocations":
                return await self._list_locations(args)
            elif op == "listReviews":
                return await self._list_reviews(args)
            elif op == "getReview":
                return await self._get_review(args)
            elif op == "replyToReview":
                return await self._reply_to_review(args, toolcall.fcall_ft_id)
            elif op == "updateReply":
                return await self._update_reply(args)
            elif op == "deleteReply":
                return await self._delete_reply(args, toolcall)
            elif op == "listNewReviews":
                return await self._list_new_reviews(args)
            else:
                return f"❌ Unknown operation: {op}\n\nTry google_business(op='help') for usage."

        except _AuthError as e:
            return f"❌ Authentication error: {e}\n\nPlease reconnect Google Business Profile in bot Integrations tab."
        except httpx.HTTPStatusError as e:
            error_msg = f"Google Business API error: {e.response.status_code} - {e.response.text[:300]}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
    async def _list_accounts(self, args: Dict[str, Any]) -> str:
        data = await self._request("GET", _ACCOUNTS_URL)
        accounts = data.get("accounts", [])
        if not accounts:
            return "📭 No Google Business Profile accounts found."
        lines = [f"Found {len(accounts)} account(s):\n"]
        for i, acc in enumerate(accounts, 1):
            name = acc.get("name", "")
            acc_name = acc.get("accountName", "(unnamed)")
            acc_type = acc.get("type", "")
            acc_id = name.split("/")[-1] if "/" in name else name
            lines.append(f"{i}. {acc_name} (ID: {acc_id}, Type: {acc_type})")
            lines.append(f"   Resource: {name}")
        lines.append(f"\n💡 Use google_business(op='listLocations', args={{'accountId': '{accounts[0].get('name', '').split('/')[-1]}'}}) to see locations")
        return "\n".join(lines)
    async def _list_locations(self, args: Dict[str, Any]) -> str:
        account_id = args.get("accountId", "")
        if not account_id:
            return "❌ Missing required parameter: 'accountId'"
        url = f"{_LOCATIONS_BASE}/accounts/{account_id}/locations"
        params = {"readMask": "name,title,storefrontAddress"}
        page_token = args.get("pageToken", "")
        if page_token:
            params["pageToken"] = page_token
        data = await self._request("GET", url, params=params)
        locations = data.get("locations", [])
        if not locations:
            return f"📭 No locations found for account {account_id}."
        lines = [f"Found {len(locations)} location(s):\n"]
        for i, loc in enumerate(locations, 1):
            name = loc.get("name", "")
            title = loc.get("title", "(untitled)")
            addr = loc.get("storefrontAddress", {})
            addr_lines = addr.get("addressLines", [])
            city = addr.get("locality", "")
            addr_str = ", ".join(addr_lines + ([city] if city else []))
            lines.append(f"{i}. {title}")
            lines.append(f"   Location: {name}")
            if addr_str:
                lines.append(f"   Address: {addr_str}")
        next_page = data.get("nextPageToken", "")
        if next_page:
            lines.append(f"\n📄 More results available, use pageToken: {next_page}")
        lines.append(f"\n💡 Use the location name (e.g. '{locations[0].get('name', '')}') for review operations")
        return "\n".join(lines)
    async def _list_reviews(self, args: Dict[str, Any]) -> str:
        location_name = args.get("locationName", "")
        if not location_name:
            return "❌ Missing required parameter: 'locationName' (e.g. 'accounts/123/locations/456')"
        page_size = min(args.get("pageSize", 20), 50)
        url = f"{_REVIEWS_BASE}/{location_name}/reviews"
        params = {"pageSize": page_size}
        page_token = args.get("pageToken", "")
        if page_token:
            params["pageToken"] = page_token
        data = await self._request("GET", url, params=params)
        reviews = data.get("reviews", [])
        if not reviews:
            return f"📭 No reviews found for {location_name}."
        total = data.get("totalReviewCount", len(reviews))
        avg = data.get("averageRating", "N/A")
        lines = [f"⭐ {total} total review(s), average rating: {avg}\n"]
        for i, rev in enumerate(reviews, 1):
            lines.append(_format_review_short(i, rev))
        next_page = data.get("nextPageToken", "")
        if next_page:
            lines.append(f"\n📄 More results: google_business(op='listReviews', args={{...pageToken: '{next_page}'}})")
        return "\n".join(lines)
    async def _get_review(self, args: Dict[str, Any]) -> str:
        review_name = args.get("reviewName", "")
        if not review_name:
            return "❌ Missing required parameter: 'reviewName'"
        url = f"{_REVIEWS_BASE}/{review_name}"
        rev = await self._request("GET", url)
        return _format_review_full(rev)
    async def _reply_to_review(self, args: Dict[str, Any], ft_id: str) -> str:
        review_name = args.get("reviewName", "")
        comment = args.get("comment", "")
        if not review_name or not comment:
            return "❌ Missing required parameters: 'reviewName' and 'comment'"
        url = f"{_REVIEWS_BASE}/{review_name}/reply"
        data = await self._request("PUT", url, json={"comment": comment})
        await self._create_activity_for_review_reply(review_name, comment, ft_id)
        return f"✅ Reply posted successfully to {review_name}"
    async def _update_reply(self, args: Dict[str, Any]) -> str:
        review_name = args.get("reviewName", "")
        comment = args.get("comment", "")
        if not review_name or not comment:
            return "❌ Missing required parameters: 'reviewName' and 'comment'"
        url = f"{_REVIEWS_BASE}/{review_name}/reply"
        await self._request("PUT", url, json={"comment": comment})
        return f"✅ Reply updated for {review_name}"
    async def _delete_reply(self, args: Dict[str, Any], toolcall: ckit_cloudtool.FCloudtoolCall) -> str:
        review_name = args.get("reviewName", "")
        if not review_name:
            return "❌ Missing required parameter: 'reviewName'"
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="google_business_delete",
                confirm_command=f"google_business delete reply {review_name}",
                confirm_explanation="This will permanently delete the reply to this review",
            )
        url = f"{_REVIEWS_BASE}/{review_name}/reply"
        await self._request("DELETE", url)
        return f"✅ Reply deleted for {review_name}"
    async def _list_new_reviews(self, args: Dict[str, Any]) -> str:
        location_name = args.get("locationName", "")
        since_ts = args.get("sinceTs", 0)
        if not location_name:
            return "❌ Missing required parameter: 'locationName'"
        if not since_ts:
            return "❌ Missing required parameter: 'sinceTs' (unix timestamp)"
        url = f"{_REVIEWS_BASE}/{location_name}/reviews"
        all_new = []
        page_token = ""
        for _ in range(10):  # max 10 pages
            params = {"pageSize": 50}
            if page_token:
                params["pageToken"] = page_token
            data = await self._request("GET", url, params=params)
            reviews = data.get("reviews", [])
            for rev in reviews:
                update_time = rev.get("updateTime", "")
                if update_time and _parse_timestamp(update_time) > since_ts:
                    all_new.append(rev)
                elif update_time and _parse_timestamp(update_time) <= since_ts:
                    return _format_new_reviews(all_new, since_ts)
            page_token = data.get("nextPageToken", "")
            if not page_token:
                break
        return _format_new_reviews(all_new, since_ts)
    async def _create_activity_for_review_reply(self, review_name: str, comment: str, ft_id: str) -> None:
        try:
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
            await ckit_erp.erp_record_create(http, "crm_activity", self.rcx.persona.ws_id, {
                "ws_id": self.rcx.persona.ws_id,
                "activity_title": f"Review reply: {review_name.split('/')[-1]}",
                "activity_type": "WEB_CHAT",
                "activity_direction": "OUTBOUND",
                "activity_platform": "GOOGLE_BUSINESS",
                "activity_ft_id": ft_id,
                "activity_summary": comment[:500] if len(comment) > 500 else comment,
                "activity_details": {"review_name": review_name, "comment": comment},
                "activity_occurred_ts": time.time(),
            })
            logger.info("Created CRM activity for review reply to %s", review_name)
        except Exception as e:
            logger.warning("Failed to create CRM activity for review reply: %s", e)


class _AuthError(Exception):
    pass


def _parse_timestamp(iso_str: str) -> float:
    # Parse ISO 8601 timestamp like "2024-01-15T10:30:00Z" to unix timestamp
    try:
        from datetime import datetime, timezone
        iso_str = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso_str)
        return dt.timestamp()
    except Exception:
        return 0.0


def _star_str(rating: str) -> str:
    stars = {"STAR_RATING_UNSPECIFIED": "?", "ONE": "⭐", "TWO": "⭐⭐", "THREE": "⭐⭐⭐", "FOUR": "⭐⭐⭐⭐", "FIVE": "⭐⭐⭐⭐⭐"}
    return stars.get(rating, rating)


def _format_review_short(idx: int, rev: dict) -> str:
    name = rev.get("name", "")
    reviewer = rev.get("reviewer", {}).get("displayName", "Anonymous")
    rating = _star_str(rev.get("starRating", ""))
    comment = rev.get("comment", "(no comment)")
    update_time = rev.get("updateTime", "")
    has_reply = "reviewReply" in rev
    reply_indicator = " [replied]" if has_reply else ""
    lines = f"{idx}. {rating} by {reviewer}{reply_indicator}\n"
    lines += f"   {comment[:120]}{'...' if len(comment) > 120 else ''}\n"
    lines += f"   Updated: {update_time}  Name: {name}\n"
    return lines


def _format_review_full(rev: dict) -> str:
    name = rev.get("name", "")
    reviewer = rev.get("reviewer", {})
    rating = _star_str(rev.get("starRating", ""))
    comment = rev.get("comment", "(no comment)")
    create_time = rev.get("createTime", "")
    update_time = rev.get("updateTime", "")
    reply = rev.get("reviewReply", {})
    lines = [
        f"📧 Review Details:",
        f"",
        f"Name: {name}",
        f"Reviewer: {reviewer.get('displayName', 'Anonymous')}",
        f"Rating: {rating}",
        f"Created: {create_time}",
        f"Updated: {update_time}",
        f"",
        f"--- Review ---",
        comment,
    ]
    if reply:
        lines.extend([
            f"",
            f"--- Owner Reply ({reply.get('updateTime', '')}) ---",
            reply.get("comment", ""),
        ])
    else:
        lines.append("\n💡 No reply yet. Use replyToReview to respond.")
    return "\n".join(lines)


def _format_new_reviews(reviews: list, since_ts: float) -> str:
    if not reviews:
        return f"📭 No new reviews since {time.strftime('%Y-%m-%d %H:%M', time.gmtime(since_ts))} UTC"
    lines = [f"🆕 Found {len(reviews)} new/updated review(s):\n"]
    for i, rev in enumerate(reviews, 1):
        lines.append(_format_review_short(i, rev))
    return "\n".join(lines)
