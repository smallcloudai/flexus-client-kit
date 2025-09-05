import asyncio
import os
import time
import pytest
from slack_sdk.web.async_client import AsyncWebClient
from flexus_client_kit import ckit_bot_exec, ckit_client
from flexus_client_kit.integrations.fi_slack import ActivitySlack, IntegrationSlack


def _create_slack_bot() -> IntegrationSlack:
    required = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "FLEXUS_API_KEY"]
    if not all(os.getenv(env) for env in required):
        pytest.skip(f"Missing: {', '.join(required)}")

    fclient = ckit_client.FlexusClient(
        "fi_slack_test",
        base_url=os.getenv("FLEXUS_URL", "https://flexus.team"),
        api_key=os.getenv("FLEXUS_API_KEY"),
        skip_logger_init=True,
    )
    persona = ckit_bot_exec.FPersonaOutput(
        owner_fuser_id="test", located_fgroup_id="test", persona_id="test",
        persona_name="test", persona_marketable_name="test", persona_marketable_version=1,
        persona_discounts=None, persona_setup={}, persona_created_ts=0.0,
        ws_id="test", ws_timezone="UTC"
    )
    rcx = ckit_bot_exec.RobotContext(fclient, persona)
    return IntegrationSlack(fclient, rcx, os.getenv("SLACK_BOT_TOKEN"), os.getenv("SLACK_APP_TOKEN"), "tests")


@pytest.mark.asyncio
async def test_slack_message_calls_callback():
    slack_bot = _create_slack_bot()
    result = {"text": None, "event": asyncio.Event()}

    async def callback(activity: ActivitySlack, already_posted_to_captured_thread: bool):
        assert isinstance(activity, ActivitySlack) and already_posted_to_captured_thread == False
        result["text"] = activity.message_text
        result["event"].set()

    slack_bot.set_activity_callback(callback)
    await slack_bot.join_channels()  # Join the "tests" channel
    await slack_bot.start_reactive()

    try:
        user_client = AsyncWebClient(token=os.environ["SLACK_USER_TOKEN"])
        bot_client = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])

        # Test 1: DM message
        bot_info = await bot_client.auth_test()
        dm = await user_client.conversations_open(users=bot_info["user_id"])
        dm_message = f"dm_test_{time.time()}"
        await user_client.chat_postMessage(channel=dm["channel"]["id"], text=dm_message)

        await asyncio.wait_for(result["event"].wait(), timeout=30)
        assert result["text"] == dm_message
        print("✓ DM test passed")

        # Test 2: Channel message (bot should already be in "tests" channel)
        result["text"] = None
        result["event"].clear()

        tests_channel_id = slack_bot.channels_name2id.get("tests")
        channel_message = f"channel_test_{time.time()}"
        await user_client.chat_postMessage(channel=tests_channel_id, text=channel_message)

        await asyncio.wait_for(result["event"].wait(), timeout=30)
        assert result["text"] == channel_message
        print("✓ Channel test passed")

    finally:
        await slack_bot.close()
        try:
            await bot_client.conversations_leave(channel=tests_channel_id)
            print("✓ Bot left #tests channel")
        except Exception as e:
            print(f"⚠️  Failed to leave channel: {e}")


if __name__ == "__main__":
    asyncio.run(test_slack_message_calls_callback())
