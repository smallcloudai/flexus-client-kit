import asyncio
import json
import base64
import io
from pathlib import Path
from typing import List

from PIL import Image

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool

from flexus_simple_bots import prompts_common
from flexus_simple_bots.lawyerrat import lawyerrat_prompts


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


lawyerrat_setup_schema = [
    {
        "bs_name": "legal_specialty",
        "bs_type": "string_short",
        "bs_default": "general",
        "bs_group": "Legal Focus",
        "bs_order": 1,
        "bs_importance": 1,
        "bs_description": "Primary legal specialty (general, corporate, contract, employment, intellectual-property, real-estate)",
    },
    {
        "bs_name": "formality_level",
        "bs_type": "string_short",
        "bs_default": "professional",
        "bs_group": "Communication",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Communication style (casual, professional, formal)",
    },
    {
        "bs_name": "citation_style",
        "bs_type": "string_short",
        "bs_default": "bluebook",
        "bs_group": "Legal Focus",
        "bs_order": 2,
        "bs_importance": 0,
        "bs_description": "Preferred legal citation format (bluebook, alwd, universal)",
    },
    {
        "bs_name": "jurisdiction",
        "bs_type": "string_short",
        "bs_default": "US-Federal",
        "bs_group": "Legal Focus",
        "bs_order": 3,
        "bs_importance": 1,
        "bs_description": "Primary jurisdiction for legal research (e.g., US-Federal, US-CA, UK, EU)",
    },
    {
        "bs_name": "max_research_depth",
        "bs_type": "int",
        "bs_default": 3,
        "bs_group": "Research Settings",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "Maximum depth for legal research (1-5, higher means more thorough)",
    },
]


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


def _tools_json(tools: List[ckit_cloudtool.CloudTool], names: List[str]) -> str:
    return json.dumps([t.openai_style_tool() for t in tools if t.name in names])


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: List[ckit_cloudtool.CloudTool],
):
    all_tools = json.dumps([t.openai_style_tool() for t in tools])
    contract_tools = _tools_json(tools, ["analyze_contract", "flexus_policy_document"])
    research_tools = _tools_json(tools, ["legal_research", "flexus_policy_document"])

    pic_big_path = Path(__file__).with_name("lawyerrat-1024x1536.webp")
    pic_small_path = Path(__file__).with_name("lawyerrat-256x256.webp")

    def create_placeholder_webp(width: int, height: int) -> str:
        img = Image.new('RGB', (width, height), color=(139, 69, 19))
        buf = io.BytesIO()
        img.save(buf, format='WEBP')
        return base64.b64encode(buf.getvalue()).decode("ascii")

    if pic_big_path.exists():
        pic_big = base64.b64encode(open(pic_big_path, "rb").read()).decode("ascii")
    else:
        pic_big = create_placeholder_webp(1024, 1536)
        print(f"Warning: {pic_big_path} not found, using placeholder")

    if pic_small_path.exists():
        pic_small = base64.b64encode(open(pic_small_path, "rb").read()).decode("ascii")
    else:
        pic_small = create_placeholder_webp(256, 256)
        print(f"Warning: {pic_small_path} not found, using placeholder")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="LawyerRat",
        marketable_title2="A thorough legal research and document assistant with meticulous attention to detail.",
        marketable_author="Flexus",
        marketable_occupation="Legal Research Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Legal / Professional",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.lawyerrat.lawyerrat_bot",
        marketable_setup_default=lawyerrat_setup_schema,
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
        marketable_experts=[
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_prompt,
                fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=all_tools,
                fexp_description="Main legal assistant for research, document drafting, and contract analysis.",
            )),
            ("setup", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_setup,
                fexp_python_kernel=LAWYERRAT_DEFAULT_LARK,
                fexp_block_tools="",
                fexp_allow_tools="",
                fexp_app_capture_tools=all_tools,
                fexp_description="Setup assistant for configuring legal specialty, formality, and jurisdiction.",
            )),
            ("contract_review", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_contract_review,
                fexp_python_kernel=LAWYERRAT_CONTRACT_REVIEW_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=contract_tools,
                fexp_description="Subchat expert for clause-by-clause contract review with RED/YELLOW/GREEN classification.",
            )),
            ("nda_triage", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_nda_triage,
                fexp_python_kernel=LAWYERRAT_NDA_TRIAGE_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=contract_tools,
                fexp_description="Subchat expert for quick NDA screening with sign/negotiate/escalate routing.",
            )),
            ("compliance", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_compliance,
                fexp_python_kernel=LAWYERRAT_COMPLIANCE_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=research_tools,
                fexp_description="Subchat expert for GDPR/CCPA/DPA compliance review with gap analysis.",
            )),
            ("risk_assessment", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=lawyerrat_prompts.lawyerrat_risk_assessment,
                fexp_python_kernel=LAWYERRAT_RISK_ASSESSMENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=research_tools,
                fexp_description="Subchat expert for severity x likelihood risk scoring with mitigation plans.",
            )),
        ],
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
