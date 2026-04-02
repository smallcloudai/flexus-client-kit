import argparse
import asyncio
import ast
import importlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import dotenv_values


@dataclass
class MockRobotContext:
    external_auth: dict[str, Any]


@dataclass
class MockToolCall:
    confirmed_by_human: bool = True


def _load_env(path: str | None = None) -> dict[str, str]:
    if path:
        cfg = dotenv_values(path)
        return {k: v for k, v in cfg.items() if isinstance(v, str)}
    cfg: dict[str, str] = {}
    for p in (".env", ".env.local"):
        if os.path.exists(p):
            cfg.update({k: v for k, v in dotenv_values(p).items() if isinstance(v, str)})
    cfg.update(os.environ)
    return cfg


def _guess_external_auth(md: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    provider = md.get("provider") or ""
    token = ""
    api_key = ""
    for k in md.get("env_keys") or []:
        if env.get(k):
            token = env[k]
            api_key = env[k]
            break
    kind = md.get("auth_kind")
    if kind == "oauth2":
        return {provider: {"token": {"access_token": token}}}
    if kind == "api_key":
        return {provider: {"api_key": api_key, "token": {"access_token": token}}}
    return {provider: {}}


def _normalize(provider: str, result: dict[str, Any], latency_ms: int) -> dict[str, Any]:
    return {
        "provider": provider,
        "ok": bool(result.get("ok", False)),
        "status": result.get("status", "error"),
        "can_read": bool(result.get("can_read", result.get("ok", False))),
        "note": str(result.get("note", "")),
        "latency_ms": int(result.get("latency_ms", latency_ms)),
    }


def _short_module_name(module_name: str) -> str:
    p = "flexus_client_kit.integrations."
    return module_name[len(p):] if module_name.startswith(p) else module_name


def _to_full_module_name(module_name: str) -> str:
    return module_name if module_name.startswith("flexus_client_kit.integrations.") else f"flexus_client_kit.integrations.{module_name}"


async def run_single(module_short_name: str, env: dict[str, str] | None = None, allow_fallback: bool = True) -> dict[str, Any]:
    t0 = time.perf_counter()
    env = env or _load_env(None)
    full = _to_full_module_name(module_short_name)
    try:
        mod = importlib.import_module(full)
    except Exception as e:
        provider = module_short_name.split(".")[-1].removeprefix("fi_")
        r = _normalize(provider, {"ok": False, "status": "error", "can_read": False, "note": f"import failed: {type(e).__name__}: {e}"}, int((time.perf_counter() - t0) * 1000))
        r["module"] = _short_module_name(module_short_name)
        return r
    md = getattr(mod, "INTEGRATION_METADATA", {})
    provider = md.get("provider") or module_short_name.removeprefix("fi_")
    if not md.get("supports_ping", False) and not allow_fallback:
        r = _normalize(provider, {"ok": False, "status": "not_covered", "can_read": False, "note": "supports_ping is false"}, int((time.perf_counter() - t0) * 1000))
        r["module"] = _short_module_name(module_short_name)
        return r
    rcx = MockRobotContext(external_auth=_guess_external_auth(md, env))

    cls = next((getattr(mod, n) for n in dir(mod) if n.startswith("Integration") and isinstance(getattr(mod, n), type)), None)
    if cls is None:
        r = _normalize(provider, {"ok": False, "status": "not_covered", "can_read": False, "note": "No integration class found"}, int((time.perf_counter() - t0) * 1000))
        r["module"] = _short_module_name(module_short_name)
        return r

    try:
        try:
            obj = cls(None, rcx)
        except TypeError:
            try:
                obj = cls(rcx)
            except TypeError:
                obj = cls(None, rcx, None)
    except Exception as e:
        r = _normalize(provider, {"ok": False, "status": "error", "can_read": False, "note": f"init failed: {type(e).__name__}: {e}"}, int((time.perf_counter() - t0) * 1000))
        r["module"] = _short_module_name(module_short_name)
        return r

    if hasattr(obj, "ping") and callable(getattr(obj, "ping")):
        try:
            r = await obj.ping()
            out = _normalize(provider, r if isinstance(r, dict) else {"ok": False, "status": "error", "note": str(r)}, int((time.perf_counter() - t0) * 1000))
            out["module"] = _short_module_name(module_short_name)
            return out
        except Exception as e:
            out = _normalize(provider, {"ok": False, "status": "error", "can_read": False, "note": f"ping failed: {type(e).__name__}: {e}"}, int((time.perf_counter() - t0) * 1000))
            out["module"] = _short_module_name(module_short_name)
            return out

    cbm = getattr(obj, "called_by_model", None)
    if allow_fallback and callable(cbm):
        try:
            raw = await cbm(MockToolCall(), {"op": "status"})
            out = _normalize(provider, {"ok": True, "status": "connected", "can_read": True, "note": str(raw)}, int((time.perf_counter() - t0) * 1000))
            out["module"] = _short_module_name(module_short_name)
            return out
        except Exception as e:
            out = _normalize(provider, {"ok": False, "status": "error", "can_read": False, "note": f"status fallback failed: {type(e).__name__}: {e}"}, int((time.perf_counter() - t0) * 1000))
            out["module"] = _short_module_name(module_short_name)
            return out

    out = _normalize(provider, {"ok": False, "status": "not_covered", "can_read": False, "note": "No ping() or status fallback"}, int((time.perf_counter() - t0) * 1000))
    out["module"] = _short_module_name(module_short_name)
    return out


def _read_metadata_from_file(path: Path) -> dict[str, Any]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "INTEGRATION_METADATA":
                try:
                    v = ast.literal_eval(node.value)
                    return v if isinstance(v, dict) else {}
                except Exception:
                    return {}
    return {}


def discover_integrations_with_metadata() -> list[dict[str, Any]]:
    root = Path(__file__).resolve().parent
    out = []
    for p in sorted(root.rglob("fi_*.py")):
        rel = p.relative_to(root).with_suffix("")
        module_name = ".".join(rel.parts)
        md = _read_metadata_from_file(p)
        if not md:
            continue
        out.append({
            "module": module_name,
            "provider": md.get("provider") or rel.stem.removeprefix("fi_"),
            "supports_ping": bool(md.get("supports_ping", False)),
        })
    return out


def render_integrations_md(results: list[dict[str, Any]]) -> str:
    rows = ["# Integrations Ping Report", "", "| Provider | Module | OK | Status | Can Read | Latency (ms) | Note |", "|---|---|---:|---|---:|---:|---|"]
    for r in results:
        rows.append(f"| {r['provider']} | {r.get('module', '')} | {'yes' if r['ok'] else 'no'} | {r['status']} | {'yes' if r['can_read'] else 'no'} | {r['latency_ms']} | {r['note'].replace('|', '/')} |")
    return "\n".join(rows) + "\n"


async def _amain() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("integration", nargs="*", help="fi_* module short name, e.g. fi_github; if empty, runs all")
    ap.add_argument("--env-file", default=None)
    ap.add_argument("--out-md", default="INTEGRATIONS.md")
    a = ap.parse_args()
    env = _load_env(a.env_file)
    if a.integration:
        res = [await run_single(n, env=env, allow_fallback=True) for n in a.integration]
    else:
        res = []
        for x in discover_integrations_with_metadata():
            if not x["supports_ping"]:
                r = _normalize(x["provider"], {"ok": False, "status": "not_covered", "can_read": False, "note": "supports_ping is false"}, 0)
                r["module"] = x["module"]
                res.append(r)
                continue
            res.append(await run_single(x["module"], env=env, allow_fallback=False))
    print(json.dumps(res, indent=2))
    with open(a.out_md, "w", encoding="utf-8") as f:
        f.write(render_integrations_md(res))
    return 0


def main() -> int:
    return asyncio.run(_amain())


if __name__ == "__main__":
    raise SystemExit(main())
