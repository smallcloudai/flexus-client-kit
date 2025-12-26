import logging

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.integrations.fi_messenger import IntegrationMessenger

logger = logging.getLogger("telegram")


class IntegrationTelegram(IntegrationMessenger):
    def __init__(
            self,
            fclient: ckit_client.FlexusClient,
            rcx: ckit_bot_exec.RobotContext,
    ):
        super().__init__(fclient, rcx)
        logger.info("Telegram integration initialized")
