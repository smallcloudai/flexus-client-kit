import json
import logging
from dataclasses import dataclass

import gql
from flexus_client_kit import ckit_client, gql_utils

logger = logging.getLogger("extauth")


@dataclass
class ExternalAuthToken:
    access_token: str | None
    expires_at: int
    token_type: str
    scope_values: list[str]
    auth_url: str | None = None


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
) -> ExternalAuthToken | None:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""
                query GetExternalAuthToken($ws_id: String!, $provider: String!) {
                    external_auth_token(ws_id: $ws_id, provider: $provider) {
                        access_token
                        expires_at
                        token_type
                        scope_values
                    }
                }"""),
            variable_values={
                "ws_id": ws_id,
                "provider": provider,
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
    scopes: list[str],
) -> str:
    http = await fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""
                mutation StartExternalAuth($ws_id: String!, $provider: String!, $scope_values: [String!]) {
                    external_auth_start(
                        ws_id: $ws_id,
                        provider: $provider,
                        scope_values: $scope_values
                    ) {
                        authorization_url
                    }
                }"""),
            variable_values={
                "ws_id": ws_id,
                "provider": provider,
                "scope_values": scopes,
            }
        )
        return r["external_auth_start"]["authorization_url"]
