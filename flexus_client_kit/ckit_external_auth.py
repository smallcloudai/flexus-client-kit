import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import gql
from flexus_client_kit import ckit_client, gql_utils

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("extauth")


@dataclass
class ExternalAuthToken:
    access_token: str | None
    expires_at: int
    token_type: str
    scope_values: list[str]
    auth_url: str | None = None


# XXX garbage code
def get_fuser_id_from_rcx(rcx: "ckit_bot_exec.RobotContext", ft_id: str | None = None) -> str:
    if ft_id and ft_id in rcx.latest_threads:
        return rcx.latest_threads[ft_id].thread_fields.owner_fuser_id
    return rcx.persona.owner_fuser_id


async def upsert_external_auth(
    fclient: ckit_client.FlexusClient,
    persona_id: str,
    auth_searchable: str,
    auth_name: str,
    auth_service_provider: str,
    auth_json: dict,
) -> None:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""
                mutation UpsertExternalAuth(
                    $persona_id: String!,
                    $auth_searchable: String!,
                    $auth_name: String!,
                    $auth_service_provider: String!,
                    $auth_json: String!
                ) {{
                    upsert_external_auth(
                        persona_id: $persona_id,
                        auth_searchable: $auth_searchable,
                        auth_name: $auth_name,
                        auth_service_provider: $auth_service_provider,
                        auth_json: $auth_json
                    )
                }}"""),
            variable_values={
                "persona_id": persona_id,
                "auth_searchable": auth_searchable,
                "auth_name": auth_name,
                "auth_service_provider": auth_service_provider,
                "auth_json": json.dumps(auth_json),
            },
        )


async def decrypt_external_auth(
    fclient: ckit_client.FlexusClient,
    auth_searchable: str,
) -> dict:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""
                query DecryptExternalAuth($auth_searchable: String!) {
                    decrypt_external_auth(auth_searchable: $auth_searchable)
                }"""),
            variable_values={"auth_searchable": auth_searchable},
        )
    return r["decrypt_external_auth"]


async def get_external_auth_token(
    fclient: ckit_client.FlexusClient,
    provider: str,
    ws_id: str,
    fuser_id: str,
) -> ExternalAuthToken | None:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""
                query GetExternalAuthToken($ws_id: String!, $provider: String!, $fuser_id: String) {
                    external_auth_token(ws_id: $ws_id, provider: $provider, fuser_id: $fuser_id) {
                        access_token
                        expires_at
                        token_type
                        scope_values
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
        )


async def start_external_auth_flow(
    fclient: ckit_client.FlexusClient,
    provider: str,
    ws_id: str,
    fuser_id: str,
    scopes: list[str],
) -> str:
    all_scopes = list(set(scopes))
    try:
        existing_token = await get_external_auth_token(fclient, provider, ws_id, fuser_id)
        if existing_token and existing_token.scope_values:
            all_scopes = list(set(all_scopes + existing_token.scope_values))
    except gql.transport.exceptions.TransportQueryError:
        pass

    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""
                mutation StartExternalAuth($ws_id: String!, $provider: String!, $scope_values: [String!], $fuser_id: String) {
                    external_auth_start(
                        ws_id: $ws_id,
                        provider: $provider,
                        scope_values: $scope_values,
                        fuser_id: $fuser_id
                    ) {
                        authorization_url
                    }
                }"""),
            variable_values={
                "ws_id": ws_id,
                "provider": provider,
                "scope_values": all_scopes,
                "fuser_id": fuser_id,
            }
        )
        return r["external_auth_start"]["authorization_url"]
