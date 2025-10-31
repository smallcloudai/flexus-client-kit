from typing import Dict, Any

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool


BOSS_SETUP_COLLEAGUES_TOOL = ckit_cloudtool.CloudTool(
    name="boss_setup_colleagues",
    description="Manage colleague bot configuration. Call with op='help' to show usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "get", "update"]},
            "args": {"type": "object"},
        },
        "required": ["op"]
    },
)

BOSS_SETUP_COLLEAGUES_HELP = """
Usage:

boss_setup_colleagues(op="help")
    Shows this help.

boss_setup_colleagues(op="get", args={"bot_name": "Karen"})
    View the complete setup for the specified bot, including schema and current values.

boss_setup_colleagues(op="update", args={"bot_name": "Karen", "set_key": "max_retries", "set_val": "5"})
    Update a specific configuration key for the bot.
    Omit set_val to reset to default.

Examples:
- boss_setup_colleagues(op="help")
- boss_setup_colleagues(op="get", args={"bot_name": "Karen"})
- boss_setup_colleagues(op="update", args={"bot_name": "Karen", "set_key": "max_retries", "set_val": "5"})
- boss_setup_colleagues(op="update", args={"bot_name": "Karen", "set_key": "debug_mode"})  # reset to default
"""


async def handle_colleague_setup(
    fclient: ckit_client.FlexusClient,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_args: Dict[str, Any],
) -> str:
    op = model_args.get("op", "")
    if not op or op == "help":
        return BOSS_SETUP_COLLEAGUES_HELP
    if op not in ["get", "update"]:
        return f"Error: Unknown op: {op}\n{BOSS_SETUP_COLLEAGUES_HELP}"

    a, err = ckit_cloudtool.sanitize_args(model_args)
    if err:
        return f"Error: {err}\n{BOSS_SETUP_COLLEAGUES_HELP}"

    if not (bot_name := ckit_cloudtool.try_best_to_find_argument(a, model_args, "bot_name", "")):
        return f"Error: bot_name is required in args\n{BOSS_SETUP_COLLEAGUES_HELP}"

    if op == "update":
        if not (set_key := ckit_cloudtool.try_best_to_find_argument(a, model_args, "set_key", "")):
            return f"Error: set_key is required in args for update operation\n{BOSS_SETUP_COLLEAGUES_HELP}"
        set_val = ckit_cloudtool.try_best_to_find_argument(a, model_args, "set_val", None)

    http = await fclient.use_http()
    async with http as h:
        try:
            r = await h.execute(
                gql.gql("""mutation BossSetupColleagues($bot_name: String!, $op: String!, $set_key: String, $set_val: String) {
                    boss_setup_colleagues(bot_name: $bot_name, op: $op, set_key: $set_key, set_val: $set_val)
                }"""),
                variable_values={
                    "bot_name": bot_name,
                    "op": op,
                    "set_key": set_key if op == "update" else None,
                    "set_val": set_val if op == "update" else None,
                },
            )
            if not (result := r.get("boss_setup_colleagues")):
                return f"Error: Failed to {op} setup for {bot_name}"
            return result
        except gql.transport.exceptions.TransportQueryError as e:
            return f"GraphQL Error: {str(e)}"
