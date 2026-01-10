import asyncio
import json
import logging
import time
import random
from typing import Optional

import gql
from telegram import Bot as TelegramBot, Update as TelegramUpdate
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.integrations.fi_messenger import IntegrationMessenger

logger = logging.getLogger("tlgrm")


class IntegrationTelegram(IntegrationMessenger):
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        telegram_bot_token: str,
        bot_username: str,
        enable_summarization: bool = True,
        message_limit_threshold: int = 80,
        budget_limit_threshold: float = 0.8,
    ):
        super().__init__(fclient, rcx, enable_summarization, message_limit_threshold, budget_limit_threshold)
        self.telegram_bot_token = telegram_bot_token
        self.bot_username = bot_username
        self.application = None
        self.problems = []
        self._conversation_state = {}  # In-memory state: {chat_id: {ft_id, contact_id, updated_ts}}

        if not telegram_bot_token:
            self.problems.append("No telegram_bot_token provided")
            logger.warning("Telegram integration disabled (no token)")
            return

        try:
            self.application = Application.builder().token(telegram_bot_token).build()
            self._setup_handlers()
            logger.info("Telegram integration initialized for persona %s", self.rcx.persona.persona_id)
        except Exception as e:
            logger.error("Failed to initialize Telegram application", exc_info=e)
            self.problems.append(f"{type(e).__name__}: {e}")

    def _setup_handlers(self):
        if not self.application:
            return

        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(CommandHandler("help", self._handle_help))
        self.application.add_handler(CommandHandler("exit", self._handle_exit))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

    async def start_reactive(self):
        if not self.application:
            logger.warning("Telegram application not initialized, polling disabled")
            return

        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(allowed_updates=["message"])
            logger.info("Telegram polling started for persona %s", self.rcx.persona.persona_id)
        except Exception as e:
            logger.error("Failed to start Telegram polling", exc_info=e)
            self.problems.append(f"Polling error: {e}")

    async def close(self):
        if not self.application:
            return

        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram integration closed for persona %s", self.rcx.persona.persona_id)
        except Exception as e:
            logger.error("Error closing Telegram integration", exc_info=e)

    def _get_messenger_link(self, platform: str, handle: str) -> str:
        if platform != "telegram":
            raise ValueError(f"IntegrationTelegram only supports telegram platform, not {platform}")
        return f"https://t.me/{self.bot_username}?start={handle}"

    async def _handle_start(self, update: TelegramUpdate, context):
        if not update.effective_chat:
            return

        chat_id = str(update.effective_chat.id)
        thread = self._thread_capturing(chat_id)

        if thread:
            await update.message.reply_text(
                "You already have an active conversation! Just send your message."
            )
            return

        await update.message.reply_text(
            "Welcome! Please enter your access code to continue.\n\n"
            "If you don't have one, please request it from our service."
        )

    async def _handle_help(self, update: TelegramUpdate, context):
        await update.message.reply_text(
            f"Bot Assistant (@{self.bot_username})\n\n"
            "Commands:\n"
            "/start - Begin conversation\n"
            "/help - Show this help\n"
            "/exit - End current conversation\n\n"
            "Just send me messages and I'll respond!"
        )

    async def _handle_exit(self, update: TelegramUpdate, context):
        if not update.effective_chat:
            return

        chat_id = str(update.effective_chat.id)

        # Check both in-memory state and captured threads
        thread = self._thread_capturing(chat_id)
        conv_state = await self._get_conversation_state(chat_id)

        if not thread and (not conv_state or not conv_state.get("ft_id")):
            await update.message.reply_text(
                "You don't have an active conversation to exit.\n\n"
                "Use /start to begin a new conversation."
            )
            return

        ft_id = thread.thread_fields.ft_id if thread else conv_state.get("ft_id")

        try:
            # Uncapture the thread
            http = await self.fclient.use_http()
            await ckit_ask_model.thread_app_capture_patch(
                http,
                ft_id,
                ft_app_searchable="",  # Empty string uncaptures
                ft_app_specific=json.dumps({
                    "platform": "telegram",
                    "disconnected_ts": time.time(),
                }),
            )

            # Clear conversation state
            if chat_id in self._conversation_state:
                del self._conversation_state[chat_id]

            await update.message.reply_text(
                "✅ Conversation ended successfully.\n\n"
                "To start a new conversation, enter a new access code or use /start."
            )

            logger.info("Telegram conversation exited for chat %s, thread %s", chat_id, ft_id)

        except Exception as e:
            logger.error("Failed to exit conversation for chat %s", chat_id, exc_info=e)
            await update.message.reply_text(
                "⚠️ There was an error ending the conversation, but you can still enter a new access code to start fresh."
            )

    async def _handle_message(self, update: TelegramUpdate, context):
        if not update.effective_chat or not update.message:
            return

        chat_id = str(update.effective_chat.id)
        text = update.message.text or ""
        username = update.effective_user.username if update.effective_user else f"user_{update.effective_chat.id}"

        conv_state = await self._get_conversation_state(chat_id)

        if conv_state and conv_state.get("awaiting_handle"):
            await self._validate_handle_and_create_thread(chat_id, text, update)
            return

        thread = self._thread_capturing(chat_id)

        if not thread:
            await self._validate_handle_and_create_thread(chat_id, text, update)
            return

        if self.enable_summarization:
            should_restart, restart_reason = await self.should_restart_thread(thread)

            if should_restart:
                await self._restart_thread_with_summary(chat_id, thread, restart_reason)
                thread = self._thread_capturing(chat_id)

        await self._post_message_to_thread(chat_id, text, username, thread)

    async def _validate_handle_and_create_thread(self, chat_id: str, handle: str, update: TelegramUpdate):
        handle_data = await self.validate_messenger_handle("telegram", handle.strip())

        if not handle_data:
            await update.message.reply_text(
                "Invalid or expired access code. Please check and try again.\n\n"
                "Codes expire after 10 minutes. If you need a new one, please contact us."
            )
            return

        contact_id = handle_data.get("contact_id", "")
        web_ft_id = handle_data.get("ft_id", "")

        try:
            ft_id = await ckit_ask_model.bot_activate(
                self.fclient,
                who_is_asking="telegram_activation",
                persona_id=self.rcx.persona.persona_id,
                skill="default",
                first_question="Fulfill the user's request professionally. Don't mention any technical details about threads, tools, CRM or any other functionality.",
                cd_instruction=json.dumps(f"TELEGRAM CONNECTION CONTEXT:\n\nCRM contact ID: {contact_id}\n\nFetch all required information about the contact first.\n\nGreet the contact and continue the conversation from where you left off on the web platform."),
                title=f"Telegram: {chat_id}",
            )

            http = await self.fclient.use_http()
            searchable = f"telegram/{self.rcx.persona.persona_id}/{chat_id}"

            await ckit_ask_model.thread_app_capture_patch(
                http,
                ft_id,
                ft_app_searchable=searchable,
                ft_app_specific=json.dumps({
                    "last_posted_assistant_ts": time.time(),
                    "contact_id": contact_id,
                    "web_ft_id": web_ft_id,
                    "started_ts": time.time(),
                    "platform": "telegram",
                }),
            )

            await self._update_conversation_state(chat_id, {
                "ft_id": ft_id,
                "contact_id": contact_id,
                "updated_ts": time.time(),
            })

            logger.info("Telegram handle validated and thread created: %s for persona %s", ft_id, self.rcx.persona.persona_id)

        except Exception as e:
            logger.error("Failed to create thread after handle validation", exc_info=e)
            await update.message.reply_text(
                "Sorry, there was an error setting up our conversation. Please try again or contact support."
            )

    async def _restart_thread_with_summary(self, chat_id: str, old_thread, reason: str):
        try:
            summary = await self.generate_thread_summary(old_thread)

            app_specific = old_thread.thread_fields.ft_app_specific
            contact_id = app_specific.get("contact_id", "") if app_specific else ""

            ft_id = await ckit_ask_model.bot_activate(
                self.fclient,
                who_is_asking="telegram_thread_restart",
                persona_id=self.rcx.persona.persona_id,
                skill="default",
                first_question="",
                title=f"Telegram continued: {chat_id}",
            )

            http = await self.fclient.use_http()

            await ckit_ask_model.thread_add_user_message(
                http,
                ft_id,
                summary,
                "telegram_restart",
                ftm_alt=100,
                role="cd_instruction",
            )

            searchable = f"telegram/{self.rcx.persona.persona_id}/{chat_id}"
            await ckit_ask_model.thread_app_capture_patch(
                http,
                ft_id,
                ft_app_searchable=searchable,
                ft_app_specific=json.dumps({
                    "last_posted_assistant_ts": time.time(),
                    "contact_id": contact_id,
                    "previous_ft_id": old_thread.thread_fields.ft_id,
                    "restart_reason": reason,
                    "started_ts": time.time(),
                    "platform": "telegram",
                }),
            )

            await ckit_ask_model.thread_app_capture_patch(
                http,
                old_thread.thread_fields.ft_id,
                ft_app_searchable="",
            )

            await self._update_conversation_state(chat_id, {
                "ft_id": ft_id,
                "contact_id": contact_id,
                "updated_ts": time.time(),
            })

            logger.info(
                "Restarted thread %s -> %s for persona %s, reason: %s",
                old_thread.thread_fields.ft_id,
                ft_id,
                self.rcx.persona.persona_id,
                reason
            )

        except Exception as e:
            logger.error("Failed to restart thread with summary", exc_info=e)

    async def _post_message_to_thread(self, chat_id: str, text: str, username: str, thread):
        try:
            http = await self.fclient.use_http()

            await ckit_ask_model.thread_add_user_message(
                http,
                thread.thread_fields.ft_id,
                content=text,
                ftm_alt=100,
                who_is_asking=f"telegram_user_{username}",
            )

            logger.debug("Posted message to thread %s from Telegram %s", thread.thread_fields.ft_id, chat_id)

        except Exception as e:
            logger.error("Failed to post message to thread", exc_info=e)

            if self.application:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text="Sorry, there was an error processing your message. Please try again."
                )

    async def look_assistant_might_have_posted_something(self, msg: ckit_ask_model.FThreadMessageOutput) -> bool:
        if msg.ftm_role != "assistant":
            return False
        if not msg.ftm_content:
            return False

        fthread = self.rcx.latest_threads.get(msg.ftm_belongs_to_ft_id, None)
        if not fthread:
            return False

        searchable = fthread.thread_fields.ft_app_searchable
        if not searchable or not searchable.startswith(f"telegram/{self.rcx.persona.persona_id}/"):
            return False

        parts = searchable.split("/")
        if len(parts) < 3:
            return False

        chat_id = parts[2]

        app_specific = fthread.thread_fields.ft_app_specific
        if app_specific:
            last_posted_ts = app_specific.get("last_posted_assistant_ts", 0)
            if msg.ftm_created_ts <= last_posted_ts:
                return False

        try:
            if self.application:
                await self.application.bot.send_message(
                    chat_id=int(chat_id),
                    text=msg.ftm_content,
                )

                http = await self.fclient.use_http()
                await ckit_ask_model.thread_app_capture_patch(
                    http,
                    fthread.thread_fields.ft_id,
                    ft_app_specific=json.dumps({
                        **(app_specific or {}),
                        "last_posted_assistant_ts": msg.ftm_created_ts,
                    })
                )

                logger.debug("Sent assistant message to Telegram %s", chat_id)
                return True

        except Exception as e:
            logger.error("Failed to send message to Telegram %s", chat_id, exc_info=e)
            return False

        return False

    def _thread_capturing(self, chat_id: str):
        searchable = f"telegram/{self.rcx.persona.persona_id}/{chat_id}"
        for t in self.rcx.latest_threads.values():
            if t.thread_fields.ft_app_searchable == searchable:
                return t
        return None

    async def _get_conversation_state(self, chat_id: str):
        """Get conversation state from in-memory cache."""
        return self._conversation_state.get(chat_id)

    async def _update_conversation_state(self, chat_id: str, state: dict):
        """Update conversation state in in-memory cache."""
        state["updated_ts"] = time.time()
        self._conversation_state[chat_id] = state
