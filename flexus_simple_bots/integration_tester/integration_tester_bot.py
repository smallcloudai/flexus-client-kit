import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Callable, Awaitable

_repo_root = Path(__file__).parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_shutdown
from flexus_client_kit import ckit_bot_version
from flexus_client_kit import ckit_cloudtool, ckit_integrations_db

logger = logging.getLogger("integration_tester")

INTEGRATION_TESTER_ROOTDIR = Path(__file__).parent

PLAN_BATCHES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="integration_plan_batches",
    description="Plan integration tests one by one and return task specs for kanban fan-out.",
    parameters={
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "requested": {"type": "string", "description": "Requested integrations, e.g. 'all' or 'newsapi,resend'."},
            "configured_only": {"type": "boolean", "description": "If true, include only integrations with configured keys."},
        },
        "required": ["requested", "configured_only"],
    },
)

INTEGRATION_TESTER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    INTEGRATION_TESTER_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "gmail",
        "google_business",
        "google_ads",
        "google_sheets",
        "telegram",
        "slack",
        "notion",
        "airtable",
        "hubspot",
        "twilio",
        "skills",
    ],
    builtin_skills=[],
)

TOOLS = [PLAN_BATCHES_TOOL] + [t for rec in INTEGRATION_TESTER_INTEGRATIONS for t in rec.integr_tools]


def _requested_names(raw: str) -> List[str]:
    s = (raw or "").strip().lower()
    if not s or s == "all":
        return ["all"]
    names = []
    for x in s.replace(";", ",").split(","):
        x = x.strip()
        if x:
            names.append(x)
    return names or ["all"]


def _auth_provider_names(rec: ckit_integrations_db.IntegrationRecord) -> List[str]:
    names = []
    for x in [rec.integr_provider, rec.integr_name, f"{rec.integr_name}_manual"]:
        if x and x not in names:
            names.append(x)
    return names


def get_configured_integrations(external_auth: Dict[str, Any], integr_names: List[str]) -> List[Dict[str, Any]]:
    result = []
    for rec in INTEGRATION_TESTER_INTEGRATIONS:
        if rec.integr_name in integr_names:
            for provider_name in _auth_provider_names(rec):
                auth = external_auth.get(provider_name) or {}
                if any(v for k, v in auth.items() if k != "status"):
                    result.append({
                        "name": rec.integr_name,
                        "provider": provider_name,
                    })
                    break
    return result


def classify_error(e: Exception) -> tuple[str, str]:
    msg = str(e).lower()
    if any(k in msg for k in ("401", "403", "unauthorized", "invalid api", "forbidden", "invalid_api")):
        return "AUTH_ERROR", "API key invalid or unauthorized"
    if any(k in msg for k in ("timeout", "connection", "dns", "network", "connect", "refused")):
        return "NETWORK_ERROR", "Network/connectivity issue"
    if any(k in msg for k in ("rate", "429", "quota", "limit")):
        return "RATE_LIMIT", "API rate limit or quota exceeded"
    return "UNKNOWN_ERROR", str(e)[:200]


def _format_result(raw: str) -> str:
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            skip = {"ok", "provider", "description", "help_text"}
            parts = []
            for k, v in data.items():
                if k in skip:
                    continue
                if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
                    parts.append(f"{k}=[{", ".join(v)}]")
                elif not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            if parts:
                return ", ".join(parts)
    except json.JSONDecodeError:
        pass
    return raw


def make_testing_wrapper(
    original: Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[str]],
    integr_name: str,
    tool_name: str,
):
    async def wrapper(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        logger.info(f"Testing {tool_name}")
        try:
            result = await original(toolcall, model_produced_args)
            op = str(model_produced_args.get("op", "")).strip() if model_produced_args else ""
            if op == "help":
                result = "[HELP OUTPUT - NOT A TEST] " + result
            formatted = _format_result(result)
            out = f"result={formatted}"
            logger.info(f"{tool_name} test result: {out[:120]}..." if len(out) > 120 else f"{tool_name} test result: {out}")
            return out
        except Exception as e:
            category, detail = classify_error(e)
            logger.error(f"toolcall_{tool_name}: {category}: {detail}", exc_info=True)
            return f"Error [{category}]: {detail}"
    return wrapper


BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)
BOT_VERSION = (Path(__file__).parents[1] / "VERSION").read_text().strip()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())


async def integration_tester_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SETUP_SCHEMA, rcx.persona.persona_setup)

    integr_objects = await ckit_integrations_db.main_loop_integrations_init(INTEGRATION_TESTER_INTEGRATIONS, rcx, setup)
    supported_integrations = sorted({r.integr_name for r in INTEGRATION_TESTER_INTEGRATIONS})

    for rec in INTEGRATION_TESTER_INTEGRATIONS:
        for tool in rec.integr_tools:
            original_handler = rcx._handler_per_tool.get(tool.name)
            if original_handler:
                rcx.on_tool_call(tool.name)(
                    make_testing_wrapper(
                        original_handler,
                        rec.integr_name,
                        tool.name,
                    )
                )

    @rcx.on_tool_call(PLAN_BATCHES_TOOL.name)
    async def toolcall_plan_batches(toolcall, model_produced_args):
        args = model_produced_args or {}
        req = _requested_names(str(args.get("requested", "all")))
        configured_only = bool(args.get("configured_only", True))

        configured = {x["name"] for x in get_configured_integrations(rcx.external_auth, supported_integrations)}
        selected = []
        unsupported = []

        if "all" in req:
            pool = [x for x in supported_integrations if (x in configured or not configured_only)]
            selected = pool
        else:
            for x in req:
                if x not in supported_integrations:
                    unsupported.append(x)
                    continue
                if configured_only and x not in configured:
                    continue
                if x not in selected:
                    selected.append(x)

        tool_name_by_integr = {r.integr_name: r.integr_tools[0].name for r in INTEGRATION_TESTER_INTEGRATIONS if r.integr_tools}
        task_specs = []
        total = len(selected)
        for i, name in enumerate(selected, start=1):
            tool_name = tool_name_by_integr.get(name, name)
            task_specs.append({
                "title": f"Test {name} ({i}/{total})",
                "description": f"Integration: {name}\nTool: {tool_name}",
                "integrations": [name],
            })

        return json.dumps({
            "ok": True,
            "requested": req,
            "supported": supported_integrations,
            "configured": sorted(configured),
            "configured_only": configured_only,
            "selected": selected,
            "unsupported": unsupported,
            "task_specs": task_specs,
        }, indent=2)

    logger.info(f"Integration Tester started. Supported integrations: {supported_integrations}")

    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    logger.info(f"{rcx.persona.persona_id} exit")


def main():
    from flexus_simple_bots.integration_tester import integration_tester_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(
        ckit_client.bot_service_name(BOT_NAME, BOT_VERSION),
        endpoint="/v1/jailed-bot",
    )

    from dotenv import load_dotenv
    load_dotenv()

    async def _install_compat(client: ckit_client.FlexusClient) -> int:
        await integration_tester_install.install(
            client,
            bot_name=BOT_NAME,
            bot_version=BOT_VERSION,
            tools=TOOLS,
        )
        return 0

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=integration_tester_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=_install_compat,
    ))


if __name__ == "__main__":
    main()
