# DEPRECATED: Old style scenario, can not run. Kept for reference to generate a happy trajectory for the new style.

import asyncio
import json
import os
import time

import discord
import gql

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_scenario, ckit_bot_query
from flexus_client_kit.integrations.fi_discord2 import ActivityDiscord, IntegrationDiscord
from flexus_simple_bots.karen import karen_bot


async def setup_discord(setup: ckit_scenario.ScenarioSetup) -> tuple[IntegrationDiscord, asyncio.Queue, discord.Client, discord.Client]:
    karen_setup = {
        "DISCORD_BOT_TOKEN": os.environ["DISCORD_TESTER1_BOT_TOKEN"],
        "discord_watch_channels": "tests",
    }
    await setup.create_group_hire_and_start_bot(
        karen_bot.BOT_NAME, None, karen_setup, [], group_prefix="discord-test"
    )
    rcx = ckit_bot_exec.RobotContext(setup.bot_fclient, setup.persona, [])
    await setup.create_fake_files_and_upload_to_mongo(rcx.workdir)

    discord_bot = IntegrationDiscord(
        setup.fclient, rcx,
        watch_channels=rcx.persona.persona_setup["discord_watch_channels"],
        mongo_collection=setup.mongo_collection,
    )

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True
    user_client = discord.Client(intents=intents)

    queue: asyncio.Queue[tuple[ActivityDiscord, bool]] = asyncio.Queue()

    async def activity_callback(activity: ActivityDiscord, already_posted_to_captured_thread: bool):
        await queue.put((activity, already_posted_to_captured_thread))

    discord_bot.set_activity_callback(activity_callback)
    await discord_bot.start_reactive()
    await discord_bot.join_channels()

    # Wait for bot to be ready and populate channel cache
    ready = await discord_bot._ensure_ready()
    print(f"Discord bot ready: {ready}")
    print(f"Discord bot channel mappings: {discord_bot.channel_name2id}")

    user_ready_event = asyncio.Event()

    @user_client.event
    async def on_ready():
        print(f"User client logged in as {user_client.user}")
        user_ready_event.set()

    user_client_task = asyncio.create_task(user_client.start(os.environ["DISCORD_TESTER2_BOT_TOKEN"]))
    await asyncio.wait_for(user_ready_event.wait(), timeout=30)

    return discord_bot, queue, user_client, user_client_task


async def _send_message_with_files(user_client: discord.Client, channel_id: int, file_paths: list[str], message: str):
    channel = user_client.get_channel(channel_id)
    if not channel:
        raise ValueError(f"Channel {channel_id} not found")

    files = []
    for file_path in file_paths:
        with open(file_path, 'rb') as f:
            filename = os.path.basename(file_path)
            files.append(discord.File(f, filename))

    await channel.send(content=message, files=files)


async def discord_channel_test(setup: ckit_scenario.ScenarioSetup, discord_bot, queue, user_client) -> None:
    print("Starting discord channel test...")
    while not queue.empty():
        queue.get_nowait()

    msg = f"channel_test_{time.time()}"
    tests_channel_id = discord_bot.channel_name2id.get("tests")
    print(f"tests channel id: {tests_channel_id}")
    assert tests_channel_id, "tests channel not found"

    print(f"Sending message: {msg}")
    await _send_message_with_files(user_client, tests_channel_id, [f"{discord_bot.rcx.workdir}/1.txt", f"{discord_bot.rcx.workdir}/2.json"], msg)
    print("Message sent, waiting for activity...")
    activity, posted = await asyncio.wait_for(queue.get(), timeout=30)
    print(f"Received activity: {activity.message_text}, posted: {posted}")
    assert activity.message_text == msg and not posted
    assert len(activity.attachments) >= 2, f"Expected 2 attachments but got {len(activity.attachments)}"

    # Check that we have both files in the attachments
    all_content = "\n".join(att["m_content"] for att in activity.attachments)
    print(f"All attachment content: {all_content}")
    assert "1.txt" in all_content and "This is test file 1" in all_content
    assert "2.json" in all_content and '"content": "json test file"' in all_content
    print("✓ Channel test passed")


async def discord_post_test(setup: ckit_scenario.ScenarioSetup, discord_bot, queue, user_client) -> None:
    while not queue.empty():
        queue.get_nowait()

    text_args = {"op": "post", "args": {"target": "tests", "text": "Test post with files"}}
    tcall1 = setup.create_fake_toolcall_output("test_call_1", "test_thread", text_args)
    result1 = await discord_bot.called_by_model(toolcall=tcall1, model_produced_args=text_args)
    assert "success" in result1.lower()

    file_args = {"op": "post", "args": {"target": "tests", "path": "1.txt"}}
    tcall2 = setup.create_fake_toolcall_output("test_call_2", "test_thread", file_args)
    result2 = await discord_bot.called_by_model(toolcall=tcall2, model_produced_args=file_args)
    assert "success" in result2.lower()
    print("✓ Post test passed")


async def discord_capture_test(setup: ckit_scenario.ScenarioSetup, discord_bot, queue, user_client) -> None:
    while not queue.empty():
        queue.get_nowait()

    tests_channel_id = discord_bot.channel_name2id.get("tests")
    assert tests_channel_id, "tests channel not found"
    channel = user_client.get_channel(tests_channel_id)

    msg = "please capture this thread"
    sent_message = await channel.send(msg)

    a1, p1 = await asyncio.wait_for(queue.get(), timeout=30)
    assert a1.message_text == msg and not p1

    thread = await channel.create_thread(name="test_thread", message=sent_message)

    # Discord automatically sends the original message to the thread, consume that first
    a_thread_creation, p_thread_creation = await asyncio.wait_for(queue.get(), timeout=30)
    print(f"Thread creation activity: text='{a_thread_creation.message_text}', posted={p_thread_creation}")

    thread_msg = await thread.send("test message 1")
    print(f"Sent thread message: id={thread_msg.id}, content='{thread_msg.content}'")
    a_pre, p_pre = await asyncio.wait_for(queue.get(), timeout=30)
    print(f"Thread message activity: text='{a_pre.message_text}', posted={p_pre}, channel_id={a_pre.channel_id}, thread_id={a_pre.thread_id}")
    assert a_pre.message_text == "test message 1" and not p_pre

    http = await discord_bot.fclient.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation BotActivateTest($who_is_asking:String!, $persona_id:String!, $first_question:String!, $first_calls:String!, $title:String!, $fexp_name:String!){ bot_activate(who_is_asking:$who_is_asking, persona_id:$persona_id, first_question:$first_question, first_calls:$first_calls, title:$title, fexp_name:$fexp_name){ ft_id }}"""),
            variable_values={
                "who_is_asking": "fi_discord_test",
                "persona_id": discord_bot.rcx.persona.persona_id,
                "first_question": msg,
                "first_calls": "[]",
                "title": "capture test",
                "fexp_name": "default",
            }
        )
    ft_id = r["bot_activate"]["ft_id"]

    args = {"op": "capture", "args": {"target": f"tests/{thread.id}"}}
    tcall = setup.create_fake_toolcall_output("capture_call", ft_id, args)
    result = await discord_bot.called_by_model(toolcall=tcall, model_produced_args=args)
    assert "captured" in result.lower()

    discord_bot.rcx.latest_threads[ft_id] = ckit_bot_query.FThreadWithMessages(
        discord_bot.rcx.persona.persona_id,
        setup.create_fake_fthread_output(ft_id, f"discord/{tests_channel_id}/{thread.id}"), {}
    )

    await thread.send("test message 2")
    a_after, p_after = await asyncio.wait_for(queue.get(), timeout=30)
    assert p_after and a_after.message_text == "test message 2"

    # Test capturing the same thread again should return "already captured"
    tcall2 = setup.create_fake_toolcall_output("capture_call_2", ft_id, args)
    result2 = await discord_bot.called_by_model(toolcall=tcall2, model_produced_args=args)
    print(f"Second capture attempt result: '{result2}'")
    assert "already captured" in result2.lower()

    content = "Test assistant response"
    assistant_msg = ckit_ask_model.FThreadMessageOutput(
        ftm_belongs_to_ft_id=ft_id, ftm_role="assistant", ftm_content=content, ftm_num=3, ftm_alt=100,
        ftm_usage=None, ftm_tool_calls=[], ftm_app_specific=None, ftm_created_ts=time.time(), ftm_provenance=json.dumps({})
    )

    discord_bot.rcx.latest_threads[ft_id].thread_fields.ft_app_specific = {"last_posted_assistant_ts": time.time() - 60}
    result = await discord_bot.look_assistant_might_have_posted_something(assistant_msg)
    assert result is True

    await asyncio.sleep(2)
    found = False
    async for message in thread.history(limit=10):
        if message.content == content:
            found = True
            break
    assert found

    uncapture_args = {"op": "uncapture"}
    tcall3 = setup.create_fake_toolcall_output("uncapture_call", ft_id, uncapture_args)
    result3 = await discord_bot.called_by_model(toolcall=tcall3, model_produced_args=uncapture_args)
    assert "error" not in result3.lower()

    if ft_id in discord_bot.rcx.latest_threads:
        del discord_bot.rcx.latest_threads[ft_id]

    await thread.send("test message 3")
    await asyncio.sleep(2)

    async with http as h:
        resp = await h.execute(
            gql.gql("""query GetThreadMessages($ft_id: String!) { thread_messages_list(ft_id: $ft_id) { ftm_content } }"""),
            variable_values={"ft_id": ft_id},
        )
    messages = resp["thread_messages_list"]
    print(f"Thread contains {len(messages)} messages")

    assert any("test message 1" in json.dumps(m) for m in messages)
    assert any("test message 2" in json.dumps(m) for m in messages)
    assert not any("test message 3" in json.dumps(m) for m in messages)
    print("✓ Capture test passed")


async def discord_test(setup: ckit_scenario.ScenarioSetup) -> None:
    discord_bot, queue, user_client, user_client_task = await setup_discord(setup)
    try:
        await discord_channel_test(setup, discord_bot, queue, user_client)
        await discord_post_test(setup, discord_bot, queue, user_client)
        await discord_capture_test(setup, discord_bot, queue, user_client)
        print("✓ All discord tests passed!")
    finally:
        await discord_bot.close()
        await user_client.close()
        user_client_task.cancel()
        try:
            await user_client_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    setup = ckit_scenario.ScenarioSetup("fi_discord_test")
    asyncio.run(setup.run_scenario(discord_test, cleanup_wait_secs=0))