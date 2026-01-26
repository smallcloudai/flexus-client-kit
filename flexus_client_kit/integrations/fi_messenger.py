import time
from collections import deque
from typing import List, Dict, Any, Optional

import gql

from flexus_client_kit import ckit_bot_exec, ckit_bot_query, ckit_client

AUTHOR_EMOJI = "👤"
FILE_EMOJI = "📎"
MAX_DEDUP_MESSAGES = 200

MESSENGER_PROMPT = """
## Messaging Platforms (Telegram, Slack, WhatsApp, etc.)

Incoming messages from these platforms appear as kanban tasks when not captured.

To respond: capture the chat using the messenger tool with op="capture".
Once captured, their messages appear here and your responses are sent back automatically.

Capture when: PMs, messages directed at you, or anything needing your response.
IMPORTANT: If you need to respond to a user from a messaging platform, you MUST capture the chat first, otherwise they won't receive your response.

### Closing a messenger conversation (MANDATORY)

When ending a conversation from a messenger platform, you MUST follow this sequence:
1. Say goodbye to the user
2. Call op="uncapture" with contact_id and conversation_summary if you identified the CRM contact
3. Then resolve the kanban task

NEVER resolve/close a kanban task without calling uncapture first.
""".strip()

CAPTURE_SUCCESS_MSG = "Captured! The next thing you write will be visible. Don't comment on that fact and think about what do you want to say in %r.\n"
CAPTURE_ADVICE_MSG = "Don't use op=post because now anything you say is visible automatically.\n"
UNCAPTURE_SUCCESS_MSG = "Uncaptured successfully. This thread is no longer connected.\n"
SKIP_SUCCESS_MSG = "Great, other people are talking, thread is still captured, any new messages will appear in this thread.\n"
OTHER_CHAT_ALREADY_CAPTURING_MSG = "Some other chat is already capturing %s\n"
NOT_CAPTURING_MSG = "This thread is not capturing any conversation. Use 'capture' first.\n"
UNKNOWN_OPERATION_MSG = "Unknown operation %r, try \"help\"\n\n"


class MessageDeduplicator:
    def __init__(self, maxlen: int = MAX_DEDUP_MESSAGES):
        self._seen: deque[str] = deque(maxlen=maxlen)

    def is_duplicate(self, msg_id: str) -> bool:
        if msg_id in self._seen:
            return True
        self._seen.append(msg_id)
        return False


def is_text_file(data: bytes) -> bool:
    if not data:
        return True
    if b'\x00' in data[:1024]:
        return False
    sample_size = min(1024, len(data))
    try:
        sample = data[:sample_size].decode('utf-8')
    except UnicodeDecodeError:
        return False
    printable = sum(1 for c in sample if c.isprintable() or c.isspace())
    return (printable / len(sample)) > 0.8 if sample else True


def format_user_message(author: str, text: str) -> str:
    return f"{AUTHOR_EMOJI}{author}\n\n{text}"


def compact_message_parts(parts: List[Dict[str, Any]], max_parts: int = 5, max_images: int = 2) -> List[Dict[str, Any]]:
    if len(parts) <= max_parts:
        return parts
    text_parts = [p for p in parts if p.get("m_type") == "text"]
    image_parts = [p for p in parts if p.get("m_type", "").startswith("image/")][:max_images]
    combined_text = "\n\n".join(p["m_content"] for p in text_parts)
    return [{"m_type": "text", "m_content": combined_text}] + image_parts


def find_thread_capturing(rcx: ckit_bot_exec.RobotContext, platform: str, identifier: str) -> Optional[ckit_bot_query.FThreadWithMessages]:
    searchable = build_searchable(platform, identifier)
    for t in rcx.latest_threads.values():
        if t.thread_fields.ft_app_searchable == searchable:
            return t
    return None


def build_searchable(platform: str, identifier: str) -> str:
    return f"{platform}/{identifier}"


def get_last_posted_ts(fthread: ckit_bot_query.FThreadWithMessages) -> float:
    if fthread.thread_fields.ft_app_specific:
        return fthread.thread_fields.ft_app_specific.get("last_posted_assistant_ts", 0)
    return 0


async def create_messenger_activity(
    fclient: ckit_client.FlexusClient,
    ws_id: str,
    platform: str,
    contact_id: str,
    ft_id: str,
    summary: str,
    direction: str = "INBOUND",
) -> bool:
    async with (await fclient.use_http()) as http:
        await http.execute(gql.gql("""mutation CreateMessengerActivity($input: ErpRecordInput!) {
            erp_record_create(input: $input) { pkey_value }
        }"""), variable_values={"input": {
            "table_name": "crm_activity",
            "ws_id": ws_id,
            "record": {
                "ws_id": ws_id,
                "activity_title": f"{platform} conversation",
                "activity_type": "MESSENGER_CHAT",
                "activity_platform": platform,
                "activity_direction": direction,
                "activity_contact_id": contact_id,
                "activity_ft_id": ft_id,
                "activity_summary": summary,
                "activity_occurred_ts": time.time(),
            },
        }})
    return True

