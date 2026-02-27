import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

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


def _parse_frontmatter(text: str) -> Dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    result = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


def _skill_dirs(bot_root_dir: Path) -> List[Path]:
    return [
        bot_root_dir / "skills",
        bot_root_dir.parents[1] / "shared_skills",
    ]


def skill_find_all(bot_root_dir: Path) -> List[str]:
    found = []
    for d in _skill_dirs(bot_root_dir):
        if d.is_dir():
            found.extend(x.parent.name for x in d.glob("*/SKILL.md"))
    return sorted(set(found))


def read_name_description(bot_root_dir: Path, whitelist: List[str]) -> str:
    result = []
    for name in whitelist:
        for d in _skill_dirs(bot_root_dir):
            p = d / name / "SKILL.md"
            if p.is_file():
                front = _parse_frontmatter(p.read_text())
                assert name == front["name"], "Ooops name inside SKILL.md does not match parent dir name in %s" % p
                result.append({
                    "name": name,
                    "description": front["description"]
                })
                break
        else:
            logger.warning("skill %r not found in %s", name, bot_root_dir)
    return json.dumps(result)


def fetch_skill_md(name: str, bot_root_dir: Path, whitelist: List[str]) -> str:
    if name not in whitelist:
        return "Skill %r not available. Available: %s" % (name, ", ".join(whitelist))
    for d in _skill_dirs(bot_root_dir):
        p = d / name / "SKILL.md"
        if p.is_file():
            return _strip_frontmatter(p.read_text())
    return "Skill %r not found on disk." % name


async def called_by_model(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any], bot_root_dir: Path, whitelist: List[str]) -> str:
    name = model_produced_args.get("name", "")
    if not name:
        return "Need the `name` parameter. Nothing happened, call again with correct parameters."
    return fetch_skill_md(name, bot_root_dir, whitelist)


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

