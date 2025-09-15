import asyncio
import contextlib
import json
import uuid

import gql

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_exec, ckit_bot_install, ckit_client
from flexus_client_kit.integrations.fi_slack_fake import (
    FAKE_SLACK_INSTANCES,
    IntegrationSlackFake,
    post_fake_slack_message,
    wait_for_bot_message,
)


karen_bot.fi_slack.IntegrationSlack = IntegrationSlackFake


async def setup_test(client: ckit_client.FlexusClient) -> tuple[str, str, str]:
    ws = (await ckit_client.query_basic_stuff(client)).workspaces
    parent_id = next((w.ws_root_group_id for w in ws if w.have_admin), ws[0].ws_root_group_id)
    http = await client.use_http()

    async with http as h:
        create_resp = await h.execute(
            gql.gql("""mutation CreateGroup($input: FlexusGroupInput!) {
                group_create(input: $input) {
                    fgroup_id
                    ws_id
                }
            }"""),
            variable_values={
                "input": {
                    "fgroup_name": f"scenario-captured-thread-{str(uuid.uuid4())[:6]}",
                    "fgroup_parent_id": parent_id
                }
            },
        )
    test_group_id = create_resp["group_create"]["fgroup_id"]
    ws_id = create_resp["group_create"]["ws_id"]

    async with http as h:
        mcp_resp = await h.execute(
            gql.gql("""mutation CreateMCP($input: FMcpServerInput!) {
                mcp_server_create(input: $input) {
                    mcp_id
                }
            }"""),
            variable_values={
                "input": {
                    "located_fgroup_id": test_group_id,
                    "mcp_name": "AWS Documentation",
                    "mcp_command": "uvx awslabs.aws-documentation-mcp-server@latest",
                    "mcp_description": "https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/",
                    "mcp_enabled": True,
                    "mcp_preinstall_script": "",
                    "owner_shared": True,
                    "mcp_env_vars": json.dumps({
                        "FASTMCP_LOG_LEVEL": "ERROR",
                        "AWS_DOCUMENTATION_PARTITION": "aws"
                    })
                }
            }
        )
    mcp_id = mcp_resp["mcp_server_create"]["mcp_id"]
    install_result = await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup=test_group_id,
        persona_marketable_name="karen",
        persona_name="Karen AWS Docs Test",
        new_setup={
            "SLACK_BOT_TOKEN": "fake_bot_token",
            "SLACK_APP_TOKEN": "fake_app_token",
            "slack_should_join": "support"
        },
        install_dev_version=True,
    )

    return test_group_id


async def _cleanup(client: ckit_client.FlexusClient, group_id: str) -> None:
    http = await client.use_http()
    async with http as h:
        await h.execute(
            gql.gql(
                """mutation GroupDelete($group_id: String!) {
                    group_delete(fgroup_id: $group_id)
                }"""
            ),
            variable_values={"group_id": group_id},
        )


async def run_scenario() -> None:
    regular_client = ckit_client.FlexusClient("scenario")

    test_group_id = await setup_test(regular_client)
    print(f"Created test group {test_group_id}")

    bot_task = None
    try:
        bot_client = ckit_client.FlexusClient(
            ckit_client.bot_service_name(karen_bot.KAREN_NAME, karen_bot.BOT_VERSION_INT, test_group_id),
            endpoint="/v1/jailed-bot"
        )

        bot_task = asyncio.create_task(ckit_bot_exec.run_bots_in_this_group(
            bot_client,
            fgroup_id=test_group_id,
            marketable_name=karen_bot.BOT_NAME,
            marketable_version=karen_bot.BOT_VERSION_INT,
            inprocess_tools=karen_bot.TOOLS,
            bot_main_loop=karen_bot.karen_main_loop,
        ))   # take rcx

        # XXX wait for MCP
        while not FAKE_SLACK_INSTANCES:
            await asyncio.sleep(0.1)

        first_msg = await post_fake_slack_message("support", "Which service of AWS offers me inference of big models like anthropic models?")
        await wait_for_bot_message("support")
        assert "ts" in first_msg
        thread_ts = first_msg["ts"]

        await post_fake_slack_message(f"support/{thread_ts}", "Is there rust SDK for it?")
        await wait_for_bot_message(f"support/{thread_ts}")
        await post_fake_slack_message(f"support/{thread_ts}", "Give me example of how to invoke model in python to ask it a simple prompt and get result")
        await wait_for_bot_message(f"support/{thread_ts}")

        print("Test completed successfully. Waiting 5 minutes before cleanup...")
        await asyncio.sleep(300)

    except TimeoutError:
        print("Timed out, no answer :/")

    except KeyboardInterrupt:
        print("Test interrupted by user. Starting cleanup...")

    finally:
        if bot_task:
            bot_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await bot_task
        try:
            await _cleanup(regular_client, test_group_id)
            print("Cleanup completed successfully.")
        except Exception as e:
            print(f"Cleanup failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_scenario())

