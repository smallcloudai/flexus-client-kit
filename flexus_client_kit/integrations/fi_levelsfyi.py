import json
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

PROVIDER_NAME = "levelsfyi"
METHOD_IDS = [
    "levelsfyi.compensation.benchmark.v1",
]


class IntegrationLevelsfyi:
    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (
                f"provider={PROVIDER_NAME}\n"
                "op=help | status | list_methods | call\n"
                f"methods: {', '.join(METHOD_IDS)}\n"
                "note: Levels.fyi does not provide a public API. Compensation data is available only via their website."
            )
        if op == "status":
            return json.dumps({
                "ok": False,
                "provider": PROVIDER_NAME,
                "status": "unavailable",
                "error_code": "NO_PUBLIC_API",
                "message": "Levels.fyi does not offer a public API. Compensation benchmark data is accessible only through their website at https://www.levels.fyi. Consider using alternative sources such as Glassdoor, LinkedIn Salary, or Bureau of Labor Statistics for compensation data.",
            }, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return json.dumps({
            "ok": False,
            "error_code": "NO_PUBLIC_API",
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "message": (
                "Levels.fyi does not provide a public API for compensation data. "
                "Data is only available on their website at https://www.levels.fyi. "
                "Alternatives: Glassdoor Salary API (via HasData scraping), LinkedIn Salary, "
                "BLS Occupational Employment Statistics (public), or Payscale."
            ),
        }, indent=2, ensure_ascii=False)
