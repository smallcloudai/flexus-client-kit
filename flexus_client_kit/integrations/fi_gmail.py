# Inspired from: https://github.com/n8n-io/n8n/blob/master/packages/nodes-base/nodes/Google/Gmail/V2/GmailV2.node.ts

import base64
import logging
import time
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import message_from_string
from email.policy import default
from typing import Dict, Any, Optional, List

import html2text
import gql
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client

logger = logging.getLogger("gmail")

GMAIL_TOOL = ckit_cloudtool.CloudTool(
    name="gmail",
    description="Interact with Gmail, call with op=\"help\" to print usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": []
    },
)

HELP = """
Help:

gmail(op="status")
    Show connection status and available operations.

# Message Operations
gmail(op="send", args={
    "to": "recipient@example.com",
    "subject": "Hello",
    "body": "Plain text message",
    "cc": "optional@example.com",  # Optional
    "bcc": "secret@example.com",  # Optional
    "html": False  # Set to True for HTML emails
})

gmail(op="search", args={
    "query": "is:unread from:boss@company.com",
    "maxResults": 10,  # Optional, default 10
    "labelIds": ["INBOX"]  # Optional
})
    Search using Gmail search syntax. Common queries:
    - "is:unread" - unread messages
    - "from:user@example.com" - from specific sender
    - "subject:urgent" - subject contains word
    - "has:attachment" - has attachments
    - "after:2024/01/01" - after date

gmail(op="get", args={"messageId": "18d4..."})
    Get full message details including body and attachments.

gmail(op="delete", args={"messageId": "18d4..."})
    Permanently delete a message.

gmail(op="markAsRead", args={"messageId": "18d4..."})
gmail(op="markAsUnread", args={"messageId": "18d4..."})

gmail(op="addLabels", args={"messageId": "18d4...", "labelIds": ["Label_123"]})
gmail(op="removeLabels", args={"messageId": "18d4...", "labelIds": ["Label_123"]})

# Label Operations
gmail(op="listLabels")
    List all Gmail labels.

gmail(op="createLabel", args={"name": "MyLabel"})
    Create a new label.

gmail(op="deleteLabel", args={"labelId": "Label_123"})
    Delete a label.

# Draft Operations
gmail(op="createDraft", args={
    "to": "recipient@example.com",
    "subject": "Draft",
    "body": "Draft content"
})

gmail(op="listDrafts", args={"maxResults": 10})

gmail(op="deleteDraft", args={"draftId": "r123..."})

# Thread Operations
gmail(op="getThread", args={"threadId": "18d4..."})
    Get all messages in a thread.

gmail(op="searchThreads", args={"query": "is:unread", "maxResults": 10})

gmail(op="deleteThread", args={"threadId": "18d4..."})
"""

GMAIL_SETUP_SCHEMA = [
    {
        "bs_name": "GMAIL_OAUTH_REQUIRED",
        "bs_type": "string_long",
        "bs_default": "true",
        "bs_group": "Gmail",
        "bs_importance": 0,
        "bs_description": "Gmail requires Google OAuth authentication via flexus external auth system",
    },
]


@dataclass
class GmailMessage:
    id: str
    threadId: str
    subject: str
    from_addr: str
    to_addr: str
    date: str
    snippet: str
    body_text: str
    body_html: str
    labels: List[str]
    has_attachments: bool


class IntegrationGmail:

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,  # ckit_bot_exec.RobotContext
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.service = None
        self.last_token_check = 0
        self.access_token = None
        self.token_expires_at = 0

    async def _ensure_authenticated(self) -> bool:
        if self.service and time.time() < self.token_expires_at - 120:
            return True

        try:
            http = await self.fclient.use_http()

            async with http as h:
                r = await h.execute(
                    gql.gql("""
                        query GetGmailToken($ws_id: String!, $provider: String!) {
                            external_auth_token(ws_id: $ws_id, provider: $provider) {
                                access_token
                                expires_at
                                token_type
                                scope_values
                            }
                        }
                    """),
                    variable_values={
                        "ws_id": self.rcx.persona.ws_id,
                        "provider": "google",
                    }
                )

            if not r or not r.get("external_auth_token"):
                return False

            token_data = r["external_auth_token"]
            self.access_token = token_data["access_token"]
            self.token_expires_at = token_data.get("expires_at", 0)

            creds = Credentials(token=self.access_token)
            self.service = build('gmail', 'v1', credentials=creds)

            logger.info("Gmail authentication successful for user %s", self.rcx.persona.owner_fuser_id)
            return True

        except Exception as e:
            logger.error("Failed to authenticate with Gmail: %s", e, exc_info=e)
            return False

    async def _initiate_oauth_flow(self) -> str:
        try:
            http = await self.fclient.use_http()

            async with http as h:
                r = await h.execute(
                    gql.gql("""
                        mutation StartGmailOAuth($ws_id: String!, $provider: String!, $scope_values: [String!]) {
                            external_auth_start(
                                ws_id: $ws_id,
                                provider: $provider,
                                scope_values: $scope_values
                            ) {
                                authorization_url
                            }
                        }
                    """),
                    variable_values={
                        "ws_id": self.rcx.persona.ws_id,
                        "provider": "google",
                        "scope_values": [
                            "https://www.googleapis.com/auth/gmail.readonly",
                            "https://www.googleapis.com/auth/gmail.compose",
                            "https://www.googleapis.com/auth/gmail.modify",
                            "https://www.googleapis.com/auth/gmail.send",
                            "https://www.googleapis.com/auth/gmail.labels",
                        ]
                    }
                )

            if not r or not r.get("external_auth_start"):
                raise Exception("Failed to initiate OAuth flow")

            return r["external_auth_start"]["authorization_url"]

        except Exception as e:
            logger.error("Failed to initiate OAuth flow: %s", e, exc_info=e)
            raise

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]]
    ) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        # Check authentication first
        authenticated = await self._ensure_authenticated()

        if print_status:
            r = f"Gmail integration status:\n"
            r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
            r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
            r += f"  Workspace: {self.rcx.persona.ws_id}\n"
            if not authenticated:
                try:
                    auth_url = await self._initiate_oauth_flow()
                    r += f"\n⚠️  Please authorize Gmail access:\n{auth_url}\n"
                except Exception as e:
                    r += f"\n❌ Error initiating OAuth: {e}\n"
            return r

        if print_help:
            return HELP

        if not authenticated:
            try:
                auth_url = await self._initiate_oauth_flow()
                return f"⚠️  Gmail not authorized. Please visit:\n{auth_url}\n\nThen try again."
            except Exception as e:
                return f"❌ Failed to initiate OAuth: {e}"

        try:
            if op == "send":
                return await self._send_message(args)
            elif op == "search":
                return await self._search_messages(args)
            elif op == "get":
                return await self._get_message(args)
            elif op == "delete":
                return await self._delete_message(args)
            elif op == "markAsRead":
                return await self._mark_as_read(args)
            elif op == "markAsUnread":
                return await self._mark_as_unread(args)
            elif op == "addLabels":
                return await self._add_labels(args)
            elif op == "removeLabels":
                return await self._remove_labels(args)
            elif op == "listLabels":
                return await self._list_labels(args)
            elif op == "createLabel":
                return await self._create_label(args)
            elif op == "deleteLabel":
                return await self._delete_label(args)
            elif op == "createDraft":
                return await self._create_draft(args)
            elif op == "listDrafts":
                return await self._list_drafts(args)
            elif op == "deleteDraft":
                return await self._delete_draft(args)
            elif op == "getThread":
                return await self._get_thread(args)
            elif op == "searchThreads":
                return await self._search_threads(args)
            elif op == "deleteThread":
                return await self._delete_thread(args)
            else:
                return f"❌ Unknown operation: {op}\n\nTry gmail(op='help') for usage."

        except HttpError as e:
            error_msg = f"Gmail API error: {e.resp.status} - {e.error_details}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
        except Exception as e:
            logger.exception("Error executing Gmail operation")
            return f"❌ Error: {type(e).__name__}: {e}"

    async def _send_message(self, args: Dict[str, Any]) -> str:
        to = args.get("to", "")
        subject = args.get("subject", "")
        body = args.get("body", "")
        cc = args.get("cc", "")
        bcc = args.get("bcc", "")
        is_html = args.get("html", False)

        if not to or not subject:
            return "❌ Missing required parameters: 'to' and 'subject'"

        for field_name, email_list in [("to", to), ("cc", cc), ("bcc", bcc)]:
            if email_list:
                for email in email_list.split(","):
                    email = email.strip()
                    if email and "@" not in email:
                        return f"❌ Invalid email in '{field_name}': {email}"

        if is_html:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(body, "html"))
        else:
            message = MIMEText(body, "plain")

        message["To"] = to
        message["Subject"] = subject
        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        result = self.service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()

        message_id = result.get("id")
        thread_id = result.get("threadId")

        return f"✅ Message sent successfully!\n  Message ID: {message_id}\n  Thread ID: {thread_id}"

    async def _search_messages(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "")
        max_results = args.get("maxResults", 10)
        label_ids = args.get("labelIds", [])

        params = {"userId": "me", "maxResults": min(max_results, 100)}

        if query:
            params["q"] = query

        if label_ids:
            params["labelIds"] = label_ids

        results = self.service.users().messages().list(**params).execute()
        messages = results.get("messages", [])

        if not messages:
            return f"📭 No messages found for query: {query or '(all)'}"

        output_lines = [f"📬 Found {len(messages)} message(s):\n"]

        for i, msg in enumerate(messages[:max_results], 1):
            msg_id = msg["id"]
            msg_detail = self.service.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in msg_detail["payload"]["headers"]}
            snippet = msg_detail.get("snippet", "")

            output_lines.append(f"{i}. ID: {msg_id}")
            output_lines.append(f"   From: {headers.get('From', 'Unknown')}")
            output_lines.append(f"   Subject: {headers.get('Subject', '(no subject)')}")
            output_lines.append(f"   Preview: {snippet[:80]}...")
            output_lines.append("")

        output_lines.append(f"💡 Use gmail(op='get', args={{'messageId': '{messages[0]['id']}'}}) to read full message")

        return "\n".join(output_lines)

    async def _get_message(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")

        if not message_id:
            return "❌ Missing required parameter: 'messageId'"

        message = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="raw"
        ).execute()

        raw_email = base64.urlsafe_b64decode(message["raw"]).decode("utf-8", errors="replace")
        parsed_email = message_from_string(raw_email, policy=default)

        body_plain = parsed_email.get_body(preferencelist=('plain',))
        body_html = parsed_email.get_body(preferencelist=('html',))

        if body_plain:
            body_content = body_plain.get_content()
            body_type = "plain text"
        elif body_html:
            html_content = body_html.get_content()
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            body_content = h.handle(html_content)
            body_type = "converted from HTML"
        else:
            body_content = "(no body content)"
            body_type = "none"

        max_preview = 5000
        output = [
            f"📧 Message Details:",
            f"",
            f"ID: {message_id}",
            f"Thread ID: {message.get('threadId')}",
            f"From: {parsed_email.get('From', 'Unknown')}",
            f"To: {parsed_email.get('To', 'Unknown')}",
            f"Subject: {parsed_email.get('Subject', '(no subject)')}",
            f"Date: {parsed_email.get('Date', 'Unknown')}",
            f"Body type: {body_type}",
            f"",
            f"--- Message Body ---",
            body_content[:max_preview],
        ]

        if len(body_content) > max_preview:
            output.append(f"\n... (truncated, {len(body_content)} total characters)")

        return "\n".join(output)

    async def _delete_message(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")

        if not message_id:
            return "❌ Missing required parameter: 'messageId'"

        self.service.users().messages().delete(userId="me", id=message_id).execute()

        return f"✅ Message {message_id} deleted successfully"

    async def _mark_as_read(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")

        if not message_id:
            return "❌ Missing required parameter: 'messageId'"

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

        return f"✅ Message {message_id} marked as read"

    async def _mark_as_unread(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")

        if not message_id:
            return "❌ Missing required parameter: 'messageId'"

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": ["UNREAD"]}
        ).execute()

        return f"✅ Message {message_id} marked as unread"

    async def _add_labels(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")
        label_ids = args.get("labelIds", [])

        if not message_id or not label_ids:
            return "❌ Missing required parameters: 'messageId' and 'labelIds'"

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": label_ids}
        ).execute()

        return f"✅ Added {len(label_ids)} label(s) to message {message_id}"

    async def _remove_labels(self, args: Dict[str, Any]) -> str:
        message_id = args.get("messageId", "")
        label_ids = args.get("labelIds", [])

        if not message_id or not label_ids:
            return "❌ Missing required parameters: 'messageId' and 'labelIds'"

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": label_ids}
        ).execute()

        return f"✅ Removed {len(label_ids)} label(s) from message {message_id}"

    async def _list_labels(self, args: Dict[str, Any]) -> str:
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            return "📭 No labels found"

        output = [f"🏷️  Found {len(labels)} label(s):\n"]
        for label in labels:
            label_id = label["id"]
            label_name = label["name"]
            label_type = label.get("type", "user")
            output.append(f"  {label_name} (ID: {label_id}, Type: {label_type})")

        return "\n".join(output)

    async def _create_label(self, args: Dict[str, Any]) -> str:
        name = args.get("name", "")

        if not name:
            return "❌ Missing required parameter: 'name'"

        body = {
            "name": name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }

        result = self.service.users().labels().create(userId="me", body=body).execute()

        return f"✅ Label '{name}' created successfully (ID: {result['id']})"

    async def _delete_label(self, args: Dict[str, Any]) -> str:
        label_id = args.get("labelId", "")

        if not label_id:
            return "❌ Missing required parameter: 'labelId'"

        self.service.users().labels().delete(userId="me", id=label_id).execute()

        return f"✅ Label {label_id} deleted successfully"

    async def _create_draft(self, args: Dict[str, Any]) -> str:
        to = args.get("to", "")
        subject = args.get("subject", "")
        body = args.get("body", "")

        if not to or not subject:
            return "❌ Missing required parameters: 'to' and 'subject'"

        message = MIMEText(body, "plain")
        message["To"] = to
        message["Subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        result = self.service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw_message}}
        ).execute()

        draft_id = result.get("id")

        return f"✅ Draft created successfully (ID: {draft_id})"

    async def _list_drafts(self, args: Dict[str, Any]) -> str:
        max_results = args.get("maxResults", 10)

        results = self.service.users().drafts().list(
            userId="me",
            maxResults=max_results
        ).execute()

        drafts = results.get("drafts", [])

        if not drafts:
            return "📭 No drafts found"

        output = [f"📝 Found {len(drafts)} draft(s):\n"]

        for i, draft in enumerate(drafts, 1):
            draft_id = draft["id"]

            draft_detail = self.service.users().drafts().get(
                userId="me",
                id=draft_id,
                format="metadata"
            ).execute()

            message = draft_detail.get("message", {})
            headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
            snippet = message.get("snippet", "(no preview)")

            output.append(f"{i}. ID: {draft_id}")
            output.append(f"   To: {headers.get('To', '(not set)')}")
            output.append(f"   Subject: {headers.get('Subject', '(no subject)')}")
            output.append(f"   Preview: {snippet[:80]}...")
            output.append("")

        return "\n".join(output)

    async def _delete_draft(self, args: Dict[str, Any]) -> str:
        draft_id = args.get("draftId", "")

        if not draft_id:
            return "❌ Missing required parameter: 'draftId'"

        self.service.users().drafts().delete(userId="me", id=draft_id).execute()

        return f"✅ Draft {draft_id} deleted successfully"

    async def _get_thread(self, args: Dict[str, Any]) -> str:
        thread_id = args.get("threadId", "")

        if not thread_id:
            return "❌ Missing required parameter: 'threadId'"

        thread = self.service.users().threads().get(
            userId="me",
            id=thread_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()

        messages = thread.get("messages", [])

        output = [
            f"🧵 Thread {thread_id} contains {len(messages)} message(s):\n"
        ]

        for i, msg in enumerate(messages, 1):
            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            snippet = msg.get("snippet", "")
            output.append(f"{i}. Message ID: {msg['id']}")
            output.append(f"   From: {headers.get('From', 'Unknown')}")
            output.append(f"   Date: {headers.get('Date', 'Unknown')}")
            output.append(f"   Preview: {snippet[:60]}...")
            output.append("")

        return "\n".join(output)

    async def _search_threads(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "")
        max_results = args.get("maxResults", 10)

        results = self.service.users().threads().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        threads = results.get("threads", [])

        if not threads:
            return f"📭 No threads found for query: {query or '(all)'}"

        output = [f"🧵 Found {len(threads)} thread(s):\n"]

        for i, thread in enumerate(threads, 1):
            thread_id = thread["id"]
            snippet = thread.get("snippet", "")
            output.append(f"{i}. Thread ID: {thread_id}")
            output.append(f"   Preview: {snippet[:80]}...")
            output.append("")

        return "\n".join(output)

    async def _delete_thread(self, args: Dict[str, Any]) -> str:
        thread_id = args.get("threadId", "")

        if not thread_id:
            return "❌ Missing required parameter: 'threadId'"

        self.service.users().threads().delete(userId="me", id=thread_id).execute()

        return f"✅ Thread {thread_id} deleted successfully"
