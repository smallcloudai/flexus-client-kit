import logging
import json
from pathlib import Path

from flexus_client_kit.core import ckit_bot_install
from flexus_simple_bots.shared import prompts_common

logger = logging.getLogger("exprt")


def parse_expert_md(text: str):
    header = {}
    body = text
    if text.startswith("---\n"):
        _, front, body = text.split("---\n", 2)
        for line in front.strip().split("\n"):
            k, _, v = line.partition(":")
            header[k.strip()] = v.strip()
    return header, body


def parse_skill_names(raw: str) -> list[str]:
    if not raw.strip():
        return []
    out = []
    for item in raw.split(","):
        x = item.strip()
        if x and x not in out:
            out.append(x)
    return out


def build_expert_prompt(prompts_dir: Path, expert_name: str) -> str:
    header, body = parse_expert_md((prompts_dir / f"expert_{expert_name}.md").read_text())
    skill_blocks = []
    for skill_name in parse_skill_names(header.get("fexp_skills", "")):
        skill_path = prompts_dir / f"skill_{skill_name}.md"
        if not skill_path.exists():
            raise KeyError(f"{prompts_dir / f'expert_{expert_name}.md'}: skill file not found: {skill_path.name}")
        skill_blocks.append(
            f"\n## Skill: {skill_name}\n\n"
            + skill_path.read_text().strip()
            + "\n"
        )
    pdoc_schemas_raw = header.get("fexp_pdoc_output_schemas", "").strip()
    pdoc_schema_block = ""
    if pdoc_schemas_raw:
        try:
            parsed = json.loads(pdoc_schemas_raw)
            if not isinstance(parsed, list):
                raise KeyError(f"{prompts_dir / f'expert_{expert_name}.md'}: fexp_pdoc_output_schemas must be a JSON array")
            pdoc_schema_block = (
                "\n## Strict PDoc Output Schemas\n\n"
                "When writing policy documents, use `flexus_policy_document(op=\"create_with_schema\")` "
                "or `flexus_policy_document(op=\"overwrite_with_schema\")`. Select one schema entry and pass its `schema` in `args.schema`.\n\n"
                f"{json.dumps(parsed, indent=2, ensure_ascii=False)}\n"
            )
        except json.JSONDecodeError as e:
            raise KeyError(f"{prompts_dir / f'expert_{expert_name}.md'}: invalid fexp_pdoc_output_schemas json: {e}") from e
    return (
        (prompts_dir / "personality.md").read_text()
        + "\n"
        + body
        + "\n"
        + "".join(skill_blocks)
        + pdoc_schema_block
        + prompts_common.PROMPT_KANBAN
        + prompts_common.PROMPT_PRINT_WIDGET
        + prompts_common.PROMPT_POLICY_DOCUMENTS
        + prompts_common.PROMPT_A2A_COMMUNICATION
        + prompts_common.PROMPT_HERE_GOES_SETUP
    )


def discover_experts(prompts_dir: Path) -> list[tuple[str, ckit_bot_install.FMarketplaceExpertInput]]:
    experts = []
    for f in sorted(prompts_dir.glob("expert_*.md")):
        name = f.stem.removeprefix("expert_")
        header, _ = parse_expert_md(f.read_text())
        recognized = {"fexp_description", "fexp_block_tools", "fexp_allow_tools", "fexp_skills", "fexp_pdoc_output_schemas"}
        required = {"fexp_description"}
        unknown = set(header.keys()) - recognized
        missing = required - set(header.keys())
        errors = []
        if unknown:
            errors.append(f"unrecognized frontmatter keys: {', '.join(sorted(unknown))}")
        if missing:
            errors.append(f"missing required frontmatter: {', '.join(sorted(missing))}")
        if errors:
            logger.error(
                f"  Expected format of expert_*.md file header:\n\n"
                f"  ---\n"
                f"  fexp_description: A short description of what this expert does\n"
                f"  fexp_block_tools: (optional) tool glob patterns to block\n"
                f"  fexp_allow_tools: (optional) tool glob patterns to allow\n"
                f"  ---\n\n"
            )
            logger.error(f"{f}: {'; '.join(errors)}")
            raise KeyError(f"{f}: {'; '.join(errors)}\n")
        experts.append((name, ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=build_expert_prompt(prompts_dir, name),
            fexp_python_kernel="",
            fexp_block_tools=header.get("fexp_block_tools", ""),
            fexp_allow_tools=header.get("fexp_allow_tools", ""),
            fexp_description=header["fexp_description"],
        )))
    return experts
