from __future__ import annotations
import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional, TYPE_CHECKING
import httpx
from .exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookTimeoutError,
    parse_api_error,
)
from .utils import validate_ad_account_id
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
                    response = await client.delete(url, headers=self._headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                if response.status_code != 200:
                    error = await parse_api_error(response)
                    raise error
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
        from flexus_client_kit import ckit_client
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                ckit_client.gql.gql("""
                    query GetFacebookToken($fuser_id: String!, $ws_id: String!, $provider: String!) {
                        external_auth_token(
                            fuser_id: $fuser_id
                            ws_id: $ws_id
                            provider: $provider
                        ) {
                            access_token
                            expires_at
                            token_type
                        }
                    }
                """),
                variable_values={
                    "fuser_id": self.rcx.persona.owner_fuser_id,
                    "ws_id": self.rcx.persona.ws_id,
                    "provider": "facebook",
                },
            )
        token_data = result.get("external_auth_token")
        if not token_data:
            raise ValueError("No Facebook OAuth connection found")
        access_token = token_data.get("access_token", "")
        if not access_token:
            raise ValueError("Facebook OAuth exists but has no access token")
        expires_at = token_data.get("expires_at")
        if expires_at and expires_at < time.time():
            raise ValueError("Facebook token expired, please reconnect")
        logger.info("Facebook token retrieved for %s", self.rcx.persona.persona_id)
        return access_token
    async def _prompt_oauth_connection(self) -> str:
        web_url = os.getenv("FLEXUS_WEB_URL", "http://localhost:3000")
        thread_id = getattr(self.rcx, 'thread_id', None)
        if thread_id:
            connect_url = f"{web_url}/profile?connect=facebook&redirect_path=/chat/{thread_id}"
        else:
            connect_url = f"{web_url}/profile?connect=facebook"
        return f"""Facebook authorization required.
Please connect your Facebook account via the Profile page:
{connect_url}
After connecting, try your request again.
Note: You'll need:
- Facebook Business Manager account
- Access to an Ad Account (starts with act_...)
- Proper permissions (ads_management, ads_read, read_insights)"""
