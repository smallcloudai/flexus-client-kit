import json
from pathlib import Path
from typing import Any

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations import integration_tool_runtime
from flexus_simple_bots import prompts_common


_PLACEHOLDER_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+Xn9kAAAAASUVORK5CYII="


def _skill_index(prompts_module: Any) -> dict[str, dict[str, Any]]:
    try:
        out: dict[str, dict[str, Any]] = {}
        for item in prompts_module.BOT_SKILLS:
            name = str(item.get("name", "")).strip()
            if name and name not in out:
                out[name] = item
        return out
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build skill index: {e}") from e


def _build_expert_prompt(prompts_module: Any, expert: dict[str, Any]) -> str:
    try:
        skills = _skill_index(prompts_module)
        skill_blocks: list[str] = []
        for skill_name in expert.get("skills", []):
            skill_obj = skills.get(skill_name)
            if skill_obj is None:
                raise KeyError(f"Missing skill {skill_name}")
            skill_blocks.append(
                "\n## Skill: "
                + str(skill_obj.get("name", skill_name))
                + "\n\n"
                + str(skill_obj.get("body_md", "")).strip()
                + "\n"
            )

        pdoc_schemas = expert.get("pdoc_output_schemas", [])
        pdoc_block = ""
        if pdoc_schemas:
            pdoc_block = (
                "\n## Strict PDoc Output Schemas\n\n"
                "When writing policy documents, use `flexus_policy_document(op=\"create_with_schema\")` "
                "or `flexus_policy_document(op=\"overwrite_with_schema\")`. "
                "Select one schema entry and pass its `schema` in `args.schema`.\n\n"
                + json.dumps(pdoc_schemas, indent=2, ensure_ascii=False)
                + "\n"
            )

        return (
            str(prompts_module.BOT_PERSONALITY_MD).strip()
            + "\n\n"
            + str(expert.get("body_md", "")).strip()
            + "\n"
            + "".join(skill_blocks)
            + pdoc_block
            + prompts_common.PROMPT_KANBAN
            + prompts_common.PROMPT_PRINT_WIDGET
            + prompts_common.PROMPT_POLICY_DOCUMENTS
            + prompts_common.PROMPT_A2A_COMMUNICATION
            + prompts_common.PROMPT_HERE_GOES_SETUP
        )
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build expert prompt: {e}") from e


def _meta_from_prompts(bot_name: str, prompts_module: Any, readme_text: str) -> dict[str, Any]:
    try:
        default_title = bot_name.replace("_", " ").title()
        default_description = readme_text.strip().splitlines()[0] if readme_text.strip() else default_title
        raw = getattr(prompts_module, "BOT_META", {})
        if isinstance(raw, dict):
            return {
                "accent_color": str(raw.get("accent_color", "#2563EB")),
                "title1": str(raw.get("title1", default_title)),
                "title2": str(raw.get("title2", default_description)),
                "author": str(raw.get("author", "Flexus")),
                "occupation": str(raw.get("occupation", "Automation Assistant")),
                "typical_group": str(raw.get("typical_group", "GTM / Ops")),
                "github_repo": str(raw.get("github_repo", "https://github.com/smallcloudai/flexus-client-kit.git")),
                "intro_message": str(raw.get("intro_message", default_description)),
                "preferred_model_default": str(raw.get("preferred_model_default", "grok-4-1-fast-non-reasoning")),
                "daily_budget_default": int(raw.get("daily_budget_default", 100000)),
                "default_inbox_default": int(raw.get("default_inbox_default", 10000)),
                "tags": list(raw.get("tags", ["GTM", "Automation"])),
            }
        return {
            "accent_color": "#2563EB",
            "title1": default_title,
            "title2": default_description,
            "author": "Flexus",
            "occupation": "Automation Assistant",
            "typical_group": "GTM / Ops",
            "github_repo": "https://github.com/smallcloudai/flexus-client-kit.git",
            "intro_message": default_description,
            "preferred_model_default": "grok-4-1-fast-non-reasoning",
            "daily_budget_default": 100000,
            "default_inbox_default": 10000,
            "tags": ["GTM", "Automation"],
        }
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build bot metadata: {e}") from e


def _featured_actions(prompts_module: Any) -> list[dict[str, Any]]:
    try:
        raw = list(getattr(prompts_module, "BOT_FEATURED_ACTIONS", []))
        out: list[dict[str, Any]] = []
        for item in raw:
            x = dict(item)
            x.setdefault("feat_depends_on_setup", [])
            out.append(x)
        return out
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build featured actions: {e}") from e


def _experts_payload(
    prompts_module: Any,
    tools: list[ckit_cloudtool.CloudTool],
) -> list[tuple[str, ckit_bot_install.FMarketplaceExpertInput]]:
    try:
        out: list[tuple[str, ckit_bot_install.FMarketplaceExpertInput]] = []
        for expert in prompts_module.BOT_EXPERTS:
            name = str(expert["name"])
            out.append((
                name,
                ckit_bot_install.FMarketplaceExpertInput(
                    fexp_system_prompt=_build_expert_prompt(prompts_module, expert),
                    fexp_python_kernel="",
                    fexp_block_tools=str(expert.get("fexp_block_tools", "")),
                    fexp_allow_tools=str(expert.get("fexp_allow_tools", "")),
                    fexp_description=str(expert.get("fexp_description", "")),
                ).provide_tools(tools),
            ))
        return out
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build experts payload: {e}") from e


async def install_bot_from_prompts(
    client: ckit_client.FlexusClient,
    bot_name: str,
    bot_version: str,
    prompts_module: Any,
    setup_schema: list[dict[str, Any]],
    install_file: str,
    tools: list[ckit_cloudtool.CloudTool],
) -> None:
    try:
        readme = Path(install_file).with_name("README.md").read_text(encoding="utf-8")
        meta = _meta_from_prompts(bot_name, prompts_module, readme)

        schedule = list(getattr(prompts_module, "BOT_SCHEDULE", [])) or [prompts_common.SCHED_PICK_ONE_5M]
        auth_supported = list(getattr(prompts_module, "BOT_AUTH_SUPPORTED", []))
        auth_scopes = dict(getattr(prompts_module, "BOT_AUTH_SCOPES", {}))

        await ckit_bot_install.marketplace_upsert_dev_bot(
            client,
            ws_id=client.ws_id,
            marketable_name=bot_name,
            marketable_version=bot_version,
            marketable_accent_color=meta["accent_color"],
            marketable_title1=meta["title1"],
            marketable_title2=meta["title2"],
            marketable_author=meta["author"],
            marketable_occupation=meta["occupation"],
            marketable_description=readme,
            marketable_typical_group=meta["typical_group"],
            marketable_github_repo=meta["github_repo"],
            marketable_run_this=f"python -m flexus_simple_bots.{bot_name}.{bot_name}_bot",
            marketable_schedule=schedule,
            marketable_setup_default=setup_schema,
            marketable_featured_actions=_featured_actions(prompts_module),
            marketable_intro_message=meta["intro_message"],
            marketable_preferred_model_default=meta["preferred_model_default"],
            marketable_daily_budget_default=meta["daily_budget_default"],
            marketable_default_inbox_default=meta["default_inbox_default"],
            marketable_picture_big_b64=_PLACEHOLDER_PNG_B64,
            marketable_picture_small_b64=_PLACEHOLDER_PNG_B64,
            marketable_experts=_experts_payload(prompts_module, tools),
            marketable_tags=meta["tags"],
            marketable_forms=ckit_bot_install.load_form_bundles(install_file),
            marketable_auth_supported=auth_supported,
            marketable_auth_scopes=auth_scopes,
        )
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot install {bot_name}: {e}") from e


def build_tools(prompts_module: Any) -> list[ckit_cloudtool.CloudTool]:
    try:
        return integration_tool_runtime.build_tools_from_prompts(prompts_module)
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build tools: {e}") from e
