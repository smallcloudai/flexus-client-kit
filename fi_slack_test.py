import asyncio
import os
import time

import pytest
from slack_sdk.web.async_client import AsyncWebClient

from flexus_client_kit import ckit_bot_exec, ckit_client
from flexus_client_kit.integrations.fi_slack import IntegrationSlack


def _make_slack() -> IntegrationSlack:
    bot = os.getenv("SLACK_BOT_TOKEN")
    app = os.getenv("SLACK_APP_TOKEN")
    api = os.getenv("FLEXUS_API_KEY")
    base = os.getenv("FLEXUS_URL", "https://flexus.team")
    if not (bot and app and api):
        pytest.skip("Missing SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_USER_TOKEN or FLEXUS_API_KEY")
    fclient = ckit_client.FlexusClient(
        "fi_slack_test", base_url=base, api_key=api, skip_logger_init=True
    )
    persona = ckit_bot_exec.FPersonaOutput(
        owner_fuser_id="o",
        located_fgroup_id="g",
        persona_id="p",
        persona_name="p",
        persona_marketable_name="p",
        persona_marketable_version=1,
        persona_discounts=None,
        persona_setup={},
        persona_created_ts=0.0,
        ws_id="w",
        ws_timezone="UTC",
    )
    rcx = ckit_bot_exec.RobotContext(fclient, persona)
    return IntegrationSlack(fclient, rcx, bot, app, "")


@pytest.mark.asyncio
async def test_slack_message_calls_callback():
    slack_bot = _make_slack()
    got = asyncio.Event()
    seen = {}

    async def cb(activity, already_posted_to_captured_thread):
        print("activity:", activity)
        assert already_posted_to_captured_thread == False
        seen["text"] = activity.message_text
        got.set()

    slack_bot.set_activity_callback(cb)
    await slack_bot.start_reactive()
    await asyncio.sleep(10)
    try:
        user_web = AsyncWebClient(token=os.environ["SLACK_USER_TOKEN"])
        bot_web = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])

        bot_auth = await bot_web.auth_test()
        dm = await user_web.conversations_open(users=bot_auth["user_id"])

        text = f"hi {time.time()}"
        await user_web.chat_postMessage(channel=dm["channel"]["id"], text=text)
        await asyncio.wait_for(got.wait(), 30)
        assert seen.get("text") == text
    finally:
        await slack_bot.close()
