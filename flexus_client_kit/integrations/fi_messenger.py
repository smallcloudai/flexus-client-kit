import json
import re
import logging

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("messenger")


class IntegrationMessenger:
    def __init__(
            self,
            fclient: ckit_client.FlexusClient,
            rcx: ckit_bot_exec.RobotContext,
    ):
        self.fclient = fclient
        self.rcx = rcx

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant":
            return False
        if not msg.ftm_content:
            return False

        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id, None)
        if not fthread:
            return False

        searchable = fthread.thread_fields.ft_app_searchable
        if not searchable:
            return False

        platform, chat_id, thread_id = self._parse_searchable(searchable)
        if not platform or not chat_id:
            return False

        my_specific = fthread.thread_fields.ft_app_specific
        if my_specific is not None:
            last_posted_assistant_ts = my_specific.get("last_posted_assistant_ts", 0)
            if msg.ftm_created_ts <= last_posted_assistant_ts:
                return False

        try:
            http = await self.fclient.use_http()
            await http.execute_async(gql.gql("""
                mutation MessengerAutoForward($persona_id: String!, $platform: String!, $chat_id: String!, $text: String!, $thread_id: String!) {
                    messenger_send_message(persona_id: $persona_id, platform: $platform, chat_id: $chat_id, text: $text, thread_id: $thread_id)
                }"""),
                variable_values={
                    "persona_id": self.rcx.persona.persona_id,
                    "platform": platform,
                    "chat_id": chat_id,
                    "text": msg.ftm_content,
                    "thread_id": thread_id,
                },
            )
        except Exception as e:
            logger.error("Failed to forward message to %s %s: %s", platform, chat_id, e, exc_info=e)
            return False

        await ckit_ask_model.thread_app_capture_patch(
            http,
            fthread.thread_fields.ft_id,
            ft_app_specific=json.dumps({"last_posted_assistant_ts": msg.ftm_created_ts})
        )
        fthread.thread_fields.ft_app_specific = {"last_posted_assistant_ts": msg.ftm_created_ts}
        return True

    def _parse_searchable(self, searchable: str) -> tuple[str | None, str | None, str]:
        telegram_match = re.match(r'^telegram/([^/]+)(?:/(.+))?$', searchable)
        if telegram_match:
            chat_id, thread_id = telegram_match.groups()
            return "telegram", chat_id, thread_id or ""

        whatsapp_match = re.match(r'^whatsapp/(\+?[\d]+)', searchable)
        if whatsapp_match:
            return "whatsapp", whatsapp_match.group(1), ""

        return None, None, ""
