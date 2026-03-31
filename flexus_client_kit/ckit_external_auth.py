import json
import logging
from dataclasses import dataclass

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
