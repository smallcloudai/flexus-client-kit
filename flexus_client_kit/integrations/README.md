# Integrations Architecture

This directory defines integration primitives used by bot tools.

## Scope (Current Mode)

Current architecture supports multiple integration modes.

Implemented modes in this codebase:
- request/response tool calls to external HTTP APIs;
- inbound webhook/event callbacks from external providers;
- scheduled/polling sync flows;
- OAuth-backed delegated integrations.

Not yet standardized as first-class integration modes:
- long-lived streaming/WebSocket feeds;
- queue-consumer integrations (Kafka/SQS/Rabbit style);
- full bidirectional state sync with conflict reconciliation.

For non-standardized modes, require explicit design review before implementation.

## Integration Mode Types

Use these architectural categories when designing a new integration:

1. `Request/Response`:
   - tool triggers provider method call and immediately gets result;
   - typical for analytics, search, CRUD-like API operations.

2. `Inbound Webhook/Event-Driven`:
   - provider pushes events to platform endpoint;
   - integration handler maps inbound event into bot/runtime actions.

3. `Scheduled/Polling Sync`:
   - integration periodically fetches provider state and upserts local records;
   - requires idempotent upsert keys and checkpoint/cursor discipline.

4. `Automation-on-Internal-Events`:
   - integration reacts to internal ERP/runtime events and performs provider actions;
   - must define strict trigger filters and replay behavior.

5. `Streaming/Queue/Bidirectional` (advanced):
   - only with explicit architecture approval;
   - requires dedicated reliability model (ordering, dedup, replay, conflict resolution).

## Layering Model

Default model is a single provider integration class:

1. `BaseIntegration` contract (shared interface and validation behavior).
2. `ProviderIntegration(BaseIntegration)` implementation.
   - private raw methods (`_raw_*`) for provider HTTP/auth/pagination;
   - normalization methods for provider payload to internal contract.
3. Tool handler composes capability from integration methods.

Tools must not call raw HTTP directly.

## BaseIntegration Contract

Every provider integration must expose:
- `describe_methods() -> list[MethodSpec]`
- `auth_status() -> dict[str, Any]`
- `call(req: IntegrationCall) -> IntegrationResult`

### MethodSpec (required fields)

- `method_id` (versioned, for example `meta.ads.get_campaigns.v1`)
- `provider`
- `input_schema`
- `output_schema`
- `capabilities`
- `auth_scopes`
- `rate_limit_hint`
- `idempotency`
- `cost_hint`
- `deprecated`
- `replacement_method_id`

### IntegrationCall (required fields)

- `trace_id`
- `method_id`
- `args`
- `timeout_ms`
- `retry_policy`
- `cursor` (optional)
- `dry_run` (optional)

### IntegrationResult (required fields)

- `ok`
- `data` (when `ok=true`)
- `raw` (optional)
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

## Validation and Fail-Fast Rules

- Reject unknown `method_id`.
- Validate input against `input_schema` before provider call.
- Validate normalized output against `output_schema` before returning.
- Never leak provider exception objects to tool output.
- Never silently fallback to another provider or method.
- Use explicit error codes (`AUTH_REQUIRED`, `RATE_LIMITED`, `TIMEOUT`, etc.).

## Versioning Rules

- Breaking method changes require a new `method_id` version (`...v2`).
- Never silently redefine `...v1`.
- Keep old versions active until dependent tools are migrated.

## Tool Composition Rules

Tools are bot-specific capabilities assembled from integration methods.

Recommended tool call envelope:
- `tool_name(op="<operation>", args={...})`

Required operations:
- `help`
- `status`

Query-oriented tools should also expose:
- `list_methods`
- `list_providers`

## Expert Access Rules

- Bot installs tools via `manifest.json -> tools`.
- Expert access is restricted via `fexp_allow_tools` / `fexp_block_tools`.
- Prefer explicit allowlists.
- For tool prompt injection, wildcard allowlists are not allowed.

## Tool Prompt Injection

For each allowed tool, load and inject:
- `prompts/tool_<tool_name>.md`

Injection position in expert prompt:
- after expert body and skills;
- before global common prompt blocks.

Fail-fast:
- allowed tool without matching tool prompt file -> build error.
- tool prompt exists but tool is not installed by bot -> build error.
- same tool appears in both allow and block -> build error.
