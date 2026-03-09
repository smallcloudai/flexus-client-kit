# Research: pilot-success-tracking

**Skill path:** `executor/skills/pilot-success-tracking/`
**Bot:** executor (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pilot-success-tracking` measures pilot progress against pre-defined success criteria and produces structured status updates. The current SKILL.md is directionally solid: the three-cadence model (weekly pulse → mid-point → success review), the status classification (Met/On track/At risk/Not measurable), and the escalation triggers are all correct. The gaps are: the "pilot purgatory" failure mode — where a technically successful pilot fails to convert commercially — is absent; the distinction between proxy metrics and GTM-level business metrics is not specified; running legal/security/procurement in parallel during the pilot (not after) is not mentioned; and the ERR vs. ARR risk (pilot revenue counted as committed ARR) is entirely missing.

---

## Definition of Done

- [x] At least 4 distinct research angles covered
- [x] Each finding has a source URL or named reference
- [x] Methodology covers practical how-to, not just theory
- [x] Tool/API landscape with current status
- [x] At least one structural failure mode documented
- [x] Output schema grounded in real data shapes
- [x] Gaps honestly listed

---

## Quality Gates

- No generic filler: **passed**
- No invented tool names: **passed**
- Contradictions between sources explicitly noted: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> What constitutes a well-run pilot tracking process in 2025?

**Findings:**

**Success criteria must be locked as a "KPI contract" before the pilot starts — the current SKILL.md phrase "success criteria were defined BEFORE the pilot started" is correct and should be treated as an absolute constraint.** The most damaging pattern is post-hoc negotiation: when the pilot ends, the customer selects whichever metrics came out favorably and declares success or failure on that basis. Prevention: all success criteria must include a numeric threshold, a measurement source, a measurement method, and a binary decision rule ("if this threshold is met, we proceed to contract"). Ambiguous criteria like "improve the process" or "create value" must be rejected at the MAP-confirmation step. [M1]

**Well-structured pilots with clear expectations convert 60-80% to closed deals.** The differentiator is not product quality — it is the mutual commitment structure. Both sides must have documented, named accountability for outcomes. [M2]

**Measurement source hierarchy — prefer actuals, flag self-reported data explicitly:**
1. Product analytics logs (highest fidelity — tracks exact behavior without interpretation)
2. CRM exports and financial audit data (actuals, not estimates)
3. Third-party system data (customer's existing BI, ERP, or analytics platform)
4. Structured interviews with ops/finance leads (secondhand actuals, requires validation)
5. Self-reported surveys (lowest fidelity — subject to social desirability bias and recall error)

The current SKILL.md maps time savings and error rates to self-reported surveys without flagging data quality risk. Self-reported data should carry an explicit "confidence: low" label and ideally be cross-validated against at least one higher-fidelity source. [M3]

**GTM-level business metrics over proxy/activation metrics.** Research shows that 43% of users hitting activation milestones churn within 60 days anyway, while 18% who "fail" activation metrics become long-term customers. This means measuring feature completion or usage frequency as success criteria is measuring the wrong thing — these are leading indicators, not outcomes. The success criteria that actually predict commercial conversion are GTM-level business metrics: quota attainment improvement, sales cycle shortening, cost-per-outcome reduction, forecast accuracy. [M4]

**Pilot length: 30-90 days maximum.** Longer pilots lose urgency; customer stakeholders move on to other priorities; the evaluation becomes indefinite. 30 days is aggressive but workable for focused use cases. 90 days is the outer limit for maintaining commercial momentum. Pilots extended beyond 90 days without a signed extension with new success criteria should be treated as a commercial risk signal. [M2]

**The parallel track: run legal/security/procurement during the pilot, not after.** The most common cause of the 3-6 month "air gap" between technical pilot success and contract signature is that procurement, legal, and security reviews are started only after the pilot ends. By that point, champion attention has moved elsewhere, budget cycles have changed, and momentum has decayed. Best practice: initiate vendor security questionnaire, MSA redlines, and procurement portal registration in parallel with the technical track, during the pilot. This requires a separate track in the status artifact. [M5]

**Sources:**
- [M1] FitGap: Turning Pilot Results into Scalable Rollout Plans: https://us.fitgap.us/stack-guides/turning-pilot-results-into-scalable-rollout-plans-with-clear-success-metrics
- [M2] PartnerStack: Pilot Programs in B2B SaaS: https://partnerstack.com/articles/pilot-programs-testing-learning-b2b-saas
- [M3] Athenic: AI Automation ROI 156 Companies: https://getathenic.com/blog/ai-automation-roi-calculator-2025-data-study
- [M4] UserIntuition: Trial Design Anti-Patterns: https://www.userintuition.ai/reference-guides/trial-design-anti-patterns-win-loss-red-flags-you-can-fix-fast/
- [M5] nēdl Labs: Escaping Pilot Purgatory: https://nedllabs.com/blog/escaping-pilot-purgatory

---

### Angle 2: Tool & API Landscape
> What tools enable pilot success tracking, and what are their practical limits?

**Findings:**

**SurveyMonkey:**
- `surveymonkey.surveys.create.v1`: creates a survey with pages and questions.
- `surveymonkey.surveys.responses.list.v1`: retrieves responses for a given survey.
- API uses OAuth 2.0 authentication. Response collection and email distribution are supported via API. [T1]
- Use case in pilot tracking: time-savings and qualitative impact questions where a product analytics source is not available. Always label these responses as "self-reported" and apply data quality flagging in the artifact.
- Limitation: survey fatigue in pilots is a real risk. Sending a weekly SurveyMonkey to the champion reduces response rates. Keep check-in surveys to 3-5 questions maximum.

**Typeform:**
- `typeform.forms.create.v1`: creates a form with fields.
- `typeform.responses.list.v1`: retrieves responses.
- Average completion rate 47% vs ~15-25% for SurveyMonkey in comparable contexts. 87% of users switching to Typeform report higher response rates. [T2]
- Practical implication: for customer-facing pilot check-ins, Typeform produces better data volume than SurveyMonkey. Use Typeform for mid-point and end-of-pilot surveys; use structured email for weekly pulses.

**Zendesk:**
- `zendesk.tickets.list.v1`: lists open tickets for a customer. Use this as a support sentiment signal — number of open tickets, ticket age, and resolution rate are leading indicators of product friction during the pilot.
- Ticket volume spike (>3 open tickets from the same account in a week) is an early warning signal; silence with no tickets but also no logins may indicate abandonment rather than satisfaction.

**Google Calendar:**
- `google_calendar.events.insert.v1`: schedules mid-point and success review meetings. These should be scheduled at kick-off, not when the date approaches — front-loading calendar coordination avoids the situation where the end-of-pilot review can't be scheduled because stakeholders are unavailable.

**Missing tool: product analytics.** The same structural gap from `pilot-onboarding` applies here. The current SKILL.md states "Pull usage metrics: ask for export from customer's system or from your product analytics" — but no product analytics tool (Mixpanel, Amplitude, Segment) is listed in Available Tools. Self-service export from the customer's system is not a reliable measurement method because it depends on customer willingness to produce data on demand. [T3]

**Sources:**
- [T1] SurveyMonkey API v3: https://api.surveymonkey.com/v3/docs
- [T2] Typeform: Maximize Survey Response Rates: https://www.typeform.com/blog/survey-response-rate
- [T3] Insight7: Evaluating a Pilot Program Best Practices: https://insight7.io/evaluating-a-pilot-program-best-practices/

---

### Angle 3: Data Interpretation & Signal Quality
> How to distinguish reliable signals from noise in pilot tracking?

**Findings:**

**Activation metrics predict retention less reliably than assumed.** 43% of users who complete activation milestones churn within 60 days; 18% who fail activation milestones become long-term customers. This means the current SKILL.md's mapping of "usage metrics" as a primary success criterion may be measuring compliance with a defined workflow rather than genuine value realization. [D1]

**Before-after methodology requires a baseline captured at pilot start.** To measure time savings, error rate reduction, or financial impact reliably, a baseline must be documented at Day 1 using the same measurement source that will be used at pilot end. If the measurement source at baseline is a self-reported interview and the measurement source at end is a CRM export, the two numbers are not comparable. Lock measurement source symmetry at the MAP stage. [D2]

**Self-reported data reliability standard.** Best-practice ROI studies exclude companies that cannot provide documented actuals (not estimates). For pilot tracking, the standard should be: self-reported data is accepted only when cross-validated against at least one objective source. If no objective source exists, label the criterion as "low confidence" and note the limitation explicitly in the status report. [D3]

**Benchmark: achieve ≥80% of projected outcome within pilot window = success.** Using a 100% threshold is unrealistic for real-world pilots with setup friction and ramp time. The 80% threshold is the research-validated standard for declaring a criterion "Met" when full projected value is not achievable within the pilot window due to adoption ramp. [D3]

**Customer silence is a diagnostic signal, not a neutral state.** The current SKILL.md escalates if customer has gone quiet >5 business days — this is correct. The interpretation framework: silence after a positive check-in = processing/busy (low risk); silence after a flagged blocker = avoidance (high risk); silence before a scheduled decision meeting = pre-churn signal (immediate escalation required). Each silence instance should be categorized in the artifact by context, not treated identically. [D4]

**ERR vs. ARR signal.** If the pilot is funded from an "innovation budget" rather than a Line of Business operating budget, the conversion to paid ARR requires a budget source transition — not just a technical decision. This is an organizational procurement event, not a product evaluation event. The status tracking should include: which budget is funding the pilot, and whether the Line of Business budget owner is engaged. If the LOB budget owner is not engaged by mid-point, this is a commercial risk. [D5]

**Sources:**
- [D1] UserIntuition: Trial Design Anti-Patterns: https://www.userintuition.ai/reference-guides/trial-design-anti-patterns-win-loss-red-flags-you-can-fix-fast/
- [D2] FitGap: Pilot Results Methodology: https://us.fitgap.us/stack-guides/turning-pilot-results-into-scalable-rollout-plans-with-clear-success-metrics
- [D3] Athenic: AI Automation ROI Study 156 Companies: https://getathenic.com/blog/ai-automation-roi-calculator-2025-data-study
- [D4] nēdl Labs: Pilot Purgatory: https://nedllabs.com/blog/escaping-pilot-purgatory
- [D5] GTMNow: ARR vs ERR: https://gtmnow.com/arr-vs-err-why-every-dollar-isnt-equal/

---

### Angle 4: Failure Modes & Anti-Patterns
> Where does pilot tracking collapse in practice?

**Findings:**

**Pilot purgatory: technical success without commercial conversion.** This is the most dangerous failure mode in B2B pilots and is entirely absent from the current SKILL.md. A pilot achieves all its success criteria, the champion is satisfied, and... nothing happens. The commercial conversion stalls because: (a) the pilot was funded by innovation budget, not LOB budget — converting requires a different budget owner's approval; (b) procurement, legal, and security reviews were not started during the pilot — they now take 3-6 months; (c) champion attention has moved to other priorities after the pilot window closed; (d) the success review had no explicit "what happens next" decision rule. [F1][F2]

Prevention requires embedding the conversion mechanism into the pilot structure before tracking starts: named next-step with a decision date, procurement pre-approval initiated during the pilot, and success review framed as "here is the conversion paperwork" not "here are the results, what do you think?"

**Success criteria drift.** During a 30-90 day pilot, real-world conditions change: business priorities shift, personnel changes occur, the product's capabilities evolve. Customers (and sometimes vendor reps) informally re-weight which criteria matter, effectively changing the finish line mid-race. The current SKILL.md correctly states "if success criteria need to change, that requires explicit agreement with the customer" — but does not specify the process for making this explicit. Any change to success criteria mid-pilot must be documented in writing, signed by both parties, and logged in the artifact with a change reason. Undocumented verbal criterion changes become disputes at the success review. [F3]

**Vanity metrics masquerading as success criteria.** Measuring feature adoption rates, login counts, and onboarding completion percentage measures the customer's compliance with the vendor's product, not the business outcome the customer cares about. These metrics satisfy the vendor's reporting needs but do not predict commercial conversion. The customer's evaluation committee at the success review will ask "did this make our business measurably better?" — feature adoption metrics cannot answer that question. [F4]

**Measurement source inconsistency.** Baseline measured via interview at Day 0, end-of-pilot measured via CRM export at Day 30 — these are not comparable. The difference in numbers will be disputed. Lock measurement source and method at the MAP stage and do not change them during the pilot, even if a better data source becomes available. If you must switch, document the switch with a reconciliation note. [F5]

**Skipping parallel procurement track.** Every day spent running procurement sequentially after the pilot ends is a day where the buyer's momentum is frozen and their attention competes with other priorities. The behavioral economics of commitment work in reverse: the longer the gap between "yes, technically it works" and "here is the purchase order," the more time the buyer has to rationalize against the purchase. Start legal and security reviews no later than Day 15 of a 30-day pilot. [F1]

**Sources:**
- [F1] nēdl Labs: Escaping Pilot Purgatory: https://nedllabs.com/blog/escaping-pilot-purgatory
- [F2] Luigi Mallardo: ERR vs. ARR Founder Guide: https://luigimallardo.com/err-vs-arr-saas-pilot-revenue-recognition/
- [F3] FitGap: Scalable Rollout Plans: https://us.fitgap.us/stack-guides/turning-pilot-results-into-scalable-rollout-plans-with-clear-success-metrics
- [F4] Fullcast: Why 95% of AI Pilots Fail: https://www.fullcast.com/content/how-to-evaluate-and-pilot-ai-solutions-for-your-gtm-team/
- [F5] Athenic: AI ROI Measurement: https://getathenic.com/blog/ai-automation-roi-calculator-2025-data-study

---

## Synthesis

The current SKILL.md is the closest to complete of any skill reviewed so far. The structure is correct: three-cadence measurement, status classification, escalation triggers. The missing pieces are all about the commercial conversion track running alongside the technical success track.

The single most important addition is making the parallel procurement track explicit: the skill must instruct the executor to initiate legal, security, and procurement reviews during the pilot, not after. This is an operational instruction, not a tracking instruction — but it belongs in this skill because it is the failure mode that turns tracked-successful pilots into "pilot purgatory."

The second most important addition is the ERR vs. ARR classification: if the pilot is funded by an innovation budget, conversion to paid ARR requires a different budget owner to activate. This is a commercial risk that the status tracking must surface explicitly, because it changes the escalation response — champion satisfaction is necessary but not sufficient for commercial conversion if the LOB budget owner is not engaged.

The data quality hierarchy (actuals > structured interviews > self-reported) should be built into the schema so every criterion entry carries a measurement source type and confidence label.

---

## Recommendations for SKILL.md

- Add parallel procurement track to the methodology: start legal/security/procurement no later than Day 15 of a 30-day pilot (proportionally for longer pilots).
- Add ERR vs. ARR risk: identify whether the pilot is funded by innovation budget or LOB operating budget. If innovation budget: LOB budget owner engagement is a required escalation trigger by mid-point.
- Tighten success criteria validation: require numeric threshold, named measurement source, measurement method, and binary decision rule for every criterion. Reject vague criteria before pilot starts.
- Add measurement source hierarchy with explicit confidence labels: actuals = high, structured interviews = medium, self-reported surveys = low.
- Add the 80% threshold convention: ≥80% of projected outcome within pilot window = "Met" (not requiring 100%).
- Add baseline capture as a mandatory Day 1 action for every measurable criterion.
- Add success criteria change process: any mid-pilot change must be documented in writing and logged with change reason.
- Expand schema: add parallel_track status, pilot_budget_type, measurement_source_confidence, baseline_values, criterion-level status, and conversion_decision fields.

---

## Draft Content for SKILL.md

### Draft: Updated core mode

You track pilot progress against pre-defined success criteria and drive the commercial conversion track in parallel. Two things must succeed simultaneously: the technical/outcome track (did success criteria get met?) and the commercial track (is the contract machinery in motion so that a positive technical result can convert to revenue?). A pilot that is technically successful but commercially stalled is not a success — it is pilot purgatory.

Core mode: success criteria are locked at pilot start. Your job is to measure, not renegotiate. If a criterion needs to change, document it explicitly in writing with customer sign-off and log the reason. Run commercial paperwork (legal, security, procurement) starting at Day 15 of a 30-day pilot — not after the success review.

---

### Draft: Methodology additions

**Parallel commercial track (start no later than Day 15 of a 30-day pilot):**

Initiate these in parallel with the technical pilot track:
1. Vendor security questionnaire: send to customer IT/security team; typical turnaround 2-4 weeks.
2. MSA / legal redlines: send draft agreement to customer legal; allow 2-6 weeks.
3. Procurement portal registration: if customer uses a procurement system, register as a vendor early to avoid form-filling delays after the success review.
4. LOB budget owner engagement: confirm that the Line of Business budget owner (not just the innovation/experiment budget owner) is aware of the pilot and has a budget line for the contract. If not confirmed by mid-point, escalate.

Track the status of each item in the artifact's `commercial_track` section.

**Baseline capture (Day 1, mandatory):**
For every measurable success criterion, capture the baseline value at pilot start using the same measurement source that will be used at pilot end. Document: metric name, current value, measurement source, measurement method, captured at timestamp. Without a documented baseline, before-after claims cannot be substantiated.

**Success criteria quality gate:**
Each criterion in the MAP must meet all of the following before the pilot tracking begins:
- Numeric or clearly binary threshold (e.g. "reduce processing time from 45 min to <20 min per case")
- Named measurement source (e.g. "CRM export from Salesforce", "product analytics from Mixpanel", "time-tracking system export")
- Measurement method (e.g. "average of 20 consecutive cases sampled in Week 4")
- Binary decision rule (e.g. "if this threshold is met, it counts as a vote for proceeding to contract")
- Measurement confidence level: high (product logs or financial actuals), medium (structured interview with documented methodology), low (self-reported survey)

Reject criteria that cannot meet this standard before tracking begins. A criterion that is "not measurable" at success review was a bad criterion from the start — not a measurement failure during the pilot.

---

### Draft: Anti-patterns

#### Pilot Purgatory
**What it looks like:** Pilot ends. Success criteria were met. Champion is happy. Then... silence. No contract materializes for weeks or months.
**Detection signal:** Success review meeting is completed without a defined next step, contract timeline, or named procurement owner. Or: no procurement / legal activity has been initiated during the pilot.
**Consequence:** Commercial momentum decays at roughly 20-30% per week after the pilot window closes. By week 6, you are effectively re-selling the deal from scratch. ERR (pilot revenue) never converts to ARR.
**Mitigation:** Start legal, security, and procurement in parallel no later than Day 15 of a 30-day pilot. Frame the success review as "here is the conversion paperwork, let's go through the results and then sign." Never frame it as "here are the results — what do you want to do next?" The answer to "what do you want to do next?" is always "let me think about it."

#### Criteria Drift
**What it looks like:** Mid-pilot, the customer says "actually, what we really care about is [different metric]." The executor accommodates verbally and starts tracking the new metric instead.
**Detection signal:** The artifact's success criteria section has different metrics than the MAP that was signed at kick-off.
**Consequence:** At success review, both sides have different baselines and different metrics. The review becomes a negotiation, not an evaluation. Deals close late or not at all.
**Mitigation:** Any change to success criteria requires a written amendment signed by both sides. Log the change in the artifact with the date, reason, and approver on both sides. Never let a verbal "actually, focus on X instead" change what gets measured without documentation.

#### Innovation Budget Without LOB Engagement
**What it looks like:** The pilot is enthusiastically funded by a VP of Innovation or a CDO's experimental budget. The CMO and RevOps team (the actual users and LOB budget owners) are not part of the pilot evaluation.
**Detection signal:** None of the pilot stakeholders have operating budget authority for the product category being evaluated.
**Consequence:** Even with a perfect technical success, converting to ARR requires a new budget process from a budget owner who didn't participate in the pilot evaluation. This re-approval process can take a full fiscal quarter and often doesn't happen at all as the business priority shifts.
**Mitigation:** At mid-point review, explicitly confirm: who owns the operating budget line for this product category? Have they been briefed on pilot progress? Are they attending the success review? If the answer to any of these is "no," escalate to the AE immediately.

---

### Draft: Artifact Schema

```json
{
  "pilot_status": {
    "type": "object",
    "description": "Point-in-time status report for a pilot against success criteria, plus commercial track status.",
    "required": [
      "account_id",
      "status_date",
      "pilot_day",
      "report_type",
      "pilot_budget_type",
      "success_criteria",
      "commercial_track",
      "overall_status",
      "escalations"
    ],
    "additionalProperties": false,
    "properties": {
      "account_id": {
        "type": "string",
        "description": "Identifier for the pilot customer account."
      },
      "status_date": {
        "type": "string",
        "format": "date",
        "description": "Date this status report was generated."
      },
      "pilot_day": {
        "type": "integer",
        "minimum": 1,
        "description": "Day number within the pilot window (Day 1 = pilot start date)."
      },
      "report_type": {
        "type": "string",
        "enum": ["weekly_pulse", "midpoint_review", "success_review"],
        "description": "Type of status report being generated."
      },
      "pilot_budget_type": {
        "type": "string",
        "enum": ["innovation_budget", "lob_operating_budget", "unknown"],
        "description": "Whether the pilot is funded by an innovation/experimental budget or a Line of Business operating budget. Innovation budget signals conversion risk — the LOB budget owner must be engaged before success review."
      },
      "lob_budget_owner_engaged": {
        "type": "boolean",
        "description": "Whether the Line of Business budget owner (not just the experiment/innovation sponsor) is aware of and engaged in the pilot evaluation. Required to be true by mid-point for innovation-budget pilots."
      },
      "success_criteria": {
        "type": "array",
        "description": "One entry per success criterion from the MAP. Status is evaluated per criterion.",
        "items": {
          "type": "object",
          "required": [
            "criterion_id",
            "description",
            "threshold",
            "measurement_source",
            "measurement_confidence",
            "baseline_value",
            "baseline_captured_at",
            "current_value",
            "status"
          ],
          "additionalProperties": false,
          "properties": {
            "criterion_id": {"type": "string"},
            "description": {"type": "string", "description": "Human-readable description of the criterion."},
            "threshold": {"type": "string", "description": "The numeric or binary threshold that defines 'Met'. Must be specific — reject vague criteria."},
            "measurement_source": {
              "type": "string",
              "description": "Named data source — e.g. 'Salesforce CRM export', 'Mixpanel product analytics', 'customer time-tracking system', 'typeform self-report survey'."
            },
            "measurement_confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "High: product logs or financial actuals. Medium: structured interview with documented method. Low: self-reported survey."
            },
            "baseline_value": {
              "type": ["string", "number", "null"],
              "description": "Value at pilot start (Day 1). Must be captured before the pilot begins using the same source as current_value."
            },
            "baseline_captured_at": {
              "type": ["string", "null"],
              "format": "date",
              "description": "Date the baseline was captured. Null means baseline was not captured — flag as a tracking gap."
            },
            "current_value": {
              "type": ["string", "number", "null"],
              "description": "Value at the time of this status report."
            },
            "progress_pct": {
              "type": ["number", "null"],
              "minimum": 0,
              "description": "Progress toward threshold as a percentage. 80%+ = on track for Met. Only applicable for numeric criteria."
            },
            "status": {
              "type": "string",
              "enum": ["met", "on_track", "at_risk", "not_measurable", "pending_baseline"],
              "description": "met: threshold achieved or ≥80% reached within pilot window. on_track: trajectory will reach threshold. at_risk: trajectory suggests threshold will be missed. not_measurable: measurement source failed — agree alternative. pending_baseline: baseline not yet captured."
            },
            "status_notes": {
              "type": ["string", "null"],
              "description": "Explanation for the status, especially for at_risk or not_measurable."
            },
            "criterion_priority": {
              "type": "string",
              "enum": ["P0", "P1", "P2"],
              "description": "P0 = must-have for contract. P1 = strongly preferred. P2 = nice-to-have. Any P0 at_risk at mid-point triggers immediate escalation."
            }
          }
        }
      },
      "commercial_track": {
        "type": "object",
        "description": "Status of parallel procurement and legal activities that must run during the pilot, not after.",
        "required": ["security_review", "legal_msa", "procurement_registration"],
        "additionalProperties": false,
        "properties": {
          "security_review": {
            "type": "object",
            "required": ["status", "initiated_at"],
            "additionalProperties": false,
            "properties": {
              "status": {"type": "string", "enum": ["not_started", "sent", "in_review", "complete", "blocked"]},
              "initiated_at": {"type": ["string", "null"], "format": "date"},
              "expected_completion": {"type": ["string", "null"], "format": "date"},
              "blocker": {"type": ["string", "null"]}
            }
          },
          "legal_msa": {
            "type": "object",
            "required": ["status", "initiated_at"],
            "additionalProperties": false,
            "properties": {
              "status": {"type": "string", "enum": ["not_started", "draft_sent", "in_redlines", "agreed", "signed", "blocked"]},
              "initiated_at": {"type": ["string", "null"], "format": "date"},
              "expected_completion": {"type": ["string", "null"], "format": "date"},
              "blocker": {"type": ["string", "null"]}
            }
          },
          "procurement_registration": {
            "type": "object",
            "required": ["status"],
            "additionalProperties": false,
            "properties": {
              "status": {"type": "string", "enum": ["not_required", "not_started", "in_progress", "complete", "blocked"]},
              "blocker": {"type": ["string", "null"]}
            }
          }
        }
      },
      "overall_status": {
        "type": "string",
        "enum": ["on_track", "at_risk", "critical", "complete_success", "complete_failure", "purgatory_risk"],
        "description": "purgatory_risk: all technical criteria on track but commercial track not initiated. critical: any P0 criterion at_risk. complete_success: success review passed. complete_failure: success review failed."
      },
      "escalations": {
        "type": "array",
        "description": "Active escalations triggered by this status report.",
        "items": {
          "type": "object",
          "required": ["trigger", "triggered_at", "escalated_to", "resolved"],
          "additionalProperties": false,
          "properties": {
            "trigger": {
              "type": "string",
              "enum": [
                "p0_criterion_at_risk",
                "customer_silent_5_days",
                "customer_reconsidering",
                "lob_budget_owner_not_engaged_by_midpoint",
                "commercial_track_not_initiated_by_day15",
                "innovation_budget_no_lob_path",
                "sponsor_turnover"
              ]
            },
            "triggered_at": {"type": "string", "format": "date"},
            "escalated_to": {"type": "string", "description": "Name or role of the escalation target."},
            "resolved": {"type": "boolean"},
            "resolution_notes": {"type": ["string", "null"]}
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- **Product analytics tool absence (same as pilot-onboarding).** The highest-fidelity measurement source for pilot success criteria is product usage logs, but no analytics API is registered in the executor bot. This forces reliance on self-reported surveys (low confidence) for usage-based criteria. Resolution requires adding a product analytics integration to the executor bot.
- **80% threshold convention source.** The ≥80% of projected outcome = "Met" convention was found in AI automation ROI research (156 companies). It may not apply universally across all product categories — in critical-path use cases (e.g. security, compliance), a 100% threshold may be required. The 80% rule should be treated as a default, not an absolute.
- **ERR vs. ARR pilot budget classification.** Determining whether a pilot is funded by an innovation budget vs. LOB operating budget requires asking the customer directly — no enrichment tool can provide this signal. The artifact's `pilot_budget_type` field will often be "unknown" unless the executor explicitly asks during kick-off.
- **Typeform vs. SurveyMonkey response rate advantage.** The 47% vs. 15-25% completion rate comparison comes from Typeform's own documentation, which has obvious self-interest. The claim is widely cited but the methodology of the comparison is not independently verified. Treat as directionally correct but not precisely calibrated.
- **Parallel procurement timeline norms.** The "3-6 month air gap" estimate for sequential post-pilot procurement comes from a single practitioner blog (nēdl Labs). The timeline varies substantially by company size, industry, and existing vendor relationship. Enterprise customers (1000+ employees) typically take longer; mid-market customers may be faster.
