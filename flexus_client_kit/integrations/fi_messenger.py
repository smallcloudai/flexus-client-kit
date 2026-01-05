import re
import logging
import time
from typing import Optional, Dict

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
            enable_summarization: bool = True,
            message_limit_threshold: int = 80,
            budget_limit_threshold: float = 0.8,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.enable_summarization = enable_summarization
        self.message_limit_threshold = message_limit_threshold
        self.budget_limit_threshold = budget_limit_threshold

    def _parse_searchable(self, searchable: str) -> tuple[str | None, str | None, str]:
        telegram_match = re.match(r'^telegram/([^/]+)(?:/(.+))?$', searchable)
        if telegram_match:
            chat_id, thread_id = telegram_match.groups()
            return "telegram", chat_id, thread_id or ""

        whatsapp_match = re.match(r'^whatsapp/(\+?[\d]+)', searchable)
        if whatsapp_match:
            return "whatsapp", whatsapp_match.group(1), ""

        return None, None, ""

    async def validate_messenger_handle(
        self,
        platform: str,
        handle: str,
    ) -> Optional[Dict]:
        http_client = await self.fclient.use_http()
        async with http_client as http:
            result = await http.execute(
                gql.gql("""query ValidateMessengerHandle($platform: String!, $handle: String!) {
                    validate_messenger_handle(platform: $platform, handle: $handle) {
                        valid
                        persona_id
                        contact_id
                        ft_id
                        platform
                    }
                }"""),
                variable_values={
                    "platform": platform,
                    "handle": handle,
                },
            )

        handle_result = result["validate_messenger_handle"]

        if not handle_result["valid"]:
            return None

        if handle_result.get("persona_id") != self.rcx.persona.persona_id:
            logger.warning(f"Handle persona mismatch: {handle_result.get('persona_id')} != {self.rcx.persona.persona_id}")
            return None

        return {
            "persona_id": handle_result["persona_id"],
            "contact_id": handle_result["contact_id"],
            "ft_id": handle_result["ft_id"],
            "platform": handle_result["platform"],
        }

    async def should_restart_thread(self, thread) -> tuple[bool, str]:
        if not self.enable_summarization:
            return False, ""

        try:
            msg_count = await self._count_thread_messages(thread.thread_fields.ft_id)

            if msg_count >= self.message_limit_threshold:
                return True, f"message_limit_{msg_count}"

            if thread.thread_fields.ft_budget > 0:
                budget_ratio = thread.thread_fields.ft_coins / thread.thread_fields.ft_budget
                if budget_ratio >= self.budget_limit_threshold:
                    return True, f"budget_limit_{budget_ratio:.2f}"

            if thread.thread_fields.ft_error:
                return True, "thread_error"

            return False, ""

        except Exception as e:
            logger.error("Error checking thread restart conditions", exc_info=e)
            return False, ""

    async def generate_thread_summary(self, thread) -> str:
        try:
            http = await self.fclient.use_http()

            messages_result = await http.execute_async(
                gql.gql("""
                    query GetThreadMessages($ft_id: String!) {
                        thread_messages(ft_id: $ft_id) {
                            ftm_role
                            ftm_content
                            ftm_created_ts
                        }
                    }
                """),
                variable_values={"ft_id": thread.thread_fields.ft_id}
            )

            messages = messages_result.get("thread_messages", [])

            user_messages = [m for m in messages if m["ftm_role"] == "user"]
            assistant_messages = [m for m in messages if m["ftm_role"] == "assistant"]

            summary = f"""CONVERSATION SUMMARY (Previous Thread)

Thread ID: {thread.thread_fields.ft_id}
Message count: {len(messages)}
Started: {time.strftime('%Y-%m-%d %H:%M', time.localtime(thread.thread_fields.ft_created_ts))}

KEY TOPICS DISCUSSED:
{self._extract_key_topics(user_messages)}

CURRENT STATUS:
{self._extract_current_status(messages)}

ACTION ITEMS:
{self._extract_action_items(assistant_messages)}

Continue the conversation naturally from this context.
"""

            return summary

        except Exception as e:
            logger.error("Error generating thread summary", exc_info=e)
            return f"Previous thread: {thread.thread_fields.ft_id}\nContinuing conversation..."

    def _extract_key_topics(self, user_msgs) -> str:
        topics = []
        for msg in user_msgs[:5]:
            content = str(msg.get("ftm_content", ""))[:200]
            if content:
                topics.append(f"- {content}")
        return "\n".join(topics) if topics else "- No specific topics recorded"

    def _extract_current_status(self, messages) -> str:
        recent = messages[-3:] if len(messages) >= 3 else messages
        status_lines = []
        for msg in recent:
            role = msg["ftm_role"]
            content = str(msg.get("ftm_content", ""))[:150]
            status_lines.append(f"{role}: {content}")
        return "\n".join(status_lines) if status_lines else "- No recent context"

    def _extract_action_items(self, assistant_msgs) -> str:
        actions = []
        action_keywords = ["will", "going to", "should", "need to", "follow up"]

        for msg in assistant_msgs[-5:]:
            content = str(msg.get("ftm_content", ""))
            for keyword in action_keywords:
                if keyword in content.lower():
                    sentences = content.split(".")
                    for sent in sentences:
                        if keyword in sent.lower():
                            actions.append(f"- {sent.strip()}")
                            break
                    break

        return "\n".join(actions[:5]) if actions else "- No pending actions"

    async def _count_thread_messages(self, ft_id: str) -> int:
        try:
            http = await self.fclient.use_http()
            result = await http.execute_async(
                gql.gql("""
                    query CountMessages($ft_id: String!) {
                        thread_message_count(ft_id: $ft_id)
                    }
                """),
                variable_values={"ft_id": ft_id}
            )
            return result.get("thread_message_count", 0)
        except Exception as e:
            logger.error("Failed to count messages for thread %s", ft_id, exc_info=e)
            return 0
