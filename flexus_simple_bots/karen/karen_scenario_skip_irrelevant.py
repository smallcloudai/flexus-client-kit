import asyncio
import logging

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_scenario_setup
from flexus_client_kit.integrations.fi_slack_fake import (
    IntegrationSlackFake,
    fake_slack_instances,
    post_fake_slack_message,
    wait_for_bot_messages,
)


logger = logging.getLogger("scenario")

karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def scenario(setup: ckit_scenario_setup.ScenarioSetup) -> None:
    await setup.create_group_hire_and_start_bot(
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_marketable_version=karen_bot.BOT_VERSION_INT,
        persona_setup={
            "SLACK_BOT_TOKEN": "fake_bot_token",
            "SLACK_APP_TOKEN": "fake_app_token",
            "slack_should_join": "support",
        },
        inprocess_tools=karen_bot.TOOLS,
        bot_main_loop=karen_bot.karen_main_loop,
        group_prefix="scenario-skip-irrelevant",
    )

    first_message = await post_fake_slack_message(
        "support",
        "Hey Karen, which AWS service should I use for managed PostgreSQL? (capture this thread)",
        user="Alice",
    )
    capture_msg = await setup.wait_for_toolcall("slack", None, {"op": "capture"})

    expected_channel = f"support/{first_message['ts']}"
    ft_id = capture_msg.ftm_belongs_to_ft_id

    await post_fake_slack_message(expected_channel, "@Claire drop the onboarding checklist here?", user="Bob")
    await setup.wait_for_toolcall("slack", ft_id, {"op": "skip"})

    await post_fake_slack_message(expected_channel, "Sure Bob, here's the checklist: welcome email, VPN setup.", user="Claire")
    await setup.wait_for_toolcall("slack", ft_id, {"op": "skip"})

    await post_fake_slack_message(expected_channel, "Alice here again—AWS docs for IAM permission boundaries?", user="Alice")
    assert len(await wait_for_bot_messages(setup, expected_channel)) > 0

    slack_instance = fake_slack_instances[0]
    all_slack_messages = [msg for msgs in slack_instance.messages.values() for msg in msgs]
    slack_msgs_from_fthreads = [msg for msg in all_slack_messages if 'ft_id' in msg.get('metadata', {})]
    fthreads_posting = {msg['metadata']['ft_id'] for msg in slack_msgs_from_fthreads if msg.get('thread_ts') == first_message['ts']}
    assert len(fthreads_posting) <= 1, f"Multiple flexus threads posted to same slack thread: {fthreads_posting}"

    slack_thread_messages = sorted([msg for msg in all_slack_messages if msg.get('thread_ts') == first_message['ts']], key=lambda x: float(x['ts']))
    slack_message_senders = [msg.get('user', 'unknown') for msg in slack_thread_messages]
    expected = ["Bob", "Claire", "Alice", "bot"]
    assert any(slack_message_senders[i:i+4] == expected for i in range(len(slack_message_senders) - len(expected) + 1)), f"Expected {expected} not found in {slack_message_senders}"


if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("karen")
    asyncio.run(setup.run_scenario(scenario))
