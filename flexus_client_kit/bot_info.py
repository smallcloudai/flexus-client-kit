import ast
import argparse
import json
import re
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from flexus_client_kit import ckit_experts_from_files
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import no_special_code_bot

_BOT_DIR_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._\-]*/[A-Za-z0-9_][A-Za-z0-9._\-]*$")
_PIC_SMALL_RE = re.compile(r"[\"'(/]([^\"' ()]+\.(?:webp|png|jpg|jpeg|svg))[\"')\s]")


@dataclass
class BotInfoEntry:
    bot_dir: str
    bot_family: str
    marketable_name: str
    runtime_start_cmd: str
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


def _placeholder_entry(workdir: Path, bot_abs: Path, manifest_file_path: Path, code_bot_files: list[Path], code_install_files: list[Path]) -> BotInfoEntry:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    runtime_entry_path = _normalize_rel_path(str(code_bot_files[0].relative_to(workdir))) if len(code_bot_files) == 1 else ""
    install_entry_path = _normalize_rel_path(str(code_install_files[0].relative_to(workdir))) if len(code_install_files) == 1 else ""
    manifest_rel = _normalize_rel_path(str(manifest_file_path.relative_to(workdir))) if manifest_file_path.is_file() else ""
    return BotInfoEntry(
        bot_dir=bot_dir,
        bot_family="manifest" if manifest_rel else "code",
        marketable_name=bot_abs.name,
        runtime_start_cmd="",
        runtime_entry_path=runtime_entry_path or manifest_rel,
        avatar_path_small="",
        avatar_candidates=[],
        metadata_summary={},
        install_entry_path=install_entry_path,
        manifest_file_path=manifest_rel,
    )


def _normalize_workspace_cmd(command: str) -> str:
    cmd = command.strip()
    if cmd.startswith("python -m pip"):
        cmd = "python3 -m pip" + cmd[len("python -m pip"):]
    elif cmd.startswith("python -u -m"):
        cmd = "python3 -u -m" + cmd[len("python -u -m"):]
    elif cmd.startswith("python -m"):
        cmd = "python3 -m" + cmd[len("python -m"):]
    if cmd.startswith("cd /workspace"):
        return cmd
    return f"cd /workspace && {cmd}"


def _check_root_installable(workdir: Path) -> tuple[bool, str]:
    if (workdir / "setup.py").is_file() or (workdir / "pyproject.toml").is_file():
        return True, ""
    return False, "repo root must contain setup.py or pyproject.toml"


_CAPTURE_KEYS = [
    "marketable_name",
    "marketable_run_this",
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


@dataclass
class _AstModule:
    path: Path
    bindings: dict[str, ast.AST]
    imports: dict[str, str]


@dataclass(frozen=True)
class _ModuleRef:
    module_name: str


_UNRESOLVED = object()
_AST_MODULE_CACHE: dict[Path, _AstModule] = {}


def _module_file_from_import(workdir: Path, module_name: str) -> Path | None:
    rel = Path(*module_name.split("."))
    py_path = workdir / f"{rel}.py"
    if py_path.is_file():
        return py_path
    init_path = workdir / rel / "__init__.py"
    if init_path.is_file():
        return init_path
    return None


def _load_ast_module(path: Path) -> _AstModule:
    path = path.resolve()
    if path in _AST_MODULE_CACHE:
        return _AST_MODULE_CACHE[path]
    tree = ast.parse(path.read_text(), filename=str(path))
    bindings: dict[str, ast.AST] = {}
    imports: dict[str, str] = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module:
            for alias in stmt.names:
                imports[alias.asname or alias.name] = f"{stmt.module}.{alias.name}"
        elif isinstance(stmt, ast.Import):
            for alias in stmt.names:
                if alias.asname:
                    imports[alias.asname] = alias.name
                elif "." not in alias.name:
                    imports[alias.name] = alias.name
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    bindings[target.id] = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
            bindings[stmt.target.id] = stmt.value
    mod = _AstModule(path=path, bindings=bindings, imports=imports)
    _AST_MODULE_CACHE[path] = mod
    return mod


def _eval_ast_node(workdir: Path, mod: _AstModule, node: ast.AST, special_names: dict[str, Any], seen: set[tuple[Path, str]]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        if node.id in special_names:
            return special_names[node.id]
        if node.id in mod.bindings:
            key = (mod.path, node.id)
            if key in seen:
                return _UNRESOLVED
            return _eval_ast_node(workdir, mod, mod.bindings[node.id], special_names, seen | {key})
        if node.id in mod.imports:
            return _ModuleRef(mod.imports[node.id])
        return _UNRESOLVED

    if isinstance(node, ast.Attribute):
        base = _eval_ast_node(workdir, mod, node.value, special_names, seen)
        if isinstance(base, _ModuleRef):
            target_path = _module_file_from_import(workdir, base.module_name)
            if target_path is None:
                return _UNRESOLVED
            target_mod = _load_ast_module(target_path)
            if node.attr not in target_mod.bindings:
                return _UNRESOLVED
            key = (target_mod.path, node.attr)
            if key in seen:
                return _UNRESOLVED
            return _eval_ast_node(workdir, target_mod, target_mod.bindings[node.attr], special_names, seen | {key})
        return _UNRESOLVED

    if isinstance(node, ast.List):
        items = []
        for elt in node.elts:
            value = _eval_ast_node(workdir, mod, elt, special_names, seen)
            if value is _UNRESOLVED:
                return _UNRESOLVED
            items.append(value)
        return items

    if isinstance(node, ast.Tuple):
        items = []
        for elt in node.elts:
            value = _eval_ast_node(workdir, mod, elt, special_names, seen)
            if value is _UNRESOLVED:
                return _UNRESOLVED
            items.append(value)
        return items

    if isinstance(node, ast.Set):
        items = []
        for elt in node.elts:
            value = _eval_ast_node(workdir, mod, elt, special_names, seen)
            if value is _UNRESOLVED:
                return _UNRESOLVED
            items.append(value)
        return items

    if isinstance(node, ast.Dict):
        out: dict[str, Any] = {}
        for key_node, value_node in zip(node.keys, node.values):
            if key_node is None:
                extra = _eval_ast_node(workdir, mod, value_node, special_names, seen)
                if not isinstance(extra, dict):
                    return _UNRESOLVED
                for k, v in extra.items():
                    out[str(k)] = v
                continue
            key = _eval_ast_node(workdir, mod, key_node, special_names, seen)
            value = _eval_ast_node(workdir, mod, value_node, special_names, seen)
            if key is _UNRESOLVED or value is _UNRESOLVED:
                return _UNRESOLVED
            out[str(key)] = value
        return out

    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value_node in node.values:
            if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                parts.append(value_node.value)
                continue
            if isinstance(value_node, ast.FormattedValue):
                value = _eval_ast_node(workdir, mod, value_node.value, special_names, seen)
                if value is _UNRESOLVED:
                    return _UNRESOLVED
                parts.append(str(value))
                continue
            return _UNRESOLVED
        return "".join(parts)

    if isinstance(node, ast.BinOp):
        left = _eval_ast_node(workdir, mod, node.left, special_names, seen)
        right = _eval_ast_node(workdir, mod, node.right, special_names, seen)
        if left is _UNRESOLVED or right is _UNRESOLVED:
            return _UNRESOLVED
        if isinstance(node.op, ast.Add):
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
        if isinstance(node.op, ast.BitOr) and isinstance(left, dict) and isinstance(right, dict):
            return left | right
        return _UNRESOLVED

    if isinstance(node, ast.UnaryOp):
        value = _eval_ast_node(workdir, mod, node.operand, special_names, seen)
        if value is _UNRESOLVED:
            return _UNRESOLVED
        if isinstance(node.op, ast.USub) and isinstance(value, (int, float)):
            return -value
        if isinstance(node.op, ast.UAdd) and isinstance(value, (int, float)):
            return +value
        return _UNRESOLVED

    return _UNRESOLVED


def _marketplace_upsert_call(tree: ast.AST) -> ast.Call | None:
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "marketplace_upsert_dev_bot":
            calls.append(node)
        elif isinstance(func, ast.Attribute) and func.attr == "marketplace_upsert_dev_bot":
            calls.append(node)
    if not calls:
        return None
    return max(calls, key=lambda x: sum(1 for kw in x.keywords if kw.arg in _CAPTURE_KEYS))


def _bot_name_from_bot_file(bot_file: Path) -> tuple[str | None, str | None]:
    try:
        mod = _load_ast_module(bot_file)
    except Exception as e:
        return None, f"bot parse failed: {type(e).__name__}: {e}"
    if "BOT_NAME" not in mod.bindings:
        return None, f"{bot_file.name}: BOT_NAME must be non-empty string"
    value = _eval_ast_node(bot_file.parent.parent.parent.resolve(), mod, mod.bindings["BOT_NAME"], {}, set())
    if not isinstance(value, str) or not value.strip():
        return None, f"{bot_file.name}: BOT_NAME must be non-empty string"
    return value, None


def _capture_install_metadata_ast(workdir: Path, install_file: Path, bot_name: str) -> dict[str, Any]:
    try:
        mod = _load_ast_module(install_file)
    except Exception as e:
        return {"ok": False, "error": f"parse failed: {type(e).__name__}: {e}"}

    call = _marketplace_upsert_call(ast.parse(install_file.read_text(), filename=str(install_file)))
    if call is None:
        return {"ok": False, "error": "marketplace_upsert_dev_bot() call not found"}

    payload = {}
    for kw in call.keywords:
        if kw.arg not in _CAPTURE_KEYS:
            continue
        value = _eval_ast_node(workdir, mod, kw.value, {"bot_name": bot_name}, set())
        if value is not _UNRESOLVED:
            payload[kw.arg] = _jsonable(value)
    return {"ok": True, "captured": payload}


def _capture_install_metadata_here(install_file: Path, bot_name: str) -> dict[str, Any]:
    return _capture_install_metadata_ast(install_file.parent.parent.parent.resolve(), install_file.resolve(), bot_name)


def _capture_code_install_metadata(workdir: Path, install_py: Path, bot_name: str) -> tuple[dict[str, Any] | None, str]:
    payload = _capture_install_metadata_ast(workdir.resolve(), install_py.resolve(), bot_name)
    if "ok" not in payload or not payload["ok"]:
        err = payload["error"] if "error" in payload else "unknown capture error"
        return None, f"metadata capture failed for {install_py.name}: {err}"
    if "captured" not in payload or not isinstance(payload["captured"], dict):
        return None, f"metadata capture failed for {install_py.name}: missing captured payload"
    return payload["captured"], ""


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
    runtime_start_cmd = f"cd /workspace && python3 -u -m flexus_client_kit.no_special_code_bot {shlex.quote(bot_dir)}"
    avatar_candidates = _avatar_candidates_manifest(workdir, bot_abs, marketable_name)
    avatar_path_small = avatar_candidates[0] if avatar_candidates else ""

    entry = BotInfoEntry(
        bot_dir=bot_dir,
        bot_family="manifest",
        marketable_name=marketable_name,
        runtime_start_cmd=runtime_start_cmd,
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

    bot_name_from_file, bot_name_error = _bot_name_from_bot_file(bot_py)
    if bot_name_error:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=bot_name_error)
    if bot_name_from_file != folder_name:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"name mismatch: folder {folder_name} != BOT_NAME {bot_name_from_file}")

    if "marketable_run_this" not in captured or not isinstance(captured["marketable_run_this"], str) or not captured["marketable_run_this"].strip():
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="install capture missing marketable_run_this")

    marketable_name = captured["marketable_name"] if "marketable_name" in captured and isinstance(captured["marketable_name"], str) and captured["marketable_name"].strip() else bot_name_from_file or folder_name
    if marketable_name != folder_name:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"name mismatch: folder {folder_name} != install marketable_name {marketable_name}")

    entry_bot_py = _normalize_rel_path(str(bot_py.relative_to(workdir)))
    entry_install_py = _normalize_rel_path(str(install_py.relative_to(workdir)))
    runtime_start_cmd = _normalize_workspace_cmd(captured["marketable_run_this"])

    avatar_candidates = _avatar_candidates_code(workdir, bot_abs, install_py, folder_name)
    avatar_path_small = avatar_candidates[0] if avatar_candidates else ""

    entry = BotInfoEntry(
        bot_dir=bot_dir,
        bot_family="code",
        marketable_name=marketable_name,
        runtime_start_cmd=runtime_start_cmd,
        runtime_entry_path=entry_bot_py,
        avatar_path_small=avatar_path_small,
        avatar_candidates=avatar_candidates,
        metadata_summary=_code_metadata_summary(captured, bot_name_from_file),
        install_entry_path=entry_install_py,
    )
    return _InspectResult(bot_dir=bot_dir, supported=True, entry=entry)


def _inspect_bot_dir(workdir: Path, bot_abs: Path, root_installable: bool, root_install_error: str) -> _InspectResult:
    bot_dir = _normalize_rel_path(str(bot_abs.relative_to(workdir)))
    manifest_file_path = bot_abs / "manifest.json"
    code_bot_files = sorted([x for x in bot_abs.glob("*_bot.py") if x.is_file()])
    code_install_files = sorted([x for x in bot_abs.glob("*_install.py") if x.is_file()])
    if not manifest_file_path.is_file() and len(code_bot_files) == 0 and len(code_install_files) == 0:
        return _InspectResult(bot_dir=bot_dir, supported=False)
    placeholder = _placeholder_entry(workdir, bot_abs, manifest_file_path, code_bot_files, code_install_files)

    if not _BOT_DIR_RE.match(bot_dir):
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="bot_dir must be folder1/bot1", entry=placeholder)

    if manifest_file_path.is_file() and code_bot_files:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="manifest bot must not have *_bot.py", entry=placeholder)

    if manifest_file_path.is_file():
        if code_install_files:
            return _InspectResult(bot_dir=bot_dir, supported=False, reason="manifest bot must not have *_install.py", entry=placeholder)
        result = _manifest_entry(workdir, bot_abs, root_installable, root_install_error)
        if result.entry is None:
            result.entry = placeholder
        return result

    if len(code_bot_files) != 1:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="code bot must have exactly one *_bot.py", entry=placeholder)
    if len(code_install_files) != 1:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason="code bot must have exactly one *_install.py", entry=placeholder)

    bot_stem = code_bot_files[0].name[:-len("_bot.py")]
    install_stem = code_install_files[0].name[:-len("_install.py")]
    if bot_stem != install_stem:
        return _InspectResult(bot_dir=bot_dir, supported=False, reason=f"code bot mismatch: {code_bot_files[0].name} vs {code_install_files[0].name}", entry=placeholder)

    result = _code_entry(workdir, bot_abs, code_bot_files[0], code_install_files[0], root_installable, root_install_error)
    if result.entry is None:
        result.entry = placeholder
    return result


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
            if not row.supported and not row.reason and row.entry is None:
                continue
            if row.supported and row.entry:
                bots.append(asdict(row.entry))
                continue
            unsupported_entries.append({
                "bot_dir": row.bot_dir,
                "reason": row.reason,
                "marketable_name": row.entry.marketable_name if row.entry else row.bot_dir.rsplit("/", 1)[-1],
                "bot_family": row.entry.bot_family if row.entry else "code",
                "runtime_entry_path": row.entry.runtime_entry_path if row.entry else "",
                "install_entry_path": row.entry.install_entry_path if row.entry else "",
                "manifest_file_path": row.entry.manifest_file_path if row.entry else "",
                "avatar_path_small": row.entry.avatar_path_small if row.entry else "",
                "metadata_summary": row.entry.metadata_summary if row.entry else {},
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
    for entry in summary["unsupported_entries"]:
        if entry["bot_dir"] == normalized:
            return {"ok": False, "error": entry["reason"], "summary": summary}
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

    p_capture = sub.add_parser("capture-install-meta")
    p_capture.add_argument("--install-file", required=True)
    p_capture.add_argument("--bot-name", required=True)

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

    if args.op == "capture-install-meta":
        _print_json(_capture_install_metadata_here(Path(args.install_file).resolve(), args.bot_name))
        return 0

    if args.op == "bump-version":
        bump = args.bump if args.bump in ("patch", "minor", "major") else None
        _print_json(_bump_version_here(Path(args.workdir).resolve(), args.bot_dir, bump))
        return 0

    _print_json({"ok": False, "error": f"unknown op: {args.op}"})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

