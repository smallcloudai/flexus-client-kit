"""
Facebook Ads API - Exception Classes

Custom exceptions for handling Facebook API errors with user-friendly messages.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("facebook.exceptions")


class FacebookError(Exception):
    """Base exception for all Facebook integration errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\n{self.details}"
        return self.message


class FacebookAPIError(FacebookError):
    """
    Facebook API returned an error response.

    Contains error code and message from Facebook for proper handling.
    """

    # Common error codes
    CODE_INVALID_PARAMS = 100
    CODE_AUTH_EXPIRED = 190
    CODE_RATE_LIMIT_1 = 4
    CODE_RATE_LIMIT_2 = 17
    CODE_RATE_LIMIT_3 = 32
    CODE_INSUFFICIENT_PERMISSIONS = 80004
    CODE_AD_ACCOUNT_DISABLED = 2635
    CODE_BUDGET_TOO_LOW = 1487387

    RATE_LIMIT_CODES = {CODE_RATE_LIMIT_1, CODE_RATE_LIMIT_2, CODE_RATE_LIMIT_3}

    def __init__(
        self,
        code: int,
        message: str,
        error_type: str = "",
        user_title: Optional[str] = None,
        user_msg: Optional[str] = None,
        fbtrace_id: Optional[str] = None,
    ):
        self.code = code
        self.error_type = error_type
        self.user_title = user_title
        self.user_msg = user_msg
        self.fbtrace_id = fbtrace_id

        # Build user-friendly message
        details_parts = []
        if user_title:
            details_parts.append(f"**{user_title}**")
        if user_msg:
            details_parts.append(user_msg)
        if not details_parts:
            details_parts.append(message)

        details = "\n".join(details_parts)
        super().__init__(message, details)

    @property
    def is_rate_limit(self) -> bool:
        """Check if this is a rate limit error."""
        return self.code in self.RATE_LIMIT_CODES

    @property
    def is_auth_error(self) -> bool:
        """Check if this is an authentication error."""
        return self.code == self.CODE_AUTH_EXPIRED

    def format_for_user(self) -> str:
        """Format error message for display to user/model."""
        if self.code == self.CODE_AUTH_EXPIRED:
            return f"Authentication failed. Please reconnect Facebook.\n{self.details}"
        elif self.is_rate_limit:
            return f"Rate limit reached. Please try again in a few minutes.\n{self.details}"
        elif self.code == self.CODE_INVALID_PARAMS:
            return f"Invalid parameters (code {self.code}):\n{self.details}"
        elif self.code == self.CODE_AD_ACCOUNT_DISABLED:
            return f"Ad account is disabled.\n{self.details}"
        elif self.code == self.CODE_BUDGET_TOO_LOW:
            return f"Budget too low:\n{self.details}"
        elif self.code == self.CODE_INSUFFICIENT_PERMISSIONS:
            return f"Insufficient permissions.\n{self.details}"
        else:
            return f"Facebook API Error ({self.code}):\n{self.details}"


class FacebookAuthError(FacebookError):
    """Authentication/authorization error with Facebook."""

    def __init__(self, message: str = "Facebook authentication required"):
        super().__init__(message)


class FacebookValidationError(FacebookError):
    """Local validation error before API call."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class FacebookRateLimitError(FacebookAPIError):
    """Specific error for rate limiting."""

    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f", retry after {retry_after} seconds"
        super().__init__(
            code=17,
            message=message,
            error_type="OAuthException",
        )


class FacebookTimeoutError(FacebookError):
    """Request timeout error."""

    def __init__(self, timeout: float):
        super().__init__(f"Request timed out after {timeout} seconds")


async def parse_api_error(response: httpx.Response) -> FacebookAPIError:
    """
    Parse Facebook API error response into FacebookAPIError.

    Extracts error_user_title and error_user_msg from FB response when available,
    as these are designed by Facebook to be shown to end users.

    Args:
        response: Failed HTTP response from Facebook API

    Returns:
        FacebookAPIError with parsed error details
    """
    try:
        error_data = response.json()
        if "error" in error_data:
            err = error_data["error"]
            return FacebookAPIError(
                code=err.get("code", response.status_code),
                message=err.get("message", "Unknown error"),
                error_type=err.get("type", ""),
                user_title=err.get("error_user_title"),
                user_msg=err.get("error_user_msg"),
                fbtrace_id=err.get("fbtrace_id"),
            )
        else:
            # No error field in response
            return FacebookAPIError(
                code=response.status_code,
                message=f"HTTP {response.status_code}: {response.text[:500]}",
            )
    except Exception as e:
        # JSON parsing failed
        logger.warning(f"Error parsing FB API error response: {e}")
        return FacebookAPIError(
            code=response.status_code,
            message=f"HTTP {response.status_code}: {response.text[:500]}",
        )


def handle_validation_error(field: str, message: str) -> str:
    """Format validation error for model response."""
    return f"ERROR: {field} - {message}"
