#!/usr/bin/env python
import asyncio
import argparse
import subprocess
import sys
import logging
import hmac
import hashlib
import os

from flexus_client_kit import ckit_client, ckit_bot_query

logger = logging.getLogger("run_bots_in_ws")


def start_bot_process(persona: ckit_bot_query.FPersonaOutput, ws_id: str, superpassword: str) -> subprocess.Popen:
    service_name = f"{persona.persona_marketable_name}_{persona.persona_marketable_version}_{persona.located_fgroup_id}"
    message = f'{service_name}:{ws_id}'
    ws_ticket = f'{service_name}:{ws_id}:{hmac.new(superpassword.encode(), message.encode(), hashlib.sha256).hexdigest()}'

    module_path = persona.marketable_run_this.replace("python -m ", "") if persona.marketable_run_this.startswith("python -m ") else persona.marketable_run_this

    logger.info(f"Starting {persona.persona_name} ({persona.persona_id}) in {persona.located_fgroup_id}")

    env = os.environ.copy()
    env['FLEXUS_SERVICE_NAME'] = service_name
    env['FLEXUS_WS_TICKET'] = ws_ticket

    return subprocess.Popen(
        [sys.executable, "-m", module_path, "--group", persona.located_fgroup_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )


async def main():
    parser = argparse.ArgumentParser(description="Run all bots in a workspace")
    parser.add_argument("--ws", required=True, help="Workspace ID")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s [%(levelname)s] %(message)s", datefmt="%Y%m%d %H:%M:%S")

    fclient = ckit_client.FlexusClient(service_name=f"run_bots_in_ws_{args.ws}", endpoint="/v1/graphql")
    personas = await ckit_bot_query.personas_in_ws_list(fclient, args.ws)

    if not personas:
        logger.error("No active personas with marketable_run_this found")
        return

    logger.info(f"Starting {len(personas)} bot(s)...")

    superpassword = "curr-secret-password-for-/v1/jailed-bot"
    processes = []
    for persona in personas:
        try:
            processes.append((persona, start_bot_process(persona, args.ws, superpassword)))
        except Exception as e:
            logger.error(f"Failed to start bot {persona.persona_name}: {e}")

    if not processes:
        return

    try:
        while True:
            for persona, proc in list(processes):
                if proc.poll() is not None:
                    logger.warning(f"Bot {persona.persona_name} exited with code {proc.returncode}")
                    processes.remove((persona, proc))
                elif line := proc.stdout.readline():
                    print(f"[{persona.persona_name[:5]:5s}] {line.rstrip()}")

            if not processes:
                break

            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Stopping all bots...")
        for persona, proc in processes:
            proc.terminate()
        await asyncio.sleep(2)
        for persona, proc in processes:
            if proc.poll() is None:
                proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
