# Research: discovery-context-import

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/discovery-context-import/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`discovery-context-import` imports prior customer evidence from CRM, support, and conversation systems to accelerate discovery before new interviews and surveys are designed. It is explicitly a seeding step, not a substitute for fresh qualitative work.

The current skill already encodes core intent (pull notes/calls/tickets/conversations, include Dovetail insights, and anonymize PII), but it needs stronger 2024-2026 grounding in five areas: import methodology, tool landscape, API endpoint reality, interpretation guardrails, and failure/compliance controls.

This research focuses on practical operations: how teams scope imports, prevent bias amplification, verify endpoint behavior, interpret noisy support/sales signals, and avoid compliance failures while still shipping useful context artifacts quickly.

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
- Volume: findings section should be 800-4000 words (too short = shallow, too long = unsynthesized)

Quality gate result: passed.

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. Effective context import starts with bounded scope, not full-history dumps. Current Dovetail integration workflows expose explicit source/time controls (for example 7/30/90 day windows and source selection), and support integrations require explicit backfill ranges. This pattern reduces early noise and gives faster relevance.

2. Teams that avoid identity fragmentation define import keys before first run. Dovetail/Salesforce mapping patterns and participant import guidance in adjacent tooling emphasize choosing one stable unique identifier and deterministic merge behavior.

3. Field minimization is now a repeated practice in modern data-platform guidance: start with the highest-value fields first, then expand. A Salesforce 2025 customer-zero lesson explicitly recommends prioritizing a constrained high-value field set.

4. Bias control begins in source selection, not at synthesis time. Product-discovery guidance warns against convenience pools (e.g., only vocal power users or only active complainers), and recommends aligning recruited evidence to learning goals plus freshness/rotation controls.

5. Segment and trend checks should happen before drafting interview instruments. HubSpot list/segment analytics now supports practical short-window anomaly inspection and segment comparisons that can reveal sudden composition drift before the next discovery wave.

6. Support evidence triage in practice uses severity ladders, not pure mention counts. Freshdesk SLA policy mechanics (priority classes, response timers, escalation cadence) provide a practical framework for ordering imported support themes by likely business urgency.

7. Theme coding quality improves when teams operate an explicit taxonomy governance loop. Dovetail guidance in 2024 stresses short, specific tags, periodic review, and anti-bloat checks (very high-count tags often too broad; very low-count tags often too fragmented).

8. Coding reliability cannot be deferred to “later analyst judgment.” 2024 guidance on inter-coder agreement stresses predeclared agreement metrics, reconciliation rules, and audit trails for codebook changes.

9. Stopping import should be novelty-based, not arbitrary-date based. 2024 saturation work supports a handoff rule: when added imported incidents are increasing volume but no longer changing thematic direction, switch effort to targeted interviews that resolve mechanism and causality.

10. AI-assisted triage improves only when goals are constrained. Current support-ticket analysis playbooks require objective framing (top goals first); unconstrained summarization tends to create diffuse, less-actionable themes.

**Sources:**
- https://docs.dovetail.com/integrations/gong.md (current docs, accessed 2026)
- https://docs.dovetail.com/integrations/zendesk.md (current docs, accessed 2026)
- https://docs.dovetail.com/integrations/intercom.md (current docs, accessed 2026)
- https://docs.dovetail.com/integrations/salesforce.md (current docs, accessed 2026)
- https://support.aha.io/aha-discovery/getting-started/imports/import-participants (current docs, accessed 2026)
- https://www.salesforce.com/ap/blog/3-lessons-from-using-data-cloud/ (2025)
- https://aha.io/roadmapping/guide/discovery/how-to-build-a-customer-database-for-product-discovery (updated 2025)
- https://aha.io/roadmapping/guide/how-to-choose-the-right-customers-for-product-discovery-interviews (updated 2025)
- https://knowledge.hubspot.com/analyze-segments (updated 2025)
- https://knowledge.hubspot.com/lists/analyze-your-list-performance (updated 2026)
- https://support.freshdesk.com/support/solutions/articles/37626-understanding-sla-policies (2025/2026 policy context)
- https://dovetail.com/blog/four-taxonomy-best-practices/ (2024)
- https://docs.dovetail.com/academy/craft-your-team-taxonomy/ (current docs, accessed 2026)
- https://www.ajqr.org/article/inter-coder-agreement-in-qualitative-coding-considerations-for-its-use-14887 (2024)
- https://research.uca.ac.uk/6262/1/naeem-et-al-2024-demystification-and-actualisation-of-data-saturation-in-qualitative-research-through-thematic-analysis.pdf (2024)
- https://api.crossref.org/works/10.1177/16094069241296206 (2024 metadata)
- https://docs.dovetail.com/academy/analyze-support-tickets.md (current docs, accessed 2026)

---

### Angle 2: Tool & Platform Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. HubSpot and Salesforce remain common CRM sources but differ operationally: HubSpot emphasizes explicit burst/day quotas by app model and tier, while Salesforce frames API allocation via daily/monthly entitlement posture with monitoring and add-on patterns.

2. HubSpot export workflows in 2025-2026 are batch-governed (single active export, rolling export windows, partition behavior for very large jobs), which favors controlled backfills over repeated giant full refreshes.

3. Salesforce integration guidance in 2024-2026 pushes event-first architectures (Platform Events / CDC / Pub/Sub API) for near-real-time coherence across systems.

4. Zendesk is strong for support evidence backfills via incremental exports plus search/audit/comment endpoints, but import throughput must respect account and endpoint-level limits.

5. Intercom is strong for conversation metadata and thread retrieval, but webhook delivery is not a strict ordered stream; practical consumers must handle duplicates, retries, and pause/suspension behavior.

6. Freshdesk provides robust ticket/conversation access but enforces plan-tier and per-minute/per-endpoint limits; some embedded expansion patterns can consume extra API credits.

7. Jira Service Management is a strong support context source for request/comment/participant/attachment evidence, but visibility and rate-limit policy is role/auth-model sensitive.

8. Dovetail is a natural research sink for imported evidence; it supports multiple inbound connectors and API-level note/highlight/insight operations, making it useful for synthesis handoff.

9. Gong remains conversation-intelligence relevant through transcript workflows and outbound automation/webhook rules, but entitlements and feature availability should be validated by tenant/plan.

10. The de-facto production pattern is hybrid push+pull: webhooks for freshness, plus scheduled search/export/incremental replay for completeness and reconciliation. Pure webhook-only pipelines are fragile for this use case.

11. Chorus/ZoomInfo public documentation is more integration-led than deeply endpoint-led for call intelligence in available public materials; teams should validate tenant-level API access before hard dependencies.

**Sources:**
- https://developers.hubspot.com/docs/api/usage-details (current docs, accessed 2026)
- https://developers.hubspot.com/changelog/increasing-our-api-limits (2024)
- https://developers.hubspot.com/docs/reference/api/crm/exports (current docs, accessed 2026)
- https://developers.hubspot.com/changelog/crm-export-partitioning-and-association-limits (2025)
- https://developer.salesforce.com/blogs/2024/11/api-limits-and-monitoring-your-api-usage (2024)
- https://developer.salesforce.com/docs/platform/pub-sub-api/guide/intro.html (current docs, accessed 2026)
- https://architect.salesforce.com/docs/architect/decision-guides/guide/event-driven (2025 context)
- https://developer.zendesk.com/api-reference/introduction/rate-limits (current docs, accessed 2026)
- https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/ (current docs, accessed 2026)
- https://developers.intercom.com/docs/references/rest-api/errors/rate-limiting (current docs, accessed 2026)
- https://developers.intercom.com/docs/webhooks/webhook-notifications (current docs, accessed 2026)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/conversations (current docs, accessed 2026)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/conversations/searchconversations (current docs, accessed 2026)
- https://support.freshdesk.com/support/solutions/articles/225439-what-are-the-rate-limits-for-the-api-calls-to-freshdesk- (2025/2026 context)
- https://developers.freshdesk.com/api/ (current docs, accessed 2026)
- https://support.freshdesk.com/support/solutions/articles/132589-using-webhooks-in-automation-rules (current docs, accessed 2026)
- https://developer.atlassian.com/cloud/jira/platform/rate-limiting/ (2026)
- https://developer.atlassian.com/cloud/jira/platform/webhooks/ (current docs, accessed 2026)
- https://support.atlassian.com/jira-cloud-administration/docs/manage-webhooks/ (current docs, accessed 2026)
- https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-request/ (current docs, accessed 2026)
- https://docs.dovetail.com/integrations/intercom (current docs, accessed 2026)
- https://dovetail.com/help/integrations/zendesk/ (current docs, accessed 2026)
- https://dovetail.com/help/integrations/hubspot/ (current docs, accessed 2026)
- https://developers.dovetail.com/docs (current docs, accessed 2026)
- https://developers.dovetail.com/reference/post_v1-notes-import-file (current docs, accessed 2026)
- https://developers.dovetail.com/reference/get_v1-notes (current docs, accessed 2026)
- https://help.gong.io/docs/introduction-to-automation-rules (current docs, accessed 2026)
- https://help.gong.io/docs/create-a-webhook-rule (current docs, accessed 2026)
- https://help.gong.io/docs/view-a-call-transcript (current docs, accessed 2026)
- https://docs.zoominfo.com/ (current docs, accessed 2026)
- https://docs.zoominfo.com/docs/general-overview (current docs, accessed 2026)
- https://www.zoominfo.com/about/get-started-old/chorus-integrations (current docs, accessed 2026)

---

### Angle 3: API Endpoint Reality & Integration Constraints
> What are the verified endpoint-level operations and constraints for context import APIs?

**Findings:**

1. HubSpot contact search endpoint is verified: `POST /crm/v3/objects/contacts/search`, with filter groups and cursor pagination (`after`), max page size 200.

2. HubSpot note/call listing endpoints are verified: `GET /crm/v3/objects/notes` and `GET /crm/v3/objects/calls`.

3. HubSpot search endpoints for evidence-bearing objects are verified: `POST /crm/v3/objects/notes/search`, `POST /crm/v3/objects/calls/search`, `POST /crm/v3/objects/tickets/search`. Search has practical limits including result ceilings and request pacing.

4. HubSpot OAuth v3 endpoints were introduced in 2026: `POST /v3/token` and `POST /v3/introspect`, with v1 deprecation context. This is a real auth migration consideration.

5. Zendesk incremental ticket-event endpoint is verified: `GET /api/v2/incremental/ticket_events?start_time={unix}&include=comment_events`. This remains core for historical support context replay.

6. Zendesk ticket-history endpoints are verified: `GET /api/v2/tickets/{ticket_id}/audits` and `GET /api/v2/tickets/{ticket_id}/comments`.

7. Zendesk unified search endpoint is verified: `GET /api/v2/search?query={query}` with result caps and pagination constraints.

8. Zendesk export-style search endpoint is verified: `GET /api/v2/search/export?query={query}&filter[type]=ticket`; cursor expiry handling is required.

9. Intercom conversation endpoints are verified: `GET /conversations`, `GET /conversations/{id}`, `POST /conversations/search`, with explicit pagination and query-complexity constraints.

10. Intercom contact and ticket search operations are verified: `POST /contacts/search`, `POST /tickets/search`, plus versioning through `Intercom-Version`.

11. Dovetail project/highlight/insight endpoints are verified: `GET /v1/projects`, `GET /v1/highlights`, and insight export `GET /v1/insights/{insight_id}/export/{type}` where `type` is `html` or `markdown`.

12. Freshdesk ticket and ticket-conversation endpoints are verified: `GET /api/v2/tickets`, `GET /api/v2/tickets/{id}/conversations`, and `GET /api/v2/search/tickets?query=...`, with practical pagination limits.

13. Important connector-mapping caveat: current skill method IDs are connector aliases, not public endpoint names. Some method names may remain valid internally even when public endpoints differ in granularity.

14. Dovetail project-level markdown export as a single public endpoint is not verified in public docs; public export docs are insight-scoped. Any project-level export behavior should be treated as connector logic, not endpoint fact.

15. Versioning and rate-limit headers differ materially across platforms; reconciliation jobs must be idempotent and resume-safe rather than single-pass assumptions.

**Sources:**
- https://developers.hubspot.com/docs/api-reference/crm-contacts-v3/search/post-crm-v3-objects-contacts-search (evergreen endpoint docs)
- https://developers.hubspot.com/docs/api-reference/crm-notes-v3/basic/get-crm-v3-objects-notes (evergreen endpoint docs)
- https://developers.hubspot.com/docs/api-reference/crm-calls-v3/basic/get-crm-v3-objects-calls (evergreen endpoint docs)
- https://developers.hubspot.com/docs/guides/api/crm/search (current docs, accessed 2026)
- https://developers.hubspot.com/docs/api/usage-details (2025/2026 platform context)
- https://developers.hubspot.com/changelog/new-oauth-v3-api-endpoints-and-standardized-error-responses (2026)
- https://developer.zendesk.com/api-reference/ticketing/ticket-management/incremental_exports/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_audits/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_comments/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/ticketing/ticket-management/search/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/introduction/pagination/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/introduction/security-and-auth/ (evergreen endpoint docs)
- https://developer.zendesk.com/api-reference/changelog/changelog (2024-2026 updates)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/conversations/listconversations (current endpoint docs)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/conversations/searchconversations (current endpoint docs)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/contacts/searchcontacts (current endpoint docs)
- https://developers.intercom.com/docs/references/rest-api/api.intercom.io/tickets (current endpoint docs)
- https://developers.intercom.com/docs/build-an-integration/learn-more/authentication (current docs)
- https://developers.intercom.com/docs/build-an-integration/learn-more/rest-apis/update-your-api-version (current docs)
- https://developers.intercom.com/docs/build-an-integration/learn-more/rest-apis/api-changelog (2024-2025 changes)
- https://developers.intercom.com/docs/build-an-integration/learn-more/rest-apis/unversioned-changes (2024-2026 changes)
- https://developers.dovetail.com/docs/introduction (current docs)
- https://developers.dovetail.com/docs/authorization (current docs)
- https://developers.dovetail.com/reference/get_v1-projects (current endpoint docs)
- https://developers.dovetail.com/reference/get_v1-highlights (current endpoint docs)
- https://developers.dovetail.com/reference/get_v1-insights-insight-id-export-type (current endpoint docs)
- https://developers.freshdesk.com/api/ (current endpoint docs)
- https://support.freshdesk.com/support/solutions/articles/225439-what-are-the-rate-limits-for-the-api-calls-to-freshdesk- (2025/2026 context)

---

### Angle 4: Data Interpretation & Signal Quality
> How should imported CRM/support/conversation data be interpreted without overclaiming?

**Findings:**

1. Frequency must be separated from business criticality. Incident and service-priority frameworks emphasize that low-volume/high-impact problems can outrank high-volume/low-impact complaints.

2. Dedupe should precede trend inference. Teams that count raw ticket volume without duplicate suppression tend to overstate issue prevalence.

3. Recency should be weighted with two windows (short vs baseline) to catch emerging shifts without overreacting to temporary spikes.

4. Segment-first interpretation outperforms global ranking. Signals should be interpreted by cohort (segment/tier/lifecycle/region) before aggregate rollups.

5. Confidence scoring from transcript/conversation systems should be treated as routing guidance, not absolute truth; low-confidence outputs need human review loops.

6. Calibration should be monitored by subgroup, not only global averages. Miscalibrated confidence across subgroups can produce systematic interpretation errors.

7. LLM-generated summaries are not automatically evidence-grade. Transcript-vs-summary audit sampling is required before using summary output as strategic input.

8. High-stakes claims should require triangulation across at least two evidence types (for example imported support themes + interview themes, or imported sales notes + behavioral analytics).

9. Complaint volume bias is real: changes in solicitation, routing, or response channels can alter volume independent of problem severity.

10. Survivorship bias is a persistent CRM interpretation trap. Mining only successful or highly-documented opportunities hides causes from closed-lost, stalled, and lightly-logged populations.

11. Mature interpretation pipelines keep a contradiction register, not a single narrative: what support data suggests, what sales notes suggest, what interviews confirm/disconfirm.

**Sources:**
- https://support.atlassian.com/jira-service-management-cloud/docs/how-impact-and-urgency-are-used-to-calculate-priority/ (current docs, accessed 2026)
- https://support.atlassian.com/jira-service-management-cloud/docs/automatically-prioritize-incident-requests/ (current docs, accessed 2026)
- https://help.leadsquared.com/service-crm/ticket-duplicate-detection/ (current docs, accessed 2026)
- https://arxiv.org/html/2404.16887v1 (2024)
- https://docs.oracle.com/en/cloud/saas/cx-unity/cx-unity-user/Help/Data_Science/Engagement_analysis/DataScience_Model_RFM.htm (current docs, accessed 2026)
- https://docs.aws.amazon.com/lexv2/latest/dg/using-transcript-confidence-scores.html (current docs, accessed 2026)
- https://arxiv.org/abs/2404.04689 (2024)
- https://aclanthology.org/2025.emnlp-industry.91/ (2025)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11334375/ (2024)
- https://www.nngroup.com/articles/triangulation-better-research-results-using-multiple-ux-methods/ (evergreen)
- https://ideas.repec.org/a/inm/ormnsc/v71y2025i2p1671-1691.html (2025)
- https://blog.hubspot.com/sales/survivorship-bias (updated 2025)
- https://www.validity.com/wp-content/uploads/2024/05/The-State-of-CRM-Data-Management-in-2024.pdf (2024)
- https://www.gartner.com/en/newsroom/press-releases/2024-02-05-gartner-identifies-three-top-priorities-for-customer-service-and-support-leaders-in-2024 (2024)
- https://www.zendesk.com/newsroom/articles/2025-cx-trends-report/ (2024 publication)
- https://www.zendesk.com/blog/zip1-cx-trends-2026-contextual-intelligence/ (2025)

---

### Angle 5+: Failure Modes, Anti-Patterns, and Compliance Pitfalls
> What goes wrong in practice, how do you detect it, and how do you mitigate it?

**Findings:**

1. PII leakage remains common even in “internal only” discovery workflows. Detection signals include direct identifiers showing up in summarized outputs or artifact logs despite masking expectations.

2. Over-broad purpose statements (for example “improve AI”) without source-by-source legal basis documentation are a repeat compliance failure in context-import workflows.

3. Teams often claim anonymity without technical proof; model/index extraction behavior and re-identification risk remain possible unless tested.

4. Deletion/retention mismatch is frequent across multi-layer stacks (source system, sync cache, index/vector store, assistant transcripts, analytics logs).

5. Controller/processor responsibility ambiguity slows rights requests and incident response in real operations.

6. Schema drift and brittle ETL can silently corrupt trend interpretation if ingestion continues without quarantine or explicit schema-change governance.

7. Data freshness failures can masquerade as “stability” or “decline” if stale windows are not marked as non-comparable.

8. Over-automation/excessive agency allows assistants to perform high-impact actions on weak evidence when permission boundaries are too broad.

9. Hallucinated categorization and unsupported summaries contaminate imported context if output grounding/citation checks are missing.

10. Low-quality summary pipelines are often rubric problems (poor criteria, weak calibration) rather than model-only problems.

11. Missing AI disclosure/labeling in customer-facing or externally consumed outputs can create trust and policy risks as regulations evolve.

12. Public overclaims of AI-derived “facts” without substantiation are an enforcement risk.

13. Contradiction management is required: platform privacy claims (e.g., “no retention” in one layer) can coexist with retained artifacts in adjacent operational layers.

**Sources:**
- https://www.edpb.europa.eu/news/news/2024/edpb-opinion-ai-models-gdpr-principles-support-responsible-ai_en (2024)
- https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en (2024)
- https://www.cnil.fr/en/ai-system-development-cnils-recommendations-to-comply-gdpr (2026)
- https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/principles-gdpr/overview-principles/what-data-can-we-process-and-under-which-conditions_en (official reference, accessed 2026)
- https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/principles-gdpr/how-much-data-can-be-collected_en (official reference, accessed 2026)
- https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en (2024)
- https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act (2026)
- https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content (2026)
- https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/ (2025)
- https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ (2025)
- https://genai.owasp.org/llmrisk/llm092025-misinformation/ (2025)
- https://developer.salesforce.com/docs/ai/agentforce/guide/trust.html (current docs, accessed 2026)
- https://developer.salesforce.com/docs/ai/agentforce/guide/models-api-data-masking.html (current docs, accessed 2026)
- https://support.zendesk.com/hc/en-us/articles/5729714731290-Zendesk-AI-Data-Use-Information (current docs, accessed 2026)
- https://support.zendesk.com/hc/en-us/articles/6059285322522-About-generative-AI-features-in-Zendesk (current docs, accessed 2026)
- https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy (2026)
- https://learn.microsoft.com/en-us/copilot/security/privacy-data-security (2026)
- https://knowledge.hubspot.com/hubspot-ai-cloud-infrastructure-frequently-asked-questions (2026)
- https://docs.airbyte.com/using-airbyte/schema-change-management (current docs, accessed 2026)
- https://fivetran.com/docs/using-fivetran/features/data-blocking-column-hashing/config (current docs, accessed 2026)
- https://fivetran.com/docs/logs/troubleshooting/track-schema-changes (current docs, accessed 2026)
- https://docs.getdbt.com/reference/resource-properties/freshness (evergreen)
- https://docs.databricks.com/aws/en/delta-live-tables/expectations (2026)
- https://cloud.google.com/agent-assist/docs/summarization-autoeval-metrics (current docs, accessed 2026)
- https://docs.cloud.google.com/contact-center/insights/docs/qai-best-practices (current docs, accessed 2026)
- https://aclanthology.org/2024.naacl-long.251/ (2024)
- https://aclanthology.org/2024.acl-long.585/ (2024)
- https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes (2024)
- https://www.bbc.com/travel/article/20240222-air-canada-chatbot-misinformation-what-travellers-should-know (2024 case coverage)

---

## Synthesis

The strongest cross-angle conclusion is that context import quality is determined more by operational controls than by connector count. Teams already have access to rich CRM/support/conversation data, but the value of that data depends on bounded extraction windows, deterministic identity merge rules, taxonomy governance, and novelty-based handoff to interviews.

The second conclusion is that tool selection matters less than reconciliation discipline. HubSpot, Zendesk, Intercom, Dovetail, and others can all support this workflow, but each introduces different limits and edge cases (quota models, cursor rules, webhook delivery behavior, endpoint caps). Reliable context import requires hybrid sync design (event + replay) and idempotent state tracking.

Third, interpretation failures are predictable and avoidable. Complaint volume bias, survivorship bias in sales notes, and uncalibrated confidence in summaries frequently create false certainty. Good practice requires severity-aware scoring, dedupe-first counting, cohort segmentation, and mandatory triangulation before strategic claims.

Fourth, API endpoint reality must be separated from connector alias behavior. Public endpoint documentation confirms core operations, but internal `method_id` names remain connector abstractions. The `discovery-context-import` skill should explicitly distinguish “verified endpoint fact” from “runtime connector mapping,” especially around Dovetail export semantics.

Finally, governance is not optional overhead. PII leakage, retention mismatches, and over-broad AI claims are now directly tied to regulatory and enforcement risk. The skill should include explicit compliance controls, uncertainty reporting, and anti-pattern detection steps inside normal methodology rather than as end-note warnings.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.

- [x] Replace current brief methodology with a full import control loop (`scope -> extract -> normalize -> score -> synthesize -> handoff`).
- [x] Add explicit bias ledger requirements (sales-process bias, complaint overrepresentation, source coverage skew, recency skew).
- [x] Add endpoint-reality notes and connector-mapping caution, especially for Dovetail export granularity.
- [x] Add reliability guidance for incremental sync, pagination, retry/backoff, and stale-window handling.
- [x] Add interpretation rubric with severity, recency, frequency, and confidence dimensions.
- [x] Add contradiction register requirement (e.g., support says X, sales says Y, interview confirms/disconfirms Z).
- [x] Add anti-pattern warning blocks with detection signals and deterministic mitigations.
- [x] Expand PII/compliance section with purpose limitation, minimization, retention mapping, and rights/deletion traceability.
- [x] Expand schema to encode evidence provenance, merge policy, scoring logic, uncertainty, and confidence.
- [x] Add pre-write artifact checklist and block publishing when required controls are missing.

---

## Draft Content for SKILL.md

> This section is intentionally the largest section and is paste-ready.
> Use directly, then trim for final SKILL.md editing.

### Draft: Core Operating Stance

You import customer context to accelerate discovery, not to replace discovery interviews.

Imported CRM, support, and conversation evidence is biased by system mechanics:
- CRM notes reflect what sales teams logged, what was remembered, and what was rewarded.
- Support tickets overrepresent users who contacted support and may over-weight acute problems.
- Conversation intelligence systems may overrepresent call types from specific segments or teams.

Treat imported data as directional evidence with known limits. Your job is to make those limits explicit and still produce useful hypothesis seeds.

Hard rule: if bias, provenance, or freshness controls are missing, downgrade output confidence and state exactly why.

### Draft: Methodology (Context Import Control Loop)

Use this six-stage workflow every time:

#### 1) Scope and Extraction Plan

Before any API calls, define:
- `study_id`
- `decision_scope` (what decisions this import informs)
- source set (`hubspot`, `zendesk`, `intercom`, `dovetail`, optional others)
- time window (`last_30_days`, `last_90_days`, custom)
- segment filters (if applicable)
- required output fields

Start narrow. Do not begin with full-history pull unless a specific reason is documented.

Default windows:
- operational discovery seed: 30-90 days
- trend verification: compare short window vs baseline window

If you need long-range history, ingest in waves and evaluate signal delta between waves.

#### 2) Pull and Normalize

Extract evidence-bearing records (notes, calls, tickets, conversations, insights) and normalize into a common internal structure:
- `source_system`
- `source_record_id`
- `created_at`
- `updated_at`
- `author_role` (if available)
- `account_segment` (if available)
- `raw_text_excerpt`
- `topic_hints` (optional)
- `severity_hint` (optional)

Normalization rules:
- normalize timestamps to UTC
- preserve source timezone metadata when present
- store cursor/checkpoint per source for replay-safe sync
- enforce deterministic merge key rules before upsert

If merge key is ambiguous, stop and resolve before synthesis.

#### 3) Privacy and Compliance Gate

Before synthesis, run mandatory privacy gate:
- redact direct identifiers in working artifacts
- replace names/emails/account identifiers with anonymized labels
- verify purpose and lawful basis are documented per source
- verify data minimization (drop unused fields)
- verify retention/deletion ownership is declared

If any control fails, do not publish artifact as complete.

#### 4) Theme Construction and Triage

Build themes with a governed taxonomy:
- short tag labels
- unambiguous tag descriptions
- source examples attached per tag
- count both raw mentions and deduped issue counts

Triaging rule:
- score theme priority using severity + urgency + frequency + recency
- do not rank by mention count alone

Recommended score components:
- `severity_score` (0-5)
- `urgency_score` (0-5)
- `frequency_score` (0-5 from deduped issue count)
- `recency_score` (0-5 from short-window movement)
- `confidence_score` (0-1 evidence quality + source coverage)

#### 5) Contradiction and Uncertainty Pass

Create a contradiction register:
- where support and CRM signals disagree
- where transcript summaries and raw excerpts disagree
- where source trends are unstable due to freshness/schema issues

Create an uncertainty register:
- what was not observed
- what could not be verified
- what requires interviews to resolve causality

#### 6) Handoff to Discovery Instruments

Convert context import into interview/survey inputs:
- `pain_themes`
- `objection_themes`
- `hypothesis_seeds`
- `interview_probe_candidates`
- `limitations`

Handoff rule:
- stop extending import when marginal novelty drops and new records mostly repeat existing themes.
- move to interviews when mechanism-level questions remain unanswered.

Do NOT:
- Do NOT treat imported counts as prevalence estimates.
- Do NOT infer causality from ticket volume alone.
- Do NOT skip fresh interviews because import looks “complete.”

### Draft: Bias Ledger Requirements

Add a required `bias_ledger` section in every output with at least:

1. **Sales-process bias**
- Detection: heavy reliance on opportunity notes from closed-won or highly-engaged accounts.
- Mitigation: include closed-lost/stalled samples and annotate note coverage gaps.

2. **Complaint overrepresentation**
- Detection: support-heavy source mix and low passive-user representation.
- Mitigation: treat support-driven themes as risk indicators, not universal prevalence.

3. **Source coverage skew**
- Detection: one source contributes dominant share of evidence.
- Mitigation: enforce minimum multi-source corroboration for high-stakes themes.

4. **Recency skew**
- Detection: trend inference uses only short spike window.
- Mitigation: compare short vs baseline window before prioritization.

5. **Summary fidelity risk**
- Detection: summary claims exceed or contradict underlying excerpts.
- Mitigation: sample-based summary-vs-source audit before final publish.

### Draft: Available Tools

Use runtime connector methods, then map claims to verified public endpoints.

```python
# Always inspect connector surface first.
hubspot(op="help")
zendesk(op="help")
intercom(op="help")
dovetail(op="help")

# HubSpot examples (connector aliases in current skill)
hubspot(op="call", args={
  "method_id": "hubspot.contacts.search.v1",
  "filterGroups": [{"filters": [{"propertyName": "company", "operator": "EQ", "value": "Company Name"}]}]
})

hubspot(op="call", args={
  "method_id": "hubspot.notes.list.v1",
  "objectType": "contacts",
  "objectId": "contact_id"
})

hubspot(op="call", args={
  "method_id": "hubspot.calls.list.v1",
  "objectType": "contacts",
  "objectId": "contact_id"
})

# Zendesk examples
zendesk(op="call", args={
  "method_id": "zendesk.incremental.ticket_events.comment_events.list.v1",
  "start_time": 1704067200
})

zendesk(op="call", args={
  "method_id": "zendesk.tickets.audits.list.v1",
  "ticket_id": "ticket_id"
})

# Intercom examples
intercom(op="call", args={
  "method_id": "intercom.conversations.list.v1",
  "per_page": 50,
  "starting_after": None
})

# Dovetail example (connector alias)
dovetail(op="call", args={
  "method_id": "dovetail.insights.export.markdown.v1",
  "projectId": "project_id"
})
```

Verified endpoint mappings for integration validation:
- HubSpot contacts search: `POST /crm/v3/objects/contacts/search`
- HubSpot notes list: `GET /crm/v3/objects/notes`
- HubSpot calls list: `GET /crm/v3/objects/calls`
- HubSpot notes search: `POST /crm/v3/objects/notes/search`
- HubSpot calls search: `POST /crm/v3/objects/calls/search`
- HubSpot tickets search: `POST /crm/v3/objects/tickets/search`
- Zendesk incremental ticket events: `GET /api/v2/incremental/ticket_events?start_time={unix}&include=comment_events`
- Zendesk ticket audits: `GET /api/v2/tickets/{ticket_id}/audits`
- Zendesk ticket comments: `GET /api/v2/tickets/{ticket_id}/comments`
- Zendesk search: `GET /api/v2/search?query={query}`
- Zendesk export search: `GET /api/v2/search/export?query={query}&filter[type]=ticket`
- Intercom conversations list: `GET /conversations`
- Intercom conversation details: `GET /conversations/{id}`
- Intercom conversations search: `POST /conversations/search`
- Intercom contacts search: `POST /contacts/search`
- Intercom tickets search: `POST /tickets/search`
- Dovetail projects list: `GET /v1/projects`
- Dovetail highlights list: `GET /v1/highlights`
- Dovetail insight export: `GET /v1/insights/{insight_id}/export/{type}`

Critical connector caveat:
- Connector `method_id` is an internal alias, not the public endpoint name.
- Do not assert endpoint behavior that you cannot map to public docs.
- For Dovetail, public docs verify insight-scoped export; any project-wide export behavior should be documented as connector implementation, not endpoint fact.

Rate-limit and reliability rules:
- Use cursor/checkpoint sync per source.
- On `429` or quota-style throttling, apply exponential backoff.
- Never assume webhooks are ordered or complete; run replay/reconciliation jobs.
- Mark data as stale when freshness threshold is exceeded.

### Draft: Interpretation Rubric (Signal vs Noise)

Use this interpretation sequence:

1. **Clean the denominator**
- dedupe near-identical issues first
- separate repeated updates from new incidents

2. **Score business significance**
- severity and urgency first
- then frequency and recency

3. **Assess evidence quality**
- source diversity
- text fidelity
- summary confidence
- sampling skew level

4. **Classify theme confidence**
- `high_confidence`: corroborated across >=2 sources with stable trend signal
- `medium_confidence`: strong in one source plus partial corroboration
- `low_confidence`: weak coverage, freshness risk, or unresolved contradictions

5. **Define action class**
- `interview_probe_now`: high importance but unresolved mechanism
- `monitor`: directional signal requiring another import cycle
- `park`: weak signal not tied to current decision scope

Interpretation anti-rules:
- Never treat complaint volume as prevalence.
- Never treat CRM note frequency as customer truth without source-mix context.
- Never publish trend claims if source freshness is out of SLA.

### Draft: Contradiction Register Instructions

Add required section:

`contradiction_register` entries must include:
- `claim_a` (source and evidence)
- `claim_b` (source and evidence)
- `possible_explanations`
- `resolution_plan` (interview probe, additional extraction, or defer)
- `status` (`open`, `partially_resolved`, `resolved`)

You must keep contradictions visible. Do not silently average them into one narrative.

### Draft: Anti-Pattern Warning Blocks

#### Warning: Ticket Volume Equals Prevalence
- **What it looks like:** You rank themes by raw ticket count only.
- **Detection signal:** High-volume low-severity themes outrank low-volume high-severity incidents by default.
- **Consequence:** Priority inversion and misleading roadmap pressure.
- **Mitigation:** Use severity+urgency gates before frequency and require deduped counts.

#### Warning: Closed-Won CRM Survivorship
- **What it looks like:** Analysis uses mostly closed-won or highly active account notes.
- **Detection signal:** Closed-lost/stalled opportunities underrepresented in source coverage.
- **Consequence:** Over-optimistic interpretation of objections and adoption patterns.
- **Mitigation:** Force balanced opportunity-state sampling and annotate note completeness.

#### Warning: Webhook-Only Completeness Assumption
- **What it looks like:** No replay/reconciliation job because webhooks are considered complete.
- **Detection signal:** Gaps between source totals and imported totals; duplicate or out-of-order event artifacts.
- **Consequence:** Silent evidence loss or double-count inflation.
- **Mitigation:** Pair push ingestion with scheduled incremental replay and idempotent merge.

#### Warning: Stale Data Interpreted as Stable Trend
- **What it looks like:** Trend charts continue after freshness failures.
- **Detection signal:** Last successful sync exceeds freshness SLA but reporting remains “green.”
- **Consequence:** False confidence and delayed issue detection.
- **Mitigation:** Block trend claims when stale; mark windows non-comparable until refreshed.

#### Warning: Summary Hallucination as Evidence
- **What it looks like:** LLM summary statements are used without source excerpt checks.
- **Detection signal:** Summary claims cannot be traced to stored raw evidence.
- **Consequence:** Fabricated or distorted themes enter discovery planning.
- **Mitigation:** Require citation links/excerpts and sample-level fidelity audits.

#### Warning: PII Leakage in Artifacts
- **What it looks like:** Names/emails/account identifiers appear in published summary artifacts.
- **Detection signal:** DLP/audit catches direct identifiers post-redaction stage.
- **Consequence:** Compliance risk and trust damage.
- **Mitigation:** Enforce pre-write redaction gate and reject artifact write on leakage.

#### Warning: Purpose Creep in Context Import
- **What it looks like:** Imported data reused for unrelated decisions without stated basis.
- **Detection signal:** Missing purpose/legal-basis metadata per source.
- **Consequence:** Governance and regulatory risk.
- **Mitigation:** Per-source purpose register; block publication when missing.

### Draft: Recording Instructions

You should write one primary artifact and optional supporting artifacts:

```python
write_artifact(
  artifact_type="discovery_context_summary",
  path="/discovery/{study_id}/context",
  data={...}
)
```

Optional supporting artifacts:
- `/discovery/{study_id}/context-contradictions`
- `/discovery/{study_id}/context-bias-ledger`
- `/discovery/{study_id}/context-import-log`

Before `write_artifact`, verify:
1. Time window and source list were declared.
2. Merge key and dedupe strategy were declared.
3. Redaction gate passed.
4. Freshness checks passed or stale window clearly labeled.
5. Contradictions were recorded.
6. Limitations and uncertainty entries are non-empty.

If any required check fails, return `blocked` and remediation actions.

### Draft: Schema additions

```json
{
  "discovery_context_summary": {
    "type": "object",
    "description": "Imported evidence summary used to seed discovery hypotheses and interview probes.",
    "required": [
      "study_id",
      "import_scope",
      "sources_used",
      "source_coverage",
      "extraction_controls",
      "pain_themes",
      "objection_themes",
      "hypothesis_seeds",
      "bias_ledger",
      "contradiction_register",
      "confidence_assessment",
      "limitations",
      "uncertainties"
    ],
    "additionalProperties": false,
    "properties": {
      "study_id": {
        "type": "string",
        "description": "Unique discovery study identifier."
      },
      "import_scope": {
        "type": "object",
        "required": [
          "decision_scope",
          "time_window",
          "segment_filters"
        ],
        "additionalProperties": false,
        "description": "Declared boundaries for this context import run.",
        "properties": {
          "decision_scope": {
            "type": "string",
            "description": "Decision this import informs (for example pricing objections, onboarding friction)."
          },
          "time_window": {
            "type": "object",
            "required": [
              "start",
              "end",
              "window_label"
            ],
            "additionalProperties": false,
            "properties": {
              "start": {
                "type": "string",
                "format": "date-time",
                "description": "UTC start timestamp for imported records."
              },
              "end": {
                "type": "string",
                "format": "date-time",
                "description": "UTC end timestamp for imported records."
              },
              "window_label": {
                "type": "string",
                "enum": [
                  "last_30_days",
                  "last_90_days",
                  "custom"
                ],
                "description": "Human-readable window category."
              }
            }
          },
          "segment_filters": {
            "type": "array",
            "description": "Optional segmentation filters applied during import.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "sources_used": {
        "type": "array",
        "description": "Source systems included in this import.",
        "minItems": 1,
        "items": {
          "type": "object",
          "required": [
            "source_type",
            "record_count",
            "date_range",
            "api_mode"
          ],
          "additionalProperties": false,
          "properties": {
            "source_type": {
              "type": "string",
              "enum": [
                "hubspot",
                "salesforce",
                "zendesk",
                "intercom",
                "dovetail",
                "freshdesk",
                "jira_service_management",
                "gong",
                "other"
              ],
              "description": "System where records originated."
            },
            "record_count": {
              "type": "integer",
              "minimum": 0,
              "description": "Number of raw records imported from this source."
            },
            "date_range": {
              "type": "string",
              "description": "Date range represented by imported records from this source."
            },
            "api_mode": {
              "type": "string",
              "enum": [
                "incremental",
                "search",
                "export",
                "webhook_plus_replay"
              ],
              "description": "Primary ingestion pattern used for this source."
            },
            "cursor_checkpoint": {
              "type": "string",
              "description": "Opaque checkpoint used for resume-safe sync."
            }
          }
        }
      },
      "source_coverage": {
        "type": "object",
        "required": [
          "source_mix_ok",
          "dominant_source",
          "coverage_notes"
        ],
        "additionalProperties": false,
        "description": "Coverage and representativeness assessment of imported sources.",
        "properties": {
          "source_mix_ok": {
            "type": "boolean",
            "description": "Whether source mix is adequate for current decision scope."
          },
          "dominant_source": {
            "type": "string",
            "description": "Source contributing largest share of evidence."
          },
          "coverage_notes": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Caveats about missing cohorts, channels, or account states."
          }
        }
      },
      "extraction_controls": {
        "type": "object",
        "required": [
          "merge_key_policy",
          "dedupe_policy",
          "freshness_status",
          "pii_redaction_status"
        ],
        "additionalProperties": false,
        "description": "Operational controls that govern import integrity.",
        "properties": {
          "merge_key_policy": {
            "type": "string",
            "description": "How records are matched/upserted across sources."
          },
          "dedupe_policy": {
            "type": "string",
            "description": "How duplicate issues and repeated records are identified."
          },
          "freshness_status": {
            "type": "string",
            "enum": [
              "fresh",
              "stale_warning",
              "stale_blocking"
            ],
            "description": "Whether source freshness meets interpretation requirements."
          },
          "pii_redaction_status": {
            "type": "string",
            "enum": [
              "passed",
              "failed"
            ],
            "description": "Outcome of PII redaction gate before artifact write."
          }
        }
      },
      "pain_themes": {
        "type": "array",
        "description": "Top imported pain patterns and supporting evidence.",
        "items": {
          "type": "object",
          "required": [
            "theme",
            "severity_score",
            "urgency_score",
            "frequency_signal",
            "recency_signal",
            "confidence",
            "supporting_evidence"
          ],
          "additionalProperties": false,
          "properties": {
            "theme": {
              "type": "string",
              "description": "Canonical theme label."
            },
            "severity_score": {
              "type": "integer",
              "minimum": 0,
              "maximum": 5,
              "description": "Estimated business impact severity."
            },
            "urgency_score": {
              "type": "integer",
              "minimum": 0,
              "maximum": 5,
              "description": "Estimated urgency/time sensitivity."
            },
            "frequency_signal": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "description": "Frequency class from deduped evidence counts."
            },
            "recency_signal": {
              "type": "string",
              "enum": [
                "rising",
                "stable",
                "declining",
                "unknown"
              ],
              "description": "Short-window trend direction vs baseline window."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "description": "Confidence level after source quality and contradiction checks."
            },
            "supporting_evidence": {
              "type": "array",
              "description": "Anonymized excerpts or evidence references.",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "objection_themes": {
        "type": "array",
        "description": "Common buying/adoption objections from imported evidence.",
        "items": {
          "type": "string"
        }
      },
      "hypothesis_seeds": {
        "type": "array",
        "description": "Candidate hypotheses generated from imported context for follow-up discovery.",
        "items": {
          "type": "string"
        }
      },
      "bias_ledger": {
        "type": "array",
        "description": "Known bias patterns detected in imported context and mitigation notes.",
        "items": {
          "type": "object",
          "required": [
            "bias_type",
            "detection_signal",
            "mitigation"
          ],
          "additionalProperties": false,
          "properties": {
            "bias_type": {
              "type": "string",
              "enum": [
                "sales_survivorship",
                "support_overrepresentation",
                "source_coverage_skew",
                "recency_skew",
                "summary_fidelity_risk",
                "other"
              ],
              "description": "Type of interpretation bias observed."
            },
            "detection_signal": {
              "type": "string",
              "description": "Operational signal indicating this bias was present."
            },
            "mitigation": {
              "type": "string",
              "description": "Mitigation applied or planned."
            }
          }
        }
      },
      "contradiction_register": {
        "type": "array",
        "description": "Explicitly tracked cross-source contradictions.",
        "items": {
          "type": "object",
          "required": [
            "claim_a",
            "claim_b",
            "resolution_plan",
            "status"
          ],
          "additionalProperties": false,
          "properties": {
            "claim_a": {
              "type": "string",
              "description": "First claim with source reference."
            },
            "claim_b": {
              "type": "string",
              "description": "Conflicting claim with source reference."
            },
            "resolution_plan": {
              "type": "string",
              "description": "How contradiction will be resolved (interview probe, additional extraction, etc.)."
            },
            "status": {
              "type": "string",
              "enum": [
                "open",
                "partially_resolved",
                "resolved"
              ],
              "description": "Current contradiction resolution status."
            }
          }
        }
      },
      "confidence_assessment": {
        "type": "object",
        "required": [
          "overall_confidence",
          "confidence_notes"
        ],
        "additionalProperties": false,
        "description": "Summary confidence for this context artifact.",
        "properties": {
          "overall_confidence": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Overall confidence in imported-context conclusions."
          },
          "confidence_notes": {
            "type": "array",
            "description": "Reasons supporting or reducing confidence.",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "limitations": {
        "type": "array",
        "description": "Known limitations of imported evidence and pipeline constraints.",
        "items": {
          "type": "string"
        }
      },
      "uncertainties": {
        "type": "array",
        "description": "Open unknowns requiring additional research or interviews.",
        "items": {
          "type": "string"
        }
      }
    }
  }
}
```

### Draft: Endpoint Verification Note Block

Add this callout where tool guidance appears:

> You must separate connector alias names from public endpoint facts.  
> Example: `dovetail.insights.export.markdown.v1` may be a valid connector alias, but public docs verify insight-level export endpoints (`/v1/insights/{insight_id}/export/{type}`).  
> If alias-to-endpoint mapping is uncertain, record uncertainty in `limitations` and avoid endpoint claims in output text.

### Draft: Completion Criteria Block

You can mark context import complete only when:
- source list + window are documented,
- at least one bias entry is recorded (or explicit none with justification),
- contradictions are either resolved or have a concrete resolution plan,
- PII redaction gate passed,
- confidence and limitations are coherent with evidence coverage,
- at least three interview/survey probes are generated from imported themes.

If not complete, return status `needs_followup` with exact missing controls.

---

## Gaps & Uncertainties

- Public endpoint docs are clear for core HubSpot/Zendesk/Intercom operations, but connector `method_id` to endpoint mapping still needs runtime verification in environment.
- Dovetail public docs verify insight-level export endpoints; a single-call project-level markdown export endpoint was not verified in public docs and may be connector-level composition.
- Several vendor documentation pages are living docs without explicit publication dates; these are cited as current docs (accessed 2026) and should be revalidated at implementation time.
- Plan/tier entitlements can materially change behavior (rate limits, automation features, export scope); final SKILL.md should include tenant-dependent caveats rather than global assumptions.
- Jurisdiction-specific privacy obligations can differ beyond sources cited; organizations should align this workflow with their legal counsel and internal data-governance policy.

