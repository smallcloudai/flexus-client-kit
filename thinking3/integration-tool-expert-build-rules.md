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
# Integration-Tool-Expert Build Rules

Last updated: 2026-02-24

## Purpose

Define one implementation standard for building:
- provider SDK adapters;
- integration classes and methods;
- bot-specific tools;
- expert-level tool permissions and tool prompt injection.

The goal is reliability, predictable composition, and low maintenance cost.

## Architecture Layers

Default architecture is `single integration class` with internal separation of concerns.

1. `BaseIntegration` contract (`integrations/base_integration.py`): shared method signatures and validation/error conventions.
2. `ProviderIntegration` (`integrations/*`): concrete provider implementation inheriting `BaseIntegration`.
   - Internal `raw sdk` methods: low-level HTTP/auth/pagination/retry.
   - Internal `normalize` methods: provider payload -> normalized output contract.
3. `Tool` (`CloudTool` + handler): bot capability assembled from integration methods.
4. `Bot` (`manifest.json` + runtime registry): selects which tools are installed.
5. `Expert` (`fexp_allow_tools`/`fexp_block_tools`): selects which installed tools are allowed.

No cross-layer shortcuts are allowed.

### Optional split into separate facade

Separate facade file/class is optional, not mandatory.
Use it only when one of these triggers is true:
- one provider integration is reused by many tools with different operation surfaces;
- normalization logic becomes large enough to reduce readability/testability;
- provider transport/auth concerns start leaking into tool business logic;
- teams need independent ownership for transport layer and capability layer.

## 1) Raw SDK Rules

### 1.1 Raw SDK responsibilities

Raw SDK code must only do:
- authentication and token refresh;
- provider request signing/headers;
- retries/backoff and timeout;
- pagination cursors;
- provider response parsing into typed objects.

Raw SDK code must not do:
- bot business logic;
- tool prompt formatting;
- expert-level filtering/routing.

### 1.2 Method naming and stability

- Method names must be deterministic and provider-scoped.
- Use `provider.resource.action` naming internally.
- Every externally exposed method must have a stable `method_id` with version suffix:
  - example: `meta.ads.get_campaigns.v1`.

### 1.3 Input/output discipline

- Every method has:
  - input schema;
  - output schema;
  - deterministic mapping from provider payload to normalized output.
- Validate input before provider call.
- Validate normalized output before returning.

### 1.4 Error model

- Do not leak raw provider exceptions to tools.
- Map provider errors into normalized error codes:
  - `AUTH_REQUIRED`
  - `AUTH_FORBIDDEN`
  - `RATE_LIMITED`
  - `VALIDATION_FAILED`
  - `NOT_FOUND`
  - `PROVIDER_UNAVAILABLE`
  - `TIMEOUT`
  - `INTERNAL_ERROR`
- Include provider diagnostics in metadata (`provider_code`, `http_status`, request id).

### 1.5 Reliability requirements

- Explicit timeout per call.
- Retry only retriable failures.
- Idempotency annotation per method:
  - `safe_read`, `idempotent_write`, `non_idempotent_write`.
- No silent fallback to another method/provider.

## 2) Unified Internal Contract: Integration -> Tool

### 2.1 Required integration interface

Each `ProviderIntegration` must implement:
- `describe_methods() -> list[MethodSpec]`
- `call(req: IntegrationCall) -> IntegrationResult`
- `auth_status() -> AuthStatus` (recommended)

### 2.2 MethodSpec contract

`MethodSpec` must contain:
- `method_id`: stable id with version
- `provider`: provider name
- `input_schema`: JSON schema
- `output_schema`: JSON schema
- `capabilities`: tags (`search`, `ads`, `metrics`, `read`, `write`, ...)
- `auth_scopes`: required scopes
- `rate_limit_hint`: provider limit info
- `idempotency`: write/read semantics
- `cost_hint`: relative cost metadata
- `deprecated`: bool
- `replacement_method_id`: optional

### 2.3 IntegrationCall contract

`IntegrationCall` fields:
- `trace_id`: string
- `method_id`: string
- `args`: object
- `timeout_ms`: integer
- `retry_policy`: object (`max_retries`, `backoff_ms`)
- `cursor`: optional string
- `dry_run`: optional bool

### 2.4 IntegrationResult contract

`IntegrationResult` fields:
- `ok`: bool
- `data`: normalized payload (when `ok=true`)
- `raw`: optional provider payload (debug/audit only)
- `meta`:
  - `provider_request_id`
  - `latency_ms`
  - `next_cursor`
  - `rate_limit_remaining`
  - `cost_units`
  - `provenance` (`source_type`, `source_ref`)
- `error` (when `ok=false`):
  - `code`
  - `message`
  - `provider_code`
  - `http_status`
  - `retriable`

### 2.5 Mandatory validation rules

- Reject unknown `method_id`.
- Reject args not matching `input_schema`.
- Reject output not matching `output_schema`.
- Reject tool call to methods outside tool allowlist.

## 3) Tool Declaration Contract in Bot

### 3.1 What a tool is

A tool is a bot-facing capability:
- declared as `CloudTool(name, description, parameters, strict)`;
- implemented via one handler (`called_by_model`) that orchestrates one or more integration methods.

### 3.2 What is generated vs handwritten

Generated:
- OpenAI tool JSON schema from method specs;
- operation list table;
- baseline help skeleton;
- baseline system prompt skeleton.

Handwritten (required):
- final tool name and intent description;
- operation semantics (`op` meaning and business constraints);
- fail-fast rules specific to this tool;
- safety constraints and prohibited behavior;
- concise usage examples mapped to real operations.

### 3.3 Tool call shape (recommended)

Use one standard envelope:
- `tool_name(op="<operation>", args={...})`

Rules:
- `op="help"` and `op="status"` are mandatory.
- Query-like tools should expose `list_methods` and `list_providers`.
- Unknown `op` must fail with explicit error and help hint.

### 3.4 Tool help template

Each tool must provide:
- one-line purpose;
- operation list with required args;
- minimal examples for top 3 operations;
- explicit fail-fast notes.

Template sections:
1. `Purpose`
2. `Operations`
3. `Arguments`
4. `Validation and failure behavior`
5. `Examples`

### 3.5 Tool system prompt template

Each tool should have a dedicated prompt block (`tool_<tool_name>.md`) including:
- when to use this tool;
- when not to use this tool;
- mandatory argument discipline;
- interpretation rules for outputs;
- failure handling and retry rules;
- output quality checklist.

Keep tool prompts short and operational. Do not duplicate provider SDK details.

## 4) Expert Tool Permissions and Tool Prompt Injection

### 4.1 Permission model

- Bot installs tools via `manifest.json -> tools`.
- Expert restricts usage via:
  - `fexp_allow_tools`
  - `fexp_block_tools`

Policy:
- Prefer explicit allowlists.
- For experts requiring tool-prompt injection, do not use wildcard allowlists.

### 4.2 Injection model

During expert prompt build:
1. Parse explicit tool names from `fexp_allow_tools`.
2. For each allowed tool, load `prompts/tool_<tool_name>.md`.
3. Inject blocks after expert body/skills and before global common prompts.

### 4.3 Injection fail-fast

- If a tool is in explicit allowlist and prompt file is missing: raise build error.
- If tool prompt exists but tool is not installed by bot: raise build error.
- If tool appears in blocklist and allowlist: raise build error.

## 5) Versioning and Change Policy

- Breaking change => new method id version (`...v2`), never silent replacement.
- Keep previous version active until all dependent tools migrate.
- Tool contract changes must update:
  - tool help
  - tool prompt
  - tests
  - migration notes

## 6) Testing Standard (Mandatory)

For each new provider method:
- schema validation test (input/output);
- auth failure test;
- rate limit behavior test;
- pagination test (if applicable).

For each tool:
- op routing tests;
- allowlist enforcement tests;
- normalized output contract tests;
- fail-fast message tests.

For expert prompt assembly:
- tool prompt injection positive test;
- missing prompt fail-fast test;
- allow/block conflict test.

## 7) Observability and Provenance

- Every tool call must emit `trace_id`.
- Each integration result must include provenance:
  - `source_type`: `api`, `artifact`, `tool_output`, `event_stream`, `expert_handoff`, `user_directive`
  - `source_ref`: concrete endpoint/doc/query identifier.
- Store provider request id when available.

## 8) Security and Governance

- Least-privilege OAuth scopes only.
- No credentials in prompts, policy docs, or tool output.
- Redact sensitive fields in `raw` payload mode.
- Explicitly mark risky operations as confirmation-required when needed.

## 9) Definition of Done for New Integration/Tool

A new integration/tool pair is done only when:
- integration methods expose `MethodSpec` and pass schema tests;
- tool supports `help`/`status` and operation validation;
- tool is registered in bot runtime registry;
- expert allow/block policy is explicit;
- tool prompt injection is configured and validated;
- logs include trace/provenance metadata.

## 10) BaseIntegration Final Skeleton

Use this as the default implementation template for new provider integrations.

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

### Notes for implementers

- Keep provider-specific HTTP/auth code inside `_call_provider` and private helper methods (`_raw_*`).
- Always normalize provider payload before returning `IntegrationResult(data=...)`.
- Never return provider exception objects directly.
- Never skip schema validation in `call()`.
