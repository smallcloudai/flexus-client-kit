import asyncio
import logging
import time
import os
import httpx
from collections import defaultdict
from typing import Tuple


logger = logging.getLogger("super")


it_might_be_a_devbox = True

_superpassword_curr = dict()
_superpassword_prev = dict()
_superpassword_expires = defaultdict(int)
_superpassword_lock = asyncio.Lock()

SUPERUSER_PASSWORD_CACHE_TTL = 300


async def get_superuser_token_from_vault(endpoint: str, force: bool = False) -> Tuple[str, str]:
    global _superpassword_curr, _superpassword_prev, _superpassword_expires
    t = time.time()
    if t < _superpassword_expires[endpoint] and not force:
        return _superpassword_curr[endpoint], _superpassword_prev[endpoint]

    async with _superpassword_lock:
        if t < _superpassword_expires[endpoint] and not force:  # Check again, the same condition
            return _superpassword_curr[endpoint], _superpassword_prev[endpoint]

        # Cache miss branch, only one coroutine fetches the new password
        if (VAULT_ENDPOINT := os.environ.get("VAULT_ENDPOINT", None)) is not None:
            vault_token = open("/vault/token/token", "r").read().strip()
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(f"{VAULT_ENDPOINT}/v1/kv/data/flexus{endpoint}", headers={"X-Vault-Token": vault_token}, timeout=3.0)
                except Exception as e:
                    logger.error(f"Error fetching superuser token from vault: {e}", exc_info=True)
                    raise RuntimeError("Whoops sorry but it's really an Internal Server Error here.")
                if r.status_code == 200:
                    _superpassword_curr[endpoint] = r.json()["data"]["data"]["current"]
                    _superpassword_prev[endpoint] = r.json()["data"]["data"]["previous"]
                    _superpassword_expires[endpoint] = t + SUPERUSER_PASSWORD_CACHE_TTL
                else:
                    logger.error(f"Fetching superuser token from vault status is {r.status_code}, response: {r.text[:100]}...", stack_info=True)  # prints less than password length just in case
                    raise RuntimeError("Whoops sorry but it's really an Internal Server Error here.")

        else: # VAULT_ENDPOINT is not set => devbox
            if not it_might_be_a_devbox:
                raise RuntimeError("OMG it's not really a devbox?")
            _superpassword_curr[endpoint] = "curr-secret-password-for-" + endpoint
            _superpassword_prev[endpoint] = "prev-secret-password-for-" + endpoint
            _superpassword_expires[endpoint] = t + SUPERUSER_PASSWORD_CACHE_TTL

    return _superpassword_curr[endpoint], _superpassword_prev[endpoint]


async def get_flexus_ws_ticket(service_name: str):
    ticket_path = f"/tmp/{service_name}_flexus_ticket"
    if os.path.exists(ticket_path):
        return open(ticket_path, "r").read().strip()
    return os.environ['FLEXUS_WS_TICKET']
