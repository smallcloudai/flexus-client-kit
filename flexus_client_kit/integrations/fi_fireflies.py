import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fireflies")

PROVIDER_NAME = "fireflies"
METHOD_IDS = [
    "fireflies.transcript.get.v1",
]

_BASE_URL = "https://api.fireflies.ai/graphql"

_TRANSCRIPT_QUERY = """
query Transcript($transcriptId: String!) {
  transcript(id: $transcriptId) {
    id
    title
    date
    duration
    sentences {
      index
      speaker_name
      text
      start_time
      end_time
    }
  }
}
""".strip()


class IntegrationFireflies:
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
                f"methods: {', '.join(METHOD_IDS)}"
            )
        if op == "status":
            key = os.environ.get("FIREFLIES_API_KEY", "")
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "available" if key else "no_credentials",
                "method_count": len(METHOD_IDS),
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
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "fireflies.transcript.get.v1":
            return await self._transcript_get(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)

    def _headers(self, key: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def _ok(self, method_label: str, data: Any) -> str:
        return (
            f"fireflies.{method_label} ok\n\n"
            f"```json\n{json.dumps({'ok': True, 'result': data}, indent=2, ensure_ascii=False)}\n```"
        )

    def _provider_error(self, status_code: int, detail: str) -> str:
        logger.info("fireflies provider error status=%s detail=%s", status_code, detail)
        return json.dumps({
            "ok": False,
            "error_code": "PROVIDER_ERROR",
            "status": status_code,
            "detail": detail,
        }, indent=2, ensure_ascii=False)

    async def _transcript_get(self, args: Dict[str, Any]) -> str:
        key = os.environ.get("FIREFLIES_API_KEY", "")
        if not key:
            return json.dumps({"ok": False, "error_code": "NO_CREDENTIALS", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        transcript_id = str(args.get("transcript_id") or args.get("meeting_id") or "").strip()
        if not transcript_id:
            return json.dumps({"ok": False, "error_code": "MISSING_ARG", "detail": "transcript_id or meeting_id required"}, indent=2, ensure_ascii=False)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    _BASE_URL,
                    headers=self._headers(key),
                    json={"query": _TRANSCRIPT_QUERY, "variables": {"transcriptId": transcript_id}},
                )
            except httpx.TimeoutException:
                return json.dumps({"ok": False, "error_code": "TIMEOUT"}, indent=2, ensure_ascii=False)
            except httpx.HTTPError as e:
                return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": str(e)}, indent=2, ensure_ascii=False)
        if resp.status_code != 200:
            return self._provider_error(resp.status_code, resp.text[:500])
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return self._provider_error(resp.status_code, "invalid json in response")
        if "errors" in data:
            errors = data["errors"]
            logger.info("fireflies graphql errors transcript_id=%s errors=%s", transcript_id, errors)
            return json.dumps({"ok": False, "error_code": "GRAPHQL_ERROR", "errors": errors}, indent=2, ensure_ascii=False)
        transcript = (data.get("data") or {}).get("transcript")
        return self._ok("transcript.get.v1", transcript)
