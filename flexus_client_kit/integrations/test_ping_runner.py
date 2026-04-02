import types
import ast
from pathlib import Path

import pytest


REQUIRE_METADATA = {
    "fi_newsapi.py",
    "fi_resend.py",
    "fi_slack.py",
    "fi_telegram.py",
    "fi_discord2.py",
    "fi_linkedin.py",
    "fi_linkedin_b2b.py",
    "fi_facebook2.py",
    "fi_facebook.py",
    "fi_github.py",
    "fi_gmail.py",
    "fi_google_calendar.py",
    "fi_google_sheets.py",
    "fi_google_analytics.py",
    "fi_jira.py",
    "fi_shopify.py",
}


def _read_metadata(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "INTEGRATION_METADATA" and isinstance(node.value, ast.Dict):
                return {k.value: v for k, v in zip(node.value.keys, node.value.values) if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    return None


def test_external_integrations_have_metadata_block():
    root = Path(__file__).resolve().parent
    files = sorted(root.rglob("fi_*.py"))
    assert files, "No integration files found"
    for p in files:
        md = _read_metadata(p)
        if p.name not in REQUIRE_METADATA:
            assert md is None, f"Unexpected INTEGRATION_METADATA in internal module {p}"
            continue
        assert md is not None, f"Missing INTEGRATION_METADATA in {p}"
        assert "provider" in md, f"Missing provider in {p}"
        assert "auth_kind" in md, f"Missing auth_kind in {p}"
        assert "env_keys" in md, f"Missing env_keys in {p}"
        assert "supports_ping" in md, f"Missing supports_ping in {p}"


def test_discover_integrations_with_metadata_reads_supports_ping():
    from flexus_client_kit.integrations import ping_runner

    rows = ping_runner.discover_integrations_with_metadata()
    by_module = {x["module"]: x for x in rows}
    assert by_module["fi_newsapi"]["supports_ping"] is True
    assert by_module["fi_resend"]["supports_ping"] is True
    assert by_module["fi_github"]["supports_ping"] is False
    assert "fi_crm" not in by_module


def test_to_full_module_name_handles_nested_paths():
    from flexus_client_kit.integrations import ping_runner

    assert ping_runner._to_full_module_name("fi_newsapi") == "flexus_client_kit.integrations.fi_newsapi"
    assert ping_runner._to_full_module_name("facebook.fi_facebook") == "flexus_client_kit.integrations.facebook.fi_facebook"
    assert ping_runner._to_full_module_name("flexus_client_kit.integrations.fi_resend") == "flexus_client_kit.integrations.fi_resend"


class _FakeResponse:
    def __init__(self, status_code=200, text="", json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


class _FakeAsyncClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *_args, **_kwargs):
        return self._response


@pytest.mark.asyncio
async def test_runner_lazy_load_and_fallbacks(monkeypatch):
    from flexus_client_kit.integrations import ping_runner

    loaded = []

    async def _status_handler(self, _toolcall, args):
        if args.get("op") == "status":
            return "status ok"
        return "bad op"

    class StatusOnlyIntegration:
        def __init__(self, _fclient, _rcx):
            pass

        called_by_model = _status_handler

    m1 = types.SimpleNamespace(
        INTEGRATION_METADATA={
            "provider": "status_only",
            "auth_kind": "api_key",
            "env_keys": ["STATUS_ONLY_TOKEN"],
            "supports_ping": False,
        },
        IntegrationStatusOnly=StatusOnlyIntegration,
    )

    m2 = types.SimpleNamespace(
        INTEGRATION_METADATA={
            "provider": "no_ping",
            "auth_kind": "none",
            "env_keys": [],
            "supports_ping": False,
        },
        IntegrationNoPing=type("IntegrationNoPing", (), {"__init__": lambda self, _fclient, _rcx: None}),
    )

    def _fake_import(name):
        loaded.append(name)
        if name.endswith("fi_status_only"):
            return m1
        if name.endswith("fi_no_ping"):
            return m2
        raise ImportError(name)

    monkeypatch.setattr(ping_runner.importlib, "import_module", _fake_import)

    r1 = await ping_runner.run_single("fi_status_only", env={"STATUS_ONLY_TOKEN": "tok"})
    assert r1["ok"] is True
    assert r1["status"] == "connected"
    assert r1["provider"] == "status_only"
    assert r1["module"] == "fi_status_only"

    r2 = await ping_runner.run_single("fi_no_ping", env={})
    assert r2["ok"] is False
    assert r2["status"] == "not_covered"
    assert r2["provider"] == "no_ping"
    assert r2["module"] == "fi_no_ping"

    assert loaded == [
        "flexus_client_kit.integrations.fi_status_only",
        "flexus_client_kit.integrations.fi_no_ping",
    ]


@pytest.mark.asyncio
async def test_runner_import_error_is_reported_not_raised(monkeypatch):
    from flexus_client_kit.integrations import ping_runner

    def _boom(name):
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(ping_runner.importlib, "import_module", _boom)
    r = await ping_runner.run_single("facebook.fi_facebook", env={})
    assert r["ok"] is False
    assert r["status"] == "error"
    assert "import failed" in r["note"]
    assert r["module"] == "facebook.fi_facebook"


@pytest.mark.asyncio
async def test_newsapi_metadata_and_ping_happy_path(monkeypatch):
    from flexus_client_kit.integrations import fi_newsapi
    from flexus_client_kit.integrations import ping_utils

    md = fi_newsapi.INTEGRATION_METADATA
    assert md["provider"] == "newsapi"
    assert md["auth_kind"] == "api_key"
    assert md["supports_ping"] is True

    fake = _FakeResponse(status_code=200, text='{"status":"ok"}', json_data={"sources": [{"id": "a"}, {"id": "b"}]})
    monkeypatch.setattr(ping_utils.httpx, "AsyncClient", lambda **_kwargs: _FakeAsyncClient(fake))

    rcx = types.SimpleNamespace(external_auth={"newsapi": {"api_key": "news_tok"}})
    r = await fi_newsapi.IntegrationNewsapi(rcx).ping()

    assert r["ok"] is True
    assert r["status"] == "connected"
    assert r["can_read"] is True
    assert "sources=2" in r["note"]
    assert isinstance(r["latency_ms"], int)


@pytest.mark.asyncio
async def test_resend_metadata_and_ping_happy_path(monkeypatch):
    from flexus_client_kit.integrations import fi_resend
    from flexus_client_kit.integrations import ping_utils

    md = fi_resend.INTEGRATION_METADATA
    assert md["provider"] == "resend"
    assert md["auth_kind"] == "api_key"
    assert md["supports_ping"] is True

    fake = _FakeResponse(status_code=200, text='{"data":[]}', json_data={"data": [{"id": "d1"}]})
    monkeypatch.setattr(ping_utils.httpx, "AsyncClient", lambda **_kwargs: _FakeAsyncClient(fake))

    rcx = types.SimpleNamespace(external_auth={"resend": {"api_key": "res_tok"}})
    r = await fi_resend.IntegrationResend(None, rcx, domains={}).ping()

    assert r["ok"] is True
    assert r["status"] == "connected"
    assert r["can_read"] is True
    assert "domains=1" in r["note"]
    assert isinstance(r["latency_ms"], int)
