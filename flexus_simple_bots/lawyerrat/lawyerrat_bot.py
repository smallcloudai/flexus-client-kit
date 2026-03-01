import asyncio
import logging
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.lawyerrat import lawyerrat_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_lawyerrat")


BOT_NAME = "lawyerrat"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


LAWYERRAT_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.integrations_load(
    lawyerrat_install.LAWYERRAT_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
    ],
    builtin_skills=[],
)

LEGAL_RESEARCH_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="legal_research",
    description="Conduct thorough legal research on a specific topic, statute, or case law. Returns relevant information and precedents.",
    parameters={
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "The legal topic, statute, or case to research"},
            "jurisdiction": {"type": "string", "description": "Optional jurisdiction override (e.g., 'US-CA', 'UK')"},
            "depth": {"type": "integer", "description": "Research depth 1-5, higher is more thorough (defaults to setup value)"},
        },
        "required": ["topic"],
    },
)

DRAFT_DOCUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="draft_document",
    description="Draft a legal document or contract based on specified requirements and type.",
    parameters={
        "type": "object",
        "properties": {
            "document_type": {"type": "string", "description": "Type of document (e.g., 'NDA', 'employment-contract', 'terms-of-service')"},
            "parties": {"type": "array", "items": {"type": "string"}, "description": "Names or descriptions of the parties involved"},
            "key_terms": {"type": "object", "description": "Key terms and conditions to include in the document"},
            "special_provisions": {"type": "array", "items": {"type": "string"}, "description": "Any special provisions or clauses to include"},
        },
        "required": ["document_type", "parties"],
    },
)

ANALYZE_CONTRACT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="analyze_contract",
    description="Analyze a contract or agreement for potential issues, risks, and notable clauses.",
    parameters={
        "type": "object",
        "properties": {
            "contract_text": {"type": "string", "description": "The contract text to analyze"},
            "focus_areas": {"type": "array", "items": {"type": "string"}, "description": "Specific areas to focus on (e.g., 'liability', 'termination', 'intellectual-property', 'nda')"},
            "party_perspective": {"type": "string", "description": "Which party's perspective to analyze from (if specified)"},
        },
        "required": ["contract_text"],
    },
)

ASSESS_RISK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="assess_risk",
    description="Assess legal risks for a specific matter, providing structured risk analysis and mitigation recommendations.",
    parameters={
        "type": "object",
        "properties": {
            "matter": {"type": "string", "description": "Description of the matter to assess for legal risk"},
            "context": {"type": "string", "description": "Additional context or background information"},
            "risk_category": {"type": "string", "description": "Category of risk: contract, regulatory, litigation, ip, privacy, employment, corporate"},
        },
        "required": ["matter"],
    },
)

NDA_KEYWORDS = {"nda", "non-disclosure", "nondisclosure", "confidentiality agreement", "confidentiality"}
COMPLIANCE_KEYWORDS = {"compliance", "privacy", "gdpr", "ccpa", "dpa", "data protection", "hipaa", "regulatory", "regulation"}

TOOLS = [
    LEGAL_RESEARCH_TOOL,
    DRAFT_DOCUMENT_TOOL,
    ANALYZE_CONTRACT_TOOL,
    ASSESS_RISK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    *[t for rec in LAWYERRAT_INTEGRATIONS for t in rec.integr_tools],
]


async def lawyerrat_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(lawyerrat_install.LAWYERRAT_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.integrations_init_all(LAWYERRAT_INTEGRATIONS, rcx)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        logger.info(f"LawyerRat task: {t}")
        pass

    @rcx.on_tool_call(LEGAL_RESEARCH_TOOL.name)
    async def toolcall_legal_research(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        topic = model_produced_args.get("topic", "")
        jurisdiction = model_produced_args.get("jurisdiction", setup.get("jurisdiction", "US-Federal"))
        depth = model_produced_args.get("depth", setup.get("max_research_depth", 3))

        if not topic:
            return "Error: Research topic is required."

        logger.info(f"Researching: {topic} (jurisdiction: {jurisdiction}, depth: {depth})")

        research_prompt = f"""Research the following legal topic thoroughly:

Topic: {topic}
Jurisdiction: {jurisdiction}
Research Depth: {depth}/5
Legal Specialty Focus: {setup.get('legal_specialty', 'general')}

Provide a comprehensive analysis including:
1. Relevant statutes, regulations, or case law
2. Key legal principles and precedents
3. Practical implications and applications
4. Any recent developments or changes
5. Potential risks or considerations

Format the response professionally with appropriate citations in {setup.get('citation_style', 'bluebook')} style."""

        topic_lower = topic.lower()
        expert = "compliance" if any(kw in topic_lower for kw in COMPLIANCE_KEYWORDS) else "default"
        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="lawyerrat_research",
            persona_id=rcx.persona.persona_id,
            first_question=[research_prompt],
            first_calls=["null"],
            title=[f"Legal Research: {topic[:50]}"],
            fcall_id=toolcall.fcall_id,
            fexp_name=expert,
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(DRAFT_DOCUMENT_TOOL.name)
    async def toolcall_draft_document(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        document_type = model_produced_args.get("document_type", "")
        parties = model_produced_args.get("parties", [])
        key_terms = model_produced_args.get("key_terms", {})
        special_provisions = model_produced_args.get("special_provisions", [])

        if not document_type or not parties:
            return "Error: Document type and parties are required."

        logger.info(f"Drafting {document_type} for parties: {parties}")

        parties_text = "\n".join([f"- {party}" for party in parties])
        terms_text = "\n".join([f"- {k}: {v}" for k, v in key_terms.items()]) if key_terms else "None specified"
        provisions_text = "\n".join([f"- {p}" for p in special_provisions]) if special_provisions else "None specified"

        draft_prompt = f"""Draft a professional {document_type} document with the following specifications:

Parties Involved:
{parties_text}

Key Terms and Conditions:
{terms_text}

Special Provisions:
{provisions_text}

Jurisdiction: {setup.get('jurisdiction', 'US-Federal')}
Legal Specialty: {setup.get('legal_specialty', 'general')}
Formality Level: {setup.get('formality_level', 'professional')}

Create a thorough, professionally formatted document that includes:
1. Appropriate legal language and structure
2. Standard clauses for this document type
3. The specified key terms and provisions
4. Necessary legal protections and disclaimers
5. Signature blocks and execution provisions

Include a brief summary of key points at the end."""

        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="lawyerrat_draft",
            persona_id=rcx.persona.persona_id,
            first_question=[draft_prompt],
            first_calls=["null"],
            title=[f"Draft: {document_type}"],
            fcall_id=toolcall.fcall_id,
            fexp_name="default",
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(ANALYZE_CONTRACT_TOOL.name)
    async def toolcall_analyze_contract(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        contract_text = model_produced_args.get("contract_text", "")
        focus_areas = model_produced_args.get("focus_areas", [])
        party_perspective = model_produced_args.get("party_perspective", "neutral")

        if not contract_text:
            return "Error: Contract text is required for analysis."

        logger.info(f"Analyzing contract from {party_perspective} perspective")

        focus_text = "\n".join([f"- {area}" for area in focus_areas]) if focus_areas else "General comprehensive review"

        analysis_prompt = f"""Analyze the following contract with meticulous attention to detail:

CONTRACT TEXT:
{contract_text}

ANALYSIS PARAMETERS:
Perspective: {party_perspective}
Focus Areas:
{focus_text}

Jurisdiction Context: {setup.get('jurisdiction', 'US-Federal')}
Legal Specialty: {setup.get('legal_specialty', 'general')}

Provide a thorough analysis including:
1. **Key Terms Summary**: Main obligations, rights, and terms
2. **Potential Issues**: Red flags, ambiguous language, or problematic clauses
3. **Risk Assessment**: Legal and practical risks for the parties
4. **Notable Clauses**: Important provisions (termination, liability, dispute resolution, etc.)
5. **Missing Provisions**: Standard clauses that might be missing
6. **Recommendations**: Suggestions for negotiation or revision

Be systematic and thorough like a diligent rat examining every detail!"""

        # route NDA-related analysis to nda_triage, everything else to contract_review
        combined = " ".join(focus_areas).lower() + " " + contract_text[:500].lower()
        expert = "nda_triage" if any(kw in combined for kw in NDA_KEYWORDS) else "contract_review"
        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="lawyerrat_analyze",
            persona_id=rcx.persona.persona_id,
            first_question=[analysis_prompt],
            first_calls=["null"],
            title=["Contract Analysis"],
            fcall_id=toolcall.fcall_id,
            fexp_name=expert,
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(ASSESS_RISK_TOOL.name)
    async def toolcall_assess_risk(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        matter = model_produced_args.get("matter", "")
        context = model_produced_args.get("context", "")
        risk_category = model_produced_args.get("risk_category", "general")
        if not matter:
            return "Error: Matter description is required."
        logger.info(f"Assessing risk: {matter[:80]} (category: {risk_category})")
        risk_prompt = f"""Assess legal risks for the following matter:

Matter: {matter}
Context: {context or 'None provided'}
Risk Category: {risk_category}
Jurisdiction: {setup.get('jurisdiction', 'US-Federal')}

Provide a structured risk assessment including:
1. **Risk Identification**: Key legal risks and exposures
2. **Severity Rating**: Rate each risk (Critical/High/Medium/Low)
3. **Likelihood**: Probability of each risk materializing
4. **Impact Analysis**: Potential consequences if risks materialize
5. **Mitigation Strategies**: Recommended actions to reduce risk
6. **Monitoring**: Ongoing risk indicators to watch"""
        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="lawyerrat_risk",
            persona_id=rcx.persona.persona_id,
            first_question=[risk_prompt],
            first_calls=["null"],
            title=[f"Risk Assessment: {matter[:50]}"],
            fcall_id=toolcall.fcall_id,
            fexp_name="risk_assessment",
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

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
        bot_main_loop=lawyerrat_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=lawyerrat_install.install,
    ))


if __name__ == "__main__":
    main()
