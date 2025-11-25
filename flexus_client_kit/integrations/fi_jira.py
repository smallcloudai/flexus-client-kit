from __future__ import annotations
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

import gql.transport.exceptions
import langchain_community.agent_toolkits.jira.toolkit
import langchain_community.utilities.jira
from atlassian import Jira, Confluence

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import langchain_adapter

logger = logging.getLogger("jira")

REQUIRED_SCOPES = [
    "read:jira-work",
    "write:jira-work",
    "read:project:jira",
    "write:issue:jira",
    "read:jql:jira",
    "offline_access",
]


JIRA_TOOL = ckit_cloudtool.CloudTool(
    name="jira",
    description="Access Jira to search issues (JQL), get projects, create issues, and other Jira API operations. Call with op=\"help\" to see all available ops.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation name: help, status, or any jira op"},
            "args": {"type": "object"},
        },
        "required": ["op"]
    },
)

JIRA_SETUP_SCHEMA = [
    {
        "bs_name": "jira_instance_url",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Jira",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Jira instance URL (e.g., https://yourcompany.atlassian.net)",
    },
]


class IntegrationJira:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        jira_instance_url: str,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.jira_instance_url = jira_instance_url
        self.token_data = None
        self.tools = []
        self.tool_map = {}

    async def _get_accessible_resources(self) -> list[dict]:
        if not self.token_data:
            return []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers={"Authorization": f"Bearer {self.token_data.access_token}"}
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        logger.warning("Failed to get accessible resources: %d", resp.status)
                        return []
        except Exception as e:
            logger.warning("Error getting accessible resources: %s", e)
            return []

    async def _ensure_tools_initialized(self) -> bool:
        if self.tools and self.token_data and time.time() < self.token_data.expires_at - 60:
            return True

        try:
            self.token_data = await ckit_external_auth.get_external_auth_token(
                self.fclient,
                "atlassian",
                self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id,
            )
        except gql.transport.exceptions.TransportQueryError:
            return False

        if not self.token_data:
            return False

        accessible = await self._get_accessible_resources()
        logger.info("Accessible Atlassian sites: %s", accessible)

        configured_matches = any(
            self.jira_instance_url.rstrip('/') in site.get('url', '').rstrip('/')
            for site in accessible
        )
        if not configured_matches and accessible:
            logger.warning(
                "Configured Jira URL %s does not match any accessible sites: %s",
                self.jira_instance_url,
                [site.get('url') for site in accessible]
            )

        cloud_id = None
        if accessible:
            cloud_id = accessible[0].get('id')
            logger.info("Using cloud ID: %s for OAuth API calls", cloud_id)

        if cloud_id:
            api_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
            logger.info("Using OAuth API URL: %s", api_url)
        else:
            api_url = self.jira_instance_url
            logger.warning("No cloud ID found, using configured URL: %s", api_url)

        jira_client = Jira(
            url=api_url,
            token=self.token_data.access_token,
            cloud=True,
        )
        confluence_client = Confluence(
            url=api_url,
            token=self.token_data.access_token,
            cloud=True,
        )

        wrapper = langchain_community.utilities.jira.JiraAPIWrapper(
            jira_instance_url=self.jira_instance_url,
            jira_api_token="dummy",
            jira_username="dummy",
            jira_cloud=True,
        )
        wrapper.jira = jira_client
        wrapper.confluence = confluence_client

        toolkit = langchain_community.agent_toolkits.jira.toolkit.JiraToolkit.from_jira_api_wrapper(wrapper)
        self.tools = toolkit.get_tools()
        self.tool_map = {t.name: t for t in self.tools}

        logger.info("Initialized %d jira tools: %s", len(self.tools), list(self.tool_map.keys()))
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

        logger.info("Jira called: op=%s, args=%s", op, args)
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

        if op == "get_projects":
            tool_input = ""
        elif op == "jql_query" and "query" in args:
            tool_input = args["query"]
        elif op == "create_issue" and isinstance(args, dict):
            tool_input = json.dumps(args)
        elif op == "catch_all_jira_api" and isinstance(args, dict):
            tool_input = json.dumps(args)
        elif op == "create_confluence_page" and isinstance(args, dict):
            tool_input = json.dumps(args)
        else:
            tool_input = json.dumps(args) if isinstance(args, dict) else str(args)

        logger.info("Calling Jira tool: op=%s, tool_input=%s", op, tool_input)

        if op == "get_projects":
            try:
                raw_projects = self.tool_map[op].api_wrapper.jira.projects()
                logger.info("Raw projects from Jira API: %s", raw_projects)
            except Exception as e:
                logger.warning("Error calling raw projects API: %s", e, exc_info=True)

        result, is_auth_error = await langchain_adapter.run_langchain_tool(self.tool_map[op], tool_input)
        logger.info("Jira tool result: op=%s, result_length=%d, result_preview=%s", op, len(result), result[:500])
        if is_auth_error:
            self.token_data = None
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient,
                "atlassian",
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
            "Jira - All Available Operations:\n" +
            langchain_adapter.format_tools_help(self.tools) +
            "To execute an operation:\n" +
            '  jira({"op": "get_projects"})\n' +
            '  jira({"op": "jql_query", "args": {"query": "project = TEST AND status = Open"}})\n' +
            '  jira({"op": "create_issue", "args": {"summary": "Bug fix", "description": "Details", "issuetype": {"name": "Task"}, "priority": {"name": "High"}}})'
        )

    async def _status(self, authenticated: bool) -> str:
        r = f"Jira integration status:\n"
        r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
        r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
        r += f"  Workspace: {self.rcx.persona.ws_id}\n"
        r += f"  Configured Instance URL: {self.jira_instance_url}\n"

        if authenticated and await self._ensure_tools_initialized():
            accessible = await self._get_accessible_resources()
            if accessible:
                r += f"\n  Accessible Atlassian sites ({len(accessible)}):\n"
                for site in accessible:
                    r += f"    - {site.get('name', 'Unknown')}: {site.get('url', 'N/A')}\n"

                configured_matches = any(
                    self.jira_instance_url.rstrip('/') in site.get('url', '').rstrip('/')
                    for site in accessible
                )
                if not configured_matches:
                    r += f"\n  ⚠️  WARNING: Your configured Jira URL does not match any accessible sites!\n"
                    r += f"  You may need to re-authorize with access to {self.jira_instance_url}\n"

            r += f"\n  Tools loaded: {len(self.tools)}\n"
            r += f"  Available ops: {', '.join(self.tool_map.keys())}\n"
        elif not authenticated:
            auth_url = await ckit_external_auth.start_external_auth_flow(
                self.fclient,
                "atlassian",
                self.rcx.persona.ws_id,
                self.rcx.persona.owner_fuser_id,
                REQUIRED_SCOPES,
            )
            r += f"\n❌ Not authenticated. Ask user to authorize at:\n{auth_url}\n"

        return r
