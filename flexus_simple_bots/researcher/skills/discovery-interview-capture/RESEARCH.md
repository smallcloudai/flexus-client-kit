# Research: discovery-interview-capture

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/discovery-interview-capture/`  
**Bot:** researcher  
**Research date:** 2026-03-05  
**Status:** complete

---

## Context

This skill captures interview transcripts and converts them into JTBD-coded, quote-traceable artifacts. It is a foundational quality point: if coding or evidence traceability is weak here, downstream research synthesis and decision support become unreliable.

The key improvement need is operational rigor. Research from 2024-2026 shows that teams fail less on "framework choice" and more on missing process gates: transcript QA, explicit stop rules, consent scope tracking, and recommendation-to-evidence traceability.

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

- No generic filler: every major claim has concrete operational implication and source.
- No invented API endpoint or method IDs: only verified public operations are listed.
- Contradictions are explicitly documented, not silently resolved.
- Findings depth is substantial and `Draft Content for SKILL.md` is the largest section.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

- **JTBD capture works best as a decision timeline, not opinion sampling.**  
  2025 practitioner guidance emphasizes reconstructing behavior sequence: struggle -> workaround/alternatives -> trigger -> decision criteria -> objection. This maps directly to your existing event taxonomy and should be encoded as mandatory coding order.

- **Decision recency affects recall quality.**  
  Recent practice guidance suggests better signal in nearer decision windows; older memories are still usable but should carry explicit recall-risk metadata and confidence downgrades.

- **AI-moderated interviews are useful for structured collection, weaker for deep semistructured probing.**  
  2026 NN/g findings support constrained use (screeners, standardized blocks) but not full replacement in exploratory discovery.

- **AI thematic coding dramatically improves speed but still needs human adjudication for nuance.**  
  2024 comparative studies report partial overlap with human coding, but not parity in all contexts; production-safe pattern remains AI first-pass + human review.

- **Coding governance is a top quality control.**  
  2025 coding-practice guidance emphasizes pilot coding, reconciliation loops, and codebook version traceability as practical reliability controls.

**Sources:**
- https://commoncog.com/putting-jtbd-interview-to-practice/ (2025)  
- https://june.so/blog/how-to-run-a-jtbd-interview-like-the-co-creator-of-the-framework (2025)  
- https://www.nngroup.com/articles/ai-interviewers/ (2026)  
- https://ai.jmir.org/2024/1/e54482 (2024)  
- https://doi.org/10.1017/rsm.2025.10019 (2025)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- **Zoom**: public docs verify recording retrieval and S2S OAuth flows; rate limits are endpoint-classed and plan-dependent.  
- **Fireflies**: GraphQL-native transcript retrieval (`transcript`, `transcripts`) with documented auth and limits.  
- **Dovetail**: import + markdown/html export endpoints support transcript workflows; 429 handling documented.  
- **Gong**: open docs strongly support ingest/OAuth and endpoint change notices; transcript retrieval endpoint naming may require tenant-verified docs.  
- **Fathom**: adjacent option with transcript and webhook endpoints.

**Verified endpoint/method matrix:**

| Tool | Verified operation | Purpose |
|---|---|---|
| Zoom | `GET /users/{userId}/recordings` | List recordings |
| Zoom | `GET /meetings/{meetingId}/recordings` | Recording files metadata |
| Zoom | `POST https://zoom.us/oauth/token?grant_type=account_credentials&account_id=...` | S2S OAuth token |
| Gong | `GET /v2/users` | User lookup |
| Gong | `POST /v2/calls` | Create call |
| Gong | `PUT /v2/calls/{callId}/media` | Upload media |
| Gong | `POST /v2/calls/extensive` | Extensive payload endpoint |
| Fireflies | `POST https://api.fireflies.ai/graphql` | GraphQL root |
| Fireflies | `query transcript(id: ...)` | Transcript fetch |
| Fireflies | `query transcripts(...)` | Transcript list/search |
| Dovetail | `POST /v1/notes/import/file` | File/media import |
| Dovetail | `GET /v1/notes/{note_id}/export/{type}` | Note export |
| Dovetail | `GET /v1/insights/{insight_id}/export/{type}` | Insight export |
| Fathom | `GET /recordings/{recording_id}/transcript` | Transcript retrieval |

**Contradictions / uncertainties:**

- Gong transcript retrieval specifics are not uniformly visible in fully open docs; avoid hardcoded pseudo methods until tenant docs confirm names.
- Some vendor docs are active but date-less at operation granularity; verify at implementation time.

**Sources:**
- https://developers.zoom.us/docs/api/meetings/ (2026 active)  
- https://developers.zoom.us/docs/api/rate-limits/ (2026 active)  
- https://developers.zoom.us/docs/internal-apps/s2s-oauth/ (2026 active)  
- https://help.gong.io/docs/uploading-calls-from-a-non-integrated-telephony-system (2024)  
- https://help.gong.io/docs/create-an-app-for-gong (2026)  
- https://help.gong.io/docs/public-api-change-deprecating-call-action-items-in-the-extensive-endpoint (2025)  
- https://docs.fireflies.ai/fundamentals/authorization (active)  
- https://docs.fireflies.ai/graphql-api/query/transcript (active)  
- https://developers.dovetail.com/reference/post_v1-notes-import-file (active)  
- https://developers.fathom.ai/api-reference/recordings/get-transcript (active)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- **Near vs true saturation difference matters in operational planning.**  
  2024 empirical work shows high recurring-signal coverage can arrive before full code closure; this supports explicit wave tracking instead of fixed N-only stop rules.

- **Evergreen saturation mechanics are still practical.**  
  The PLOS method (base size, run length, threshold) remains a useful, auditable scaffold and should be marked Evergreen in `SKILL.md`.

- **Reliability claims need protocol context.**  
  Agreement metrics without coding design, prevalence context, and reconciliation rules are weak evidence.

- **CERQual-style confidence framing avoids fake precision.**  
  Assign confidence per finding using methodological limitations, coherence, adequacy, and relevance.

- **Quote-level traceability remains core quality requirement.**  
  Evergreen reporting standards (COREQ/SRQR) still align with modern evidence-quality expectations.

- **AI-assisted coding requires verification controls.**  
  2024-2025 work supports hybrid workflows; hallucination/over-abstraction risk means quote mapping and human review remain mandatory.

**Recommended decision rules:**

1. Continue sampling/coding when wave novelty is above threshold.
2. Mark operational saturation only after threshold is met across consecutive waves and contradictions are stable.
3. Hold synthesis when high-impact code reliability is unresolved.
4. Exclude decision-facing claims that cannot map to quote-level evidence.
5. Reject AI-generated codes without exact transcript-span support.

**Sources:**
- https://doi.org/10.2196/52998 (2024)  
- https://doi.org/10.1177/16094069241229777 (2024)  
- https://doi.org/10.1371/journal.pone.0232076 (2020, Evergreen)  
- https://doi.org/10.29333/ajqr/14887 (2024)  
- https://www.cerqual.org/official-guidance-for-applying-grade-cerqual/ (active)  
- https://www.equator-network.org/reporting-guidelines/coreq/ (2007, Evergreen)  
- https://www.equator-network.org/reporting-guidelines/srqr/ (2014, Evergreen)  
- https://doi.org/10.18653/v1/2025.acl-long.71 (2025)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Leading-question contamination**  
  Detection: findings change when prompts are neutralized.  
  Consequence: biased theme prevalence and weak transferability.  
  Mitigation: neutral prompt templates, wording pilot runs, downgrade wording-sensitive claims.

- **Consent scope mismatch**  
  Detection: recording consent exists, transcription/AI scope absent.  
  Consequence: governance risk and evidence invalidation risk.  
  Mitigation: mandatory scope fields + block before processing.

- **Transcript-as-truth behavior**  
  Detection: no transcript QA/corrections log before coding.  
  Consequence: silent quote errors and attribution drift.  
  Mitigation: required QA state + correction manifest.

- **False saturation assertions**  
  Detection: no novelty-wave records or stop criteria.  
  Consequence: premature stop and missed high-impact themes.  
  Mitigation: predeclared threshold + wave logs + contradiction checks.

- **Unsupported synthesis**  
  Detection: recommendation cannot map to code and quote references.  
  Consequence: non-auditable output.  
  Mitigation: recommendation-to-evidence chain checker.

**Bad vs good examples:**

- Bad: "Users dislike reporting."  
  Good: "11 quote-backed struggle events across 8 interviews indicate recurring reporting friction; one disconfirming subgroup noted."

- Bad: "Saturation reached at 8 interviews."  
  Good: "Operational saturation met at <=5% new-code ratio for two consecutive waves; unresolved contradictions listed."

**Sources:**
- https://doi.org/10.1007/s11135-024-01934-6 (2024)  
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12048736/ (2024)  
- https://doi.org/10.29333/ajqr/14887 (2024)  
- https://doi.org/10.1177/16094069241229777 (2024)  
- https://doi.org/10.1007/s11135-024-02022-5 (2024)

---

### Angle 5+: Privacy, Consent, and Governance Controls
> Domain-specific addition: operational governance requirements for transcript workflows.

**Findings:**

- Consent evidence should be auditable (`who/when/how/what scope`) and revocable in process.
- Data minimization and storage limitation should be encoded as workflow fields/gates, not policy-only text.
- Vendor/processor and cross-border transfer controls are practical blockers for production workflows.
- Retention/deletion failures are often procedural; artifacts need lifecycle status and deletion evidence refs.
- NIST GenAI profile and regulator updates support traceability-focused process controls.

**Sources:**
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/how-should-we-obtain-record-and-manage-consent (active)  
- https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/ (active)  
- https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2026/01/updated-guidance-on-international-transfers-published/ (2026)  
- https://www.edpb.europa.eu/news/news/2026/edpb-identifies-challenges-hindering-full-implementation-right-erasure_en (2026)  
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence (2024)  
- https://www.cnil.fr/en/sheet-ndeg14-define-data-retention-period (2020, Evergreen)

---

## Synthesis

The strongest cross-angle conclusion is that this skill should behave like a gated evidence system, not a summarization pipeline. Quality comes from process discipline: preflight consent checks, transcript QA, quote-level coding traceability, saturation logs, and explicit confidence rationale.

Tool/API landscape is usable but uneven. Several providers expose stable transcript workflows publicly; however, uncertain endpoint surfaces (notably Gong transcript retrieval naming in open docs) should be handled by runtime verification rather than static pseudo method IDs.

AI can accelerate capture and coding, but reliability and hallucination risk mean this skill must remain human-adjudicated for decision-grade artifacts. The right policy is "AI propose, human verify, evidence chain enforce."

Governance and methodology are tightly coupled: missing consent scope, retention ambiguity, or transfer uncertainty is not only compliance risk but also evidence-trust risk. Schema and process gates should reflect that coupling directly.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Be specific: "Add X to methodology", "Replace Y tool with Z", "Add anti-pattern: ...", "Schema field X should be enum [...]".
> Each item here must have a corresponding draft in the section below.

- [x] Replace pseudo method IDs with verified endpoint syntax or runtime mapping checks.
- [x] Add mandatory preflight gate (consent scope, jurisdiction, retrieval readiness, retention class).
- [x] Add transcript QA + correction manifest gate before coding.
- [x] Add AI-boundary policy (draft assist allowed, human adjudication required).
- [x] Add wave-based saturation protocol with explicit stop criteria.
- [x] Add reliability and disagreement-resolution protocol.
- [x] Add CERQual-style confidence assignment policy.
- [x] Add named anti-pattern warning blocks with detection and mitigation.
- [x] Expand schema with traceability, governance, and retrieval manifest fields.
- [x] Add recommendation-to-evidence chain enforcement logic.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the **actual text** that should go into SKILL.md — as if you were writing it. Be verbose and comprehensive. The future editor will cut what they don't need; they should never need to invent content from scratch.
>
> Rules:
> - Write full paragraphs and bullet lists, not summaries
> - For methodology changes: write the actual instruction text in second person ("You should...", "Before doing X, always verify Y")
> - For schema changes: write the full JSON fragment with all fields, types, descriptions, enums, and `additionalProperties: false`
> - For anti-patterns: write the complete warning block including detection signal and mitigation steps
> - For tool recommendations: write the actual `## Available Tools` section text with real method syntax
> - Do not hedge or abbreviate — if a concept needs 3 paragraphs to explain properly, write 3 paragraphs
> - Mark sections with `### Draft: <topic>` headers so the editor can navigate

### Draft: Core operating contract

---
You capture interview evidence for decision-quality research. Your core output is an auditable evidence corpus, not a high-level summary.

For every coded event, you must preserve a complete evidence tuple:
1. quote text,
2. speaker reference,
3. time reference (timestamp or turn index),
4. transcript reference,
5. coder/reviewer reference.

Hard rule: **No quote-linked evidence -> no coded event. No coded event -> no decision-facing claim.**

If quality controls fail (consent, transcript integrity, unresolved contradictions), you must downgrade coverage status and produce explicit remediation tasks rather than filling gaps with inferred confidence.
---

### Draft: Preflight gate

---
### Preflight and consent gate (mandatory)

Before retrieval or coding, run preflight checks:

1. **Consent scope check**  
   Verify scope fields include recording, transcription, AI-assist (if used), quote reuse, and transfer handling.

2. **Jurisdiction and policy check**  
   Capture participant/interviewer jurisdiction context and confirm policy path. If uncertain, mark blocked and escalate.

3. **Retrieval readiness check**  
   Confirm source provider and source IDs are available and connector can produce traceability fields.

4. **Retention class check**  
   Assign artifact lifecycle class and review/delete checkpoint before ingest.

5. **Processor stack check**  
   Record all platforms/services that will process transcript artifacts.

If any preflight field is missing, stop processing and write a blocked record with required remediation.
---

### Draft: Retrieval + QA section

---
### Transcript retrieval and QA

Retrieve transcript artifacts using verified API operations only.

Workflow:
1. Resolve provider and source identifier.
2. Retrieve transcript + metadata.
3. Validate transcript quality:
   - structural completeness,
   - speaker fields present,
   - time reference present,
   - encoding/corruption check.
4. Record all normalization actions in `transcript_corrections`.
5. Set `qa_status` to `pass`, `pass_with_warnings`, or `fail`.

Only `pass` and `pass_with_warnings` proceed to coding.  
`fail` must be excluded from coded corpus with explicit reason.
---

### Draft: Available tools section

---
## Available Tools

Use only verified operations. If runtime wrapper methods are required, map them to verified operations at execution time and fail closed if mapping is unavailable.

### Zoom

```bash
GET /users/{userId}/recordings?from=YYYY-MM-DD&to=YYYY-MM-DD
Authorization: Bearer <access_token>
```

```bash
GET /meetings/{meetingId}/recordings
Authorization: Bearer <access_token>
```

```bash
POST https://zoom.us/oauth/token?grant_type=account_credentials&account_id=<account_id>
Authorization: Basic <base64(client_id:client_secret)>
```

### Gong

```bash
GET /v2/users
POST /v2/calls
PUT /v2/calls/{callId}/media
POST /v2/calls/extensive
```

Only use transcript retrieval operation names that are verified in current tenant docs.

### Fireflies

```bash
POST https://api.fireflies.ai/graphql
Authorization: Bearer <api_key>
Content-Type: application/json
```

```graphql
query TranscriptById($id: String!) {
  transcript(id: $id) {
    id
    title
    dateString
    sentences { text speaker_name start_time }
  }
}
```

### Dovetail

```bash
POST /v1/notes/import/file
GET /v1/notes/{note_id}/export/markdown
GET /v1/insights/{insight_id}/export/markdown
Authorization: Bearer <api_token>
```

### Fathom (adjacent)

```bash
GET /recordings/{recording_id}/transcript
Authorization: Bearer <api_key>
```

Retry policy:
- Backoff on 429/5xx,
- track retries,
- log final retrieval status into manifest.
---

### Draft: JTBD coding workflow

---
### JTBD coding workflow

Use this event taxonomy:
- `struggle`
- `workaround`
- `trigger`
- `decision_criteria`
- `objection`

Coding steps:
1. Build participant timeline from transcript.
2. Extract candidate events from behavior-grounded statements.
3. Attach quote/speaker/time/transcript refs.
4. Assign `evidence_strength` (`weak`, `moderate`, `strong`).
5. Record contradictions and disconfirming evidence.
6. Run reviewer verification before final artifact write.

AI-assist policy:
- AI can propose candidate events and summaries.
- Human reviewer must verify source mapping for every retained event.
- AI-generated content without exact source mapping is excluded from final artifacts.
---

### Draft: Saturation and reliability

---
### Saturation protocol

Do not use fixed interview count as sole stop rule.

Define:
- `saturation_base_size`
- `saturation_run_length`
- `saturation_threshold`

Default operational values:
- base size: 6
- run length: 3
- threshold: 0.05

Decision rules:
1. If wave novelty > threshold, continue.
2. If wave novelty <= threshold for two consecutive waves and contradiction trend stabilizes, mark operational saturation.
3. If unresolved high-impact contradictions remain, continue targeted sampling.

### Reliability protocol

- Predefine calibration and disagreement resolution approach.
- Log disagreement on high-impact codes and reconcile before synthesis.
- Do not over-claim certainty from single metric in sparse-code contexts.
---

### Draft: Confidence policy

---
### Confidence assignment

Assign confidence per finding using:
1. methodological limitations,
2. coherence,
3. adequacy,
4. relevance.

Allowed labels:
- `high`
- `moderate`
- `low`
- `very_low`

Downgrade when:
- claim lacks quote traceability,
- evidence relies primarily on weak events,
- contradiction unresolved in key segment,
- AI-generated interpretation lacks human verification.
---

### Draft: Anti-pattern warning blocks

---
### Warning: Leading-question contamination
- **Detection:** finding direction changes under neutral rephrasing.
- **Consequence:** inflated/biased theme prevalence.
- **Mitigation:** neutral stems, prompt piloting, confidence downgrade.

### Warning: Consent scope mismatch
- **Detection:** recording consent present, transcription/AI scope missing.
- **Consequence:** governance failure; evidence may be excluded.
- **Mitigation:** block processing until scope-complete consent captured.

### Warning: Transcript-as-truth
- **Detection:** no `qa_status` and no correction manifest.
- **Consequence:** quote errors and attribution drift.
- **Mitigation:** mandatory QA gate before coding.

### Warning: False saturation
- **Detection:** no novelty-wave data and no explicit stop criteria.
- **Consequence:** premature stop, missed themes.
- **Mitigation:** wave-based threshold tracking + contradiction checks.

### Warning: Unsupported synthesis
- **Detection:** recommendation cannot be mapped to quote chain.
- **Consequence:** non-auditable strategy output.
- **Mitigation:** enforce recommendation-to-evidence chain checker.
---

### Draft: Schema additions

```json
{
  "interview_record_extensions": {
    "type": "object",
    "required": [
      "qa_status",
      "decision_recency_bucket",
      "eligibility_status",
      "consent",
      "transcript_corrections"
    ],
    "additionalProperties": false,
    "properties": {
      "qa_status": {
        "type": "string",
        "enum": ["pass", "pass_with_warnings", "fail"],
        "description": "Transcript quality gate outcome."
      },
      "decision_recency_bucket": {
        "type": "string",
        "enum": ["0_6_months", "7_18_months", "over_18_months", "not_applicable"],
        "description": "Recency of decision context for recall-risk handling."
      },
      "eligibility_status": {
        "type": "string",
        "enum": ["included", "excluded", "included_with_limitations"],
        "description": "Whether interview is valid for coding."
      },
      "transcript_corrections": {
        "type": "array",
        "description": "Corrections applied before coding.",
        "items": {
          "type": "object",
          "required": ["field", "reason", "editor_ref"],
          "additionalProperties": false,
          "properties": {
            "field": {
              "type": "string",
              "description": "Corrected field/segment."
            },
            "reason": {
              "type": "string",
              "description": "Why correction was required."
            },
            "editor_ref": {
              "type": "string",
              "description": "Who made the correction."
            }
          }
        }
      },
      "consent": {
        "type": "object",
        "required": ["notice_version", "consent_timestamp_utc", "consent_method", "scope", "withdrawal_status"],
        "additionalProperties": false,
        "properties": {
          "notice_version": {
            "type": "string",
            "description": "Version ID of disclosure/notice shown."
          },
          "consent_timestamp_utc": {
            "type": "string",
            "description": "UTC timestamp of captured consent."
          },
          "consent_method": {
            "type": "string",
            "enum": ["written", "oral_recorded", "platform_clickthrough"],
            "description": "How consent was collected."
          },
          "scope": {
            "type": "object",
            "required": ["recording", "transcription", "ai_summary", "quote_reuse", "cross_border_transfer"],
            "additionalProperties": false,
            "properties": {
              "recording": {
                "type": "boolean",
                "description": "Permission to record interview."
              },
              "transcription": {
                "type": "boolean",
                "description": "Permission to transcribe recording."
              },
              "ai_summary": {
                "type": "boolean",
                "description": "Permission for AI-assisted summarization/coding."
              },
              "quote_reuse": {
                "type": "boolean",
                "description": "Permission to reuse quotes in outputs."
              },
              "cross_border_transfer": {
                "type": "boolean",
                "description": "Permission/eligibility for cross-border processing."
              }
            }
          },
          "withdrawal_status": {
            "type": "string",
            "enum": ["active", "withdrawn", "partial_withdrawal"],
            "description": "Current consent state."
          }
        }
      }
    }
  },
  "study_level_extensions": {
    "type": "object",
    "required": ["saturation_tracking", "retrieval_manifest", "governance"],
    "additionalProperties": false,
    "properties": {
      "saturation_tracking": {
        "type": "object",
        "required": ["base_size", "run_length", "threshold", "waves", "status"],
        "additionalProperties": false,
        "properties": {
          "base_size": {
            "type": "integer",
            "minimum": 1,
            "description": "Initial count before first saturation check."
          },
          "run_length": {
            "type": "integer",
            "minimum": 1,
            "description": "Interviews added per saturation wave."
          },
          "threshold": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "New-code ratio threshold for operational saturation."
          },
          "waves": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["wave_id", "interview_count", "new_code_ratio"],
              "additionalProperties": false,
              "properties": {
                "wave_id": {
                  "type": "string",
                  "description": "Wave identifier."
                },
                "interview_count": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Total interviews covered in wave."
                },
                "new_code_ratio": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1,
                  "description": "Proportion of newly observed codes."
                },
                "notes": {
                  "type": "string",
                  "description": "Contradictions and interpretation notes."
                }
              }
            }
          },
          "status": {
            "type": "string",
            "enum": ["not_started", "in_progress", "operationally_saturated", "continue_sampling"],
            "description": "Current saturation state."
          }
        }
      },
      "retrieval_manifest": {
        "type": "array",
        "description": "Provider retrieval operation logs.",
        "items": {
          "type": "object",
          "required": ["interview_id", "provider", "operation", "status", "retrieved_at_utc"],
          "additionalProperties": false,
          "properties": {
            "interview_id": {
              "type": "string",
              "description": "Interview identifier."
            },
            "provider": {
              "type": "string",
              "enum": ["zoom", "gong", "fireflies", "dovetail", "fathom", "other"],
              "description": "Source provider."
            },
            "operation": {
              "type": "string",
              "description": "Endpoint/query/export operation used."
            },
            "status": {
              "type": "string",
              "enum": ["success", "partial", "failed"],
              "description": "Final retrieval status."
            },
            "retry_count": {
              "type": "integer",
              "minimum": 0,
              "description": "Retries performed."
            },
            "retrieved_at_utc": {
              "type": "string",
              "description": "UTC timestamp of final attempt."
            }
          }
        }
      },
      "governance": {
        "type": "object",
        "required": ["retention_policy_id", "transfer_assessment_status", "deletion_evidence_refs"],
        "additionalProperties": false,
        "properties": {
          "retention_policy_id": {
            "type": "string",
            "description": "Retention policy identifier."
          },
          "transfer_assessment_status": {
            "type": "string",
            "enum": ["not_needed", "pending", "approved", "blocked"],
            "description": "Cross-border transfer assessment state."
          },
          "deletion_evidence_refs": {
            "type": "array",
            "description": "Evidence references for deletion/retention tasks.",
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

### Draft: Recommendation chain enforcement

---
Before writing final `jtbd_outcomes`, validate:

`recommendation -> finding -> coded_event -> quote -> transcript_ref`

If any link is missing:
1. set recommendation status to `unsupported`,
2. exclude from decision-facing output,
3. append required validation action to `next_checks`.

Do not collapse unresolved contradictions into high-confidence guidance.
---

---

## Gaps & Uncertainties

- Gong transcript retrieval operation names need tenant-level verification before hardcoding.
- Some active vendor docs do not provide operation-level publication dates; implementation-time validation is still required.
- Saturation thresholds are context dependent; defaults here are operational starting points, not universal constants.
- Consent/recording law requirements vary by jurisdiction; skill should enforce blockers and escalation, not legal conclusions.
- AI coding quality depends on model/version/prompt stack and domain language; periodic recalibration remains necessary.
