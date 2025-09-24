import asyncio
import logging
import sys

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_exec, ckit_scenario_setup, ckit_utils, ckit_mcp_server
from flexus_client_kit.integrations.fi_slack_fake import (
    fake_slack_instances,
    IntegrationSlackFake,
    post_fake_slack_message,
    wait_for_bot_message,
)

logger = logging.getLogger("scenario")

karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def scenario(setup: ckit_scenario_setup.ScenarioSetup, use_mcp: bool = False) -> None:
    karen_setup = {
        "SLACK_BOT_TOKEN": "fake_bot_token",
        "SLACK_APP_TOKEN": "fake_app_token",
        "slack_should_join": "support"
    }

    await setup.create_group_hire_and_start_bot(
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_marketable_version=karen_bot.BOT_VERSION_INT,
        persona_setup=karen_setup,
        inprocess_tools=karen_bot.TOOLS,
        bot_main_loop=karen_bot.karen_main_loop,
        group_prefix="scenario-captured-thread"
    )

    if use_mcp:
        mcp_output = await ckit_mcp_server.create_mcp(
            setup.fclient,
            setup.fgroup_id,
            "AWS Documentation",
            "uvx awslabs.aws-documentation-mcp-server@latest",
            "https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/",
            "",
            {"FASTMCP_LOG_LEVEL": "ERROR", "AWS_DOCUMENTATION_PARTITION": "aws"}
        )
        await ckit_mcp_server.wait_for_mcp(setup.fclient, mcp_output.mcp_id)


    first_msg = await post_fake_slack_message("support", "Which service of AWS offers me inference of big models like anthropic models?")
    capture_msg = await setup.wait_for_toolcall("slack", None, {"op": "capture"})

    ft_id = capture_msg.ftm_belongs_to_ft_id
    thread_ts = first_msg["ts"]

    await post_fake_slack_message(f"support/{thread_ts}", "Is there rust SDK for it?")
    await wait_for_bot_message(f"support/{thread_ts}")

    await post_fake_slack_message(f"support/{thread_ts}", "Give me an example of how to invoke model in python to ask it a simple prompt and get result")
    await wait_for_bot_message(f"support/{thread_ts}")

    slack_instance = fake_slack_instances[0]
    assert slack_instance.captured and slack_instance.captured[1] == thread_ts, f"Wrong or no thread captured, expected support/{thread_ts}, got {slack_instance.captured}"

    all_slack_messages = [msg for msgs in slack_instance.messages.values() for msg in msgs]
    slack_msgs_from_fthreads = [msg for msg in all_slack_messages if 'ft_id' in msg.get('metadata', {})]
    fthreads_posting = {msg['metadata']['ft_id'] for msg in slack_msgs_from_fthreads if msg.get('thread_ts') == thread_ts}
    assert len(fthreads_posting) <= 1, f"Multiple flexus threads posted to same slack thread: {fthreads_posting}"


if __name__ == "__main__":
    parser = ckit_scenario_setup.ScenarioSetup.create_args_parser()
    parser.add_argument("--mcp", action="store_true", help="Use MCP server")

    setup = ckit_scenario_setup.ScenarioSetup("karen", parser=parser)
    asyncio.run(setup.run_scenario(scenario, use_mcp=setup.args.mcp))
