import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_install
from flexus_simple_bots.frog import frog_install

logger = logging.getLogger("bot_frog")


BOT_NAME = "frog"
BOT_VERSION = "0.1.0"


RIBBIT_TOOL = ckit_cloudtool.CloudTool(
    name="ribbit",
    description="Make a frog sound to greet users or express happiness.",
    parameters={
        "type": "object",
        "properties": {
            "intensity": {"type": "string", "enum": ["quiet", "normal", "loud"], "description": "How loud the ribbit should be"},
            "message": {"type": "string", "description": "Optional message to include with the ribbit"},
        },
        "required": ["intensity"],
    },
)

CATCH_INSECTS_TOOL = ckit_cloudtool.CloudTool(
    name="catch_insects",
    description="Catch insects in parallel.",
    parameters={
        "type": "object",
        "properties": {
            "N": {"type": "integer", "description": "Number of parallel catch attempts (1-50)"},
        },
        "required": ["N"],
    },
)

TOOLS = [
    RIBBIT_TOOL,
    CATCH_INSECTS_TOOL,
]


async def frog_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(frog_install.frog_setup_default, rcx.persona.persona_setup)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(RIBBIT_TOOL.name)
    async def toolcall_ribbit(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        intensity = model_produced_args.get("intensity", "normal")
        message = model_produced_args.get("message", "")

        ribbit_sound = {
            "quiet": "ribbit...",
            "normal": "RIBBIT!",
            "loud": "RIBBIT RIBBIT RIBBIT!!!"
        }.get(intensity, "RIBBIT!")

        result = ribbit_sound
        if message:
            result += f" {message}"

        logger.info(f"Frog says: {result}")
        return result

    @rcx.on_tool_call(CATCH_INSECTS_TOOL.name)
    async def toolcall_catch_insects(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        N = model_produced_args.get("N", 1)
        if not isinstance(N, int) or N < 1 or N > 50:
            return "Error: N must be an integer between 1 and 50"

        # Create parallel subchats to catch insects
        first_questions = [f"Catch insect #{i+1} by flicking tongue!" for i in range(N)]
        first_calls = ["null" for _ in range(N)]
        titles = [f"Catching insect #{i+1}" for i in range(N)]

        if 1:
            await ckit_ask_model.bot_subchat_create_multiple(
                fclient,
                "frog_catch_insects",
                rcx.persona.persona_id,
                first_questions,
                first_calls,
                titles,
                toolcall.fcall_ft_id,
                toolcall.fcall_ftm_alt,
                toolcall.fcall_called_ftm_num,
                toolcall.fcall_call_n,
            )
            return "WAIT_SUBCHATS"
        else:
            return f"Unsuccessfully launched {N} parallel insect-catching subchats!"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseurl", default="", help="Base URL for the Flexus API")
    parser.add_argument("--group", type=str, required=True, help="Flexus group ID where the bot will run, take it from the address bar in the browser when you are looking on something inside a group.")
    parser.add_argument("--apikey", type=str, help="Your personal API key is suitable for a dev bot")
    args = parser.parse_args()
    ENCODED_BOT_VERSION = ckit_bot_install.encode_market_version(BOT_VERSION)
    fclient = ckit_client.FlexusClient(
        f"{BOT_NAME}_{ENCODED_BOT_VERSION}_{args.group}",
        base_url=args.baseurl,
        endpoint="/v1/superuser-bot",
        api_key=args.apikey,
        use_ws_ticket=args.apikey is None
    )

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=ENCODED_BOT_VERSION,
        fgroup_id=args.group,
        bot_main_loop=frog_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()