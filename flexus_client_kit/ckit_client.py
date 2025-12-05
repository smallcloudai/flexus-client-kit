import os
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Any, List

import gql
import re
from gql.transport.websockets import WebsocketsTransport
from gql.transport.aiohttp import AIOHTTPTransport

from flexus_client_kit import ckit_logs
from flexus_client_kit import ckit_passwords, gql_utils


logger = logging.getLogger("fclnt")


HELP = """
These environment variables affect execution:

export FLEXUS_API_KEY=fx-******
export FLEXUS_API_BASEURL=https://flexus.team/
"""


FLEXUS_API_BASEURL_DEFAULT = "https://flexus.team/"


class FlexusClient:
    def __init__(self,
        service_name: str,
        *,
        api_key: str = None,
        base_url: Optional[str] = None,   # "http://localhost:8008" if you have local flexus deployment
        endpoint: str = "/v1/graphql",
        skip_logger_init: bool = False,
        superuser: bool = False,
    ):
        if not skip_logger_init:
            ckit_logs.setup_logger()
        have_api_key = api_key or os.getenv("FLEXUS_API_KEY")
        self.use_ws_ticket = os.getenv("FLEXUS_WS_TICKET") is not None
        if superuser:
            assert endpoint != "/v1/graphql", "Whoops superuser set but it's regular endpoint"
            self.api_key = None
        elif self.use_ws_ticket:
            self.api_key = None
        else:
            assert have_api_key, "Set FLEXUS_API_KEY you can generate on your personal profile page."
            assert "superuser" not in endpoint
            self.api_key = have_api_key
        self.base_url_http = base_url or os.getenv("FLEXUS_API_BASEURL", FLEXUS_API_BASEURL_DEFAULT)
        self.base_url_ws = self.base_url_http.replace("https://", "wss://").replace("http://", "ws://")
        self.http_url = self.base_url_http.rstrip("/") + endpoint
        self.websocket_url = self.base_url_ws.rstrip("/") + endpoint
        self.endpoint = endpoint
        self.service_name = service_name
        self.ws_id = os.getenv("FLEXUS_WORKSPACE")
        if os.getenv("FLEXUS_IS_RADIX_WORKSPACE") and self.ws_id:
            self.service_name = f"{self.service_name}_r_{self.ws_id}"

        logger.info("FlexusClient service_name=%s api_key=%s %s", self.service_name, ("..." + self.api_key[-4:]) if self.api_key else "None", self.http_url)
        if have_api_key:
            assert not have_api_key.startswith("http:")
        assert not self.base_url_http.startswith("fx-")

    async def use_http(self, execute_timeout: float = 10) -> gql.Client:
        if self.api_key is not None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "x-flexus-service-name": self.service_name,
            }
        elif self.use_ws_ticket:
            ws_ticket = await ckit_passwords.get_flexus_ws_ticket(self.service_name)
            headers = {
                "x-flexus-ws-ticket": ws_ticket,
                "x-flexus-service-name": self.service_name
            }
        else:
            superpassword_curr, _ = await ckit_passwords.get_superuser_token_from_vault(self.endpoint)
            headers = {
                "x-flexus-superuser": superpassword_curr,
                "x-flexus-service-name": self.service_name,
            }
        transport = AIOHTTPTransport(url=self.http_url, headers=headers)
        return gql.Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=execute_timeout)

    async def use_ws(self) -> gql.Client:
        if self.api_key is not None:
            payload = {
                "apikey": self.api_key,
                "x-flexus-service-name": self.service_name,
            }
        elif self.use_ws_ticket:
            ws_ticket = await ckit_passwords.get_flexus_ws_ticket(self.service_name)
            payload = {
                "x-flexus-ws-ticket": ws_ticket,
                "x-flexus-service-name": self.service_name
            }
        else:
            superpassword_curr, _ = await ckit_passwords.get_superuser_token_from_vault(self.endpoint)
            payload = {
                "x-flexus-superuser": superpassword_curr,
                "x-flexus-service-name": self.service_name,
            }
        transport = WebsocketsTransport(url=self.websocket_url, init_payload=payload)
        return gql.Client(transport=transport, fetch_schema_from_transport=False)


def marketplace_version_as_int(v: str) -> int:
    if not re.match(r'^\d{1,4}\.\d{1,4}\.\d{1,4}$', v):
        raise ValueError('bad version')
    a, b, c = [int(x) for x in v.split('.')]
    return a * 100_000_000 + b * 10_000 + c


def marketplace_version_as_str(v: int) -> str:
    a = v // 100_000_000
    remainder = v % 100_000_000
    b = remainder // 10_000
    c = remainder % 10_000
    return f"{a}.{b}.{c}"


def bot_service_name(bot_name: str, bot_version: str):
    assert isinstance(bot_version, str)
    bot_version_int = marketplace_version_as_int(bot_version)
    return f"{bot_name}_{bot_version_int}"


@dataclass
class FWorkspaceInvitationOutput:
    wsi_id: str
    wsi_invite_fuser_id: str
    wsi_invited_by_fuser_id: str
    wsi_fgroup_id: str
    wsi_roles: int
    group_name: str


@dataclass
class FWorkspaceOutput:
    ws_id: str
    ws_owner_fuser_id: str
    ws_root_group_id: str
    ws_archived_ts: float
    ws_created_ts: float
    root_group_name: str
    have_admin: bool
    have_coins_exactly: int
    have_coins_enough: bool


@dataclass
class BasicStuffOutput:
    fuser_id: str
    workspaces: List[FWorkspaceOutput]
    my_own_ws_id: Optional[str]
    invitations: Optional[List[FWorkspaceInvitationOutput]]
    fuser_psystem: Optional[Any]
    is_oauth: bool


async def query_basic_stuff(
    client: FlexusClient,
    want_invitations: bool = False,
) -> BasicStuffOutput:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(f"""query CkitClientTest($w: Boolean!) {{
                query_basic_stuff(want_invitations: $w) {{
                    {gql_utils.gql_fields(BasicStuffOutput)}
                }}
            }}"""),
            variable_values={"w": want_invitations},
        )
        return gql_utils.dataclass_from_dict(r["query_basic_stuff"], BasicStuffOutput)


async def test() -> None:
    client = FlexusClient("ckit_client_test", api_key="sk_alice_123456")
    r = await query_basic_stuff(client, True)
    print("Look, Alice has %d workspaces!" % len(r.workspaces))
    for ws in r.workspaces:
        print("  Workspace %r has %d coins" % (ws.ws_id, ws.have_coins_exactly))
    print("Full response:", r)


if __name__ == "__main__":
    asyncio.run(test())
