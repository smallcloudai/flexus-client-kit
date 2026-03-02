import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.lawyerrat import lawyerrat_prompts


LAWYERRAT_ROOTDIR = Path(__file__).parent
LAWYERRAT_SKILLS = ckit_skills.static_skills_find(LAWYERRAT_ROOTDIR, shared_skills_allowlist="")
LAWYERRAT_SETUP_SCHEMA = json.loads((LAWYERRAT_ROOTDIR / "setup_schema.json").read_text())

BOT_DESCRIPTION = """
## LawyerRat - Legal Research & Document Assistant

A thorough legal assistant that burrows through documents with rat-like persistence. LawyerRat handles legal research, document drafting, contract review, NDA triage, compliance checks, and risk assessments.

**Key Features:**
- **Legal Research**: Comprehensive research on legal topics and precedents
- **Document Drafting**: Professional legal documents and contracts
- **Contract Review**: Clause-by-clause analysis with GREEN/YELLOW/RED classification
- **NDA Triage**: Quick screening against standard checklist with sign/negotiate/escalate routing
- **Compliance Review**: GDPR, CCPA/CPRA, DPA assessment with gap analysis
- **Risk Assessment**: Severity x Likelihood scoring with prioritized mitigation plans

**Important**: LawyerRat provides legal information and analysis, not legal advice. Always consult with a licensed attorney for actual legal advice.
"""


LAWYERRAT_DEFAULT_LARK = f"""
print("LawyerRat processing %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    assistant_content = str(msg["content"])
    if "malpractice" in assistant_content.lower():
        post_cd_instruction = "Remember to include appropriate disclaimers about not providing legal advice!"
"""

LAWYERRAT_CONTRACT_REVIEW_LARK = """
if messages[-1]["role"] == "assistant":
    content = str(messages[-1]["content"])
    if "REVIEW-COMPLETE" in content:
        subchat_result = "Contract review complete. Read the policy document for detailed analysis."
    elif "REVIEW-ERROR" in content:
        subchat_result = content
    elif len(messages[-1].get("tool_calls", [])) == 0:
        post_cd_instruction = "Continue your analysis. End with REVIEW-COMPLETE or REVIEW-ERROR."
"""

LAWYERRAT_NDA_TRIAGE_LARK = """
if messages[-1]["role"] == "assistant":
    content = str(messages[-1]["content"])
    if "TRIAGE-COMPLETE" in content:
        subchat_result = "NDA triage complete. Read the policy document for triage results."
    elif "TRIAGE-ERROR" in content:
        subchat_result = content
    elif len(messages[-1].get("tool_calls", [])) == 0:
        post_cd_instruction = "Continue your triage. End with TRIAGE-COMPLETE or TRIAGE-ERROR."
"""

LAWYERRAT_COMPLIANCE_LARK = """
if messages[-1]["role"] == "assistant":
    content = str(messages[-1]["content"])
    if "COMPLIANCE-COMPLETE" in content:
        subchat_result = "Compliance review complete. Read the policy document for compliance report."
    elif "COMPLIANCE-ERROR" in content:
        subchat_result = content
    elif len(messages[-1].get("tool_calls", [])) == 0:
        post_cd_instruction = "Continue your review. End with COMPLIANCE-COMPLETE or COMPLIANCE-ERROR."
"""

LAWYERRAT_RISK_ASSESSMENT_LARK = """
if messages[-1]["role"] == "assistant":
    content = str(messages[-1]["content"])
    if "ASSESSMENT-COMPLETE" in content:
        subchat_result = "Risk assessment complete. Read the policy document for risk memo."
    elif "ASSESSMENT-ERROR" in content:
        subchat_result = content
    elif len(messages[-1].get("tool_calls", [])) == 0:
        post_cd_instruction = "Continue your assessment. End with ASSESSMENT-COMPLETE or ASSESSMENT-ERROR."
"""


EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_prompt,
        fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Main legal assistant for research, document drafting, and contract analysis.",
    )),
    ("setup", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_setup,
        fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
        fexp_block_tools="",
        fexp_allow_tools="",
        fexp_description="Setup assistant for configuring legal specialty, formality, and jurisdiction.",
    )),
    ("contract_review", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_contract_review,
        fexp_python_kernel=LAWYERRAT_CONTRACT_REVIEW_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Subchat expert for clause-by-clause contract review with RED/YELLOW/GREEN classification.",
    )),
    ("nda_triage", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_nda_triage,
        fexp_python_kernel=LAWYERRAT_NDA_TRIAGE_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Subchat expert for quick NDA screening with sign/negotiate/escalate routing.",
    )),
    ("compliance", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_compliance,
        fexp_python_kernel=LAWYERRAT_COMPLIANCE_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Subchat expert for GDPR/CCPA/DPA compliance review with gap analysis.",
    )),
    ("risk_assessment", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=lawyerrat_prompts.lawyerrat_risk_assessment,
        fexp_python_kernel=LAWYERRAT_RISK_ASSESSMENT_LARK,
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Subchat expert for severity x likelihood risk scoring with mitigation plans.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode((LAWYERRAT_ROOTDIR / "lawyerrat-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode((LAWYERRAT_ROOTDIR / "lawyerrat-256x256.webp").read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#49cdc2",
        marketable_title1="LawyerRat",
        marketable_title2="A thorough legal research and document assistant with meticulous attention to detail.",
        marketable_author="Flexus",
        marketable_occupation="Legal Research Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Legal / Professional",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.lawyerrat.lawyerrat_bot",
        marketable_setup_default=LAWYERRAT_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Research contract law basics", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Draft a simple NDA", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Review this contract for issues", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Triage an NDA before signing", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Check our privacy policy for GDPR compliance", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Assess legal risks in this partnership agreement", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Hello! I'm LawyerRat, your thorough legal research assistant. I can help with legal research, document drafting, and contract analysis. What legal matter can I assist you with today? (Remember: I provide legal information, not legal advice - always consult a licensed attorney for actual legal advice.)",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_experts=[(name, exp.filter_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Legal", "Research", "Professional", "Documents"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:10m", "sched_first_question": "Look if there are any legal research tasks in inbox. If so, sort them by priority and complexity."},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:5m", "sched_first_question": "Work on the assigned legal task with thorough attention to detail."},
        ]
    )


if __name__ == "__main__":
    from flexus_simple_bots.lawyerrat import lawyerrat_bot
    client = ckit_client.FlexusClient("lawyerrat_install")
    asyncio.run(install(client, bot_name=lawyerrat_bot.BOT_NAME, bot_version=lawyerrat_bot.BOT_VERSION, tools=lawyerrat_bot.TOOLS))
