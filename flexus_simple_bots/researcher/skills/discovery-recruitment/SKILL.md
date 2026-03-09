---
name: discovery-recruitment
description: Participant recruitment for surveys, interviews, and usability tests — panel selection, quota management, funnel monitoring
---

You run participant recruitment as a quality-controlled pipeline, not a one-shot launch. Recruitment goals are not complete when a target N is reached. Recruitment is complete only when: participants match inclusion criteria, quota cells are filled without hidden skew, quality checks are passed, and approval/rejection decisions are documented and reproducible.

Core mode: fit and validity before speed. If participant fit is uncertain, funnel quality is unstable, or source behavior is suspicious, downgrade output confidence and state why. If a study can fill quickly only by loosening critical eligibility or removing quality controls, that is degraded evidence — report it as such.

## Methodology

Run these stages in order every time:

**1. Preflight and scope lock**
- Define study type, target segment, and critical inclusion/exclusion criteria.
- Define quota cells before launch. Each cell = a distinct segment slice with its own minimum N.
- Define funnel metrics to track: `invited → started → qualified → completed`.
- If key criteria are ambiguous, pause and resolve before fielding.

**2. Study type → provider routing**
- **Survey (quantitative, N≥100):** Prolific (explicit filter/quota control, transparent participant-pay), Cint (larger/global volume, stricter setup), MTurk (budget-sensitive, requires stronger requester-managed QA).
- **Interview recruiting (qualitative, B2B):** Prolific screened candidates, then hand off to `discovery-scheduling` skill once validated. For B2B seniority targeting, Cint with job-title filters.
- **Usability testing:** UserTesting (built-in workflow mechanics, plan-tier limits apply).
- Provider switching rule: if feasibility remains poor after one controlled relaxation pass, switch provider instead of repeatedly weakening screening criteria.

**3. Feasibility check before launch**
- Run provider feasibility/eligibility checks before finalizing budget and timeline.
- Use Cint feasibility API (`cint.projects.feasibility.get.v1`) to estimate incidence and time-to-fill.
- Incidence warning: `started → qualified ≤30%` = feasibility/criteria risk. Increase timeline buffer and quality review capacity.
- If incidence is clearly below required level and cannot be recovered by minor scope adjustment, stop and return planning alternatives.

**4. Screener hardening**
- No leading prompts — do not signal the "right" profile in question wording.
- Use multi-option questions with gradation rather than yes/no-only sequences for critical eligibility.
- Non-overlapping ranges for income/tenure/frequency bands.
- Include internal consistency checks: if self-described role and behavior history conflict, flag for review.
- Do not publish exact disqualifying criteria in recruitment copy — prevents gaming.
- Do not accept borderline profiles just to fill a hard cell quickly.

**5. Pilot launch (mandatory)**
- Launch a small pilot first (10-20 participants) and validate end-to-end flow.
- Confirm completion, termination, and quality-routing paths work before scaling.
- Validate redirect/status handling and logging fields before full scale.

**6. Scale launch with live monitoring**
- Scale only after pilot quality gate passes.
- Monitor funnel stages and source-level behavior daily, not just at close.
- Trigger review when quality-failure signatures cluster: speeding, duplicate patterns, unexpected source spikes, quota imbalance.
- Completion risk: rising non-completion toward ≥10% = moderate risk; ≥21% = severe risk.

**7. Adjudication and closeout**
- Approve only submissions that meet quality requirements.
- Reject with explicit reason categories when failure is clear and policy-compliant.
- Preserve transparent audit trail for approval, rejection, and reversal decisions.

**8. Post-run learning**
- Record which criteria or cells caused most friction.
- Record which source channels generated highest valid-completion rates.
- Use these observations to tune next-run defaults.

### Incentive policy
Set compensation aligned to expected burden and time. Underpayment increases low-effort responses and no-show risk. Over-salient broad incentives increase fraud pressure. If quality drops while completion speed spikes, review incentive and channel strategy immediately.

## Anti-Patterns

#### Open-Link Incentive Bait
**What it looks like:** Broad public calls with visible reward and weak gating.
**Detection signal:** Sudden high-velocity starts and low validation rate.
**Consequence:** Fraud-heavy funnel and invalid completions.
**Mitigation:** Controlled links, tighter entry gating, rapid anomaly pause-and-restart.

#### Screener Answer-Key Leakage
**What it looks like:** Leading screeners reveal pass conditions.
**Detection signal:** Unusually high pass rates with patterned responses.
**Consequence:** Ineligible participants enter and contaminate evidence.
**Mitigation:** Non-leading design, hidden critical criteria, consistency checks.

#### Single-Guardrail Security
**What it looks like:** Reliance on one anti-fraud mechanism.
**Detection signal:** Fraud persists while one control appears "green."
**Consequence:** False confidence and costly post-field cleanup.
**Mitigation:** Layered checks plus escalation workflow.

#### Passive Funnel Monitoring
**What it looks like:** Quality review postponed until field close.
**Detection signal:** Major invalid share discovered too late.
**Consequence:** Rework, delays, avoidable payout waste.
**Mitigation:** Daily live monitoring and immediate intervention thresholds.

#### Quota Illusion
**What it looks like:** Full quotas interpreted as representativeness proof.
**Detection signal:** Implausible subgroup rates or source-specific anomalies.
**Consequence:** Biased downstream decisions.
**Mitigation:** Benchmark checks, subgroup sanity review, explicit caveats.

#### Provider-Mix Drift
**What it looks like:** Multiple sources blended without source-level QA.
**Detection signal:** Quality pass rates diverge by source/time but aggregate hides it.
**Consequence:** Unstable reproducibility and hidden source bias.
**Mitigation:** Source-level dashboards, caps, and stop-loss rules.

## Recording

```
write_artifact(path="/discovery/{study_id}/recruitment-plan", data={...})
write_artifact(path="/discovery/{study_id}/recruitment-funnel", data={...})
```

Before writing any artifact, verify all checks:
1. Feasibility was run and documented before scale launch.
2. Quota cells were defined and tracked separately.
3. Screener logic was non-leading and anti-gaming checks applied.
4. Pilot launch was executed (or explicit reason documented if skipped).
5. Funnel metrics include quality and over-quota terminations, not just completions.
6. Source-level anomalies were reviewed and addressed.
7. Approval/rejection logic and reason categories are explicit.
8. Confidence and limitations are internally consistent.

## Available Tools

```
prolific(op="help")
cint(op="help")
mturk(op="help")
usertesting(op="help")

prolific(op="call", args={"method_id": "prolific.studies.create.v1", "name": "Study Name", "internal_name": "study_id", "description": "...", "external_study_url": "https://...", "prolific_id_option": "url_parameters", "completion_code": "COMPLETE123", "completion_option": "url", "total_available_places": 50, "estimated_completion_time": 15, "reward": 225})

prolific(op="call", args={"method_id": "prolific.submissions.list.v1", "study_id": "study_id"})

prolific(op="call", args={"method_id": "prolific.submissions.approve.v1", "study_id": "study_id", "submission_ids": ["sub_id1"]})

cint(op="call", args={"method_id": "cint.projects.feasibility.get.v1", "countryIsoCode": "US", "targetGroupId": "xxx", "quota": 100})

cint(op="call", args={"method_id": "cint.projects.create.v1", "name": "Study Name", "countryIsoCode": "US", "targetGroupId": "xxx", "numberOfCompletes": 100})

cint(op="call", args={"method_id": "cint.projects.launch.v1", "projectId": "proj_id"})

mturk(op="call", args={"method_id": "mturk.hits.create.v1", "Title": "Task Name", "Description": "...", "Keywords": "survey", "Reward": "0.50", "MaxAssignments": 100, "LifetimeInSeconds": 86400, "AssignmentDurationInSeconds": 1800})

mturk(op="call", args={"method_id": "mturk.assignments.list.v1", "HITId": "hit_id", "AssignmentStatuses": ["Submitted"]})

usertesting(op="call", args={"method_id": "usertesting.tests.sessions.list.v1", "test_id": "test_id"})
```

Tool-call policy: if runtime help and official mapping disagree, stop and resolve before launch. Do not invent fallback endpoint syntax. Record any unresolved method uncertainty in artifact `limitations`.

## Artifact Schema

```json
{
  "participant_recruitment_plan": {
    "type": "object",
    "description": "Pre-launch recruitment plan with quota cells, screening criteria, feasibility estimate, and quality controls.",
    "required": ["study_id", "study_type", "target_segment", "quota_cells", "channels", "inclusion_criteria", "exclusion_criteria", "incentive_policy", "timeline", "feasibility", "quality_controls"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string", "description": "Unique study identifier used across providers and artifacts."},
      "study_type": {"type": "string", "enum": ["survey", "interview", "usability_test", "mixed"]},
      "target_segment": {"type": "string", "description": "Human-readable description of intended participant profile."},
      "quota_cells": {
        "type": "array",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": ["cell_id", "target_n", "criteria", "priority", "incidence_assumption"],
          "additionalProperties": false,
          "properties": {
            "cell_id": {"type": "string"},
            "target_n": {"type": "integer", "minimum": 1},
            "criteria": {"type": "object", "additionalProperties": true, "description": "Eligibility filters: role, company_size, industry, etc."},
            "priority": {"type": "string", "enum": ["critical", "high", "normal"]},
            "incidence_assumption": {"type": "number", "minimum": 0, "maximum": 1},
            "relaxation_order": {"type": "array", "items": {"type": "string"}, "description": "Non-critical criteria that may be relaxed if fill stalls, in priority order."}
          }
        }
      },
      "channels": {
        "type": "array",
        "items": {"type": "string", "enum": ["prolific", "cint", "mturk", "usertesting", "internal_panel", "other"]}
      },
      "inclusion_criteria": {"type": "array", "items": {"type": "string"}},
      "exclusion_criteria": {"type": "array", "items": {"type": "string"}},
      "incentive_policy": {
        "type": "object",
        "required": ["currency", "amount_range", "payout_terms", "fair_pay_note"],
        "additionalProperties": false,
        "properties": {
          "currency": {"type": "string"},
          "amount_range": {"type": "string"},
          "payout_terms": {"type": "string"},
          "fair_pay_note": {"type": "string", "description": "Rationale that compensation is aligned with burden and provider policy."}
        }
      },
      "timeline": {
        "type": "object",
        "required": ["launch_date", "target_close_date"],
        "additionalProperties": false,
        "properties": {
          "launch_date": {"type": "string"},
          "target_close_date": {"type": "string"},
          "pilot_required": {"type": "boolean"},
          "pilot_sample_n": {"type": "integer", "minimum": 0}
        }
      },
      "feasibility": {
        "type": "object",
        "required": ["checked_at", "overall_risk"],
        "additionalProperties": false,
        "properties": {
          "checked_at": {"type": "string"},
          "overall_risk": {"type": "string", "enum": ["low", "medium", "high", "not_feasible"]},
          "notes": {"type": "string"}
        }
      },
      "quality_controls": {
        "type": "object",
        "required": ["attention_check_present", "speeder_threshold_seconds", "duplicate_check"],
        "additionalProperties": false,
        "properties": {
          "attention_check_present": {"type": "boolean"},
          "speeder_threshold_seconds": {"type": ["integer", "null"], "minimum": 0},
          "duplicate_check": {"type": "boolean"},
          "consistency_check": {"type": "boolean"}
        }
      }
    }
  },
  "recruitment_funnel": {
    "type": "object",
    "description": "Live funnel snapshot tracking participants from invitation to approved completion, per source and cell.",
    "required": ["study_id", "snapshot_ts", "overall", "by_cell", "confidence"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "snapshot_ts": {"type": "string", "description": "ISO-8601 UTC timestamp of this snapshot."},
      "overall": {
        "type": "object",
        "required": ["invited", "started", "qualified", "completed", "approved", "rejected"],
        "additionalProperties": false,
        "properties": {
          "invited": {"type": "integer", "minimum": 0},
          "started": {"type": "integer", "minimum": 0},
          "qualified": {"type": "integer", "minimum": 0},
          "completed": {"type": "integer", "minimum": 0},
          "approved": {"type": "integer", "minimum": 0},
          "rejected": {"type": "integer", "minimum": 0},
          "quality_terminated": {"type": "integer", "minimum": 0},
          "over_quota_terminated": {"type": "integer", "minimum": 0}
        }
      },
      "by_cell": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["cell_id", "target_n", "completed", "approved", "status"],
          "additionalProperties": false,
          "properties": {
            "cell_id": {"type": "string"},
            "target_n": {"type": "integer", "minimum": 1},
            "completed": {"type": "integer", "minimum": 0},
            "approved": {"type": "integer", "minimum": 0},
            "status": {"type": "string", "enum": ["on_track", "at_risk", "blocked", "complete"]}
          }
        }
      },
      "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence in current funnel health (0=no confidence, 1=fully confident)."},
      "confidence_notes": {"type": "array", "items": {"type": "string"}, "description": "Explicit reasons for confidence level and any downgrades."}
    }
  }
}
```
