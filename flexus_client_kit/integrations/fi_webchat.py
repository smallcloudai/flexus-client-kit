import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

import gql

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool, ckit_kanban
from flexus_client_kit.integrations import fi_messenger

logger = logging.getLogger("wchat")

WEBCHAT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="webchat",
    description="Interact with the web chat widget. Call with op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
    },
)

HELP = """Help:

webchat(op="capture", args={"session_id": "uuid"})
    Capture a web chat session. Messages will appear here and your responses will be sent back.

webchat(op="uncapture")
    Stop capturing this session.
"""


@dataclass
class ActivityWebchat:
    session_id: str
    text: str


class IntegrationWebchat(fi_messenger.FlexusMessenger):
    platform_name = "webchat"
    emessage_type = "WEBCHAT"

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, default_fexp_name: str = "default"):
        super().__init__(fclient, rcx)
        self.default_fexp_name = default_fexp_name
        self._activity_callback: Callable[[ActivityWebchat, bool], Awaitable[None]] = self.default_activity_to_inbox

    def on_incoming_activity(self, handler: Callable[[ActivityWebchat, bool], Awaitable[None]]):
        self._activity_callback = handler
        return handler

    async def default_activity_to_inbox(self, a: ActivityWebchat, already_posted: bool):
        if already_posted:
            return
        await ckit_kanban.bot_kanban_post_into_inbox(
            self.fclient, self.rcx.persona.persona_id,
            title=f"Web chat session={a.session_id}\n{a.text}",
            details_json=json.dumps({"session_id": a.session_id, "text": a.text}),
            provenance_message="webchat_inbound",
            fexp_name=self.default_fexp_name,
        )

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP
        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error
        if not op or "help" in op or "status" in op:
            return HELP
        if op == "capture":
            session_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "session_id", None)
            if not session_id:
                return "Missing session_id parameter\n"
            if already := self.recent_thread_that_captures(session_id):
                if already.thread_fields.ft_id == toolcall.fcall_ft_id:
                    return "Already captured\n"
                return fi_messenger.OTHER_CHAT_ALREADY_CAPTURING_MSG % session_id
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable=f"webchat/{session_id}")
            if fthread := self.rcx.latest_threads.get(toolcall.fcall_ft_id):
                fthread.thread_fields.ft_app_searchable = f"webchat/{session_id}"
            return fi_messenger.CAPTURE_SUCCESS_MSG % session_id + fi_messenger.CAPTURE_ADVICE_MSG
        if op == "uncapture":
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable="")
            if fthread := self.rcx.latest_threads.get(toolcall.fcall_ft_id):
                fthread.thread_fields.ft_app_searchable = ""
            return fi_messenger.UNCAPTURE_SUCCESS_MSG
        return fi_messenger.UNKNOWN_OPERATION_MSG % op

    async def handle_emessage(self, emsg: ckit_bot_query.FExternalMessageOutput) -> None:
        payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
        text = payload.get("text", "")
        session_id = emsg.emsg_from.split(":", 1)[1] if ":" in emsg.emsg_from else emsg.emsg_from
        if not text.strip():
            return
        http = await self.fclient.use_http()
        ft_id = await ckit_ask_model.captured_thread_post_user_message(http, self.rcx.persona.persona_id, f"webchat/{session_id}", text)
        if ft_id:
            logger.info("%s webchat inbound captured ft_id=%s session=%s: %s", self.rcx.persona.persona_id, ft_id, session_id, text[:120])
        else:
            logger.info("%s webchat inbound session=%s no capture: %s", self.rcx.persona.persona_id, session_id, text[:120])
        await self._activity_callback(ActivityWebchat(session_id=session_id, text=text), bool(ft_id))

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False
        searchable = msg.ft_app_searchable or ""
        if not searchable.startswith("webchat/"):
            return False
        session_id = searchable[len("webchat/"):]
        text = msg.ftm_content
        if "TASK_COMPLETED" in text and len(text) <= len("TASK_COMPLETED") + 6:
            return False
        text = text.replace("TASK_COMPLETED", "")
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(gql.gql("""
                mutation WebchatDeliverReply($session_id: String!, $text: String!) {
                    webchat_deliver_reply(session_id: $session_id, text: $text)
                }"""),
                variable_values={"session_id": session_id, "text": text},
            )
        logger.info("%s webchat reply to session=%s: %s", self.rcx.persona.persona_id, session_id, text[:80])
        return True
