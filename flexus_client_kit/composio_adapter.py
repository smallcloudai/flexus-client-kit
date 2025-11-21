import os
import logging
import json
from typing import Dict, Any, Optional, List

from composio import Composio

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("composio")


class ComposioToolsetManager:
    def __init__(self, user_id: str):
        self.api_key = os.getenv("COMPOSIO_API_KEY", "")
        self.user_id = user_id
        self._client = None
        self._tools_cache: Dict[str, List[Any]] = {}

    def _ensure_client(self) -> Composio:
        if self._client is None:
            self._client = Composio(api_key=self.api_key)
            logger.info("Initialized Composio client for user: %s", self.user_id)
        return self._client

    def get_tools_for_app(self, app_name: str) -> List[Any]:
        if app_name in self._tools_cache:
            logger.info("Returning cached tools for app: %s", app_name)
            return self._tools_cache[app_name]

        client = self._ensure_client()
        try:
            tools = client.tools.get(user_id=self.user_id, toolkits=[app_name.upper()])
            self._tools_cache[app_name] = tools
            logger.info("Loaded %d tools for app: %s", len(tools), app_name)
            return tools
        except Exception as e:
            logger.exception("Error loading tools for app %s: %s", app_name, e)
            return []

    def get_actions_for_app(self, app_name: str) -> List[str]:
        try:
            client = self._ensure_client()
            actions = client.actions.get(apps=[app_name.upper()])
            action_names = [action.name for action in actions.items]
            logger.info("Found %d actions for app: %s", len(action_names), app_name)
            return action_names
        except Exception as e:
            logger.exception("Error getting actions for app %s: %s", app_name, e)
            return []

    def execute_action(
        self,
        action_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        client = self._ensure_client()
        try:
            result = client.tools.execute(
                slug=action_name,
                arguments=params,
                user_id=self.user_id,
                dangerously_skip_version_check=True,
            )
            logger.info("Executed action %s successfully", action_name)

            if hasattr(result, 'data'):
                return result.data if result.data else {}
            elif hasattr(result, 'error'):
                return {"error": str(result.error)}
            else:
                return {"result": str(result)}
        except Exception as e:
            error_msg = f"Error executing action {action_name}: {type(e).__name__} {e}"
            logger.exception(error_msg)
            return {"error": error_msg}

    def get_connected_accounts(self, app_name: Optional[str] = None) -> List[Dict[str, Any]]:
        client = self._ensure_client()
        try:
            kwargs = {"user_ids": [self.user_id]}
            if app_name:
                kwargs["toolkit_slugs"] = [app_name.lower()]

            response = client.connected_accounts.list(**kwargs)

            result = []
            for conn in response.items:
                result.append({
                    "id": conn.id,
                    "app": conn.toolkit.slug,
                    "status": conn.status,
                    "enabled": not conn.is_disabled,
                })
            logger.info("Found %d connected accounts", len(result))
            return result
        except Exception as e:
            logger.exception("Error getting connected accounts: %s", e)
            return []

    def get_or_create_connection(self, app_name: str, auth_config_id: Optional[str] = None) -> Optional[str]:
        accounts = self.get_connected_accounts(app_name)
        if accounts:
            conn_id = accounts[0]["id"]
            logger.info("Found existing connection for %s: %s", app_name, conn_id)
            return conn_id

        logger.info("No existing connection for %s, need user to connect", app_name)
        return None

    def initiate_connection(self, app_name: str, auth_config_id: str, redirect_url: Optional[str] = None, api_key: Optional[str] = None, workspace_subdomain: Optional[str] = None) -> Dict[str, Any]:
        client = self._ensure_client()
        try:
            kwargs = {
                "user_id": self.user_id,
                "auth_config_id": auth_config_id,
            }

            if api_key:
                config_val = {"generic_api_key": api_key}
                if workspace_subdomain:
                    config_val["subdomain"] = workspace_subdomain
                kwargs["config"] = {
                    "auth_scheme": "API_KEY",
                    "val": config_val
                }
                logger.info("Initiating API key connection for %s", app_name)
            elif redirect_url:
                kwargs["redirect_url"] = redirect_url
                logger.info("Initiating OAuth connection for %s", app_name)

            request = client.connected_accounts.initiate(**kwargs)

            return {
                "connection_status": request.status if hasattr(request, 'status') else 'initiated',
                "redirect_url": getattr(request, 'redirect_url', None),
                "connected_account_id": getattr(request, 'id', None),
            }
        except Exception as e:
            logger.exception("Error initiating connection: %s", e)
            return {"error": str(e)}

    def reset_and_connect(self, app_name: str, auth_config_id: str, **connection_kwargs) -> Dict[str, Any]:
        client = self._ensure_client()
        try:
            response = client.connected_accounts.list(
                user_ids=[self.user_id],
                toolkit_slugs=[app_name.lower()]
            )
            for account in response.items:
                logger.info("Deleting existing %s connection %s", app_name, account.id)
                client.connected_accounts.delete(account.id)

            logger.info("Creating new %s connection", app_name)
            return self.initiate_connection(app_name, auth_config_id, **connection_kwargs)
        except Exception as e:
            logger.exception("Error resetting %s connection: %s", app_name, e)
            return {"error": str(e)}

    async def execute_action_async(self, action_name: str, args: Dict[str, Any], app_name: str, auth_config_id: Optional[str] = None) -> tuple[str, bool]:
        try:
            result = self.execute_action(action_name, args)

            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"]
                is_auth_error = any(
                    x in str(error_msg).lower()
                    for x in ["401", "403", "unauthorized", "not authenticated", "authentication", "not connected"]
                )

                r = f"❌ Error: {error_msg}\n\n"

                if is_auth_error and auth_config_id:
                    request = self.initiate_connection(app_name, auth_config_id)
                    if "error" not in request:
                        r += "Authentication required. Please authorize the connection at:\n"
                        r += f"{request.get('redirect_url', 'N/A')}\n"

                return r, is_auth_error
            elif isinstance(result, str):
                return result, False
            elif isinstance(result, dict) or isinstance(result, list):
                return json.dumps(result, indent=2), False
            else:
                return str(result), False

        except Exception as e:
            logger.exception("Error executing action")
            error_msg = str(e).lower()
            is_auth_error = (
                "401" in error_msg or
                "403" in error_msg or
                "unauthorized" in error_msg or
                "not authenticated" in error_msg or
                "authentication" in error_msg or
                "not connected" in error_msg
            )

            r = f"❌ Error: {type(e).__name__}: {e}\n\n"

            if is_auth_error and auth_config_id:
                request = self.initiate_connection(app_name, auth_config_id)
                if "error" not in request:
                    r += "Authentication required. Please authorize the connection at:\n"
                    r += f"{request.get('redirect_url', 'N/A')}\n"

            return r, is_auth_error


class IntegrationComposio:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        app_name: str,
        auth_config_id: Optional[str] = None,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.app_name = app_name
        self.auth_config_id = auth_config_id
        user_id = rcx.persona.ws_id
        self.composio_mgr = ComposioToolsetManager(user_id=user_id)

    def format_tools_help(self) -> str:
        tools = self.composio_mgr.get_tools_for_app(self.app_name)
        if not tools:
            return f"No actions available for app: {self.app_name}"

        help_sections = []
        for tool in tools:
            help_sections.append(f"\n{'='*60}")

            if isinstance(tool, dict):
                func = tool.get("function", {})
                action_name = func.get("name", "unknown")
                action_desc = func.get("description", "No description")
                params = func.get("parameters", {})
            else:
                action_name = getattr(tool, 'name', 'unknown')
                action_desc = getattr(tool, 'description', 'No description')
                params = getattr(tool, 'parameters', {})

            help_sections.append(f"Action: {action_name}")
            help_sections.append(f"Description: {action_desc}\n")

            try:
                properties = params.get("properties", {})
                required = params.get("required", [])

                if properties:
                    help_sections.append("Arguments:")
                    for prop_name, prop_schema in properties.items():
                        is_required = prop_name in required
                        req_marker = "[REQUIRED]" if is_required else "[optional]"
                        prop_desc = prop_schema.get("description", "")
                        prop_type = prop_schema.get("type", "")

                        help_sections.append(f"  - {prop_name} {req_marker}")
                        if prop_type:
                            help_sections.append(f"    type: {prop_type}")
                        if prop_desc:
                            help_sections.append(f"    {prop_desc}")
                else:
                    help_sections.append("No arguments required.")
            except Exception as e:
                logger.warning("Error parsing parameters for action %s: %s", action_name, e)
                help_sections.append("Arguments schema not available.")

        help_sections.append(f"\n{'='*60}\n")
        return "\n".join(help_sections)

    def format_status(self) -> str:
        r = f"{self.app_name.title()} Integration Status:\n\n"
        r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
        r += f"  Workspace: {self.rcx.persona.ws_id}\n\n"

        accounts = self.composio_mgr.get_connected_accounts(self.app_name)
        if accounts:
            r += f"✅ Connected to {self.app_name.title()}:\n"
            for acc in accounts:
                status_icon = "✅" if acc.get("enabled") else "❌"
                r += f"  {status_icon} ID: {acc.get('id')}\n"
                r += f"     Status: {acc.get('status')}\n"
                r += f"     Enabled: {acc.get('enabled')}\n\n"

            tools = self.composio_mgr.get_tools_for_app(self.app_name)
            r += f"  Available actions: {len(tools)}\n"
            r += f"  Use op=\"help\" to see all available actions with their parameters.\n"
        else:
            r += f"❌ Not connected to {self.app_name.title()}.\n"
            if self.auth_config_id:
                request = self.composio_mgr.initiate_connection(self.app_name, self.auth_config_id)
                if "error" not in request:
                    r += f"Please authorize the connection at:\n{request.get('redirect_url', 'N/A')}\n\n"
                    r += f"Connection Status: {request.get('connection_status', 'unknown')}\n"
                else:
                    r += f"Error initiating connection: {request['error']}\n"
            else:
                r += "No auth_config_id configured. Please set up authentication in bot setup.\n"

        return r

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return self.format_tools_help()

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        logger.info("%s called: op=%s, args=%s", self.app_name, op, args)

        if not op or op.lower() == "help":
            return self.format_tools_help()

        if op.lower() == "status":
            return self.format_status()

        tools = self.composio_mgr.get_tools_for_app(self.app_name)
        action_name = None
        for tool in tools:
            if isinstance(tool, dict):
                func = tool.get("function", {})
                name = func.get("name", "")
            else:
                name = getattr(tool, 'name', '')

            if name.lower() == op.lower():
                action_name = name
                break

        if not action_name:
            r = f"❌ Unknown action: {op}.\n\n"
            r += self.format_tools_help()
            return r

        result, _ = await self.composio_mgr.execute_action_async(action_name, args, self.app_name, self.auth_config_id)
        return result
