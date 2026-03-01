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


def _extract_json_blocks(text: str) -> List[str]:
    return re.findall(r"```json\s*\n(.*?)```", text, re.DOTALL)


def _validate_skill(path: Path, text: str) -> Dict[str, str]:
    front = _parse_frontmatter(text)
    if not front:
        logger.warning("%s: missing YAML frontmatter (---)", path)
        return front
    if "name" not in front:
        logger.warning("%s: frontmatter missing 'name'", path)
    if "description" not in front:
        logger.warning("%s: frontmatter missing 'description'", path)
    body = _strip_frontmatter(text)
    for i, raw in enumerate(_extract_json_blocks(body)):
        raw = raw.strip()
        print("AAAA", path, raw)
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError("%s: json block #%d: %s" % (path, i + 1, e))
        if isinstance(obj, dict) and ("type" in obj or "properties" in obj):
            print(5555)
            logger.info("%s: json block #%d looks like a json-schema", path, i + 1)
    return front


def _skill_dirs(bot_root_dir: Path) -> List[Path]:
    return [
        bot_root_dir / "skills",
        bot_root_dir.parents[1] / "shared_skills",
    ]


def skill_find_all(bot_root_dir: Path) -> List[str]:
    # Called from bot module top level, logger was not set up at this point, any logs are invisible
    found = []
    for d in _skill_dirs(bot_root_dir):
        if d.is_dir():
            for p in d.glob("*/SKILL.md"):
                _validate_skill(p, p.read_text())
                found.append(p.parent.name)
    found.sort()
    return found


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
                    "description": front["description"],
                })
                break
        else:
            raise FileNotFoundError("skill %r not found in %s" % (name, [str(d) for d in _skill_dirs(bot_root_dir)]))
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

