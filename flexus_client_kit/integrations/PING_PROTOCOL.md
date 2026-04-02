# Ping Protocol

This is a lightweight way to check whether an integration is minimally working.

## Goal

- Keep checks decentralized: each `fi_*.py` owns its own connectivity check.
- Keep checks cheap: one small real API call.
- Generate `INTEGRATIONS.md` for developers and users.

## Integration contract

External provider integrations should expose:

```python
INTEGRATION_METADATA = {
    "provider": "newsapi",
    "auth_kind": "api_key",  # api_key | oauth2 | none
    "env_keys": ["NEWSAPI_API_KEY", "NEWSAPI_KEY"],
    "supports_ping": True,
}
```

Internal utility integrations may skip metadata for now.

When `supports_ping` is true:

```python
async def ping(self) -> dict:
    return {
        "ok": True,
        "status": "connected",      # connected | error | expired | missing_credentials | not_covered
        "can_read": True,
        "note": "Connected, ...",
        "latency_ms": 123,
    }
```

`called_by_model()` must stay independent from `ping()`.

## Shared helper

Use `flexus_client_kit.integrations.ping_utils` to avoid duplicate boilerplate:

- `ping_result(...)`
- `ping_http_get_json(...)`

Keep integration `ping()` methods short and provider-specific.

## Runner

Use `flexus_client_kit.integrations.ping_runner`:

- lazy-imports requested integration modules only,
- injects `.env` / `.env.local` values into mock `external_auth`,
- runs `ping()` if present,
- falls back to `called_by_model(op="status")` when needed,
- emits JSON and writes `INTEGRATIONS.md`.

Example:

```bash
python -m flexus_client_kit.integrations.ping_runner fi_newsapi fi_resend --out-md INTEGRATIONS.md
```

## OAuth integrations

Runner does not perform OAuth login flow.

For local checks, paste a valid access token into `.env.local` using keys from `env_keys`.
That is enough for connectivity checks and keeps the dev loop fast.

## Tests

Run protocol tests:

```bash
pytest -q flexus_client_kit/integrations/test_ping_runner.py
```
