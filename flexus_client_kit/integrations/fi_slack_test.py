import asyncio
import json
import os
import time

import gql
from slack_sdk.web.async_client import AsyncWebClient

from flexus_client_kit import (
    ckit_ask_model,
    ckit_bot_exec,
    ckit_cloudtool,
    ckit_scenario_setup,
)
from flexus_client_kit.integrations.fi_slack import ActivitySlack, IntegrationSlack
from flexus_client_kit.integrations.fi_slack_fake import IntegrationSlackFake
from flexus_simple_bots.karen import karen_bot


async def _start_slack_test(slack_fake: bool = False) -> tuple[IntegrationSlack | IntegrationSlackFake, asyncio.Queue, AsyncWebClient, asyncio.Task]:
    setup = ckit_scenario_setup.ScenarioSetup("fi_slack_test")
    karen_setup = {
        "SLACK_BOT_TOKEN": "" if slack_fake else os.environ["SLACK_BOT_TOKEN"],
        "SLACK_APP_TOKEN": "" if slack_fake else os.environ["SLACK_APP_TOKEN"],
        "slack_should_join": "tests",
    }
    rcx, mongo = await setup.setup(
        karen_bot.BOT_NAME, karen_setup, require_dev=True, prefix="slack-test"
    )

    if slack_fake:
        slack_bot = IntegrationSlackFake(setup.fclient, rcx, "", "", should_join=rcx.persona.persona_setup["slack_should_join"], mongo_collection=mongo)
        user_client = None
    else:
        slack_bot = IntegrationSlack(
            setup.fclient, rcx,
            rcx.persona.persona_setup["SLACK_BOT_TOKEN"],
            rcx.persona.persona_setup["SLACK_APP_TOKEN"],
            should_join=rcx.persona.persona_setup["slack_should_join"],
            mongo_collection=mongo
        )
        user_client = AsyncWebClient(token=os.environ["SLACK_USER_TOKEN"])

    queue: asyncio.Queue[tuple[ActivitySlack, bool]] = asyncio.Queue()

    async def callback(activity: ActivitySlack, already_posted_to_captured_thread: bool):
        await queue.put((activity, already_posted_to_captured_thread))

    slack_bot.set_activity_callback(callback)
    await slack_bot.join_channels()
    await slack_bot.start_reactive()

    async def cleanup():
        if hasattr(slack_bot, "reactive_slack"):
            for channel_name in slack_bot.actually_joined:
                channel_id = slack_bot.channels_name2id.get(channel_name)
                if channel_id:
                    try:
                        await slack_bot.reactive_slack.client.conversations_leave(channel=channel_id)
                        print(f"✓ Bot left #{channel_name}")
                    except Exception as e:
                        print(f"⚠️  Failed to leave #{channel_name}: {e}")
        await slack_bot.close()
        await setup.cleanup()

    return slack_bot, queue, user_client, cleanup


def _create_toolcall(slack_bot: IntegrationSlack, call_id: str, ft_id: str, args: dict, called_ftm_num: int = 1):
    persona = slack_bot.rcx.persona
    return ckit_cloudtool.FCloudtoolCall(
        caller_fuser_id=persona.owner_fuser_id, located_fgroup_id=persona.located_fgroup_id,
        fcall_id=call_id, fcall_ft_id=ft_id, fcall_ftm_alt=100, fcall_called_ftm_num=called_ftm_num,
        fcall_call_n=0, fcall_name="slack", fcall_arguments=json.dumps(args), fcall_created_ts=time.time(),
        connected_persona_id=persona.persona_id, ws_id=persona.ws_id, subgroups_list=[],
    )


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


async def test_message_dm_calls_callback_with_images(
    slack_bot: IntegrationSlack,
    queue: asyncio.Queue[tuple[ActivitySlack, bool]],
    user_client: AsyncWebClient
) -> None:
    while not queue.empty():
        queue.get_nowait()

    bot_info = await slack_bot.reactive_slack.client.auth_test()
    dm = await user_client.conversations_open(users=bot_info["user_id"])
    dm_message = f"dm_test_{time.time()}"

    workdir = slack_bot.rcx.workdir
    await _upload_files(
        user_client,
        dm["channel"]["id"],
        [f"{workdir}/1.png", f"{workdir}/2.png"],
        dm_message,
    )

    activity, posted = await asyncio.wait_for(queue.get(), timeout=30)
    assert activity.message_text == dm_message and posted is False
    assert len(activity.file_contents) == 2, "Should have 2 image files"


async def test_message_in_channel_calls_callback_with_text_files(
    slack_bot: IntegrationSlack,
    queue: asyncio.Queue[tuple[ActivitySlack, bool]],
    user_client: AsyncWebClient
) -> None:
    while not queue.empty():
        queue.get_nowait()

    msg = f"channel_test_{time.time()}"
    await _upload_files(
        user_client,
        slack_bot.channels_name2id.get("tests"),
        [f"{slack_bot.rcx.workdir}/1.txt", f"{slack_bot.rcx.workdir}/2.json"],
        msg,
    )

    activity, posted = await asyncio.wait_for(queue.get(), timeout=30)
    assert activity.message_text == msg and posted is False
    content = activity.file_contents[0]["m_content"]
    assert "1.txt" in content and "This is test file 1" in content, "Should contain 1.txt"
    assert "2.json" in content and '\"content\": \"json test file\"' in content, "Should contain 2.json"


async def test_post_operation_with_files(
    slack_bot: IntegrationSlack,
    queue: asyncio.Queue[tuple[ActivitySlack, bool]]
) -> None:
    while not queue.empty():
        queue.get_nowait()

    text_args = {"op": "post", "args": {"channel_slash_thread": "@flexus.testing", "text": "Test post with files"}}
    tcall1 = _create_toolcall(slack_bot, "test_call_id_1", "test_thread_id", text_args)
    result1 = await slack_bot.called_by_model(toolcall=tcall1, model_produced_args=text_args)
    assert "success" in result1.lower(), f"Text post should succeed: {result1}"

    file_args = {"op": "post", "args": {"channel_slash_thread": "@flexus.testing", "path": "1.txt"}}
    tcall2 = _create_toolcall(slack_bot, "test_call_id_2", "test_thread_id", file_args, called_ftm_num=2)
    result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
    assert "success" in result2.lower(), f"File post should succeed: {result2}"


async def test_capture_thread(
    slack_bot: IntegrationSlack,
    queue: asyncio.Queue[tuple[ActivitySlack, bool]],
    user_client: AsyncWebClient
) -> None:
    while not queue.empty():
        queue.get_nowait()

    ch_id = slack_bot.channels_name2id.get("tests")
    msg = "please capture this thread"
    resp = await user_client.chat_postMessage(channel=ch_id, text=msg)

    a1, p1 = await asyncio.wait_for(queue.get(), timeout=30)
    assert a1.message_text == msg and p1 is False

    await user_client.chat_postMessage(channel=ch_id, thread_ts=resp["ts"], text="test message 1")
    a_pre, p_pre = await asyncio.wait_for(queue.get(), timeout=30)
    assert a_pre.message_text == "test message 1" and p_pre is False

    http = await slack_bot.fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation CreateThread($input:FThreadInput!){ thread_create(input:$input){ ft_id }}"""),
            variable_values={"input": {
                "owner_shared": False, "located_fgroup_id": slack_bot.rcx.persona.located_fgroup_id,
                "ft_fexp_id": "id:default", "ft_persona_id": slack_bot.rcx.persona.persona_id,
                "ft_title": "capture test", "ft_toolset": "[]", "ft_app_capture": "bot"
            }}
        )
    ft_id = r["thread_create"]["ft_id"]
    await ckit_ask_model.thread_add_user_message(
        http, ft_id, msg, "fi_slack_test", ftm_alt=100,
        user_preferences=json.dumps({"model": "no-model", "disable_title_generation": True, "disable_streaming": True})
    )

    args = {"op": "capture", "args": {"channel_slash_thread": f"tests/{resp['ts']}"}}
    tcall = _create_toolcall(slack_bot, "capture_call_1", ft_id, args)
    result = await slack_bot.called_by_model(toolcall=tcall, model_produced_args=args)
    assert "captured" in result.lower()

    async with http as h:
        resp_thread = await h.execute(
            gql.gql("""query GetThread($id:String!){ thread_get(id:$id){ ft_app_searchable }}"""),
            variable_values={"id": ft_id}
        )
    assert resp_thread["thread_get"]["ft_app_searchable"] == f"slack/{ch_id}/{resp['ts']}"

    slack_bot.rcx.latest_threads[ft_id] = ckit_bot_exec.FThreadWithMessages(
        slack_bot.rcx.persona.persona_id,
        ckit_ask_model.FThreadOutput(
            ft_id=ft_id, ft_error=None, ft_need_tool_calls=-1, ft_need_user=-1,
            ft_persona_id=slack_bot.rcx.persona.persona_id, ft_app_searchable=f"slack/{ch_id}/{resp['ts']}",
            ft_app_specific=None, ft_updated_ts=time.time()
        ), {}
    )

    await user_client.chat_postMessage(channel=ch_id, thread_ts=resp["ts"], text="test message 2")
    a_after, p_after = await asyncio.wait_for(queue.get(), timeout=30)
    assert p_after and a_after.message_text == "test message 2"

    tcall2 = _create_toolcall(slack_bot, "capture_call_2", ft_id, args, called_ftm_num=2)
    result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=args)
    assert "already captured" in result2.lower()

    content = "Test assistant response"
    assistant_msg = ckit_ask_model.FThreadMessageOutput(
        ftm_belongs_to_ft_id=ft_id, ftm_role="assistant", ftm_content=content, ftm_num=3, ftm_alt=100,
        ftm_usage=None, ftm_tool_calls=[], ftm_app_specific=None, ftm_created_ts=time.time(), ftm_provenance=json.dumps({})
    )

    slack_bot.rcx.latest_threads[ft_id].thread_fields.ft_app_specific = {"last_posted_assistant_ts": time.time() - 60}

    result = await slack_bot.look_assistant_might_have_posted_something(assistant_msg)
    assert result is True

    await asyncio.sleep(1)
    found = False
    async for m in slack_bot._get_history(slack_bot.reactive_slack.client, "tests", resp["ts"], str(int(time.time() - 60)), 10):
        if m.get("text") == content:
            found = True
            break
    assert found

    uncapture_args = {"op": "uncapture", "args": {"channel_slash_thread": f"tests/{resp['ts']}"}}
    tcall3 = _create_toolcall(slack_bot, "uncapture_call", ft_id, uncapture_args, called_ftm_num=3)
    result3 = await slack_bot.called_by_model(toolcall=tcall3, model_produced_args=uncapture_args)
    assert "error" not in result3.lower()

    if ft_id in slack_bot.rcx.latest_threads:
        del slack_bot.rcx.latest_threads[ft_id]

    await user_client.chat_postMessage(channel=ch_id, thread_ts=resp["ts"], text="test message 3")
    await asyncio.sleep(2)

    async with http as h:
        resp = await h.execute(
            gql.gql(
                """query GetThreadMessages($ft_id: String!) {
                    thread_messages_list(ft_id: $ft_id) { ftm_content }
                }"""
            ),
            variable_values={"ft_id": ft_id},
        )
    messages = resp["thread_messages_list"]
    assert any("test message 1" in json.dumps(m) for m in messages)
    assert any("test message 2" in json.dumps(m) for m in messages)
    assert not any("test message 3" in json.dumps(m) for m in messages)


if __name__ == "__main__":
    async def _main():
        bot, queue, user, cleanup = await _start_slack_test()
        try:
            print(f"Starting tests with user_client: {type(user)}")
            await test_message_dm_calls_callback_with_images(bot, queue, user)
            print("✓ DM test passed")
            await test_message_in_channel_calls_callback_with_text_files(bot, queue, user)
            print("✓ Channel test passed")
            await test_post_operation_with_files(bot, queue)
            print("✓ Post operation test passed")
            await test_capture_thread(bot, queue, user)
            print("✓ All tests passed!")
            print("Waiting 5mins before cleanup (Ctrl+C to cleanup immediately)")
            await asyncio.sleep(300)
        except KeyboardInterrupt:
            print("\nCleaning up immediately...")
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await cleanup()

    asyncio.run(_main())
