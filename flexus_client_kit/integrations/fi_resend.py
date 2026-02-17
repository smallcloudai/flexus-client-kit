import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

import gql
import httpx

from flexus_client_kit import ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool

logger = logging.getLogger("resend")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_TESTING_DOMAIN = os.environ.get("RESEND_TESTING_DOMAIN", "")
RESEND_BASE = "https://api.resend.com"

RESEND_SETUP_SCHEMA = [
    {
        "bs_name": "RESEND_API_KEY",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Email",
        "bs_importance": 0,
        "bs_description": "Your own Resend API key. Leave empty to use the managed platform key.",
    },
    {
        "bs_name": "RESEND_SIGNING_SECRET",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "Email",
        "bs_importance": 0,
        "bs_description": "Webhook signing secret from your Resend account (whsec_...). Recommended for verifying incoming webhook signatures.",
    },
    {
        "bs_name": "DOMAINS",
        "bs_type": "string_multiline",
        "bs_default": "{}",
        "bs_group": "Email",
        "bs_importance": 0,
        "bs_description": 'Registered domains, e.g. {"mail.example.com": "d_abc123"}. Send and receive emails from these domains. Incoming emails are logged as CRM activities.',
    },
]

RESEND_PROMPT = f"""## Email

Use email_send() to send emails. Use email_setup_domain() to register and manage sending domains, call email_setup_domain(op="help") first.
Users can configure EMAIL_RESPOND_TO addresses — emails to those addresses are handled as tasks, all others are logged as CRM activities.
Strongly recommend using a subdomain (e.g. mail.example.com) instead of the main domain, especially for inbound emails.
If no domain is configured, send from *@{RESEND_TESTING_DOMAIN} for testing.
Never use flexus_my_setup() for email domains — they are saved automatically via email_setup_domain() tool.
If user has their own RESEND_API_KEY and wants to receive inbound emails, call email_setup_domain(op="help") for webhook setup instructions."""

RESEND_SEND_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="email_send",
    description="Send an email. Provide html and/or text body.",
    parameters={
        "type": "object",
        "properties": {
            "from": {"type": "string", "order": 1, "description": "Sender, e.g. Name <noreply@domain.com>"},
            "to": {"type": "array", "items": {"type": "string"}, "order": 2, "description": "Recipient email addresses"},
            "subject": {"type": "string", "order": 3, "description": "Subject line"},
            "html": {"type": "string", "order": 4, "description": "HTML body, or empty string if text-only"},
            "text": {"type": "string", "order": 5, "description": "Plain text fallback, or empty string if html-only"},
            "cc": {"type": "array", "items": {"type": "string"}, "order": 6, "description": "CC recipient email addresses"},
            "bcc": {"type": "array", "items": {"type": "string"}, "order": 7, "description": "BCC recipient email addresses"},
            "reply_to": {"type": "string", "order": 8, "description": "Reply-to address, or empty string"},
        },
        "required": ["from", "to", "subject", "html", "text", "cc", "bcc", "reply_to"],
        "additionalProperties": False,
    },
)

RESEND_SETUP_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="email_setup_domain",
    description="Manage email domains: add, verify, check status, list, delete. Call with op=\"help\" for usage. Before adding a domain, ask the user if they want to enable receiving emails on it.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation: help, add, verify, status, list, delete"},
            "args": {"type": "object"},
        },
        "required": [],
    },
)

SETUP_HELP = """Email domain setup:

email_setup_domain(op="add", args={"domain": "yourdomain.com", "region": "us-east-1", "enable_receiving": true})
    Register a domain or update an existing one. Returns DNS records to configure.
    If the domain already exists, updates its settings (receiving, etc.).
    Ask the user which region they prefer and whether they want to enable receiving emails.
    Regions: us-east-1, eu-west-1, sa-east-1, ap-northeast-1.

email_setup_domain(op="verify", args={"domain_id": "..."})
    Trigger verification after adding DNS records. May take a few minutes.

email_setup_domain(op="status", args={"domain_id": "..."})
    Check verification status and DNS records.

email_setup_domain(op="list")
    List all registered domains and their verification status.

email_setup_domain(op="delete", args={"domain_id": "..."})
    Remove a domain.

Receiving emails with your own Resend account (requires RESEND_API_KEY in bot setup):
    1. In Resend dashboard, create a webhook pointing to: https://flexus.team/v1/webhook/resend/PERSONA_ID
       (use BotPersonaId from your setup config)
    2. Subscribe to event: email.received
    3. Recommended: copy the signing secret (whsec_...) into RESEND_SIGNING_SECRET in bot setup for security
"""


@dataclass
class ActivityEmail:
    email_id: str
    from_addr: str
    from_full: str  # "Name <email>" if available
    to_addrs: List[str]
    cc_addrs: List[str]
    bcc_addrs: List[str]
    subject: str
    body_text: str
    body_html: str


def _setup_help(has_domains: bool) -> str:
    if not has_domains and RESEND_TESTING_DOMAIN:
        return SETUP_HELP + f"No domains configured yet. Send from @{RESEND_TESTING_DOMAIN} in the meantime.\n"
    return SETUP_HELP


async def _check_dns_txt(domain: str, expected: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"https://dns.google/resolve?name={domain}&type=TXT")
            return any(expected in a.get("data", "") for a in r.json().get("Answer", []))
    except Exception as e:
        logger.warning("DNS TXT check failed for %s: %s", domain, e)
        return False


def parse_emessage(emsg: ckit_bot_query.FExternalMessageOutput) -> ActivityEmail:
    payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
    content = payload.get("email_content", {})
    data = payload.get("data", {})
    header_from = content.get("headers", {}).get("from", "")
    return ActivityEmail(
        email_id=data.get("email_id", emsg.emsg_external_id),
        from_addr=emsg.emsg_from or data.get("from", ""),
        from_full=header_from or data.get("from", "") or emsg.emsg_from,
        to_addrs=data.get("to", []),
        cc_addrs=data.get("cc", []),
        bcc_addrs=data.get("bcc", []),
        subject=content.get("subject", data.get("subject", "")),
        body_text=content.get("text", ""),
        body_html=content.get("html", ""),
    )


class IntegrationResend:

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, domains: Dict[str, str], emails_to_register: set):
        self.fclient = fclient
        self.rcx = rcx
        self.domains = domains  # {"domain.com": "resend_domain_id"}
        self.emails_to_register = emails_to_register

    async def send_called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]):
        if not model_produced_args:
            return "Provide from, to, subject, and html or text body."
        a = model_produced_args
        frm, to = a.get("from", ""), a.get("to", [])
        if not frm or not to:
            return "Missing required: 'from' and 'to'"
        if not a.get("html", "") and not a.get("text", ""):
            return "Provide 'html' and/or 'text'"
        http = await self.fclient.use_http()
        async with http as h:
            r = await h.execute(gql.gql("""mutation ResendBotSendEmail($input: ResendEmailSendInput!) {
                resend_email_send(input: $input)
            }"""), variable_values={"input": {
                "persona_id": self.rcx.persona.persona_id,
                "email_from": frm,
                "email_to": to,
                "email_subject": a.get("subject", ""),
                "email_html": a.get("html", ""),
                "email_text": a.get("text", ""),
                "email_cc": a.get("cc", []),
                "email_bcc": a.get("bcc", []),
                "email_reply_to": a.get("reply_to", ""),
            }})
        rid = r.get("resend_email_send", "")
        logger.info("sent email %s to %s", rid, to)
        return ckit_cloudtool.ToolResult(content=f"Email sent (id: {rid})", dollars=0)

    async def setup_called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]):
        if not model_produced_args:
            return _setup_help(bool(self.domains))
        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error
        if not op or "help" in op:
            return _setup_help(bool(self.domains))
        gql_input = {"persona_id": self.rcx.persona.persona_id, "op": op}
        for k in ("domain", "domain_id", "region"):
            if v := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, k, None):
                gql_input[k] = v
        if ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "enable_receiving", False):
            gql_input["enable_receiving"] = True
        if op == "add" and not gql_input.get("domain"):
            return "domain is required for add"
        if op in ("verify", "status", "delete") and not gql_input.get("domain_id"):
            return "domain_id is required for " + op
        http = await self.fclient.use_http()
        async with http as h:
            r = await h.execute(gql.gql("""mutation ResendBotSetupDomain($input: ResendSetupDomainInput!) {
                resend_setup_domain(input: $input)
            }"""), variable_values={"input": gql_input})
        return r.get("resend_setup_domain", "")
