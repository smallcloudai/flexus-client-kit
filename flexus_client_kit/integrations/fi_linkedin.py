import json
import logging
from typing import Any, Dict, Optional

import httpx

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("linkedin")
INTEGRATION_METADATA = {
    "provider": "linkedin",
    "auth_kind": "oauth2",
    "env_keys": [],
    "supports_ping": False,
}


PROVIDER_NAME = "linkedin"
METHOD_IDS = [
    "linkedin.auth.userinfo.get.v1",
    "linkedin.posts.create_text.v1",
    "linkedin.posts.create_article.v1",
    "linkedin.assets.register_image_upload.v1",
    "linkedin.assets.register_video_upload.v1",
    "linkedin.posts.create_image.v1",
    "linkedin.posts.create_video.v1",
]

_BASE_URL = "https://api.linkedin.com"
_TIMEOUT = 30.0

LINKEDIN_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="linkedin",
    description="LinkedIn open permissions: OIDC userinfo and member posting.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Use help, status, list_methods, or call."},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

# Open-permissions LinkedIn does not need per-bot setup fields.
# Credentials are not pasted into this file or bot setup.
# They must already exist in the platform auth provider named "linkedin".
# Required provider-side values are:
# - client_id: LinkedIn app Client ID from developer.linkedin.com
# - client_secret: LinkedIn app Client Secret from developer.linkedin.com
# - redirect_uri: the Flexus OAuth callback URL configured in the platform auth layer
# - scopes: at minimum openid, profile, email, w_member_social
# After user OAuth completes, Flexus must store the connected account under
# rcx.external_auth["linkedin"], with token.access_token populated.
# Optional refresh flow data, if available in the auth layer, also belongs there.
LINKEDIN_SETUP_SCHEMA = []


class IntegrationLinkedIn:
    def __init__(self, fclient=None, rcx=None, ad_account_id=""):
        self.fclient = fclient
        self.rcx = rcx
        self.ad_account_id = ad_account_id

    def _auth(self) -> Dict[str, Any]:
        # This integration only reads already-connected OAuth data.
        # Where to paste values:
        # - app-level keys such as client_id/client_secret belong in the platform auth provider "linkedin"
        # - user-level access tokens belong in the connected external auth record for provider "linkedin"
        # Expected token shape:
        # {
        #   "token": {
        #     "access_token": "...",
        #     "refresh_token": "...",   # optional, if your auth layer supports refresh
        #   }
        # }
        # Legacy fallback oauth_token is still accepted to keep the read path simple.
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
            "products": [
                "Sign in with LinkedIn using OpenID Connect",
                "Share on LinkedIn",
            ],
            "scopes_expected": ["openid", "profile", "email", "w_member_social"],
            "has_access_token": bool(access_token),
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- auth.userinfo.get returns OIDC userinfo from /v2/userinfo\n"
            "- register_*_upload returns uploadUrl + asset for a later binary upload step\n"
            "- create_image/create_video require an already uploaded asset URN\n"
        )

    def _headers(self, *, has_body: bool) -> Dict[str, str]:
        access_token = self._access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        if has_body:
            headers["Content-Type"] = "application/json"
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
        logger.info("linkedin api error method=%s status=%s body=%s", method_id, status_code, body[:300])
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
        body: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = _BASE_URL + path
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                if http_method == "GET":
                    response = await client.get(url, headers=self._headers(has_body=False))
                elif http_method == "POST":
                    response = await client.post(url, headers=self._headers(has_body=True), json=body)
                else:
                    return json.dumps({"ok": False, "error_code": "UNSUPPORTED_HTTP_METHOD"}, indent=2, ensure_ascii=False)
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "provider": PROVIDER_NAME, "method_id": method_id, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
        except (httpx.HTTPError, ValueError) as e:
            logger.error("linkedin request failed", exc_info=e)
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

    def _build_share_payload(self, args: Dict[str, Any], media_category: str) -> Dict[str, Any]:
        author = str(args.get("author", "")).strip()
        text = str(args.get("text", "") or args.get("commentary", "")).strip()
        visibility = str(args.get("visibility", "PUBLIC")).strip().upper()
        if not author:
            raise ValueError("author is required and must be a Person URN such as urn:li:person:123.")
        if not text:
            raise ValueError("text is required.")

        share_content: Dict[str, Any] = {
            "shareCommentary": {"text": text},
            "shareMediaCategory": media_category,
        }
        if media_category == "ARTICLE":
            original_url = str(args.get("original_url", "") or args.get("url", "")).strip()
            if not original_url:
                raise ValueError("original_url is required for article posts.")
            share_content["media"] = [{
                "status": "READY",
                "originalUrl": original_url,
                **({"title": {"text": str(args.get("title", "")).strip()}} if str(args.get("title", "")).strip() else {}),
                **({"description": {"text": str(args.get("description", "")).strip()}} if str(args.get("description", "")).strip() else {}),
            }]
        if media_category in {"IMAGE", "VIDEO"}:
            asset = str(args.get("asset", "")).strip()
            if not asset:
                raise ValueError("asset is required for image/video posts. Register and upload media first.")
            share_content["media"] = [{
                "status": "READY",
                "media": asset,
                **({"title": {"text": str(args.get("title", "")).strip()}} if str(args.get("title", "")).strip() else {}),
                **({"description": {"text": str(args.get("description", "")).strip()}} if str(args.get("description", "")).strip() else {}),
            }]

        return {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": share_content,
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility,
            },
        }

    def _build_register_upload_payload(self, args: Dict[str, Any], recipe_suffix: str) -> Dict[str, Any]:
        owner = str(args.get("owner", "")).strip()
        if not owner:
            raise ValueError("owner is required and must be a Person URN such as urn:li:person:123.")
        return {
            "registerUploadRequest": {
                "recipes": [f"urn:li:digitalmediaRecipe:feedshare-{recipe_suffix}"],
                "owner": owner,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        try:
            if method_id == "linkedin.auth.userinfo.get.v1":
                return await self._request(method_id, "GET", "/v2/userinfo")
            if method_id == "linkedin.assets.register_image_upload.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/assets?action=registerUpload",
                    body=self._build_register_upload_payload(args, "image"),
                )
            if method_id == "linkedin.assets.register_video_upload.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/assets?action=registerUpload",
                    body=self._build_register_upload_payload(args, "video"),
                )
            if method_id == "linkedin.posts.create_text.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/ugcPosts",
                    body=self._build_share_payload(args, "NONE"),
                )
            if method_id == "linkedin.posts.create_article.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/ugcPosts",
                    body=self._build_share_payload(args, "ARTICLE"),
                )
            if method_id == "linkedin.posts.create_image.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/ugcPosts",
                    body=self._build_share_payload(args, "IMAGE"),
                )
            if method_id == "linkedin.posts.create_video.v1":
                return await self._request(
                    method_id,
                    "POST",
                    "/v2/ugcPosts",
                    body=self._build_share_payload(args, "VIDEO"),
                )
        except ValueError as e:
            return self._invalid_args(method_id, str(e))
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)
