import re

import pytest

from flexus_client_kit.integrations import fi_discord_community as dc


@pytest.mark.parametrize(
    "raw,expect",
    [
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("", False),
        ("0", False),
    ],
)
def test_setup_truthy(raw: str, expect: bool) -> None:
    assert dc.setup_truthy(raw) is expect


def test_parse_snowflake() -> None:
    assert dc.parse_snowflake(" 12345 ") == 12345
    assert dc.parse_snowflake("") is None
    assert dc.parse_snowflake("abc") is None


def test_discord_bot_api_key_from_external_auth() -> None:
    assert dc.discord_bot_api_key_from_external_auth({}) == ""
    assert dc.discord_bot_api_key_from_external_auth({"discord_manual": {"api_key": "  t  "}}) == "t"
    assert dc.discord_bot_api_key_from_external_auth({"discord": {"api_key": "x"}}) == "x"
    assert (
        dc.discord_bot_api_key_from_external_auth(
            {"discord_manual": {"api_key": "manual"}, "discord": {"api_key": "oauth"}},
        )
        == "manual"
    )


def test_truncate_message() -> None:
    long = "x" * 3000
    out = dc.truncate_message(long, limit=100)
    assert len(out) <= 100
    assert "truncated" in out


def test_message_has_invite() -> None:
    assert dc.message_has_invite("hello discord.gg/abc here")
    assert dc.message_has_invite("https://discord.com/invite/xyz")
    assert not dc.message_has_invite("no link here")


def test_match_blocked_url() -> None:
    pats = [re.compile(r"malware\.com", re.I)]
    assert dc.match_blocked_url("see malware.com", pats)
    assert not dc.match_blocked_url("safe", pats)


def test_compile_url_patterns_skips_bad() -> None:
    out = dc.compile_url_patterns("foo\\.bar\n(\n")
    assert len(out) == 1


def test_guild_matches() -> None:
    assert dc.guild_matches(None, 1) is False
    class G:
        id = 5
    assert dc.guild_matches(G(), 5) is True
    assert dc.guild_matches(G(), None) is True
