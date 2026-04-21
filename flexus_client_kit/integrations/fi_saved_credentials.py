import logging
from typing import Any, Optional

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_external_auth

logger = logging.getLogger("fi_saved_credentials")


SAVED_CREDENTIALS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="saved_credentials",
    description=(
        "List or find workspace-shared credentials saved by the user (API keys, tokens, etc.). "
        "Values are always masked — use this to check what credentials exist and reference them by name. "
        "op=list: list all saved credentials, optionally filtered by provider. "
        "op=get: find one credential by provider + exact name."
    ),
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["list", "get"],
                "description": "list — show all saved credentials (optionally by provider); get — look up one by provider + name",
            },
            "args": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "provider": {
                        "type": ["string", "null"],
                        "description": "Filter by provider namespace, e.g. 'openai', 'tavily'. For op=get this is required.",
                    },
                    "credential_name": {
                        "type": ["string", "null"],
                        "description": "For op=get: exact credential name to look up, e.g. 'Production OpenAI'.",
                    },
                },
                "required": ["provider", "credential_name"],
            },
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

SAVED_CREDENTIALS_HELP = """
list   - List all workspace-shared credentials, optionally filtered by provider.
         args: provider (optional)

get    - Find one credential by provider + exact name (case-sensitive).
         args: provider (required), credential_name (required)

Fields are always masked. This tool is for discovery and referencing, not secret retrieval.

Examples:
  saved_credentials(op="list", args={"provider": null, "credential_name": null})
  saved_credentials(op="list", args={"provider": "openai", "credential_name": null})
  saved_credentials(op="get", args={"provider": "openai", "credential_name": "Production OpenAI"})
"""


async def handle_saved_credentials(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: dict[str, Any],
    fclient: ckit_client.FlexusClient,
    ws_id: str,
) -> str:
    op = model_produced_args.get("op", "")
    if not op:
        return SAVED_CREDENTIALS_HELP

    args = model_produced_args.get("args") or {}
    provider: Optional[str] = args.get("provider") or None
    credential_name: Optional[str] = args.get("credential_name") or None

    http = await fclient.use_http_on_behalf(toolcall.connected_persona_id, toolcall.fcall_untrusted_key)
    async with http as h:
        if op == "list":
            creds = await ckit_external_auth.list_saved_credentials(h, ws_id, provider=provider)
            if not creds:
                filter_msg = f" for provider '{provider}'" if provider else ""
                return f"No saved credentials found{filter_msg}."
            lines = [f"Found {len(creds)} saved credential(s):\n"]
            for c in creds:
                field_summary = ", ".join(f"{f.key}: {f.masked_value}" for f in c.fields)
                lines.append(f"- **{c.credential_name}** (provider: {c.provider}, auth_id: {c.auth_id})\n  Fields: {field_summary or '(none)'}")
            return "\n".join(lines)

        elif op == "get":
            if not provider or not credential_name:
                return "Error: op=get requires both provider and credential_name\n\n" + SAVED_CREDENTIALS_HELP
            cred = await ckit_external_auth.get_saved_credential_by_name(h, ws_id, provider, credential_name)
            if not cred:
                return f"No credential found with provider='{provider}' and name='{credential_name}'."
            field_lines = [f"  - {f.key} ({f.label}): {f.masked_value}" for f in cred.fields]
            return (
                f"**{cred.credential_name}**\n"
                f"Provider: {cred.provider}\n"
                f"Auth ID: {cred.auth_id}\n"
                f"Status: {cred.status}\n"
                f"Fields:\n" + "\n".join(field_lines)
            )

    return f"Unknown op: {op}\n\n" + SAVED_CREDENTIALS_HELP
