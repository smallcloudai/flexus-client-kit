import asyncio
import logging

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_shutdown
from flexus_simple_bots.owl3 import owl3_bot
from flexus_simple_bots.strategist import experiment_design_tools
from flexus_simple_bots.strategist import gtm_economics_rtm_tools
from flexus_simple_bots.strategist import mvp_validation_tools
from flexus_simple_bots.strategist import positioning_offer_tools
from flexus_simple_bots.strategist import pricing_validation_tools
from flexus_simple_bots.strategist import strategist_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_strategist")

BOT_NAME = "strategist"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

STRATEGIST_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    strategist_install.STRATEGIST_ROOTDIR,
    ["flexus_policy_document", "skills", "print_widget"],
    builtin_skills=strategist_install.STRATEGIST_SKILLS,
)

TOOLS = [
    owl3_bot.UPDATE_STRATEGY_TOOL,
    *experiment_design_tools.API_TOOLS,
    *experiment_design_tools.WRITE_TOOLS,
    *mvp_validation_tools.API_TOOLS,
    *mvp_validation_tools.WRITE_TOOLS,
    *positioning_offer_tools.API_TOOLS,
    *positioning_offer_tools.WRITE_TOOLS,
    *pricing_validation_tools.API_TOOLS,
    *pricing_validation_tools.WRITE_TOOLS,
    *gtm_economics_rtm_tools.API_TOOLS,
    *gtm_economics_rtm_tools.WRITE_TOOLS,
    *[t for rec in STRATEGIST_INTEGRATIONS for t in rec.integr_tools],
]


async def strategist_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(STRATEGIST_INTEGRATIONS, rcx)
    pdoc_integration = integr_objects["flexus_policy_document"]

    owl3_bot.setup_handlers(rcx, pdoc_integration)

    for tool in experiment_design_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await experiment_design_tools.handle_api_tool_call(_n, toolcall, args)

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

    for tool in mvp_validation_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await mvp_validation_tools.handle_api_tool_call(_n, toolcall, args)

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

    for tool in positioning_offer_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await positioning_offer_tools.handle_api_tool_call(_n, toolcall, args)

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

    for tool in pricing_validation_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await pricing_validation_tools.handle_api_tool_call(_n, toolcall, args)

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

    for tool in gtm_economics_rtm_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await gtm_economics_rtm_tools.handle_api_tool_call(_n, toolcall, args)

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
