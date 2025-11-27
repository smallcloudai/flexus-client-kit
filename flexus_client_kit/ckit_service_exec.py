import logging
import asyncio
import time
from typing import Callable

import gql.transport.exceptions
import websockets

from flexus_client_kit import ckit_client, ckit_shutdown
logger = logging.getLogger("stexe")

assert "TransportConnectionFailed" in dir(gql.transport.exceptions), "pip install -U gql websockets"


async def run_typical_single_subscription_with_restart_on_network_errors(fclient: ckit_client.FlexusClient, subscribe_and_do_something: Callable, *func_args, **func_kwargs):
    ckit_shutdown.setup_signals()
    exception_times = []

    while not ckit_shutdown.shutdown_event.is_set():
        try:
            logger.info("Connecting %s", fclient.websocket_url)
            ws_client = await fclient.use_ws()
            try:
                ckit_shutdown.give_ws_client(fclient.service_name, ws_client)
                await subscribe_and_do_something(fclient, ws_client, *func_args, **func_kwargs)
                if not ckit_shutdown.shutdown_event.is_set():
                    logger.error("🛑 The only way we get there is shutdown, what happened?")
            finally:
                ckit_shutdown.take_away_ws_client(fclient.service_name)

        except (
            websockets.exceptions.ConnectionClosedError,
            gql.transport.exceptions.TransportError,
            OSError,
            asyncio.exceptions.TimeoutError,
        ) as e:
            if ckit_shutdown.shutdown_event.is_set():
                break

            n = time.time()
            exception_times = [t for t in exception_times if n - t < 300] + [n]
            if len(exception_times) >= 3:
                logger.exception("3 exceptions in 5 min, exiting")
                raise

            if "403:" in str(e):
                logger.error("That looks bad, my key doesn't work: %s", e)
            else:
                nothing = isinstance(e, gql.transport.exceptions.TransportConnectionFailed)
                logger.info("got %s (attempt %d/3), sleep 60...", type(e).__name__, len(exception_times), exc_info=(not nothing))
            await ckit_shutdown.wait(60)

    # logger.info("run_typical_single_subscription_with_restart_on_network_errors(%s) clean exit", fclient.service_name)
