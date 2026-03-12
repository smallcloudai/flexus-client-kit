# Research: discovery-survey

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/discovery-survey/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-survey` designs and collects customer discovery instruments: interview guides, screeners, and structured surveys. The core behavior is hypothesis-first design, strict bias control, and reliable response collection across Typeform, SurveyMonkey, and Qualtrics integrations.

The practical problem this skill solves is common in early-stage and growth product work: teams often ask questions that cannot falsify assumptions, over-trust low-quality samples, and treat hypothetical intent as behavioral truth. This skill must produce instruments that can survive real-world constraints (fraud, panel noise, async export flows, rate limits, and consent obligations) while still moving quickly enough for iterative discovery.

Research was scoped to modern practice and evidence from 2024-2026 where available. Older references are only kept when they remain foundational and are explicitly marked **Evergreen**.

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
- [x] All findings are from 2024-2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- No generic filler ("it is important to...", "best practices suggest...") without concrete backing
- No invented tool names, method IDs, or API endpoints - only verified real ones
- Contradictions between sources are explicitly noted, not silently resolved
- Volume: findings section is within the 800-4000 word target

Quality gate result: passed.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. Recent evidence separates **near saturation** from **true saturation**, and the difference is large enough to matter operationally. In a 2024 secondary analysis of five web-based qualitative studies, near code saturation appeared around n=15-23, while true saturation often required n=30-67. This supports a two-speed operating model: near saturation for discovery velocity and true saturation for high-stakes synthesis.

2. Saturation speed is not a single magic number; it depends on guide structure and coding strategy. More structured guides and deductive coding saturate earlier than exploratory, inductive work. The skill should therefore set stopping criteria based on study intent (exploratory vs confirmatory), not fixed interview counts.

3. Large-scale screener operations show measurable drop-off effects from format decisions. A 2024 report on 42,756 screeners found average drop-off around 6%, with open-ended additions increasing abandonment more than closed-ended additions. This supports "mostly closed-ended + one articulation check" instead of all-open screeners.

4. Behavior-first screening remains a strong practical pattern in 2024-2025 practitioner guidance. High-quality recruitment screeners qualify by lived problem experience and role context rather than broad demographics alone, and include anti-gaming consistency checks.

5. Cognitive testing remains central in modern instrument design, not an optional add-on. CDC and U.S. Census 2024-2025 materials consistently show that comprehension/recall/judgment/response probing and flow/usability checks surface wording and route failures before expensive fielding.

6. Format choice should be explicitly tied to decision goal. Pew's 2024 evidence shows closed-ended online formats can better support comparability/tracking in some contexts, while open-ended formats are better for emergent-category discovery but add coding burden and nonresponse risk.

7. Iterative interview protocol construction is now commonly formalized in phases (alignment -> guide design -> feedback -> pilot). This aligns with the skill's need to produce auditable iteration rather than one-shot scripts.

8. **Evergreen:** transparent saturation formulas (base size, run length, new-information threshold) remain useful for documenting why collection stopped, and for reducing arbitrary interview counts.

**Sources:**
- https://www.jmir.org/2024/1/e52998/
- https://www.userinterviews.com/screener-dropoff-report
- https://www.userinterviews.com/blog/seven-common-screener-survey-mistakes-and-how-to-fix-them
- https://blog.logrocket.com/ux-design/effective-screener-surveys/
- https://www.cdc.gov/nchs/ccqder/question-evaluation/cognitive-interviewing.html
- https://www.census.gov/library/working-papers/2024/adrm/rsm2024-10.html
- https://www.census.gov/library/working-papers/2025/adrm/rsm2025-10.html
- https://www.pewresearch.org/decoded/2024/05/13/measuring-partisanship-in-europe-how-online-survey-questions-compare-with-phone-polls/
- https://www.shs-conferences.org/articles/shsconf/pdf/2024/02/shsconf_access2024_04006.pdf
- https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0232076 (**Evergreen**)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. Typeform's Create and Responses APIs remain straightforward REST+JSON with stable base URLs (`https://api.typeform.com/` and EU variants), but data-center routing must be explicit in workspace configuration for reliable calls.

2. `PUT /forms/{form_id}` in Typeform is full-replace and can delete omitted fields and their associated data semantics. This creates a real destructive-update risk if the skill performs partial updates without read-modify-write.

3. Typeform response retrieval supports robust incremental ingestion (`since`, `until`, `after`, `before`, `page_size` up to 1000), but docs note very recent responses (about the last 30 minutes) may be delayed in polling.

4. Typeform explicitly recommends webhooks for near-real-time collection; the practical architecture is webhook-first plus periodic polling backfill for missed events.

5. Typeform rate limits for Create/Responses (2 requests/sec/account) are low enough that queueing and jittered retries should be standard behavior, not optional.

6. SurveyMonkey v3 remains OAuth2 with account/tenant host routing via `access_url`, so connector logic must persist and use the host returned during auth rather than hardcoded global hosts.

7. SurveyMonkey provides distinct response surfaces (`/responses`, `/responses/bulk`, `/responses/{id}/details`) that should map to different workloads: change detection, batched extraction, and deep per-response inspection.

8. SurveyMonkey collector creation (`POST /surveys/{survey_id}/collectors`) is a critical workflow for distribution and must be first-class in the skill when instrument creation is automated.

9. SurveyMonkey draft/private app quotas (120 req/min and initial 500 req/day) can throttle discovery pipelines quickly if export polling is naive; batching and quota-aware scheduling are required.

10. Qualtrics response exports are explicitly asynchronous: start export, poll progress, then download file. The skill already models this pattern, but guidance should enforce polling cadence and timeout behavior.

11. Qualtrics support docs note request parameter sensitivity (for example, case-sensitive fields in some contexts) and datacenter correctness requirements for export retrieval; these are common operational failure points.

12. 2024 Typeform changelog entries (for example, partial response support and removed capability field) reinforce the need for schema-drift-tolerant connector parsing.

**Sources:**
- https://www.typeform.com/developers/get-started/
- https://www.typeform.com/developers/create/reference/create-form/
- https://www.typeform.com/developers/create/reference/update-form/
- https://www.typeform.com/developers/responses/reference/retrieve-responses/
- https://www.typeform.com/developers/webhooks/
- https://www.typeform.com/developers/changelog/
- https://api.surveymonkey.com/v3/docs
- https://raw.githubusercontent.com/SurveyMonkey/public_api_docs/main/includes/_responses.md (**Evergreen** docs mirror)
- https://raw.githubusercontent.com/SurveyMonkey/public_api_docs/main/includes/_webhooks.md (**Evergreen** docs mirror)
- https://www.qualtrics.com/support/integrations/api-integration/common-api-use-cases/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-questions-by-product/

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. 2024 replication work from Pew reinforces that opt-in samples can overstate rare attitudes in specific subgroups and fail replication under probability-based panels. This directly impacts discovery claims from open online samples.

2. For nonprobability samples, confidence intervals and "margin of error" language are often misapplied. Current federal and AAPOR guidance emphasizes that classical MOE is a probability-sample construct.

3. Fraud-detection method choice can materially change which responses survive and therefore change substantive conclusions. 2024 evidence comparing multilayer vs platform-level detection found low agreement and large kept-sample differences.

4. Single indicators (like one attention check) are weak quality guards. Evidence in 2024 shows IMCs can perform poorly for carelessness screening and should not be the only quality gate.

5. Straight-lining and speed rules are context-sensitive; there is no universal cutoff that works across instruments. Better practice is multi-flag scoring plus sensitivity analysis.

6. Qualitative rigor currently splits into two coherent lanes:
   - codebook/reliability lane (predefined coding frame + inter-coder agreement protocol),
   - reflexive thematic lane (coherence and reflexive transparency over kappa targets).
   Mixing lanes without declaring epistemic stance creates invalid quality claims.

7. A practical interpretation framework for this skill is to classify outputs as:
   - **directional**: useful for exploration, not sufficient for high-stakes commitment,
   - **decision-grade**: sufficiently robust to support expensive or irreversible moves.

8. Recent standards movement (ICC/ESOMAR 2025) pushes stronger transparency and human oversight in AI-assisted research workflows. This should flow into reporting fields, not just prose warnings.

**Sources:**
- https://www.pewresearch.org/short-reads/2024/03/05/online-opt-in-polls-can-produce-misleading-results-especially-for-young-people-and-hispanic-adults/
- https://www.pewresearch.org/methods/2023/09/07/comparing-two-types-of-online-survey-samples/ (**Evergreen** benchmark)
- https://formative.jmir.org/2024/1/e47091/
- https://www.jmir.org/2024/1/e60184/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11501094/
- https://largescaleassessmentsineducation.springeropen.com/articles/10.1186/s40536-024-00205-y
- https://acf.gov/sites/default/files/documents/opre/opre_nonprobability_samples_brief_september2024.pdf
- https://aapor.org/wp-content/uploads/2023/01/Margin-of-Sampling-Error-508.pdf (**Evergreen**)
- https://www.ajqr.org/article/inter-coder-agreement-in-qualitative-coding-considerations-for-its-use-14887
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11157981/
- https://esocorpwebsitestg.blob.core.windows.net/strapi-uploads/uploads/icc_esomar_international_code_on_market_opinion_and_social_research_and_data_analytics_2025_7e74a25b54.pdf

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

1. Leading wording still measurably shifts responses in 2024 evidence. Discovery prompts that imply a preferred answer can produce false confidence and downstream product misprioritization.

2. Agree/disagree batteries are vulnerable to acquiescence bias. Using unbalanced agreement formats for key problem statements can inflate apparent demand or urgency.

3. Hypothetical-intent questions remain a high-frequency trap. "Would you buy/use..." responses often diverge from observed behavior and can mislead roadmap decisions.

4. Screener leakage and gaming remain active risks in incentivized online recruitment. Respondents can learn pass criteria, especially when screeners telegraph purpose and thresholds.

5. Open-link + incentive combinations can trigger bot/fraud swarms; case-like reports from 2024-2025 show very high invalid-completion rates when controls are weak.

6. Weak quality-control stacks create false assurance. Relying on a single check (captcha only, speed only, IMC only) misses substantial bad data.

7. Question order effects and post-treatment sensitive question placement can alter observed relationships and subgroup signals.

8. Over-interpretation of single-wave opt-in subgroup outliers is a recurring analytic failure, especially for rare beliefs and sensitive claims.

9. Consent/recording disclosure is often treated as boilerplate instead of an auditable protocol, creating legal and ethical risk and potentially invalidating collected data.

10. "Bad output" signature for this skill is now clear: hypothesis-free question blocks, hypothetical-first prompts, low-trust sample provenance, absent exclusion logic, and no evidence-grade declaration.

**Sources:**
- https://link.springer.com/article/10.1007/s11135-024-01934-6
- https://link.springer.com/article/10.1007/s11135-024-01891-0
- https://www.surveypractice.org/article/38280-assessing-measurement-error-in-hypothetical-questions (**Evergreen**)
- https://www.cambridge.org/core/journals/journal-of-experimental-political-science/article/fraud-in-online-surveys-evidence-from-a-nonprobability-subpopulation-sample/52CCFB8B9FEFC4C11155BE256F6D9116 (**Evergreen**)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11686022/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12142081/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11646990/
- https://www.pewresearch.org/short-reads/2024/03/05/online-opt-in-polls-can-produce-misleading-results-especially-for-young-people-and-hispanic-adults/
- https://www.ukri.org/councils/esrc/guidance-for-applicants/research-ethics-guidance/consent/

---

### Angle 5+: Ethics, Consent, and Governance Requirements
> Discovery research now intersects legal, ethical, and AI-assistance governance obligations. This angle consolidates hard constraints for instrument and collection design.

**Findings:**

1. Current guidance emphasizes that consent is not a one-time checkbox. Consent language should clearly cover recording, storage, secondary use, sharing boundaries, and withdrawal mechanism.

2. ICC/ESOMAR 2025 code updates increase expectations for transparency and accountability in data analytics and AI-assisted research; teams should document human oversight in analysis decisions.

3. Federal cognitive interview standards remain useful as baseline governance even when older: plan, purposeful sampling, documented protocol, systematic analysis, and report transparency are still relevant.

4. Governance should be embedded in schema fields and collection logs (who approved instrument, what consent script used, retention window), not left to narrative notes.

5. Cross-tool collection requires explicit region and data-location awareness (Typeform EU base URLs, Qualtrics datacenter handling) to avoid accidental policy violations.

**Sources:**
- https://www.ukri.org/councils/esrc/guidance-for-applicants/research-ethics-guidance/consent/ (updated 2026)
- https://esocorpwebsitestg.blob.core.windows.net/strapi-uploads/uploads/icc_esomar_international_code_on_market_opinion_and_social_research_and_data_analytics_2025_7e74a25b54.pdf (2025)
- https://obamawhitehouse.archives.gov/sites/default/files/omb/inforeg/directive2/final_addendum_to_stat_policy_dir_2.pdf (**Evergreen** foundational standards)
- https://www.typeform.com/developers/get-started/
- https://www.qualtrics.com/support/integrations/api-integration/common-api-use-cases/

---

## Synthesis

The strongest cross-angle pattern is that discovery rigor is now less about "asking good questions" in isolation and more about operating a full evidence system: explicit assumptions, instrument design controls, respondent-quality defenses, and interpretation boundaries. In other words, good wording is necessary but not sufficient.

A second pattern is the collapse of one-number heuristics. There is no universal interview count for saturation, no universal fraud threshold, and no one metric that certifies data quality. The practical replacement is explicit decision rules: declare saturation mode before fielding, define exclusion logic before analysis, and classify output confidence at the end.

Third, the tool landscape is mature but operationally sharp-edged. The skill's current tool coverage is directionally correct, but production reliability depends on details: destructive update behavior (Typeform PUT), async export state machines (Qualtrics), host/tenant routing (SurveyMonkey), and low API quotas that require queue discipline. The difference between a clean pilot and a failed collection run is mostly in these mechanics.

Contradictions in the literature are mostly trade-off contradictions, not factual conflicts. Open-ended prompts are useful for discovery depth but increase drop-off and coding burden. Opt-in samples can be useful for directional discovery but are unreliable for rare-attitude prevalence claims. These are not "pick one forever" conflicts; they are context-setting requirements the skill should force users to declare.

Most surprising finding: modern failure case studies show how quickly data quality can collapse under open-link incentivized collection, even in sophisticated teams. This supports making anti-fraud and exclusion policy first-class fields in artifacts, not optional analyst notes.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Add an explicit **evidence-grade framework** (`directional` vs `decision_grade`) with nonprobability MOE disclaimer and required justification fields.
- [x] Add a **saturation protocol** that forces near-vs-true declaration, with base size, run length, and new-information threshold.
- [x] Expand methodology with a **behavior-first screener blueprint** (mostly closed-ended, one articulation check, anti-gaming consistency check, drop-off monitoring).
- [x] Add mandatory **pilot loop guidance** combining cognitive probes and flow/usability checks before full fielding.
- [x] Upgrade collection guidance to a **reliability architecture**: webhook-first + polling backfill, async export polling state machine, rate-limit-aware retries, and tenant/datacenter handling.
- [x] Add a **layered quality-control stack** and explicitly forbid IMC-only or single-check gating.
- [x] Add named **anti-pattern warning blocks** with detection signals, consequences, and mitigations.
- [x] Expand schema with governance and quality metadata: hypothesis mapping, quality diagnostics, exclusion policy, evidence grade, and consent/retention fields.
- [x] Add explicit consent/governance instructions aligned to current 2025-2026 standards guidance.

---

## Draft Content for SKILL.md

### Draft: Evidence Grade and Decision Boundaries

Add this section near the top of the skill, immediately after the core mode statement.

---
### Evidence Grade Policy

You must classify every completed discovery run as either `directional` or `decision_grade` before you publish findings.

Use `directional` when your data is useful for exploration but does not support high-stakes commitments. Typical triggers: nonprobability sample, weak respondent quality confidence, small n without robust replication, inconsistent quality screens, or unresolved coding disagreements.

Use `decision_grade` only when collection quality, interpretation rigor, and uncertainty disclosure are all sufficient for expensive or hard-to-reverse actions.

Do not report classical margin-of-error language for nonprobability data. If your sample is opt-in or panel-based without known inclusion probabilities, you must state that inferential precision is model-dependent and should be interpreted as directional unless stronger design assumptions are validated.

Required output fields in your findings summary:
1. `evidence_grade`: `directional` or `decision_grade`.
2. `grade_rationale`: 3-7 sentences naming the exact signals that justify the grade.
3. `inference_limits`: specific claims you cannot make from the data.
4. `recommended_next_validation`: concrete follow-up step needed to upgrade confidence.
---

### Draft: Methodology - Hypothesis Mapping, Interview Flow, and Screener Design

Replace the existing brief methodology with the following expanded operating instructions.

---
### Methodology

You work in hypothesis-first mode. Every question must map to a validation need. If a question cannot change a decision, delete it.

#### 1) Build a hypothesis-to-evidence map before writing any instrument

Before drafting questions, define:
- the decision this research informs,
- the assumptions/hypotheses that could change that decision,
- disconfirming evidence for each hypothesis.

For each hypothesis, add:
- `hypothesis_id`
- `decision_ref`
- `evidence_needed`
- `disconfirming_signal`
- `priority` (`critical`, `important`, `nice_to_know`)

If you cannot define disconfirming evidence, you are writing exploratory conversation prompts, not a validation instrument. Mark that explicitly and downgrade expected confidence.

#### 2) Interview guide construction (past-behavior first)

Structure interview guides in this order:
1. Context warm-up (role, environment, frequency of relevant workflows)
2. Last-incident narrative ("Tell me about the last time...")
3. Timeline and trigger probes
4. Decision criteria and trade-off probes
5. Objection/friction probes
6. Wrap-up and "what we did not ask"

Rules:
- Ask for concrete episodes before opinions.
- Probe for actions and constraints, not abstract preferences.
- Keep the first 2-3 core prompts stable across interviews for comparability.
- Allow flexible follow-ups, but keep a required core.

Forbidden patterns:
- "Would you use/buy this?"
- "If this existed, how valuable would it be?"
- Questions that mention your proposed solution in problem-diagnosis blocks.
- Double-barreled prompts with multiple ideas in one question.

#### 3) Screener blueprint (quality + completion balanced)

Design screeners as short qualification instruments, not mini-interviews.

Default pattern:
- mostly closed-ended qualification items,
- one open-ended articulation check,
- one consistency check,
- routing logic for eligible profiles.

Implementation constraints:
- keep screener length intentionally tight (target around 8-12 items unless justified),
- qualify primarily on role + recent lived problem exposure,
- avoid purpose-revealing wording that enables gaming,
- avoid demographic-only qualification except when decision context requires it.

When incentives are used:
- add anti-gaming checks,
- separate qualification logic from visible success cues,
- document exclusion criteria before launch.

#### 4) Survey instrument design for quant discovery

For quant discovery surveys:
- use forced-choice, Likert, and numeric scales for comparable analysis,
- use open text selectively for novelty capture or explanation,
- route participants using explicit branching logic tied to hypothesis map.

Use open-ended items intentionally:
- include them when discovering unknown categories or language,
- avoid excessive open-ended burden in screeners,
- do not place heavy free-text blocks before key closed-form measures unless this is a deliberate design choice.

#### 5) Pilot loop is mandatory

You must run pilot iterations before full launch.

Pilot cycle:
1. cognitive probing for comprehension/recall/judgment/response issues,
2. flow/usability check for routing and completion friction,
3. revision log per changed item,
4. confirmatory pilot re-run on changed blocks.

Do not field at scale if high-volatility terms or confusing branch logic remain unresolved.

---

### Draft: Saturation and Stopping Rules

Add a dedicated section for stopping criteria.

---
### Saturation and Stopping

You must declare the stopping model before interview collection starts.

Allowed models:
- `near_saturation`: stop when incremental novelty is low enough for directional decisions.
- `true_saturation`: continue until new-code emergence is effectively exhausted for decision-grade synthesis.

Required plan fields:
- `saturation_mode`
- `base_n`
- `run_length`
- `new_information_threshold`
- `heterogeneity_adjustment_rule`

Default operating baseline (can be overridden with rationale):
- start with `base_n=12`,
- evaluate novelty over `run_length=4`,
- use `new_information_threshold<=0.05` for near-saturation stop checks,
- require one confirmation run before stopping.

Escalate sample when:
- target segment is heterogeneous,
- interview guide is weakly structured,
- coding is exploratory/inductive and still generating new categories.

Your output must include a short stopping audit:
- where novelty flattened,
- what still remained uncertain,
- why stop was acceptable for the chosen evidence grade.
---

### Draft: Collection Reliability and Tool Use

Replace or expand the tool section with operational guidance that includes call syntax and reliability constraints.

---
## Available Tools

Use only verified connector methods. Do not invent method IDs.

### Typeform

Create instrument:
```python
typeform(
    op="call",
    args={
        "method_id": "typeform.forms.create.v1",
        "title": "Study Name",
        "fields": [...],
        "settings": {"is_public": false}
    }
)
```

List responses:
```python
typeform(
    op="call",
    args={
        "method_id": "typeform.responses.list.v1",
        "uid": "form_id",
        "page_size": 100
    }
)
```

Operational guidance:
- Typeform Create/Responses are rate-limited (2 req/sec/account). Queue and backoff accordingly.
- Polling may miss very recent responses; implement polling with overlap windows and idempotent dedupe.
- For low-latency collection, prefer webhook-driven ingestion where available in your integration stack, then run periodic polling backfill.
- Do not perform partial destructive updates to existing forms without preserving full field sets.

### SurveyMonkey

Create survey:
```python
surveymonkey(
    op="call",
    args={
        "method_id": "surveymonkey.surveys.create.v1",
        "title": "Study Name",
        "pages": [...]
    }
)
```

List responses:
```python
surveymonkey(
    op="call",
    args={
        "method_id": "surveymonkey.surveys.responses.list.v1",
        "survey_id": "survey_id"
    }
)
```

Create collector:
```python
surveymonkey(
    op="call",
    args={
        "method_id": "surveymonkey.collectors.create.v1",
        "survey_id": "survey_id",
        "type": "weblink"
    }
)
```

Operational guidance:
- Respect account quotas and minute/day limits with budgeted polling.
- Persist tenant/access host returned by auth flow; do not assume a single global endpoint.
- Use response list calls for change detection and deeper retrieval paths for heavy answer payloads when your connector exposes them.

### Qualtrics

Create survey:
```python
qualtrics(
    op="call",
    args={
        "method_id": "qualtrics.surveys.create.v1",
        "SurveyName": "Study Name",
        "Language": "EN",
        "ProjectCategory": "CORE"
    }
)
```

Start export:
```python
qualtrics(
    op="call",
    args={
        "method_id": "qualtrics.responseexports.start.v1",
        "surveyId": "SV_xxx",
        "format": "json"
    }
)
```

Poll export progress:
```python
qualtrics(
    op="call",
    args={
        "method_id": "qualtrics.responseexports.progress.get.v1",
        "surveyId": "SV_xxx",
        "exportProgressId": "ES_xxx"
    }
)
```

Download export file:
```python
qualtrics(
    op="call",
    args={
        "method_id": "qualtrics.responseexports.file.get.v1",
        "surveyId": "SV_xxx",
        "fileId": "xxx"
    }
)
```

Operational guidance:
- Export is asynchronous by design: start -> poll -> download.
- Poll every 10-30 seconds with timeout and retry bounds.
- Keep parameter casing exact and datacenter routing correct; both are common failure causes.
- Persist export job states and support resume after interruption.
---

### Draft: Quality Controls and Interpretation Rules

Add a dedicated section that governs data quality decisions.

---
### Response Quality Controls

Never rely on one data-quality signal.

Build a layered quality stack with:
- speed/timing checks,
- response-pattern checks (straight-lining and long-string behavior),
- screener-main consistency checks,
- duplicate fingerprint checks where available,
- open-text coherence checks,
- source-wave anomaly checks (sudden completion bursts, unusual cluster timing).

Use multi-flag review:
- avoid auto-exclusion from one weak signal,
- define exclusion policy before seeing outcomes,
- log which rules fired per respondent.

Do NOT use IMC-only screening as your sole quality gate.

### Interpretation Rules

1. If sample is nonprobability/opt-in, mark output as directional unless you provide robust additional validation.
2. Do not present classical MOE for nonprobability samples.
3. For subgroup claims, require stronger evidence than for overall trends, especially for rare-attitude estimates.
4. Treat sensitive, high-salience outliers as replication candidates before decision-making.
5. Distinguish:
   - `signal`: stable across checks and coherent with collection context,
   - `noise`: unstable, quality-sensitive, or unsupported by robustness checks.

### Qualitative Synthesis Rules

Declare your lane:
- `codebook_reliability` lane: predefined coding frame + inter-coder protocol + disagreement resolution.
- `reflexive_thematic` lane: reflexive rigor and transparent analytic decisions without forced reliability metrics.

Do not claim one lane's quality standards using the other lane's evidence structure.
---

### Draft: Anti-Pattern Warning Blocks

Add these warning blocks to make failure prevention executable.

---
### Warning: Hypothetical Intent Trap

**Looks like:** Core questions ask what participants would do in the future without anchoring to prior behavior.  
**Detection signal:** High stated intent but weak evidence of prior workaround, spending, or switching behavior.  
**Consequence:** False-positive demand and roadmap distortion.  
**Mitigation:** Rewrite as past-behavior prompts, add last-incident probing, and require behavior-linked evidence before making priority calls.

### Warning: Leading Question Contamination

**Looks like:** Questions include loaded framing, implied desirability, or embedded assumptions.  
**Detection signal:** Material response shift after neutral rewording in pilot or split-sample test.  
**Consequence:** Bias enters at measurement step and cannot be corrected later with analysis.  
**Mitigation:** Neutral wording pass, independent wording review, and mandatory pilot for high-stakes items.

### Warning: Agree/Disagree Acquiescence Bias

**Looks like:** Key constructs measured with agree/disagree statements only.  
**Detection signal:** Inflated agreement rates with weak discriminative variation across segments.  
**Consequence:** Overstated demand, urgency, or consensus.  
**Mitigation:** Use item-specific and balanced response formats; avoid acquiescence-prone batteries for primary decisions.

### Warning: Screener Leakage and Gaming

**Looks like:** Screener clearly telegraphs pass criteria; incentives are visible and high.  
**Detection signal:** Unusually high qualification rates, inconsistent profile answers, suspiciously homogeneous pass patterns.  
**Consequence:** Target-segment contamination and invalid findings.  
**Mitigation:** Hide qualification logic, add consistency checks, pre-register exclusion policy, and monitor qualification anomalies.

### Warning: Single-Check Quality Theater

**Looks like:** Team claims "data is clean" because one check (captcha/speed/IMC) passed.  
**Detection signal:** Contradictory quality indicators, unresolved anomaly spikes, or high exclusion swings when one extra check is applied.  
**Consequence:** False confidence and unstable conclusions.  
**Mitigation:** Use layered quality stack and sensitivity analysis before publishing findings.

### Warning: Subgroup Over-Interpretation

**Looks like:** One-wave opt-in subgroup outlier is treated as market truth.  
**Detection signal:** Result is non-replicated under stronger design, or highly sensitive to quality filters.  
**Consequence:** Mis-targeted strategy and reputational risk.  
**Mitigation:** Replicate with improved sampling/quality controls and downgrade claim confidence until replicated.

### Warning: Consent and Recording Gaps

**Looks like:** Consent copy is generic and does not specify recording, storage, reuse, or withdrawal process.  
**Detection signal:** Missing retention window, unclear sharing terms, no operational withdrawal path.  
**Consequence:** Ethical/legal exposure and potential data unusability.  
**Mitigation:** Use explicit consent protocol fields, include recording and retention policy text, and require withdrawal mechanism documentation.
---

### Draft: Governance and Consent Protocol

Add this section to enforce auditable ethics behavior.

---
### Consent, Privacy, and Governance

Before launching any interview or survey, you must finalize and store a consent protocol that includes:
- whether recording is required,
- what data is stored,
- where it is stored,
- who can access it,
- retention period,
- withdrawal mechanism and practical limits.

Consent must be understandable and specific to the actual data flow. Do not use generic one-line consent text for studies that involve recording, external integrations, or secondary analysis.

For AI-assisted synthesis:
- document where human oversight occurred,
- document any automated exclusion or coding assistance,
- retain an audit trace of major interpretation decisions.

If governance metadata is incomplete, mark evidence as `directional` and block `decision_grade` publication until remediated.
---

### Draft: Schema additions

```json
{
  "interview_instrument": {
    "type": "object",
    "required": [
      "study_id",
      "research_goal",
      "target_segment",
      "hypothesis_refs",
      "hypothesis_map",
      "interview_mode",
      "question_blocks",
      "bias_controls",
      "saturation_plan",
      "completion_criteria",
      "consent_protocol"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique identifier for this discovery study run."
      },
      "research_goal": {
        "type": "string",
        "description": "Primary decision-oriented objective of the interview study."
      },
      "target_segment": {
        "type": "string",
        "description": "Participant segment this instrument is intended to represent."
      },
      "hypothesis_refs": {
        "type": "array",
        "description": "Ordered list of hypothesis IDs referenced by question blocks.",
        "items": {
          "type": "string"
        }
      },
      "hypothesis_map": {
        "type": "array",
        "description": "Explicit mapping from each hypothesis to required evidence and disconfirmation criteria.",
        "items": {
          "type": "object",
          "required": [
            "hypothesis_id",
            "decision_ref",
            "evidence_needed",
            "disconfirming_signal",
            "priority"
          ],
          "additionalProperties": false,
          "properties": {
            "hypothesis_id": {
              "type": "string",
              "description": "Stable ID of the hypothesis being tested."
            },
            "decision_ref": {
              "type": "string",
              "description": "Decision this hypothesis can affect if validated or invalidated."
            },
            "evidence_needed": {
              "type": "string",
              "description": "What specific behavioral evidence is required to support this hypothesis."
            },
            "disconfirming_signal": {
              "type": "string",
              "description": "Observation that would count as falsifying this hypothesis."
            },
            "priority": {
              "type": "string",
              "enum": [
                "critical",
                "important",
                "nice_to_know"
              ],
              "description": "Importance level used for guide depth and synthesis emphasis."
            }
          }
        }
      },
      "interview_mode": {
        "type": "string",
        "enum": [
          "live_video",
          "live_audio",
          "async_text"
        ],
        "description": "Collection mode for this interview instrument."
      },
      "question_blocks": {
        "type": "array",
        "description": "Structured interview prompts mapped to evidence objectives.",
        "items": {
          "type": "object",
          "required": [
            "question_id",
            "question_text",
            "evidence_objective",
            "question_type",
            "hypothesis_id",
            "forbidden_patterns"
          ],
          "additionalProperties": false,
          "properties": {
            "question_id": {
              "type": "string",
              "description": "Unique question block identifier."
            },
            "question_text": {
              "type": "string",
              "description": "Exact participant-facing question text."
            },
            "evidence_objective": {
              "type": "string",
              "description": "What evidence this question should produce."
            },
            "question_type": {
              "type": "string",
              "enum": [
                "past_behavior",
                "timeline",
                "switch_trigger",
                "decision_criteria",
                "objection_probe"
              ],
              "description": "Question family used to enforce interview structure and analysis consistency."
            },
            "hypothesis_id": {
              "type": "string",
              "description": "Hypothesis this question is intended to validate or disconfirm."
            },
            "forbidden_patterns": {
              "type": "array",
              "description": "Leading or hypothetical patterns that must not appear in this block.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "saturation_plan": {
        "type": "object",
        "required": [
          "mode",
          "base_n",
          "run_length",
          "new_information_threshold",
          "heterogeneity_adjustment_rule"
        ],
        "additionalProperties": false,
        "properties": {
          "mode": {
            "type": "string",
            "enum": [
              "near_saturation",
              "true_saturation"
            ],
            "description": "Declared stopping model for interview collection."
          },
          "base_n": {
            "type": "integer",
            "minimum": 1,
            "description": "Initial interview count before novelty-rate stopping checks begin."
          },
          "run_length": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of most recent interviews considered in novelty-rate evaluation."
          },
          "new_information_threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Maximum acceptable share of newly emergent codes in run window before stopping."
          },
          "heterogeneity_adjustment_rule": {
            "type": "string",
            "description": "Rule describing how sample size increases for heterogeneous segments."
          }
        }
      },
      "consent_protocol": {
        "type": "object",
        "required": [
          "consent_required",
          "recording_policy",
          "retention_policy",
          "withdrawal_process"
        ],
        "additionalProperties": false,
        "properties": {
          "consent_required": {
            "type": "boolean",
            "description": "Whether explicit participant consent is required before collection."
          },
          "recording_policy": {
            "type": "string",
            "description": "Human-readable description of recording behavior and disclosure language."
          },
          "retention_policy": {
            "type": "string",
            "description": "Data retention window and deletion policy statement."
          },
          "withdrawal_process": {
            "type": "string",
            "description": "Operational procedure participants can use to withdraw data."
          }
        }
      }
    }
  },
  "survey_instrument": {
    "type": "object",
    "required": [
      "study_id",
      "survey_goal",
      "target_segment",
      "hypothesis_refs",
      "sample_plan",
      "questions",
      "quality_controls",
      "interpretation_guardrails",
      "evidence_grade_policy"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique identifier for this survey run."
      },
      "survey_goal": {
        "type": "string",
        "description": "Primary decision-oriented objective of the survey."
      },
      "target_segment": {
        "type": "string",
        "description": "Intended population segment for interpretation."
      },
      "hypothesis_refs": {
        "type": "array",
        "description": "Hypothesis IDs tested by this survey instrument.",
        "items": {
          "type": "string"
        }
      },
      "sample_plan": {
        "type": "object",
        "required": [
          "target_n",
          "min_n_per_segment",
          "sample_source_type"
        ],
        "additionalProperties": false,
        "properties": {
          "target_n": {
            "type": "integer",
            "minimum": 1,
            "description": "Target completed response count."
          },
          "min_n_per_segment": {
            "type": "integer",
            "minimum": 1,
            "description": "Minimum responses required per key segment."
          },
          "sample_source_type": {
            "type": "string",
            "enum": [
              "probability_panel",
              "nonprobability_opt_in",
              "customer_list",
              "mixed"
            ],
            "description": "Sampling source class used to determine inference limitations."
          }
        }
      },
      "questions": {
        "type": "array",
        "description": "Survey questions and response modalities.",
        "items": {
          "type": "object",
          "required": [
            "question_id",
            "question_text",
            "response_type"
          ],
          "additionalProperties": false,
          "properties": {
            "question_id": {
              "type": "string",
              "description": "Unique survey question identifier."
            },
            "question_text": {
              "type": "string",
              "description": "Exact participant-facing question wording."
            },
            "response_type": {
              "type": "string",
              "enum": [
                "single_select",
                "multi_select",
                "likert",
                "numeric",
                "free_text"
              ],
              "description": "Expected response format for this question."
            },
            "answer_scale": {
              "type": "string",
              "description": "Label for the response scale where applicable."
            }
          }
        }
      },
      "quality_controls": {
        "type": "array",
        "description": "List of layered quality-control rules used in this run.",
        "items": {
          "type": "string"
        }
      },
      "interpretation_guardrails": {
        "type": "object",
        "required": [
          "allow_moe_reporting",
          "subgroup_claim_policy",
          "replication_required_for_rare_claims"
        ],
        "additionalProperties": false,
        "properties": {
          "allow_moe_reporting": {
            "type": "boolean",
            "description": "Whether classical margin-of-error reporting is methodologically allowed for this sample design."
          },
          "subgroup_claim_policy": {
            "type": "string",
            "enum": [
              "strict",
              "moderate",
              "exploratory_only"
            ],
            "description": "How aggressively subgroup claims may be made from this dataset."
          },
          "replication_required_for_rare_claims": {
            "type": "boolean",
            "description": "Whether sensitive/rare prevalence claims require replication before publication."
          }
        }
      },
      "evidence_grade_policy": {
        "type": "object",
        "required": [
          "default_grade",
          "grade_upgrade_requirements"
        ],
        "additionalProperties": false,
        "properties": {
          "default_grade": {
            "type": "string",
            "enum": [
              "directional",
              "decision_grade"
            ],
            "description": "Default confidence class used for synthesis output."
          },
          "grade_upgrade_requirements": {
            "type": "array",
            "description": "Conditions required to upgrade directional output to decision-grade.",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Qualtrics support documentation clearly describes the 3-step export workflow, but public page structures for exact v3 endpoint paths are inconsistent across docs; connector method IDs in this skill were treated as canonical integration surface.
- Tool pricing and feature-gating details (especially enterprise contracts) vary by tenant and are not consistently public; research focused on documented API capabilities and limits.
- Some practitioner sources (blogs, platform reports) are operationally useful but not peer-reviewed; they were used for workflow tuning, not as sole evidence for high-stakes statistical claims.
- No single universal threshold exists for inattentive/fraud exclusion. Recommended thresholds are explicitly context-dependent and should be piloted per study design.
- This pass did not include a dedicated legal review by jurisdiction (for example, country-specific recording consent statutes). Governance recommendations are process-level and should be paired with local legal policy when needed.
