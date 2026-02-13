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
        "bs_name": "DOMAINS",
        "bs_type": "string_multiline",
        "bs_default": "{}",
        "bs_group": "Email",
        "bs_importance": 0,
        "bs_description": 'Registered domains, e.g. {"mail.example.com": "d_abc123"}. Send and receive emails from these domains. Incoming emails are logged as CRM activities.',
    },
]

RESEND_PROMPT = f"""## Email

Use email() tool to send emails and help users register their own domain for sending and receiving. Call email(op="help") first.
Users can configure EMAIL_RESPOND_TO addresses — emails to those addresses are handled as tasks, all others are logged as CRM activities.
Strongly recommend using a subdomain (e.g. mail.example.com) instead of the main domain.
If no domain is configured, send from *@{RESEND_TESTING_DOMAIN} for testing.
Never use flexus_my_setup() for email domains — they are saved automatically via email() tool."""

RESEND_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="email",
    description="Send and receive email, call with op=\"help\" for usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": []
    },
)

HELP = """Help:

email(op="send", args={
    "from": "Name <noreply@yourdomain.com>",
    "to": "recipient@example.com",
    "subject": "Hello",
    "html": "<p>HTML body</p>",
    "text": "Plain text fallback",       # optional if html provided
    "cc": "cc@example.com",              # optional, comma-separated
    "bcc": "bcc@example.com",            # optional, comma-separated
    "reply_to": "reply@example.com",     # optional
})

email(op="add_domain", args={"domain": "yourdomain.com", "region": "us-east-1"})
    Register your own domain. Returns DNS records you need to configure.
    Ask the user which region they prefer before calling.
    Regions: us-east-1, eu-west-1, sa-east-1, ap-northeast-1.

email(op="verify_domain", args={"domain_id": "..."})
    Trigger verification after adding DNS records. May take a few minutes.

email(op="domain_status", args={"domain_id": "..."})
    Check verification status and DNS records.

email(op="list_domains")
    List all registered domains and their verification status.

Notes:
- "from" and "to" are required for send. "to" can be comma-separated.
- Provide "html" and/or "text". At least one is required.
"""


@dataclass
class ActivityEmail:
    email_id: str
    from_addr: str
    to_addrs: List[str]
    cc_addrs: List[str]
    bcc_addrs: List[str]
    subject: str
    body_text: str
    body_html: str


def _help_text(has_domains: bool) -> str:
    if not has_domains and RESEND_TESTING_DOMAIN:
        return HELP + f"- No domains configured yet. Send from @{RESEND_TESTING_DOMAIN} in the meantime.\n"
    return HELP


def _format_dns_records(records) -> str:
    if not records:
        return "  (none)"
    lines = []
    for rec in records:
        lines.append(f"  {rec['record']} {rec['type']} {rec['name']} -> {rec['value']} [{rec['status']}]")
    return "\n".join(lines)


async def _check_dns_txt(domain: str, expected: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"https://dns.google/resolve?name={domain}&type=TXT")
            return any(expected in a.get("data", "") for a in r.json().get("Answer", []))
    except Exception as e:
        logger.warning("DNS TXT check failed for %s: %s", domain, e)
        return False


async def _resend_request(method: str, path: str, json_body: Optional[Dict] = None) -> httpx.Response:
    async with httpx.AsyncClient(timeout=30) as c:
        return await c.request(method, f"{RESEND_BASE}{path}", headers={"Authorization": f"Bearer {RESEND_API_KEY}"}, json=json_body)


def parse_emessage(emsg: ckit_bot_query.FExternalMessageOutput) -> ActivityEmail:
    payload = emsg.emsg_payload if isinstance(emsg.emsg_payload, dict) else json.loads(emsg.emsg_payload)
    content = payload.get("email_content", {})
    data = payload.get("data", {})
    return ActivityEmail(
        email_id=data.get("email_id", emsg.emsg_external_id),
        from_addr=emsg.emsg_from or data.get("from", ""),
        to_addrs=data.get("to", []),
        cc_addrs=data.get("cc", []),
        bcc_addrs=data.get("bcc", []),
        subject=content.get("subject", data.get("subject", "")),
        body_text=content.get("text", ""),
        body_html=content.get("html", ""),
    )


async def register_email_addresses(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
    email_addresses: List[str],
) -> None:
    txt_val = f"flexus-verify={rcx.persona.ws_id}"
    verified = []
    for a in email_addresses:
        domain = a.rsplit("@", 1)[1] if "@" in a else a
        if RESEND_TESTING_DOMAIN and domain == RESEND_TESTING_DOMAIN:
            verified.append(a)
        elif await _check_dns_txt(domain, txt_val):
            verified.append(a)
        else:
            logger.warning("address %s failed TXT ownership check, not registering", a)
    if not verified:
        return
    http = await fclient.use_http()
    async with http as h:
        await h.execute(
            gql.gql("""mutation ResendRegister($persona_id: String!, $channel: String!, $addresses: [String!]!) {
                persona_set_external_addresses(persona_id: $persona_id, channel: $channel, addresses: $addresses)
            }"""),
            variable_values={
                "persona_id": rcx.persona.persona_id,
                "channel": "EMAIL",
                "addresses": [f"EMAIL:{a}" for a in verified],
            },
        )
    logger.info("registered email addresses %s for persona %s", verified, rcx.persona.persona_id)


class IntegrationResend:

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, domains: Dict[str, str], emails_to_register: set):
        self.fclient = fclient
        self.rcx = rcx
        self.domains = domains  # {"domain.com": "resend_domain_id"}
        self.emails_to_register = emails_to_register

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]):
        if not model_produced_args:
            return _help_text(bool(self.domains))

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if not op or "help" in op:
            return _help_text(bool(self.domains))
        if op == "send":
            return await self._send(args, model_produced_args)
        if op == "add_domain":
            return await self._add_domain(args, model_produced_args)
        if op == "verify_domain":
            return await self._verify_domain(args, model_produced_args)
        if op == "domain_status":
            return await self._domain_status(args, model_produced_args)
        if op == "list_domains":
            return await self._list_domains()

        return f"Unknown operation: {op}\n\nTry email(op='help') for usage."

    async def _send(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]):
        frm = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "from", None)
        to = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "to", None)
        if not frm or not to:
            return "Missing required: 'from' and 'to'"
        html = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "html", "")
        text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
        if not html and not text:
            return "Provide 'html' and/or 'text'"

        params: Dict[str, Any] = {
            "from": frm,
            "to": [e.strip() for e in to.split(",")],
            "subject": ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "subject", ""),
        }
        if html:
            params["html"] = html
        if text:
            params["text"] = text
        cc = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "cc", None)
        bcc = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "bcc", None)
        reply_to = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "reply_to", None)
        if cc:
            params["cc"] = [e.strip() for e in cc.split(",")]
        if bcc:
            params["bcc"] = [e.strip() for e in bcc.split(",")]
        if reply_to:
            params["reply_to"] = reply_to

        n_recipients = len(params["to"]) + len(params.get("cc", [])) + len(params.get("bcc", []))
        r = await _resend_request("POST", "/emails", params)
        if r.status_code == 200:
            rid = r.json().get("id", "")
            logger.info("sent email %s to %s", rid, to)
            return ckit_cloudtool.ToolResult(content=f"Email sent (id: {rid})", dollars=0.0009 * n_recipients)
        logger.error("resend send error: %s %s", r.status_code, r.text[:200])
        return "Internal error sending email, please try again later"

    async def _add_domain(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        if not (domain := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain", None)):
            return "Missing required: 'domain'"
        if len(self.domains) >= 20:
            return "Domain limit reached (20). Remove unused domains before adding new ones."

        region = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "region", "us-east-1")
        if region not in ("us-east-1", "eu-west-1", "sa-east-1", "ap-northeast-1"):
            return "Invalid region. Must be one of: us-east-1, eu-west-1, sa-east-1, ap-northeast-1."

        r = await _resend_request("POST", "/domains", {
            "name": domain,
            "region": region,
            "open_tracking": False,
            "click_tracking": True,
            "capabilities": {"sending": "enabled", "receiving": "enabled"},
        })
        if r.status_code == 200 or r.status_code == 201:
            d = r.json()
        elif "already" in r.text.lower():
            # Resend does not support find domain without listing all
            lr = await _resend_request("GET", "/domains")
            d = None
            if lr.status_code == 200:
                for item in lr.json().get("data", []):
                    if item["name"] == domain:
                        d = item
                        break
            if not d:
                return f"Domain {domain} already exists in Resend but could not retrieve it."
        else:
            logger.error("resend add domain error: %s %s", r.status_code, r.text[:200])
            return f"Failed to add domain: {r.text[:200]}"

        self.domains[domain] = d["id"]
        await self._save_domains()
        txt_val = f"flexus-verify={self.rcx.persona.ws_id}"
        logger.info("resend domain %s id=%s", domain, d["id"])
        return (
            f"Domain: {domain}\n"
            f"domain_id: {d['id']}\n"
            f"status: {d.get('status', 'pending')}\n\n"
            f"DNS records:\n{_format_dns_records(d.get('records'))}\n"
            f"  TXT {domain} -> {txt_val} (ownership verification)\n\n"
            f"After adding records, call verify_domain with domain_id=\"{d['id']}\".\n"
            f"DNS propagation can take minutes to hours."
        )

    async def _verify_domain(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        domain_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain_id", None)
        if not domain_id:
            return "Missing required: 'domain_id'"

        gr = await _resend_request("GET", f"/domains/{domain_id}")
        if gr.status_code != 200:
            logger.error("resend get domain error: %s %s", gr.status_code, gr.text[:200])
            return "Failed to get domain info"
        d = gr.json()
        txt_val = f"flexus-verify={self.rcx.persona.ws_id}"
        if not await _check_dns_txt(d["name"], txt_val):
            return f"TXT record '{txt_val}' not found for {d['name']}. DNS may still be propagating, try again later."
        await _resend_request("POST", f"/domains/{domain_id}/verify")
        msg = "Verification triggered. Check domain_status for results."
        if domain_id not in self.domains.values():
            self.domains[d["name"]] = domain_id
            await self._save_domains()
            msg += f"\nDomain {d['name']} added to setup."
        await register_email_addresses(self.fclient, self.rcx,
            [f"*@{dom}" for dom in self.domains] + list(self.emails_to_register))
        return msg

    async def _domain_status(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        domain_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain_id", None)
        if not domain_id:
            return "Missing required: 'domain_id'"

        r = await _resend_request("GET", f"/domains/{domain_id}")
        if r.status_code != 200:
            logger.error("resend domain status error: %s %s", r.status_code, r.text[:200])
            return "Failed to get domain status"
        d = r.json()
        txt_val = f"flexus-verify={self.rcx.persona.ws_id}"
        txt_ok = await _check_dns_txt(d["name"], txt_val)
        out = f"Domain: {d['name']}\n"
        if not txt_ok:
            out += f"ownership: NOT VERIFIED — add TXT record: {d['name']} -> {txt_val}, then call verify_domain. Domain cannot be used until verified.\n"
        else:
            out += "ownership: verified\n"
        out += f"resend status: {d['status']}\n\nDNS records:\n{_format_dns_records(d.get('records'))}"
        return out

    async def _list_domains(self) -> str:
        if not self.domains:
            return "No domains registered."
        lines = []
        for domain, domain_id in self.domains.items():
            r = await _resend_request("GET", f"/domains/{domain_id}")
            if r.status_code == 200:
                d = r.json()
                lines.append(f"  {d['name']} (id: {d['id']}) [{d['status']}]")
            else:
                lines.append(f"  {domain} (id: {domain_id}) [error fetching status]")
        return "Domains:\n" + "\n".join(lines)

    async def _save_domains(self):
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""mutation SaveResendDomains($persona_id: String!, $set_key: String!, $set_val: String) {
                    persona_setup_set_key(persona_id: $persona_id, set_key: $set_key, set_val: $set_val)
                }"""),
                variable_values={
                    "persona_id": self.rcx.persona.persona_id,
                    "set_key": "DOMAINS",
                    "set_val": json.dumps(self.domains),
                },
            )
