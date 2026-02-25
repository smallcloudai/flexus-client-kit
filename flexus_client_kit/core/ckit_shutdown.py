import asyncio
import logging
import signal
import sys
from typing import Dict

import gql

logger = logging.getLogger("cshut")

shutdown_event = asyncio.Event()


# Websocket clients are especially problematic for shutdown, because they sleep on their websocket
# transport recv() without looking at anything
ws_clients: Dict[str, gql.Client] = {}
tasks_to_cancel: Dict[str, asyncio.Task] = {}

def give_ws_client(under_name: str, ws_client: gql.Client):
    ws_clients[under_name] = ws_client

def take_away_ws_client(under_name: str) -> gql.Client:
    ws_clients.pop(under_name)

def give_task_to_cancel(under_name: str, task: asyncio.Task):
    tasks_to_cancel[under_name] = task

def take_away_task_to_cancel(under_name: str) -> asyncio.Task:
    return tasks_to_cancel.pop(under_name)


def spiral_down_now(loop, enable_exit1):
    if shutdown_event.is_set() and enable_exit1:
        logger.info("exit(1)")
        sys.exit(1)
    shutdown_event.set()
    for k, ws_client in ws_clients.items():
        logger.info("ws close %r" % k)
        # Luckily, there is a way to kick them from outside
        loop.create_task(ws_client.transport.close())
    for k, task in tasks_to_cancel.items():
        logger.info("task cancel %r" % k)
        task.cancel()


def setup_signals():
    loop = asyncio.get_running_loop()

    def h():
        logger.info(f"✋ Got signal")
        spiral_down_now(loop, enable_exit1=True)

    try:
        loop.add_signal_handler(signal.SIGINT, h)
        loop.add_signal_handler(signal.SIGTERM, h)
    except NotImplementedError:
        # Fallback for Windows - signal.signal works everywhere but is sync
        def windows_handler(signum, frame):
            h()
        signal.signal(signal.SIGINT, windows_handler)
        signal.signal(signal.SIGTERM, windows_handler)


async def wait(timeout: float) -> bool:
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        return False
