import asyncio
import json
import sys
from pathlib import Path

_repo_root = Path(__file__).parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from flexus_client_kit import ckit_bot_exec, ckit_client, ckit_shutdown, ckit_integrations_db
from flexus_client_kit import ckit_bot_version
from flexus_simple_bots.integration_tester import integration_tester_shared as shared
from flexus_simple_bots.integration_tester import integration_tester_install

BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)
BOT_VERSION = (Path(__file__).parents[1] / "VERSION").read_text().strip()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())


async def integration_tester_main_loop(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SETUP_SCHEMA, rcx.persona.persona_setup)
    shared.load_env_config(setup)

    integr_records = shared.INTEGRATION_TESTER_INTEGRATIONS
    setup_allow = shared._setup_allowlist_names(setup)
    if setup_allow:
        allow = set(setup_allow)
        integr_records = [r for r in integr_records if r.integr_name in allow]

    await ckit_integrations_db.main_loop_integrations_init(integr_records, rcx, setup)
    supported_integrations = sorted({r.integr_name for r in integr_records})

    for name, reg in shared.INTEGRATION_REGISTRY.items():
        obj = reg["integration_cls"](*reg["integration_args"](fclient, rcx, setup))
        rcx.on_tool_call(reg["tool"].name)(shared.IntegrationHandler(reg, obj))

    @rcx.on_tool_call(shared.PLAN_BATCHES_TOOL.name)
    async def toolcall_plan_batches(toolcall, model_produced_args):
        args = model_produced_args or {}
        req = shared._requested_names(str(args.get("requested", "all")))
        bs = args.get("batch_size", 5)
        configured_only = bool(args.get("configured_only", True))
        try:
            bs = int(bs)
        except (TypeError, ValueError):
            bs = 5

        configured = {x["name"] for x in shared.get_configured_integrations()}
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

        batches = shared._chunk_names(selected, bs)
        task_specs = []
        total = len(batches)
        for i, b in enumerate(batches, start=1):
            tool_map = ", ".join(f"{name}->{shared.INTEGRATION_REGISTRY[name]['tool'].name}" for name in b)
            task_specs.append({
                "title": f"Test integrations batch {i}/{total}",
                "description": f"Integrations: {','.join(b)}\nTool mapping: {tool_map}",
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

    configured = shared.get_configured_integrations()
    shared.logger.info(f"Integration Tester started. Configured integrations: {[i['name'] for i in configured]}")

    @rcx.on_updated_task
    async def on_task_update(action, old_task, new_task):
        task = new_task or old_task
        if not task:
            shared.logger.info(f"TASK UPDATE: {action} with no task payload")
            return
        col = task.calc_bucket()
        title = task.ktask_title
        tid = task.ktask_id
        if col == "inprogress":
            shared.logger.info(f"TASK ASSIGNED: {title} (id={tid}) - will test now")
        elif col == "done":
            shared.logger.info(f"TASK COMPLETED: {title} (id={tid})")
        else:
            shared.logger.info(f"TASK UPDATE: {title} moved to {col} (id={tid})")

    while not ckit_shutdown.shutdown_event.is_set():
        await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    shared.logger.info(f"{rcx.persona.persona_id} exit")


def main():
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
            tools=shared.TOOLS,
        )
        return 0

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=integration_tester_main_loop,
        inprocess_tools=shared.TOOLS,
        scenario_fn=scenario_fn,
        install_func=_install_compat,
    ))


if __name__ == "__main__":
    main()
