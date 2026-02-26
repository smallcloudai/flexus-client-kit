import asyncio
import sys
import json
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Callable, Awaitable

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_kanban   # TODO add default reactions to messengers (post to inbox)
from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_widget
from flexus_client_kit.integrations.integration_registry import INTEGRATION_REGISTRY
import flexus_client_kit.integrations.fi_google_calendar  # registers on import
import flexus_client_kit.integrations.fi_gmail  # registers on import
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots import prompts_common
import jsonschema

logger = logging.getLogger("no_special_code_bot")

MANIFEST_SCHEMA = json.loads((Path(__file__).parent / "manifest_schema.json").read_text())
SETUP_SCHEMA_SCHEMA = json.loads((Path(__file__).parent / "setup_schema_schema.json").read_text())


ToolCalledByModel = Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[str]]


def _setup_pdoc(rcx: ckit_bot_exec.RobotContext) -> ToolCalledByModel:
    integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    return integration.called_by_model


def _setup_widget(rcx: ckit_bot_exec.RobotContext) -> ToolCalledByModel:
    return fi_widget.handle_print_widget


TOOL_REGISTRY: dict[str, tuple[ckit_cloudtool.CloudTool, Callable]] = {
    "flexus_policy_document": (fi_pdoc.POLICY_DOCUMENT_TOOL, _setup_pdoc),
    "print_widget": (fi_widget.PRINT_WIDGET_TOOL, _setup_widget),
}


def tool_registry_lookup(tool_names: list[str]) -> list[ckit_cloudtool.CloudTool]:
    tools = []
    for name in tool_names:
        if name not in TOOL_REGISTRY:
            raise ValueError(f"Unknown tool {name!r}, available: {list(TOOL_REGISTRY.keys())}")
        tools.append(TOOL_REGISTRY[name][0])
    return tools


def collect_integration_tools(m) -> list[ckit_cloudtool.CloudTool]:
    integration_tools = []
    for int_name in m.get("integrations", []):
        if int_name not in INTEGRATION_REGISTRY:
            raise ValueError(f"Unknown integration {int_name!r}, available: {list(INTEGRATION_REGISTRY.keys())}")
        integration_tools.extend(INTEGRATION_REGISTRY[int_name].tools)
    return integration_tools


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

    # Resolve integrations → collect their tools and merge auth params
    integration_tools = []
    auth_supported = list(m.get("auth_supported", []))
    auth_scopes: dict = dict(m.get("auth_scopes", {}))
    for int_name in m.get("integrations", []):
        if int_name not in INTEGRATION_REGISTRY:
            raise ValueError(f"Unknown integration {int_name!r}, available: {list(INTEGRATION_REGISTRY.keys())}")
        intg = INTEGRATION_REGISTRY[int_name]
        integration_tools.extend(intg.tools)
        if intg.auth_type == "oauth" and intg.provider:
            if intg.provider not in auth_supported:
                auth_supported.append(intg.provider)
            existing = auth_scopes.get(intg.provider, [])
            merged = list(dict.fromkeys(existing + intg.scopes))  # dedupe, preserve order
            auth_scopes[intg.provider] = merged

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
        marketable_experts=[(name, exp.provide_tools(tools + integration_tools)) for name, exp in experts],
        marketable_tags=m["tags"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_forms={},
        marketable_auth_supported=auth_supported,
        marketable_auth_scopes=auth_scopes,
    )


async def bot_main_loop(m, fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    ckit_bot_exec.official_setup_mixing_procedure(m["_setup_schema"], rcx.persona.persona_setup)

    # Register handlers for manifest "tools" (existing TOOL_REGISTRY)
    for name in m["tools"]:
        tool, setup_fn = TOOL_REGISTRY[name]
        handler = setup_fn(rcx)
        rcx.on_tool_call(tool.name)(handler)

    # Register handlers for "integrations" tools.
    # Handlers are created with access to rcx so they can read live external_auth.
    # When user connects/disconnects a provider, rcx._soft_restart_requested=True causes
    # bot_main_loop to exit and re-enter, picking up the updated rcx.external_auth.
    for int_name in m.get("integrations", []):
        intg = INTEGRATION_REGISTRY[int_name]
        for tool in intg.tools:
            if tool.name in intg.tool_handler_factories:
                handler = intg.tool_handler_factories[tool.name](rcx)
                rcx.on_tool_call(tool.name)(handler)

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
    tools = tool_registry_lookup(m["tools"])
    integration_tools = collect_integration_tools(m)
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(bot_name, SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=bot_name,
        marketable_version_str=SIMPLE_BOTS_COMMON_VERSION,
        bot_main_loop=lambda fc, rcx: bot_main_loop(m, fc, rcx),
        inprocess_tools=tools + integration_tools,
        scenario_fn=scenario_fn,
        install_func=lambda client, bn, bv, t: install_from_manifest(m, client, bn, bv, t),
    ))


if __name__ == "__main__":
    main()
