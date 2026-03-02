import asyncio
import logging
import time

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_shutdown
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_linkedin
from flexus_client_kit.integrations.facebook.fi_facebook import IntegrationFacebook, FACEBOOK_TOOL
from flexus_simple_bots.botticelli import botticelli_bot
from flexus_simple_bots.botticelli.botticelli_bot import (
    STYLEGUIDE_TEMPLATE_TOOL,
    GENERATE_PICTURE_TOOL,
    CROP_IMAGE_TOOL,
    CAMPAIGN_BRIEF_TOOL,
)
from flexus_simple_bots.executor import churn_learning_tools
from flexus_simple_bots.executor import creative_paid_channels_tools
from flexus_simple_bots.executor import executor_install
from flexus_simple_bots.executor import experiment_execution
from flexus_simple_bots.executor import partner_ecosystem_tools
from flexus_simple_bots.executor import pilot_delivery_tools
from flexus_simple_bots.executor import retention_intelligence_tools
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_executor")

BOT_NAME = "executor"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

EXECUTOR_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    executor_install.EXECUTOR_ROOTDIR,
    ["flexus_policy_document", "skills", "print_widget"],
    builtin_skills=executor_install.EXECUTOR_SKILLS,
)

TOOLS = [
    fi_linkedin.LINKEDIN_TOOL,
    FACEBOOK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    experiment_execution.LAUNCH_EXPERIMENT_TOOL,
    STYLEGUIDE_TEMPLATE_TOOL,
    GENERATE_PICTURE_TOOL,
    CROP_IMAGE_TOOL,
    CAMPAIGN_BRIEF_TOOL,
    *creative_paid_channels_tools.API_TOOLS,
    *creative_paid_channels_tools.WRITE_TOOLS,
    *pilot_delivery_tools.API_TOOLS,
    *pilot_delivery_tools.WRITE_TOOLS,
    *partner_ecosystem_tools.API_TOOLS,
    *partner_ecosystem_tools.WRITE_TOOLS,
    *retention_intelligence_tools.API_TOOLS,
    *retention_intelligence_tools.WRITE_TOOLS,
    *churn_learning_tools.API_TOOLS,
    *churn_learning_tools.WRITE_TOOLS,
    *[t for rec in EXECUTOR_INTEGRATIONS for t in rec.integr_tools],
]


async def executor_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(EXECUTOR_INTEGRATIONS, rcx)
    pdoc_integration = integr_objects["flexus_policy_document"]

    setup = ckit_bot_exec.official_setup_mixing_procedure(executor_install.EXECUTOR_SETUP_SCHEMA, rcx.persona.persona_setup)
    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    linkedin_integration = fi_linkedin.IntegrationLinkedIn(
        fclient=fclient,
        rcx=rcx,
        ad_account_id=setup.get("ad_account_id", ""),
    )
    facebook_integration = IntegrationFacebook(fclient=fclient, rcx=rcx, ad_account_id="", pdoc_integration=pdoc_integration)
    experiment_integr = experiment_execution.IntegrationExperimentExecution(
        pdoc_integration=pdoc_integration,
        fclient=fclient,
        facebook_integration=facebook_integration,
    )

    @rcx.on_tool_call(fi_linkedin.LINKEDIN_TOOL.name)
    async def _h_linkedin(toolcall, args):
        return await linkedin_integration.called_by_model(toolcall, args)

    @rcx.on_tool_call(FACEBOOK_TOOL.name)
    async def _h_facebook(toolcall, args):
        return await facebook_integration.called_by_model(toolcall, args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def _h_mongo(toolcall, args):
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, args)

    @rcx.on_tool_call(experiment_execution.LAUNCH_EXPERIMENT_TOOL.name)
    async def _h_launch(toolcall, args):
        return await experiment_integr.launch_experiment(toolcall, args)

    await botticelli_bot.setup_handlers(fclient, rcx, pdoc_integration)

    for tool in creative_paid_channels_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await creative_paid_channels_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (creative_paid_channels_tools.WRITE_CREATIVE_VARIANT_PACK_TOOL, creative_paid_channels_tools.handle_write_creative_variant_pack),
        (creative_paid_channels_tools.WRITE_CREATIVE_ASSET_MANIFEST_TOOL, creative_paid_channels_tools.handle_write_creative_asset_manifest),
        (creative_paid_channels_tools.WRITE_CREATIVE_CLAIM_RISK_REGISTER_TOOL, creative_paid_channels_tools.handle_write_creative_claim_risk_register),
        (creative_paid_channels_tools.WRITE_PAID_CHANNEL_TEST_PLAN_TOOL, creative_paid_channels_tools.handle_write_paid_channel_test_plan),
        (creative_paid_channels_tools.WRITE_PAID_CHANNEL_RESULT_TOOL, creative_paid_channels_tools.handle_write_paid_channel_result),
        (creative_paid_channels_tools.WRITE_PAID_CHANNEL_BUDGET_GUARDRAIL_TOOL, creative_paid_channels_tools.handle_write_paid_channel_budget_guardrail),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in pilot_delivery_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await pilot_delivery_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (pilot_delivery_tools.WRITE_PILOT_CONTRACT_PACKET_TOOL, pilot_delivery_tools.handle_write_pilot_contract_packet),
        (pilot_delivery_tools.WRITE_PILOT_RISK_CLAUSE_REGISTER_TOOL, pilot_delivery_tools.handle_write_pilot_risk_clause_register),
        (pilot_delivery_tools.WRITE_PILOT_GO_LIVE_READINESS_TOOL, pilot_delivery_tools.handle_write_pilot_go_live_readiness),
        (pilot_delivery_tools.WRITE_FIRST_VALUE_DELIVERY_PLAN_TOOL, pilot_delivery_tools.handle_write_first_value_delivery_plan),
        (pilot_delivery_tools.WRITE_FIRST_VALUE_EVIDENCE_TOOL, pilot_delivery_tools.handle_write_first_value_evidence),
        (pilot_delivery_tools.WRITE_PILOT_EXPANSION_READINESS_TOOL, pilot_delivery_tools.handle_write_pilot_expansion_readiness),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in partner_ecosystem_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await partner_ecosystem_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (partner_ecosystem_tools.WRITE_PARTNER_ACTIVATION_SCORECARD_TOOL, partner_ecosystem_tools.handle_write_partner_activation_scorecard),
        (partner_ecosystem_tools.WRITE_PARTNER_ENABLEMENT_PLAN_TOOL, partner_ecosystem_tools.handle_write_partner_enablement_plan),
        (partner_ecosystem_tools.WRITE_PARTNER_PIPELINE_QUALITY_TOOL, partner_ecosystem_tools.handle_write_partner_pipeline_quality),
        (partner_ecosystem_tools.WRITE_CHANNEL_CONFLICT_INCIDENT_TOOL, partner_ecosystem_tools.handle_write_channel_conflict_incident),
        (partner_ecosystem_tools.WRITE_DEAL_REGISTRATION_POLICY_TOOL, partner_ecosystem_tools.handle_write_deal_registration_policy),
        (partner_ecosystem_tools.WRITE_CONFLICT_RESOLUTION_AUDIT_TOOL, partner_ecosystem_tools.handle_write_conflict_resolution_audit),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in retention_intelligence_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await retention_intelligence_tools.handle_retention_tool_call(_n, toolcall, args)

    for tool, fn in [
        (retention_intelligence_tools.WRITE_COHORT_REVENUE_REVIEW_TOOL, retention_intelligence_tools.handle_write_cohort_revenue_review),
        (retention_intelligence_tools.WRITE_RETENTION_DRIVER_MATRIX_TOOL, retention_intelligence_tools.handle_write_retention_driver_matrix),
        (retention_intelligence_tools.WRITE_RETENTION_READINESS_GATE_TOOL, retention_intelligence_tools.handle_write_retention_readiness_gate),
        (retention_intelligence_tools.WRITE_PMF_CONFIDENCE_SCORECARD_TOOL, retention_intelligence_tools.handle_write_pmf_confidence_scorecard),
        (retention_intelligence_tools.WRITE_PMF_SIGNAL_EVIDENCE_TOOL, retention_intelligence_tools.handle_write_pmf_signal_evidence),
        (retention_intelligence_tools.WRITE_PMF_RESEARCH_BACKLOG_TOOL, retention_intelligence_tools.handle_write_pmf_research_backlog),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    for tool in churn_learning_tools.API_TOOLS:
        n = tool.name
        @rcx.on_tool_call(n)
        async def _h(toolcall, args, _n=n):
            return await churn_learning_tools.handle_api_tool_call(_n, toolcall, args)

    for tool, fn in [
        (churn_learning_tools.WRITE_INTERVIEW_CORPUS_TOOL, churn_learning_tools.handle_write_interview_corpus),
        (churn_learning_tools.WRITE_INTERVIEW_COVERAGE_TOOL, churn_learning_tools.handle_write_interview_coverage),
        (churn_learning_tools.WRITE_SIGNAL_QUALITY_TOOL, churn_learning_tools.handle_write_signal_quality),
        (churn_learning_tools.WRITE_ROOTCAUSE_BACKLOG_TOOL, churn_learning_tools.handle_write_rootcause_backlog),
        (churn_learning_tools.WRITE_FIX_EXPERIMENT_PLAN_TOOL, churn_learning_tools.handle_write_fix_experiment_plan),
        (churn_learning_tools.WRITE_PREVENTION_GATE_TOOL, churn_learning_tools.handle_write_prevention_gate),
    ]:
        @rcx.on_tool_call(tool.name)
        async def _hw(toolcall, args, _f=fn):
            return await _f(toolcall, args, pdoc_integration, rcx)

    @rcx.on_updated_task
    async def _on_updated_task(t: ckit_kanban.FPersonaKanbanTaskOutput):
        experiment_integr.track_experiment_task(t)

    initial_tasks = await ckit_kanban.bot_get_all_tasks(fclient, rcx.persona.persona_id)
    for t in [x for x in initial_tasks if x.ktask_done_ts == 0]:
        experiment_integr.track_experiment_task(t)

    last_experiment_check = 0
    experiment_check_interval = 3600

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
            current_time = time.time()
            if current_time - last_experiment_check > experiment_check_interval:
                await experiment_integr.update_active_experiments()
                last_experiment_check = current_time
    finally:
        logger.info("%s exit", rcx.persona.persona_id)


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=executor_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=executor_install.install,
    ))


if __name__ == "__main__":
    main()
