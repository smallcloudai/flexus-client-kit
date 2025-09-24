import asyncio
import logging
import json

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_scenario_setup, ckit_ask_model
from flexus_client_kit.integrations.fi_slack_fake import (
    IntegrationSlackFake,
    fake_slack_instances,
    post_fake_slack_message,
    wait_for_bot_messages,
)

STALE_INACTIVITY_REMINDER = "Inactivity timeout after %s. The task %s is still assigned to this chat. Follow the system prompt to resolve the task."

logger = logging.getLogger("scenario")

karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def send_reminder(setup, ft_id, task_id):
    http = await setup.fclient.use_http()
    await ckit_ask_model.thread_add_user_message(
        http=http,
        ft_id=ft_id,
        content=STALE_INACTIVITY_REMINDER % ("2m", task_id),
        who_is_asking="service_scheduler",
        ftm_alt=100,
        user_preferences="null",
        role="cd_instruction",
    )


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
        group_prefix="scenario-close-after-reminder",
    )

    first_message = await post_fake_slack_message(
        "support",
        "Hey Karen, I need AWS documentation about IAM roles.",
        user="Alice",
    )
    capture_msg = await setup.wait_for_toolcall("slack", None, {"op": "capture"})

    expected_channel = f"support/{first_message['ts']}"
    ft_id = capture_msg.ftm_belongs_to_ft_id

    assign_msg = await setup.wait_for_toolcall("flexus_bot_kanban", ft_id, {"op": "assign_to_this_chat"}, allow_existing_toolcall=True)
    assign_args = json.loads(assign_msg.ftm_tool_calls[0]["function"]["arguments"])
    task_id = assign_args["args"]["batch"][0]

    await send_reminder(setup, ft_id, task_id)
    assert len(await wait_for_bot_messages(setup, expected_channel)) > 0

    slack_instance = fake_slack_instances[0]
    slack_thread_messages_before = [msg for msgs in slack_instance.messages.values() for msg in msgs if msg.get('thread_ts') == first_message['ts']]
    bot_msgs_count_before = len([msg for msg in slack_thread_messages_before if msg.get('user') == 'bot'])

    await send_reminder(setup, ft_id, task_id)
    await setup.wait_for_toolcall("flexus_bot_kanban", ft_id, {"op": "current_task_done"})

    slack_thread_messages_after = [msg for msgs in slack_instance.messages.values() for msg in msgs if msg.get('thread_ts') == first_message['ts']]
    bot_msgs_count_after = len([msg for msg in slack_thread_messages_after if msg.get('user') == 'bot'])
    assert bot_msgs_count_after == bot_msgs_count_before, f"Expected no new bot messages after kanban call, but found {bot_msgs_count_after - bot_msgs_count_before} more"


if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("karen")
    asyncio.run(setup.run_scenario(scenario))
