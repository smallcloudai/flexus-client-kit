import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("skills")


FETCH_SKILL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="flexus_fetch_skill",
    description="Load a skill by name. Returns the skill instructions (SKILL.md body without YAML header).",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Skill name, e.g. 'internal-comms'"},
        },
        "required": ["name"],
        "additionalProperties": False,
    },
)


def _strip_frontmatter(text: str) -> str:
    m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    if m:
        return text[m.end():]
    return text


def _skill_dirs(bot_root_dir: str) -> List[Path]:
    bot = Path(bot_root_dir)
    # bot-specific skills first, then shared
    return [bot / "skills", bot.parents[1] / "shared_skills"]


def fetch_skill_md(name: str, bot_root_dir: str) -> str:
    for d in _skill_dirs(bot_root_dir):
        p = d / name / "SKILL.md"
        if p.is_file():
            return _strip_frontmatter(p.read_text())
    return "Skill %r not found. Available: %s" % (name, ", ".join(skill_find_all(bot_root_dir)) or "(none)")


def skill_find_all(bot_root_dir: str) -> List[str]:
    found = []
    for d in _skill_dirs(bot_root_dir):
        if d.is_dir():
            found.extend(x.parent.name for x in d.glob("*/SKILL.md"))
    return sorted(set(found))


async def called_by_model(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]], bot_root_dir: str) -> str:
    name = (model_produced_args or {}).get("name", "")
    if not name:
        return "Need the `name` parameter. Nothing happened, call again with correct parameters."
    return fetch_skill_md(name, bot_root_dir)


# Running scripts in skills:
#
# 1) create a pod that stays alive long enough to copy + run
# kubectl run tmp-job --restart=Never --image=alpine --command -- sh -c "sleep 3600"
#
# 2) wait until it's ready
# kubectl wait --for=condition=Ready pod/tmp-job
#
# 3) copy inputs in (directory → /work/in)
# kubectl exec tmp-job -- sh -c "mkdir -p /work/in /work/out"
# kubectl cp ./my_inputs/. tmp-job:/work/in
#
# 4) run your command, write outputs to /work/out
# kubectl exec tmp-job -- sh -c "ls -la /work/in > /work/out/result.txt"
#
# 5) copy outputs back
# kubectl cp tmp-job:/work/out ./outputs
#
# 6) cleanup
# kubectl delete pod tmp-job
#

