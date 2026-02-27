import asyncio
import sys
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_kanban   # TODO add default reactions to messengers (post to inbox)
from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit import ckit_integrations_db
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots import prompts_common
import jsonschema

logger = logging.getLogger("no_special_code_bot")

MANIFEST_SCHEMA = json.loads((Path(__file__).parent / "manifest_schema.json").read_text())
SETUP_SCHEMA_SCHEMA = json.loads((Path(__file__).parent / "setup_schema_schema.json").read_text())


def _load_integrations(m):
    return ckit_integrations_db.load(m["integrations"])


def _load_pic_b64(bot_dir: Path, bot_name: str, size: str, ext: str):
    p = bot_dir / f"{bot_name}-{size}{ext}"
    return base64.b64encode(p.read_bytes()).decode("ascii") if p.exists() else None


def load_manifest(bot_dir: Path):
    m = json.loads((bot_dir / "manifest.json").read_text())
    jsonschema.validate(m, MANIFEST_SCHEMA)
    schema_path = bot_dir / "setup_schema.json"
    m["_dir"] = bot_dir
    setup_schema = json.loads(schema_path.read_text()) if schema_path.exists() else []
    jsonschema.validate(setup_schema, SETUP_SCHEMA_SCHEMA)
    m["_setup_schema"] = setup_schema
    return m


async def install_from_manifest(m, client, bot_name, bot_version, tools):
    d = m["_dir"]
    pic_big = _load_pic_b64(d, bot_name, "1024x1536", ".webp")
    pic_small = _load_pic_b64(d, bot_name, "256x256", ".webp") or _load_pic_b64(d, bot_name, "256x256", ".png")
    readme_path = d / "README.md"
    description = readme_path.read_text() if readme_path.exists() else m["title2"]
    experts = ckit_experts_from_files.discover_experts(d / "prompts")
    featured = [fa | {"feat_depends_on_setup": []} for fa in m["featured_actions"]]

    auth_supported = list(m.get("auth_supported", []))
    auth_scopes: dict = dict(m.get("auth_scopes", {}))
    for rec in _load_integrations(m).values():
        provider = rec.get("integr_provider")
        if provider:
            if provider not in auth_supported:
                auth_supported.append(provider)
            existing = auth_scopes.get(provider, [])
            merged = list(dict.fromkeys(existing + rec.get("integr_scopes", [])))
            auth_scopes[provider] = merged

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color=m["accent_color"],
        marketable_title1=m["title1"],
        marketable_title2=m["title2"],
        marketable_author=m["author"],
        marketable_occupation=m["occupation"],
        marketable_description=description,
        marketable_typical_group=m["typical_group"],
        marketable_github_repo=m["github_repo"],
        marketable_run_this="python -m flexus_client_kit.no_special_code_bot " + str(d),
        marketable_setup_default=m["_setup_schema"],
        marketable_featured_actions=featured,
        marketable_intro_message=m["intro_message"],
        marketable_preferred_model_default=m["preferred_model_default"],
        marketable_daily_budget_default=m["daily_budget_default"],
        marketable_default_inbox_default=m["default_inbox_default"],
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in experts],
        marketable_tags=m["tags"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_forms={},
        marketable_auth_supported=auth_supported,
        marketable_auth_scopes=auth_scopes,
    )


async def bot_main_loop(manifest, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    ckit_bot_exec.official_setup_mixing_procedure(manifest["_setup_schema"], rcx.persona.persona_setup)

    for name, rec in _load_integrations(manifest).items():
        obj = await rec["integr_init"](rcx)
        rec["integr_setup_handlers"](obj, rcx)

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
    m = load_manifest(bot_dir)
    bot_name = m["bot_name"]
    integrations = _load_integrations(m)
    all_tools = [t for rec in integrations.values() for t in rec["integr_tools"]]
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(bot_name, SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=bot_name,
        marketable_version_str=SIMPLE_BOTS_COMMON_VERSION,
        bot_main_loop=lambda fc, rcx: bot_main_loop(m, fc, rcx),
        inprocess_tools=all_tools,
        scenario_fn=scenario_fn,
        install_func=lambda client, bn, bv, t: install_from_manifest(m, client, bn, bv, t),
    ))


if __name__ == "__main__":
    main()
