# Research: segment-icp-scoring

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/segment-icp-scoring/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

`segment-icp-scoring` is the synthesis layer that turns multiple upstream artifacts into a reproducible ICP tier decision. It combines firmographic evidence, behavioral intent signals, technographic context, and interview/JTBD evidence into a scorecard that strategist workflows can trust and replay.

The core problem this skill solves is false precision: many GTM teams output a single score without provenance, source quality checks, or repeatability controls. Research across 2024-2026 shows that high-performing teams separate fit/intent/engagement components, enforce source-specific quality gates, apply recency logic, and validate tiers against conversion outcomes rather than static score distributions.

The primary users are researcher and strategist agents (and their human operators) who need defensible segment-level tiering before campaign and pipeline allocation decisions.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024–2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- Generic filler removed; every major claim is tied to a concrete source or named framework.
- No invented tools, methods, or endpoints were added; endpoint names are copied only from vendor docs where explicit.
- Contradictions are called out explicitly in Synthesis and findings.
- Findings volume is within target range and the Draft Content section is larger than findings.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. High-performing teams increasingly separate scoring into explicit components (fit, intent, engagement) instead of a single opaque number, then recombine into a composite prioritization layer. This improves explainability and operational debugging when tier quality drifts.  
   Evidence: 6sense score model framing, Demandbase account scoring guidance, HubSpot combined score model.

2. Numeric score bands are only useful when tied to deterministic action states. Vendor implementations map score ranges to stages/tier actions (for example, 6sense buying stage bands and HubSpot score labels), which reduces rep interpretation drift.

3. Intent filtering is provider-specific, not portable. Bombora documentation recommends thresholding around score >=60 and topic coverage constraints; G2 Buyer Intent supports stage/activity and event-volume constraints. Teams that apply one vendor's threshold to another source produce noisy over-tiering.

4. Recency logic is now mandatory in production systems. HubSpot scoring supports explicit decay windows (1/3/6/12 months), while Demandbase operational playbooks frame 1-week/1-month/3-month windows and "trending vs baseline" logic.

5. Data sufficiency minimums are explicit in modern systems. HubSpot AI scoring requires minimum converted/non-converted sample counts; Demandbase predictive setup notes minimum account counts and retraining cadence. The practical implication is fail-fast behavior for underpowered cohorts.

6. Reproducibility is validated with outcome lift by tier (conversion/pipeline progression), not by "nice distribution" of scores. 6sense model insights emphasize stage/fit ordering sanity, and HubSpot includes pre-activation testing workflows.

7. Buying-group and account-level aggregation has become the default orientation in 2024-2026 GTM research. Forrester and Adobe business research both point to larger committees and reduced value from single-contact scoring heuristics.

8. Qualitative evidence can be included, but only with coding discipline (semi-structured interview guide + codebook + inter-rater checks). Without coding consistency, qualitative inputs become narrative bias rather than scoring evidence.

**Sources:**
- https://support.6sense.com/docs/6sense-scores-overview
- https://support.6sense.com/docs/predictive-buying-stages
- https://support.6sense.com/docs/predictive-model-insights-report
- https://www.demandbase.com/blog/account-scoring/
- https://www.demandbase.com/resources/playbook/engagement-points-demandbase-intent/
- https://www.demandbase.com/resources/playbook/engagement-minutes-introduction/
- https://www.demandbase.com/resources/playbook/predictive-models-setup/
- https://knowledge.hubspot.com/scoring/understand-the-lead-scoring-tool
- https://knowledge.hubspot.com/scoring/build-combined-scores
- https://customers.bombora.com/crc-brand/thresholding
- https://documentation.g2.com/docs/buyer-intent
- https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/
- https://business.adobe.com/uk/blog/basics/new-research-b2b-marketing-leaders-target-buying-groups-as-part-of-a-winning-strategy
- https://www.productmarketingalliance.com/designing-semi-structured-interviews/ (evergreen method framing)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4372765/ (evergreen inter-rater reference)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

Practical ICP scoring stacks in 2024-2026 are multi-provider by design. A common architecture has: CRM truth layer (Salesforce/HubSpot), firmographic enrichment (PDL/ZoomInfo/Crunchbase), intent layer (6sense/Bombora/G2), and technographic layer (Wappalyzer/HG Insights). The key operational insight is not "which one is best," but "which one supplies which feature family with known constraints."

Concrete provider capabilities that are directly useful for this skill:

- **HubSpot**: expanded API limits in late 2024; CRM limits endpoints and scoring tooling updates, plus Breeze Intelligence enrichment/intent expansion. Good for score activation in CRM-native flows.
- **Salesforce**: explicit API limit monitoring (`/services/data/vXX.0/limits`) and change-management around API retirement; critical for stable scoring pipelines at scale.
- **People Data Labs**: explicit company enrichment APIs including bulk flows (`/v5/company/enrich`, `/v5/company/enrich/bulk`) and rate/credit telemetry headers.
- **ZoomInfo**: search-then-enrich model with credit controls; useful for "shortlist first, enrich second" cost containment.
- **Crunchbase Data**: fundamentals + insights/predictions packaging; useful for funding and company growth features in fit scoring.
- **6sense**: account-centric scores/stages and API/credit model for intent and fit signals.
- **Bombora**: Company Surge API and threshold controls for topic/domain/geography; useful as a third-party intent feed with strict source-specific handling.
- **G2 Buyer Intent**: account/software research behavior with buyer stage/activity semantics and documented v2 endpoint shape.
- **Wappalyzer**: technographic lookup/list APIs with documented limits and credit model.
- **HG Insights**: technographics/spend enrichment focused on enterprise software context.

Notable 2024-2026 changes: HubSpot API limit increase and lead scoring transition timeline; Salesforce API retirement tooling emphasis; PDL schema/release updates; Bombora taxonomy expansion cadence; HG Insights v2 docs updates.

**Sources:**
- https://developers.hubspot.com/changelog/increasing-our-api-limits
- https://developers.hubspot.com/docs/api/usage-details (evergreen limits mechanics)
- https://developers.hubspot.com/docs/guides/api/crm/limits-tracking (evergreen)
- https://hubspot.com/company-news/spotlight-product-deep-dive-the-complete-customer-picture-with-breeze-intelligence-hubspots-new-data-enrichment-and-buyer-intent-solution
- https://knowledge.hubspot.com/ai-tools/get-started-using-breeze-intelligence
- https://developer.salesforce.com/blogs/2024/11/api-limits-and-monitoring-your-api-usage
- https://developer.salesforce.com/blogs/2024/10/new-tools-to-help-prepare-for-api-version-retirement
- https://developer.salesforce.com/blogs/2025/05/summer25-developers
- https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/salesforce_app_limits_cheatsheet.pdf (evergreen/updated 2026)
- https://docs.peopledatalabs.com/docs/reference-company-enrichment-api
- https://docs.peopledatalabs.com/docs/bulk-company-enrichment-api
- https://docs.peopledatalabs.com/docs/usage-limits (evergreen)
- https://docs.peopledatalabs.com/changelog/september-2025-release-notes-v312
- https://docs.peopledatalabs.com/changelog/november-2025-release-notes-v321
- https://docs.zoominfo.com/reference/overview
- https://docs.zoominfo.com/docs/credit-usage-and-limits
- https://data.crunchbase.com/docs/welcome-to-crunchbase-data
- https://data.crunchbase.com/docs/using-the-api
- https://data.crunchbase.com/docs/calling-api-endpoints
- https://api.6sense.com/docs
- https://support.6sense.com/docs/api-credits-api-tokens
- https://customers.bombora.com/crc-brand/company-surge
- https://bombora-partners.atlassian.net/wiki/spaces/DOC/pages/20381698/Surge+API
- https://documentation.g2.com/docs/buyer-intent
- https://data.g2.com/openapi/v2.yaml
- https://www.wappalyzer.com/docs/api/v2/basics/ (evergreen)
- https://wappalyzer.com/docs/api/v2/lookup
- https://api.hginsights.com/
- https://data-docs.hginsights.com/v2/guides/enrichment

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. Calibration must be treated as multi-metric evidence, not a single scalar. Recent 2024-2025 ML literature highlights limitations in common calibration summaries and warns against over-trusting ECE-style outputs in isolation.

2. Calibration quality should be interpreted jointly with discrimination/generalization metrics. Practical implication: pair reliability-style checks with log-loss/PR behavior before adjusting tier thresholds.

3. Fixed `0.5` decision thresholds are usually poor for imbalanced GTM tasks. Cost-sensitive threshold tuning materially changes business outcomes and should be part of scoring governance.

4. Cost asymmetry matters more than ROC aesthetics in tier boundaries. For ICP tiering, false positives (wasted sales effort) and false negatives (missed in-market accounts) should be represented explicitly in threshold policy.

5. Reliability varies by source family and should be modeled. Equal weighting across firmographic, intent, and behavioral feeds overstates noisy channels.

6. Conflicting cross-source evidence should reduce confidence, not average away disagreement. Conflict-aware confidence downgrade is preferable to deterministic promotion.

7. Missingness is itself signal in many regimes; blind imputation can erase important reliability indicators. The scorecard should preserve missingness profiles and confidence impact.

8. Public multi-company benchmarks for B2B ICP quality remain limited. Most available data is single-company or vendor-reported; thresholds should be contextual and periodically revalidated.

9. Drift and governance are operational requirements, not optional "modeling extras." Modern guidance (NIST RMF + production monitoring docs) supports continuous measurement and incident loops.

**Sources:**
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/9a30247fcca95299c2fd48d4667282de-Abstract-Conference.html
- https://proceedings.mlr.press/v235/chidambaram24a.html
- https://papers.nips.cc/paper_files/paper/2024/file/d4cbcae8cfc8aa3ae897a1296e4e0cac-Paper-Conference.pdf
- https://sklearn.org/stable/modules/calibration.html (evergreen practical calibration guidance)
- https://scikit-learn.org/1.6/auto_examples/model_selection/plot_cost_sensitive_learning.html (evergreen practical threshold tuning guidance)
- https://proceedings.mlr.press/v235/gabidolla24a.html
- https://proceedings.mlr.press/v235/sun24o.html
- https://proceedings.mlr.press/v258/bezirganyan25a.html
- https://proceedings.mlr.press/v267/gorla25a.html
- https://arxiv.org/html/2510.02625v4
- https://pdfs.semanticscholar.org/dad1/49e1113256251cbdad273cd91a8ebb8f979e.pdf
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf (evergreen governance baseline)
- https://airc.nist.gov/airmf-resources/playbook/measure/ (evergreen operational guidance)
- https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/overview
- https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/using-model-monitoring

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. **Dirty/stale CRM + enrichment inputs** produce believable but incorrect tiering.  
   Detection: duplicate or missing-key-field rates rise while top-tier meeting acceptance drops.  
   Mitigation: enforce mandatory field gates, freshness SLAs, and pre-score data quality checks.

2. **Identity resolution collisions** leak activity between accounts.  
   Detection: abnormal merge spikes and abrupt drops in distinct-profile counts after tracking changes.  
   Mitigation: blocked placeholder identifiers, per-identifier limits, and pre-prod reconciliation tests.

3. **Single intent spikes routed directly to sales** creates early-stage false positives.  
   Detection: high intent-qualified volume but weak meeting/pipeline progression.  
   Mitigation: multi-signal persistence checks and buying-stage gating before sales handoff.

4. **No recency/decay logic** causes score inflation.  
   Detection: account pool remains permanently "hot."  
   Mitigation: rolling windows, decay rules, and periodic baseline resets.

5. **Intent-only ranking without fit triangulation** over-prioritizes irrelevant accounts.  
   Detection: high-intent cohort converts worse than balanced fit+intent cohorts.  
   Mitigation: mandatory composite scoring (fit + intent + engagement + readiness).

6. **Unversioned scoring logic during platform migrations** breaks reproducibility.  
   Detection: score distribution shifts at migration dates without explainable model-version tags.  
   Mitigation: external versioning, parallel runs, rollback plan.

7. **Qualification coverage gaps** (segment overlap or uncaptured segment) silently lose pipeline.  
   Detection: abrupt qualified-account drop in specific segment/product slices.  
   Mitigation: coverage matrix and post-release monitoring.

8. **Compliance assumptions ("vendor is compliant so we are compliant")** are unsafe.  
   Detection: missing lawful-basis matrix and weak provenance records for acquired data.  
   Mitigation: purpose-based lawful basis records, consent traceability, due diligence logs.

9. **Over-personalized or high-impact automated decisions without human review** increase legal and trust risk.  
   Detection: unsubscribes/complaints spike and legal escalations increase.  
   Mitigation: sensitive-category blocks, human override paths, explainability records.

**Sources:**
- https://www.validity.com/wp-content/uploads/2024/05/The-State-of-CRM-Data-Management-in-2024.pdf
- https://www.salesforce.com/blog/sales-ops-accurate-crm-data/?bc=HA
- https://segment.com/docs/unify/identity-resolution/identity-resolution-onboarding/
- https://6sense.com/science-of-b2b/intent-data-part-2-why-sales-hates-it-and-why-that-makes-sense/
- https://6sense.com/science-of-b2b/stop-calling-it-intent-why-b2b-marketing-needs-a-signal-shift/
- https://www.forrester.com/blogs/the-10-biggest-intent-data-mistakes-for-b2b-marketing-and-sales/
- https://support.6sense.com/docs/6sense-qualified-accounts-6qas
- https://community.hubspot.com/t5/Releases-and-Updates/HubSpot-s-New-Lead-Scoring-Your-Guide-to-the-August-2025-Update/ba-p/1110840
- https://community.hubspot.com/t5/Releases-and-Updates/Navigating-the-Transition-Migrating-from-Legacy-Scoring-to/ba-p/1139800
- https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/sending-direct-marketing-choosing-your-lawful-basis/
- https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/direct-marketing-guidance/collect-information-and-generate-leads/
- https://www.cnil.fr/en/cookies-and-other-tracking-devices-cnil-publishes-new-guidelines
- https://www.cnil.fr/en/transfer-data-social-network-advertising-purposes-cnil-imposed-fine-eu35-million
- https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-order-prohibits-data-broker-x-mode-social-outlogic-selling-sensitive-location-data
- https://www.ftc.gov/news-events/news/press-releases/2024/12/ftc-takes-action-against-mobilewalla-collecting-selling-sensitive-location-data

---

### Angle 5+: Governance, Privacy, and Measurement Ops
> Domain-specific angle: how to keep scoring systems auditable, compliant, and maintainable when used for GTM decision automation.

**Findings:**

1. Governance frameworks now require explicit measurement plans and post-deployment monitoring loops. NIST RMF guidance is increasingly used as an operational checklist for risk logging and monitoring quality.

2. EU/UK regulatory posture around profiling and marketing data use reinforces the need for lawful-basis traceability, consent provenance, and human intervention paths for consequential automated decisions.

3. Vendor data compliance claims are not substitutes for operator accountability. Teams need in-artifact provenance and policy metadata to prove why each signal was used and under which policy conditions.

4. Scorecards without model/version metadata cannot be reliably audited after migrations or policy changes.

5. Monitoring must include both technical drift (input/output changes) and business drift (tier-to-outcome degradation), or teams miss silent model deterioration.

**Sources:**
- https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf (evergreen)
- https://airc.nist.gov/airmf-resources/playbook/measure/ (evergreen)
- https://artificialintelligenceact.eu/article/10/
- https://artificialintelligenceact.eu/article/72/
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/rights-related-to-automated-decision-making-including-profiling/
- https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/overview

---

## Synthesis

The strongest cross-source pattern is that reliable ICP scoring in 2024-2026 is less about discovering a perfect formula and more about enforcing an evidence pipeline contract. Teams with durable results separate fit/intent/engagement evidence, apply source-specific gates, and require recency-aware behavior. This is a structural shift away from single-score heuristics.

A second pattern is operational: modern vendors expose many scoring features, but they do not remove the need for versioning, threshold governance, and replayability. HubSpot and Salesforce change timelines, plus intent-taxonomy evolution from providers such as Bombora, make unversioned scoring especially fragile.

There are real contradictions that should be preserved in the skill text. Calibration metrics are useful but imperfect, and intent thresholds are provider-specific and non-portable. There is also disagreement between platform guidance on whether certain engagement signals (for example email opens) are reliable enough for model training. The skill should codify this as a confidence/quality policy, not silently resolve it.

The most actionable conclusion is to evolve `segment-icp-scoring` from a threshold-only output into a reproducibility artifact: each tier decision should include subscore evidence, confidence with conflict handling, data sufficiency status, and validation metadata. This preserves explainability while still enabling automated prioritization.

---

## Recommendations for SKILL.md

- [ ] Replace single aggregate orientation with explicit `fit_score`, `intent_score`, and `engagement_score` subscores plus a governed composite.
- [ ] Add provider-specific quality gates before normalization (Bombora thresholds, G2 activity/stage constraints, and source-specific freshness rules).
- [ ] Add fail-fast data sufficiency checks and `insufficient_data` outcome for underpowered segments/cohorts.
- [ ] Add mandatory recency/decay policy and timestamp lineage requirements for all dynamic signals.
- [ ] Replace static tier thresholds as hard truth; keep them as fallback defaults and add periodic utility-based recalibration workflow.
- [ ] Add confidence model that combines source count, source reliability, conflict score, and missingness profile.
- [ ] Add reproducibility validation block (tier conversion lift, ordering sanity checks, drift status) before publishing scorecards.
- [ ] Add anti-pattern warning blocks and compliance guardrails (lawful basis, consent provenance, sensitive-data exclusions, human override).
- [ ] Expand artifact schema to carry scoring policy metadata, evidence traceability, and governance/monitoring fields.

---

## Draft Content for SKILL.md

> This section is intentionally verbose and paste-ready. Each block can be copied directly into `SKILL.md` and trimmed as needed.

### Draft: Methodology upgrade - evidence contract and scoring flow

---
### Evidence-first ICP scoring protocol

You must treat ICP scoring as an evidence synthesis problem, not a single-number opinion. Before generating any tier, build three explicit subscores:

1. `fit_score` (firmographic and structural fit)
2. `intent_score` (in-market and research-intent behavior)
3. `engagement_score` (first-party interaction and readiness)

Then compute `total_score` from those governed components. Do not output only `total_score` without subscore decomposition.

Before scoring, activate all required artifacts and fail fast if required evidence is missing:

```python
flexus_policy_document(op="activate", args={"p": f"/segments/{segment_id}/firmographic"})
flexus_policy_document(op="activate", args={"p": f"/segments/{segment_id}/behavioral-intent"})
flexus_policy_document(op="list", args={"p": "/signals/"})
flexus_policy_document(op="activate", args={"p": f"/discovery/{study_id}/jtbd-outcomes"})
```

If required artifacts do not exist, are stale beyond your freshness policy, or do not meet minimum sample rules, return an `insufficient_data` decision and do not tier accounts.

Step-by-step scoring flow:

1. **Collect and validate inputs.**  
   Check required fields and freshness before any scoring math. Required baseline fields should include: account/domain identity, firmographic banding, at least one intent-family signal, and at least one first-party engagement or interview-derived signal. If baseline is not met, quarantine records from scoring.

2. **Apply source-specific quality gates before normalization.**  
   Never normalize raw source outputs until each source passes its own minimum quality rule (for example, Bombora thresholding and topic coverage, or G2 stage/activity minimums). This prevents low-quality intent from contaminating calibrated composite scores.

3. **Build subscores and preserve traceability.**  
   Compute `fit_score`, `intent_score`, and `engagement_score` independently. Store not only numeric values but also the source evidence summary and timestamp windows used. A reviewer must be able to reconstruct each subscore from artifact references.

4. **Apply recency and decay.**  
   Dynamic signals must have explicit recency logic (rolling windows and/or decay). If the source lacks a native decay signal, apply local policy decay and persist that policy version in the scorecard.

5. **Compute composite and assign tier.**  
   Use weighted composition after quality-gated normalization. Assign tier with deterministic boundaries. If boundaries are fallback defaults instead of tuned thresholds, mark policy status as `default_thresholds`.

6. **Set confidence with conflict handling.**  
   Confidence is not source count alone. Combine source count, source reliability profile, conflict score, and missingness profile. If conflict exceeds policy threshold, cap confidence and block auto-promotion to top tier.

7. **Validate before publication.**  
   Run reproducibility checks: tier ordering sanity and conversion-lift by tier versus baseline. If checks fail, publish with `needs_review` and do not mark the run as production-ready.

Do NOT:
- Do not score records that fail mandatory data quality gates.
- Do not promote accounts to Tier 1 on single-source intent spikes.
- Do not treat a score with no evidence references as valid output.
---

### Draft: Provider-specific quality gates and normalization rules

---
### Source-specific gating rules (must run before scoring)

You must apply source-specific gating because intent/enrichment semantics are not portable across vendors.

#### Intent source gating

- **Bombora Company Surge:** enforce score thresholding policy (commonly score >= 60 in documented thresholding workflows) and topic coverage filters before including any signal in `intent_score`.
- **G2 Buyer Intent:** require stage/activity constraints and minimum event volume for the chosen interval before counting as strong intent.
- **6sense-style stage data:** treat buying stage as an input feature, not a final verdict; corroborate with fit and engagement.

If a source fails its own gate, do not coerce it into normalized score space. Mark the source as `gated_out` with reason.

#### Enrichment and firmographic gating

- Reject ambiguous account identity matches.
- Enforce freshness policy for key firmographic fields.
- Preserve provider confidence/match metadata when available.

#### Technographic gating

- Validate technology observations against recency windows.
- Avoid assuming installed technology equals buying intent; use as fit/risk context only.

#### Normalization policy

After gating, normalize each source family to a bounded subscore contribution. Avoid equal averaging by default. Weight by:

1. source reliability,
2. recency quality,
3. historical predictive utility in your environment.

If these three weights are unavailable, use conservative fallback weights and mark run metadata as `weighting_mode: "fallback"`.
---

### Draft: Tier policy, threshold tuning, and recency

---
### Tier assignment policy

Default tiers (fallback):

- Tier 1 (ICP): `total_score >= 75`
- Tier 2 (near-ICP): `50 <= total_score < 75`
- Tier 3 (not ICP): `total_score < 50`

These defaults are operational bootstraps, not permanent truth. You must periodically tune tier thresholds against business utility.

#### Threshold tuning policy

1. Start with calibrated score outputs.
2. Define cost assumptions for false positives and false negatives.
3. Evaluate candidate thresholds using utility metrics and tier outcome lift.
4. Select thresholds that optimize utility while preserving tier ordering sanity.
5. Version the threshold set and stamp it into each scorecard.

If you cannot tune due to insufficient outcomes data, use fallback thresholds and mark `threshold_policy_status: "default_due_to_insufficient_outcomes"`.

#### Recency and decay policy

Every dynamic signal included in scoring must record:

- event timestamp,
- evaluation window,
- decay rule used.

Recommended operating windows for GTM signal review are short (week), medium (month), and contextual long (quarter). If no signal occurs inside policy windows, down-weight stale intent rather than carrying historical strength unchanged.
---

### Draft: Confidence, conflict, and missing-data handling

---
### Confidence model (replace source-count-only logic)

You must calculate confidence from multiple factors:

1. **Coverage factor:** number of independent source families contributing evidence.
2. **Reliability factor:** quality/reputation/performance of each source family in your environment.
3. **Conflict factor:** degree of contradiction between source families.
4. **Missingness factor:** concentration of missing required fields in high-impact dimensions.

Example confidence policy:

- `high`: strong coverage, low conflict, low missingness, and no critical source gates failed.
- `medium`: acceptable coverage with moderate conflict or moderate missingness.
- `low`: poor coverage, high conflict, or high missingness.

If conflict is high (for example, strong intent but poor fit and no buying-committee corroboration), cap confidence at `low` and require review before Tier 1 assignment.

#### Missing-data policy

Do not erase missingness with blanket imputation and pretend confidence is unchanged. Preserve missingness indicators in artifact outputs and reflect missingness in confidence.

Required behavior:

- carry missingness metrics per account and dimension,
- document imputation method (if used),
- mark whether missingness likely affects final tier.

If missingness materially affects fit or timing dimensions, do not auto-promote beyond Tier 2.
---

### Draft: Validation and reproducibility requirements

---
### Reproducibility validation block

Before publishing a scorecard run as production-ready, you must run and record:

1. **Tier ordering sanity check:** higher tiers should not underperform lower tiers on key downstream outcomes over an equivalent window.
2. **Baseline comparison:** quantify lift/decline of each tier versus overall baseline.
3. **Distribution stability check:** detect abrupt score distribution shifts versus prior version/run.
4. **Policy/version replayability:** verify the run can be reconstructed from stored policy version, source artifacts, and timestamp window.

Publication rule:

- If validation passes: mark `validation_status: "pass"`.
- If any required check fails: mark `validation_status: "needs_review"` and include failed checks list.

Do NOT silently ship updated tiering when validation fails.
---

### Draft: Available Tools (real method syntax)

---
## Available Tools

Use these policy-document calls to load required scoring artifacts:

```python
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/firmographic"})
flexus_policy_document(op="activate", args={"p": "/segments/{segment_id}/behavioral-intent"})
flexus_policy_document(op="list", args={"p": "/signals/"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```

Use this to persist the final scorecard artifact:

```python
write_artifact(
    artifact_type="segment_icp_scorecard",
    path="/segments/{segment_id}/icp-scorecard",
    data={...},
)
```

Usage rules:

1. Always activate and validate dependencies before computing scores.
2. If any dependency fails quality or sufficiency checks, write a scorecard with `run_status: "insufficient_data"` and stop.
3. Persist source lineage and policy version in every successful or partial run.
4. Never write tier outputs without evidence references.
---

### Draft: Anti-pattern warning blocks

> [!WARNING]
> **Do not route one-off intent spikes directly to sales qualification.**  
> Detection signal: intent-qualified count rises while meeting conversion stagnates.  
> Consequence: false positives, SDR capacity waste, and trust erosion.  
> Mitigation: require multi-signal persistence and buying-stage corroboration before handoff.

> [!WARNING]
> **Do not score on dirty or stale CRM/enrichment data.**  
> Detection signal: duplicate rates and missing critical fields increase while top-tier outcomes degrade.  
> Consequence: high-confidence wrong tiers.  
> Mitigation: enforce pre-score data quality gates, freshness SLAs, and record quarantine.

> [!WARNING]
> **Do not hide scoring logic inside unversioned UI configuration.**  
> Detection signal: unexplained distribution shifts after vendor migration or admin edits.  
> Consequence: non-reproducible scorecards and broken longitudinal analysis.  
> Mitigation: version scoring policy externally, stamp every run, parallel-test before cutover.

> [!WARNING]
> **Do not assume vendor compliance equals your compliance.**  
> Detection signal: no lawful-basis records, no consent provenance, no sensitive-data exclusion policy.  
> Consequence: legal and trust risk.  
> Mitigation: maintain policy metadata per source and decision path, and require human override for high-impact automation.

### Draft: Governance and compliance guardrails

---
### Governance and compliance guardrails

You must include policy metadata sufficient for internal audit:

- lawful basis category for marketing use where applicable,
- provenance reference for each source family,
- model/policy version and change date,
- human review requirement flag for high-impact routing decisions.

You must not create or use sensitive inferred categories for ICP tiering. If a source exposes potentially sensitive attributes, exclude them from scoring features unless explicit legal approval is documented.

For automated decisions that materially affect outreach inclusion/exclusion, provide:

1. explanation record,
2. human intervention path,
3. challenge/review mechanism.

If governance metadata is absent, confidence must be capped and run marked `needs_review`.
---

### Draft: Schema additions

```json
{
  "segment_icp_scorecard": {
    "type": "object",
    "required": [
      "segment_id",
      "scored_at",
      "run_status",
      "scoring_model",
      "accounts",
      "tier_distribution",
      "confidence",
      "validation",
      "governance",
      "source_artifacts"
    ],
    "additionalProperties": false,
    "properties": {
      "segment_id": {
        "type": "string",
        "description": "Segment identifier used for this score run."
      },
      "scored_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when scoring completed."
      },
      "run_status": {
        "type": "string",
        "enum": ["ok", "insufficient_data", "needs_review"],
        "description": "Overall run state after sufficiency and validation checks."
      },
      "scoring_model": {
        "type": "object",
        "required": [
          "model_version",
          "dimensions",
          "subscore_weights",
          "tier_thresholds",
          "recency_policy",
          "quality_gates"
        ],
        "additionalProperties": false,
        "properties": {
          "model_version": {
            "type": "string",
            "description": "Version identifier for scoring logic and thresholds."
          },
          "dimensions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "max_points", "source_skills"],
              "additionalProperties": false,
              "properties": {
                "name": {
                  "type": "string",
                  "description": "Dimension name such as problem_fit, budget_fit, tech_fit, timing_fit, access_fit."
                },
                "max_points": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Maximum points available for this dimension."
                },
                "source_skills": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Upstream skill artifacts that feed this dimension."
                }
              }
            }
          },
          "subscore_weights": {
            "type": "object",
            "required": ["fit_weight", "intent_weight", "engagement_weight"],
            "additionalProperties": false,
            "properties": {
              "fit_weight": {
                "type": "number",
                "minimum": 0,
                "description": "Composite weight for fit subscore."
              },
              "intent_weight": {
                "type": "number",
                "minimum": 0,
                "description": "Composite weight for intent subscore."
              },
              "engagement_weight": {
                "type": "number",
                "minimum": 0,
                "description": "Composite weight for engagement subscore."
              }
            }
          },
          "tier_thresholds": {
            "type": "object",
            "required": ["tier1_min", "tier2_min", "policy_status"],
            "additionalProperties": false,
            "properties": {
              "tier1_min": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Minimum total score for Tier 1."
              },
              "tier2_min": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Minimum total score for Tier 2."
              },
              "policy_status": {
                "type": "string",
                "enum": ["default_thresholds", "tuned_thresholds", "default_due_to_insufficient_outcomes"],
                "description": "Whether thresholds are tuned or fallback defaults."
              }
            }
          },
          "recency_policy": {
            "type": "object",
            "required": ["window_days_short", "window_days_medium", "window_days_long", "decay_mode"],
            "additionalProperties": false,
            "properties": {
              "window_days_short": {
                "type": "integer",
                "minimum": 1,
                "description": "Short recency window in days."
              },
              "window_days_medium": {
                "type": "integer",
                "minimum": 1,
                "description": "Medium recency window in days."
              },
              "window_days_long": {
                "type": "integer",
                "minimum": 1,
                "description": "Long recency window in days."
              },
              "decay_mode": {
                "type": "string",
                "enum": ["none", "linear", "exponential"],
                "description": "Decay function used for time-sensitive signals."
              }
            }
          },
          "quality_gates": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["source_family", "gate_name", "passed"],
              "additionalProperties": false,
              "properties": {
                "source_family": {
                  "type": "string",
                  "description": "Source family such as bombora, g2, crm, firmographic, technographic."
                },
                "gate_name": {
                  "type": "string",
                  "description": "Human-readable gate label."
                },
                "passed": {
                  "type": "boolean",
                  "description": "Whether the gate passed for this run."
                },
                "details": {
                  "type": "string",
                  "description": "Short rationale for pass/fail."
                }
              }
            },
            "description": "Run-level source quality gate outcomes."
          }
        }
      },
      "accounts": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "domain",
            "fit_score",
            "intent_score",
            "engagement_score",
            "total_score",
            "icp_tier",
            "confidence",
            "conflict_score",
            "missingness_profile",
            "evidence_refs"
          ],
          "additionalProperties": false,
          "properties": {
            "domain": {
              "type": "string",
              "description": "Account domain or canonical account identifier."
            },
            "fit_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "Firmographic and structural fit subscore."
            },
            "intent_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "Intent and in-market behavior subscore after source gating."
            },
            "engagement_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "First-party engagement and readiness subscore."
            },
            "total_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "Composite score used for tier assignment."
            },
            "icp_tier": {
              "type": "string",
              "enum": ["tier1", "tier2", "tier3"],
              "description": "Assigned ICP tier."
            },
            "confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "Confidence state after coverage, reliability, conflict, and missingness assessment."
            },
            "conflict_score": {
              "type": "number",
              "minimum": 0,
              "maximum": 1,
              "description": "Cross-source contradiction score where higher means greater disagreement."
            },
            "missingness_profile": {
              "type": "object",
              "required": ["missing_required_fields", "missingness_rate"],
              "additionalProperties": false,
              "properties": {
                "missing_required_fields": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "Required fields absent at scoring time."
                },
                "missingness_rate": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1,
                  "description": "Proportion of required fields missing for this account."
                }
              }
            },
            "evidence_refs": {
              "type": "array",
              "items": {"type": "string"},
              "description": "Artifact references used to compute this account score."
            }
          }
        }
      },
      "tier_distribution": {
        "type": "object",
        "required": ["tier1_count", "tier2_count", "tier3_count"],
        "additionalProperties": false,
        "properties": {
          "tier1_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of Tier 1 accounts in run output."
          },
          "tier2_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of Tier 2 accounts in run output."
          },
          "tier3_count": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of Tier 3 accounts in run output."
          }
        }
      },
      "confidence": {
        "type": "string",
        "enum": ["high", "medium", "low"],
        "description": "Overall run-level confidence."
      },
      "validation": {
        "type": "object",
        "required": ["validation_status", "tier_ordering_check", "baseline_lift_check", "drift_status"],
        "additionalProperties": false,
        "properties": {
          "validation_status": {
            "type": "string",
            "enum": ["pass", "needs_review"],
            "description": "Overall validation result."
          },
          "tier_ordering_check": {
            "type": "string",
            "enum": ["pass", "fail", "not_available"],
            "description": "Whether higher tiers outperform lower tiers on tracked outcomes."
          },
          "baseline_lift_check": {
            "type": "string",
            "enum": ["pass", "fail", "not_available"],
            "description": "Whether tier outcomes beat or match baseline expectations."
          },
          "drift_status": {
            "type": "string",
            "enum": ["stable", "warning", "critical", "not_monitored"],
            "description": "Latest monitored drift status relevant to score reliability."
          },
          "failed_checks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of failed validation checks when status is needs_review."
          }
        }
      },
      "governance": {
        "type": "object",
        "required": ["policy_version", "provenance_logged", "human_override_path"],
        "additionalProperties": false,
        "properties": {
          "policy_version": {
            "type": "string",
            "description": "Governance policy version used during scoring."
          },
          "provenance_logged": {
            "type": "boolean",
            "description": "Whether source provenance metadata is present for all scoring inputs."
          },
          "human_override_path": {
            "type": "boolean",
            "description": "Whether a human intervention path exists for high-impact automated decisions."
          },
          "lawful_basis_recorded": {
            "type": "boolean",
            "description": "Whether lawful basis metadata was documented where required."
          }
        }
      },
      "source_artifacts": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Artifact IDs or paths used in this score run."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Public, open, cross-company benchmark datasets for B2B ICP/account scoring remain limited; many available references are vendor or single-organization studies.
- Some vendor docs expose conceptual thresholds and examples but do not publish global hard API rate limits publicly for all plans; plan-specific limits may require authenticated docs.
- Regulatory mappings are jurisdiction-sensitive; this research highlights governance implications but is not legal advice and should be localized by deployment region.
- Contradictory vendor guidance exists for certain engagement signals (for example, email-open reliability); environment-specific validation remains necessary.
