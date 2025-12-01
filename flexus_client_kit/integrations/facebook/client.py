"""
Facebook Ads API - HTTP Client

Provides authenticated HTTP client for Facebook Graph API with retry logic.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

import httpx

from .exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookRateLimitError,
    FacebookTimeoutError,
    parse_api_error,
)
from .utils import validate_ad_account_id

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

logger = logging.getLogger("facebook.client")

# Facebook Graph API configuration
API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0


class FacebookAdsClient:
    """
    HTTP client for Facebook Marketing API.

    Handles OAuth token retrieval, request signing, retry logic,
    and test mode support.

    Usage:
        client = FacebookAdsClient(fclient, rcx, "act_123456")
        await client.ensure_auth()
        response = await client.get("me/adaccounts", params={"fields": "id,name"})
    """

    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
    ):
        """
        Initialize Facebook Ads client.

        Args:
            fclient: Flexus client for backend calls
            rcx: Robot context with persona and thread info
            ad_account_id: Default ad account ID (can be empty, set per-request)
        """
        self.fclient = fclient
        self.rcx = rcx
        self._ad_account_id = ""
        if ad_account_id:
            self._ad_account_id = validate_ad_account_id(ad_account_id)

        self._access_token: str = ""
        self._headers: Dict[str, str] = {}
        self._problems: list[str] = []

    @property
    def ad_account_id(self) -> str:
        """Current ad account ID."""
        return self._ad_account_id

    @ad_account_id.setter
    def ad_account_id(self, value: str) -> None:
        """Set ad account ID with validation."""
        if value:
            self._ad_account_id = validate_ad_account_id(value)
        else:
            self._ad_account_id = ""

    @property
    def is_test_mode(self) -> bool:
        """Check if running in test scenario mode."""
        return self.rcx.running_test_scenario

    @property
    def access_token(self) -> str:
        """Current access token (empty if not authenticated)."""
        return self._access_token

    @property
    def problems(self) -> list[str]:
        """List of problems encountered during operations."""
        return self._problems

    def add_problem(self, problem: str) -> None:
        """Record a problem encountered during operation."""
        self._problems.append(problem)

    def clear_problems(self) -> None:
        """Clear recorded problems."""
        self._problems.clear()

    async def ensure_auth(self) -> Optional[str]:
        """
        Ensure OAuth token and HTTP headers are ready for API calls.

        Fetches token from backend if not already loaded.
        In test mode, skips authentication.

        Returns:
            None on success, error message string if auth failed
        """
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

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Make GET request to Facebook API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            timeout: Request timeout in seconds

        Returns:
            JSON response as dict
        """
        return await self.request("GET", endpoint, params=params, timeout=timeout)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Make POST request to Facebook API.

        Args:
            endpoint: API endpoint (without base URL)
            data: JSON body data
            form_data: Form-encoded data (for uploads)
            timeout: Request timeout in seconds

        Returns:
            JSON response as dict
        """
        return await self.request(
            "POST", endpoint, data=data, form_data=form_data, timeout=timeout
        )

    async def delete(
        self,
        endpoint: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Make DELETE request to Facebook API.

        Args:
            endpoint: API endpoint (without base URL)
            timeout: Request timeout in seconds

        Returns:
            JSON response as dict
        """
        return await self.request("DELETE", endpoint, timeout=timeout)

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Facebook Graph API.

        Includes retry logic with exponential backoff for transient errors.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: JSON body data
            form_data: Form-encoded data
            timeout: Request timeout in seconds

        Returns:
            JSON response as dict

        Raises:
            FacebookAPIError: On API error
            FacebookAuthError: On authentication failure
            FacebookTimeoutError: On timeout
        """
        auth_error = await self.ensure_auth()
        if auth_error:
            raise FacebookAuthError(auth_error)

        url = f"{API_BASE}/{API_VERSION}/{endpoint}"

        async def make_request() -> Dict[str, Any]:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(
                        url, params=params, headers=self._headers, timeout=timeout
                    )
                elif method == "POST":
                    if form_data:
                        # Form-encoded POST (for uploads, adsets, etc.)
                        response = await client.post(
                            url, data=form_data, timeout=timeout
                        )
                    else:
                        # JSON POST
                        response = await client.post(
                            url, json=data, headers=self._headers, timeout=timeout
                        )
                elif method == "DELETE":
                    response = await client.delete(
                        url, headers=self._headers, timeout=timeout
                    )
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
        """
        Execute function with exponential backoff retry.

        Args:
            func: Async function to execute
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)

        Returns:
            Function result

        Raises:
            Last exception if all retries failed
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await func()

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt == max_retries - 1:
                    raise FacebookTimeoutError(DEFAULT_TIMEOUT)

                delay = initial_delay * (2 ** attempt)
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}"
                )
                await asyncio.sleep(delay)

            except FacebookAPIError as e:
                if e.is_rate_limit:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise

                    # Longer delay for rate limits
                    delay = initial_delay * (2 ** attempt) * 2
                    logger.warning(
                        f"Rate limit hit, retry {attempt + 1}/{max_retries} after {delay}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    raise

        if last_exception:
            raise last_exception
        raise FacebookAPIError(500, "Unexpected retry loop exit")

    async def _fetch_token(self) -> str:
        """
        Fetch Facebook OAuth token from Flexus backend.

        Calls external_auth_token GraphQL query which:
        1. Authenticates bot via API key
        2. Verifies bot can access this user's token
        3. Decrypts and returns the stored OAuth token

        Returns:
            Access token string

        Raises:
            ValueError: If no token found or token expired
        """
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

        # Check expiration
        expires_at = token_data.get("expires_at")
        if expires_at and expires_at < time.time():
            raise ValueError("Facebook token expired, please reconnect")

        logger.info("Facebook token retrieved for %s", self.rcx.persona.persona_id)
        return access_token

    async def _prompt_oauth_connection(self) -> str:
        """
        Generate user-friendly message prompting OAuth connection.

        Called when token fetch fails (user hasn't connected Facebook yet).

        Returns:
            Formatted message with connection instructions
        """
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
