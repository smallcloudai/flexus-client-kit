from __future__ import annotations
import os
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec
    from flexus_client_kit import ckit_client

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import composio_adapter

logger = logging.getLogger("fibery")


FIBERY_TOOL = ckit_cloudtool.CloudTool(
    name="fibery",
    description="Access Fibery for managing work items, projects, documents, and workflows. Call with op=\"help\" to see all available operations.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation name or tool name to execute"},
            "args": {"type": "object"},
        },
        "required": []
    },
)

FIBERY_SETUP_SCHEMA = [
    {
        "bs_name": "fibery_workspace_subdomain",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Fibery",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Fibery workspace subdomain (e.g., 'yourcompany' from yourcompany.fibery.io)",
    },
    {
        "bs_name": "fibery_api_key",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Fibery",
        "bs_order": 2,
        "bs_importance": 1,
        "bs_description": "Fibery API key for authentication",
    },
]


class IntegrationFibery(composio_adapter.IntegrationComposio):
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        fibery_workspace_subdomain: str = "",
        fibery_api_key: str = "",
    ):
        auth_config_id = os.getenv("COMPOSIO_FIBERY_AUTH_CONFIG_ID")
        super().__init__(fclient, rcx, "fibery", auth_config_id)

        if fibery_api_key and fibery_workspace_subdomain and auth_config_id:
            result = self.composio_mgr.reset_and_connect(
                self.app_name,
                auth_config_id,
                api_key=fibery_api_key,
                workspace_subdomain=fibery_workspace_subdomain,
            )
            if "error" not in result:
                logger.info("✅ Connected Fibery: connection_id=%s", result.get('connected_account_id'))
            else:
                logger.error("❌ Failed to connect Fibery: %s", result['error'])
        else:
            logger.warning("Fibery auto-connect skipped: subdomain=%s, api_key=%s, auth_config=%s",
                         bool(fibery_workspace_subdomain), bool(fibery_api_key), bool(auth_config_id))
