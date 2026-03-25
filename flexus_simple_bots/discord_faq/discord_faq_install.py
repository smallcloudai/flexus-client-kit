import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common
from flexus_simple_bots.discord_faq import discord_faq_prompts
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION


ROOT = Path(__file__).parent

DISCORD_FAQ_SKILLS = ckit_skills.static_skills_find(ROOT, shared_skills_allowlist="setting-up-external-knowledge-base")

DISCORD_FAQ_SETUP_SCHEMA = json.loads((ROOT / "setup_schema.json").read_text())

DISCORD_FAQ_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    ROOT,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "skills",
        "magic_desk",
    ],
    builtin_skills=DISCORD_FAQ_SKILLS,
)

EXPERTS = [
    (
        "default",
        ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=discord_faq_prompts.discord_faq_stub,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="",
            fexp_inactivity_timeout=3600,
            fexp_description="Operator chat for setup and policy questions.",
            fexp_builtin_skills=ckit_skills.read_name_description(ROOT, DISCORD_FAQ_SKILLS),
        ),
    ),
    (
        "kb_helper",
        ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=discord_faq_prompts.discord_faq_kb_helper,
            fexp_python_kernel="",
            fexp_block_tools="",
            fexp_allow_tools="flexus_vector_search,flexus_read_original,flexus_bot_kanban",
            fexp_inactivity_timeout=3600,
            fexp_description="Research escalated Discord questions using the workspace knowledge base.",
            fexp_builtin_skills=ckit_skills.read_name_description(ROOT, DISCORD_FAQ_SKILLS),
        ),
    ),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big_b64 = base64.b64encode((ROOT / "discord_faq-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small_b64 = base64.b64encode((ROOT / "discord_faq-256x256.webp").read_bytes()).decode("ascii")
    desc = (ROOT / "README.md").read_text()
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#57F287",
        marketable_title1="Discord FAQ",
        marketable_title2="Regex auto-replies plus KB-backed escalations in Flexus.",
        marketable_author="Flexus",
        marketable_occupation="Support",
        marketable_description=desc,
        marketable_typical_group="Community / Discord",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.discord_faq.discord_faq_bot",
        marketable_setup_default=DISCORD_FAQ_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "How do FAQ escalations reach the knowledge base?", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="I answer common questions on Discord from your regex rules and can escalate hard questions to Flexus for KB research.",
        marketable_preferred_model_default="gpt-5.4-nano",
        marketable_experts=[(n, e.filter_tools(tools)) for n, e in EXPERTS],
        add_integrations_into_expert_system_prompt=DISCORD_FAQ_INTEGRATIONS,
        marketable_tags=["Discord", "FAQ", "Support"],
        marketable_picture_big_b64=pic_big_b64,
        marketable_picture_small_b64=pic_small_b64,
        marketable_schedule=[prompts_common.SCHED_PICK_ONE_5M],
        marketable_auth_supported=["discord_manual"],
    )


if __name__ == "__main__":
    async def _main() -> None:
        fclient = ckit_client.FlexusClient(ckit_client.bot_service_name("discord_faq", SIMPLE_BOTS_COMMON_VERSION), endpoint="/v1/jailed-bot")
        await install(fclient, "discord_faq", SIMPLE_BOTS_COMMON_VERSION, [])

    asyncio.run(_main())
