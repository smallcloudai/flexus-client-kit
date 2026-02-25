from __future__ import annotations
import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

import httpx

from flexus_client_kit.integrations.facebook.exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookTimeoutError,
    parse_api_error,
)
from flexus_client_kit.integrations.facebook.utils import validate_ad_account_id

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

logger = logging.getLogger("facebook.client")

API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0


class FacebookAdsClient:
    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
    ):
        self.fclient = fclient
        self.rcx = rcx
        self._ad_account_id = ""
        if ad_account_id:
            self._ad_account_id = validate_ad_account_id(ad_account_id)
        self._access_token: str = ""
        self._headers: Dict[str, str] = {}

    @property
    def ad_account_id(self) -> str:
        return self._ad_account_id

    @ad_account_id.setter
    def ad_account_id(self, value: str) -> None:
        if value:
            self._ad_account_id = validate_ad_account_id(value)
        else:
            self._ad_account_id = ""

    @property
    def is_test_mode(self) -> bool:
        return self.rcx.running_test_scenario

    @property
    def access_token(self) -> str:
        return self._access_token

    async def ensure_auth(self) -> Optional[str]:
        try:
            if self.is_test_mode:
                return None
            if not self._access_token:
                self._access_token = await self._fetch_token()
            self._headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
            return None
        except Exception as e:
            logger.info(f"Failed to get Facebook token: {e}")
            return await self._prompt_oauth_connection()

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        auth_error = await self.ensure_auth()
        if auth_error:
            raise FacebookAuthError(auth_error)
        url = f"{API_BASE}/{API_VERSION}/{endpoint}"

        async def make_request() -> Dict[str, Any]:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, params=params, headers=self._headers, timeout=timeout)
                elif method == "POST":
                    if form_data:
                        response = await client.post(url, data=form_data, timeout=timeout)
                    else:
                        response = await client.post(url, json=data, headers=self._headers, timeout=timeout)
                elif method == "DELETE":
                    response = await client.delete(url, json=data, headers=self._headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                return response.json()

        return await self._retry_with_backoff(make_request)

    async def _retry_with_backoff(
        self,
        func,
        max_retries: int = MAX_RETRIES,
        initial_delay: float = INITIAL_RETRY_DELAY,
    ) -> Dict[str, Any]:
        last_exception = None
        for attempt in range(max_retries):
            try:
                return await func()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt == max_retries - 1:
                    raise FacebookTimeoutError(DEFAULT_TIMEOUT)
                delay = initial_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}")
                await asyncio.sleep(delay)
            except FacebookAPIError as e:
                if e.is_rate_limit:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
                    delay = initial_delay * (2 ** attempt) * 2
                    logger.warning(f"Rate limit hit, retry {attempt + 1}/{max_retries} after {delay}s")
                    await asyncio.sleep(delay)
                else:
                    raise
        if last_exception:
            raise last_exception
        raise FacebookAPIError(500, "Unexpected retry loop exit")


    async def _fetch_token(self) -> str:
        facebook_auth = self.rcx.external_auth.get("facebook") or {}
        token_obj = facebook_auth.get("token") or {}
        access_token = token_obj.get("access_token", "")
        if not access_token:
            raise ValueError("No Facebook OAuth connection found")
        logger.info("Facebook token retrieved for %s", self.rcx.persona.owner_fuser_id)
        return access_token


    async def _prompt_oauth_connection(self) -> str:
        from flexus_client_kit import ckit_client
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                ckit_client.gql.gql("""
                    query GetFacebookToken($fuser_id: String!, $ws_id: String!, $provider: String!, $scopes: [String!]!) {
                        external_auth_token(
                            fuser_id: $fuser_id
                            ws_id: $ws_id
                            provider: $provider
                            scopes: $scopes
                        )
                    }
                """),
                variable_values={
                    "fuser_id": self.rcx.persona.owner_fuser_id,
                    "ws_id": self.rcx.persona.ws_id,
                    "provider": "facebook",
                    "scopes": ["ads_management", "ads_read", "business_management", "pages_manage_ads"],
                },
            ),
        auth_url = result.get("external_auth_token", "")
        return f"""Facebook authorization required.

Click this link to connect your Facebook account:

{auth_url}

After authorizing, return here and try your request again.

Requirements:
- Facebook Business Manager account
- Access to an Ad Account (starts with act_...)
"""
