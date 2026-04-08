import asyncio
import argparse
import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import ckit_bot_install
from flexus_client_kit import no_special_code_bot

_BOT_DIR_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._\-]*/[A-Za-z0-9_][A-Za-z0-9._\-]*$")
_PIC_SMALL_RE = re.compile(r"[\"'(/]([^\"' ()]+\.(?:webp|png|jpg|jpeg|svg))[\"')\s]")


@dataclass
class BotInfoEntry:
    bot_dir: str
    bot_family: str
    marketable_name: str
    runtime_start_cmd: str
    publish_install_cmd: str
    marketable_install_cmd: str
    runtime_entry_path: str
    avatar_path_small: str
    avatar_candidates: list[str]
    metadata_summary: dict[str, Any]
    install_entry_path: str = ""
    manifest_file_path: str = ""


@dataclass
class _InspectResult:
    bot_dir: str
    supported: bool
    reason: str = ""
    entry: BotInfoEntry | None = None


def _normalize_rel_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _normalize_workspace_cmd(command: str) -> str:
    cmd = command.strip()
    if cmd.startswith("cd /workspace"):
        return cmd
    return f"cd /workspace && {cmd}"


def _strip_workspace_prefix(command: str) -> str:
    cmd = command.strip()
    if cmd.startswith("cd /workspace &&"):
        return cmd[len("cd /workspace &&"):].strip()
    if cmd.startswith("cd /workspace;"):
        return cmd[len("cd /workspace;"):].strip()
    return cmd


def _join_publish_install_cmd(marketable_install_cmd: str) -> str:
    cmd = _strip_workspace_prefix(marketable_install_cmd)
    base = "cd /workspace && python -m pip install -e ."
    if not cmd or cmd == "python -m pip install -e .":
        return base
    return f"{base} && {cmd}"


def _check_root_installable(workdir: Path) -> tuple[bool, str]:
    if (workdir / "setup.py").is_file() or (workdir / "pyproject.toml").is_file():
        return True, ""
    return False, "repo root must contain setup.py or pyproject.toml"


def _extract_last_json_obj(text: str) -> dict[str, Any] | None:
    for line in reversed(text.splitlines()):
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


_CAPTURE_KEYS = [
    "bot_name",
    "marketable_name",
    "marketable_run_this",
    "marketable_install_cmd",
    "marketable_setup_default",
    "marketable_featured_actions",
    "marketable_auth_supported",
    "marketable_auth_scopes",
    "marketable_tags",
    "marketable_title1",
    "marketable_title2",
    "marketable_github_repo",
    "marketable_intro_message",
    "marketable_preferred_model_expensive",
    "marketable_preferred_model_cheap",
    "marketable_daily_budget_default",
    "marketable_default_inbox_default",
]


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(x) for x in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            out[str(k)] = _jsonable(v)
        return out
    return repr(value)


class _StopCapture(Exception):
    pass


async def _capture_marketplace_upsert_dev_bot(*args, **kwargs):
    payload = {}
    for key in _CAPTURE_KEYS:
        if key in kwargs:
            payload[key] = _jsonable(kwargs[key])
    raise _StopCapture(payload)


class _DummyClient:
    ws_id = "capture"


def _load_module(install_file: Path):
    spec = importlib.util.spec_from_file_location("_bot_install_capture_module", str(install_file))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec for {install_file}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _capture_install_metadata_here(install_file: Path, bot_name: str) -> dict[str, Any]:
    ckit_bot_install.marketplace_upsert_dev_bot = _capture_marketplace_upsert_dev_bot
    ckit_bot_install.FMarketplaceExpertInput.filter_tools = lambda self, tools: self
    try:
        mod = _load_module(install_file)
    except Exception as e:
        return {"ok": False, "error": f"load failed: {type(e).__name__}: {e}"}
    if not hasattr(mod, "install"):
        return {"ok": False, "error": "install() not found"}

    bot_mod = install_file.name.removesuffix("_install.py") + "_bot.py"
    bot_file = install_file.parent / bot_mod
    if not bot_file.is_file():
        return {"ok": False, "error": f"matching bot file not found: {bot_mod}"}

    async def _run_capture():
        r = await mod.install(_DummyClient(), bot_name=bot_name, bot_version="0.0.0", tools=[])
        return r

    try:
        asyncio.run(_run_capture())
    except _StopCapture as captured:
        payload = captured.args[0] if captured.args else {}
        try:
            bot_mod_spec = importlib.util.spec_from_file_location("_bot_capture_module", str(bot_file))
            if bot_mod_spec is None or bot_mod_spec.loader is None:
                return {"ok": False, "error": f"failed to load bot module spec for {bot_file}"}
            bot_mod_obj = importlib.util.module_from_spec(bot_mod_spec)
            bot_mod_spec.loader.exec_module(bot_mod_obj)
            if not hasattr(bot_mod_obj, "BOT_NAME") or not isinstance(bot_mod_obj.BOT_NAME, str) or not bot_mod_obj.BOT_NAME.strip():
                return {"ok": False, "error": f"{bot_file.name}: BOT_NAME must be non-empty string"}
            payload["bot_name"] = bot_mod_obj.BOT_NAME
        except Exception as e:
            return {"ok": False, "error": f"bot load failed: {type(e).__name__}: {e}"}
        return {"ok": True, "captured": payload}
    except TypeError:
        async def _run_capture_positional():
            r = await mod.install(_DummyClient(), bot_name, "0.0.0", [])
            return r
        try:
            asyncio.run(_run_capture_positional())
        except _StopCapture as captured:
            payload = captured.args[0] if captured.args else {}
            try:
                bot_mod_spec = importlib.util.spec_from_file_location("_bot_capture_module", str(bot_file))
                if bot_mod_spec is None or bot_mod_spec.loader is None:
                    return {"ok": False, "error": f"failed to load bot module spec for {bot_file}"}
                bot_mod_obj = importlib.util.module_from_spec(bot_mod_spec)
                bot_mod_spec.loader.exec_module(bot_mod_obj)
                if not hasattr(bot_mod_obj, "BOT_NAME") or not isinstance(bot_mod_obj.BOT_NAME, str) or not bot_mod_obj.BOT_NAME.strip():
                    return {"ok": False, "error": f"{bot_file.name}: BOT_NAME must be non-empty string"}
                payload["bot_name"] = bot_mod_obj.BOT_NAME
            except Exception as e:
                return {"ok": False, "error": f"bot load failed: {type(e).__name__}: {e}"}
            return {"ok": True, "captured": payload}
        except Exception as e:
            return {"ok": False, "error": f"run failed: {type(e).__name__}: {e}"}
    except Exception as e:
        return {"ok": False, "error": f"run failed: {type(e).__name__}: {e}"}

    return {"ok": False, "error": "install() finished without marketplace_upsert_dev_bot"}


def _capture_code_install_metadata_subprocess(workdir: Path, install_py: Path, bot_name: str) -> tuple[dict[str, Any] | None, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "flexus_client_kit.bot_info", "capture-install-meta", "--install-file", str(install_py), "--bot-name", bot_name],
        cwd=str(workdir),
        capture_output=True,
        text=True,
        timeout=45,
    )
    merged = proc.stdout + "\n" + proc.stderr
    payload = _extract_last_json_obj(merged)
    if payload is None:
        tail = merged[-500:].strip()
        return None, f"metadata capture failed for {install_py.name}: {tail or 'no output'}"
    if "ok" not in payload or not payload["ok"]:
        err = payload["error"] if "error" in payload else "unknown capture error"
        return None, f"metadata capture failed for {install_py.name}: {err}"
    if "captured" not in payload or not isinstance(payload["captured"], dict):
        return None, f"metadata capture failed for {install_py.name}: missing captured payload"
    return payload["captured"], ""


def _capture_code_install_metadata(workdir: Path, install_py: Path, bot_name: str) -> tuple[dict[str, Any] | None, str]:
    return _capture_code_install_metadata_subprocess(workdir, install_py, bot_name)


def _existing_avatar_candidates(workdir: Path, bot_abs: Path, rel_candidates: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for rel in rel_candidates:
        cleaned = _normalize_rel_path(rel)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        full = workdir / cleaned
        if full.is_file():
            out.append(cleaned)
    return out


def _avatar_candidates_manifest(workdir: Path, bot_abs: Path, bot_name: str) -> list[str]:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    return _existing_avatar_candidates(workdir, bot_abs, [
        f"{bot_dir}/{bot_name}-256x256.webp",
        f"{bot_dir}/{bot_name}-256x256.png",
        f"{bot_dir}/assets/avatar.svg",
    ])


def _avatar_candidates_code(workdir: Path, bot_abs: Path, install_py: Path, bot_name: str) -> list[str]:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    rels: list[str] = []
    try:
        for line in install_py.read_text().splitlines():
            if "pic_small" not in line:
                continue
            m = _PIC_SMALL_RE.search(line)
            if not m:
                continue
            raw = m.group(1).lstrip("/")
            rels.append(f"{bot_dir}/{raw}")
    except Exception:
        pass
    rels.extend([
        f"{bot_dir}/{bot_name}-256x256.webp",
        f"{bot_dir}/{bot_name}-256x256.png",
        f"{bot_dir}/assets/avatar.svg",
    ])
    return _existing_avatar_candidates(workdir, bot_abs, rels)


def _manifest_metadata_summary(bot_abs: Path, manifest: dict[str, Any], setup_schema: list[dict[str, Any]]) -> dict[str, Any]:
    allowlist = manifest["shared_skills_allowlist"] if "shared_skills_allowlist" in manifest else ""
    skills = ckit_skills.static_skills_find(bot_abs, allowlist)
    integrations = ckit_integrations_db.static_integrations_load(bot_abs, manifest["integrations"], builtin_skills=skills)
    experts = ckit_experts_from_files.discover_experts(bot_abs, skills)

    auth_supported = list(manifest["auth_supported"]) if "auth_supported" in manifest else []
    auth_scopes = dict(manifest["auth_scopes"]) if "auth_scopes" in manifest else {}
    for rec in integrations:
        if rec.integr_provider:
            if rec.integr_provider not in auth_supported:
                auth_supported.append(rec.integr_provider)
            existing = auth_scopes[rec.integr_provider] if rec.integr_provider in auth_scopes else []
            auth_scopes[rec.integr_provider] = list(dict.fromkeys(existing + rec.integr_scopes))

    featured_actions: list[dict[str, Any]] = []
    for x in manifest["featured_actions"]:
        y = dict(x)
        if "feat_depends_on_setup" not in y:
            y["feat_depends_on_setup"] = []
        featured_actions.append(y)

    preferred_default = manifest["preferred_model_default"] if "preferred_model_default" in manifest else ""
    preferred_expensive = manifest["preferred_model_expensive"] if "preferred_model_expensive" in manifest else preferred_default
    preferred_cheap = manifest["preferred_model_cheap"] if "preferred_model_cheap" in manifest else preferred_default

    return {
        "manifest": manifest,
        "setup_schema": setup_schema,
        "skills": skills,
        "integrations": [x.integr_name for x in integrations],
        "experts": [x[0] for x in experts],
        "featured_actions": featured_actions,
        "auth_supported": auth_supported,
        "auth_scopes": auth_scopes,
        "preferred_model_expensive": preferred_expensive,
        "preferred_model_cheap": preferred_cheap,
    }


def _code_metadata_summary(captured: dict[str, Any], bot_name: str) -> dict[str, Any]:
    picked: dict[str, Any] = {}
    for key in [
        "marketable_name",
        "marketable_run_this",
        "marketable_install_cmd",
        "marketable_setup_default",
        "marketable_featured_actions",
        "marketable_auth_supported",
        "marketable_auth_scopes",
        "marketable_tags",
        "marketable_title1",
        "marketable_title2",
        "marketable_github_repo",
        "marketable_intro_message",
        "marketable_preferred_model_expensive",
        "marketable_preferred_model_cheap",
        "marketable_daily_budget_default",
        "marketable_default_inbox_default",
    ]:
        if key in captured:
            picked[key] = captured[key]
    return {
        "bot_name": bot_name,
        "captured_install": picked,
    }


def _manifest_entry(workdir: Path, bot_abs: Path, root_installable: bool, root_install_error: str) -> _InspectResult:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    if not root_installable:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=root_install_error)

    try:
        manifest, setup_schema = no_special_code_bot.load_manifest_and_setup_schema(bot_abs)
    except Exception as e:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"manifest parse failed: {type(e).__name__}: {e}")

    if "bot_name" not in manifest:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="manifest.bot_name is required")
    marketable_name = manifest["bot_name"]
    folder_name = bot_abs.name
    if marketable_name != folder_name:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"name mismatch: folder {folder_name} != manifest.bot_name {marketable_name}")

    manifest_file_path = f"{bot_dir}/manifest.json"
    runtime_start_cmd = f"cd /workspace && python -u -m flexus_client_kit.no_special_code_bot {shlex.quote(bot_dir)}"
    marketable_install_cmd = ""
    publish_install_cmd = _join_publish_install_cmd(marketable_install_cmd)
    avatar_candidates = _avatar_candidates_manifest(workdir, bot_abs, marketable_name)
    avatar_path_small = avatar_candidates[0] if avatar_candidates else ""

    entry = BotInfoEntry(
        bot_dir=bot_dir,
        bot_family="manifest",
        marketable_name=marketable_name,
        runtime_start_cmd=runtime_start_cmd,
        publish_install_cmd=publish_install_cmd,
        marketable_install_cmd=marketable_install_cmd,
        runtime_entry_path=manifest_file_path,
        avatar_path_small=avatar_path_small,
        avatar_candidates=avatar_candidates,
        metadata_summary=_manifest_metadata_summary(bot_abs, manifest, setup_schema),
        manifest_file_path=manifest_file_path,
    )
    return _InspectResult(bot_dir=bot_dir, supported=True, entry=entry)


def _code_entry(workdir: Path, bot_abs: Path, bot_py: Path, install_py: Path, root_installable: bool, root_install_error: str) -> _InspectResult:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    if not root_installable:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=root_install_error)

    folder_name = bot_abs.name

    captured, capture_error = _capture_code_install_metadata(workdir, install_py, folder_name)
    if capture_error:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=capture_error)

    if "bot_name" not in captured or not isinstance(captured["bot_name"], str) or not captured["bot_name"].strip():
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="install capture missing bot_name")
    if captured["bot_name"] != folder_name:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"name mismatch: folder {folder_name} != BOT_NAME {captured['bot_name']}")

    if "marketable_name" not in captured or not isinstance(captured["marketable_name"], str):
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="install capture missing marketable_name")
    if captured["marketable_name"] != folder_name:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"name mismatch: folder {folder_name} != install marketable_name {captured['marketable_name']}")

    if "marketable_run_this" not in captured or not isinstance(captured["marketable_run_this"], str) or not captured["marketable_run_this"].strip():
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="install capture missing marketable_run_this")

    entry_bot_py = _normalize_rel_path(str(bot_py.relative_to(workdir)))
    entry_install_py = _normalize_rel_path(str(install_py.relative_to(workdir)))
    runtime_start_cmd = _normalize_workspace_cmd(captured["marketable_run_this"])

    if "marketable_install_cmd" not in captured or not isinstance(captured["marketable_install_cmd"], str) or not captured["marketable_install_cmd"].strip():
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="install capture missing marketable_install_cmd")

    marketable_install_cmd = captured["marketable_install_cmd"].strip()
    publish_install_cmd = _join_publish_install_cmd(marketable_install_cmd)
    avatar_candidates = _avatar_candidates_code(workdir, bot_abs, install_py, folder_name)
    avatar_path_small = avatar_candidates[0] if avatar_candidates else ""

    entry = BotInfoEntry(
        bot_dir=bot_dir,
        bot_family="code",
        marketable_name=captured["marketable_name"],
        runtime_start_cmd=runtime_start_cmd,
        publish_install_cmd=publish_install_cmd,
        marketable_install_cmd=marketable_install_cmd,
        runtime_entry_path=entry_bot_py,
        avatar_path_small=avatar_path_small,
        avatar_candidates=avatar_candidates,
        metadata_summary=_code_metadata_summary(captured, captured["bot_name"]),
        install_entry_path=entry_install_py,
    )
    return _InspectResult(bot_dir=bot_dir, supported=True, entry=entry)


def _inspect_bot_dir(workdir: Path, bot_abs: Path, root_installable: bool, root_install_error: str) -> _InspectResult:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    if not _BOT_DIR_RE.match(bot_dir):
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="bot_dir must be folder1/bot1")

    manifest_file_path = bot_abs / "manifest.json"
    code_bot_files = sorted([x for x in bot_abs.glob("*_bot.py") if x.is_file()])
    code_install_files = sorted([x for x in bot_abs.glob("*_install.py") if x.is_file()])

    if manifest_file_path.is_file() and code_bot_files:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="manifest bot must not have *_bot.py")

    if manifest_file_path.is_file():
        if code_install_files:
            return _InspectResult(bot_dir=bot_dir, supported=False, reason="manifest bot must not have *_install.py")
        return _manifest_entry(workdir, bot_abs, root_installable, root_install_error)

    if len(code_bot_files) != 1:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="code bot must have exactly one *_bot.py")
    if len(code_install_files) != 1:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="code bot must have exactly one *_install.py")

    bot_stem = code_bot_files[0].name[:-len("_bot.py")]
    install_stem = code_install_files[0].name[:-len("_install.py")]
    if bot_stem != install_stem:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"code bot mismatch: {code_bot_files[0].name} vs {code_install_files[0].name}")

    return _code_entry(workdir, bot_abs, code_bot_files[0], code_install_files[0], root_installable, root_install_error)


def repo_summary(workdir: str | Path) -> dict[str, Any]:
    root = Path(workdir).resolve()
    if not root.is_dir():
        return {"ok": False, "error": f"workdir not found: {root}"}

    root_installable, root_install_error = _check_root_installable(root)
    by_top: dict[str, list[_InspectResult]] = {}
    top_level_counts: dict[str, int] = {}

    top_dirs = sorted([x for x in root.iterdir() if x.is_dir() and not x.name.startswith(".")])
    for top in top_dirs:
        rows: list[_InspectResult] = []
        for bot_abs in sorted([x for x in top.iterdir() if x.is_dir() and not x.name.startswith(".")]):
            rows.append(_inspect_bot_dir(root, bot_abs, root_installable, root_install_error))
        by_top[top.name] = rows
        top_level_counts[top.name] = sum(1 for x in rows if x.supported)

    bots_root_dir = ""
    if top_level_counts:
        best = max(top_level_counts.values())
        if best > 0:
            winners = sorted([k for k, v in top_level_counts.items() if v == best])
            bots_root_dir = winners[0]
    if not bots_root_dir:
        bots_root_dir = "flexus_my_bots"

    bots: list[dict[str, Any]] = []
    unsupported_entries: list[dict[str, str]] = []
    for top_name, rows in by_top.items():
        for row in rows:
            if row.supported and row.entry:
                if top_name == bots_root_dir:
                    bots.append(asdict(row.entry))
                else:
                    unsupported_entries.append({
                        "bot_dir": row.bot_dir,
                        "reason": f"outside selected bots_root_dir={bots_root_dir}",
                    })
                continue
            unsupported_entries.append({
                "bot_dir": row.bot_dir,
                "reason": row.reason,
            })

    bots.sort(key=lambda x: x["bot_dir"])

    return {
        "ok": True,
        "workdir": str(root),
        "bots_root_dir": bots_root_dir,
        "root_installable": root_installable,
        "root_install_error": root_install_error,
        "bots": bots,
        "unsupported_entries": unsupported_entries,
    }


def bot_entry(workdir: str | Path, bot_dir: str) -> dict[str, Any]:
    summary = repo_summary(workdir)
    if not summary["ok"]:
        return summary
    normalized = _normalize_rel_path(bot_dir)
    if not _BOT_DIR_RE.match(normalized):
        return {"ok": False, "error": f"bad bot_dir format: {bot_dir}"}
    for entry in summary["bots"]:
        if entry["bot_dir"] == normalized:
            return {"ok": True, "entry": entry, "summary": summary}
    return {"ok": False, "error": f"bot_dir not found: {normalized}", "summary": summary}


def _bump_code_bot_version(entry_bot_py: Path, bump_type: str) -> tuple[bool, str]:
    if bump_type not in ("patch", "minor", "major"):
        return True, ""

    def bump_version(v, bump):
        parts = list(map(int, v.split(".")))
        while len(parts) < 3:
            parts.append(0)
        if bump == "major":
            parts = [parts[0] + 1, 0, 0]
        elif bump == "minor":
            parts = [parts[0], parts[1] + 1, 0]
        else:
            parts = [parts[0], parts[1], parts[2] + 1]
        return ".".join(map(str, parts))

    runtime_entry_path = str(entry_bot_py)
    bot_content = entry_bot_py.read_text()
    version_file = None
    version_var = None
    old_version = None
    uses_common = re.search(r'^\s*BOT_VERSION\s*=\s*SIMPLE_BOTS_COMMON_VERSION\s*$', bot_content, re.M) is not None
    if uses_common:
        bot_dir = entry_bot_py.parent
        for check in [
            bot_dir / ".." / "version_common.py",
            bot_dir / "version_common.py",
            Path("flexus_simple_bots/version_common.py"),
        ]:
            check = check.resolve()
            if check.exists():
                version_file = check
                version_var = "SIMPLE_BOTS_COMMON_VERSION"
                break
        if version_file is None:
            return False, "Bot uses SIMPLE_BOTS_COMMON_VERSION but version_common.py not found"
    else:
        m = re.search(r'BOT_VERSION\s*=\s*["\']([0-9]+\.[0-9]+(?:\.[0-9]+)?)["\']', bot_content)
        if not m:
            return False, f"Could not find BOT_VERSION in {runtime_entry_path}"
        version_file = entry_bot_py
        version_var = "BOT_VERSION"
        old_version = m.group(1)

    if old_version is None:
        content = version_file.read_text()
        m = re.search(rf'{version_var}\s*=\s*["\']([0-9]+\.[0-9]+(?:\.[0-9]+)?)["\']', content)
        if not m:
            return False, f"Could not find {version_var} in {version_file}"
        old_version = m.group(1)

    new_version = bump_version(old_version, bump_type)
    content = version_file.read_text()
    new_content = re.sub(
        rf'({version_var}\s*=\s*["\'])([0-9]+\.[0-9]+(?:\.[0-9]+)?)(["\'])',
        rf'\g<1>{new_version}\g<3>',
        content,
    )
    version_file.write_text(new_content)
    return True, f"Version: {old_version} -> {new_version}\nUpdated {version_var} in {version_file}"


def _run_install_here(workdir: Path, bot_dir: str, bump: str | None) -> dict[str, Any]:
    info = bot_entry(workdir, bot_dir)
    if not info["ok"]:
        return info
    entry = info["entry"]
    os.chdir(workdir)

    if not ((workdir / "setup.py").exists() or (workdir / "pyproject.toml").exists()):
        return {"ok": False, "error": "root setup.py or pyproject.toml is required"}

    logs: list[str] = []
    if entry["bot_family"] == "manifest":
        manifest_path = workdir / entry["manifest_file_path"]
        if not manifest_path.exists():
            return {"ok": False, "error": f"manifest.json not found in {bot_dir}"}
    else:
        entry_bot_py = workdir / entry["runtime_entry_path"]
        if not entry_bot_py.exists():
            return {"ok": False, "error": f"Bot file not found: {entry['runtime_entry_path']}"}
        ok, msg = _bump_code_bot_version(entry_bot_py, bump or "")
        if not ok:
            return {"ok": False, "error": msg}
        if msg:
            logs.append(msg)

    logs.append("---\nInstalling package from repo root...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().split("\n") if (r.stdout or r.stderr) else []
    logs.extend([x for x in out[-20:] if x])
    if r.returncode != 0:
        logs.append(f"pip install failed with code {r.returncode}")
        return {"ok": False, "error": "pip install failed", "output": "\n".join(logs)}
    logs.append("Package installed")

    marketable_install_cmd = entry["marketable_install_cmd"] if entry["marketable_install_cmd"].strip() else ""
    stripped_install_cmd = _strip_workspace_prefix(marketable_install_cmd)
    if stripped_install_cmd and stripped_install_cmd != "python -m pip install -e .":
        if not os.environ.get("FLEXUS_WORKSPACE", ""):
            logs.append("---\nFLEXUS_WORKSPACE not set, skipping marketable_install_cmd")
        else:
            logs.append(f"---\nRunning marketable_install_cmd: {marketable_install_cmd}")
            r = subprocess.run(marketable_install_cmd, capture_output=True, text=True, shell=True)
            if r.stdout:
                logs.append(r.stdout.rstrip())
            if r.stderr:
                logs.append(r.stderr.rstrip())
            if r.returncode != 0:
                logs.append(f"marketable_install_cmd failed with code {r.returncode}")
                return {"ok": False, "error": "marketable_install_cmd failed", "output": "\n".join(logs)}
            logs.append("Install command completed")

    logs.append("---\nInstall complete")
    return {"ok": True, "output": "\n".join(logs), "entry": entry}


def _bump_version_here(workdir: Path, bot_dir: str, bump: str | None) -> dict[str, Any]:
    info = bot_entry(workdir, bot_dir)
    if not info["ok"]:
        return info
    entry = info["entry"]
    if entry["bot_family"] != "code":
        return {"ok": True, "output": "", "entry": entry}
    entry_bot_py = workdir / entry["runtime_entry_path"]
    if not entry_bot_py.exists():
        return {"ok": False, "error": f"Bot file not found: {entry['runtime_entry_path']}"}
    ok, msg = _bump_code_bot_version(entry_bot_py, bump or "")
    if not ok:
        return {"ok": False, "error": msg}
    return {"ok": True, "output": msg, "entry": entry}


def build_install_cmd(entry: dict[str, Any], bump: str | None = None) -> tuple[str, str]:
    if "bot_family" not in entry or "bot_dir" not in entry:
        return "", "bad entry payload"
    cmds: list[str] = []
    if entry["bot_family"] == "code" and bump in ("patch", "minor", "major"):
        bump_args = [
            sys.executable,
            "-m",
            "flexus_client_kit.bot_info",
            "bump-version",
            "--workdir",
            "/workspace",
            "--bot-dir",
            entry["bot_dir"],
            "--bump",
            bump,
        ]
        cmds.append(" ".join(shlex.quote(x) for x in bump_args) + " >/tmp/flexus_bot_install_bump.log 2>&1 || (cat /tmp/flexus_bot_install_bump.log; exit 1)")
    cmds.append("cd /workspace && python -m pip install -e .")
    install_cmd = _strip_workspace_prefix(entry["marketable_install_cmd"])
    if install_cmd:
        if install_cmd != "python -m pip install -e .":
            cmds.append(install_cmd)
    return " && ".join(cmds) + " 2>&1", ""


def install_cmd(workdir: str | Path, bot_dir: str, bump: str | None = None) -> dict[str, Any]:
    info = bot_entry(workdir, bot_dir)
    if not info["ok"]:
        return info
    entry = info["entry"]
    cmd, err = build_install_cmd(entry, bump)
    if err:
        return {"ok": False, "error": err}
    return {
        "ok": True,
        "bot_dir": entry["bot_dir"],
        "marketable_name": entry["marketable_name"],
        "install_cmd": cmd,
        "entry": entry,
    }


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="op", required=True)

    p_repo = sub.add_parser("repo-summary")
    p_repo.add_argument("--workdir", default="/workspace")

    p_entry = sub.add_parser("bot-entry")
    p_entry.add_argument("--workdir", default="/workspace")
    p_entry.add_argument("--bot-dir", required=True)

    p_install = sub.add_parser("install-cmd")
    p_install.add_argument("--workdir", default="/workspace")
    p_install.add_argument("--bot-dir", required=True)
    p_install.add_argument("--bump", default="")

    p_capture = sub.add_parser("capture-install-meta")
    p_capture.add_argument("--install-file", required=True)
    p_capture.add_argument("--bot-name", required=True)

    p_run_install = sub.add_parser("run-install")
    p_run_install.add_argument("--workdir", default="/workspace")
    p_run_install.add_argument("--bot-dir", required=True)
    p_run_install.add_argument("--bump", default="")

    p_bump_version = sub.add_parser("bump-version")
    p_bump_version.add_argument("--workdir", default="/workspace")
    p_bump_version.add_argument("--bot-dir", required=True)
    p_bump_version.add_argument("--bump", default="")

    args = parser.parse_args()

    if args.op == "repo-summary":
        _print_json(repo_summary(args.workdir))
        return 0

    if args.op == "bot-entry":
        _print_json(bot_entry(args.workdir, args.bot_dir))
        return 0

    if args.op == "install-cmd":
        bump = args.bump if args.bump in ("patch", "minor", "major") else None
        _print_json(install_cmd(args.workdir, args.bot_dir, bump=bump))
        return 0

    if args.op == "capture-install-meta":
        _print_json(_capture_install_metadata_here(Path(args.install_file).resolve(), args.bot_name))
        return 0

    if args.op == "run-install":
        bump = args.bump if args.bump in ("patch", "minor", "major") else None
        _print_json(_run_install_here(Path(args.workdir).resolve(), args.bot_dir, bump))
        return 0

    if args.op == "bump-version":
        bump = args.bump if args.bump in ("patch", "minor", "major") else None
        _print_json(_bump_version_here(Path(args.workdir).resolve(), args.bot_dir, bump))
        return 0

    _print_json({"ok": False, "error": f"unknown op: {args.op}"})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

