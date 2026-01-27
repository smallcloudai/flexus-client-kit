from __future__ import annotations
import logging
import time
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

import gql.transport.exceptions
import google.oauth2.credentials
import googleapiclient.discovery
import langchain_google_community.sheets.toolkit

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import langchain_adapter

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
        self.token_data = None
        self.tools = []
        self.tool_map = {}

    async def _ensure_tools_initialized(self) -> bool:
        if self.tools and self.token_data and time.time() < self.token_data.expires_at - 60:
            return True

        try:
            self.token_data = await ckit_external_auth.get_external_auth_token(
                self.fclient,
                "google",
                self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id,
            )
        except gql.transport.exceptions.TransportQueryError:
            return False

        if not self.token_data:
            return False

        creds = google.oauth2.credentials.Credentials(token=self.token_data.access_token)
        service = googleapiclient.discovery.build("sheets", "v4", credentials=creds)

        toolkit = langchain_google_community.sheets.toolkit.SheetsToolkit(api_resource=service)
        self.tools = toolkit.get_tools()
        self.tool_map = {t.name: t for t in self.tools}

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
            self.token_data = None
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient,
                "google",
                self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id,
                REQUIRED_SCOPES,
            )
            return f"❌ Authentication error. Ask user to authorize at:\n{auth_url}\n\nThen retry."
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
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient,
                "google",
                self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id,
                REQUIRED_SCOPES,
            )
            r += f"\n❌ Not authenticated. Ask user to authorize at:\n{auth_url}\n"

        return r
