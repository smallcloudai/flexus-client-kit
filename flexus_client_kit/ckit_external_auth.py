import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import gql
from flexus_client_kit import ckit_client

logger = logging.getLogger("extauth")

@dataclass
class ExternalAuthToken:
    access_token: str | None
    expires_at: int
    token_type: str
    scope_values: list[str]
    auth_url: str | None = None
    url_template_vars: dict | None = None


async def external_auth_disconnect(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    persona_id: str,
    provider_name: str,
) -> None:
    http = await fclient.use_http_on_behalf(persona_id, "")
    async with http as h:
        await h.execute(
            gql.gql("""
                mutation DisconnectExternalAuth($ws_id: String!, $persona_id: String!, $provider_name: String!) {
                    external_auth_disconnect(ws_id: $ws_id, persona_id: $persona_id, provider_name: $provider_name)
                }"""),
            variable_values={"ws_id": ws_id, "persona_id": persona_id, "provider_name": provider_name},
        )


async def get_external_auth_token(
    http,
    provider: str,
    ws_id: str,
    fuser_id: str,
) -> ExternalAuthToken | None:
    r = await http.execute(
        gql.gql("""
            query GetExternalAuthToken($ws_id: String!, $provider: String!, $fuser_id: String) {
                external_auth_token(ws_id: $ws_id, provider: $provider, fuser_id: $fuser_id) {
                    access_token
                    expires_at
                    token_type
                    scope_values
                    url_template_vars
                }
            }"""),
        variable_values={
            "ws_id": ws_id,
            "provider": provider,
            "fuser_id": fuser_id,
        }
    )
    token_data = r.get("external_auth_token")
    if not token_data:
        return None
    return ExternalAuthToken(
        access_token=token_data.get("access_token"),
        expires_at=token_data.get("expires_at", 0),
        token_type=token_data.get("token_type", ""),
        scope_values=token_data.get("scope_values", []),
        url_template_vars=token_data.get("url_template_vars"),
    )


async def start_external_auth_flow(
    http,
    provider: str,
    ws_id: str,
    fuser_id: str,
    scopes: list[str],
    url_template_vars: dict | None = None,
    persona_id: str = "",
) -> str:
    all_scopes = list(set(scopes))
    try:
        existing_token = await get_external_auth_token(http, provider, ws_id, fuser_id)
        if existing_token and existing_token.scope_values:
            all_scopes = list(set(all_scopes + existing_token.scope_values))
    except gql.transport.exceptions.TransportQueryError:
        pass

    r = await http.execute(
        gql.gql("""
            mutation StartExternalAuth($ws_id: String!, $provider: String!, $scope_values: [String!], $fuser_id: String, $url_template_vars: String, $persona_id: String) {
                external_auth_start(
                    ws_id: $ws_id,
                    provider: $provider,
                    scope_values: $scope_values,
                    fuser_id: $fuser_id,
                    url_template_vars: $url_template_vars,
                    persona_id: $persona_id
                ) {
                    authorization_url
                }
            }"""),
        variable_values={
            "ws_id": ws_id,
            "provider": provider,
            "scope_values": all_scopes,
            "fuser_id": fuser_id,
            "url_template_vars": json.dumps(url_template_vars) if url_template_vars else None,
            "persona_id": persona_id,
        }
    )
    return r["external_auth_start"]["authorization_url"]


@dataclass
class SavedCredentialField:
    key: str
    label: str
    masked_value: str


@dataclass
class SavedCredential:
    auth_id: str
    provider: str
    credential_name: str
    status: str
    fields: list[SavedCredentialField] = field(default_factory=list)


async def list_saved_credentials(
    http,
    ws_id: str,
    provider: Optional[str] = None,
) -> list[SavedCredential]:
    r = await http.execute(gql.gql("""
        query ListSavedCredentials($ws_id: String!, $provider: String) {
            workspace_saved_credentials(ws_id: $ws_id, provider: $provider) {
                auth_id
                provider
                credential_name
                status
                fields { key label masked_value }
            }
        }
        """), variable_values={"ws_id": ws_id, "provider": provider}
    )
    results = []
    for item in (r.get("workspace_saved_credentials") or []):
        results.append(SavedCredential(
            auth_id=item["auth_id"],
            provider=item["provider"],
            credential_name=item["credential_name"],
            status=item["status"],
            fields=[SavedCredentialField(key=f["key"], label=f["label"], masked_value=f["masked_value"])
                    for f in (item.get("fields") or [])],
        ))
    return results


async def fetch_resolved_persona_setup(http, persona_id: str) -> dict:
    r = await http.execute(gql.gql("""
        query PersonaResolvedSetup($persona_id: String!) {
            persona_resolved_setup(persona_id: $persona_id)
        }
    """), variable_values={"persona_id": persona_id})
    return r.get("persona_resolved_setup") or {}


async def get_saved_credential_by_name(
    http,
    ws_id: str,
    provider: str,
    credential_name: str,
) -> Optional[SavedCredential]:
    all_creds = await list_saved_credentials(http, ws_id, provider=provider)
    for cred in all_creds:
        if cred.credential_name == credential_name:
            return cred
    return None
