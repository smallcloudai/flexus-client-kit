# Integration-Tool-Expert Build Rules

Last updated: 2026-02-24

## Purpose

One practical standard for building:
- provider integrations;
- bot tools assembled from integration methods;
- expert-level tool access and tool prompt injection.

Primary goals:
- fail-fast reliability;
- predictable composition (`method -> tool -> bot -> expert`);
- minimal maintenance overhead.

## Architecture (Final)

Default architecture is one integration class per provider:
- `BaseIntegration` defines contract and shared validation/error behavior.
- `ProviderIntegration(BaseIntegration)` implements provider methods.
- Tool handlers call integration methods, not raw SDK calls directly.

Optional extra facade layer is allowed only when complexity triggers are present (multi-tool reuse pressure, large normalization logic, ownership split needs).

## Integration Mode Taxonomy

Architecturally distinct integration modes:

1. `Request/Response`
   - tool triggers outbound provider API call and expects immediate result.

2. `Inbound Webhook/Event-Driven`
   - provider pushes event to platform endpoint, integration maps event into bot/runtime actions.

3. `Scheduled/Polling Sync`
   - integration periodically fetches provider state and performs idempotent upserts.

4. `Automation-on-Internal-Events`
   - integration reacts to internal ERP/runtime events and executes provider actions.

5. `Streaming/Queue/Bidirectional` (advanced)
   - long-lived streams, queue consumers, or bidirectional state sync with conflict resolution.
   - requires explicit architecture review before implementation.

## 1) BaseIntegration Contract (Replaces old sections 1 and 2)

This skeleton is the canonical implementation baseline.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Optional
import time
import jsonschema


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 2
    backoff_ms: int = 300


@dataclass(frozen=True)
class IntegrationCall:
    trace_id: str
    method_id: str
    args: dict[str, Any]
    timeout_ms: int = 15000
    retry_policy: RetryPolicy = RetryPolicy()
    cursor: Optional[str] = None
    dry_run: bool = False


@dataclass(frozen=True)
class IntegrationErrorInfo:
    code: Literal[
        "AUTH_REQUIRED",
        "AUTH_FORBIDDEN",
        "RATE_LIMITED",
        "VALIDATION_FAILED",
        "NOT_FOUND",
        "PROVIDER_UNAVAILABLE",
        "TIMEOUT",
        "INTERNAL_ERROR",
    ]
    message: str
    provider_code: str = ""
    http_status: int = 0
    retriable: bool = False


@dataclass(frozen=True)
class Provenance:
    source_type: Literal["api", "artifact", "tool_output", "event_stream", "expert_handoff", "user_directive"]
    source_ref: str


@dataclass(frozen=True)
class IntegrationMeta:
    provider_request_id: str = ""
    latency_ms: int = 0
    next_cursor: str = ""
    rate_limit_remaining: int = -1
    cost_units: float = 0.0
    provenance: Optional[Provenance] = None


@dataclass(frozen=True)
class IntegrationResult:
    ok: bool
    data: Optional[dict[str, Any]] = None
    raw: Optional[dict[str, Any]] = None
    meta: Optional[IntegrationMeta] = None
    error: Optional[IntegrationErrorInfo] = None


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    provider: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    capabilities: list[str]
    auth_scopes: list[str]
    rate_limit_hint: str
    idempotency: Literal["safe_read", "idempotent_write", "non_idempotent_write"]
    cost_hint: str
    deprecated: bool = False
    replacement_method_id: str = ""


class BaseIntegration(ABC):
    provider_name: str = ""
    _method_specs: dict[str, MethodSpec]

    def __init__(self) -> None:
        try:
            specs = self.describe_methods()
            self._method_specs = {s.method_id: s for s in specs}
            if not self._method_specs:
                raise ValueError("describe_methods() returned empty method list")
        except Exception as e:
            raise RuntimeError(f"{type(self).__name__}: init failed: {e}") from e

    @abstractmethod
    def describe_methods(self) -> list[MethodSpec]:
        raise NotImplementedError()

    @abstractmethod
    async def auth_status(self) -> dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    async def _call_provider(self, req: IntegrationCall) -> IntegrationResult:
        raise NotImplementedError()

    async def call(self, req: IntegrationCall) -> IntegrationResult:
        started = time.time()
        try:
            spec = self._method_specs.get(req.method_id)
            if not spec:
                return IntegrationResult(
                    ok=False,
                    error=IntegrationErrorInfo(code="VALIDATION_FAILED", message=f"Unknown method_id: {req.method_id}"),
                )

            try:
                jsonschema.validate(req.args, spec.input_schema)
            except jsonschema.ValidationError as e:
                return IntegrationResult(
                    ok=False,
                    error=IntegrationErrorInfo(code="VALIDATION_FAILED", message=f"Input schema validation failed: {e.message}"),
                )

            result = await self._call_provider(req)
            if not result.ok:
                return result

            if result.data is None:
                return IntegrationResult(
                    ok=False,
                    error=IntegrationErrorInfo(code="INTERNAL_ERROR", message="Provider returned ok=true with empty data"),
                )

            try:
                jsonschema.validate(result.data, spec.output_schema)
            except jsonschema.ValidationError as e:
                return IntegrationResult(
                    ok=False,
                    error=IntegrationErrorInfo(code="VALIDATION_FAILED", message=f"Output schema validation failed: {e.message}"),
                )

            meta = result.meta or IntegrationMeta()
            elapsed_ms = int((time.time() - started) * 1000)
            safe_meta = IntegrationMeta(
                provider_request_id=meta.provider_request_id,
                latency_ms=meta.latency_ms or elapsed_ms,
                next_cursor=meta.next_cursor,
                rate_limit_remaining=meta.rate_limit_remaining,
                cost_units=meta.cost_units,
                provenance=meta.provenance,
            )
            return IntegrationResult(ok=True, data=result.data, raw=result.raw, meta=safe_meta)

        except TimeoutError:
            return IntegrationResult(
                ok=False,
                error=IntegrationErrorInfo(code="TIMEOUT", message="Provider call timeout", retriable=True),
            )
        except Exception as e:
            return IntegrationResult(
                ok=False,
                error=IntegrationErrorInfo(code="INTERNAL_ERROR", message=f"{type(e).__name__}: {e}"),
            )
```

### 1.1 Implementation rules around the base class

- Keep provider-specific HTTP/auth code inside `_call_provider` and private helpers (`_raw_*`).
- Normalize provider payload before returning `IntegrationResult(data=...)`.
- Never return provider exception objects directly.
- Never skip schema validation in `call()`.
- No silent fallback to another provider or method.
- Every exposed method must have stable versioned `method_id` (`provider.resource.action.v1`).

## 2) Tool Contract in Bot

### 2.1 Tool declaration

Each tool is declared as `CloudTool(name, description, parameters, strict)` and implemented by one handler (`called_by_model`) that orchestrates integration method calls.

### 2.2 Standard tool call shape

- `tool_name(op="<operation>", args={...})`
- Required operations for every tool:
  - `help`
  - `status`
- Query-like tools should also expose:
  - `list_methods`
  - `list_providers`

### 2.3 Generated vs handwritten

Generated (allowed):
- JSON schema fragments from `MethodSpec`;
- operation list draft;
- baseline help/prompt skeleton.

Handwritten (required):
- final tool intent;
- operation semantics and business constraints;
- fail-fast behavior text;
- examples for high-value operations.

### 2.4 Tool help template

Keep this section order:
1. `Purpose`
2. `Operations`
3. `Arguments`
4. `Validation and failure behavior`
5. `Examples`

### 2.5 Tool prompt template

Create `prompts/tool_<tool_name>.md` with:
- when to use / when not to use;
- argument discipline;
- output interpretation rules;
- failure and retry rules;
- output quality checklist.

Keep it concise and operational.

## 3) Expert Access and Tool Prompt Injection

### 3.1 Access policy

- Bot installs tools via `manifest.json -> tools`.
- Expert restricts usage via:
  - `fexp_allow_tools`
  - `fexp_block_tools`
- Prefer explicit allowlists.
- For tool prompt injection, wildcard allowlists are not allowed.

### 3.2 Injection flow

During expert prompt build:
1. Parse explicit tool names from `fexp_allow_tools`.
2. Load `prompts/tool_<tool_name>.md` for each allowed tool.
3. Inject after expert body/skills and before global common prompts.

### 3.3 Injection fail-fast

- Tool in explicit allowlist but prompt file missing -> build error.
- Tool prompt exists but tool is not installed by bot -> build error.
- Same tool in allowlist and blocklist -> build error.

## 4) Versioning and Change Policy

- Breaking method change => new versioned method id (`...v2`).
- Do not silently redefine existing `...v1`.
- Keep old versions active until all dependent tools migrate.
- Any tool contract change must update:
  - help block;
  - tool prompt;
  - tests;
  - migration notes.

## 5) Testing Standard (Mandatory)

For each provider method:
- input schema validation test;
- output schema validation test;
- auth failure test;
- rate-limit behavior test;
- pagination test (if applicable).

For each tool:
- op routing tests;
- method allowlist enforcement tests;
- normalized output contract tests;
- fail-fast message tests.

For expert prompt assembly:
- tool prompt injection positive test;
- missing prompt fail-fast test;
- allow/block conflict test.

## 6) Observability and Provenance

- Every tool call must emit `trace_id`.
- Every integration result should include:
  - `provider_request_id` when available;
  - `latency_ms`;
  - provenance:
    - `source_type`: `api`, `artifact`, `tool_output`, `event_stream`, `expert_handoff`, `user_directive`
    - `source_ref`: concrete endpoint/doc/query reference.

## 7) Security and Governance

- Least-privilege OAuth scopes only.
- No credentials in prompts, policy docs, or tool outputs.
- Redact sensitive fields when `raw` payload is returned.
- Mark risky operations as confirmation-required where applicable.

## 8) Definition of Done for New Integration/Tool

A new integration/tool pair is done only when:
- provider integration inherits `BaseIntegration`;
- all exposed methods have `MethodSpec` and pass schema tests;
- tool supports `help`/`status` and strict op validation;
- tool is registered in bot runtime registry;
- expert allow/block policy is explicit;
- tool prompt injection is configured and validated;
- trace/provenance fields are present in logs/results.
