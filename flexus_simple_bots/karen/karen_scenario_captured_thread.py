import asyncio
import sys
import traceback

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_exec, ckit_scenario_setup
from flexus_client_kit.integrations.fi_slack_fake import (
    FAKE_SLACK_INSTANCES,
    IntegrationSlackFake,
    post_fake_slack_message,
    wait_for_bot_message,
)

karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def scenario(setup: ckit_scenario_setup.ScenarioSetup, use_mcp: bool = False) -> None:
    karen_setup = {
        "SLACK_BOT_TOKEN": "fake_bot_token",
        "SLACK_APP_TOKEN": "fake_app_token",
        "slack_should_join": "support"
    }

    await setup.setup(
        persona_name=karen_bot.BOT_NAME,
        persona_setup=karen_setup,
        persona_require_dev=True,
        persona_marketable_version=karen_bot.BOT_VERSION_INT,
        group_prefix="scenario-captured-thread"
    )

    if use_mcp:
        mcp_id = await setup.create_mcp(
            "AWS Documentation",
            "uvx awslabs.aws-documentation-mcp-server@latest",
            "https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/",
            {"FASTMCP_LOG_LEVEL": "ERROR", "AWS_DOCUMENTATION_PARTITION": "aws"}
        )
        await setup.wait_for_mcp(mcp_id)

    bot_task = asyncio.create_task(ckit_bot_exec.run_bots_in_this_group(
        setup.bot_fclient,
        fgroup_id=setup.fgroup_id,
        marketable_name=karen_bot.BOT_NAME,
        marketable_version=karen_bot.BOT_VERSION_INT,
        inprocess_tools=karen_bot.TOOLS,
        bot_main_loop=karen_bot.karen_main_loop,
    ))
    bot_task.add_done_callback(lambda t: t.exception() and traceback.print_exception(type(t.exception()), t.exception(), t.exception().__traceback__))

    while not FAKE_SLACK_INSTANCES:
        await asyncio.sleep(0.1)

    first_msg = await post_fake_slack_message("support", "Which service of AWS offers me inference of big models like anthropic models?")
    await wait_for_bot_message("support")
    assert "ts" in first_msg
    thread_ts = first_msg["ts"]

    await post_fake_slack_message(f"support/{thread_ts}", "Is there rust SDK for it?")
    await wait_for_bot_message(f"support/{thread_ts}")
    await post_fake_slack_message(f"support/{thread_ts}", "Give me example of how to invoke model in python to ask it a simple prompt and get result")
    await wait_for_bot_message(f"support/{thread_ts}")

    slack_instance = FAKE_SLACK_INSTANCES[0]
    assert slack_instance.captured and slack_instance.captured[1] == thread_ts, f"Wrong or no thread captured, expected support/{thread_ts}, got {slack_instance.captured}"

    all_messages = [msg for msgs in slack_instance.messages.values() for msg in msgs]
    msgs_from_fthreads = [msg for msg in all_messages if 'ft_id' in msg.get('metadata', {})]
    fthreads_posting = {msg['metadata']['ft_id'] for msg in msgs_from_fthreads if msg.get('thread_ts') == thread_ts}
    assert len(fthreads_posting) <= 1, f"Multiple flexus threads posted to same slack thread: {fthreads_posting}"


if __name__ == "__main__":
    use_mcp = "--mcp" in sys.argv
    setup = ckit_scenario_setup.ScenarioSetup("karen")
    asyncio.run(setup.run_scenario(scenario, use_mcp=use_mcp))
