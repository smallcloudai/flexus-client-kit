import argparse
import difflib
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import jsonschema

from flexus_client_kit.runtime import no_special_code_bot

logger = logging.getLogger("bot_registry_engine")

REGISTRY_SCHEMA = json.loads((Path(__file__).parent / "bot_registry_schema.json").read_text())
BOT_CONFIG_SCHEMA = json.loads((Path(__file__).parent / "bot_config_schema.json").read_text())
CORE_MANAGED_FILES = ["manifest.json", "setup_schema.json", "README.md", "prompts/personality.md"]
BUILDER_STATE_FILE = ".builder-state.json"
BUILDERIGNORE_FILE = ".builderignore"
BUILDER_MODE_NO_SPECIAL_CODE = "no_special_code"
BUILDER_MODE_FULL_SCAFFOLD = "full_scaffold_managed"
BUILDER_MODE_FROZEN = "frozen_custom"
ALLOWED_BUILDER_MODES = {BUILDER_MODE_NO_SPECIAL_CODE, BUILDER_MODE_FULL_SCAFFOLD, BUILDER_MODE_FROZEN}


def _find_repo_root(start_dir: Path) -> Path:
    try:
        d = start_dir.resolve()
        while d != d.parent:
            if (d / ".git").exists():
                return d
            d = d.parent
        raise FileNotFoundError(f"Cannot find repo root from {start_dir}")
    except OSError as e:
        raise RuntimeError(f"Cannot resolve repo root from {start_dir}") from e


def _resolve_input_path(path_raw: str, base_dir: Path, repo_root: Path) -> Path:
    try:
        p = Path(path_raw)
        if p.is_absolute():
            return p
        p1 = (base_dir / p).resolve()
        if p1.exists():
            return p1
        return (repo_root / p).resolve()
    except OSError as e:
        raise RuntimeError(f"Cannot resolve path {path_raw}") from e


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as e:
        raise RuntimeError(f"Missing required file: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Cannot read {path}: {e}") from e


def _read_json_optional(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        raw = _read_json(path)
        if not isinstance(raw, dict):
            raise RuntimeError(f"Expected object JSON in {path}")
        return raw
    except RuntimeError:
        raise


def _write_text_atomic(path: Path, text: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text)
        tmp.replace(path)
    except OSError as e:
        raise RuntimeError(f"Cannot write {path}: {e}") from e


def _json_text(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=4) + "\n"
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot serialize object to JSON: {e}") from e


def write_json_atomic(path: Path, obj: Any) -> None:
    try:
        _write_text_atomic(path, _json_text(obj))
    except RuntimeError:
        raise


def _text_sha256(text: str) -> str:
    try:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    except (UnicodeEncodeError, ValueError) as e:
        raise RuntimeError(f"Cannot hash text: {e}") from e


def _normalize_path_token(raw: str) -> str:
    return raw.replace("\\", "/").strip("/")


def _load_builderignore(repo_root: Path) -> set[str]:
    try:
        p = repo_root / BUILDERIGNORE_FILE
        if not p.exists():
            return set()
        out: set[str] = set()
        for line in p.read_text().splitlines():
            x = line.strip()
            if not x or x.startswith("#"):
                continue
            out.add(_normalize_path_token(x))
        return out
    except OSError as e:
        raise RuntimeError(f"Cannot read {repo_root / BUILDERIGNORE_FILE}: {e}") from e


def _is_ignored_bot(entry: dict[str, Any], ignore_tokens: set[str]) -> bool:
    try:
        if not ignore_tokens:
            return False
        bot_id = str(entry["bot_id"]).strip()
        output_dir = _normalize_path_token(str(entry["output_dir"]))
        output_dir_name = Path(output_dir).name
        bot_json_path = _normalize_path_token(str(entry["bot_json_path"]))
        bot_json_name = Path(bot_json_path).name
        candidates = {
            bot_id,
            output_dir,
            output_dir_name,
            bot_json_path,
            bot_json_name,
        }
        return len(candidates.intersection(ignore_tokens)) > 0
    except KeyError as e:
        raise RuntimeError(f"Registry bot entry missing key: {e}") from e


def _builder_mode(bot_cfg: dict[str, Any]) -> str:
    mode = str(bot_cfg.get("builder_mode", BUILDER_MODE_NO_SPECIAL_CODE))
    if mode not in ALLOWED_BUILDER_MODES:
        raise RuntimeError(f"Invalid builder_mode {mode!r}, allowed: {sorted(ALLOWED_BUILDER_MODES)}")
    return mode


def _custom_dir(bot_cfg: dict[str, Any]) -> str:
    x = str(bot_cfg.get("custom_dir", "custom")).strip()
    if not x:
        raise RuntimeError("custom_dir cannot be empty")
    return x


def _build_manifest(bot_cfg: dict[str, Any]) -> dict[str, Any]:
    try:
        m = {
            "bot_name": bot_cfg["bot_name"],
            "accent_color": bot_cfg["accent_color"],
            "title1": bot_cfg["title1"],
            "title2": bot_cfg["title2"],
            "author": bot_cfg["author"],
            "occupation": bot_cfg["occupation"],
            "typical_group": bot_cfg["typical_group"],
            "github_repo": bot_cfg["github_repo"],
            "tools": bot_cfg["tools"],
            "featured_actions": bot_cfg["featured_actions"],
            "intro_message": bot_cfg["intro_message"],
            "preferred_model_default": bot_cfg["preferred_model_default"],
            "daily_budget_default": bot_cfg["daily_budget_default"],
            "default_inbox_default": bot_cfg["default_inbox_default"],
            "tags": bot_cfg["tags"],
        }
        if "schedule" in bot_cfg:
            m["schedule"] = bot_cfg["schedule"]
        if "forms" in bot_cfg:
            m["forms"] = bot_cfg["forms"]
        if "auth_supported" in bot_cfg:
            m["auth_supported"] = bot_cfg["auth_supported"]
        if "auth_scopes" in bot_cfg:
            m["auth_scopes"] = bot_cfg["auth_scopes"]
        return m
    except KeyError as e:
        raise RuntimeError(f"Missing key in bot config while rendering manifest: {e}") from e


def _render_expert_md(exp: dict[str, Any]) -> str:
    try:
        front = ["---", f"fexp_description: {exp['fexp_description']}"]
        if exp.get("fexp_block_tools", ""):
            front.append(f"fexp_block_tools: {exp['fexp_block_tools']}")
        if exp.get("fexp_allow_tools", ""):
            front.append(f"fexp_allow_tools: {exp['fexp_allow_tools']}")
        if exp.get("skills", []):
            front.append(f"fexp_skills: {','.join(exp['skills'])}")
        if exp.get("pdoc_output_schemas"):
            try:
                schema_meta = exp["pdoc_output_schemas"]
                schema_text = json.dumps(schema_meta, separators=(",", ":"))
                front.append(f"fexp_pdoc_output_schemas: {schema_text}")
            except (TypeError, ValueError) as e:
                raise RuntimeError(f"Cannot serialize pdoc_output_schemas for expert {exp.get('name', '<unknown>')}: {e}") from e
        front.append("---")
        return "\n".join(front) + "\n\n" + str(exp["body_md"]).strip() + "\n"
    except KeyError as e:
        raise RuntimeError(f"Missing key in expert config: {e}") from e


def _render_core_files(bot_cfg: dict[str, Any]) -> dict[str, str]:
    try:
        files = {
            "manifest.json": _json_text(_build_manifest(bot_cfg)),
            "setup_schema.json": _json_text(bot_cfg["setup_schema"]),
            "prompts/personality.md": str(bot_cfg["personality_md"]).strip() + "\n",
        }
        if bot_cfg.get("readme_md", ""):
            files["README.md"] = str(bot_cfg["readme_md"]).strip() + "\n"
        else:
            files["README.md"] = str(bot_cfg["title2"]).strip() + "\n"
        for exp in bot_cfg["experts"]:
            files[f"prompts/expert_{exp['name']}.md"] = _render_expert_md(exp)
        for sk in bot_cfg.get("skills", []):
            files[f"prompts/skill_{sk['name']}.md"] = str(sk["body_md"]).strip() + "\n"
        return files
    except KeyError as e:
        raise RuntimeError(f"Missing key in bot config while rendering files: {e}") from e


def _render_full_scaffold_extras(bot_cfg: dict[str, Any]) -> dict[str, str]:
    try:
        bot_name = str(bot_cfg["bot_name"]).strip()
        module_stem = bot_name[:-4] if bot_name.endswith("_bot") else bot_name
        custom_dir = _custom_dir(bot_cfg)
        prompt_module_name = f"{module_stem}_prompts"

        tools_literal = json.dumps(bot_cfg["tools"], indent=4)
        experts_literal = json.dumps(bot_cfg["experts"], indent=4)
        skills_literal = json.dumps(bot_cfg.get("skills", []), indent=4)

        prompt_py = (
            "import json\n\n"
            f"BOT_PERSONALITY_MD = {json.dumps(str(bot_cfg['personality_md']))}\n"
            f"BOT_EXPERTS = json.loads({json.dumps(json.dumps(bot_cfg['experts']))})\n"
            f"BOT_SKILLS = json.loads({json.dumps(json.dumps(bot_cfg.get('skills', [])))})\n"
        )

        bot_py = (
            "import sys\n"
            "from pathlib import Path\n"
            "from flexus_client_kit.runtime import no_special_code_bot\n\n"
            "def main() -> None:\n"
            "    bot_dir = Path(__file__).resolve().parent\n"
            "    sys.argv = [sys.argv[0], str(bot_dir)]\n"
            "    no_special_code_bot.main()\n\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        )

        install_py = (
            "import asyncio\n"
            "from pathlib import Path\n"
            "from flexus_client_kit.core import ckit_client\n"
            "from flexus_client_kit.runtime import no_special_code_bot\n"
            "from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION\n\n"
            "def main() -> None:\n"
            "    bot_dir = Path(__file__).resolve().parent\n"
            "    manifest = no_special_code_bot.load_manifest(bot_dir)\n"
            "    tools = no_special_code_bot.tool_registry_lookup(manifest[\"tools\"])\n"
            f"    client = ckit_client.FlexusClient(\"{bot_name}_install\")\n"
            "    asyncio.run(no_special_code_bot.install_from_manifest(\n"
            "        manifest,\n"
            "        client,\n"
            "        bot_name=manifest[\"bot_name\"],\n"
            "        bot_version=SIMPLE_BOTS_COMMON_VERSION,\n"
            "        tools=tools,\n"
            "    ))\n\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        )

        custom_init_py = ""
        custom_hooks_py = (
            "from typing import Any\n\n"
            "def register_custom_hooks(rcx: Any, setup: dict[str, Any]) -> None:\n"
            "    _ = rcx\n"
            "    _ = setup\n"
            "    # Add your custom event hooks and tool handlers here.\n"
            "    return None\n"
        )

        scaffold_readme = (
            "# Builder-Managed Full Scaffold\n\n"
            "This bot is generated in full scaffold mode.\n"
            f"Custom code belongs to `{custom_dir}/` and is never overwritten by builder.\n"
        )

        scaffold_meta_json = _json_text(
            {
                "bot_name": bot_name,
                "managed_mode": BUILDER_MODE_FULL_SCAFFOLD,
                "tools": bot_cfg["tools"],
                "experts": [x["name"] for x in bot_cfg["experts"]],
                "skills": [x["name"] for x in bot_cfg.get("skills", [])],
            }
        )

        scaffold_contract_md = (
            "# Full Scaffold Contract\n\n"
            "- Managed files are regenerated by builder.\n"
            f"- Custom logic lives only in `{custom_dir}/`.\n"
            "- If managed files are edited manually, build fails fast unless overwrite is explicit.\n"
        )

        return {
            f"{module_stem}_bot.py": bot_py,
            f"{module_stem}_install.py": install_py,
            f"{prompt_module_name}.py": prompt_py,
            "scaffold/contract.md": scaffold_contract_md,
            "scaffold/meta.json": scaffold_meta_json,
            "forms/README.md": "Place optional HTML forms here.\n",
            "integrations/README.md": "Place bot-specific integration adapters here.\n",
            "scenarios/README.md": "Place scenario yaml files here.\n",
            f"{custom_dir}/__init__.py": custom_init_py,
            f"{custom_dir}/hooks.py": custom_hooks_py,
            "README.builder.md": scaffold_readme,
            "scaffold/input_snapshot_tools.json": tools_literal + "\n",
            "scaffold/input_snapshot_experts.json": experts_literal + "\n",
            "scaffold/input_snapshot_skills.json": skills_literal + "\n",
        }
    except (KeyError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot render full scaffold files: {e}") from e


def _render_managed_files(bot_cfg: dict[str, Any]) -> dict[str, str]:
    mode = _builder_mode(bot_cfg)
    if mode == BUILDER_MODE_FROZEN:
        return {}
    files = _render_core_files(bot_cfg)
    if mode == BUILDER_MODE_FULL_SCAFFOLD:
        files.update(_render_full_scaffold_extras(bot_cfg))
    return files


def _load_builder_state(out_dir: Path) -> dict[str, Any]:
    try:
        return _read_json_optional(out_dir / BUILDER_STATE_FILE)
    except RuntimeError:
        raise


def _validate_managed_overwrite(
    out_dir: Path,
    files_new: dict[str, str],
    state: dict[str, Any],
    mode: str,
) -> None:
    try:
        if mode != BUILDER_MODE_FULL_SCAFFOLD:
            return
        managed_prev = state.get("managed_files", {})
        if not isinstance(managed_prev, dict):
            raise RuntimeError(f"{out_dir / BUILDER_STATE_FILE}: managed_files must be an object")
        for rel_path, new_text in files_new.items():
            abs_path = out_dir / rel_path
            if not abs_path.exists():
                continue
            old_text = abs_path.read_text()
            new_hash = _text_sha256(new_text)
            if rel_path in managed_prev:
                old_hash_expected = str(managed_prev[rel_path])
                old_hash_actual = _text_sha256(old_text)
                if old_hash_actual != old_hash_expected and old_hash_actual != new_hash:
                    raise RuntimeError(
                        f"{abs_path}: managed file was edited outside builder; refuse overwrite (move changes to custom/ or reset file)"
                    )
            else:
                if old_text != new_text:
                    raise RuntimeError(
                        f"{abs_path}: exists but not managed by builder; refuse overwrite in full_scaffold_managed mode"
                    )
    except OSError as e:
        raise RuntimeError(f"Cannot validate managed overwrite in {out_dir}: {e}") from e


def _collect_stale_managed_files(
    out_dir: Path,
    state: dict[str, Any],
    files_new: dict[str, str],
) -> list[Path]:
    try:
        managed_prev = state.get("managed_files", {})
        if not isinstance(managed_prev, dict):
            return []
        stale: list[Path] = []
        for rel_path in managed_prev.keys():
            if rel_path in files_new:
                continue
            p = out_dir / rel_path
            if p.exists():
                stale.append(p)
        return stale
    except OSError as e:
        raise RuntimeError(f"Cannot collect stale managed files in {out_dir}: {e}") from e


def _write_builder_state(out_dir: Path, mode: str, files_new: dict[str, str], apply_changes: bool) -> None:
    try:
        if mode != BUILDER_MODE_FULL_SCAFFOLD:
            return
        state_obj = {
            "builder_mode": mode,
            "managed_files": {rel: _text_sha256(text) for rel, text in files_new.items()},
        }
        if apply_changes:
            write_json_atomic(out_dir / BUILDER_STATE_FILE, state_obj)
    except RuntimeError:
        raise


def _diff_text(old: str, new: str, rel_path: str) -> str:
    try:
        return "".join(difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"{rel_path} (old)",
            tofile=f"{rel_path} (new)",
            n=3,
        ))
    except OSError as e:
        raise RuntimeError(f"Cannot generate diff for {rel_path}: {e}") from e


def _validate_bot_config(bot_cfg: dict[str, Any], bot_json_path: Path) -> None:
    try:
        jsonschema.validate(bot_cfg, BOT_CONFIG_SCHEMA)
        mode = _builder_mode(bot_cfg)
        if mode == BUILDER_MODE_FROZEN:
            return
        if "default" not in {exp["name"] for exp in bot_cfg["experts"]}:
            raise ValueError(f"{bot_json_path}: experts must include 'default'")
        for t in bot_cfg["tools"]:
            if t not in no_special_code_bot.TOOL_REGISTRY:
                raise ValueError(f"{bot_json_path}: unknown tool {t!r}, allowed {list(no_special_code_bot.TOOL_REGISTRY.keys())}")
        exp_names = {exp["name"] for exp in bot_cfg["experts"]}
        for item in bot_cfg["featured_actions"]:
            if item["feat_expert"] not in exp_names:
                raise ValueError(f"{bot_json_path}: featured action references unknown expert {item['feat_expert']!r}")
        skills = bot_cfg.get("skills", [])
        skill_names = [x["name"] for x in skills]
        if len(skill_names) != len(set(skill_names)):
            raise ValueError(f"{bot_json_path}: duplicate skill name in skills[]")
        skill_name_set = set(skill_names)
        for exp in bot_cfg["experts"]:
            for sk in exp.get("skills", []):
                if sk not in skill_name_set:
                    raise ValueError(f"{bot_json_path}: expert {exp['name']!r} references unknown skill {sk!r}")
            pdoc_schemas = exp.get("pdoc_output_schemas", [])
            schema_names = [x["schema_name"] for x in pdoc_schemas]
            if len(schema_names) != len(set(schema_names)):
                raise ValueError(f"{bot_json_path}: expert {exp['name']!r} has duplicate schema_name in pdoc_output_schemas")
        auth_supported = bot_cfg.get("auth_supported", [])
        auth_scopes = bot_cfg.get("auth_scopes", {})
        for provider in auth_scopes.keys():
            if provider not in auth_supported:
                raise ValueError(f"{bot_json_path}: auth_scopes has provider {provider!r} not listed in auth_supported")
    except jsonschema.ValidationError as e:
        raise RuntimeError(f"{bot_json_path}: schema validation failed: {e.message}") from e
    except ValueError as e:
        raise RuntimeError(str(e)) from e


def load_registry(registry_path: Path) -> tuple[dict[str, Any], Path]:
    try:
        repo_root = _find_repo_root(registry_path.parent)
        reg = _read_json(registry_path)
        jsonschema.validate(reg, REGISTRY_SCHEMA)
        ids = [x["bot_id"] for x in reg["bots"]]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate bot_id in registry")
        ignored = _load_builderignore(repo_root)
        reg["bots"] = [x for x in reg["bots"] if not _is_ignored_bot(x, ignored)]
        return reg, repo_root
    except jsonschema.ValidationError as e:
        raise RuntimeError(f"{registry_path}: schema validation failed: {e.message}") from e
    except ValueError as e:
        raise RuntimeError(f"{registry_path}: {e}") from e


def validate_registry_and_bots(registry_path: Path) -> dict[str, Any]:
    try:
        reg, repo_root = load_registry(registry_path)
        out = {"registry": str(registry_path), "repo_root": str(repo_root), "bots": []}
        for b in reg["bots"]:
            bot_json_path = _resolve_input_path(b["bot_json_path"], registry_path.parent, repo_root)
            bot_cfg = _read_json(bot_json_path)
            _validate_bot_config(bot_cfg, bot_json_path)
            mode = _builder_mode(bot_cfg)
            out["bots"].append({
                "bot_id": b["bot_id"],
                "enabled": b["enabled"],
                "bot_json_path": str(bot_json_path),
                "output_dir": str(_resolve_input_path(b["output_dir"], registry_path.parent, repo_root)),
                "bot_name": bot_cfg["bot_name"],
                "builder_mode": mode,
            })
        return out
    except RuntimeError:
        raise


def build_from_registry(registry_path: Path, apply_changes: bool, bot_id: str | None = None) -> dict[str, Any]:
    try:
        reg, repo_root = load_registry(registry_path)
        result = {"registry": str(registry_path), "apply_changes": apply_changes, "bots": []}
        for b in reg["bots"]:
            if not b["enabled"]:
                continue
            if bot_id and b["bot_id"] != bot_id:
                continue
            bot_json_path = _resolve_input_path(b["bot_json_path"], registry_path.parent, repo_root)
            out_dir = _resolve_input_path(b["output_dir"], registry_path.parent, repo_root)
            bot_cfg = _read_json(bot_json_path)
            _validate_bot_config(bot_cfg, bot_json_path)
            mode = _builder_mode(bot_cfg)
            if bot_cfg["bot_name"] != b["bot_id"]:
                raise RuntimeError(f"{bot_json_path}: bot_name {bot_cfg['bot_name']!r} must match registry bot_id {b['bot_id']!r}")
            if mode == BUILDER_MODE_FROZEN:
                result["bots"].append({
                    "bot_id": b["bot_id"],
                    "bot_json_path": str(bot_json_path),
                    "output_dir": str(out_dir),
                    "builder_mode": mode,
                    "files": [],
                    "skipped_reason": "builder_mode=frozen_custom",
                })
                continue
            files = _render_managed_files(bot_cfg)
            state = _load_builder_state(out_dir)
            _validate_managed_overwrite(out_dir, files, state, mode)
            stale_paths = _collect_stale_managed_files(out_dir, state, files)
            bot_res = {
                "bot_id": b["bot_id"],
                "bot_json_path": str(bot_json_path),
                "output_dir": str(out_dir),
                "builder_mode": mode,
                "files": [],
            }
            for rel_path, new_text in files.items():
                abs_path = out_dir / rel_path
                old_text = abs_path.read_text() if abs_path.exists() else ""
                status = "unchanged"
                diff_text = ""
                if old_text != new_text:
                    status = "updated" if abs_path.exists() else "created"
                    diff_text = _diff_text(old_text, new_text, rel_path)
                    if apply_changes:
                        _write_text_atomic(abs_path, new_text)
                bot_res["files"].append({
                    "path": str(abs_path),
                    "status": status,
                    "diff": diff_text,
                })
            for stale in stale_paths:
                rel = str(stale.relative_to(out_dir))
                old_text = stale.read_text()
                diff_text = _diff_text(old_text, "", rel)
                if apply_changes:
                    stale.unlink()
                bot_res["files"].append({
                    "path": str(stale),
                    "status": "deleted",
                    "diff": diff_text,
                })
            _write_builder_state(out_dir, mode, files, apply_changes)
            result["bots"].append(bot_res)
        if bot_id and len(result["bots"]) == 0:
            raise RuntimeError(f"Enabled bot not found for bot_id={bot_id}")
        return result
    except OSError as e:
        raise RuntimeError(f"Build failed due to filesystem error: {e}") from e


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description="Validate and build no-special-code bots from registry")
        parser.add_argument("--registry", required=True, help="Path to bots registry json")
        parser.add_argument("--bot-id", default=None, help="Build only a specific bot_id")
        parser.add_argument("--write", action="store_true", help="Apply filesystem updates")
        parser.add_argument("--validate-only", action="store_true", help="Only run validation")
        args = parser.parse_args()
        reg_path = Path(args.registry).resolve()
        if args.validate_only:
            print(json.dumps(validate_registry_and_bots(reg_path), indent=2))
            return
        print(json.dumps(build_from_registry(reg_path, apply_changes=args.write, bot_id=args.bot_id), indent=2))
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
