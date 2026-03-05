# Research: signal-professional-network

**Skill path:** `flexus-client-kit/flexus_simple_bots/researcher/skills/signal-professional-network/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`signal-professional-network` detects organization-level professional network signals from LinkedIn activity for one company set or one industry topic per run. The current skill is already focused on post themes, follower momentum, and engagement quality, but it is too optimistic about metric comparability and too light on API/access constraints.

2024-2026 evidence points to three practical changes needed for authoritative output quality:
- LinkedIn organization analytics should be interpreted with explicit lag and denominator awareness (impressions-based and follower-based rates are not interchangeable).
- API reality matters as much as analysis logic: version headers, access tiers, permissions, and data retention rules can invalidate implementation assumptions.
- "Strong signal" decisions now require quality controls against vanity engagement, plan-gated analytics differences, and compliance-unsafe data usage patterns.

This research expands the skill with source-backed methodology, tooling constraints, interpretation thresholds, anti-pattern guardrails, and paste-ready `SKILL.md` draft sections.

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

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources are explicitly noted: **passed**
- Volume target met (Findings sections 800-4000 words): **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

- Practitioners are converging on a three-window workflow for organization signal tracking: near-term check (7-14 days), operating window (30 days), and baseline window (90-365 days). LinkedIn page analytics surfaces are naturally aligned to 30-day and 365-day comparisons, and competitor trending views are explicitly refreshed daily for the past 30 days.
- Decision quality improves when teams enforce a "D-2 cutoff" rule for performance verdicts, because LinkedIn states content metrics (except reactions/comments) can take up to 48 hours to reflect.
- Better teams keep the competitor cohort fixed for at least one full 30-day cycle before changing peers, because competitor rank/order instability can create false "theme shift" conclusions.
- Theme analysis quality increases when each detected topic is segmented at least once by native professional dimensions (Location, Seniority, Job function, Industry, Company size), instead of relying only on global page averages.
- Follower momentum should be normalized by page size tier, not interpreted as absolute gains. Small pages can show high percent growth with low absolute increments; large pages can have meaningful momentum with lower percentage growth.
- Format normalization is now required for fair interpretation. Recent benchmark studies show material engagement spread by format (multi-image, documents, video, static image, polls, text), so a "topic is weak" claim without format adjustment is often wrong.
- In 2024-2026 practice, "conversation depth" (comment behavior) is increasingly weighted above raw reaction totals for quality judgments, aligned with LinkedIn's public framing of deeper engagement and comments growth.
- Search-appearance data is increasingly used as a secondary signal when engagement is mixed: if topic-keyword discoverability rises while engagement lags, practitioners mark it as "visibility-leading, conversion-lagging" instead of dropping the topic.
- LinkedIn's own 2025 business highlights report comments growth and continued video upload growth, which implies methodological updates: video and comment-intensity should be mandatory dimensions in organization signal scans, not optional add-ons.

**Contradictions / nuances to encode:**

- Benchmarks disagree on "good engagement" because denominator definitions differ (`by impressions` vs `by followers`), so thresholds must be metric-specific.
- LinkedIn provides metric definitions and timing behavior but not ranking-weight formulas; operational thresholds are heuristics, not official platform cutoffs.
- Premium and non-premium page analytics surfaces differ, so run-level limitations must state whether "missing insight" is actual absence or plan-gated visibility.

**Sources:**
- [LinkedIn Page analytics](https://www.linkedin.com/help/linkedin/answer/a547077)
- [Content analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a564051)
- [Competitor analytics for your LinkedIn Page](https://www.linkedin.com/help/lms/answer/a553615/competitor-analytics-for-your-linkedin-page?lang=en)
- [Follower analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a570460)
- [Visitor analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a570455)
- [Search Appearances analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a7473929)
- [Socialinsider LinkedIn Benchmarks (2025)](https://www.socialinsider.io/social-media-benchmarks/linkedin)
- [Q1 Business Highlights (LinkedIn, 2025)](https://news.linkedin.com/2025/Q1-Business-Highlights)
- [LinkedIn video growth update (2025)](https://www.linkedin.com/pulse/up-36-over-last-year-video-linkedin-booming-time-now-somasundaram-yqbzc)
- [Leveraging dwell-time on LinkedIn feed (evergreen)](https://www.linkedin.com/blog/engineering/feed/leveraging-dwell-time-to-improve-member-experiences-on-the-linkedin-feed)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- Native LinkedIn Page analytics remains the highest-trust baseline for owned page monitoring, with distinct modules for content, followers, visitors, search appearances, and competitors.
- Premium Company Page materially expands competitor and visitor insight surfaces, so "tool capability" must be assessed against subscription tier, not only product category.
- Sales Navigator is a complementary signal layer for company/account-level momentum events, but it should not be treated as a replacement for Page analytics.
- LinkedIn Community Management APIs are practical for productized org monitoring, but access is vetted and tiered; implementation requires app review, approved use case, and ongoing compliance posture.
- LinkedIn rate limits are endpoint-specific and not fully published in docs; practical operations must read quotas from Developer Portal analytics instead of assuming static global values.
- LinkedIn versioning is not optional: missing or deprecated `Linkedin-Version` headers can fail calls. API strategy must include yearly upgrade planning.
- External platforms (Buffer, Metricool, Sprout, Sprinklr, Brandwatch, Meltwater, Hootsuite) differ most on historical depth, permissions footprint, and LinkedIn content field availability. Marketing pages often overstate "coverage"; documentation caveats matter more than feature headlines.
- Enterprise tooling should be treated as "workflow amplifiers" over official API/network constraints, not replacements for them. The base constraint set remains LinkedIn scopes, terms, and retention limits.

| Provider | Primary strength | Practical limitation | Operational note |
|---|---|---|---|
| LinkedIn Page Analytics (native) | Highest-fidelity owned-page signals | Plan-gated depth in some modules | Best baseline for methodology and thresholds |
| Premium Company Page | Stronger competitor/visitor insight surfaces | Paid tier required | Must tag run with premium/non-premium availability |
| Sales Navigator | Account/lead/company change signals | Separate product and scope | Use as context layer, not direct engagement source |
| LinkedIn Community Mgmt API | Programmatic publishing + analytics endpoints | Access vetting and tier upgrade process | Essential for scalable pipeline builds |
| Buffer | Lightweight publishing + basic analytics | LinkedIn feature and history constraints | Good for SMB ops; weaker deep analytics |
| Metricool | Unified dashboard/reporting and competitor snapshots | History/sync depth varies by plan and API return | Validate historical backfill assumptions |
| Sprout / Sprinklr / Brandwatch / Meltwater / Hootsuite | Enterprise workflow, governance, reporting | Contract/plan-specific limits and content restrictions | Check field-level availability and export/legal constraints |

**Sources:**
- [LinkedIn Page analytics](https://www.linkedin.com/help/linkedin/answer/a547077)
- [Competitor analytics for your LinkedIn Page](https://www.linkedin.com/help/lms/answer/a553615/competitor-analytics-for-your-linkedin-page?lang=en)
- [Premium Insights on Company Pages (Sales Navigator)](https://www.linkedin.com/help/sales-navigator/answer/a565340/premium-insights-on-company-pages-overview?lang=en)
- [Community Management App Review](https://learn.microsoft.com/en-us/linkedin/marketing/community-management-app-review)
- [LinkedIn API rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)
- [LinkedIn Marketing API versioning](https://learn.microsoft.com/en-us/linkedin/marketing/versioning?view=li-lms-2025-10)
- [Buffer + LinkedIn support](https://support.buffer.com/article/560-using-linkedin-with-buffer)
- [Metricool historical data](https://help.metricool.com/en/article/historical-data-available-rn3q49/)
- [Sprinklr LinkedIn limitations](https://www.sprinklr.com/help/articles/capabilities-and-limitations/linkedin-capabilities-and-limitations/649aeadbefca565f6513b912)
- [Brandwatch LinkedIn data restrictions](https://developers.brandwatch.com/docs/data-restrictions)
- [Meltwater API usage limits](https://developer.meltwater.com/docs/meltwater-api/getting-started/usage-limits/)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- LinkedIn defines engagement rate as interactions per impressions for page content analytics. This should be the primary post-quality denominator for organization-level signal interpretation.
- Impressions and members-reached values in LinkedIn page analytics are estimates, so small point changes should be treated as noise unless sustained across multiple windows.
- A practical 2025 benchmark anchor from large-sample studies is around ~5% engagement by impressions for LinkedIn business content, but this varies by format and page cohort.
- Format-level spread is material (multi-image and native documents often above baseline; text lower), so comparisons should be intra-format first, cross-format second.
- Follower-based engagement metrics remain useful for account-size normalization, but they answer a different question than impression-based quality. Mixing them without labeling causes false conclusions.
- Follower growth interpretation is heavily size-dependent: smaller pages can post stronger percentage growth while larger pages show lower percent growth with larger absolute gains.
- Comments are rising as a strategic signal dimension (official LinkedIn business updates cite comments growth), so frameworks that rely mostly on likes/reactions are now under-sensitive.
- Organic page analytics and Campaign Manager views can diverge for boosted content; cross-surface reconciliation is required before declaring performance shifts.
- Confidence should be capped when interpretation uses one provider, one denominator, or one short window.

**Practical threshold guidance (defaults, tune by niche):**

- `Strong content-quality signal` (org-level): engagement by impressions >= page 30-day median and sustained in at least 2 snapshots.
- `Emerging topic priority`: same topic appears in >=3 posts across >=2 competitor orgs within 30 days and at least one post crosses benchmark-adjusted engagement threshold.
- `Follower momentum growth`: monthly follower growth above peer size-tier baseline OR above organization's own trailing baseline for 2 consecutive windows.
- `Debate-quality uplift`: comments-per-1k impressions rises while reactions-per-1k impressions is flat (often indicates stronger active interest).

**Misinterpretations to avoid:**

- Misread: "Engagement is up" while switching denominator from followers to impressions.
- Misread: Treating 24-48h metrics as final verdict despite published lag behavior.
- Misread: Calling trend from a single viral outlier post.
- Misread: Comparing boosted performance with organic-only metrics without noting source surface.
- Misread: Treating estimated impression changes as definitive when change magnitude is within noise range.

**Sources:**
- [Content analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a564051)
- [Follower analytics for your LinkedIn Page](https://www.linkedin.com/help/linkedin/answer/a570460)
- [Competitor analytics for your LinkedIn Page](https://www.linkedin.com/help/lms/answer/a553615/competitor-analytics-for-your-linkedin-page?lang=en)
- [Socialinsider LinkedIn Benchmarks (2025)](https://www.socialinsider.io/social-media-benchmarks/linkedin)
- [Rival IQ 2024 LinkedIn Benchmark Report](https://www.rivaliq.com/blog/linkedin-benchmark-report/)
- [Q1 Business Highlights (LinkedIn, 2025)](https://news.linkedin.com/2025/Q1-Business-Highlights)
- [Hootsuite benchmark framing (denominator caveats)](https://blog.hootsuite.com/calculate-engagement-rate/)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Unauthorized scraping/automation anti-pattern**
  - What it looks like: browser bots, crawlers, scripted actions, or extensions that scrape/automate LinkedIn UI.
  - Detection signal: high-frequency non-human interaction patterns, repeated account restrictions.
  - Consequence: account/API access risk; hard policy violations.
  - Mitigation: use approved API pathways only; remove unapproved automation; keep auditable access logs.

- **Metric denominator conflation**
  - What it looks like: mixing engagement-by-impressions, engagement-by-followers, and raw counts as if equivalent.
  - Detection signal: one score changes denominators by section without disclosure.
  - Consequence: false trend calls and wrong prioritization.
  - Mitigation: require metric-definition labels for each claim; compare like-for-like only.

- **Recency overreaction**
  - What it looks like: strategy shifts based on <48h windows or one outlier post.
  - Detection signal: recommendation references only latest week and no baseline.
  - Consequence: volatility chasing.
  - Mitigation: require 30d + baseline window and D-2 lag guard before strong verdicts.

- **Plan-surface blindness**
  - What it looks like: assuming analytics parity between free and premium company pages.
  - Detection signal: missing module data interpreted as "no signal."
  - Consequence: false negatives.
  - Mitigation: record plan tier and mark unavailable surfaces explicitly in limitations.

- **Compliance-unsafe member data handling**
  - What it looks like: exporting/combining member activity data to CRM or lead enrichment.
  - Detection signal: downstream datasets include member-level LinkedIn social activity outside allowed use.
  - Consequence: terms breach and API loss risk.
  - Mitigation: strict purpose binding, retention controls, no transfer/combination where prohibited.

- **Retention rule violations**
  - What it looks like: indefinite storage of member social activity or profile fields.
  - Detection signal: no TTL/delete job for member activity cache.
  - Consequence: direct violation of documented storage requirements.
  - Mitigation: field-level retention matrix and automated purge.

- **Official API vs wrapper confusion**
  - What it looks like: treating third-party scraping APIs as equivalent to official LinkedIn APIs.
  - Detection signal: endpoints are provider URLs but labeled "LinkedIn API."
  - Consequence: fragility, legal risk, broken assumptions on scopes/versioning.
  - Mitigation: separate "official" and "third-party" evidence classes in both logic and reporting.

**Risk prioritization (highest impact first):**
1. Unauthorized scraping/automation
2. Compliance-unsafe member-data usage
3. Retention/deletion non-compliance
4. Denominator conflation in interpretation
5. Recency overreaction and volatility chasing

**Sources:**
- [Prohibited software and extensions](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en)
- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [Restricted uses of LinkedIn Marketing APIs and data](https://learn.microsoft.com/en-us/linkedin/marketing/restricted-use-cases?view=li-lms-2026-01)
- [LinkedIn Marketing API Program data storage requirements](https://learn.microsoft.com/en-us/linkedin/marketing/data-storage-requirements?view=li-lms-2025-10)
- [LinkedIn Marketing API Terms](https://www.linkedin.com/legal/l/marketing-api-terms)
- [LinkedIn API Terms of Use](https://www.linkedin.com/legal/l/api-terms-of-use)
- [ICO and global privacy authorities joint follow-up statement (2024)](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2024/10/global-privacy-authorities-issue-follow-up-joint-statement-on-data-scraping-after-industry-engagement/)

---

### Angle 5+: Official API Endpoint Reality & Integration Constraints
> Domain-specific additional angle: exact endpoint verification, permission/tier constraints, and migration nuances for organization-level LinkedIn signal collection.

**Findings:**

- Official org post creation/retrieval is documented on `https://api.linkedin.com/rest/posts`, and Posts API is positioned as the replacement for legacy `ugcPosts`.
- Organization-level engagement surfaces are split: `socialActions` is still documented, while newer docs also emphasize `reactions` and `socialMetadata`. Integrations must treat this as migration overlap, not contradiction-free replacement.
- `organizationalEntityFollowerStatistics` remains core for follower demographics and gains, but docs explicitly state total follower counts are no longer returned there; total follower count now belongs to `networkSizes`.
- `organizationalEntityShareStatistics` is organic-only, has a rolling 12-month limit, and should not be mixed with paid performance without explicit separation.
- LinkedIn versioning must be sent in request headers (`Linkedin-Version`) and older versions can be sunset. Unversioned calls are not safe defaults.
- Rate limits are endpoint-specific and not publicly enumerated as universal static values; teams must inspect Developer Portal analytics and design adaptive quota handling.
- App review and tiering gate practical access: development and standard tiers, use-case review, and screencast verification are part of real integration delivery.
- Permission scope naming and migration notes show drift across docs (`*_social` vs `*_social_feed`), so implementation should validate scopes against currently approved app scopes before rollout.
- Official and third-party endpoints must be clearly separated in reporting; wrapper APIs are provider APIs, not LinkedIn official APIs.

**Verified endpoint/method map (official):**

| Surface | Verified endpoint | Purpose | Notes |
|---|---|---|---|
| Posts | `POST /rest/posts` | Create org/member posts | Replaces legacy `ugcPosts` workflow |
| Posts finder | `GET /rest/posts?...&q=author` | Retrieve posts by author URN | Count/sort controls documented |
| Social actions | `GET /rest/socialActions/{urn}` | Aggregate likes/comments summary | Legacy + still documented |
| Reactions | `GET/POST /rest/reactions...` | Reaction read/write | Replaces likes behavior |
| Social metadata | `GET /rest/socialMetadata/{urn}` | Reaction/comment summaries | Supports comments-state controls |
| Follower statistics | `GET /rest/organizationalEntityFollowerStatistics?...` | Lifetime/time-bound follower stats | No `totalFollowerCounts` now |
| Share statistics | `GET /rest/organizationalEntityShareStatistics?...` | Org share engagement stats | Organic only, rolling 12 months |
| Network size | `GET /rest/networkSizes/urn:li:organization:{id}?edgeType=COMPANY_FOLLOWED_BY_MEMBER` | Total follower size | EdgeType migration nuance by version |
| Org ACLs | `GET /rest/organizationAcls?...` | Role/access checks | Needed before role-gated operations |

**Sources:**
- [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2025-10)
- [Content API migration guide](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/contentapi-migration-guide?view=li-lms-2025-10)
- [Social Actions API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/network-update-social-actions?view=li-lms-2025-10)
- [Reactions API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/reactions-api?view=li-lms-2025-09)
- [Social Metadata API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/social-metadata-api?view=li-lms-2025-09)
- [Organization Follower Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/follower-statistics?view=li-lms-2026-01)
- [Organization Share Statistics](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/share-statistics?view=li-lms-2025-11)
- [Organization Lookup API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/organizations/organization-lookup-api?view=li-lms-2025-10)
- [LinkedIn API rate limits](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits)
- [LinkedIn Marketing API versioning](https://learn.microsoft.com/en-us/linkedin/marketing/versioning?view=li-lms-2025-10)
- [Marketing API access tiers](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers?view=li-lms-2024-11)
- [Community Management App Review](https://learn.microsoft.com/en-us/linkedin/marketing/community-management-app-review)

---

## Synthesis

The most important synthesis point is that professional-network signal quality depends less on "more data" and more on denominator discipline plus API reality. The same organization can look strong or weak depending on whether you compare by impressions, followers, or raw engagement counts. A reliable skill must force denominator labeling and avoid mixed-metric verdicts.

The second clear pattern is access and integration governance. In 2024-2026, LinkedIn documentation is explicit on versioned calls, endpoint-specific limits, and restricted data use. This means a technically elegant scoring system can still fail operationally if it ignores tier/scopes, version headers, or retention boundaries. Robust `SKILL.md` guidance needs to define both analysis logic and collection legality.

The third pattern is methodological: comments and video are no longer optional side signals. Official business updates and benchmark studies both indicate stronger conversation and video momentum, so theme classification should explicitly track comment-intensity and format mix. Post frequency alone is insufficient as a market-priority proxy.

The biggest contradiction to preserve (not hide) is that benchmark thresholds vary across reports due to metric definitions, cohort windows, and sampling methods. The right implementation response is confidence tiering and explicit source/denominator metadata, not forced numeric agreement.

Overall, the skill should evolve from "collect posts, likes, followers" into a controlled evidence pipeline: verify auth/access, gather segmented windows, normalize metrics, classify with explicit confidence, and publish limitations that tell the user what remains uncertain.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item has corresponding draft content below.

- [x] Replace current methodology bullets with a staged workflow that includes lag handling, fixed windows, and denominator normalization.
- [x] Add a strict evidence contract that separates metric classes (`observed`, `estimated`, `derived`) and disallows denominator mixing.
- [x] Expand tool usage guidance to include required call sequencing, auth preflight, and fallback behavior using only existing connector methods.
- [x] Add API reality notes: version header expectations, scope/tier constraints, and "official vs wrapper" distinctions.
- [x] Add interpretation defaults with benchmark-anchored thresholds and explicit confidence downgrade rules.
- [x] Add named anti-pattern warning blocks with detection signal, consequence, and mitigation steps.
- [x] Add compliance and retention guardrails for member-level data and restricted use-cases.
- [x] Expand `result_state` and confidence policy to handle contradictions, sparse data, and technical access failures.
- [x] Expand artifact schema with evidence provenance, denominator metadata, contradiction records, and benchmark context.
- [x] Add an output-quality checklist that must pass before `write_artifact`.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, this provides paste-ready text to include in `SKILL.md`.

### Draft: Core operating principle and evidence contract

---
You are detecting organization-level professional network signals on LinkedIn for one company set or one industry topic per run.

Your primary rule is **evidence fidelity before conclusion strength**. If metric definitions are mixed or source constraints are unclear, you must reduce confidence and explicitly state limitations.

Before writing any signal, label every evidence item with:
- `metric_denominator`: one of `impressions`, `followers`, `raw_count`, `time_normalized_rate`.
- `data_class`: one of `observed`, `estimated`, `derived`.
- `source_surface`: one of `linkedin_page_analytics`, `linkedin_api`, `third_party_platform`.

You must never compare unlike denominators in the same verdict sentence. If you need cross-metric context, first normalize and then state the transformation rule.

You must treat all "impressions" and "members reached" values as estimates unless the source explicitly says otherwise.

If you cannot verify auth/access tier or method availability, return `result_state: auth_required` or `result_state: technical_failure` instead of inventing data.
---

### Draft: Methodology workflow (collection -> normalization -> classification -> verdict)

---
### Methodology

Run this exact sequence every time:

1. **Preflight and scope lock**
   - Confirm one run scope only: one company set OR one industry topic.
   - Call `linkedin(op="status")` first.
   - If status indicates disconnected/auth required, stop collection and return a clear auth instruction.
   - Record run constraints up front: time window, organization list, and any unavailable modules.

2. **Collect organization post evidence**
   - For each organization, retrieve recent posts via `linkedin.organization.posts.list.v1`.
   - Keep a consistent operating window (`last 30 days`) and at least one baseline context window (`last 90-365 days`) when available.
   - Tag each post by topic theme and post format before performance comparison.
   - Do not score cross-format performance without normalization.

3. **Collect engagement quality evidence**
   - Pull post-level social actions via `linkedin.organization.social_actions.list.v1`.
   - Prioritize comments and repost dynamics for debate/interest quality, not reactions alone.
   - When possible, compute per-1k-impressions style rates from available fields rather than using raw totals.

4. **Collect follower momentum evidence**
   - Pull follower stats via `linkedin.organization.followers.stats.v1`.
   - Evaluate momentum as change-rate against the organization's own trailing baseline and peer size-tier context.
   - Do not treat absolute follower additions as comparable across differently sized pages.

5. **Apply lag and stability guard**
   - LinkedIn notes that many content metrics can lag up to 48 hours. Treat the freshest 48h as provisional unless only comments/reactions are being inspected.
   - Require signal persistence across at least two snapshots before labeling `strong`.

6. **Classify signals**
   - `topic_priority`: recurring topic appears across multiple orgs and meets normalized engagement quality expectations.
   - `pain_acknowledgment`: pain/problem language appears and attracts above-baseline discussion quality.
   - `momentum_growth` / `momentum_decline`: follower and engagement trend move coherently across windows.
   - `low_engagement`: evidence is broadly weak after normalization and lag handling.

7. **Write verdict with uncertainty**
   - If metrics conflict by denominator or window, include contradiction entry and downgrade confidence.
   - If data is sparse or gated, use `insufficient_data` instead of overconfident narrative.

Decision defaults:
- Strong signal requires agreement across at least two independent dimensions (e.g., topic recurrence + engagement quality, or follower momentum + discussion depth).
- One-outlier-post runs cannot produce `strong`.
- If only one organization has usable data, cap confidence at medium and state representativeness limits.
---

### Draft: Available Tools section text (verified methods only)

---
## Available Tools

Use only verified connector methods. Do not invent method IDs. If uncertain, call `linkedin(op="help")` first and work only with listed methods.

```python
linkedin(op="status")
linkedin(op="help")

linkedin(
  op="call",
  args={
    "method_id": "linkedin.organization.posts.list.v1",
    "organizationId": "urn:li:organization:12345",
    "count": 20
  }
)

linkedin(
  op="call",
  args={
    "method_id": "linkedin.organization.social_actions.list.v1",
    "activityId": "urn:li:activity:12345"
  }
)

linkedin(
  op="call",
  args={
    "method_id": "linkedin.organization.followers.stats.v1",
    "organizationId": "urn:li:organization:12345"
  }
)
```

Call sequencing:
1. `status` -> verify auth/connection.
2. posts list -> build post/topic universe.
3. social actions -> enrich quality metrics.
4. follower stats -> momentum context.
5. If any step fails, continue with available steps but downgrade confidence and write explicit `limitations`.

Fallback behavior:
- If `status` is auth-required: stop and request LinkedIn reconnection.
- If posts are available but social actions fail: allow weak/moderate topic inference only.
- If follower stats fail: block momentum labels and add `next_checks` item.
---

### Draft: API reality notes for implementation safety

---
### API and access reality (must-follow)

Even when connector methods abstract endpoint details, your reasoning must align with LinkedIn API realities:

- LinkedIn Marketing APIs are versioned and require a `Linkedin-Version` header in direct integrations.
- Endpoint limits are endpoint-specific and discovered in Developer Portal analytics, not from one global hardcoded number.
- Organization analytics endpoints and permissions are role/scoped. If role/scope preconditions are not met, do not infer from partial failures.
- Official API endpoints and third-party wrappers are not equivalent evidence classes. If wrapper output is used in future connector versions, mark it `source_surface: third_party_platform`.
- Keep migration awareness in notes: docs contain legacy/new overlap (`socialActions` plus `reactions`/`socialMetadata`). Do not assume one page implies immediate global deprecation.
---

### Draft: Interpretation rules and confidence policy

---
### Signal interpretation rules

Use these metric interpretation defaults:

1. **Denominator discipline**
   - Engagement by impressions evaluates content quality per exposure.
   - Engagement by followers evaluates audience-normalized interaction.
   - Raw interactions are volume indicators, not quality indicators.
   - Never compare these as interchangeable.

2. **Window discipline**
   - Use at least one operating window (30d) and one baseline window (90d+ when available).
   - Treat freshest 48h non-comment/non-reaction metrics as provisional.

3. **Format normalization**
   - Compare theme performance inside the same format first (video vs video, document vs document).
   - Cross-format theme conclusions require explicit normalization note.

4. **Momentum discipline**
   - Follower momentum requires relative context (size tier or own historical baseline).
   - Absolute follower gains are not enough.

5. **Conversation quality**
   - Weight comments/reposts more than raw reactions when assessing depth of interest.
   - A reaction-only spike with flat comments is weaker evidence than a comment-led increase.

Confidence scoring defaults:
- Start at `0.50`.
- +0.10 if denominator consistency is preserved.
- +0.10 if 30d and baseline windows both available.
- +0.10 if at least two organizations show aligned direction.
- +0.10 if at least two dimensions agree (theme + engagement or momentum + discussion).
- -0.10 for each unresolved contradiction.
- -0.15 if core module missing (posts or social actions).
- -0.10 if data is within lag/provisional window.

Confidence grade mapping:
- `high`: 0.80-1.00
- `medium`: 0.60-0.79
- `low`: 0.40-0.59
- `insufficient`: <0.40
---

### Draft: Anti-pattern warning blocks

---
### WARNING: Denominator Mixing
**What it looks like:** You compare impression-based and follower-based engagement as if they were the same metric.  
**Detection signal:** Verdict text uses one "engagement trend" claim but cites mismatched formulas.  
**Consequence:** False direction calls and bad prioritization.  
**Mitigation:** Label denominator per metric, compare like-for-like, and include normalization note for cross-metric context.

### WARNING: Freshness Illusion
**What it looks like:** You call winners/losers from the newest 24-48h slice.  
**Detection signal:** Strong verdict references only latest partial window.  
**Consequence:** Noise-driven decisions.  
**Mitigation:** Apply D-2 guard, require persistence across snapshots, downgrade confidence when provisional.

### WARNING: Vanity Engagement Trap
**What it looks like:** High reactions are treated as strong demand without discussion depth.  
**Detection signal:** Reactions spike while comments/reposts remain flat, yet output says "strong market pull."  
**Consequence:** Inflated confidence and false topic prioritization.  
**Mitigation:** Require conversation-quality co-signal before strong label.

### WARNING: Plan-Tier Blindness
**What it looks like:** Missing analytics modules are interpreted as no signal.  
**Detection signal:** No mention of free vs premium feature availability in limitations.  
**Consequence:** False negatives due to entitlement gaps.  
**Mitigation:** Record subscription/tier context and mark unavailable surfaces explicitly.

### WARNING: Noncompliant Data Use
**What it looks like:** Member-level social activity is exported/combined into CRM or lead enrichment.  
**Detection signal:** Artifact or downstream note references member data transfer to sales/recruiting workflows.  
**Consequence:** Terms breach and potential API suspension.  
**Mitigation:** Enforce purpose-limited use, no prohibited transfer/combining, retention controls by field type.
---

### Draft: Compliance and data retention guardrails

---
### Compliance guardrails (required)

Before any run:
- Confirm collection method is approved API access, not UI scraping or unapproved automation.
- Confirm use-case stays within allowed page/profile management and analytics boundaries.

Data-handling constraints:
- Treat member-level profile/activity data as restricted.
- Apply documented retention windows (for example, short caching windows for member profile/activity where applicable; longer windows for organization admin/reporting data per LinkedIn storage requirements).
- Implement deletion workflows and avoid indefinite caches of restricted fields.

Use-case restrictions:
- Do not use community management member data for advertising, sales prospecting, recruiting enrichment, CRM append, or audience list building where prohibited.
- Do not combine restricted member data with third-party datasets to build derivative profiles.

Operational behavior:
- If requested task implies restricted use, return `insufficient_data` with explicit policy limitation instead of attempting workaround collection.
---

### Draft: Result state policy

---
### Result state policy

Use these states consistently:
- `ok`: sufficient, coherent evidence; no major unresolved contradictions.
- `zero_results`: query executed correctly but returned no relevant posts/signals.
- `insufficient_data`: data exists but quality/coverage cannot support defensible verdict.
- `technical_failure`: connector/tool failure prevented analysis.
- `auth_required`: LinkedIn auth missing/expired.
- `ok_with_conflicts` (recommended addition): useful evidence exists but meaningful contradictions remain unresolved.

When contradictions exist:
- Keep useful signals if still evidence-backed.
- Add contradiction note and confidence downgrade.
- Avoid binary "signal/no-signal" claims.
---

### Draft: Schema additions

> Full JSON Schema fragment for recommended `signal_professional_network` upgrades.

```json
{
  "signal_professional_network": {
    "type": "object",
    "required": [
      "organizations",
      "time_window",
      "result_state",
      "signals",
      "confidence",
      "confidence_grade",
      "limitations",
      "next_checks",
      "evidence_summary"
    ],
    "additionalProperties": false,
    "properties": {
      "organizations": {
        "type": "array",
        "description": "LinkedIn organization URNs or names analyzed in this run.",
        "items": {
          "type": "string"
        },
        "minItems": 1
      },
      "time_window": {
        "type": "object",
        "required": [
          "start_date",
          "end_date"
        ],
        "additionalProperties": false,
        "properties": {
          "start_date": {
            "type": "string",
            "description": "ISO date (YYYY-MM-DD) for analysis start."
          },
          "end_date": {
            "type": "string",
            "description": "ISO date (YYYY-MM-DD) for analysis end."
          }
        }
      },
      "result_state": {
        "type": "string",
        "description": "Overall run outcome quality and completeness.",
        "enum": [
          "ok",
          "ok_with_conflicts",
          "zero_results",
          "insufficient_data",
          "technical_failure",
          "auth_required"
        ]
      },
      "signals": {
        "type": "array",
        "description": "Structured organization-level signals emitted by the run.",
        "items": {
          "type": "object",
          "required": [
            "signal_type",
            "description",
            "strength",
            "organization",
            "evidence",
            "metric_denominator",
            "data_class",
            "source_surface"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": [
                "topic_priority",
                "pain_acknowledgment",
                "momentum_growth",
                "momentum_decline",
                "product_launch_signal",
                "hiring_surge",
                "low_engagement",
                "conversation_depth_increase",
                "format_shift_signal"
              ],
              "description": "Signal category derived from post, engagement, and follower evidence."
            },
            "description": {
              "type": "string",
              "description": "Human-readable explanation of what changed and why it matters."
            },
            "strength": {
              "type": "string",
              "enum": [
                "strong",
                "moderate",
                "weak"
              ],
              "description": "Signal strength after quality gate checks."
            },
            "organization": {
              "type": "string",
              "description": "Organization name or URN tied to this signal."
            },
            "evidence": {
              "type": "string",
              "description": "Concise evidence snippet: post summary and/or metric fact."
            },
            "metric_denominator": {
              "type": "string",
              "enum": [
                "impressions",
                "followers",
                "raw_count",
                "time_normalized_rate"
              ],
              "description": "Metric denominator used for this signal; prevents formula mixing."
            },
            "data_class": {
              "type": "string",
              "enum": [
                "observed",
                "estimated",
                "derived"
              ],
              "description": "Evidence class for reliability context."
            },
            "source_surface": {
              "type": "string",
              "enum": [
                "linkedin_page_analytics",
                "linkedin_api",
                "third_party_platform"
              ],
              "description": "Source surface used to derive this signal."
            },
            "post_refs": {
              "type": "array",
              "description": "Optional list of post/activity references supporting this signal.",
              "items": {
                "type": "string"
              }
            },
            "metric_snapshot": {
              "type": "object",
              "description": "Optional metric payload used in this signal.",
              "required": [
                "window_label"
              ],
              "additionalProperties": false,
              "properties": {
                "window_label": {
                  "type": "string",
                  "description": "Window label such as 30d, 90d, baseline."
                },
                "engagement_rate": {
                  "type": "number",
                  "description": "Engagement rate used for this signal, if available."
                },
                "comment_count": {
                  "type": "integer",
                  "minimum": 0,
                  "description": "Comment volume supporting conversation-quality interpretation."
                },
                "follower_delta_pct": {
                  "type": "number",
                  "description": "Percent follower change for momentum inference."
                }
              }
            }
          }
        }
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Numeric confidence after consistency and contradiction checks."
      },
      "confidence_grade": {
        "type": "string",
        "enum": [
          "high",
          "medium",
          "low",
          "insufficient"
        ],
        "description": "Bucketed confidence label derived from numeric confidence."
      },
      "limitations": {
        "type": "array",
        "description": "Explicit caveats that constrain interpretation quality.",
        "items": {
          "type": "string"
        }
      },
      "next_checks": {
        "type": "array",
        "description": "Concrete follow-up checks to reduce uncertainty on next run.",
        "items": {
          "type": "string"
        }
      },
      "evidence_summary": {
        "type": "object",
        "required": [
          "organizations_covered",
          "posts_analyzed",
          "signals_emitted"
        ],
        "additionalProperties": false,
        "properties": {
          "organizations_covered": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of organizations with usable evidence."
          },
          "posts_analyzed": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of posts considered in this run."
          },
          "signals_emitted": {
            "type": "integer",
            "minimum": 0,
            "description": "Count of signals produced after filtering."
          },
          "contradictions_found": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of unresolved contradictions affecting confidence."
          }
        }
      },
      "benchmark_context": {
        "type": "object",
        "additionalProperties": false,
        "description": "Optional benchmark references used for thresholding this run.",
        "properties": {
          "engagement_baseline_note": {
            "type": "string",
            "description": "Text note about benchmark denominator and source."
          },
          "follower_growth_baseline_note": {
            "type": "string",
            "description": "Text note about follower growth baseline and size-tier context."
          }
        }
      },
      "contradictions": {
        "type": "array",
        "description": "Optional explicit source/metric conflicts that remain unresolved.",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "conflict_note",
            "impact_on_confidence"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string",
              "description": "Conflict topic, e.g. denominator mismatch or window mismatch."
            },
            "conflict_note": {
              "type": "string",
              "description": "What conflicts and why it cannot be resolved in current run."
            },
            "impact_on_confidence": {
              "type": "string",
              "enum": [
                "minor",
                "moderate",
                "major"
              ],
              "description": "Severity of this conflict's impact on confidence."
            }
          }
        }
      }
    }
  }
}
```

### Draft: Recording and pre-write checklist

---
### Recording

After completing analysis, call:

```python
write_artifact(
  artifact_type="signal_professional_network",
  path="/signals/professional-network-{YYYY-MM-DD}",
  data={...}
)
```

Before writing the artifact, verify all of the following:

1. You ran `linkedin(op="status")` and handled auth state correctly.
2. You used consistent denominator labels for every emitted signal.
3. You did not assign `strong` based on a single post or single source.
4. You applied lag guard for freshest non-comment/non-reaction metrics.
5. You recorded plan/tier or module availability limits where relevant.
6. You included contradictions when metrics disagree.
7. `result_state`, `confidence`, and `confidence_grade` are internally consistent.
8. `limitations` and `next_checks` are concrete (no generic filler).

If any check fails, downgrade confidence and keep the run transparent instead of overfitting a narrative.
---

## Gaps & Uncertainties

- LinkedIn documentation exposes some overlapping or migrating social endpoint surfaces (`socialActions` and newer reaction/metadata surfaces), but exact connector implementation mapping can differ by app scope and migration state.
- Public benchmark reports differ by cohort and denominator definitions, so absolute cross-report thresholds are not universally portable. The skill should keep defaults tunable.
- Third-party platform capabilities and pricing/limits are frequently plan- and contract-dependent; behavior should be re-validated during implementation, not assumed from marketing pages.
- Several API/legal rules are intentionally broad (e.g., restricted use language), so edge-case legal interpretation may require counsel for production deployments.
- Some foundational feed-quality sources are evergreen rather than 2024-2026 publications; they are used as conceptual support, not sole evidence for current numeric thresholds.
