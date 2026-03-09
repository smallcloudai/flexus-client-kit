---
name: mvp-validation-criteria
description: MVP validation criteria design — define what success looks like for the MVP phase, including pilot metrics, PMF signals, and go/no-go thresholds
---

You define the quantitative and qualitative criteria that determine whether the MVP has validated product-market fit sufficiently to justify scaling investment. Treat MVP validation criteria as a **pre-registered decision contract**, not as a post-launch narrative. Before any pilot starts, lock the definitions of success, failure, and invalid evidence states. Your objective is to reduce false confidence, not to maximize the probability of a `go` verdict.

Core mode: pre-define everything. The success bar must be set before launch, not after seeing results. Post-hoc success bar adjustment is one of the most common ways teams fool themselves into thinking they have PMF when they don't. PMF is not one number — it is a composite claim requiring aligned evidence across behavior, retention, economics, and user-reported value.

**Decision outcomes:**
- `go`: all mandatory quality gates pass, primary evidence meets thresholds, guardrails are within allowed bounds.
- `no_go`: one or more disqualifying conditions met under valid evidence.
- `rework`: evidence is valid but contradictory or incomplete — additional work required before commitment.
- `invalid_test`: evidence validity fails (SRM, instrumentation integrity, insufficient exposure) — no business verdict allowed.

## Methodology

### Step 1: Activate required strategy context
```
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

### Step 2: Lock validation window and decision checkpoints
Define `validation_window_days` and checkpoint cadence. You may monitor continuously, but final decision logic must be declared before first exposure. Never change thresholds after first readout without recording a formal protocol revision.

### Step 3: Define signal families
PMF is a composite — require at minimum:
1. **Retention:** users coming back. B2B SaaS benchmarks: Week-1 >60%, Month-1 >40%, Month-3 >25%. Define cohort, observation window, and minimum sample.
2. **Engagement:** users completing the core job repeatedly. Define the "core action" and what frequency indicates habitual use.
3. **Satisfaction:** do users recommend? Sean Ellis test: >40% "very disappointed" is PMF proxy. NPS ≥50 is a stronger signal than NPS ≥30.
4. **Expansion:** upgrade requests, unprompted referrals, pilot customers requesting commercial contract early.
5. **Economics** (when monetization is central to hypothesis): conversion rate from pilot to paid, ACV achieved vs. target.

For each signal: define metric, cohort, observation window, minimum sample/evidence requirement, and predeclared threshold.

### Step 4: Declare decision protocol
Set before launch and do not change without formal revision:
- Methodology mode: `fixed_horizon` or `sequential_adjusted`. If monitoring continuously, use sequential-adjusted mode. If using fixed-horizon, prohibit peeking-based decisioning.
- Alpha (type-I error budget), power, MDE (minimum detectable effect), practical significance floor.
- Multiplicity control: if evaluating many metrics or segments, apply Benjamini-Hochberg or Bonferroni correction. Post-hoc metric fishing is invalid.

### Step 5: Quality gates (evaluate before interpretation)
If any gate fails → `invalid_test` regardless of top-line metrics:
- SRM (Sample Ratio Mismatch): if observed variant allocation materially deviates from expected split, the test is invalid.
- Schema violation tolerance: declared maximum acceptable schema error rate.
- Event drop tolerance: maximum acceptable event drop rate.
- Minimum observation depth: minimum sessions/users before any inference.

### Step 6: Define gate-based outcomes
Create explicit go_rule, no_go_rule, and recycle_rule that combine multiple signal families and quality constraints. Decision flow:
1. Evaluate quality gates first.
2. Quality fails → `invalid_test`.
3. Quality passes → evaluate `go_rule`.
4. `go_rule` fails → evaluate `no_go_rule`.
5. Neither clearly applies → `rework` with required next evidence.

### Step 7: Mixed-method arbitration
If quant passes but qual indicates unresolved core-value mismatch → `rework` with required follow-up evidence. If qual enthusiasm is strong but retention/economics fail → `no_go` or `rework` depending on severity and runway. Do not let enthusiasm override behavioral evidence.

### Step 8: Define failure mode taxonomy
Document specifically what observations would indicate:
- **Wrong ICP:** target segment doesn't have the problem we thought.
- **Wrong solution:** problem exists but product doesn't solve it well.
- **Wrong channel:** product and ICP are right, reaching the wrong people.
- **Wrong timing:** market not ready.

### Interpretation guardrails
- Statistical significance alone is not sufficient for a `go` call. Require practical significance against predeclared MDE.
- Guardrails are veto constraints. Primary metric improvement does not override meaningful degradation in guardrails (reliability, churn risk, support burden, payment failure rates).
- Require lagging confirmation for PMF-level decisions. Leading indicators can support early directionality, but scale decisions require retention durability evidence.
- Segment-specific pass conditions: do not let blended averages hide target ICP segment underperformance.

## Anti-Patterns

#### Post-Hoc Threshold Rewriting
**What it looks like:** You redefine success after seeing data ("we almost hit target, let's relax the threshold").
**Detection signal:** Thresholds in decision notes differ from pre-launch criteria version.
**Consequence:** False `go` rates increase; narratives become non-reproducible.
**Mitigation:** Freeze initial thresholds in versioned protocol. Any change must record reason, timestamp, approver, and "protocol_changed_post_launch" label.

#### Peek-and-Ship
**What it looks like:** Checking results repeatedly and launching at the first favorable snapshot.
**Detection signal:** No predeclared stopping logic; significance appears early and disappears later.
**Consequence:** Inflated false positives and unstable post-launch performance.
**Mitigation:** Predeclare methodology mode. Block final `go` until declared decision checkpoint criteria are met.

#### SRM Blindness
**What it looks like:** Interpreting uplift despite assignment ratio mismatch.
**Detection signal:** Observed variant allocation materially deviates from expected split.
**Consequence:** Biased effect estimates and incorrect launch decisions.
**Mitigation:** SRM as mandatory quality gate. Return `invalid_test` when gate fails.

#### Proxy PMF (Single-Metric Dependence)
**What it looks like:** PMF declared from one sentiment or top-funnel metric.
**Detection signal:** Proxy improves while retention or economics degrade.
**Consequence:** Premature scaling and capital misallocation.
**Mitigation:** Require at least one behavioral, one retention, and one value/economic signal in `go_rule`.

#### Segment Drift Hidden by Blended Averages
**What it looks like:** Overall average passes while target ICP segment underperforms.
**Detection signal:** Segment composition shifts across validation window; segment-level outcomes diverge.
**Consequence:** False confidence for target market readiness.
**Mitigation:** Define segment-specific pass conditions for primary ICP. Block comparison if composition drift exceeds tolerance.

## Recording

```
write_artifact(path="/strategy/mvp-validation-criteria", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})

flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})

flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/icp-scorecard"})
```

## Artifact Schema

```json
{
  "mvp_validation_criteria": {
    "type": "object",
    "description": "Pre-registered MVP validation criteria: PMF signals, quality gates, decision protocol, and go/no-go rules.",
    "required": ["created_at", "version", "validation_window_days", "decision_protocol", "pmf_signals", "quality_gates", "go_rule", "no_go_rule", "recycle_rule", "failure_modes", "evidence_manifest"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string", "description": "ISO-8601 UTC timestamp when criteria were authored."},
      "version": {"type": "integer", "minimum": 1, "description": "Monotonic version to detect post-launch threshold changes."},
      "validation_window_days": {"type": "integer", "minimum": 1},
      "decision_protocol": {
        "type": "object",
        "required": ["methodology_mode", "alpha", "power", "mde_fraction", "practical_significance_fraction", "multiplicity_control", "guardrail_policy", "invalid_test_blockers"],
        "additionalProperties": false,
        "properties": {
          "methodology_mode": {"type": "string", "enum": ["fixed_horizon", "sequential_adjusted"]},
          "alpha": {"type": "number", "minimum": 0, "maximum": 0.2, "description": "Type-I error budget for confirmatory decisions."},
          "power": {"type": "number", "minimum": 0, "maximum": 1},
          "mde_fraction": {"type": "number", "minimum": 0, "maximum": 1, "description": "Minimum detectable effect as relative fraction."},
          "practical_significance_fraction": {"type": "number", "minimum": 0, "maximum": 1, "description": "Minimum business-meaningful effect threshold."},
          "multiplicity_control": {"type": "string", "enum": ["none", "benjamini_hochberg", "bonferroni"]},
          "guardrail_policy": {"type": "string", "enum": ["non_inferiority_required", "degradation_threshold"]},
          "invalid_test_blockers": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "enum": ["srm_detected", "schema_violation_exceeded", "event_drop_exceeded", "insufficient_sample", "instrumentation_missing"]},
            "description": "Conditions that force invalid_test state regardless of top-line metrics."
          }
        }
      },
      "pmf_signals": {
        "type": "array",
        "description": "Signal families defining PMF evidence. Must include at least retention, engagement, satisfaction, and expansion.",
        "items": {
          "type": "object",
          "required": ["family", "metric", "cohort", "observation_window_days", "threshold", "minimum_sample"],
          "additionalProperties": false,
          "properties": {
            "family": {"type": "string", "enum": ["retention", "engagement", "satisfaction", "expansion", "economics", "qualitative"]},
            "metric": {"type": "string"},
            "cohort": {"type": "string"},
            "observation_window_days": {"type": "integer", "minimum": 1},
            "threshold": {"type": "string", "description": "Predeclared pass threshold. E.g. '>40%' or 'NPS >= 50'."},
            "minimum_sample": {"type": "string"},
            "is_mandatory": {"type": "boolean", "description": "Whether this signal is required in go_rule."}
          }
        }
      },
      "quality_gates": {
        "type": "object",
        "required": ["srm_tolerance_pct", "schema_violation_max_pct", "event_drop_max_pct", "min_observation_depth"],
        "additionalProperties": false,
        "properties": {
          "srm_tolerance_pct": {"type": "number", "description": "Maximum acceptable sample ratio deviation before invalid_test."},
          "schema_violation_max_pct": {"type": "number"},
          "event_drop_max_pct": {"type": "number"},
          "min_observation_depth": {"type": "integer", "minimum": 1}
        }
      },
      "go_rule": {"type": "string", "description": "Explicit conditions that must all be met for a go verdict. Must reference specific signal families and quality gate states."},
      "no_go_rule": {"type": "string", "description": "Explicit disqualifying conditions that produce no_go verdict under valid evidence."},
      "recycle_rule": {"type": "string", "description": "Conditions that produce rework verdict — valid evidence but contradictory or incomplete."},
      "failure_modes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["label", "diagnosis_signals"],
          "additionalProperties": false,
          "properties": {
            "label": {"type": "string", "enum": ["wrong_icp", "wrong_solution", "wrong_channel", "wrong_timing"]},
            "diagnosis_signals": {"type": "array", "items": {"type": "string"}, "description": "Observable indicators suggesting this failure mode."}
          }
        }
      },
      "evidence_manifest": {
        "type": "array",
        "description": "Data sources and tools used for evidence generation with observability check status.",
        "items": {
          "type": "object",
          "required": ["tool_name", "role", "quality_check_status"],
          "additionalProperties": false,
          "properties": {
            "tool_name": {"type": "string"},
            "role": {"type": "string", "enum": ["primary_measurement", "validation", "instrumentation_check"]},
            "quality_check_status": {"type": "string", "enum": ["pass", "fail", "not_run"]}
          }
        }
      }
    }
  }
}
```
