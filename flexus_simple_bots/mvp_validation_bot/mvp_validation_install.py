import asyncio
from pathlib import Path
from flexus_client_kit.core import ckit_client
from flexus_client_kit.runtime import no_special_code_bot
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

def main() -> None:
    bot_dir = Path(__file__).resolve().parent
    manifest = no_special_code_bot.load_manifest(bot_dir)
    tools = no_special_code_bot.tool_registry_lookup(manifest["tools"])
    client = ckit_client.FlexusClient("mvp_validation_bot_install")
    asyncio.run(no_special_code_bot.install_from_manifest(
        manifest,
        client,
        bot_name=manifest["bot_name"],
        bot_version=SIMPLE_BOTS_COMMON_VERSION,
        tools=tools,
    ))

if __name__ == "__main__":
    main()
