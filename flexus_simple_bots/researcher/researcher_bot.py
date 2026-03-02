import asyncio
import logging
import time

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_shutdown
from flexus_simple_bots.productman import productman_bot
from flexus_simple_bots.productman.integrations import survey_research as productman_survey
from flexus_simple_bots.researcher import customer_discovery_tools
from flexus_simple_bots.researcher import market_signal_tools
from flexus_simple_bots.researcher import pain_alternatives_tools
from flexus_simple_bots.researcher import pipeline_qualification_tools
from flexus_simple_bots.researcher import researcher_install
from flexus_simple_bots.researcher import segment_qualification_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_researcher")

BOT_NAME = "researcher"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

RESEARCHER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    researcher_install.RESEARCHER_ROOTDIR,
    ["flexus_policy_document", "skills", "print_widget"],
    builtin_skills=researcher_install.RESEARCHER_SKILLS,
)

TOOLS = [
    *market_signal_tools.SIGNAL_TOOLS,
    *market_signal_tools.WRITE_TOOLS,
    *customer_discovery_tools.API_TOOLS,
    *customer_discovery_tools.WRITE_TOOLS,
    *pain_alternatives_tools.API_TOOLS,
    *pain_alternatives_tools.WRITE_TOOLS,
    *segment_qualification_tools.API_TOOLS,
    *segment_qualification_tools.WRITE_TOOLS,
    *pipeline_qualification_tools.API_TOOLS,
    *pipeline_qualification_tools.WRITE_TOOLS,
    productman_bot.IDEA_TEMPLATE_TOOL,
    productman_bot.HYPOTHESIS_TEMPLATE_TOOL,
    productman_bot.VERIFY_IDEA_TOOL,
    productman_survey.SURVEY_RESEARCH_TOOL,
    *[t for rec in RESEARCHER_INTEGRATIONS for t in rec.integr_tools],
]


async def researcher_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(RESEARCHER_INTEGRATIONS, rcx)
    pdoc_integration = integr_objects["flexus_policy_document"]

    for tool in market_signal_tools.SIGNAL_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await market_signal_tools.handle_signal_tool_call(_n, toolcall, args, rcx)

    for tool, fn in [
        (market_signal_tools.WRITE_SNAPSHOT_TOOL, market_signal_tools.handle_write_snapshot),
        (market_signal_tools.WRITE_SIGNAL_REGISTER_TOOL, market_signal_tools.handle_write_signal_register),
        (market_signal_tools.WRITE_HYPOTHESIS_BACKLOG_TOOL, market_signal_tools.handle_write_hypothesis_backlog),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in customer_discovery_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await customer_discovery_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (customer_discovery_tools.WRITE_INTERVIEW_INSTRUMENT_TOOL, customer_discovery_tools.handle_write_interview_instrument),
        (customer_discovery_tools.WRITE_SURVEY_INSTRUMENT_TOOL, customer_discovery_tools.handle_write_survey_instrument),
        (customer_discovery_tools.WRITE_INSTRUMENT_READINESS_TOOL, customer_discovery_tools.handle_write_instrument_readiness),
        (customer_discovery_tools.WRITE_RECRUITMENT_PLAN_TOOL, customer_discovery_tools.handle_write_recruitment_plan),
        (customer_discovery_tools.WRITE_RECRUITMENT_FUNNEL_TOOL, customer_discovery_tools.handle_write_recruitment_funnel),
        (customer_discovery_tools.WRITE_RECRUITMENT_COMPLIANCE_TOOL, customer_discovery_tools.handle_write_recruitment_compliance),
        (customer_discovery_tools.WRITE_INTERVIEW_CORPUS_TOOL, customer_discovery_tools.handle_write_interview_corpus),
        (customer_discovery_tools.WRITE_JTBD_OUTCOMES_TOOL, customer_discovery_tools.handle_write_jtbd_outcomes),
        (customer_discovery_tools.WRITE_EVIDENCE_QUALITY_TOOL, customer_discovery_tools.handle_write_evidence_quality),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in pain_alternatives_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await pain_alternatives_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (pain_alternatives_tools.WRITE_PAIN_SIGNAL_REGISTER_TOOL, pain_alternatives_tools.handle_write_pain_signal_register),
        (pain_alternatives_tools.WRITE_PAIN_ECONOMICS_TOOL, pain_alternatives_tools.handle_write_pain_economics),
        (pain_alternatives_tools.WRITE_PAIN_RESEARCH_READINESS_GATE_TOOL, pain_alternatives_tools.handle_write_pain_research_readiness_gate),
        (pain_alternatives_tools.WRITE_ALTERNATIVE_LANDSCAPE_TOOL, pain_alternatives_tools.handle_write_alternative_landscape),
        (pain_alternatives_tools.WRITE_COMPETITIVE_GAP_MATRIX_TOOL, pain_alternatives_tools.handle_write_competitive_gap_matrix),
        (pain_alternatives_tools.WRITE_DISPLACEMENT_HYPOTHESES_TOOL, pain_alternatives_tools.handle_write_displacement_hypotheses),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in segment_qualification_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await segment_qualification_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (segment_qualification_tools.WRITE_SEGMENT_ENRICHMENT_TOOL, segment_qualification_tools.handle_write_segment_enrichment),
        (segment_qualification_tools.WRITE_SEGMENT_DATA_QUALITY_TOOL, segment_qualification_tools.handle_write_segment_data_quality),
        (segment_qualification_tools.WRITE_SEGMENT_PRIORITY_MATRIX_TOOL, segment_qualification_tools.handle_write_segment_priority_matrix),
        (segment_qualification_tools.WRITE_PRIMARY_SEGMENT_DECISION_TOOL, segment_qualification_tools.handle_write_primary_segment_decision),
        (segment_qualification_tools.WRITE_PRIMARY_SEGMENT_GO_NO_GO_GATE_TOOL, segment_qualification_tools.handle_write_primary_segment_go_no_go_gate),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in pipeline_qualification_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await pipeline_qualification_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (pipeline_qualification_tools.WRITE_PROSPECTING_BATCH_TOOL, pipeline_qualification_tools.handle_write_prospecting_batch),
        (pipeline_qualification_tools.WRITE_OUTREACH_EXECUTION_LOG_TOOL, pipeline_qualification_tools.handle_write_outreach_execution_log),
        (pipeline_qualification_tools.WRITE_PROSPECT_DATA_QUALITY_TOOL, pipeline_qualification_tools.handle_write_prospect_data_quality),
        (pipeline_qualification_tools.WRITE_QUALIFICATION_MAP_TOOL, pipeline_qualification_tools.handle_write_qualification_map),
        (pipeline_qualification_tools.WRITE_BUYING_COMMITTEE_COVERAGE_TOOL, pipeline_qualification_tools.handle_write_buying_committee_coverage),
        (pipeline_qualification_tools.WRITE_QUALIFICATION_GO_NO_GO_GATE_TOOL, pipeline_qualification_tools.handle_write_qualification_go_no_go_gate),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    survey_integration = productman_bot.setup_handlers(fclient, rcx, pdoc_integration)

    @rcx.on_updated_task
    async def _on_updated_task(t: ckit_kanban.FPersonaKanbanTaskOutput):
        survey_integration.track_survey_task(t)

    initial_tasks = await ckit_kanban.bot_get_all_tasks(fclient, rcx.persona.persona_id)
    for t in [x for x in initial_tasks if x.ktask_done_ts == 0]:
        survey_integration.track_survey_task(t)

    last_survey_update = 0.0
    survey_update_interval = 60

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

            if time.time() - last_survey_update > survey_update_interval:
                await survey_integration.update_active_surveys(
                    fclient,
                    survey_integration.update_task_survey_status,
                )
                last_survey_update = time.time()
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=researcher_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=researcher_install.install,
    ))


if __name__ == "__main__":
    main()
