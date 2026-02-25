import logging
import asyncio
import time
import sys
import random
from typing import Callable

import gql.transport.exceptions
import websockets

from flexus_client_kit.core import ckit_client, ckit_shutdown
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
                    logger.info("backend has disconnected gracefully, that's normal for backend upgrades or restarts, will sleep 10-20 seconds and reconnect")
                    await ckit_shutdown.wait(10 + random.randint(0, 10))
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

            err_str = str(e)
            if "460:" in err_str:
                # 460 is custom Flexus error with informative message, no point retrying
                logger.error("%s", e)
                sys.exit(1)
            elif "403:" in err_str:
                logger.error("Authentication failed - key doesn't work: %s", e)
            else:
                nothing = isinstance(e, gql.transport.exceptions.TransportError)
                logger.info("got %s (attempt %d/3), sleep 60...", type(e).__name__, len(exception_times), exc_info=(not nothing))
            await ckit_shutdown.wait(60)

    # logger.info("run_typical_single_subscription_with_restart_on_network_errors(%s) clean exit", fclient.service_name)
