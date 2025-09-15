import asyncio
import json
import os
import time
import pytest
import gql
from PIL import Image
from slack_sdk.web.async_client import AsyncWebClient
from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_cloudtool, ckit_ask_model
from flexus_client_kit.integrations.fi_slack import ActivitySlack, IntegrationSlack


TEST_GROUP_ID = "NqeZnN9aLE"
TEST_PERSONA_ID = "G1JzW4WA7W"
TEST_DIR = f"/tmp/bot_workspace/{TEST_PERSONA_ID}"


def _create_toolcall(slack_bot: IntegrationSlack, ws_id: str, call_id: str, ft_id: str, args: dict, called_ftm_num: int = 1):
    return ckit_cloudtool.FCloudtoolCall(
        caller_fuser_id=slack_bot.rcx.persona.owner_fuser_id, located_fgroup_id=TEST_GROUP_ID,
        fcall_id=call_id, fcall_ft_id=ft_id, fcall_ftm_alt=100, fcall_called_ftm_num=called_ftm_num,
        fcall_call_n=0, fcall_name="slack", fcall_arguments=json.dumps(args), fcall_created_ts=time.time(),
        connected_persona_id=TEST_PERSONA_ID, ws_id=ws_id, subgroups_list=[],
    )


def _create_test_files():
    os.makedirs(TEST_DIR, exist_ok=True)
    Image.new('RGB', (100, 100), color='red').save(f'{TEST_DIR}/1.png')
    Image.new('RGB', (100, 100), color='blue').save(f'{TEST_DIR}/2.png')
    open(f'{TEST_DIR}/1.txt', 'w').write('This is test file 1\nWith multiple lines\nFor testing file attachments')
    open(f'{TEST_DIR}/2.json', 'w').write('{"test": "data", "file": "2", "content": "json test file"}')


async def _create_slack_bot(is_fake: bool = False):
    required = ["FLEXUS_API_KEY"]
    if not is_fake:
        required += ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN"]
    if not all(os.getenv(env) for env in required):
        pytest.skip(f"Missing: {', '.join(required)}")

    fclient = ckit_client.FlexusClient(service_name="fi_slack_test")
    bs = await ckit_client.query_basic_stuff(fclient)

    http = await fclient.use_http()
    async with http as h:
        group_resp = await h.execute(
            gql.gql("""query GetGroup($id: String!) { group_get(fgroup_id: $id) { ws_id } }"""),
            variable_values={"id": TEST_GROUP_ID},
        )
    ws_id = group_resp["group_get"]["ws_id"]

    persona = ckit_bot_exec.FPersonaOutput(
        owner_fuser_id=bs.fuser_id,
        located_fgroup_id=TEST_GROUP_ID,
        persona_id=TEST_PERSONA_ID,
        persona_name="test",
        persona_marketable_name="test",
        persona_marketable_version=1,
        persona_discounts=None,
        persona_setup={},
        persona_created_ts=0.0,
        ws_id=ws_id,
        ws_timezone="UTC",
    )
    rcx = ckit_bot_exec.RobotContext(fclient, persona)
    rcx.workdir = TEST_DIR

    if not is_fake:
        slack_bot = IntegrationSlack(
            fclient,
            rcx,
            os.getenv("SLACK_BOT_TOKEN"),
            os.getenv("SLACK_APP_TOKEN"),
            should_join="tests",
        )
    else:
        from flexus_client_kit.integrations.fi_slack_fake import IntegrationSlackFake
        slack_bot = IntegrationSlackFake(fclient, rcx, should_join="tests")

    return slack_bot, ws_id


async def _setup_slack_test(is_fake: bool = False):
    _create_test_files()
    slack_bot, ws_id = await _create_slack_bot(is_fake=is_fake)
    activity_queue: asyncio.Queue[tuple[ActivitySlack, bool]] = asyncio.Queue()

    async def callback(activity: ActivitySlack, already_posted_to_captured_thread: bool):
        await activity_queue.put((activity, already_posted_to_captured_thread))

    slack_bot.set_activity_callback(callback)
    await slack_bot.join_channels()
    await slack_bot.start_reactive()

    user_client = AsyncWebClient(token=os.environ["SLACK_USER_TOKEN"]) if not is_fake else None

    async def bot_cleanup():
        if not is_fake:
            for channel_name in slack_bot.actually_joined:
                channel_id = slack_bot.channels_name2id.get(channel_name)
                if channel_id:
                    try:
                        await slack_bot.reactive_slack.client.conversations_leave(channel=channel_id)
                        print(f"✓ Bot left #{channel_name}")
                    except Exception as e:
                        print(f"⚠️  Failed to leave #{channel_name}: {e}")
        await slack_bot.close()

    return slack_bot, ws_id, activity_queue, user_client, bot_cleanup


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
    slack_bot, _ws_id, activity_queue, user_client, bot_cleanup = await _setup_slack_test(is_fake=False)

    try:
        bot_info = await slack_bot.reactive_slack.client.auth_test()
        dm = await user_client.conversations_open(users=bot_info["user_id"])
        dm_message = f"dm_test_{time.time()}"

        await _upload_files(user_client, dm["channel"]["id"], [f'{TEST_DIR}/1.png', f'{TEST_DIR}/2.png'], dm_message)

        activity, posted = await asyncio.wait_for(activity_queue.get(), timeout=30)
        assert activity.message_text == dm_message
        assert posted is False
        assert len(activity.file_contents) == 2, "Should have 2 image files"

        print(f"✓ DM image test passed with {len(activity.file_contents)} files")
    finally:
        await bot_cleanup()


@pytest.mark.asyncio
async def test_message_in_channel_calls_callback_with_text_files():
    slack_bot, _ws_id, activity_queue, user_client, bot_cleanup = await _setup_slack_test(is_fake=False)

    try:
        tests_channel_id = slack_bot.channels_name2id.get("tests")
        channel_message = f"channel_test_{time.time()}"

        await _upload_files(user_client, tests_channel_id, [f'{TEST_DIR}/1.txt', f'{TEST_DIR}/2.json'], channel_message)

        activity, posted = await asyncio.wait_for(activity_queue.get(), timeout=30)
        assert activity.message_text == channel_message
        assert posted is False
        file_contents = activity.file_contents[0]['m_content']
        assert "1.txt" in file_contents and "This is test file 1" in file_contents, "Should contain 1.txt"
        assert "2.json" in file_contents and "\"content\": \"json test file\"" in file_contents, "Should contain 2.json"

        print(f"✓ Channel text file test passed")

    finally:
        await bot_cleanup()


@pytest.mark.asyncio
async def test_post_operation_with_files():
    slack_bot, ws_id, _, _, bot_cleanup = await _setup_slack_test(is_fake=False)

    try:
        text_args = {
            "op": "post",
            "args": {
                "channel_slash_thread": "@flexus.testing",
                "text": "Test post with files"
            }
        }
        tcall1 = _create_toolcall(slack_bot, ws_id, "test_call_id_1", "test_thread_id", text_args)
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
        tcall2 = _create_toolcall(slack_bot, ws_id, "test_call_id_2", "test_thread_id", file_args, called_ftm_num=2)
        result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
        print("file result:", result2)
        assert "success" in result2.lower(), f"File post should succeed: {result2}"

        print("✓ Post operation test passed (text + file)")
    finally:
        await asyncio.sleep(1)
        await bot_cleanup()


@pytest.mark.asyncio
async def test_capture_thread():
    slack_bot, ws_id, activity_queue, user_client, bot_cleanup = await _setup_slack_test(is_fake=False)

    try:
        tests_channel_id = slack_bot.channels_name2id.get("tests")
        initial_msg = "please capture this thread"
        resp = await user_client.chat_postMessage(channel=tests_channel_id, text=initial_msg)
        thread_ts = resp["ts"]

        activity1, posted1 = await asyncio.wait_for(activity_queue.get(), timeout=30)
        assert activity1.message_text == initial_msg
        assert posted1 is False

        await user_client.chat_postMessage(channel=tests_channel_id, thread_ts=thread_ts, text="test message 1")
        activity_pre, posted_pre = await asyncio.wait_for(activity_queue.get(), timeout=30)
        assert activity_pre.message_text == "test message 1"
        assert posted_pre is False

        http = await slack_bot.fclient.use_http()
        async with http as h:
            r = await h.execute(
                gql.gql("""mutation CreateThread($input:FThreadInput!){ thread_create(input:$input){ ft_id }}"""),
                variable_values={
                    "input": {
                        "owner_shared": False,
                        "located_fgroup_id": TEST_GROUP_ID,
                        "ft_fexp_id": "id:default",
                        "ft_persona_id": TEST_PERSONA_ID,
                        "ft_title": "capture test",
                        "ft_toolset": "[]",
                        "ft_app_capture": "bot",
                    }
                },
            )
        ft_id = r["thread_create"]["ft_id"]
        user_pref = json.dumps({"model": "no-model", "disable_title_generation": True, "disable_streaming": True})
        await ckit_ask_model.thread_add_user_message(http, ft_id, initial_msg, "fi_slack_test", ftm_alt=100, user_preferences=user_pref)

        args = {"op": "capture", "args": {"channel_slash_thread": f"tests/{thread_ts}"}}
        tcall = _create_toolcall(slack_bot, ws_id, "capture_call_1", ft_id, args)
        result = await slack_bot.called_by_model(toolcall=tcall, model_produced_args=args)
        assert "captured" in result.lower()

        async with http as h:
            resp_thread = await h.execute(
                gql.gql("""query GetThread($id:String!){ thread_get(id:$id){ ft_app_searchable }}"""),
                variable_values={"id": ft_id},
            )
        assert resp_thread["thread_get"]["ft_app_searchable"] == f"slack/{tests_channel_id}/{thread_ts}"

        # Updating this is a bot responsibility
        slack_bot.rcx.latest_threads[ft_id] = ckit_bot_exec.FThreadWithMessages(
            TEST_PERSONA_ID,
            ckit_ask_model.FThreadOutput(
                ft_id=ft_id,
                ft_error=None,
                ft_need_tool_calls=-1,
                ft_need_user=-1,
                ft_persona_id=TEST_PERSONA_ID,
                ft_app_searchable=f"slack/{tests_channel_id}/{thread_ts}",
                ft_app_specific=None,
                ft_updated_ts=time.time(),
            ),
            {},
        )

        await user_client.chat_postMessage(channel=tests_channel_id, thread_ts=thread_ts, text="test message 2")
        activity_after, posted_after = await asyncio.wait_for(activity_queue.get(), timeout=30)

        assert posted_after
        assert activity_after.message_text == "test message 2"

        tcall2 = _create_toolcall(slack_bot, ws_id, "capture_call_2", ft_id, args, called_ftm_num=2)
        result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=args)
        assert "already captured" in result2.lower()

        assistant_content = "Test assistant response"
        assistant_msg = ckit_ask_model.FThreadMessageOutput(
            ftm_belongs_to_ft_id=ft_id,
            ftm_role="assistant",
            ftm_content=assistant_content,
            ftm_num=3,
            ftm_alt=100,
            ftm_usage=None,
            ftm_tool_calls=[],
            ftm_app_specific=None,
            ftm_created_ts=time.time(),
        )

        slack_bot.rcx.latest_threads[ft_id].thread_fields.ft_app_specific = {
            "last_posted_assistant_ts": time.time() - 60
        }

        result = await slack_bot.look_assistant_might_have_posted_something(assistant_msg)
        assert result is True

        await asyncio.sleep(1)
        found = False
        async for msg in slack_bot.get_history(slack_bot.reactive_slack.client, "tests", thread_ts, str(int(time.time() - 60)), 10):
            if msg.get('text') == assistant_content:
                found = True
                break
        assert found

        print("✓ Assistant post test passed")

        uncapture_args = {"op": "uncapture", "args": {"channel_slash_thread": f"tests/{thread_ts}"}}
        tcall3 = _create_toolcall(slack_bot, ws_id, "uncapture_call", ft_id, uncapture_args, called_ftm_num=3)
        result3 = await slack_bot.called_by_model(toolcall=tcall3, model_produced_args=uncapture_args)
        assert "error" not in result3.lower()

        if ft_id in slack_bot.rcx.latest_threads:
            del slack_bot.rcx.latest_threads[ft_id]

        await user_client.chat_postMessage(channel=tests_channel_id, thread_ts=thread_ts, text="test message 3")
        await asyncio.sleep(2)

        async with http as h:
            resp = await h.execute(
                gql.gql("""query GetThreadMessages($ft_id: String!) {
                    thread_messages_list(ft_id: $ft_id) { ftm_content }
                }"""),
                variable_values={"ft_id": ft_id}
            )
        messages = resp["thread_messages_list"]
        print("Messages:", messages)
        assert any("test message 1" in json.dumps(m) for m in messages)
        assert any("test message 2" in json.dumps(m) for m in messages)
        assert not any("test message 3" in json.dumps(m) for m in messages)

        async with http as h:
            await h.execute(
                gql.gql("""mutation PatchThread($id: String!, $patch: FThreadPatch!) { thread_patch(id: $id, patch: $patch) { ft_id } }"""),
                variable_values={"id": ft_id, "patch": {"ft_archived_ts": time.time()}}
            )
    finally:
        await bot_cleanup()


if __name__ == "__main__":
    asyncio.run(test_message_dm_calls_callback_with_images())
    asyncio.run(test_message_in_channel_calls_callback_with_text_files())
    asyncio.run(test_post_operation_with_files())
    asyncio.run(test_capture_thread())
