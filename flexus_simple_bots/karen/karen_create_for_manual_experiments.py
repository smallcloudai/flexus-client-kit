import os
import asyncio

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client


async def run_scenario():
    client = ckit_client.FlexusClient("scenario", api_key="sk_alice_123456")
    ws_id = "solarsystem"
    inside_fgroup = "innerplanets"
    assert os.getenv("SLACK_BOT_TOKEN")
    assert os.getenv("SLACK_APP_TOKEN")
    await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup_id=inside_fgroup,
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_id="karen_manual",
        persona_name="Karen Manual",
        new_setup={
            "escalate_technical_person": "Bob",
            "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
            "SLACK_APP_TOKEN": os.getenv("SLACK_APP_TOKEN"),
            "slack_should_join": "",
        },
        install_dev_version=True,
    )


if __name__ == '__main__':
    asyncio.run(run_scenario())
