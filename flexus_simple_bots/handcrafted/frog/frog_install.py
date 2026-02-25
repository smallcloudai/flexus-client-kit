import asyncio
import base64
import json
from pathlib import Path

from flexus_client_kit.core import ckit_client, ckit_bot_install, ckit_cloudtool
from flexus_simple_bots.shared import prompts_common
from flexus_simple_bots.handcrafted.frog import frog_prompts


BOT_DESCRIPTION = (Path(__file__).parent / "README.md").read_text()
SETUP_SCHEMA = json.loads((Path(__file__).parent / "setup_schema.json").read_text())

FROG_SUBCHAT_LARK = f"""
print("Ribbit in logs")     # will be visible in lark logs
subchat_result = "Insect!"
"""

FROG_DEFAULT_LARK = f"""
print("I see %d messages" % len(messages))
msg = messages[-1]
if msg["role"] == "assistant":
    assistant_says1 = str(msg["content"])    # assistant can only produce text, there will not be [{{"m_type": "image/png", "m_content": "..."}}, ...]
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
        fexp_block_tools="*setup*",
        fexp_allow_tools="",
        fexp_description="Main conversational expert that handles user interactions, task management, and provides cheerful encouragement.",
    )),
    ("huntmode", ckit_bot_install.FMarketplaceExpertInput(
        fexp_system_prompt=frog_prompts.frog_prompt,
        fexp_python_kernel=FROG_SUBCHAT_LARK,
        fexp_block_tools="*setup*,frog_catch_insects",
        fexp_allow_tools="",
        fexp_description="Subchat expert for catching insects, respecting tongue_capacity limit.",
    )),
]


async def install(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    tools: list[ckit_cloudtool.CloudTool],
):
    pic_big = base64.b64encode(Path(__file__).with_name("frog-1024x1536.webp").read_bytes()).decode("ascii")
    pic_small = base64.b64encode(Path(__file__).with_name("frog-256x256.webp").read_bytes()).decode("ascii")
    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=client.ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#228B22",
        marketable_title1="Frog",
        marketable_title2="A cheerful frog bot that brings joy and positivity to your workspace.",
        marketable_author="Flexus",
        marketable_occupation="Motivational Assistant",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Fun / Testing",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.handcrafted.frog.frog_bot",
        marketable_setup_default=SETUP_SCHEMA,
        marketable_featured_actions=[
            {"feat_question": "Ribbit! Tell me something fun", "feat_expert": "default", "feat_depends_on_setup": []},
            {"feat_question": "Give me a motivational boost", "feat_expert": "default", "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Ribbit! Hi there! I'm Frog, your cheerful workspace companion. I'm here to bring joy and keep your spirits high. What can I do for you today?",
        marketable_preferred_model_default="grok-4-1-fast-non-reasoning",
        marketable_daily_budget_default=100_000,
        marketable_default_inbox_default=10_000,
        marketable_experts=[(name, exp.provide_tools(tools)) for name, exp in EXPERTS],
        marketable_tags=["Fun", "Simple", "Motivational"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[
            prompts_common.SCHED_TASK_SORT_10M | {"sched_when": "EVERY:5m"},
            prompts_common.SCHED_TODO_5M | {"sched_when": "EVERY:2m", "sched_first_question": "Work on the assigned task with enthusiasm!"},
        ],
        marketable_forms=ckit_bot_install.load_form_bundles(__file__),
        marketable_auth_supported=["google"],
        marketable_auth_scopes={
            "google": [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.labels",
            ]
        },
    )


if __name__ == "__main__":
    from flexus_simple_bots.handcrafted.frog import frog_bot
    client = ckit_client.FlexusClient("frog_install")
    asyncio.run(install(client, bot_name=frog_bot.BOT_NAME, bot_version=frog_bot.BOT_VERSION, tools=frog_bot.TOOLS))
