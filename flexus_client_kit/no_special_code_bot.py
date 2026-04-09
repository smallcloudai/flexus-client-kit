import asyncio
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_kanban   # TODO add default reactions to messengers (post to inbox)
from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import ckit_bot_version
from flexus_simple_bots import prompts_common
import jsonschema

logger = logging.getLogger("no_special_code_bot")

MANIFEST_SCHEMA = json.loads((Path(__file__).parent / "manifest_schema.json").read_text())
SETUP_SCHEMA_SCHEMA = json.loads((Path(__file__).parent / "setup_schema_schema.json").read_text())


def load_manifest_and_setup_schema(bot_dir: Path) -> tuple[dict, list]:
    m = json.loads((bot_dir / "manifest.json").read_text())
    jsonschema.validate(m, MANIFEST_SCHEMA)
    schema_path = bot_dir / "setup_schema.json"
    setup_schema = json.loads(schema_path.read_text()) if schema_path.exists() else []
    jsonschema.validate(setup_schema, SETUP_SCHEMA_SCHEMA)
    return m, setup_schema


async def install_from_manifest(m, setup_schema, bot_dir, tools, client):
    bot_name = bot_dir.name
    readme_path = bot_dir / "README.md"
    description = readme_path.read_text() if readme_path.exists() else m["title2"]
    skills = ckit_skills.static_skills_find(bot_dir, m.get("shared_skills_allowlist", ""), m.get("integration_skills_allowlist", ""))
    experts = ckit_experts_from_files.discover_experts(bot_dir, skills)
    featured = m["featured_actions"]

    auth_supported = list(m.get("auth_supported", []))
    auth_scopes: dict = dict(m.get("auth_scopes", {}))
    integrations_records = ckit_integrations_db.static_integrations_load(bot_dir, m["integrations"], builtin_skills=skills)
    for rec in integrations_records:
        if rec.integr_provider:
            if rec.integr_provider not in auth_supported:
                auth_supported.append(rec.integr_provider)
            existing = auth_scopes.get(rec.integr_provider, [])
            auth_scopes[rec.integr_provider] = list(dict.fromkeys(existing + rec.integr_scopes))

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=bot_dir,
        marketable_accent_color=m["accent_color"],
        marketable_title1=m["title1"],
        marketable_title2=m["title2"],
        marketable_author=m["author"],
        marketable_occupation=m["occupation"],
        marketable_description=description,
        marketable_typical_group=m["typical_group"],
        marketable_github_repo=m["github_repo"],
        marketable_run_this="python -m flexus_client_kit.no_special_code_bot " + str(bot_dir),
        marketable_setup_default=setup_schema,
        marketable_featured_actions=featured,
        marketable_intro_message=m["intro_message"],
        marketable_preferred_model_expensive=m["preferred_model_expensive"],
        marketable_preferred_model_cheap=m["preferred_model_cheap"],
        marketable_daily_budget_default=m["daily_budget_default"],
        marketable_default_inbox_default=m["default_inbox_default"],
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in experts],
        add_integrations_into_expert_system_prompt=integrations_records,
        marketable_tags=m["tags"],
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_forms={},
        marketable_auth_supported=auth_supported,
        marketable_auth_scopes=auth_scopes,
    )


async def bot_main_loop(m, setup_schema, bot_dir, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(setup_schema, rcx.persona.persona_setup)
    skills = ckit_skills.static_skills_find(bot_dir, m.get("shared_skills_allowlist", ""), m.get("integration_skills_allowlist", ""))
    await ckit_integrations_db.main_loop_integrations_init(ckit_integrations_db.static_integrations_load(bot_dir, m["integrations"], builtin_skills=skills), rcx, setup)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def _resolve_bot_dir(raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    # relative path -- try CWD first, then walk up to repo root (.git) and resolve there
    if (Path.cwd() / p / "manifest.json").exists():
        return (Path.cwd() / p).resolve()
    d = Path.cwd()
    while d != d.parent:
        if (d / ".git").exists():
            candidate = d / p
            if (candidate / "manifest.json").exists():
                return candidate.resolve()
            break
        d = d.parent
    print(f"Cannot find {raw}/manifest.json from CWD or repo root")
    sys.exit(1)


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("Usage: python -m flexus_client_kit.no_special_code_bot <bot_dir>")
        print("  bot_dir can be absolute or relative to CWD or repo root, must contain manifest.json")
        sys.exit(1)
    bot_dir = _resolve_bot_dir(sys.argv.pop(1))
    manifest, setup_schema = load_manifest_and_setup_schema(bot_dir)
    bot_name = bot_dir.name
    skills = ckit_skills.static_skills_find(bot_dir, manifest.get("shared_skills_allowlist", ""), manifest.get("integration_skills_allowlist", ""))
    integrations = ckit_integrations_db.static_integrations_load(bot_dir, manifest["integrations"], builtin_skills=skills)
    all_tools = [t for rec in integrations for t in rec.integr_tools]   # double loop collapses list of lists into one list
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(str(bot_dir / "x"))
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(bot_name, bot_version), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=lambda fc, rcx: bot_main_loop(manifest, setup_schema, bot_dir, fc, rcx),
        inprocess_tools=all_tools,
        scenario_fn=scenario_fn,
        install_func=lambda client: install_from_manifest(manifest, setup_schema, bot_dir, all_tools, client),
    ))


if __name__ == "__main__":
    main()
