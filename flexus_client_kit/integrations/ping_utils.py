import time

import httpx


def ping_result(ok: bool, status: str, can_read: bool, note: str, latency_ms: int) -> dict:
    return {
        "ok": ok,
        "status": status,
        "can_read": can_read,
        "note": note,
        "latency_ms": latency_ms,
    }


async def ping_http_get_json(
    url: str,
    headers: dict[str, str],
    timeout_s: float = 15.0,
    note_limit: int = 240,
) -> tuple[dict, dict]:
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.get(url, headers=headers)
    except Exception as e:
        return ping_result(False, "error", False, f"{type(e).__name__}: {e}", int((time.perf_counter() - t0) * 1000)), {}

    lat = int((time.perf_counter() - t0) * 1000)
    if r.status_code == 401:
        return ping_result(False, "expired", False, (r.text or "Unauthorized")[:note_limit], lat), {}
    if r.status_code >= 400:
        return ping_result(False, "error", False, (r.text or f"HTTP {r.status_code}")[:note_limit], lat), {}

    try:
        data = r.json() if r.text else {}
    except Exception:
        data = {}
    return ping_result(True, "connected", True, "Connected", lat), (data if isinstance(data, dict) else {})
