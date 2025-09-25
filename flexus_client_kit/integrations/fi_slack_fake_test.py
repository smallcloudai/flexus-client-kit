import asyncio
import json
import time

import gql

from flexus_client_kit import ckit_ask_model, ckit_scenario_setup, ckit_bot_query
from flexus_client_kit.integrations.fi_slack_fake import post_fake_slack_message
from flexus_client_kit.integrations.fi_slack_test import setup_slack


async def fake_dm_test(setup: ckit_scenario_setup.ScenarioSetup, slack_bot, queue, _user) -> None:
    while not queue.empty():
        queue.get_nowait()

    await post_fake_slack_message("@tester", "dm1", path="1.png")
    await post_fake_slack_message("@tester", "dm2", path="2.png")

    a1, p1 = await asyncio.wait_for(queue.get(), timeout=3)
    a2, p2 = await asyncio.wait_for(queue.get(), timeout=3)
    assert a1.message_text == "dm1" and len(a1.file_contents) == 1
    assert a2.message_text == "dm2" and len(a2.file_contents) == 1
    assert not p1 and not p2
    print("✓ Fake DM test passed")

async def fake_channel_test(setup: ckit_scenario_setup.ScenarioSetup, slack_bot, queue, _user) -> None:
    while not queue.empty():
        queue.get_nowait()

    await post_fake_slack_message("tests", "channel_msg", path="1.txt")
    activity, posted = await asyncio.wait_for(queue.get(), timeout=3)
    assert activity.message_text == "channel_msg"
    assert "This is test file 1" in activity.file_contents[0]["m_content"] and not posted
    print("✓ Fake channel test passed")

async def fake_post_test(setup: ckit_scenario_setup.ScenarioSetup, slack_bot, queue, _user) -> None:
    while not queue.empty():
        queue.get_nowait()

    text_args = {"op": "post", "args": {"channel_slash_thread": "tests", "text": "hi"}}
    tcall1 = setup.create_fake_toolcall_output("call1", "ft1", text_args)
    result1 = await slack_bot.called_by_model(toolcall=tcall1, model_produced_args=text_args)
    assert "success" in result1.lower()

    file_args = {"op": "post", "args": {"channel_slash_thread": "tests", "path": "1.txt"}}
    tcall2 = setup.create_fake_toolcall_output("call2", "ft1", file_args)
    result2 = await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
    assert "success" in result2.lower()
    print("✓ Fake post test passed")

async def fake_capture_test(setup: ckit_scenario_setup.ScenarioSetup, slack_bot, queue, _user) -> None:
    while not queue.empty():
        queue.get_nowait()

    await post_fake_slack_message("tests", "please capture this thread")
    first_activity, posted1 = await asyncio.wait_for(queue.get(), timeout=3)
    assert not posted1
    ts = first_activity.thread_ts

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
        http, ft_id, first_activity.message_text, "fi_slack_fake_test", ftm_alt=100,
        user_preferences=json.dumps({"model": "no-model", "disable_title_generation": True, "disable_streaming": True})
    )

    args = {"op": "capture", "args": {"channel_slash_thread": f"tests/{ts}"}}
    tcall = setup.create_fake_toolcall_output("cap1", ft_id, args)
    result = await slack_bot.called_by_model(toolcall=tcall, model_produced_args=args)
    assert "captured" in result.lower()

    slack_bot.rcx.latest_threads[ft_id] = ckit_bot_query.FThreadWithMessages(
        slack_bot.rcx.persona.persona_id,
        setup.create_fake_fthread_output(ft_id, f"slack/{slack_bot.channels_name2id['tests']}/{ts}"), {}
    )

    post_args = {"op": "post", "args": {"channel_slash_thread": f"tests/{ts}", "text": "blocked"}}
    tcall_post = setup.create_fake_toolcall_output("postfail", ft_id, post_args)
    result_post = await slack_bot.called_by_model(toolcall=tcall_post, model_produced_args=post_args)
    assert "captured thread" in result_post.lower()

    await post_fake_slack_message(f"tests/{ts}", "captured msg")
    act_after, posted_after = await asyncio.wait_for(queue.get(), timeout=3)
    assert posted_after and act_after.message_text == "captured msg"

    assistant_msg = ckit_ask_model.FThreadMessageOutput(
        ftm_belongs_to_ft_id=ft_id, ftm_role="assistant", ftm_content="assistant reply", ftm_num=3, ftm_alt=100,
        ftm_usage=None, ftm_tool_calls=[], ftm_app_specific=None, ftm_provenance=json.dumps({}), ftm_created_ts=time.time()
    )
    assert await slack_bot.look_assistant_might_have_posted_something(assistant_msg)

    found = False
    chan_id = slack_bot.channels_name2id.get("tests", "tests")
    for m in slack_bot.messages.get(chan_id, []):
        if m.get("text") == "assistant reply" and m.get("thread_ts") == ts:
            found = True
            break
    assert found

    assistant_activity, assistant_posted = await asyncio.wait_for(queue.get(), timeout=3)
    assert assistant_activity.message_text == "assistant reply" and assistant_posted

    uncapture_args = {"op": "uncapture", "args": {"channel_slash_thread": f"tests/{ts}"}}
    tcall2 = setup.create_fake_toolcall_output("cap2", ft_id, uncapture_args)
    await slack_bot.called_by_model(toolcall=tcall2, model_produced_args=uncapture_args)

    if ft_id in slack_bot.rcx.latest_threads:
        del slack_bot.rcx.latest_threads[ft_id]

    await post_fake_slack_message(f"tests/{ts}", "not captured")
    activity_not_captured, posted_last = await asyncio.wait_for(queue.get(), timeout=3)
    assert activity_not_captured.message_text == "not captured"
    assert not posted_last
    print("✓ Fake capture test passed")

async def fake_slack_test(setup: ckit_scenario_setup.ScenarioSetup) -> None:
    slack_bot, queue, _user = await setup_slack(setup, slack_fake=True)
    try:
        await fake_dm_test(setup, slack_bot, queue, _user)
        await fake_channel_test(setup, slack_bot, queue, _user)
        await fake_post_test(setup, slack_bot, queue, _user)
        await fake_capture_test(setup, slack_bot, queue, _user)
        print("✓ All fake slack tests passed!")
    finally:
        await slack_bot.close()

if __name__ == "__main__":
    setup = ckit_scenario_setup.ScenarioSetup("fi_slack_fake_test")
    asyncio.run(setup.run_scenario(fake_slack_test))
