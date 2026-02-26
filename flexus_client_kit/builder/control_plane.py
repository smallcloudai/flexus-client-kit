import json
import re
from pathlib import Path
from typing import Any

import jsonschema

from flexus_client_kit.builder import bot_registry_engine
from flexus_client_kit.runtime import no_special_code_bot


_METHOD_ID_RE = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)+\.v[0-9]+$")
_METHOD_ID_SCAN_RE = re.compile(r"[a-z0-9_]+(?:\.[a-z0-9_]+){2,}\.v[0-9]+")
MANAGED_PATH_PATTERNS = [
    "manifest.json",
    "setup_schema.json",
    "README.md",
    "prompts/personality.md",
    "prompts/expert_*.md",
    "prompts/skill_*.md",
]
CUSTOM_ZONE_REL = "custom"


def _issue(
    issues: list[dict[str, str]],
    severity: str,
    scope: str,
    code: str,
    message: str,
    hint: str = "",
) -> None:
    try:
        issues.append({
            "severity": severity,
            "scope": scope,
            "code": code,
            "message": message,
            "hint": hint,
        })
    except Exception as e:
        raise RuntimeError(f"Cannot append issue {code}: {e}") from e


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise RuntimeError(f"Missing file: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Cannot read file {path}: {e}") from e


def _discover_integration_files(repo_root: Path) -> list[Path]:
    try:
        base = repo_root / "flexus_client_kit" / "integrations" / "providers"
        if not base.exists():
            return []
        return sorted(base.rglob("fi_*.py"))
    except OSError as e:
        raise RuntimeError(f"Cannot scan integration files: {e}") from e


def _discover_generated_bot_configs(repo_root: Path) -> list[Path]:
    try:
        base = repo_root / "flexus_simple_bots" / "bot_configs"
        if not base.exists():
            return []
        return sorted(base.glob("*.bot.json"))
    except OSError as e:
        raise RuntimeError(f"Cannot scan generated bot configs: {e}") from e


def _extract_method_ids_from_text(text: str) -> list[str]:
    try:
        xs = _METHOD_ID_SCAN_RE.findall(text)
        out: list[str] = []
        for x in xs:
            if x not in out:
                out.append(x)
        return out
    except Exception as e:
        raise RuntimeError(f"Cannot extract method ids from text: {e}") from e


def _safe_read_text_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise RuntimeError(f"UTF-8 decode failed for {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Cannot read text file {path}: {e}") from e


def _integration_key_from_rel(rel_path: str) -> str:
    try:
        return rel_path.replace("\\", "/").replace("/", "__").replace(".py", "")
    except Exception as e:
        raise RuntimeError(f"Cannot build integration key for {rel_path}: {e}") from e


def _integration_rel_from_key(key: str) -> str:
    try:
        return key.replace("__", "/") + ".py"
    except Exception as e:
        raise RuntimeError(f"Cannot build integration rel path for {key}: {e}") from e


def _check_bot_assets(
    issues: list[dict[str, str]],
    bot_id: str,
    bot_name: str,
    output_dir: Path,
) -> None:
    try:
        big = output_dir / f"{bot_name}-1024x1536.webp"
        small_webp = output_dir / f"{bot_name}-256x256.webp"
        small_png = output_dir / f"{bot_name}-256x256.png"
        if not big.exists():
            _issue(
                issues,
                "warning",
                f"bot:{bot_id}",
                "missing_picture_big",
                f"Missing big image: {big}",
                "Add 1024x1536 webp for better marketplace presentation.",
            )
        if not small_webp.exists() and not small_png.exists():
            _issue(
                issues,
                "warning",
                f"bot:{bot_id}",
                "missing_picture_small",
                f"Missing small image: {small_webp} or {small_png}",
                "Add 256x256 image for cards and compact UI surfaces.",
            )
    except Exception as e:
        raise RuntimeError(f"Cannot validate assets for {bot_id}: {e}") from e


def _check_tool_contracts(
    issues: list[dict[str, str]],
    bot_id: str,
    cfg: dict[str, Any],
) -> None:
    try:
        tools = list(cfg.get("tools", []))
        tool_catalog = cfg.get("tool_catalog", {})
        if not isinstance(tool_catalog, dict):
            _issue(
                issues,
                "error",
                f"bot:{bot_id}",
                "tool_catalog_not_object",
                "tool_catalog must be an object",
                "Fix bot config shape for tool catalog.",
            )
            return

        for t in tools:
            if t.startswith("signal_") and t not in tool_catalog:
                _issue(
                    issues,
                    "warning",
                    f"bot:{bot_id}",
                    "tool_catalog_missing_entry",
                    f"Tool {t!r} is used but missing in tool_catalog",
                    "Add integration_mode/apis/method_ids for governance.",
                )

        for t in tool_catalog.keys():
            if t not in tools:
                _issue(
                    issues,
                    "warning",
                    f"bot:{bot_id}",
                    "tool_catalog_orphan_entry",
                    f"tool_catalog contains {t!r} which is absent in tools[]",
                    "Remove orphan entry or include tool in tools[] explicitly.",
                )

        for t, meta in tool_catalog.items():
            if not isinstance(meta, dict):
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "tool_catalog_entry_not_object",
                    f"tool_catalog[{t!r}] must be an object",
                )
                continue
            method_ids = meta.get("method_ids", [])
            if not isinstance(method_ids, list):
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "tool_catalog_method_ids_not_array",
                    f"tool_catalog[{t!r}].method_ids must be array",
                )
                continue
            for mid in method_ids:
                if not isinstance(mid, str) or not _METHOD_ID_RE.match(mid):
                    _issue(
                        issues,
                        "warning",
                        f"bot:{bot_id}",
                        "method_id_pattern_warning",
                        f"Unexpected method_id format in {t!r}: {mid!r}",
                        "Expected dotted id with version suffix like provider.group.method.v1",
                    )
    except Exception as e:
        raise RuntimeError(f"Cannot validate tool contracts for {bot_id}: {e}") from e


def _check_required_tool_prompts(
    issues: list[dict[str, str]],
    bot_id: str,
    cfg: dict[str, Any],
    output_dir: Path,
) -> None:
    try:
        required = cfg.get("required_tool_prompt_files", [])
        if not required:
            return
        if not isinstance(required, list):
            _issue(
                issues,
                "error",
                f"bot:{bot_id}",
                "required_tool_prompt_files_not_array",
                "required_tool_prompt_files must be an array of paths",
            )
            return
        for rel_path in required:
            if not isinstance(rel_path, str) or not rel_path.strip():
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "required_tool_prompt_invalid_path",
                    f"Invalid required prompt path: {rel_path!r}",
                )
                continue
            p = output_dir / rel_path
            if not p.exists():
                _issue(
                    issues,
                    "warning",
                    f"bot:{bot_id}",
                    "required_tool_prompt_missing",
                    f"Required prompt file not found: {p}",
                    "Generate file or adjust required_tool_prompt_files list.",
                )
    except Exception as e:
        raise RuntimeError(f"Cannot validate required tool prompts for {bot_id}: {e}") from e


def _check_tools_registered(
    issues: list[dict[str, str]],
    bot_id: str,
    cfg: dict[str, Any],
) -> None:
    try:
        known = set(no_special_code_bot.TOOL_REGISTRY.keys())
        for t in cfg.get("tools", []):
            if t not in known:
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "tool_not_registered",
                    f"Tool {t!r} is not in runtime TOOL_REGISTRY",
                    "Implement and register tool handler in runtime before production launch.",
                )
    except Exception as e:
        raise RuntimeError(f"Cannot validate tool registration for {bot_id}: {e}") from e


def build_control_plane_report(registry_path: Path) -> dict[str, Any]:
    try:
        reg, repo_root = bot_registry_engine.load_registry(registry_path)
        issues: list[dict[str, str]] = []
        bots_report: list[dict[str, Any]] = []
        integration_files = _discover_integration_files(repo_root)
        all_generated_bot_cfgs = _discover_generated_bot_configs(repo_root)
        tool_registry_names = sorted(list(no_special_code_bot.TOOL_REGISTRY.keys()))
        registered_bot_cfgs: set[str] = set()

        for item in reg["bots"]:
            bot_id = str(item["bot_id"])
            bot_json_path = bot_registry_engine._resolve_input_path(item["bot_json_path"], registry_path.parent, repo_root)
            output_dir = bot_registry_engine._resolve_input_path(item["output_dir"], registry_path.parent, repo_root)
            registered_bot_cfgs.add(str(bot_json_path.resolve()))

            bot_state: dict[str, Any] = {
                "bot_id": bot_id,
                "enabled": bool(item.get("enabled", False)),
                "bot_json_path": str(bot_json_path),
                "output_dir": str(output_dir),
                "json_exists": bot_json_path.exists(),
                "output_exists": output_dir.exists(),
                "schema_ok": False,
                "runtime_ok": False,
                "tools_total": 0,
                "experts_total": 0,
                "skills_total": 0,
            }

            if not bot_json_path.exists():
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "missing_bot_json",
                    f"Bot config file not found: {bot_json_path}",
                )
                bots_report.append(bot_state)
                continue

            cfg = _safe_read_json(bot_json_path)
            bot_state["tools_total"] = len(cfg.get("tools", []))
            bot_state["experts_total"] = len(cfg.get("experts", []))
            bot_state["skills_total"] = len(cfg.get("skills", []))

            try:
                jsonschema.validate(cfg, bot_registry_engine.BOT_CONFIG_SCHEMA)
                bot_state["schema_ok"] = True
            except jsonschema.ValidationError as e:
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "bot_schema_invalid",
                    f"Schema validation failed: {e.message}",
                )

            try:
                bot_registry_engine._validate_bot_config(cfg, bot_json_path)
                bot_state["runtime_ok"] = True
            except RuntimeError as e:
                _issue(
                    issues,
                    "error",
                    f"bot:{bot_id}",
                    "bot_runtime_invalid",
                    str(e),
                )

            _check_tools_registered(issues, bot_id, cfg)
            _check_tool_contracts(issues, bot_id, cfg)
            _check_required_tool_prompts(issues, bot_id, cfg, output_dir)
            _check_bot_assets(issues, bot_id, str(cfg.get("bot_name", bot_id)), output_dir)
            bots_report.append(bot_state)

        unregistered_bot_cfgs = [p for p in all_generated_bot_cfgs if str(p.resolve()) not in registered_bot_cfgs]
        for p in unregistered_bot_cfgs:
            _issue(
                issues,
                "warning",
                "registry",
                "unregistered_bot_config",
                f"Generated bot config is not in registry: {p}",
                "Add entry to bots_registry.json if bot should be managed by UI build flow.",
            )

        summary = {
            "bots_total": len(reg["bots"]),
            "bots_enabled": len([x for x in reg["bots"] if x.get("enabled")]),
            "tool_registry_total": len(tool_registry_names),
            "integrations_total": len(integration_files),
            "generated_bot_configs_total": len(all_generated_bot_cfgs),
            "unregistered_bot_configs_total": len(unregistered_bot_cfgs),
            "issues_total": len(issues),
            "errors_total": len([x for x in issues if x["severity"] == "error"]),
            "warnings_total": len([x for x in issues if x["severity"] == "warning"]),
        }
        return {
            "registry_path": str(registry_path),
            "repo_root": str(repo_root),
            "summary": summary,
            "tool_registry": tool_registry_names,
            "integration_files": [str(x) for x in integration_files],
            "bots": bots_report,
            "issues": issues,
        }
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Cannot build control plane report: {e}") from e


def build_integrations_inventory(registry_path: Path) -> dict[str, Any]:
    try:
        reg, repo_root = bot_registry_engine.load_registry(registry_path)
        files = _discover_integration_files(repo_root)
        items: list[dict[str, Any]] = []
        issues: list[dict[str, str]] = []
        for p in files:
            rel = str(p.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
            try:
                txt = _safe_read_text_utf8(p)
            except RuntimeError as e:
                _issue(
                    issues,
                    "error",
                    f"integration:{rel}",
                    "integration_file_decode_error",
                    str(e),
                    "Save integration file as UTF-8.",
                )
                items.append({
                    "key": _integration_key_from_rel(rel),
                    "path": rel,
                    "name": p.stem,
                    "method_ids": [],
                    "method_ids_total": 0,
                    "has_describe_methods": False,
                    "has_call": False,
                    "has_auth_status": False,
                    "has_base_integration": False,
                    "validation_score_0_3": 0,
                    "read_ok": False,
                })
                continue
            method_ids = _extract_method_ids_from_text(txt)
            has_describe_methods = "def describe_methods" in txt
            has_call = "def call(" in txt or "async def call(" in txt
            has_auth_status = "def auth_status" in txt or "async def auth_status" in txt
            has_base_integration = "BaseIntegration" in txt
            validation_score = int(has_describe_methods) + int(has_auth_status) + int(has_base_integration)
            items.append({
                "key": _integration_key_from_rel(rel),
                "path": rel,
                "name": p.stem,
                "method_ids": method_ids,
                "method_ids_total": len(method_ids),
                "has_describe_methods": has_describe_methods,
                "has_call": has_call,
                "has_auth_status": has_auth_status,
                "has_base_integration": has_base_integration,
                "validation_score_0_3": validation_score,
                "read_ok": True,
            })
        return {
            "registry_bots_total": len(reg["bots"]),
            "integrations_total": len(items),
            "items": items,
            "issues": issues,
        }
    except OSError as e:
        raise RuntimeError(f"Cannot build integrations inventory: {e}") from e
    except RuntimeError:
        raise


def build_tools_inventory(registry_path: Path) -> dict[str, Any]:
    try:
        reg, repo_root = bot_registry_engine.load_registry(registry_path)
        tools = sorted(list(no_special_code_bot.TOOL_REGISTRY.keys()))
        usage: dict[str, dict[str, Any]] = {
            t: {
                "tool_name": t,
                "used_by_bots": [],
                "used_by_experts_allow": [],
                "used_by_experts_block": [],
                "tool_catalog_entries": [],
            }
            for t in tools
        }

        cfg_paths = _discover_generated_bot_configs(repo_root)
        for cfg_path in cfg_paths:
            cfg = _safe_read_json(cfg_path)
            bot_name = str(cfg.get("bot_name", cfg_path.stem))
            for t in cfg.get("tools", []):
                if t not in usage:
                    usage[t] = {
                        "tool_name": t,
                        "used_by_bots": [],
                        "used_by_experts_allow": [],
                        "used_by_experts_block": [],
                        "tool_catalog_entries": [],
                    }
                if bot_name not in usage[t]["used_by_bots"]:
                    usage[t]["used_by_bots"].append(bot_name)
            for exp in cfg.get("experts", []):
                exp_name = str(exp.get("name", "unknown"))
                allow = [x.strip() for x in str(exp.get("fexp_allow_tools", "")).split(",") if x.strip()]
                block = [x.strip() for x in str(exp.get("fexp_block_tools", "")).split(",") if x.strip()]
                for t in allow:
                    if t not in usage:
                        usage[t] = {
                            "tool_name": t,
                            "used_by_bots": [],
                            "used_by_experts_allow": [],
                            "used_by_experts_block": [],
                            "tool_catalog_entries": [],
                        }
                    usage[t]["used_by_experts_allow"].append(f"{bot_name}:{exp_name}")
                for t in block:
                    if t not in usage:
                        usage[t] = {
                            "tool_name": t,
                            "used_by_bots": [],
                            "used_by_experts_allow": [],
                            "used_by_experts_block": [],
                            "tool_catalog_entries": [],
                        }
                    usage[t]["used_by_experts_block"].append(f"{bot_name}:{exp_name}")

            tc = cfg.get("tool_catalog", {})
            if isinstance(tc, dict):
                for t, meta in tc.items():
                    entry = {
                        "bot_name": bot_name,
                        "integration_mode": str(meta.get("integration_mode", "")) if isinstance(meta, dict) else "",
                        "method_ids_total": len(meta.get("method_ids", [])) if isinstance(meta, dict) and isinstance(meta.get("method_ids", []), list) else 0,
                    }
                    if t not in usage:
                        usage[t] = {
                            "tool_name": t,
                            "used_by_bots": [],
                            "used_by_experts_allow": [],
                            "used_by_experts_block": [],
                            "tool_catalog_entries": [],
                        }
                    usage[t]["tool_catalog_entries"].append(entry)

        items = []
        for t in sorted(usage.keys()):
            x = usage[t]
            items.append({
                "tool_name": t,
                "registered_in_runtime": t in no_special_code_bot.TOOL_REGISTRY,
                "used_by_bots": sorted(x["used_by_bots"]),
                "used_by_experts_allow": sorted(x["used_by_experts_allow"]),
                "used_by_experts_block": sorted(x["used_by_experts_block"]),
                "tool_catalog_entries": x["tool_catalog_entries"],
            })
        return {
            "registry_bots_total": len(reg["bots"]),
            "runtime_tools_total": len(no_special_code_bot.TOOL_REGISTRY),
            "tools_total": len(items),
            "items": items,
        }
    except RuntimeError:
        raise


def build_bots_inventory(registry_path: Path) -> dict[str, Any]:
    try:
        reg, repo_root = bot_registry_engine.load_registry(registry_path)
        generated_cfgs = _discover_generated_bot_configs(repo_root)
        cfg_map = {str(x.resolve()): x for x in generated_cfgs}
        registered = []
        registered_cfg_paths: set[str] = set()
        for item in reg["bots"]:
            bot_id = str(item["bot_id"])
            cfg_path = bot_registry_engine._resolve_input_path(item["bot_json_path"], registry_path.parent, repo_root)
            out_dir = bot_registry_engine._resolve_input_path(item["output_dir"], registry_path.parent, repo_root)
            registered_cfg_paths.add(str(cfg_path.resolve()))
            cfg = _safe_read_json(cfg_path) if cfg_path.exists() else {}
            existing_managed = []
            for rel in MANAGED_PATH_PATTERNS:
                if "*" in rel:
                    for p in out_dir.glob(rel):
                        existing_managed.append(str(p.resolve().relative_to(out_dir.resolve())).replace("\\", "/"))
                else:
                    p = out_dir / rel
                    if p.exists():
                        existing_managed.append(rel)
            custom_zone = out_dir / CUSTOM_ZONE_REL
            custom_files = []
            if custom_zone.exists():
                for p in custom_zone.rglob("*"):
                    if p.is_file():
                        custom_files.append(str(p.resolve().relative_to(out_dir.resolve())).replace("\\", "/"))
            registered.append({
                "bot_id": bot_id,
                "enabled": bool(item.get("enabled", False)),
                "bot_json_path": str(cfg_path),
                "output_dir": str(out_dir),
                "bot_name": str(cfg.get("bot_name", bot_id)),
                "tools_total": len(cfg.get("tools", [])) if isinstance(cfg, dict) else 0,
                "experts_total": len(cfg.get("experts", [])) if isinstance(cfg, dict) else 0,
                "skills_total": len(cfg.get("skills", [])) if isinstance(cfg, dict) else 0,
                "managed_path_patterns": MANAGED_PATH_PATTERNS,
                "existing_managed_files": sorted(existing_managed),
                "custom_zone_rel": CUSTOM_ZONE_REL,
                "custom_files": sorted(custom_files),
                "editor_path": f"/bot/{bot_id}",
            })
        unregistered = []
        for abs_cfg, p in cfg_map.items():
            if abs_cfg in registered_cfg_paths:
                continue
            cfg = _safe_read_json(p)
            unregistered.append({
                "bot_name": str(cfg.get("bot_name", p.stem)),
                "bot_json_path": str(p),
                "tools_total": len(cfg.get("tools", [])),
                "experts_total": len(cfg.get("experts", [])),
                "skills_total": len(cfg.get("skills", [])),
            })
        return {
            "bots_registered_total": len(registered),
            "bots_unregistered_total": len(unregistered),
            "registered": registered,
            "unregistered": unregistered,
        }
    except RuntimeError:
        raise
