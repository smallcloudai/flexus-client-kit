import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

import gql
import resend

from flexus_client_kit import ckit_bot_exec, ckit_bot_query, ckit_client, ckit_cloudtool

logger = logging.getLogger("resend")

RESEND_TESTING_DOMAIN = os.environ.get("RESEND_TESTING_DOMAIN", "")

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
    http = await fclient.use_http()
    async with http as h:
        await h.execute(
            gql.gql("""mutation ResendRegister($persona_id: String!, $channel: String!, $addresses: [String!]!) {
                persona_set_external_addresses(persona_id: $persona_id, channel: $channel, addresses: $addresses)
            }"""),
            variable_values={
                "persona_id": rcx.persona.persona_id,
                "channel": "EMAIL",
                "addresses": [f"EMAIL:{a}" for a in email_addresses],
            },
        )
    logger.info("registered email addresses %s for persona %s", email_addresses, rcx.persona.persona_id)


class IntegrationResend:

    def __init__(self, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext, domains: Dict[str, str]):
        self.fclient = fclient
        self.rcx = rcx
        self.domains = domains  # {"domain.com": "resend_domain_id"}

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return _help_text(bool(self.domains))

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if not op or "help" in op:
            return _help_text(bool(self.domains))
        if op == "send":
            return self._send(args, model_produced_args)
        if op == "add_domain":
            return await self._add_domain(args, model_produced_args)
        if op == "verify_domain":
            return await self._verify_domain(args, model_produced_args)
        if op == "domain_status":
            return self._domain_status(args, model_produced_args)
        if op == "list_domains":
            return self._list_domains()

        return f"Unknown operation: {op}\n\nTry email(op='help') for usage."

    def _send(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
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

        try:
            r = resend.Emails.send(params)
            logger.info("sent email %s to %s", r["id"], to)
            return f"Email sent (id: {r['id']})"
        except resend.exceptions.ResendError as e:
            logger.error("resend send error: %s", e)
            return "Internal error sending email, please try again later"

    async def _add_domain(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        if not (domain := ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain", None)):
            return "Missing required: 'domain'"
        if len(self.domains) >= 20:
            return "Domain limit reached (20). Remove unused domains before adding new ones."

        region = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "region", "us-east-1")
        if region not in ("us-east-1", "eu-west-1", "sa-east-1", "ap-northeast-1"):
            return "Invalid region. Must be one of: us-east-1, eu-west-1, sa-east-1, ap-northeast-1."

        try:
            r = resend.Domains.create({
                "name": domain,
                "region": region,
                "open_tracking": False,
                "click_tracking": True,
                "capabilities": {"sending": "enabled", "receiving": "enabled"},
            })
        except resend.exceptions.ResendError as e:
            if "already" not in str(e).lower():
                logger.error("resend add domain error: %s", e)
                return f"Failed to add domain: {e}"
            # Resend does not support find domain without listing all
            r = None
            try:
                for d in resend.Domains.list()["data"]:
                    if d["name"] == domain:
                        r = d
                        break
            except Exception as ex:
                logger.error("resend find domain error: %s", ex)
            if not r:
                return f"Domain {domain} already exists in Resend but could not retrieve it."
        self.domains[domain] = r["id"]
        await self._save_domains()
        logger.info("resend domain %s id=%s", domain, r["id"])
        return (
            f"Domain: {domain}\n"
            f"domain_id: {r['id']}\n"
            f"status: {r['status']}\n\n"
            f"DNS records:\n{_format_dns_records(r.get('records'))}\n\n"
            f"After adding records, call verify_domain with domain_id=\"{r['id']}\".\n"
            f"DNS propagation can take minutes to hours."
        )

    async def _verify_domain(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        domain_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain_id", None)
        if not domain_id:
            return "Missing required: 'domain_id'"

        try:
            resend.Domains.verify(domain_id=domain_id)
            msg = "Verification triggered. Check domain_status for results."
            if domain_id not in self.domains.values():
                r = resend.Domains.get(domain_id=domain_id)
                self.domains[r["name"]] = domain_id
                await self._save_domains()
                msg += f"\nDomain {r['name']} added to setup."
            return msg
        except resend.exceptions.ResendError as e:
            logger.error("resend verify error: %s", e)
            return "Failed to trigger verification"

    def _domain_status(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        domain_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "domain_id", None)
        if not domain_id:
            return "Missing required: 'domain_id'"

        try:
            r = resend.Domains.get(domain_id=domain_id)
            return f"Domain: {r['name']}\nstatus: {r['status']}\n\nDNS records:\n{_format_dns_records(r.get('records'))}"
        except resend.exceptions.ResendError as e:
            logger.error("resend domain status error: %s", e)
            return "Failed to get domain status"

    def _list_domains(self) -> str:
        if not self.domains:
            return "No domains registered."
        lines = []
        for domain, domain_id in self.domains.items():
            try:
                r = resend.Domains.get(domain_id=domain_id)
                lines.append(f"  {r['name']} (id: {r['id']}) [{r['status']}]")
            except resend.exceptions.ResendError:
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
