import logging
import asyncio
from typing import Callable

import gql.transport.exceptions
import websockets

from flexus_client_kit import ckit_client, ckit_shutdown
logger = logging.getLogger("stexe")

assert "TransportConnectionFailed" in dir(gql.transport.exceptions), "pip install -U gql websockets"


async def run_typical_single_subscription_with_restart_on_network_errors(fclient: ckit_client.FlexusClient, subscribe_and_do_something: Callable, *func_args, **func_kwargs):
    ckit_shutdown.setup_signals()
    while not ckit_shutdown.shutdown_event.is_set():
        try:
            logger.info("Connecting %s", fclient.websocket_url)
            ws_client = await fclient.use_ws()
            try:
                ckit_shutdown.give_ws_client(fclient.service_name, ws_client)
                await subscribe_and_do_something(fclient, ws_client, *func_args, **func_kwargs)
                assert ckit_shutdown.shutdown_event.is_set()  # the only way we get there
            finally:
                ckit_shutdown.take_away_ws_client(fclient.service_name)

        except (websockets.exceptions.ConnectionClosedError,
                OSError,
                gql.transport.exceptions.TransportConnectionFailed,
                gql.transport.exceptions.TransportQueryError,   # "Server disconnected without sending a response" goes here
                asyncio.exceptions.TimeoutError,
        ) as e:
            if ckit_shutdown.shutdown_event.is_set():
                break
            logger.info("got %s, sleep 60..." % (type(e).__name__,))
            await ckit_shutdown.wait(60)
