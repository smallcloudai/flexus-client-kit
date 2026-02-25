from __future__ import annotations
import logging
import time
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit.core import ckit_bot_exec

import google.oauth2.credentials
import googleapiclient.discovery
import langchain_google_community.sheets.toolkit

from flexus_client_kit.core import ckit_cloudtool
from flexus_client_kit.core import ckit_client
from flexus_client_kit.core import ckit_external_auth
from flexus_client_kit.integrations.providers.request_response import langchain_adapter

logger = logging.getLogger("google_sheets")

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


GOOGLE_SHEETS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="google_sheets",
    description="Access Google Sheets to read, write, create, update, append, clear, and batch update data. Call with op=\"help\" to see all available ops.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation name: help, status, or any sheets op"},
            "args": {"type": "object"},
        },
        "required": ["op"]
    },
)


class IntegrationGoogleSheets:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self._last_access_token = None
        self.tools = []
        self.tool_map = {}

    async def _ensure_tools_initialized(self) -> bool:
        google_auth = self.rcx.external_auth.get("google") or {}
        token_obj = google_auth.get("token") or {}
        access_token = token_obj.get("access_token", "")
        if not access_token:
            self.tools = []
            self.tool_map = {}
            self._last_access_token = None
            return False
        if access_token == self._last_access_token and self.tools:
            return True
        creds = google.oauth2.credentials.Credentials(token=access_token)
        service = googleapiclient.discovery.build("sheets", "v4", credentials=creds)

        toolkit = langchain_google_community.sheets.toolkit.SheetsToolkit(api_resource=service)
        self.tools = toolkit.get_tools()
        self.tool_map = {t.name: t for t in self.tools}
        self._last_access_token = access_token

        logger.info("Initialized %d sheets tools: %s", len(self.tools), list(self.tool_map.keys()))
        return True

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]]
    ) -> str:
        if not model_produced_args:
            return self._all_commands_help()

        op = model_produced_args.get("op", "")
        if not op:
            return self._all_commands_help()

        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        op_lower = op.lower()
        print_help = op_lower == "help" or op_lower == "status+help"
        print_status = op_lower == "status" or op_lower == "status+help"

        authenticated = await self._ensure_tools_initialized()

        if print_status:
            status_msg = await self._status(authenticated)
            if print_help and authenticated:
                return status_msg + "\n\n" + self._all_commands_help()
            return status_msg

        if print_help:
            if authenticated:
                return self._all_commands_help()
            return await self._status(authenticated)

        if not authenticated:
            return await self._status(authenticated)

        if op not in self.tool_map:
            return self._all_commands_help()

        result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], args)
        if is_auth_error:
            self._last_access_token = None
            return "❌ Authentication error. Please reconnect Google in workspace settings.\n\nThen retry."
        return result

    def _all_commands_help(self) -> str:
        if not self.tools:
            return "❌ No tools loaded"

        return (
            "Google Sheets - All Available Operations:\n" +
            langchain_adapter.format_tools_help(self.tools) +
            "To execute an operation:\n" +
            '  google_sheets({"op": "sheets_read_data", "args": {"spreadsheet_id": "...", "range": "Sheet1!A1:D10"}})\n' +
            '  google_sheets({"op": "sheets_update_values", "args": {...}})'
        )

    async def _status(self, authenticated: bool) -> str:
        r = f"Google Sheets integration status:\n"
        r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
        r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
        r += f"  Workspace: {self.rcx.persona.ws_id}\n"

        if authenticated and await self._ensure_tools_initialized():
            r += f"  Tools loaded: {len(self.tools)}\n"
            r += f"  Available ops: {', '.join(self.tool_map.keys())}\n"
        elif not authenticated:
            r += "\n❌ Not authenticated. Please connect Google in workspace settings.\n"

        return r
