import asyncio
import json
import time

import gql

from flexus_client_kit import ckit_ask_model, ckit_bot_exec
from flexus_client_kit.integrations.fi_slack import ActivitySlack
from flexus_client_kit.integrations.fi_slack_fake import IntegrationSlackFake, post_fake_slack_message
from flexus_client_kit.integrations.fi_slack_test import (
    _clear_queue,
    _create_toolcall,
    _start_slack_test,
)


async def test_fake_message_dm_calls_callback_with_images(
    slack_bot: IntegrationSlackFake,
    activity_queue: asyncio.Queue[tuple[ActivitySlack, bool]]
) -> None:
    _reset(slack_bot, activity_queue)

    await post_fake_slack_message("@tester", "dm1", localfile_path="1.png")
    await post_fake_slack_message("@tester", "dm2", localfile_path="2.png")

    act1, posted1 = await asyncio.wait_for(activity_queue.get(), timeout=3)
    act2, posted2 = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert act1.message_text == "dm1" and len(act1.file_contents) == 1
    assert act2.message_text == "dm2" and len(act2.file_contents) == 1
    assert not posted1 and not posted2
    print(f"✓ DM image test processed {len(act1.file_contents)+len(act2.file_contents)} files")


async def test_fake_message_in_channel_calls_callback_with_text_files(
    slack_bot: IntegrationSlackFake,
    activity_queue: asyncio.Queue[tuple[ActivitySlack, bool]]
) -> None:
    _reset(slack_bot, activity_queue)

    await post_fake_slack_message("tests", "channel_msg", localfile_path="1.txt")
    activity, posted = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert activity.message_text == "channel_msg"
    assert "This is test file 1" in activity.file_contents[0]["m_content"]
    assert not posted
    print("✓ Channel file test passed")


async def test_fake_post_operation_with_files(
    slack_bot: IntegrationSlackFake,
    activity_queue: asyncio.Queue[tuple[ActivitySlack, bool]]
) -> None:
    _reset(slack_bot, activity_queue)

    text_args = {"op": "post", "args": {"channel_slash_thread": "tests", "text": "hi"}}
    tcall1 = _create_toolcall(slack_bot, "call1", "ft1", text_args)
    result1 = await slack_bot.called_by_model(toolcall=tcall1, model_produced_args=text_args)
    assert "success" in result1.lower()

    file_args = {
        "op": "post",
        "args": {"channel_slash_thread": "tests", "localfile_path": "1.txt"},
    }
    tcall2 = _create_toolcall(slack_bot, "call2", "ft1", file_args, called_ftm_num=2)
    result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
    assert "success" in result2.lower()

    print("text result:", result1)
    print("file result:", result2)


async def test_fake_capture_thread(
    slack_bot: IntegrationSlackFake,
    activity_queue: asyncio.Queue[tuple[ActivitySlack, bool]]
) -> None:
    _reset(slack_bot, activity_queue)

    await post_fake_slack_message("tests", "please capture this thread")
    first_activity, posted1 = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert not posted1
    thread_ts = first_activity.thread_ts

    http = await slack_bot.fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation CreateThread($input:FThreadInput!){ thread_create(input:$input){ ft_id }}"""),
            variable_values={
                "input": {
                    "owner_shared": False,
                    "located_fgroup_id": slack_bot.rcx.persona.located_fgroup_id,
                    "ft_fexp_id": "id:default",
                    "ft_persona_id": slack_bot.rcx.persona.persona_id,
                    "ft_title": "capture test",
                    "ft_toolset": "[]",
                    "ft_app_capture": "bot",
                }
            },
        )
    ft_id = r["thread_create"]["ft_id"]

    user_pref = json.dumps({
        "model": "no-model",
        "disable_title_generation": True,
        "disable_streaming": True,
    })
    await ckit_ask_model.thread_add_user_message(
        http,
        ft_id,
        first_activity.message_text,
        "fi_slack_fake_test",
        ftm_alt=100,
        user_preferences=user_pref,
    )

    args = {"op": "capture", "args": {"channel_slash_thread": f"tests/{thread_ts}"}}
    tcall = _create_toolcall(slack_bot, "cap1", ft_id, args)
    result = await slack_bot.called_by_model(toolcall=tcall, model_produced_args=args)
    assert "captured" in result.lower()

    slack_bot.rcx.latest_threads[ft_id] = ckit_bot_exec.FThreadWithMessages(
        slack_bot.rcx.persona.persona_id,
        ckit_ask_model.FThreadOutput(
            ft_id=ft_id,
            ft_error=None,
            ft_need_tool_calls=-1,
            ft_need_user=-1,
            ft_persona_id=slack_bot.rcx.persona.persona_id,
            ft_app_searchable=f"slack/{slack_bot.channels_name2id['tests']}/{thread_ts}",
            ft_app_specific=None,
            ft_updated_ts=time.time(),
        ),
        {},
    )

    post_args = {
        "op": "post",
        "args": {"channel_slash_thread": f"tests/{thread_ts}", "text": "blocked"},
    }
    tcall_post = _create_toolcall(slack_bot, "postfail", ft_id, post_args)
    result_post = await slack_bot.called_by_model(toolcall=tcall_post, model_produced_args=post_args)
    assert "captured thread" in result_post.lower()

    await post_fake_slack_message(f"tests/{thread_ts}", "captured msg")
    act_after, posted_after = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert posted_after and act_after.message_text == "captured msg"

    assistant_msg = ckit_ask_model.FThreadMessageOutput(
        ftm_belongs_to_ft_id=ft_id,
        ftm_role="assistant",
        ftm_content="assistant reply",
        ftm_num=3,
        ftm_alt=100,
        ftm_usage=None,
        ftm_tool_calls=[],
        ftm_app_specific=None,
        ftm_provenance=json.dumps({}),
        ftm_created_ts=time.time(),
    )
    assert await slack_bot.look_assistant_might_have_posted_something(assistant_msg)

    found = False
    chan_id = slack_bot.channels_name2id.get("tests", "tests")
    for m in slack_bot.messages.get(chan_id, []):
        if m.get("text") == "assistant reply" and m.get("thread_ts") == thread_ts:
            found = True
            break
    assert found

    assistant_activity, assistant_posted = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert assistant_activity.message_text == "assistant reply" and assistant_posted

    uncapture_args = {"op": "uncapture", "args": {"channel_slash_thread": f"tests/{thread_ts}"}}
    tcall2 = _create_toolcall(slack_bot, "cap2", ft_id, uncapture_args, called_ftm_num=2)
    await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=uncapture_args)

    if ft_id in slack_bot.rcx.latest_threads:
        del slack_bot.rcx.latest_threads[ft_id]

    await post_fake_slack_message(f"tests/{thread_ts}", "not captured")
    activity_not_captured, posted_last = await asyncio.wait_for(activity_queue.get(), timeout=3)
    assert activity_not_captured.message_text == "not captured"
    assert not posted_last

    print("✓ Capture test passed")


def _reset(slack_bot, queue):
    _clear_queue(queue)
    slack_bot.messages.clear()
    slack_bot.captured = None
    slack_bot.captured_ft_id = None


if __name__ == "__main__":
    async def _main():
        slack_bot, activity_queue, _user_client, cleanup = await _start_slack_test(slack_fake=True)
        try:
            await test_fake_message_dm_calls_callback_with_images(slack_bot, activity_queue)
            await test_fake_message_in_channel_calls_callback_with_text_files(slack_bot, activity_queue)
            await test_fake_post_operation_with_files(slack_bot, activity_queue)
            await test_fake_capture_thread(slack_bot, activity_queue)
        finally:
            await cleanup()

    asyncio.run(_main())
