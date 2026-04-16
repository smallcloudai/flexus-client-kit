import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Callable, Awaitable

from flexus_client_kit import ckit_cloudtool, ckit_integrations_db

logger = logging.getLogger("integration_tester")

INTEGRATION_TESTER_ROOTDIR = Path(__file__).parent

PLAN_BATCHES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="integration_plan_batches",
    description="Plan deterministic integration test batches and return task specs for kanban fan-out.",
    parameters={
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "requested": {"type": "string", "description": "Requested integrations, e.g. 'all' or 'newsapi,resend'."},
            "batch_size": {"type": "integer", "description": "Max integrations per task batch."},
            "configured_only": {"type": "boolean", "description": "If true, include only integrations with configured keys."},
        },
        "required": ["requested", "batch_size", "configured_only"],
    },
)

INTEGRATION_TESTER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    INTEGRATION_TESTER_ROOTDIR,
    allowlist=["newsapi", "resend"],
    builtin_skills=[],
)

TOOLS = [PLAN_BATCHES_TOOL] + [t for rec in INTEGRATION_TESTER_INTEGRATIONS for t in rec.integr_tools]


def _chunk_names(xs: List[str], n: int) -> List[List[str]]:
    if n < 1:
        n = 1
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def _requested_names(raw: str) -> List[str]:
    s = (raw or "").strip().lower()
    if not s or s == "all":
        return ["all"]
    names = []
    for x in s.replace(";", ",").split(","):
        x = x.strip()
        if x:
            names.append(x)
    return names or ["all"]


def _setup_allowlist_names(setup: Dict[str, Any]) -> List[str]:
    raw = str(setup.get("INTEGRATION_TESTER_ALLOWLIST", "") or "").strip().lower()
    if not raw:
        return []
    names: List[str] = []
    for x in raw.replace(";", ",").split(","):
        x = x.strip()
        if x:
            names.append(x)
    return names


def load_env_config(setup: Dict[str, Any]) -> None:
    env_config = setup.get("ENV_CONFIG", "")
    if not env_config:
        logger.info("No ENV_CONFIG found in persona_setup")
        return
    count = 0
    for line in env_config.strip().split('\n'):
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()
            count += 1
    logger.info(f"Loaded {count} environment variables from ENV_CONFIG")


def _integration_env_vars(integr_name: str) -> tuple[str, list[str]]:
    name = integr_name.upper()
    return f"{name}_API_KEY", [f"{name}_KEY"]


def get_configured_integrations(integr_names: List[str]) -> List[Dict[str, Any]]:
    result = []
    for name in integr_names:
        env_var, alt_env_vars = _integration_env_vars(name)
        key = os.environ.get(env_var)
        if not key:
            for alt in alt_env_vars:
                key = os.environ.get(alt)
                if key:
                    break
        if key:
            result.append({
                "name": name,
                "env_var": env_var,
                "key_hint": key[-4:] if len(key) > 4 else "***",
            })
    return result


def _resolve_api_key(env_var: str, alt_env_vars: list[str]) -> str | None:
    key = os.environ.get(env_var)
    if not key:
        for alt in alt_env_vars:
            key = os.environ.get(alt)
            if key:
                break
    return key


def classify_error(e: Exception) -> tuple[str, str]:
    msg = str(e).lower()
    if any(k in msg for k in ("401", "403", "unauthorized", "invalid api", "forbidden", "invalid_api")):
        return "AUTH_ERROR", "API key invalid or unauthorized"
    if any(k in msg for k in ("timeout", "connection", "dns", "network", "connect", "refused")):
        return "NETWORK_ERROR", "Network/connectivity issue"
    if any(k in msg for k in ("rate", "429", "quota", "limit")):
        return "RATE_LIMIT", "API rate limit or quota exceeded"
    return "UNKNOWN_ERROR", str(e)[:200]


def _format_result(raw: str) -> str:
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            skip = {"ok", "provider", "description", "help_text"}
            parts = []
            for k, v in data.items():
                if k in skip:
                    continue
                if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
                    parts.append(f"{k}=[{', '.join(v)}]")
                elif not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            if parts:
                return ", ".join(parts)
    except json.JSONDecodeError:
        pass
    return raw


def make_testing_wrapper(
    original: Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[str]],
    integr_name: str,
    tool_name: str,
):
    env_var, alt_env_vars = _integration_env_vars(integr_name)

    async def wrapper(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        key = _resolve_api_key(env_var, alt_env_vars)
        logger.info(f"Testing {tool_name} - API key present: {bool(key)}")
        if not key:
            logger.warning(f"{tool_name} test FAILED - no API key configured")
            return f"Error [AUTH_ERROR]: {env_var} not configured. Resolve the kanban task as FAILED with status: 'FAILED - No API key configured for {tool_name}'"
        try:
            result = await original(toolcall, model_produced_args)
            op = str(model_produced_args.get("op", "")).strip() if model_produced_args else ""
            if op == "help":
                result = "[HELP OUTPUT - NOT A TEST] " + result
            formatted = _format_result(result)
            key_hint = key[-3:] if len(key) > 3 else "***"
            out = f"api_key_hint=***{key_hint}, {formatted}"
            logger.info(f"{tool_name} test result: {out[:120]}..." if len(out) > 120 else f"{tool_name} test result: {out}")
            return out
        except Exception as e:
            category, detail = classify_error(e)
            logger.error(f"toolcall_{tool_name}: {category}: {detail}", exc_info=True)
            return f"Error [{category}]: {detail}"
    return wrapper
