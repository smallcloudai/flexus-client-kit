import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

_repo_root = Path(__file__).parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_shutdown, ckit_cloudtool
from flexus_client_kit import ckit_bot_version
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_newsapi, fi_resend

logger = logging.getLogger("integration_tester")

BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)
BOT_VERSION = (Path(__file__).parents[1] / "VERSION").read_text().strip()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())

INTEGRATION_TESTER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    Path(__file__).parent,
    allowlist=["newsapi", "resend"],
    builtin_skills=[],
)

PLAN_BATCHES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="integration_plan_batches",
    description="Plan deterministic integration test batches and return task specs for kanban fan-out.",
    parameters={
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "requested": {"type": "string", "description": "Requested integrations, e.g. 'all' or 'newsapi,resend'."},
            "batch_size": {"type": "integer", "description": "Max integrations per task batch."},
            "configured_only": {"type": "boolean", "description": "If true, include only integrations with configured keys."},
        },
        "required": ["requested", "batch_size", "configured_only"],
    },
)

NEWSAPI_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name=fi_newsapi.PROVIDER_NAME,
    description=f"{fi_newsapi.PROVIDER_NAME}: data provider. op=help|status|list_methods|call",
    parameters={
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "op": {"type": "string", "enum": ["help", "status", "list_methods", "call"]},
            "args": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "method_id": {"type": "string"},
                    "include_raw": {"type": "boolean"},
                    "q": {"type": "string"},
                    "query": {"type": "string"},
                    "sources": {"type": "string"},
                    "domains": {"type": "string"},
                    "excludeDomains": {"type": "string"},
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "language": {"type": "string"},
                    "sortBy": {"type": "string"},
                    "pageSize": {"type": "integer"},
                    "page": {"type": "integer"},
                    "country": {"type": "string"},
                    "category": {"type": "string"},
                    "time_window": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                }
            },
        },
        "required": ["op", "args"],
    },
)


INTEGRATION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "newsapi": {
        "env_var": "NEWSAPI_API_KEY",
        "alt_env_vars": ["NEWSAPI_KEY"],
        "tool": NEWSAPI_TOOL,
        "integration_cls": fi_newsapi.IntegrationNewsapi,
        "integration_args": lambda fclient, rcx, setup: (rcx,),
        "handler_method": "called_by_model",
        "test_prompt_op": "call",
        "test_prompt_args": {"method_id": "newsapi.sources.v1"},
    },
    "resend": {
        "env_var": "RESEND_API_KEY",
        "tool": fi_resend.RESEND_SETUP_TOOL,
        "integration_cls": fi_resend.IntegrationResend,
        "integration_args": lambda fclient, rcx, setup: (fclient, rcx, {}),
        "handler_method": "setup_called_by_model",
        "test_prompt_op": "list",
        "test_prompt_args": {},
    },
}

TOOLS = [PLAN_BATCHES_TOOL] + [reg["tool"] for reg in INTEGRATION_REGISTRY.values()]


def _chunk_names(xs: List[str], n: int) -> List[List[str]]:
    if n < 1:
        n = 1
    return [xs[i:i + n] for i in range(0, len(xs), n)]


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


def _setup_allowlist_names(setup: Dict[str, Any]) -> List[str]:
    raw = str(setup.get("INTEGRATION_TESTER_ALLOWLIST", "") or "").strip().lower()
    if not raw:
        return []
    names: List[str] = []
    for x in raw.replace(";", ",").split(","):
        x = x.strip()
        if x:
            names.append(x)
    return names


def load_env_config(setup: Dict[str, Any]) -> None:
    env_config = setup.get("ENV_CONFIG", "")
    if not env_config:
        logger.info("No ENV_CONFIG found in persona_setup")
        return
    count = 0
    for line in env_config.strip().split('\n'):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()
            count += 1
    logger.info(f"Loaded {count} environment variables from ENV_CONFIG")


def get_configured_integrations() -> List[Dict[str, Any]]:
    result = []
    for name, reg in INTEGRATION_REGISTRY.items():
        key = os.environ.get(reg["env_var"])
        if not key and "alt_env_vars" in reg:
            for alt in reg["alt_env_vars"]:
                key = os.environ.get(alt)
                if key:
                    break
        if key:
            result.append({
                "name": name,
                "env_var": reg["env_var"],
                "key_hint": key[-4:] if len(key) > 4 else "***",
            })
    return result


async def integration_tester_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SETUP_SCHEMA, rcx.persona.persona_setup)
    load_env_config(setup)

    integr_records = INTEGRATION_TESTER_INTEGRATIONS
    setup_allow = _setup_allowlist_names(setup)
    if setup_allow:
        allow = set(setup_allow)
        integr_records = [r for r in integr_records if r.integr_name in allow]

    await ckit_integrations_db.main_loop_integrations_init(integr_records, rcx, setup)
    supported_integrations = sorted({r.integr_name for r in integr_records})

    for name, reg in INTEGRATION_REGISTRY.items():
        integration_obj = reg["integration_cls"](*reg["integration_args"](fclient, rcx, setup))

        def make_handler(reg, obj):
            env_var = reg["env_var"]
            alt_env_vars = reg.get("alt_env_vars", [])
            handler_method = reg["handler_method"]
            tool_name = reg["tool"].name

            async def handler(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
                keys = [os.environ.get(env_var)] + [os.environ.get(v) for v in alt_env_vars]
                key = next((k for k in keys if k), None)
                logger.info(f"Testing {tool_name} - API key present: {bool(key)}")
                if not key:
                    logger.warning(f"{tool_name} test FAILED - no API key configured")
                    return f"Error: {env_var} not configured. Resolve the kanban task as FAILED with status: 'FAILED - No API key configured for {tool_name}'"
                try:
                    result = await getattr(obj, handler_method)(toolcall, model_produced_args)
                    logger.info(f"{tool_name} test result: {result[:100]}..." if len(result) > 100 else f"{tool_name} test result: {result}")
                    return result
                except Exception as e:
                    logger.error(f"toolcall_{tool_name}: %s" % str(e), exc_info=True)
                    return "Error: %s" % str(e)
            return handler

        rcx.on_tool_call(reg["tool"].name)(make_handler(reg, integration_obj))

    @rcx.on_tool_call(PLAN_BATCHES_TOOL.name)
    async def toolcall_plan_batches(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        args = model_produced_args or {}
        req = _requested_names(str(args.get("requested", "all")))
        bs = args.get("batch_size", 5)
        configured_only = bool(args.get("configured_only", True))
        try:
            bs = int(bs)
        except (TypeError, ValueError):
            bs = 5

        configured = {x["name"] for x in get_configured_integrations()}
        selected: List[str] = []
        unsupported: List[str] = []

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

        batches = _chunk_names(selected, bs)
        task_specs = []
        total = len(batches)
        for i, b in enumerate(batches, start=1):
            task_specs.append({
                "title": f"Test integrations batch {i}/{total}",
                "description": f"Integrations: {','.join(b)}",
                "integrations": b,
            })

        return json.dumps({
            "ok": True,
            "requested": req,
            "supported": supported_integrations,
            "configured": sorted(configured),
            "configured_only": configured_only,
            "selected": selected,
            "unsupported": unsupported,
            "batch_size": bs,
            "batches": batches,
            "task_specs": task_specs,
        }, indent=2)

    configured = get_configured_integrations()
    logger.info(f"Integration Tester started. Configured integrations: {[i['name'] for i in configured]}")

    @rcx.on_updated_task
    async def on_task_update(action: str, old_task, new_task):
        task = new_task or old_task
        if not task:
            logger.info(f"TASK UPDATE: {action} with no task payload")
            return
        col = task.calc_bucket()
        title = task.ktask_title
        tid = task.ktask_id
        if col == "inprogress":
            logger.info(f"TASK ASSIGNED: {title} (id={tid}) - will test now")
        elif col == "done":
            logger.info(f"TASK COMPLETED: {title} (id={tid})")
        else:
            logger.info(f"TASK UPDATE: {title} moved to {col} (id={tid})")

    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    logger.info(f"{rcx.persona.persona_id} exit")


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(
        ckit_client.bot_service_name(BOT_NAME, BOT_VERSION),
        endpoint="/v1/jailed-bot",
    )

    from dotenv import load_dotenv
    load_dotenv()

    from flexus_simple_bots.integration_tester import integration_tester_install

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
