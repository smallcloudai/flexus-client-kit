import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import quote

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("linkedin_b2b")
INTEGRATION_METADATA = {
    "provider": "linkedin_b2b",
    "auth_kind": "oauth2",
    "env_keys": [],
    "supports_ping": False,
}


PROVIDER_NAME = "linkedin_b2b"
METHOD_IDS = [
    "linkedin_b2b.organizations.get.v1",
    "linkedin_b2b.organizations.search.v1",
    "linkedin_b2b.organization_acls.member_organizations.list.v1",
    "linkedin_b2b.organization_acls.organization_members.list.v1",
    "linkedin_b2b.organization_posts.create.v1",
    "linkedin_b2b.organization_posts.get.v1",
    "linkedin_b2b.organization_posts.list.v1",
    "linkedin_b2b.organization_posts.delete.v1",
    "linkedin_b2b.comments.create.v1",
    "linkedin_b2b.comments.get.v1",
    "linkedin_b2b.comments.list.v1",
    "linkedin_b2b.comments.update.v1",
    "linkedin_b2b.comments.delete.v1",
    "linkedin_b2b.reactions.create.v1",
    "linkedin_b2b.reactions.list.v1",
    "linkedin_b2b.reactions.delete.v1",
    "linkedin_b2b.social_metadata.get.v1",
    "linkedin_b2b.followers.get.v1",
    "linkedin_b2b.followers.stats.get.v1",
    "linkedin_b2b.page_analytics.get.v1",
    "linkedin_b2b.share_statistics.get.v1",
    "linkedin_b2b.video_analytics.get.v1",
    "linkedin_b2b.member_profile_analytics.get.v1",
    "linkedin_b2b.member_post_analytics.get.v1",
    "linkedin_b2b.mentions.people.search.v1",
    "linkedin_b2b.notifications.social_actions.list.v1",
    "linkedin_b2b.ad_accounts.get.v1",
    "linkedin_b2b.ad_accounts.list.v1",
    "linkedin_b2b.ad_account_users.get.v1",
    "linkedin_b2b.ad_account_users.list.v1",
    "linkedin_b2b.ad_account_users.create.v1",
    "linkedin_b2b.ad_account_users.update.v1",
    "linkedin_b2b.ad_account_users.delete.v1",
    "linkedin_b2b.ad_campaign_groups.create.v1",
    "linkedin_b2b.ad_campaign_groups.get.v1",
    "linkedin_b2b.ad_campaign_groups.list.v1",
    "linkedin_b2b.ad_campaign_groups.update.v1",
    "linkedin_b2b.ad_campaigns.create.v1",
    "linkedin_b2b.ad_campaigns.get.v1",
    "linkedin_b2b.ad_campaigns.list.v1",
    "linkedin_b2b.ad_campaigns.update.v1",
    "linkedin_b2b.creatives.create.v1",
    "linkedin_b2b.creatives.get.v1",
    "linkedin_b2b.creatives.list.v1",
    "linkedin_b2b.ad_analytics.get.v1",
    "linkedin_b2b.ad_analytics.query.v1",
    "linkedin_b2b.audience_counts.get.v1",
    "linkedin_b2b.targeting_facets.list.v1",
    "linkedin_b2b.targeting_entities.list.v1",
    "linkedin_b2b.lead_forms.get.v1",
    "linkedin_b2b.lead_forms.list.v1",
    "linkedin_b2b.lead_forms.create.v1",
    "linkedin_b2b.lead_forms.update.v1",
    "linkedin_b2b.events.create.v1",
    "linkedin_b2b.events.get.v1",
    "linkedin_b2b.events.update.v1",
    "linkedin_b2b.events.list_by_organizer.v1",
    "linkedin_b2b.events.list_leadgen_by_organizer.v1",
    "linkedin_b2b.events.register_background_upload.v1",
    "linkedin_b2b.lead_sync.forms.get.v1",
    "linkedin_b2b.lead_sync.forms.list.v1",
    "linkedin_b2b.lead_sync.responses.get.v1",
    "linkedin_b2b.lead_sync.responses.list.v1",
    "linkedin_b2b.lead_sync.notifications.create.v1",
    "linkedin_b2b.lead_sync.notifications.get.v1",
    "linkedin_b2b.lead_sync.notifications.delete.v1",
    "linkedin_b2b.conversions.create.v1",
    "linkedin_b2b.conversions.get.v1",
    "linkedin_b2b.conversions.list.v1",
    "linkedin_b2b.conversions.associate_campaigns.v1",
    "linkedin_b2b.conversion_events.upload.v1",
    "linkedin_b2b.dmp_segments.create.v1",
    "linkedin_b2b.dmp_segments.get.v1",
    "linkedin_b2b.dmp_segments.list.v1",
    "linkedin_b2b.dmp_segments.update.v1",
    "linkedin_b2b.dmp_segment_users.upload.v1",
    "linkedin_b2b.dmp_segment_companies.upload.v1",
    "linkedin_b2b.dmp_segment_destinations.list.v1",
    "linkedin_b2b.dmp_segment_list_uploads.get.v1",
    "linkedin_b2b.ad_segments.list.v1",
    "linkedin_b2b.website_retargeting.list.v1",
    "linkedin_b2b.predictive_audiences.list.v1",
    "linkedin_b2b.audience_insights.query.v1",
    "linkedin_b2b.media_planning.forecast_reach.v1",
    "linkedin_b2b.media_planning.forecast_impressions.v1",
    "linkedin_b2b.media_planning.forecast_leads.v1",
    "linkedin_b2b.account_intelligence.get.v1",
]

_BASE_URL = "https://api.linkedin.com"
_TIMEOUT = 30.0

LINKEDIN_B2B_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="linkedin_b2b",
    description="LinkedIn non-partner B2B APIs: Community Management, Ads, Leads, Events, Conversions, and qualified private marketing surfaces.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Use help, status, list_methods, or call."},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

# B2B LinkedIn shares the same OAuth provider as open LinkedIn: "linkedin".
# App-level keys are not pasted into this module. They belong in the platform auth provider:
# - client_id: LinkedIn app Client ID from developer.linkedin.com
# - client_secret: LinkedIn app Client Secret from developer.linkedin.com
# - redirect_uri: the Flexus OAuth callback URL configured in the platform auth layer
# - scopes: the reviewed LinkedIn Marketing / Community / Lead Sync scopes approved for this app
# After OAuth completes, Flexus must store token.access_token in rcx.external_auth["linkedin"].
# The setup schema below is only for default runtime IDs that the bot can reuse on calls.
LINKEDIN_B2B_SETUP_SCHEMA = [
    {
        "bs_name": "ad_account_id",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "LinkedIn B2B",
        "bs_order": 10,
        "bs_importance": 1,
        "bs_description": (
            "Default LinkedIn Ads account ID used by ad and lead methods. "
            "Value: the numeric ad account ID, for example 123456789. "
            "Get it from LinkedIn Campaign Manager or from the adAccounts API after auth works. "
            "Paste it into this setup field in the bot/persona setup, not into OAuth secrets."
        ),
    },
    {
        "bs_name": "organization_id",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "LinkedIn B2B",
        "bs_order": 20,
        "bs_importance": 1,
        "bs_description": (
            "Default LinkedIn organization ID used by page, org, post, follower, and analytics methods. "
            "Value: the numeric organization ID, for example 987654321. "
            "Get it from the LinkedIn Page admin URL, organization lookup calls, or your onboarding data. "
            "Paste it into this setup field in the bot/persona setup."
        ),
    },
    {
        "bs_name": "linkedin_api_version",
        "bs_type": "string_short",
        "bs_default": "202509",
        "bs_group": "LinkedIn B2B",
        "bs_order": 30,
        "bs_importance": 1,
        "bs_description": (
            "LinkedIn Marketing API version header in YYYYMM format. "
            "Value: a version string like 202509. "
            "Get it from the LinkedIn Marketing API versioning docs and keep it aligned with the approved API surface. "
            "Paste it into this setup field only if you need to override the default shipped version."
        ),
    },
]


class IntegrationLinkedinB2B:
    def __init__(
        self,
        rcx=None,
        ad_account_id: str = "",
        organization_id: str = "",
        linkedin_api_version: str = "202509",
    ):
        self.rcx = rcx
        self.ad_account_id = str(ad_account_id or "").strip()
        self.organization_id = str(organization_id or "").strip()
        self.linkedin_api_version = str(linkedin_api_version or "202509").strip()

    def _auth(self) -> Dict[str, Any]:
        # Same auth storage contract as fi_linkedin.py:
        # - provider name in Flexus auth layer: "linkedin"
        # - connected account payload location: rcx.external_auth["linkedin"]
        # - required value for runtime calls: token.access_token
        # This module does not own client_id/client_secret storage; our responsibility starts once
        # the platform auth layer already exposes the connected account here.
        return (self.rcx.external_auth.get("linkedin") or {}) if self.rcx else {}

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
            "auth_provider": "linkedin",
            "default_ad_account_id": self.ad_account_id,
            "default_organization_id": self.organization_id,
            "linkedin_api_version": self.linkedin_api_version,
            "products": [
                "Community Management API",
                "Advertising API",
                "Events Management API",
                "Lead Sync API",
                "Conversions API",
                "Matched Audiences API",
                "Audience Insights API",
                "Media Planning API",
                "Company Intelligence API",
            ],
            "has_access_token": bool(access_token),
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- This integration assumes official LinkedIn reviewed or qualified B2B access.\n"
            "- Many create/update methods accept args.body for full pass-through provider payloads.\n"
            "- Where LinkedIn docs expose only query-style resources, method ids normalize that shape into one call.\n"
        )

    def _headers(self, *, has_body: bool, restli_method: str = "") -> Dict[str, str]:
        access_token = self._access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Linkedin-Version": self.linkedin_api_version,
            "X-Restli-Protocol-Version": "2.0.0",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
        if restli_method:
            headers["X-RestLi-Method"] = restli_method
        return headers

    def _auth_missing(self, method_id: str) -> str:
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "AUTH_MISSING",
            "message": "Connect LinkedIn in workspace settings and ensure an access token is present.",
        }, indent=2, ensure_ascii=False)

    def _invalid_args(self, method_id: str, message: str) -> str:
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "INVALID_ARGS",
            "message": message,
        }, indent=2, ensure_ascii=False)

    def _docs_gap(self, method_id: str, message: str) -> str:
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "OFFICIAL_DOCS_GAP",
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
        logger.info("linkedin_b2b api error method=%s status=%s body=%s", method_id, status_code, body[:300])
        return json.dumps({
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": "PROVIDER_ERROR",
            "http_status": status_code,
            "detail": detail,
        }, indent=2, ensure_ascii=False)

    def _enc(self, value: Any) -> str:
        return quote(str(value), safe="")

    def _query(self, params: Dict[str, Any]) -> str:
        parts = []
        for key, value in params.items():
            if value is None or value == "":
                continue
            if isinstance(value, bool):
                value = "true" if value else "false"
            parts.append(f"{key}={self._enc(value)}")
        return "&".join(parts)

    def _with_query(self, path: str, params: Dict[str, Any]) -> str:
        query = self._query(params)
        return f"{path}?{query}" if query else path

    async def _request(
        self,
        method_id: str,
        http_method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        restli_method: str = "",
    ) -> str:
        url = _BASE_URL + path
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(has_body=False, restli_method=restli_method))
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(has_body=True, restli_method=restli_method), json=body)
                elif http_method == "PUT":
                    response = await client.put(url, headers=self._headers(has_body=True, restli_method=restli_method), json=body)
                elif http_method == "DELETE":
                    response = await client.delete(url, headers=self._headers(has_body=False, restli_method=restli_method))
                else:
                    return json.dumps({"ok": False, "error_code": "UNSUPPORTED_HTTP_METHOD"}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            logger.error("linkedin_b2b request failed", exc_info=e)
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "error_code": "HTTP_ERROR",
                "message": f"{type(e).__name__}: {e}",
            }, indent=2, ensure_ascii=False)

        if response.status_code >= 400:
            return self._provider_error(method_id, response.status_code, response.text)

        if response.status_code == 204 or not response.text.strip():
            return self._result(method_id, {"status": "success"})
        try:
            payload: Any = response.json()
        except json.JSONDecodeError:
            payload = response.text
        response_id = response.headers.get("x-restli-id") or response.headers.get("x-linkedin-id")
        if response_id:
            return self._result(method_id, {"id": response_id, "payload": payload})
        return self._result(method_id, payload)

    def _body(self, args: Dict[str, Any], required: bool = False) -> Dict[str, Any]:
        body = args.get("body")
        if isinstance(body, dict):
            return body
        if required:
            raise ValueError("body is required and must be an object for this method.")
        return {}

    def _patch_body(self, args: Dict[str, Any]) -> Dict[str, Any]:
        body = args.get("body")
        if isinstance(body, dict):
            return body
        patch_set = args.get("set")
        if isinstance(patch_set, dict) and patch_set:
            return {"patch": {"$set": patch_set}}
        raise ValueError("Provide body as a Rest.li patch object or set as a non-empty object.")

    def _pick(self, args: Dict[str, Any], key: str, default: str = "") -> str:
        return str(args.get(key, default)).strip()

    def _organization_id(self, args: Dict[str, Any], required: bool = False) -> str:
        value = self._pick(args, "organization_id", self.organization_id)
        if required and not value:
            raise ValueError("organization_id is required.")
        return value

    def _organization_urn(self, args: Dict[str, Any], required: bool = False) -> str:
        if self._pick(args, "organization_urn"):
            return self._pick(args, "organization_urn")
        organization_id = self._organization_id(args, required=required)
        return f"urn:li:organization:{organization_id}" if organization_id else ""

    def _ad_account_id(self, args: Dict[str, Any], required: bool = False) -> str:
        value = self._pick(args, "ad_account_id", self.ad_account_id)
        if required and not value:
            raise ValueError("ad_account_id is required.")
        return value

    def _ad_account_urn(self, args: Dict[str, Any], required: bool = False) -> str:
        if self._pick(args, "ad_account_urn"):
            return self._pick(args, "ad_account_urn")
        ad_account_id = self._ad_account_id(args, required=required)
        return f"urn:li:sponsoredAccount:{ad_account_id}" if ad_account_id else ""

    def _campaign_urn(self, args: Dict[str, Any], required: bool = False) -> str:
        if self._pick(args, "campaign_urn"):
            return self._pick(args, "campaign_urn")
        campaign_id = self._pick(args, "campaign_id")
        if required and not campaign_id:
            raise ValueError("campaign_id or campaign_urn is required.")
        return f"urn:li:sponsoredCampaign:{campaign_id}" if campaign_id else ""

    def _person_urn(self, args: Dict[str, Any], required: bool = False) -> str:
        person_urn = self._pick(args, "person_urn") or self._pick(args, "role_assignee") or self._pick(args, "user_urn")
        if required and not person_urn:
            raise ValueError("person_urn is required.")
        return person_urn

    def _social_target_urn(self, args: Dict[str, Any], required: bool = False) -> str:
        target_urn = self._pick(args, "target_urn") or self._pick(args, "entity_urn") or self._pick(args, "post_urn")
        if required and not target_urn:
            raise ValueError("target_urn is required.")
        return target_urn

    def _comment_id(self, args: Dict[str, Any], required: bool = False) -> str:
        comment_id = self._pick(args, "comment_id")
        if required and not comment_id:
            raise ValueError("comment_id is required.")
        return comment_id

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

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:  # noqa: C901
        try:
            if method_id == "linkedin_b2b.organizations.get.v1":
                organization_id = self._organization_id(args, required=True)
                return await self._request(method_id, "GET", f"/rest/organizations/{organization_id}")
            if method_id == "linkedin_b2b.organizations.search.v1":
                if self._pick(args, "vanity_name"):
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/organizations", {"q": "vanityName", "vanityName": self._pick(args, "vanity_name")}),
                    )
                if isinstance(args.get("ids"), list) and args.get("ids"):
                    ids = ",".join(str(x) for x in args.get("ids", []))
                    return await self._request(method_id, "GET", self._with_query("/rest/organizationsLookup", {"ids": f"List({ids})"}))
                raise ValueError("Provide vanity_name or ids for organization lookup.")
            if method_id == "linkedin_b2b.organization_acls.member_organizations.list.v1":
                person_urn = self._person_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationAcls", {
                        "q": "roleAssignee",
                        "roleAssignee": person_urn,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                        "state": self._pick(args, "state"),
                        "role": self._pick(args, "role"),
                    }),
                )
            if method_id == "linkedin_b2b.organization_acls.organization_members.list.v1":
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationAcls", {
                        "q": "organization",
                        "organization": organization_urn,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                        "state": self._pick(args, "state"),
                        "role": self._pick(args, "role"),
                    }),
                )
            if method_id == "linkedin_b2b.organization_posts.create.v1":
                return await self._request(method_id, "POST", "/rest/posts", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.organization_posts.get.v1":
                post_urn = self._social_target_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/posts/{self._enc(post_urn)}", {"viewContext": self._pick(args, "viewContext")}),
                )
            if method_id == "linkedin_b2b.organization_posts.list.v1":
                author = self._pick(args, "author") or self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/posts", {
                        "q": "author",
                        "author": author,
                        "viewContext": self._pick(args, "viewContext"),
                        "sortBy": self._pick(args, "sortBy"),
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.organization_posts.delete.v1":
                post_urn = self._social_target_urn(args, required=True)
                return await self._request(method_id, "DELETE", f"/rest/posts/{self._enc(post_urn)}")
            if method_id == "linkedin_b2b.comments.create.v1":
                target_urn = self._social_target_urn(args, required=True)
                return await self._request(method_id, "POST", f"/rest/socialActions/{self._enc(target_urn)}/comments", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.comments.get.v1":
                target_urn = self._social_target_urn(args, required=True)
                comment_id = self._comment_id(args, required=True)
                return await self._request(method_id, "GET", f"/rest/socialActions/{self._enc(target_urn)}/comments/{comment_id}")
            if method_id == "linkedin_b2b.comments.list.v1":
                target_urn = self._social_target_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/socialActions/{self._enc(target_urn)}/comments", {
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.comments.update.v1":
                target_urn = self._social_target_urn(args, required=True)
                comment_id = self._comment_id(args, required=True)
                actor = self._pick(args, "actor")
                if not actor:
                    raise ValueError("actor is required for comment update.")
                return await self._request(
                    method_id,
                    "POST",
                    self._with_query(f"/rest/socialActions/{self._enc(target_urn)}/comments/{comment_id}", {"actor": actor}),
                    body=self._body(args, required=True),
                )
            if method_id == "linkedin_b2b.comments.delete.v1":
                target_urn = self._social_target_urn(args, required=True)
                comment_id = self._comment_id(args, required=True)
                actor = self._pick(args, "actor")
                if not actor:
                    raise ValueError("actor is required for comment delete.")
                return await self._request(
                    method_id,
                    "DELETE",
                    self._with_query(f"/rest/socialActions/{self._enc(target_urn)}/comments/{comment_id}", {"actor": actor}),
                )
            if method_id == "linkedin_b2b.reactions.create.v1":
                actor = self._pick(args, "actor")
                if not actor:
                    raise ValueError("actor is required for reaction create.")
                return await self._request(
                    method_id,
                    "POST",
                    self._with_query("/rest/reactions", {"actor": actor}),
                    body=self._body(args, required=True),
                )
            if method_id == "linkedin_b2b.reactions.list.v1":
                entity_urn = self._social_target_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/reactions/(entity:{self._enc(entity_urn)})", {
                        "q": "entity",
                        "sort": self._pick(args, "sort"),
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.reactions.delete.v1":
                actor = self._pick(args, "actor")
                entity_urn = self._social_target_urn(args, required=True)
                if not actor:
                    raise ValueError("actor is required for reaction delete.")
                return await self._request(method_id, "DELETE", f"/rest/reactions/(actor:{self._enc(actor)},entity:{self._enc(entity_urn)})")
            if method_id == "linkedin_b2b.social_metadata.get.v1":
                entity_urn = self._social_target_urn(args, required=True)
                return await self._request(method_id, "GET", f"/rest/socialMetadata/{self._enc(entity_urn)}")
            if method_id == "linkedin_b2b.followers.get.v1":
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/networkSizes/{self._enc(organization_urn)}", {"edgeType": "COMPANY_FOLLOWED_BY_MEMBER"}),
                )
            if method_id == "linkedin_b2b.followers.stats.get.v1":
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationalEntityFollowerStatistics", {
                        "q": "organizationalEntity",
                        "organizationalEntity": organization_urn,
                        "timeIntervals": self._pick(args, "timeIntervals"),
                    }),
                )
            if method_id == "linkedin_b2b.page_analytics.get.v1":
                brand_urn = self._pick(args, "brand_urn")
                if brand_urn:
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/brandPageStatistics", {"q": "brand", "brand": brand_urn, "timeIntervals": self._pick(args, "timeIntervals")}),
                    )
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationPageStatistics", {
                        "q": "organization",
                        "organization": organization_urn,
                        "timeIntervals": self._pick(args, "timeIntervals"),
                    }),
                )
            if method_id == "linkedin_b2b.share_statistics.get.v1":
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationalEntityShareStatistics", {
                        "q": "organizationalEntity",
                        "organizationalEntity": organization_urn,
                        "timeIntervals": self._pick(args, "timeIntervals"),
                        "shares": self._pick(args, "shares"),
                        "ugcPosts": self._pick(args, "ugcPosts"),
                    }),
                )
            if method_id == "linkedin_b2b.video_analytics.get.v1":
                entity_urn = self._social_target_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/videoAnalytics", {
                        "q": "entity",
                        "entity": entity_urn,
                        "type": self._pick(args, "type", "VIDEO_VIEW"),
                        "aggregation": self._pick(args, "aggregation"),
                        "timeRange": self._pick(args, "timeRange"),
                    }),
                )
            if method_id == "linkedin_b2b.member_profile_analytics.get.v1":
                if self._pick(args, "dateRange"):
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/memberFollowersCount", {"q": "dateRange", "dateRange": self._pick(args, "dateRange")}),
                    )
                return await self._request(method_id, "GET", self._with_query("/rest/memberFollowersCount", {"q": "me"}))
            if method_id == "linkedin_b2b.member_post_analytics.get.v1":
                if self._pick(args, "entity"):
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/memberCreatorPostAnalytics", {
                            "q": "entity",
                            "entity": self._pick(args, "entity"),
                            "queryType": self._pick(args, "queryType"),
                            "aggregation": self._pick(args, "aggregation"),
                            "dateRange": self._pick(args, "dateRange"),
                        }),
                    )
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/memberCreatorPostAnalytics", {
                        "q": "me",
                        "queryType": self._pick(args, "queryType"),
                        "aggregation": self._pick(args, "aggregation"),
                        "dateRange": self._pick(args, "dateRange"),
                    }),
                )
            if method_id == "linkedin_b2b.mentions.people.search.v1":
                organization_urn = self._organization_urn(args, required=True)
                vanity_url = self._pick(args, "vanity_url")
                if vanity_url:
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/vanityUrl", {
                            "q": "vanityUrlAsOrganization",
                            "vanityUrl": vanity_url,
                            "organization": organization_urn,
                        }),
                    )
                keywords = self._pick(args, "keywords")
                if not keywords:
                    raise ValueError("keywords is required unless vanity_url is provided.")
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/peopleTypeahead", {
                        "q": "organizationFollowers",
                        "keywords": keywords,
                        "organization": organization_urn,
                    }),
                )
            if method_id == "linkedin_b2b.notifications.social_actions.list.v1":
                organization_urn = self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/organizationalEntityNotifications", {
                        "q": "criteria",
                        "organizationalEntity": organization_urn,
                        "actions": self._pick(args, "actions"),
                        "sourcePost": self._pick(args, "sourcePost"),
                        "timeRange.start": self._pick(args, "timeRange.start"),
                        "timeRange.end": self._pick(args, "timeRange.end"),
                    }),
                )
            if method_id == "linkedin_b2b.ad_accounts.get.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(method_id, "GET", f"/rest/adAccounts/{ad_account_id}")
            if method_id == "linkedin_b2b.ad_accounts.list.v1":
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/adAccounts", {
                        "q": "search",
                        "search": self._pick(args, "search"),
                        "pageSize": self._pick(args, "pageSize"),
                        "pageToken": self._pick(args, "pageToken"),
                    }),
                )
            if method_id == "linkedin_b2b.ad_account_users.get.v1":
                account_urn = self._ad_account_urn(args, required=True)
                user_urn = self._person_urn(args, required=True)
                return await self._request(method_id, "GET", f"/rest/adAccountUsers/(account:{self._enc(account_urn)},user:{self._enc(user_urn)})")
            if method_id == "linkedin_b2b.ad_account_users.list.v1":
                account_urn = self._ad_account_urn(args)
                if account_urn:
                    return await self._request(
                        method_id,
                        "GET",
                        self._with_query("/rest/adAccountUsers", {"q": "accounts", "accounts": account_urn}),
                    )
                return await self._request(method_id, "GET", self._with_query("/rest/adAccountUsers", {"q": "authenticatedUser"}))
            if method_id == "linkedin_b2b.ad_account_users.create.v1":
                account_urn = self._ad_account_urn(args, required=True)
                user_urn = self._person_urn(args, required=True)
                body = self._body(args) or {"account": account_urn, "user": user_urn, "role": self._pick(args, "role")}
                if not body.get("role"):
                    raise ValueError("role is required for ad account user create.")
                return await self._request(method_id, "PUT", f"/rest/adAccountUsers/(account:{self._enc(account_urn)},user:{self._enc(user_urn)})", body=body)
            if method_id == "linkedin_b2b.ad_account_users.update.v1":
                account_urn = self._ad_account_urn(args, required=True)
                user_urn = self._person_urn(args, required=True)
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/adAccountUsers/(account:{self._enc(account_urn)},user:{self._enc(user_urn)})",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.ad_account_users.delete.v1":
                account_urn = self._ad_account_urn(args, required=True)
                user_urn = self._person_urn(args, required=True)
                return await self._request(method_id, "DELETE", f"/rest/adAccountUsers/(account:{self._enc(account_urn)},user:{self._enc(user_urn)})")
            if method_id == "linkedin_b2b.ad_campaign_groups.create.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(method_id, "POST", f"/rest/adAccounts/{ad_account_id}/adCampaignGroups", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.ad_campaign_groups.get.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                campaign_group_id = self._pick(args, "campaign_group_id")
                if not campaign_group_id:
                    raise ValueError("campaign_group_id is required.")
                return await self._request(method_id, "GET", f"/rest/adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}")
            if method_id == "linkedin_b2b.ad_campaign_groups.list.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/adAccounts/{ad_account_id}/adCampaignGroups", {
                        "q": "search",
                        "search": self._pick(args, "search"),
                        "pageSize": self._pick(args, "pageSize"),
                        "pageToken": self._pick(args, "pageToken"),
                    }),
                )
            if method_id == "linkedin_b2b.ad_campaign_groups.update.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                campaign_group_id = self._pick(args, "campaign_group_id")
                if not campaign_group_id:
                    raise ValueError("campaign_group_id is required.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/adAccounts/{ad_account_id}/adCampaignGroups/{campaign_group_id}",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.ad_campaigns.create.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(method_id, "POST", f"/rest/adAccounts/{ad_account_id}/adCampaigns", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.ad_campaigns.get.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                campaign_id = self._pick(args, "campaign_id")
                if not campaign_id:
                    raise ValueError("campaign_id is required.")
                return await self._request(method_id, "GET", f"/rest/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}")
            if method_id == "linkedin_b2b.ad_campaigns.list.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/adAccounts/{ad_account_id}/adCampaigns", {
                        "q": "search",
                        "search": self._pick(args, "search"),
                        "pageSize": self._pick(args, "pageSize"),
                        "pageToken": self._pick(args, "pageToken"),
                    }),
                )
            if method_id == "linkedin_b2b.ad_campaigns.update.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                campaign_id = self._pick(args, "campaign_id")
                if not campaign_id:
                    raise ValueError("campaign_id is required.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.creatives.create.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                action = self._pick(args, "action")
                path = f"/rest/adAccounts/{ad_account_id}/creatives?action={self._enc(action)}" if action else f"/rest/adAccounts/{ad_account_id}/creatives"
                return await self._request(method_id, "POST", path, body=self._body(args, required=True))
            if method_id == "linkedin_b2b.creatives.get.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                creative_urn = self._pick(args, "creative_urn") or self._pick(args, "creative_id")
                if not creative_urn:
                    raise ValueError("creative_urn or creative_id is required.")
                return await self._request(method_id, "GET", f"/rest/adAccounts/{ad_account_id}/creatives/{self._enc(creative_urn)}")
            if method_id == "linkedin_b2b.creatives.list.v1":
                ad_account_id = self._ad_account_id(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query(f"/rest/adAccounts/{ad_account_id}/creatives", {
                        "q": "criteria",
                        "campaigns": self._pick(args, "campaigns"),
                        "contentReferences": self._pick(args, "contentReferences"),
                        "creatives": self._pick(args, "creatives"),
                        "intendedStatuses": self._pick(args, "intendedStatuses"),
                        "isTestAccount": self._pick(args, "isTestAccount"),
                        "leadgenCreativeCallToActionDestinations": self._pick(args, "leadgenCreativeCallToActionDestinations"),
                        "pageSize": self._pick(args, "pageSize"),
                        "pageToken": self._pick(args, "pageToken"),
                    }),
                )
            if method_id in {"linkedin_b2b.ad_analytics.get.v1", "linkedin_b2b.ad_analytics.query.v1"}:
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/adAnalytics", {
                        "q": self._pick(args, "q", "analytics"),
                        "pivot": self._pick(args, "pivot"),
                        "pivots": self._pick(args, "pivots"),
                        "timeGranularity": self._pick(args, "timeGranularity"),
                        "dateRange": self._pick(args, "dateRange"),
                        "campaigns": self._pick(args, "campaigns"),
                        "accounts": self._pick(args, "accounts"),
                        "campaignGroups": self._pick(args, "campaignGroups"),
                        "creatives": self._pick(args, "creatives"),
                        "shares": self._pick(args, "shares"),
                        "fields": self._pick(args, "fields"),
                        "account": self._pick(args, "account"),
                    }),
                )
            if method_id == "linkedin_b2b.audience_counts.get.v1":
                targeting_criteria = self._pick(args, "targetingCriteria")
                if not targeting_criteria:
                    raise ValueError("targetingCriteria is required.")
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/audienceCounts", {"q": "targetingCriteriaV2", "targetingCriteria": targeting_criteria}),
                )
            if method_id == "linkedin_b2b.targeting_facets.list.v1":
                return await self._request(method_id, "GET", "/rest/adTargetingFacets")
            if method_id == "linkedin_b2b.targeting_entities.list.v1":
                query_kind = self._pick(args, "query_kind", "adTargetingFacet")
                params = {"q": query_kind}
                if query_kind == "adTargetingFacet":
                    params["facet"] = self._pick(args, "facet")
                elif query_kind == "typeahead":
                    params["facet"] = self._pick(args, "facet")
                    params["query"] = self._pick(args, "query")
                elif query_kind == "urns":
                    params["urns"] = self._pick(args, "urns")
                else:
                    raise ValueError("query_kind must be adTargetingFacet, typeahead, or urns.")
                params["locale"] = self._pick(args, "locale")
                params["queryVersion"] = self._pick(args, "queryVersion")
                return await self._request(method_id, "GET", self._with_query("/rest/adTargetingEntities", params))
            if method_id == "linkedin_b2b.lead_forms.get.v1":
                lead_form_id = self._pick(args, "lead_form_id")
                if not lead_form_id:
                    raise ValueError("lead_form_id is required.")
                return await self._request(method_id, "GET", f"/rest/leadForms/{lead_form_id}")
            if method_id == "linkedin_b2b.lead_forms.list.v1":
                owner = self._pick(args, "owner") or self._ad_account_urn(args) or self._organization_urn(args)
                if not owner:
                    raise ValueError("owner or ad_account_id or organization_id is required.")
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/leadForms", {
                        "q": "owner",
                        "owner": owner,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.lead_forms.create.v1":
                return await self._request(method_id, "POST", "/rest/leadForms", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.lead_forms.update.v1":
                lead_form_id = self._pick(args, "lead_form_id")
                if not lead_form_id:
                    raise ValueError("lead_form_id is required.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/leadForms/{lead_form_id}",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.events.create.v1":
                return await self._request(method_id, "POST", "/rest/events", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.events.get.v1":
                event_id = self._pick(args, "event_id")
                if not event_id:
                    raise ValueError("event_id is required.")
                return await self._request(method_id, "GET", f"/rest/events/{event_id}")
            if method_id == "linkedin_b2b.events.update.v1":
                event_id = self._pick(args, "event_id")
                if not event_id:
                    raise ValueError("event_id is required.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/events/{event_id}",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.events.list_by_organizer.v1":
                organizer = self._pick(args, "organizer") or self._organization_urn(args)
                if not organizer:
                    raise ValueError("organizer or organization_id is required.")
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/events", {
                        "q": "eventsByOrganizer",
                        "organizer": organizer,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                        "excludeCancelled": self._pick(args, "excludeCancelled"),
                        "timeBasedFilter": self._pick(args, "timeBasedFilter"),
                        "entryCriteria": self._pick(args, "entryCriteria"),
                        "sortOrder": self._pick(args, "sortOrder"),
                    }),
                )
            if method_id == "linkedin_b2b.events.list_leadgen_by_organizer.v1":
                organizer = self._pick(args, "organizer") or self._organization_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/events", {
                        "q": "organizerLeadGenFormEnabledEvents",
                        "organizer": organizer,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.events.register_background_upload.v1":
                return await self._request(method_id, "POST", "/rest/assets?action=registerUpload", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.lead_sync.forms.get.v1":
                lead_form_id = self._pick(args, "lead_form_id")
                if not lead_form_id:
                    raise ValueError("lead_form_id is required.")
                return await self._request(method_id, "GET", f"/rest/leadForms/{lead_form_id}")
            if method_id == "linkedin_b2b.lead_sync.forms.list.v1":
                owner = self._pick(args, "owner") or self._ad_account_urn(args) or self._organization_urn(args)
                if not owner:
                    raise ValueError("owner or ad_account_id or organization_id is required.")
                return await self._request(method_id, "GET", self._with_query("/rest/leadForms", {"q": "owner", "owner": owner, "start": self._pick(args, "start"), "count": self._pick(args, "count")}))
            if method_id == "linkedin_b2b.lead_sync.responses.get.v1":
                lead_id = self._pick(args, "lead_id")
                if not lead_id:
                    raise ValueError("lead_id is required.")
                return await self._request(method_id, "GET", f"/rest/leadFormResponses/{lead_id}")
            if method_id == "linkedin_b2b.lead_sync.responses.list.v1":
                owner = self._pick(args, "owner") or self._ad_account_urn(args) or self._organization_urn(args)
                if not owner:
                    raise ValueError("owner or ad_account_id or organization_id is required.")
                lead_type = self._pick(args, "leadType")
                if not lead_type:
                    raise ValueError("leadType is required.")
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/leadFormResponses", {
                        "q": "owner",
                        "owner": owner,
                        "leadType": f"(leadType:{lead_type})",
                        "versionedLeadGenFormUrn": self._pick(args, "versionedLeadGenFormUrn"),
                        "associatedEntity": self._pick(args, "associatedEntity"),
                        "submittedAtTimeRange": self._pick(args, "submittedAtTimeRange"),
                        "limitedToTestLeads": self._pick(args, "limitedToTestLeads"),
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                    }),
                )
            if method_id == "linkedin_b2b.lead_sync.notifications.create.v1":
                return await self._request(method_id, "POST", "/rest/leadNotifications", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.lead_sync.notifications.get.v1":
                notification_id = self._pick(args, "notification_id")
                if not notification_id:
                    raise ValueError("notification_id is required.")
                return await self._request(method_id, "GET", f"/rest/leadNotifications/{notification_id}")
            if method_id == "linkedin_b2b.lead_sync.notifications.delete.v1":
                notification_id = self._pick(args, "notification_id")
                if not notification_id:
                    raise ValueError("notification_id is required.")
                return await self._request(method_id, "DELETE", f"/rest/leadNotifications/{notification_id}")
            if method_id == "linkedin_b2b.conversions.create.v1":
                auto_association_type = self._pick(args, "autoAssociationType")
                path = f"/rest/conversions?autoAssociationType={self._enc(auto_association_type)}" if auto_association_type else "/rest/conversions"
                return await self._request(method_id, "POST", path, body=self._body(args, required=True))
            if method_id == "linkedin_b2b.conversions.get.v1":
                conversion_id = self._pick(args, "conversion_id")
                if not conversion_id:
                    raise ValueError("conversion_id is required.")
                account = self._pick(args, "account") or self._ad_account_urn(args, required=True)
                return await self._request(method_id, "GET", self._with_query(f"/rest/conversions/{conversion_id}", {"account": account}))
            if method_id == "linkedin_b2b.conversions.list.v1":
                account = self._pick(args, "account") or self._ad_account_urn(args, required=True)
                return await self._request(method_id, "GET", self._with_query("/rest/conversions", {"q": "account", "account": account}))
            if method_id == "linkedin_b2b.conversions.associate_campaigns.v1":
                if isinstance(args.get("ids"), list) and args.get("ids"):
                    ids = ",".join(str(x) for x in args.get("ids", []))
                    body = self._body(args)
                    return await self._request(
                        method_id,
                        "PUT",
                        self._with_query("/rest/campaignConversions", {"ids": f"List({ids})"}),
                        body=body,
                        restli_method="BATCH_UPDATE",
                    )
                campaign_urn = self._campaign_urn(args, required=True)
                conversion_urn = self._pick(args, "conversion_urn")
                if not conversion_urn:
                    raise ValueError("conversion_urn is required.")
                return await self._request(
                    method_id,
                    "PUT",
                    f"/rest/campaignConversions/(campaign:{self._enc(campaign_urn)},conversion:{self._enc(conversion_urn)})",
                    body=self._body(args),
                )
            if method_id == "linkedin_b2b.conversion_events.upload.v1":
                body = self._body(args, required=True)
                restli_method = "BATCH_CREATE" if isinstance(body.get("elements"), list) else ""
                return await self._request(method_id, "POST", "/rest/conversionEvents", body=body, restli_method=restli_method)
            if method_id == "linkedin_b2b.dmp_segments.create.v1":
                return await self._request(method_id, "POST", "/rest/dmpSegments", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.dmp_segments.get.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                return await self._request(method_id, "GET", f"/rest/dmpSegments/{dmp_segment_id}")
            if method_id == "linkedin_b2b.dmp_segments.list.v1":
                account = self._ad_account_urn(args, required=True)
                return await self._request(method_id, "GET", self._with_query("/rest/dmpSegments", {"q": "account", "account": account}))
            if method_id == "linkedin_b2b.dmp_segments.update.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                return await self._request(
                    method_id,
                    "POST",
                    f"/rest/dmpSegments/{dmp_segment_id}",
                    body=self._patch_body(args),
                    restli_method="PARTIAL_UPDATE",
                )
            if method_id == "linkedin_b2b.dmp_segment_users.upload.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                body = self._body(args, required=True)
                restli_method = "BATCH_CREATE" if isinstance(body.get("elements"), list) else ""
                return await self._request(method_id, "POST", f"/rest/dmpSegments/{dmp_segment_id}/users", body=body, restli_method=restli_method)
            if method_id == "linkedin_b2b.dmp_segment_companies.upload.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                body = self._body(args, required=True)
                restli_method = "BATCH_CREATE" if isinstance(body.get("elements"), list) else ""
                return await self._request(method_id, "POST", f"/rest/dmpSegments/{dmp_segment_id}/companies", body=body, restli_method=restli_method)
            if method_id == "linkedin_b2b.dmp_segment_destinations.list.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                return await self._request(method_id, "GET", f"/rest/dmpSegments/{dmp_segment_id}/destinations")
            if method_id == "linkedin_b2b.dmp_segment_list_uploads.get.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                list_upload_id = self._pick(args, "list_upload_id")
                if not dmp_segment_id or not list_upload_id:
                    raise ValueError("dmp_segment_id and list_upload_id are required.")
                return await self._request(method_id, "GET", f"/rest/dmpSegments/{dmp_segment_id}/listUploads/{list_upload_id}")
            if method_id == "linkedin_b2b.ad_segments.list.v1":
                account = self._ad_account_urn(args, required=True)
                return await self._request(method_id, "GET", self._with_query("/rest/adSegments", {"q": "accounts", "accounts": f"List({account})", "start": self._pick(args, "start"), "count": self._pick(args, "count")}))
            if method_id == "linkedin_b2b.website_retargeting.list.v1":
                account = self._ad_account_urn(args, required=True)
                return await self._request(method_id, "GET", self._with_query("/rest/adPageSets", {"q": "account", "account": account}))
            if method_id == "linkedin_b2b.predictive_audiences.list.v1":
                dmp_segment_id = self._pick(args, "dmp_segment_id")
                predictive_audience_id = self._pick(args, "predictive_audience_id")
                if not dmp_segment_id:
                    raise ValueError("dmp_segment_id is required.")
                if predictive_audience_id:
                    return await self._request(method_id, "GET", f"/rest/dmpSegments/{dmp_segment_id}/businessObjectiveBasedAudiences/{predictive_audience_id}")
                return self._docs_gap(method_id, "Official docs confirm get-by-id on businessObjectiveBasedAudiences. A collection list endpoint was not confidently documented.")
            if method_id == "linkedin_b2b.audience_insights.query.v1":
                return await self._request(method_id, "POST", "/rest/targetingAudienceInsights?action=audienceInsights", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.media_planning.forecast_reach.v1":
                return await self._request(method_id, "POST", "/rest/mediaPlanning?action=forecastReaches", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.media_planning.forecast_impressions.v1":
                return await self._request(method_id, "POST", "/rest/mediaPlanning?action=forecastImpressions", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.media_planning.forecast_leads.v1":
                return await self._request(method_id, "POST", "/rest/mediaPlanning?action=forecastLeads", body=self._body(args, required=True))
            if method_id == "linkedin_b2b.account_intelligence.get.v1":
                account = self._pick(args, "account") or self._ad_account_urn(args, required=True)
                return await self._request(
                    method_id,
                    "GET",
                    self._with_query("/rest/accountIntelligence", {
                        "q": "account",
                        "account": account,
                        "start": self._pick(args, "start"),
                        "count": self._pick(args, "count"),
                        "filterCriteria": self._pick(args, "filterCriteria"),
                    }),
                )
        except ValueError as e:
            return self._invalid_args(method_id, str(e))
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)
