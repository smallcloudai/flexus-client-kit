from collections import deque
from typing import List, Dict, Any, Optional

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_client

MESSENGER_PROMPT = """
## Messaging Platforms (Telegram, Slack, WhatsApp, Flexus Magic Desk, etc.)

Incoming messages from these platforms appear as kanban tasks when not captured.

To start responding: capture the chat using the messenger tool with op="capture".
Once captured, their messages appear here and your responses are sent back automatically.
At that point you can talk normally like a regular assistant by printing text!

There is usually also op="post", that is intended for one-off messaging without capturing
the chat, there's no good way to receive messages back, it's only good for tests or daily reports,
not for talking to people and keeping context of the conversation.

IMPORTANT: if your thread does not capture any chat, your responses will go nowhere,
only tool calls will have an effect!

When you see a timeout message from scheduler, think what you should do:

- If it's a thread specialized on a single issue, then keep it captured, because if someone will ask a
  question later, the current task will automatically reopen, that's good you'll see the context
  to respond.
- If it's an infinite chat like channel/group or DM, then uncapture it. Any message will create
  a new task, not reopen an old one.

After you have run op="uncapture" or decided to keep it captured, resolve the current kanban task and
after that say "TASK_COMPLETED" in English all caps, that's a special word that does not make it into the
captured chat in any case, and of course call no tools so the chat stops.
""".strip()

CAPTURE_SUCCESS_MSG = "Captured! The next thing you write will be visible. Don't comment on that fact and think about what do you want to say in %r.\n"
CAPTURE_ADVICE_MSG = "Don't use op=post because now anything you say is visible automatically.\n"
UNCAPTURE_SUCCESS_MSG = "Uncaptured successfully. This thread is no longer connected.\n"
SKIP_SUCCESS_MSG = "Great, other people are talking, thread is still captured, any new messages will appear in this thread.\n"
OTHER_CHAT_ALREADY_CAPTURING_MSG = "Some other chat is already capturing %s\n"
NOT_CAPTURING_MSG = "This thread is not capturing any conversation. Use 'capture' first.\n"
UNKNOWN_OPERATION_MSG = "Unknown operation %r, try \"help\"\n\n"
CAPTURE_WRONG_EXPERT_MSG = "This chat is not suitable to receive messages from outside. Create a task instead with expert %r that will handle it, or if the task already exists just wait for it to execute.\n\n"


class FlexusMessenger:
    platform_name: str = ""   # override in subclass, e.g. "telegram"
    emessage_type: str = ""   # override in subclass, e.g. "TELEGRAM"

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext):
        self.fclient = fclient
        self.rcx = rcx
        self.outside_messages_fexp_name: str = ""

    def accept_outside_messages_only_to_expert(self, fexp_name: str):
        self.outside_messages_fexp_name = fexp_name

    def recent_thread_that_captures(self, identifier: str) -> Optional[ckit_bot_query.FThreadWithMessages]:
        searchable = f"{self.platform_name}/{identifier}"
        for t in self.rcx.latest_threads.values():
            if t.thread_fields.ft_app_searchable == searchable:
                return t
        return None

    async def handle_emessage(self, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
        raise NotImplementedError

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        raise NotImplementedError

    async def look_user_message_got_confirmed(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        return False


def ftm_content_to_text(content) -> str:
    if isinstance(content, list):
        return "\n\n".join(
            x.get("m_content") or x.get("text", "")
            for x in content
            if isinstance(x, dict) and (x.get("m_type") or x.get("type")) == "text"
        )
    return content or ""


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


def compact_message_parts(parts: List[Dict[str, Any]], max_parts: int = 5, max_images: int = 2) -> List[Dict[str, Any]]:
    # XXX if it's just text, simplify into simple string not list of dicts
    if len(parts) <= max_parts:
        return parts
    text_parts = [p for p in parts if p.get("m_type") == "text"]
    image_parts = [p for p in parts if p.get("m_type", "").startswith("image/")][:max_images]
    combined_text = "\n\n".join(p["m_content"] for p in text_parts)
    return [{"m_type": "text", "m_content": combined_text}] + image_parts

