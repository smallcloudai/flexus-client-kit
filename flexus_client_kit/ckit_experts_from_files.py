import fnmatch
import logging
from pathlib import Path
from typing import List

from flexus_client_kit import ckit_bot_install
from flexus_client_kit import ckit_skills
from flexus_simple_bots import prompts_common

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


def build_expert_prompt(prompts_dir: Path, expert_name: str) -> str:
    header, body = parse_expert_md((prompts_dir / f"expert_{expert_name}.md").read_text())
    return (
        (prompts_dir / "personality.md").read_text()
        + "\n"
        + body
        + "\n"
        + prompts_common.PROMPT_KANBAN
        + prompts_common.PROMPT_PRINT_WIDGET
        + prompts_common.PROMPT_POLICY_DOCUMENTS
        + prompts_common.PROMPT_A2A_COMMUNICATION
        + prompts_common.PROMPT_HERE_GOES_SETUP
    )


def _filter_skills(all_skills: List[str], header: dict) -> List[str]:
    block = [p.strip() for p in header.get("expert_block_skills", "").split(",") if p.strip()]
    allow = [p.strip() for p in header.get("expert_allow_skills", "").split(",") if p.strip()]
    if allow:
        return [s for s in all_skills if any(fnmatch.fnmatch(s, p) for p in allow)]
    if block:
        return [s for s in all_skills if not any(fnmatch.fnmatch(s, p) for p in block)]
    return all_skills


def discover_experts(bot_dir: Path, all_possible_skills: List[str]) -> list[tuple[str, ckit_bot_install.FMarketplaceExpertInput]]:
    prompts_dir = bot_dir / "prompts"
    experts = []
    for f in sorted(prompts_dir.glob("expert_*.md")):
        name = f.stem.removeprefix("expert_")
        header, _ = parse_expert_md(f.read_text())
        recognized = {"expert_description", "expert_block_tools", "expert_allow_tools", "expert_block_skills", "expert_allow_skills"}
        required = {"expert_description"}
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
                f"  expert_description: A short description of what this expert does\n"
                f"  expert_block_tools: (optional) tool glob patterns to block\n"
                f"  expert_allow_tools: (optional) tool glob patterns to allow\n"
                f"  expert_block_skills: (optional) skill glob patterns to block\n"
                f"  expert_allow_skills: (optional) skill glob patterns to allow\n"
                f"  ---\n\n"
            )
            logger.error(f"{f}: {'; '.join(errors)}")
            raise KeyError(f"{f}: {'; '.join(errors)}\n")
        exp_skills = _filter_skills(all_possible_skills, header)
        experts.append((name, ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=build_expert_prompt(prompts_dir, name),
            fexp_python_kernel="",
            fexp_block_tools=header.get("expert_block_tools", ""),
            fexp_allow_tools=header.get("expert_allow_tools", ""),
            fexp_description=header["expert_description"],
            fexp_builtin_skills=ckit_skills.read_name_description(bot_dir, exp_skills) if exp_skills else "[]",
        )))
    return experts
