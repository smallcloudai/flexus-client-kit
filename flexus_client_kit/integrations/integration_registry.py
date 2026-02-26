from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Callable
from flexus_client_kit import ckit_cloudtool


@dataclass
class Integration:
    name: str                          # registry key, e.g. "google_calendar"
    display_name: str                  # shown in UI, e.g. "Google Calendar"
    auth_type: Literal["oauth", "api_key"]
    # OAuth-specific
    provider: str | None = None        # matches PROVIDER_CONFIGS key: "google", "github", etc.
    scopes: list[str] = field(default_factory=list)
    # API-key-specific (setup_schema format)
    setup_fields: list[dict] = field(default_factory=list)
    # Tools provided to the bot
    tools: list[ckit_cloudtool.CloudTool] = field(default_factory=list)
    # Factory: given RobotContext, returns tool handler for the named tool.
    # Signature: (rcx: RobotContext) -> async fn(toolcall, args) -> str | ToolResult
    # Using rcx (not just auth dict) allows access to live external_auth and fclient.
    tool_handler_factories: dict[str, Callable] = field(default_factory=dict)


# The global registry — integrations register themselves here
INTEGRATION_REGISTRY: dict[str, Integration] = {}


def register(integration: Integration) -> Integration:
    """Register an integration. Call at module level in each integration file."""
    INTEGRATION_REGISTRY[integration.name] = integration
    return integration
