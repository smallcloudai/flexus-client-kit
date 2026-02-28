import asyncio
import datetime
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION
from flexus_simple_bots.owl3 import owl3_install

logger = logging.getLogger("bot_owl3")

BOT_DIR = Path(__file__).parent
BOT_NAME = "owl3"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
OWL3_INTEGRATIONS = ckit_integrations_db.integrations_load(["flexus_policy_document", "skills"], bot_dir=BOT_DIR)

PIPELINE = [
    "section01-calibration",
    "section02-diagnostic",
    "section03-metrics",
    "section04-segment",
    "section05-messaging",
    "section06-channels",
    "section07-tactics",
]

UPDATE_STRATEGY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="update_strategy_section",
    description="Update a section of the marketing strategy document. Sections must be filled in order: calibration -> diagnostic -> metrics -> segment -> messaging -> channels -> tactics.",
    parameters={
        "type": "object",
        "properties": {
            "idea_slug": {"type": "string", "description": "Idea slug from discovery path"},
            "hyp_slug": {"type": "string", "description": "Hypothesis slug from discovery path"},
            "section": {
                "type": "string",
                "enum": PIPELINE,
            },
            "data": {"type": "object", "description": "Section content, freeform"},
        },
    },
)

TOOLS = [
    UPDATE_STRATEGY_TOOL,
    *[t for rec in OWL3_INTEGRATIONS for t in rec.integr_tools],
]


def make_tool_response(path: str, step: str, score: int, filled: List[str], unfilled: List[str]) -> str:
    filled_str = ", ".join(filled) if filled else "none"
    unfilled_str = ", ".join(unfilled) if unfilled else "none"
    return f"""✍️ {path}

✓ Updated step: {step}

Score: {score}/100
Filled: {filled_str}
Unfilled: {unfilled_str}
"""


async def handle_update_strategy(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())

    idea_slug = args.get("idea_slug")
    hyp_slug = args.get("hyp_slug")
    section = args.get("section")
    data = args.get("data")
    if not idea_slug or not hyp_slug or not section or not data:
        return "Error: idea_slug, hyp_slug, section, and data are all required.\n\n"

    if section not in PIPELINE:
        return f"Error: unknown section {section!r}, must be one of: {', '.join(PIPELINE)}\n\n"

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/gtm/strategy/{idea_slug}--{hyp_slug}/strategy"

    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        doc = {
            "strategy": {
                "meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                "progress": {"score": 0, "step": "section01-calibration"},
            }
        }
    else:
        doc = existing.pdoc_content

    # Validate gating: previous section must be filled
    step_idx = PIPELINE.index(section)
    if step_idx > 0:
        prev = PIPELINE[step_idx - 1]
        if not doc["strategy"].get(prev):
            return f"Error: must complete {prev} before {section}"

    doc["strategy"][section] = data
    doc["strategy"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sections_filled = sum(1 for s in PIPELINE if doc["strategy"].get(s))
    score = min(100 * sections_filled // 7, 100)

    doc["strategy"]["progress"]["score"] = score
    doc["strategy"]["progress"]["step"] = PIPELINE[step_idx + 1] if step_idx + 1 < len(PIPELINE) else "complete"

    await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    filled = [s for s in PIPELINE if doc["strategy"].get(s)]
    unfilled = [s for s in PIPELINE if not doc["strategy"].get(s)]
    return make_tool_response(path, section, score, filled, unfilled)


async def owl3_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.integrations_init_all(OWL3_INTEGRATIONS, rcx)
    pdoc_integration = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(UPDATE_STRATEGY_TOOL.name)
    async def toolcall_update_strategy(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        return await handle_update_strategy(toolcall, args, rcx, pdoc_integration)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=owl3_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=owl3_install.install,
    ))


if __name__ == "__main__":
    main()
