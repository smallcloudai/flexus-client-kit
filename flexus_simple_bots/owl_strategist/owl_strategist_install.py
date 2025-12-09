import asyncio
import json
import base64
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_install

from flexus_simple_bots.owl_strategist import owl_strategist_bot, owl_strategist_prompts
from flexus_simple_bots.owl_strategist.skills import diagnostic as skill_diagnostic


BOT_DESCRIPTION = """
## Owl Strategist — AI Marketing Strategist

Expert bot for hypothesis validation and go-to-market strategy creation.

**8-step pipeline (strict order):**
1. 📝 Input — product, hypothesis, budget, timeline
2. 🔍 Diagnostic — hypothesis classification, identifying unknowns
3. 📊 Metrics — KPIs, stop-rules, MDE calculation
4. 👥 Segment — ICP, JTBD, Customer Journey
5. 💬 Messaging — value proposition, positioning
6. 📡 Channels — channel selection, experiment design
7. 🎯 Tactics — campaign specs, creatives, landing pages
8. ⚖️ Compliance — risk assessment, platform policies

**Human-in-the-Loop:**
Every step is discussed with you — no automation without your understanding and approval.

**Who it's for:**
- Startups at validation stage
- Product managers exploring new markets
- Marketers planning experiments
"""


# Default Lark kernel for agent subchats — used by skills that don't define their own
DEFAULT_AGENT_LARK = '''
msg = messages[-1]
if msg["role"] == "assistant":
    content = str(msg["content"])
    if "AGENT_COMPLETE" in content:
        print("Agent finished, returning result")
        subchat_result = content
    elif len(msg["tool_calls"]) == 0:
        print("Agent stopped without completion marker")
        post_cd_instruction = "You must complete your analysis. Save your result via flexus_policy_document and end with AGENT_COMPLETE."
'''


async def install(
    client: ckit_client.FlexusClient,
    ws_id: str,
    bot_name: str,
    bot_version: str,
    tools: list,
):
    bot_tools_json = json.dumps([t.openai_style_tool() for t in tools])
    agent_tools_json = json.dumps([t.openai_style_tool() for t in owl_strategist_bot.AGENT_TOOLS])

    # XXX pictures will be added later
    pic_big = None
    pic_small = None
    pic_big_path = Path(__file__).with_name("owl_strategist-1024x1536.webp")
    pic_small_path = Path(__file__).with_name("owl_strategist-256x256.webp")
    if pic_big_path.exists():
        pic_big = base64.b64encode(pic_big_path.read_bytes()).decode("ascii")
    if pic_small_path.exists():
        pic_small = base64.b64encode(pic_small_path.read_bytes()).decode("ascii")

    await ckit_bot_install.marketplace_upsert_dev_bot(
        client,
        ws_id=ws_id,
        marketable_name=bot_name,
        marketable_version=bot_version,
        marketable_accent_color="#8B4513",
        marketable_title1="Owl Strategist",
        marketable_title2="AI expert for marketing strategies and hypothesis validation",
        marketable_author="Flexus",
        marketable_occupation="Marketing Strategist",
        marketable_description=BOT_DESCRIPTION,
        marketable_typical_group="Marketing / Strategy",
        marketable_github_repo="https://github.com/smallcloudai/flexus-client-kit.git",
        marketable_run_this="python -m flexus_simple_bots.owl_strategist.owl_strategist_bot",
        marketable_setup_default=[],
        marketable_featured_actions=[
            {"feat_question": "Help me create a strategy for my hypothesis", "feat_run_as_setup": False, "feat_depends_on_setup": []},
            {"feat_question": "Analyze my product idea", "feat_run_as_setup": False, "feat_depends_on_setup": []},
        ],
        marketable_intro_message="Привет! Я Сова-Стратег 🦉 Помогаю фаундерам валидировать гипотезы и создавать маркетинговые стратегии. Расскажи о продукте — что хочешь протестировать?",
        marketable_preferred_model_default="gpt-5.1",
        marketable_daily_budget_default=500_000,
        marketable_default_inbox_default=50_000,
        marketable_experts=[
            # Orchestrator — talks to human, manages pipeline
            ("default", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.DEFAULT_PROMPT,
                fexp_python_kernel="",
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=bot_tools_json,
            )),
            # Agent: Diagnostic — classify hypothesis, identify unknowns (from skills/diagnostic.py)
            ("diagnostic", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=skill_diagnostic.SYSTEM_PROMPT,
                fexp_python_kernel=skill_diagnostic.LARK_KERNEL,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Metrics — KPI, MDE, stop/accelerate rules (TODO: move to skills/)
            ("metrics", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.METRICS_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Segment — ICP, JTBD, customer journey (TODO: move to skills/)
            ("segment", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.SEGMENT_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Messaging — value prop, angles, objections (TODO: move to skills/)
            ("messaging", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.MESSAGING_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Channels — channel selection, test cells, budget (TODO: move to skills/)
            ("channels", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.CHANNELS_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Tactics — campaigns, creatives, landing, tracking (TODO: move to skills/)
            ("tactics", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.TACTICS_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
            # Agent: Compliance — risks, ads policies, privacy (TODO: move to skills/)
            ("compliance", ckit_bot_install.FMarketplaceExpertInput(
                fexp_system_prompt=owl_strategist_prompts.COMPLIANCE_PROMPT,
                fexp_python_kernel=DEFAULT_AGENT_LARK,
                fexp_block_tools="*setup*",
                fexp_allow_tools="",
                fexp_app_capture_tools=agent_tools_json,
            )),
        ],
        marketable_tags=["Marketing", "Strategy", "Hypothesis Validation"],
        marketable_picture_big_b64=pic_big,
        marketable_picture_small_b64=pic_small,
        marketable_schedule=[],
    )


if __name__ == "__main__":
    args = ckit_bot_install.bot_install_argparse()
    client = ckit_client.FlexusClient("owl_strategist_install")
    asyncio.run(install(
        client,
        ws_id=args.ws,
        bot_name=owl_strategist_bot.BOT_NAME,
        bot_version=owl_strategist_bot.BOT_VERSION,
        tools=owl_strategist_bot.TOOLS,
    ))
