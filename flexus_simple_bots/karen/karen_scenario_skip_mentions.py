import asyncio
import logging

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_exec, ckit_scenario_setup, ckit_utils
from flexus_client_kit.integrations.fi_slack_fake import (
    IntegrationSlackFake,
    fake_slack_instances,
    post_fake_slack_message,
    wait_for_bot_message,
)


logger = logging.getLogger("scenario")

karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def scenario(setup: ckit_scenario_setup.ScenarioSetup, use_mcp: bool = False) -> None:
    fake_slack_instances.clear()

    await setup.create_group_and_hire_bot(
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_marketable_version=karen_bot.BOT_VERSION_INT,
        persona_setup={
            "SLACK_BOT_TOKEN": "fake_bot_token",
            "SLACK_APP_TOKEN": "fake_app_token",
            "slack_should_join": "support",
        },
        group_prefix="scenario-skip-mentions",
    )

    bot_task = asyncio.create_task(
        ckit_bot_exec.run_bots_in_this_group(
            setup.bot_fclient,
            fgroup_id=setup.fgroup_id,
            marketable_name=karen_bot.BOT_NAME,
            marketable_version=karen_bot.BOT_VERSION_INT,
            inprocess_tools=karen_bot.TOOLS,
            bot_main_loop=karen_bot.karen_main_loop,
        )
    )
    bot_task.add_done_callback(lambda t: ckit_utils.report_crash(t, logger))

    while not fake_slack_instances:
        await asyncio.sleep(0.1)

    first_message = await post_fake_slack_message(
        "support",
        "Hey Karen, which AWS service should I use for managed PostgreSQL? (capture this thread)",
        user="Alice",
    )
    messages_queue = await setup.subscribe_to_thread_messages(karen_bot.TOOLS)
    capture_msg = await setup.wait_for_toolcall(messages_queue, "slack", None, {"op": "capture"})

    expected_channel = f"support/{first_message['ts']}"
    ft_id = capture_msg.ftm_belongs_to_ft_id
    await wait_for_bot_message(expected_channel)

    await post_fake_slack_message(expected_channel, "@Claire drop the onboarding checklist here?", user="Bob")
    await setup.wait_for_toolcall(messages_queue, "slack", ft_id, {"op": "skip"})

    await post_fake_slack_message(expected_channel, "Sure Bob, here's the checklist: welcome email, VPN setup.", user="Claire")
    await setup.wait_for_toolcall(messages_queue, "slack", ft_id, {"op": "skip"})

    await post_fake_slack_message(expected_channel, "Alice here again—AWS docs for IAM permission boundaries?", user="Alice")
    await wait_for_bot_message(expected_channel)

    slack_instance = fake_slack_instances[0]
    all_slack_messages = [msg for msgs in slack_instance.messages.values() for msg in msgs]
    slack_msgs_from_fthreads = [msg for msg in all_slack_messages if 'ft_id' in msg.get('metadata', {})]
    fthreads_posting = {msg['metadata']['ft_id'] for msg in slack_msgs_from_fthreads if msg.get('thread_ts') == first_message['ts']}
    assert len(fthreads_posting) <= 1, f"Multiple flexus threads posted to same slack thread: {fthreads_posting}"

    slack_thread_messages = [msg for msg in all_slack_messages if msg.get('thread_ts') == first_message['ts']]
    slack_thread_messages.sort(key=lambda x: float(x['ts']))
    bob_idx = next(i for i, msg in enumerate(slack_thread_messages) if msg.get('user') == 'Bob')
    alice_second_idx = next(i for i, msg in enumerate(slack_thread_messages) if msg.get('user') == 'Alice' and i > 0)
    between_messages = slack_thread_messages[bob_idx+1:alice_second_idx]
    bot_msgs_between = [msg for msg in between_messages if msg.get('user') == 'bot']
    assert not bot_msgs_between, f"Bot messages found between Bob and Alice: {bot_msgs_between}, should have been just skipped"


if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("karen")
    asyncio.run(setup.run_scenario(scenario))
