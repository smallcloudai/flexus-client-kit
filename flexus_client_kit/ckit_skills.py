import asyncio
import fnmatch
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_github

logger = logging.getLogger("skills")


FETCH_SKILL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="flexus_fetch_skill",
    description="Load a skill by name, returns the skill instructions. Use plain name for built-in skills, or org/repo:skill-name for repo skills.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
        },
        "required": ["name"],
        "additionalProperties": False,
    },
)

DISCOVER_SKILLS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="flexus_discover_skills",
    description="Discover available skills. Returns list of skill names with descriptions. Call to see what skills are available before loading one.",
    parameters={"type": "object", "properties": {}, "required": [], "additionalProperties": False},
)

# Authoritative sources about skills:
# https://agentskills.io/specification
# https://agentskills.io/client-implementation/adding-skills-support


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
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError("%s: json block #%d: %s" % (path, i + 1, e))
        if isinstance(obj, dict) and ("type" in obj or "properties" in obj):
            logger.info("%s: json block #%d looks like a json-schema", path, i + 1)
    return front


def _skill_dirs(bot_root_dir: Path) -> List[Path]:
    return [
        bot_root_dir / "skills",
        bot_root_dir.parents[1] / "shared_skills",
    ]


def _match_allowlist(name: str, allowlist: str) -> bool:
    for pat in allowlist.split(","):
        pat = pat.strip()
        if pat and fnmatch.fnmatch(name, pat):
            return True
    return False


def static_skills_find(bot_root_dir: Path, shared_skills_allowlist: str) -> List[str]:
    # static means designed to save into constant on top level of a bot file
    # logger is not yet initilized here, no logs possible
    found = []
    local_dir = bot_root_dir / "skills"
    shared_dir = bot_root_dir.parents[1] / "shared_skills"
    for d in [local_dir, shared_dir]:
        if not d.is_dir():
            continue
        is_shared = (d == shared_dir)
        for p in d.glob("*/SKILL.md"):
            name = p.parent.name
            if is_shared and not _match_allowlist(name, shared_skills_allowlist):
                continue
            _validate_skill(p, p.read_text())
            found.append(name)
    found.sort()
    return found


def read_name_description(bot_root_dir: Path, skills: List[str]) -> str:
    result = []
    for name in skills:
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


def fetch_skill_md(name: str, bot_root_dir: Path, allowlist: List[str]) -> str:
    if name not in allowlist:
        return "Skill %r not available. Available: %s" % (name, ", ".join(allowlist))
    for d in _skill_dirs(bot_root_dir):
        p = d / name / "SKILL.md"
        if p.is_file():
            return _strip_frontmatter(p.read_text())
    return "Skill %r not found on disk." % name


async def _run_git(*args, timeout=60):
    proc = await asyncio.create_subprocess_exec(
        "git", *args,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return None, "timeout"
    return proc.returncode, stderr.decode()


async def _clone_or_pull_repo(repo_slug: str, workdir: str, fclient, fgroup_id: str) -> str:
    repo_name = repo_slug.split("/")[-1]
    repo_path = os.path.join(workdir, "repos", repo_name)
    repo_url = f"https://github.com/{repo_slug}"
    gh_token = await ckit_github.get_github_token_with_cache(fclient, fgroup_id, repo_url)
    token_part = f"x-access-token:{gh_token.token}@" if gh_token else ""
    auth_url = f"https://{token_part}github.com/{repo_slug}.git"
    clean_url = f"https://github.com/{repo_slug}.git"
    try:
        if not os.path.isdir(repo_path):
            os.makedirs(os.path.dirname(repo_path), exist_ok=True)
            rc, err = await _run_git("clone", auth_url, repo_path, timeout=300)
            if rc != 0:
                logger.error("clone %s failed: %s", repo_slug, err)
                return ""
            await _run_git("-C", repo_path, "remote", "set-url", "origin", clean_url)
        else:
            await _run_git("-C", repo_path, "remote", "set-url", "origin", auth_url)
            rc, err = await _run_git("-C", repo_path, "pull", "--ff-only", timeout=30)
            await _run_git("-C", repo_path, "remote", "set-url", "origin", clean_url)
            if rc != 0:
                logger.warning("pull %s failed: %s", repo_slug, err)
    except Exception:
        logger.error("_clone_or_pull_repo %s failed", repo_slug, exc_info=True)
        return ""
    return repo_path


def _scan_repo_skills(repo_path: str, repo_slug: str) -> List[Dict[str, str]]:
    results = []
    for skills_glob in [".claude/skills/*/SKILL.md", ".agents/skills/*/SKILL.md"]:
        for p in Path(repo_path).glob(skills_glob):
            front = _parse_frontmatter(p.read_text())
            skill_name = front.get("name", p.parent.name)
            results.append({
                "name": f"{repo_slug}:{skill_name}",
                "description": front.get("description", ""),
                "_path": str(p),
            })
    return results


async def discover_skills(
    bot_root_dir: Path,
    builtin_skills: List[str],
    repos: List[str],
    workdir: str,
    fclient,
    fgroup_id: str,
) -> str:
    lines = []
    # built-in skills
    for name in builtin_skills:
        for d in _skill_dirs(bot_root_dir):
            p = d / name / "SKILL.md"
            if p.is_file():
                front = _parse_frontmatter(p.read_text())
                lines.append(f"- {name}: {front.get('description', '(no description)')}")
                break
    # repo skills
    for slug in repos:
        repo_path = await _clone_or_pull_repo(slug, workdir, fclient, fgroup_id)
        if not repo_path:
            lines.append(f"- {slug}: (failed to clone)")
            continue
        for sk in _scan_repo_skills(repo_path, slug):
            desc = sk["description"] or "(no description)"
            lines.append(f"- {sk['name']}: {desc}")
    if not lines:
        return "No skills available."
    return "Available skills:\n" + "\n".join(lines)


def fetch_skill_namespaced(name: str, bot_root_dir: Path, builtin_skills: List[str], workdir: str) -> str:
    if ":" in name:
        # repo skill: "org/repo:skill-name"
        repo_part, skill_name = name.split(":", 1)
        repo_name = repo_part.split("/")[-1]
        for skills_dir in [".claude/skills", ".agents/skills"]:
            p = Path(workdir) / "repos" / repo_name / skills_dir / skill_name / "SKILL.md"
            if p.is_file():
                return _strip_frontmatter(p.read_text())
        return "Skill %r not found on disk." % name
    return fetch_skill_md(name, bot_root_dir, builtin_skills)


async def called_by_model(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any], bot_root_dir: Path, allowlist: List[str]) -> str:
    name = model_produced_args.get("name", "")
    if not name:
        return "Need the `name` parameter. Nothing happened, call again with correct parameters."
    return fetch_skill_md(name, bot_root_dir, allowlist)


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

