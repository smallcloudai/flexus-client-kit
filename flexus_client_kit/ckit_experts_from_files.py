from pathlib import Path

from flexus_client_kit import ckit_bot_install
from flexus_simple_bots import prompts_common


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


def discover_experts(prompts_dir: Path) -> list[tuple[str, ckit_bot_install.FMarketplaceExpertInput]]:
    experts = []
    for f in sorted(prompts_dir.glob("expert_*.md")):
        name = f.stem.removeprefix("expert_")
        header, _ = parse_expert_md(f.read_text())
        experts.append((name, ckit_bot_install.FMarketplaceExpertInput(
            fexp_system_prompt=build_expert_prompt(prompts_dir, name),
            fexp_python_kernel="",
            fexp_block_tools=header.get("fexp_block_tools", ""),
            fexp_allow_tools=header.get("fexp_allow_tools", ""),
            fexp_description=header["fexp_description"],
        )))
    return experts
