import asyncio
import datetime
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_shutdown
from flexus_simple_bots.strategist import experiment_design_tools
from flexus_simple_bots.strategist import gtm_economics_rtm_tools
from flexus_simple_bots.strategist import mvp_validation_tools
from flexus_simple_bots.strategist import positioning_offer_tools
from flexus_simple_bots.strategist import pricing_validation_tools
from flexus_simple_bots.strategist import strategist_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_strategist")

BOT_DIR = Path(__file__).parent
BOT_NAME = "strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


def load_strategy_skill_schemas() -> Dict[str, Any]:
    skills_dir = BOT_DIR / "skills"
    schema = {}
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.name.startswith("filling-"):
            continue
        md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        m = re.search(r"```json\s*(\{.*?\})\s*```", md, re.DOTALL)
        if not m:
            continue
        section = skill_dir.name.replace("filling-", "")
        parsed = json.loads(m.group(1))
        parsed["title"] = section.split("-", 1)[1].capitalize()
        schema[section] = parsed
    return schema


STRATEGY_SKILL_SCHEMAS = load_strategy_skill_schemas()

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
            "idea_slug": {
                "type": "string",
                "description": "Idea slug from discovery path",
            },
            "hyp_slug": {
                "type": "string",
                "description": "Hypothesis slug from discovery path",
            },
            "section": {
                "type": "string",
                "enum": PIPELINE,
            },
            "data": {
                "type": "object",
                "description": "Section content, freeform",
            },
        },
    },
)


def make_tool_response(path: str, step: str, score: int, filled: List[str], unfilled: List[str]) -> str:
    filled_str = ", ".join(filled) if filled else "none"
    unfilled_str = ", ".join(unfilled) if unfilled else "none"
    return f"""✍️ {path}

✓ Updated step: {step}

Score: {score}/100
Filled: {filled_str}
Unfilled: {unfilled_str}
"""


async def handle_update_strategy(toolcall, args: Dict[str, Any], rcx, pdoc_integration) -> str:
    idea_slug = args.get("idea_slug")
    hyp_slug = args.get("hyp_slug")
    section = args.get("section")
    data = args.get("data")
    if not idea_slug or not hyp_slug or not section or not data:
        return "Error: idea_slug, hyp_slug, section, and data are all required."

    if section not in PIPELINE:
        return f"Error: unknown section {section!r}, must be one of: {', '.join(PIPELINE)}"

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/gtm/strategy/{idea_slug}--{hyp_slug}/strategy"

    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        doc = {
            "strategy": {
                "meta": {
                    "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                },
                "progress": {
                    "score": 0,
                    "step": "section01-calibration",
                },
            },
        }
    else:
        doc = existing.pdoc_content

    step_idx = PIPELINE.index(section)
    if step_idx > 0:
        prev = PIPELINE[step_idx - 1]
        if not doc["strategy"].get(prev):
            return f"Error: must complete {prev} before {section}"

    doc["strategy"]["schema"] = STRATEGY_SKILL_SCHEMAS
    doc["strategy"][section] = data
    doc["strategy"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    sections_filled = sum(1 for s in PIPELINE if doc["strategy"].get(s))
    score = min(100 * sections_filled // len(PIPELINE), 100)

    doc["strategy"]["progress"]["score"] = score
    if step_idx + 1 < len(PIPELINE):
        doc["strategy"]["progress"]["step"] = PIPELINE[step_idx + 1]
    else:
        doc["strategy"]["progress"]["step"] = "complete"

    await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    filled = [s for s in PIPELINE if doc["strategy"].get(s)]
    unfilled = [s for s in PIPELINE if not doc["strategy"].get(s)]
    return make_tool_response(path, section, score, filled, unfilled)


STRATEGIST_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    strategist_install.STRATEGIST_ROOTDIR,
    [
        "flexus_policy_document", "skills", "print_widget",
        "chargebee", "crunchbase", "datadog", "ga4", "gnews", "google_ads",
        "launchdarkly", "linkedin", "meta", "mixpanel", "optimizely", "paddle",
        "pipedrive", "qualtrics", "recurly", "salesforce", "segment", "statsig",
        "surveymonkey", "typeform", "zendesk",
    ],
    builtin_skills=strategist_install.STRATEGIST_SKILLS,
)

TOOLS = [
    UPDATE_STRATEGY_TOOL,
    *experiment_design_tools.WRITE_TOOLS,
    *mvp_validation_tools.WRITE_TOOLS,
    *positioning_offer_tools.WRITE_TOOLS,
    *pricing_validation_tools.WRITE_TOOLS,
    *gtm_economics_rtm_tools.WRITE_TOOLS,
    *[t for rec in STRATEGIST_INTEGRATIONS for t in rec.integr_tools],
]


async def strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(strategist_install.STRATEGIST_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(STRATEGIST_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(UPDATE_STRATEGY_TOOL.name)
    async def _h_update_strategy(toolcall, args):
        return await handle_update_strategy(toolcall, args, rcx, pdoc_integration)

    for tool, fn in [
        (experiment_design_tools.WRITE_EXPERIMENT_CARD_DRAFT_TOOL, experiment_design_tools.handle_write_experiment_card_draft),
        (experiment_design_tools.WRITE_EXPERIMENT_MEASUREMENT_SPEC_TOOL, experiment_design_tools.handle_write_experiment_measurement_spec),
        (experiment_design_tools.WRITE_EXPERIMENT_BACKLOG_PRIORITIZATION_TOOL, experiment_design_tools.handle_write_experiment_backlog_prioritization),
        (experiment_design_tools.WRITE_EXPERIMENT_RELIABILITY_REPORT_TOOL, experiment_design_tools.handle_write_experiment_reliability_report),
        (experiment_design_tools.WRITE_EXPERIMENT_APPROVAL_TOOL, experiment_design_tools.handle_write_experiment_approval),
        (experiment_design_tools.WRITE_EXPERIMENT_STOP_RULE_EVALUATION_TOOL, experiment_design_tools.handle_write_experiment_stop_rule_evaluation),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool, fn in [
        (mvp_validation_tools.WRITE_MVP_RUN_LOG_TOOL, mvp_validation_tools.handle_write_mvp_run_log),
        (mvp_validation_tools.WRITE_MVP_ROLLOUT_INCIDENT_TOOL, mvp_validation_tools.handle_write_mvp_rollout_incident),
        (mvp_validation_tools.WRITE_MVP_FEEDBACK_DIGEST_TOOL, mvp_validation_tools.handle_write_mvp_feedback_digest),
        (mvp_validation_tools.WRITE_TELEMETRY_QUALITY_REPORT_TOOL, mvp_validation_tools.handle_write_telemetry_quality_report),
        (mvp_validation_tools.WRITE_TELEMETRY_DECISION_MEMO_TOOL, mvp_validation_tools.handle_write_telemetry_decision_memo),
        (mvp_validation_tools.WRITE_MVP_SCALE_READINESS_GATE_TOOL, mvp_validation_tools.handle_write_mvp_scale_readiness_gate),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool, fn in [
        (positioning_offer_tools.WRITE_VALUE_PROPOSITION_TOOL, positioning_offer_tools.handle_write_value_proposition),
        (positioning_offer_tools.WRITE_OFFER_PACKAGING_TOOL, positioning_offer_tools.handle_write_offer_packaging),
        (positioning_offer_tools.WRITE_POSITIONING_NARRATIVE_BRIEF_TOOL, positioning_offer_tools.handle_write_positioning_narrative_brief),
        (positioning_offer_tools.WRITE_MESSAGING_EXPERIMENT_PLAN_TOOL, positioning_offer_tools.handle_write_messaging_experiment_plan),
        (positioning_offer_tools.WRITE_POSITIONING_TEST_RESULT_TOOL, positioning_offer_tools.handle_write_positioning_test_result),
        (positioning_offer_tools.WRITE_POSITIONING_CLAIM_RISK_REGISTER_TOOL, positioning_offer_tools.handle_write_positioning_claim_risk_register),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool, fn in [
        (pricing_validation_tools.WRITE_PRICE_CORRIDOR_TOOL, pricing_validation_tools.handle_write_price_corridor),
        (pricing_validation_tools.WRITE_PRICE_SENSITIVITY_CURVE_TOOL, pricing_validation_tools.handle_write_price_sensitivity_curve),
        (pricing_validation_tools.WRITE_PRICING_ASSUMPTION_REGISTER_TOOL, pricing_validation_tools.handle_write_pricing_assumption_register),
        (pricing_validation_tools.WRITE_PRICING_COMMITMENT_EVIDENCE_TOOL, pricing_validation_tools.handle_write_pricing_commitment_evidence),
        (pricing_validation_tools.WRITE_VALIDATED_PRICE_HYPOTHESIS_TOOL, pricing_validation_tools.handle_write_validated_price_hypothesis),
        (pricing_validation_tools.WRITE_PRICING_GO_NO_GO_GATE_TOOL, pricing_validation_tools.handle_write_pricing_go_no_go_gate),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool, fn in [
        (gtm_economics_rtm_tools.WRITE_UNIT_ECONOMICS_REVIEW_TOOL, gtm_economics_rtm_tools.handle_write_unit_economics_review),
        (gtm_economics_rtm_tools.WRITE_CHANNEL_MARGIN_STACK_TOOL, gtm_economics_rtm_tools.handle_write_channel_margin_stack),
        (gtm_economics_rtm_tools.WRITE_PAYBACK_READINESS_GATE_TOOL, gtm_economics_rtm_tools.handle_write_payback_readiness_gate),
        (gtm_economics_rtm_tools.WRITE_RTM_RULES_TOOL, gtm_economics_rtm_tools.handle_write_rtm_rules),
        (gtm_economics_rtm_tools.WRITE_DEAL_OWNERSHIP_MATRIX_TOOL, gtm_economics_rtm_tools.handle_write_deal_ownership_matrix),
        (gtm_economics_rtm_tools.WRITE_RTM_CONFLICT_PLAYBOOK_TOOL, gtm_economics_rtm_tools.handle_write_rtm_conflict_playbook),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=strategist_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=strategist_install.install,
    ))


if __name__ == "__main__":
    main()
