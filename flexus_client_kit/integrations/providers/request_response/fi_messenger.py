from collections import deque
from typing import List, Dict, Any, Optional

from flexus_client_kit.core import ckit_bot_exec, ckit_bot_query

AUTHOR_EMOJI = "👤"
FILE_EMOJI = "📎"
MAX_DEDUP_MESSAGES = 200

MESSENGER_PROMPT = """
## Messaging Platforms (Telegram, Slack, WhatsApp, etc.)

Incoming messages from these platforms appear as kanban tasks when not captured.

To start responding: capture the chat using the messenger tool with op="capture".
Once captured, their messages appear here and your responses are sent back automatically.
At that point you can talk normally like a regular assistant by printing text!

There is usually also op="post", that is intended for one-off messaging without capturing
the chat, follow-ups will go the long way via kanban tasks. It's good for tests or daily reports,
not for talking to people and keeping context of the conversation.

IMPORTANT: if your thread does not capture any chat, your responses will go nowhere,
only tool calls will have an effect!

When you see a timeout message from scheduler, think what you should do:

- If it's a thread specialized on a topic, then keep it captured, because if someone will ask a
  question later, the current task will automatically reopen, that's good you'll see the context
  to respond.
- If it's an infinite chat like channel/group or DMs with somebody, then uncapture it. Any
  message will create a new task, not reopen an old one.

After you have run op="uncapture" or decided to keep it captured, resolve the current kanban task and
after that say "TASK_COMPLETED" in English all caps, that's a special word that does not make it into the
captured chat in any case.
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


def recent_thread_that_captures(rcx: ckit_bot_exec.RobotContext, platform: str, identifier: str) -> Optional[ckit_bot_query.FThreadWithMessages]:
    searchable = fmt_searchable(platform, identifier)
    for t in rcx.latest_threads.values():
        if t.thread_fields.ft_app_searchable == searchable:
            return t
    return None


def fmt_searchable(platform: str, identifier: str) -> str:
    return f"{platform}/{identifier}"


def get_last_posted_ts(fthread: ckit_bot_query.FThreadWithMessages) -> float:
    if fthread.thread_fields.ft_app_specific:
        return fthread.thread_fields.ft_app_specific.get("last_posted_assistant_ts", 0)
    return 0

