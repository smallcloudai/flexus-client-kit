import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

import gql

from flexus_client_kit import ckit_ask_model, ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool, ckit_kanban, ckit_scenario
from flexus_client_kit.integrations import fi_messenger

logger = logging.getLogger("mdesk")

MAGIC_DESK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="magic_desk",
    description="Interact with the Magic Desk chat widget. Call with op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
    },
)

HELP = """Help:

magic_desk(op="capture", args={"session_id": "uuid"})
    Capture a Magic Desk chat session. Messages will appear here and your responses will be sent back.

magic_desk(op="uncapture")
    Stop capturing this session.
"""


@dataclass
class ActivityMagicDesk:
    session_id: str
    text: str


class IntegrationMagicDesk(fi_messenger.FlexusMessenger):
    platform_name = "magic_desk"
    emessage_type = "MAGIC_DESK"

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext):
        super().__init__(fclient, rcx)
        self.is_fake = rcx.running_test_scenario
        self._activity_callback: Callable[[ActivityMagicDesk, bool], Awaitable[None]] = self.inbound_activity_to_task

    def on_incoming_activity(self, handler: Callable[[ActivityMagicDesk, bool], Awaitable[None]]):
        self._activity_callback = handler
        return handler

    async def inbound_activity_to_task(self, a: ActivityMagicDesk, already_posted: bool):
        if already_posted:
            return
        await ckit_kanban.bot_kanban_post_into_inprogress(
            await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, ""),
            self.rcx.persona.persona_id,
            title=f"Magic Desk session={a.session_id}\n{a.text}",
            human_id="magic_desk:%s" % a.session_id,
            details_json=json.dumps({"session_id": a.session_id, "text": a.text}),
            provenance_message="magic_desk_inbound",
            fexp_name=self.outside_messages_fexp_name,
        )

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP
        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error
        if self.is_fake:
            return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
        if not op or "help" in op or "status" in op:
            return HELP
        if op == "capture":
            session_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "session_id", None)
            if not session_id:
                return "Missing session_id parameter\n"
            if self.outside_messages_fexp_name and not toolcall.fcall_fexp_name.endswith("_" + self.outside_messages_fexp_name):
                return fi_messenger.CAPTURE_WRONG_EXPERT_MSG % self.outside_messages_fexp_name
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            try:
                await ckit_ask_model.thread_app_capture_patch(http, toolcall.fcall_ft_id, ft_app_searchable=f"magic_desk/{session_id}")
            except gql.transport.exceptions.TransportQueryError as e:
                return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "magic_desk_capture")
            return fi_messenger.CAPTURE_SUCCESS_MSG % session_id + fi_messenger.CAPTURE_ADVICE_MSG
        if op == "uncapture":
            http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)
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
        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        ft_id = await ckit_ask_model.captured_thread_post_user_message(
            http,
            self.rcx.persona.persona_id,
            f"magic_desk/{session_id}",
            text,
            ftm_provenance={"system_type": "captured_thread_post", "mdesk_id": emsg.emsg_external_id},
            only_to_expert=self.outside_messages_fexp_name,
            thread_too_old_s=3600,
        )
        if ft_id:
            logger.info("%s magic_desk inbound captured ft_id=%s session=%s: %s", self.rcx.persona.persona_id, ft_id, session_id, text[:120])
        else:
            logger.info("%s magic_desk inbound session=%s no capture: %s", self.rcx.persona.persona_id, session_id, text[:120])
        await self._activity_callback(ActivityMagicDesk(session_id=session_id, text=text), bool(ft_id))

    async def look_user_message_got_confirmed(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "user" or msg.ftm_num < 0:
            return False
        searchable = msg.ft_app_searchable or ""
        if not searchable.startswith("magic_desk/"):
            return False
        prov = msg.ftm_provenance if isinstance(msg.ftm_provenance, dict) else {}
        if prov.get("system_type") != "captured_thread_post":
            return False
        session_id = searchable[len("magic_desk/"):]
        text = fi_messenger.ftm_content_to_text(msg.ftm_content)
        if not text.strip():
            return False
        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        async with http as h:
            await h.execute(gql.gql("""
                mutation MagicDeskConfirmUserMessage($session_id: String!, $text: String!, $ftm_alt: Int!, $ftm_num: Int!, $mdesk_id: String, $persona_id: String) {
                    magic_desk_deliver_reply(session_id: $session_id, text: $text, role: "user", ftm_alt: $ftm_alt, ftm_num: $ftm_num, mdesk_id: $mdesk_id, persona_id: $persona_id)
                }"""),
                variable_values={"session_id": session_id, "text": text, "ftm_alt": msg.ftm_alt, "ftm_num": msg.ftm_num, "mdesk_id": prov.get("mdesk_id"), "persona_id": self.rcx.persona.persona_id},
            )
        return True

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant" or not msg.ftm_content:
            return False
        searchable = msg.ft_app_searchable or ""
        if not searchable.startswith("magic_desk/"):
            return False
        session_id = searchable[len("magic_desk/"):]
        text = fi_messenger.ftm_content_to_text(msg.ftm_content)
        if "TASK_COMPLETED" in text and len(text) <= len("TASK_COMPLETED") + 6:
            return False
        text = text.replace("TASK_COMPLETED", "")
        http = await self.fclient.use_http_on_behalf(self.rcx.persona.persona_id, "")
        async with http as h:
            await h.execute(gql.gql("""
                mutation MagicDeskDeliverReply($session_id: String!, $text: String!, $ftm_alt: Int!, $ftm_num: Int!, $persona_id: String) {
                    magic_desk_deliver_reply(session_id: $session_id, text: $text, ftm_alt: $ftm_alt, ftm_num: $ftm_num, persona_id: $persona_id)
                }"""),
                variable_values={"session_id": session_id, "text": text, "ftm_alt": msg.ftm_alt, "ftm_num": msg.ftm_num, "persona_id": self.rcx.persona.persona_id},
            )
        logger.info("%s magic_desk reply to session=%s: %s", self.rcx.persona.persona_id, session_id, text[:80])
        return True
