import asyncio
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills

from flexus_simple_bots import prompts_common
from flexus_simple_bots.frog import frog_bot
from flexus_simple_bots.frog import frog_prompts


TOOL_NAMESET = {t.name for t in frog_bot.TOOLS}

FROG_SUBCHAT_LARK = """
print("Ribbit in logs")     # will be visible in lark logs
subchat_result = "Insect!"
"""

FROG_DEFAULT_LARK = """
print("I see %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    assistant_says1 = str(msg["content"])    # assistant can only produce text, there will not be [{"m_type": "image/png", "m_content": "..."}, ...]
    assistant_says2 = str(msg["tool_calls"]) # that might be a big json but it still converts to string, good enough for a frog
    print("assistant_says1", assistant_says1)
    print("assistant_says2", assistant_says2)
    if "snake" in assistant_says1.lower() or "snake" in assistant_says2.lower():
        post_cd_instruction = "OMG dive down!!!"
"""

EXPERTS = [
    ("default", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=frog_prompts.frog_prompt,
        fexp_python_kernel=FROG_DEFAULT_LARK,
        fexp_allow_tools=",".join(TOOL_NAMESET | ckit_cloudtool.CLOUDTOOLS_QUITE_A_LOT),
        fexp_nature="NATURE_INTERACTIVE",
        fexp_inactivity_timeout=3600,
        fexp_description="Main conversational expert that handles user interactions, task management, and provides cheerful encouragement.",
        fexp_builtin_skills=ckit_skills.read_name_description(frog_bot.FROG_ROOTDIR, frog_bot.FROG_SKILLS),
    )),
    ("huntmode", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=frog_prompts.frog_prompt,
        fexp_python_kernel=FROG_SUBCHAT_LARK,
        fexp_allow_tools=",".join(ckit_cloudtool.KANBAN_SAFE | {"ribbit", "flexus_policy_document", "mongo_store", "make_pond_report"}),
        fexp_nature="NATURE_NO_TASK",
        fexp_description="Subchat expert for catching insects, respecting tongue_capacity limit.",
        fexp_subchat_only=True,
        fexp_model_class="cheap",
    )),
]


async def install(client: ckit_client.FlexusClient):
    r = await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        bot_dir=frog_bot.FROG_ROOTDIR,
        marketable_accent_color="#228B22",
        marketable_title1="Frog",
        marketable_title2="A cheerful frog bot that brings joy and positivity to your workspace.",
        marketable_author="Flexus",
        marketable_occupation="Motivational Assistant",
        marketable_description=(frog_bot.FROG_ROOTDIR / "README.md").read_text(),
        marketable_typical_group="Fun / Testing",
        marketable_setup_default=frog_bot.FROG_SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Ribbit! Tell me something fun", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Give me a motivational boost", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Ribbit! Hi there! I'm Frog, your cheerful workspace companion. I'm here to bring joy and keep your spirits high. What can I do for you today?",
        marketable_preferred_model_expensive="grok-4-1-fast-reasoning",
        marketable_preferred_model_cheap="gpt-5.4-nano",
        marketable_experts=[(name, exp.filter_tools(frog_bot.TOOLS)) for name, exp in EXPERTS],
        add_integrations_into_expert_system_prompt=frog_bot.FROG_INTEGRATIONS,
        marketable_tags=["Fun", "Simple", "Motivational"],
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Work on the assigned task with enthusiasm!"},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_supported=["gmail", "google_business", "google_ads", "google", "notion", "notion_manual", "airtable", "hubspot", "twilio_manual"],
        marketable_auth_scopes={
            "gmail": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.labels",
            ],
            "google_business": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/business.manage",
            ],
            "google_ads": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/adwords",
            ],
            "google": ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/documents",
            ],
        },
    )
    return r.marketable_version


if __name__ == "__main__":
    client = ckit_client.FlexusClient("frog_install")
    asyncio.run(install(client))
