import json
import logging
import time
from typing import Dict, Any, Optional

import google.oauth2.credentials
import googleapiclient.discovery
import langchain_google_community.calendar.toolkit

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit.integrations import langchain_adapter

logger = logging.getLogger("google_calendar")

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/calendar"]


GOOGLE_CALENDAR_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="google_calendar",
    description="Access Google Calendar to create, search, update, move, and delete events. Call with op=\"help\" to see all available ops.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation name: help, status, or any calendar op"},
            "args": {"type": "object"},
        },
        "required": ["op"]
    },
)


class IntegrationGoogleCalendar:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,
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
        service = googleapiclient.discovery.build("calendar", "v3", credentials=creds)

        toolkit = langchain_google_community.calendar.toolkit.CalendarToolkit(api_resource=service)
        self.tools = toolkit.get_tools()
        self.tool_map = {t.name: t for t in self.tools}
        self._last_access_token = access_token

        logger.info("Initialized %d calendar tools: %s", len(self.tools), list(self.tool_map.keys()))
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

        if op == "search_events" and "calendars_info" in args:
            try:
                if isinstance(args["calendars_info"], str):
                    cal_str = args["calendars_info"].strip()
                    if cal_str and cal_str[0] in '[{':
                        calendars_info = json.loads(cal_str)
                    else:
                        calendars_info = [cal_str] if cal_str else []
                else:
                    calendars_info = args["calendars_info"]
                if calendars_info and (isinstance(calendars_info[0], str) or not calendars_info[0].get("timeZone")):
                    get_cal_result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map["get_calendars_info"], {})
                    if is_auth_error:
                        result, is_auth_error = get_cal_result, is_auth_error
                    else:
                        all_calendars = json.loads(get_cal_result)
                        requested_ids = set(calendars_info if isinstance(calendars_info[0], str) else [cal["id"] for cal in calendars_info])
                        matched_calendars = [cal for cal in all_calendars if cal["id"] in requested_ids or "primary" in requested_ids]
                        args["calendars_info"] = json.dumps(matched_calendars)
                        logger.info("Fetched full calendar info for %d calendars", len(matched_calendars))
                        result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], args)
                else:
                    result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], args)
            except Exception as e:
                logger.warning("Error preprocessing search_events args: %s", e)
                result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], args)
        else:
            result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], args)

        if is_auth_error:
            self._last_access_token = None
            return "❌ Authentication error. Please reconnect Google in workspace settings.\n\nThen retry."
        return result

    def _all_commands_help(self) -> str:
        if not self.tools:
            return "❌ No tools loaded"

        return (
            "Google Calendar - All Available Operations:\n" +
            langchain_adapter.format_tools_help(self.tools) +
            "To execute an operation:\n" +
            '  google_calendar({"op": "get_calendars_info"})\n' +
            '  google_calendar({"op": "create_calendar_event", "args": {...}})'
        )

    async def _status(self, authenticated: bool) -> str:
        r = f"Google Calendar integration status:\n"
        r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
        r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
        r += f"  Workspace: {self.rcx.persona.ws_id}\n"

        if authenticated and await self._ensure_tools_initialized():
            r += f"  Tools loaded: {len(self.tools)}\n"
            r += f"  Available ops: {', '.join(self.tool_map.keys())}\n"
        elif not authenticated:
            r += "\n❌ Not authenticated. Please connect Google in workspace settings.\n"

        return r


