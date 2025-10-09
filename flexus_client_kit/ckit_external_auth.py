import json
import logging
from dataclasses import dataclass
from typing import Optional
import gql
from flexus_client_kit import ckit_client, gql_utils

logger = logging.getLogger("extauth")


@dataclass
class ExternalAuth:
    auth_id: str
    # auth_searchable: str
    auth_name: str
    auth_auth_type: str
    auth_service_provider: str
    # auth_json: dict
    auth_expires_ts: float


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
