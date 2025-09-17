import asyncio
import contextlib
import json
import sys
import traceback

import gql

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_exec, ckit_scenario_setup
from flexus_client_kit.integrations.fi_slack_fake import (
    FAKE_SLACK_INSTANCES,
    IntegrationSlackFake,
    post_fake_slack_message,
    wait_for_bot_message,
)


karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake




async def run_scenario(use_mcp: bool = False) -> None:
    setup = ckit_scenario_setup.ScenarioSetup("karen")
    karen_setup = {
        "SLACK_BOT_TOKEN": "fake_bot_token",
        "SLACK_APP_TOKEN": "fake_app_token",
        "slack_should_join": "support"
    }

    bot_task = None
    try:
        rcx, _mongo_collection = await setup.setup(karen_bot.BOT_NAME, karen_setup, require_dev=True, prefix="scenario-captured-thread")

        if use_mcp:
            mcp_id = await setup.create_mcp(
                "AWS Documentation",
                "uvx awslabs.aws-documentation-mcp-server@latest",
                "https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/",
                {"FASTMCP_LOG_LEVEL": "ERROR", "AWS_DOCUMENTATION_PARTITION": "aws"}
            )
            print(f"Created test group {setup.fgroup_id} with MCP {mcp_id}")

            print("Waiting for MCP server to be ready...")
            if not await setup.wait_for_mcp(mcp_id):
                print("⚠️ MCP server failed to start within timeout")
            else:
                print("✓ MCP server is ready")
        else:
            print(f"Created test group {setup.fgroup_id} without MCP")

        bot_task = asyncio.create_task(ckit_bot_exec.run_bots_in_this_group(
            setup.bot_fclient,
            fgroup_id=setup.fgroup_id,
            marketable_name=karen_bot.BOT_NAME,
            marketable_version=karen_bot.BOT_VERSION_INT,
            inprocess_tools=karen_bot.TOOLS,
            bot_main_loop=karen_bot.karen_main_loop,
        ))

        while not FAKE_SLACK_INSTANCES:
            if bot_task.done():
                exc = bot_task.exception()
                exc and traceback.print_exception(type(exc), exc, exc.__traceback__) or bot_task.result()
            await asyncio.sleep(0.1)

        first_msg = await post_fake_slack_message("support", "Which service of AWS offers me inference of big models like anthropic models?")
        await wait_for_bot_message("support")
        assert "ts" in first_msg
        thread_ts = first_msg["ts"]

        await post_fake_slack_message(f"support/{thread_ts}", "Is there rust SDK for it?")
        await wait_for_bot_message(f"support/{thread_ts}")
        await post_fake_slack_message(f"support/{thread_ts}", "Give me example of how to invoke model in python to ask it a simple prompt and get result")
        await wait_for_bot_message(f"support/{thread_ts}")

        print("Test completed successfully. Waiting 5 minutes before cleanup...")
        await asyncio.sleep(300)

    except TimeoutError:
        print("Timed out, no answer :/")
    except KeyboardInterrupt:
        print("Test interrupted by user. Starting cleanup...")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if bot_task:
            bot_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await bot_task
        await setup.cleanup()
        print("Cleanup completed.")


if __name__ == "__main__":
    use_mcp = "--mcp" in sys.argv
    asyncio.run(run_scenario(use_mcp))

