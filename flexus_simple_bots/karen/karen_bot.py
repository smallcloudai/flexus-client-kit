import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_repo_reader
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_mcp
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_karen")


BOT_NAME = "karen"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.static_skills_find(KAREN_ROOTDIR, shared_skills_allowlist="setting-up-external-knowledge-base")
KAREN_MCPS = []
KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += fi_discord2.DISCORD_SETUP_SCHEMA
KAREN_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(KAREN_MCPS))

KAREN_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    KAREN_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "slack",
        "telegram",
        "discord",
        "skills",
        "magic_desk",
    ],
    builtin_skills=KAREN_SKILLS,
)

SUPPORT_STATUS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="support_collection_status",
    description="Check how complete the support knowledge base is: /support/summary existence, drafts in /support/, answer fill percentage, translation status. No parameters needed.",
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)

TOOLS = [
    fi_repo_reader.REPO_READER_TOOL,
    SUPPORT_STATUS_TOOL,
    *[t for rec in KAREN_INTEGRATIONS for t in rec.integr_tools],
]


def _qa_fill_stats(doc: dict) -> dict:
    total_q = 0
    filled_q = 0
    total_a = 0
    filled_a = 0
    translated = True
    for k, v in doc.items():
        if k == "meta":
            continue
        if not isinstance(v, dict):
            continue
        for qk, qv in v.items():
            if not isinstance(qv, dict) or "q" not in qv or "a" not in qv:
                continue
            total_q += 1
            total_a += 1
            if qv["q"].strip():
                filled_q += 1
            else:
                translated = False
            if qv["a"].strip():
                filled_a += 1
    return {"total_q": total_q, "filled_q": filled_q, "total_a": total_a, "filled_a": filled_a, "translated": translated}


_DATE_PREFIX_RE = re.compile(r"^\d{8}-")


async def handle_support_status(pdoc: fi_pdoc.IntegrationPdoc, rcx: ckit_bot_exec.RobotContext, fcall_untrusted_key: str) -> str:
    persona_id = rcx.persona.persona_id
    lines = []

    # check /support/summary
    summary = await pdoc.pdoc_cat("/support/summary", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
    if summary:
        content = summary.pdoc_content
        top_tag = next((k for k in content if k != "meta"), None) if isinstance(content, dict) else None
        if top_tag and isinstance(content.get(top_tag), dict):
            stats = _qa_fill_stats(content[top_tag])
            pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
            lines.append(f"/support/summary exists — {stats['filled_a']}/{stats['total_a']} answers filled ({pct}%)")
            if not stats["translated"]:
                lines.append(f"   ⚠️ {stats['total_q'] - stats['filled_q']}/{stats['total_q']} questions not translated yet")
        else:
            lines.append("/support/summary exists (not QA format, can't measure fill percentage)")
    else:
        lines.append("/support/summary does not exist")
    lines.append("")

    # list drafts in /support/
    items = await pdoc.pdoc_list("/support/", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key, depth=1)
    drafts = [it for it in items if not it.is_folder and it.path != "/support/summary"]
    if drafts:
        lines.append(f"Drafts in /support/")
        for d in drafts:
            doc = await pdoc.pdoc_cat(d.path, persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
            if not doc:
                lines.append(f"    {d.path} —- could not read")
                continue
            content = doc.pdoc_content
            top_tag = next((k for k in content if k != "meta"), None) if isinstance(content, dict) else None
            if top_tag and isinstance(content.get(top_tag), dict):
                stats = _qa_fill_stats(content[top_tag])
                pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
                untranslated = stats['total_q'] - stats['filled_q']
                if not stats["translated"]:
                    t_status = f", {untranslated}/{stats['total_q']} questions need translation before user can answer."
                else:
                    t_status = ""
                lines.append(f"    {d.path} —- has {stats['filled_a']}/{stats['total_a']} answers {t_status}")
                name = d.path.rsplit("/", 1)[-1]
                if _DATE_PREFIX_RE.match(name) and pct >= 80:
                    lines.append(f"    💡 Looks ready, ask user if you should: flexus_policy_document(op=\"mv\", args={{\"p1\": \"{d.path}\", \"p2\": \"/support/summary\"}})")
            else:
                lines.append(f"    {d.path} —- not QA format")
    else:
        lines.append("No drafts in /support/.")

    return "\n".join(lines)

async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(KAREN_SETUP_SCHEMA, rcx.persona.persona_setup)
    integrations = await ckit_integrations_db.main_loop_integrations_init(KAREN_INTEGRATIONS, rcx, setup)
    pdoc_integration: fi_pdoc.IntegrationPdoc = integrations["flexus_policy_document"]

    # SAFETY
    # What we are trying to prevent: an outside user via slack/telegram/etc having access to any tools that leak information
    # about the company, or do any actions like sending A2A to Boss, that would be really silly.
    # How: expert 'very_limited' only has allowlist of tools, all messengers informed about the destination expert that they
    # are allowed to post the outside messages to.
    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("very_limited")

    @rcx.on_tool_call(fi_repo_reader.REPO_READER_TOOL.name)
    async def toolcall_repo_reader(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_repo_reader.handle_repo_reader(rcx, toolcall, model_produced_args)

    @rcx.on_tool_call(SUPPORT_STATUS_TOOL.name)
    async def toolcall_support_status(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_support_status(pdoc_integration, rcx, toolcall.fcall_untrusted_key)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await integrations["discord"].close()
        await integrations["telegram"].close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.karen import karen_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=karen_install.install,
    ))


if __name__ == "__main__":
    main()
