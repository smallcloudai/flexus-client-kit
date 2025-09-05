import asyncio
import json
import os
import time
import pytest
from PIL import Image
from slack_sdk.web.async_client import AsyncWebClient
from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_cloudtool
from flexus_client_kit.integrations.fi_slack import ActivitySlack, IntegrationSlack


def _create_test_files():
    test_dir = f'/tmp/bot_workspace/persona_id'
    os.makedirs(test_dir, exist_ok=True)
    img1 = Image.new('RGB', (100, 100), color='red')
    img1.save(f'{test_dir}/1.png')
    img2 = Image.new('RGB', (100, 100), color='blue')
    img2.save(f'{test_dir}/2.png')
    with open(f'{test_dir}/1.txt', 'w') as f:
        f.write('This is test file 1\nWith multiple lines\nFor testing file attachments')
    with open(f'{test_dir}/2.json', 'w') as f:
        f.write('{"test": "data", "file": "2", "content": "json test file"}')
    return test_dir


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
        owner_fuser_id="test", located_fgroup_id="test", persona_id="persona_id",
        persona_name="test", persona_marketable_name="test", persona_marketable_version=1,
        persona_discounts=None, persona_setup={}, persona_created_ts=0.0,
        ws_id="test", ws_timezone="UTC"
    )
    rcx = ckit_bot_exec.RobotContext(fclient, persona)
    return IntegrationSlack(fclient, rcx, os.getenv("SLACK_BOT_TOKEN"), os.getenv("SLACK_APP_TOKEN"), "tests")


async def _setup_slack_test():
    test_dir = _create_test_files()
    slack_bot = _create_slack_bot()
    result = {"activity": None, "event": asyncio.Event(), "test_dir": test_dir}

    async def callback(activity: ActivitySlack, already_posted_to_captured_thread: bool):
        assert isinstance(activity, ActivitySlack) and already_posted_to_captured_thread == False
        result["activity"] = activity
        result["event"].set()

    slack_bot.set_activity_callback(callback)
    await slack_bot.join_channels()
    await slack_bot.start_reactive()

    user_client = AsyncWebClient(token=os.environ["SLACK_USER_TOKEN"])
    bot_client = AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"])

    async def bot_cleanup():
        await slack_bot.close()
        for channel_name in slack_bot.actually_joined:
            channel_id = slack_bot.channels_name2id.get(channel_name)
            if channel_id:
                try:
                    await bot_client.conversations_leave(channel=channel_id)
                    print(f"✓ Bot left #{channel_name}")
                except Exception as e:
                    print(f"⚠️  Failed to leave #{channel_name}: {e}")

    return slack_bot, result, user_client, bot_client, bot_cleanup


async def _upload_files(user_client: AsyncWebClient, channel_id: str, file_paths: list[str], message: str):
    file_uploads = []
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            file_uploads.append({"file": f.read(), "filename": filename})

    await user_client.files_upload_v2(
        channel=channel_id,
        file_uploads=file_uploads,
        initial_comment=message
    )


@pytest.mark.asyncio
async def test_message_dm_calls_callback_with_images():
    slack_bot, result, user_client, bot_client, bot_cleanup = await _setup_slack_test()

    try:
        bot_info = await bot_client.auth_test()
        dm = await user_client.conversations_open(users=bot_info["user_id"])
        dm_message = f"dm_test_{time.time()}"

        test_dir = result["test_dir"]
        await _upload_files(user_client, dm["channel"]["id"], [f'{test_dir}/1.png', f'{test_dir}/2.png'], dm_message)

        await asyncio.wait_for(result["event"].wait(), timeout=30)

        assert result["activity"].message_text == dm_message
        assert len(result["activity"].file_contents) == 2, "Should have 2 image files"

        print(f"✓ DM image test passed with {len(result['activity'].file_contents)} files")
    finally:
        await bot_cleanup()


@pytest.mark.asyncio
async def test_message_in_channel_calls_callback_with_text_files():
    slack_bot, result, user_client, bot_client, bot_cleanup = await _setup_slack_test()

    try:
        tests_channel_id = slack_bot.channels_name2id.get("tests")
        channel_message = f"channel_test_{time.time()}"

        test_dir = result["test_dir"]
        await _upload_files(user_client, tests_channel_id, [f'{test_dir}/1.txt', f'{test_dir}/2.json'], channel_message)

        await asyncio.wait_for(result["event"].wait(), timeout=30)

        assert result["activity"].message_text == channel_message
        file_contents = result["activity"].file_contents[0]['m_content']
        assert "1.txt" in file_contents and "This is test file 1" in file_contents, "Should contain 1.txt"
        assert "2.json" in file_contents and "\"content\": \"json test file\"" in file_contents, "Should contain 2.json"

        print(f"✓ Channel text file test passed")

    finally:
        await bot_cleanup()


@pytest.mark.asyncio
async def test_post_operation_with_files():
    _ = _create_test_files()
    slack_bot, _, _, _, bot_cleanup = await _setup_slack_test()

    try:
        text_args = {
            "op": "post",
            "args": {
                "channel_slash_thread": "@flexus.testing",
                "text": "Test post with files"
            }
        }
        tcall1 = ckit_cloudtool.FCloudtoolCall(
            caller_fuser_id="test_user", located_fgroup_id="test_group",
            fcall_id="test_call_id_1", fcall_ft_id="test_thread_id",
            fcall_ftm_alt=100, fcall_called_ftm_num=1, fcall_call_n=0,
            fcall_name="slack", fcall_arguments=json.dumps(text_args),
            fcall_created_ts=time.time(), connected_persona_id="persona_id",
            ws_id="test_ws", subgroups_list=[]
        )
        result1 = await slack_bot.called_by_model(toolcall=tcall1, model_produced_args=text_args)
        print("text result:", result1)
        assert "success" in result1.lower(), f"Text post should succeed: {result1}"

        file_args = {
            "op": "post",
            "args": {
                "channel_slash_thread": "@flexus.testing",
                "localfile_path": "1.txt"
            }
        }
        tcall2 = ckit_cloudtool.FCloudtoolCall(
            caller_fuser_id="test_user", located_fgroup_id="test_group",
            fcall_id="test_call_id_2", fcall_ft_id="test_thread_id",
            fcall_ftm_alt=100, fcall_called_ftm_num=2, fcall_call_n=1,
            fcall_name="slack", fcall_arguments=json.dumps(file_args),
            fcall_created_ts=time.time(), connected_persona_id="persona_id",
            ws_id="test_ws", subgroups_list=[]
        )
        result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
        print("file result:", result2)
        assert "success" in result2.lower(), f"File post should succeed: {result2}"

        print("✓ Post operation test passed (text + file)")
    finally:
        await asyncio.sleep(1)
        await bot_cleanup()


if __name__ == "__main__":
    asyncio.run(test_message_dm_calls_callback_with_images())
    asyncio.run(test_message_in_channel_calls_callback_with_text_files())
    asyncio.run(test_post_operation_with_files())
