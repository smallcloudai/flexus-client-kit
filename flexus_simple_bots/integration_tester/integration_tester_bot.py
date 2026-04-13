import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_shutdown, ckit_cloudtool
from flexus_client_kit import ckit_bot_version
from flexus_client_kit.integrations import fi_newsapi, fi_resend

logger = logging.getLogger("integration_tester")

BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)
BOT_VERSION = (Path(__file__).parents[1] / "VERSION").read_text().strip()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())
SUPPORTED_INTEGRATIONS = ["newsapi", "resend"]

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


TOOLS = [
    PLAN_BATCHES_TOOL,
    NEWSAPI_TOOL,
    fi_resend.RESEND_SETUP_TOOL,
]


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
    
    newsapi_key = os.environ.get("NEWSAPI_API_KEY") or os.environ.get("NEWSAPI_KEY")
    if newsapi_key:
        result.append({
            "name": "newsapi",
            "env_var": "NEWSAPI_API_KEY",
            "key_hint": newsapi_key[-4:] if len(newsapi_key) > 4 else "***",
        })
    
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        result.append({
            "name": "resend",
            "env_var": "RESEND_API_KEY",
            "key_hint": resend_key[-4:] if len(resend_key) > 4 else "***",
        })
    
    return result


async def integration_tester_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SETUP_SCHEMA, rcx.persona.persona_setup)
    load_env_config(setup)

    newsapi = fi_newsapi.IntegrationNewsapi(rcx)
    domains = setup.get("DOMAINS", {}) if isinstance(setup, dict) else {}
    resend = fi_resend.IntegrationResend(fclient, rcx, domains)

    @rcx.on_tool_call(NEWSAPI_TOOL.name)
    async def toolcall_newsapi(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        newsapi_key = os.environ.get("NEWSAPI_API_KEY") or os.environ.get("NEWSAPI_KEY")
        logger.info(f"Testing newsapi - API key present: {bool(newsapi_key)}")
        if not newsapi_key:
            logger.warning("newsapi test FAILED - no API key configured")
            return "Error: NEWSAPI_API_KEY not configured. Resolve the kanban task as FAILED with status: 'FAILED - No API key configured for newsapi'"
        try:
            result = await newsapi.called_by_model(toolcall, model_produced_args)
            logger.info(f"newsapi test result: {result[:100]}..." if len(result) > 100 else f"newsapi test result: {result}")
            return result
        except Exception as e:
            logger.error("toolcall_newsapi: %s" % str(e), exc_info=True)
            return "Error: %s" % str(e)

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
            pool = [x for x in SUPPORTED_INTEGRATIONS if (x in configured or not configured_only)]
            selected = pool
        else:
            for x in req:
                if x not in SUPPORTED_INTEGRATIONS:
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
            "supported": SUPPORTED_INTEGRATIONS,
            "configured": sorted(configured),
            "configured_only": configured_only,
            "selected": selected,
            "unsupported": unsupported,
            "batch_size": bs,
            "batches": batches,
            "task_specs": task_specs,
        }, indent=2)

    @rcx.on_tool_call(fi_resend.RESEND_SETUP_TOOL.name)
    async def toolcall_email_setup_domain(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        resend_key = os.environ.get("RESEND_API_KEY")
        logger.info(f"Testing resend - API key present: {bool(resend_key)}")
        if not resend_key:
            logger.warning("resend test FAILED - no API key configured")
            return "Error: RESEND_API_KEY not configured. Resolve the kanban task as FAILED with status: 'FAILED - No API key configured for resend'"
        try:
            result = await resend.setup_called_by_model(toolcall, model_produced_args)
            logger.info(f"resend test result: {result[:100]}..." if len(result) > 100 else f"resend test result: {result}")
            return result
        except Exception as e:
            logger.error("toolcall_email_setup_domain: %s" % str(e), exc_info=True)
            return "Error: %s" % str(e)

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
