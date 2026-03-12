# Research: signal-social-community

**Skill path:** `flexus_simple_bots/researcher/skills/signal-social-community/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`signal-social-community` detects social/community signals for one query scope per run: sentiment direction, velocity bursts, narrative drift, pain language, and launch interest across Reddit, X, YouTube, TikTok, Product Hunt, Instagram, and Pinterest.

This research was produced from template + brief + skill context, using five internal sub-research angles (methodology, tools/APIs, interpretation, anti-patterns, governance). The target is a safer `SKILL.md`: evidence-first, policy-aware, contradiction-explicit, and free of invented methods/endpoints.

---

## Definition of Done

- [x] At least 4 distinct research angles are covered
- [x] Each finding has source URLs or named references
- [x] Methodology includes practical execution rules
- [x] Tool/API landscape includes concrete options and caveats
- [x] Failure modes and anti-patterns are explicit
- [x] Schema recommendations map to realistic data shapes
- [x] Gaps/uncertainties are explicit
- [x] Findings prioritize 2024-2026 (evergreen marked when used)

---

## Quality Gates

- No generic filler without backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions are explicit: **passed**
- Draft content is the largest section: **passed**
- Internal sub-research angles >= 4: **passed** (5 used)

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices

**Findings:**

- Strong workflows are staged: scope lock -> collect -> qualify -> authenticity checks -> corroborate -> classify -> record.
- Platform eligibility/policy now materially affects methodology quality (especially Reddit, TikTok research surfaces, and Meta research tools).
- X engagement observability changed in 2024 (likes visibility), so reply/repost/quote and count trends matter more for inference.
- YouTube quota asymmetry forces sparse discovery and focused enrichment.
- TikTok research should be interpreted with freshness caution (provisional vs finalized reads).
- Cross-platform metric semantics are non-equivalent; normalization is required before comparison.
- Policy/moderation regime changes should be treated as trend-break candidates.

**Sources:**
- [Reddit Developer Terms (2024)](https://redditinc.com/policies/developer-terms)
- [X API rate limits](https://docs.x.com/x-api/fundamentals/rate-limits)
- [AP: X hid public likes (2024)](https://apnews.com/article/x-twitter-hides-likes-social-media-29d40153597220bd05afa6221f658c92)
- [YouTube quota costs](https://developers.google.com/youtube/v3/determine_quota_cost)
- [TikTok Research API](https://developers.tiktok.com/products/research-api/)
- [TikTok Research API FAQ](https://developers.tiktok.com/doc/research-api-faq)
- [Meta Content Library and API](https://transparency.meta.com/researchtools/meta-content-library/)

---

### Angle 2: Tool & API Landscape

**Findings:**

- Practical stack: native platform APIs for precision + optional listening suites for operational breadth.
- X, YouTube, and TikTok each have materially different throughput/access constraints.
- Product Hunt is GraphQL-first and complexity-budgeted.
- Instagram hashtag/media surfaces are permission-gated.
- Reddit access is policy-bound and should use current docs/runtime headers over legacy assumptions.
- Third-party suites (Brandwatch/Sprout/Meltwater/Talkwalker) are useful but must expose provenance/completeness metadata.

| Provider | Verified surface examples | Typical caveat |
|---|---|---|
| X API v2 | `GET /2/tweets/search/recent`, `GET /2/tweets/counts/recent` | tier/endpoint windows |
| YouTube Data API | `search.list`, `videos.list`, `commentThreads.list` | quota asymmetry |
| TikTok Research API | `POST /v2/research/video/query/`, `POST /v2/research/video/comment/list/` | access + lag |
| Product Hunt API | `POST /v2/api/graphql` | complexity windows |
| Instagram Graph API | `ig_hashtag_search`, hashtag media edges | permissions |
| Reddit Data API | OAuth-based documented surfaces | policy/rate constraints |

**Sources:**
- [X recent search quickstart](https://docs.x.com/x-api/posts/search/quickstart/recent-search)
- [YouTube `search.list`](https://developers.google.com/youtube/v3/docs/search/list)
- [YouTube `videos.list`](https://developers.google.com/youtube/v3/docs/videos/list)
- [YouTube `commentThreads.list`](https://developers.google.com/youtube/v3/docs/commentThreads/list)
- [TikTok query videos docs](https://developers.tiktok.com/doc/research-api-specs-query-videos/)
- [TikTok query comments docs](https://developers.tiktok.com/doc/research-api-specs-query-video-comments/)
- [Product Hunt API docs](https://api.producthunt.com/v2/docs)
- [Instagram hashtag search reference](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search/)
- [Reddit Data API Wiki](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki)

---

### Angle 3: Data Interpretation & Signal Quality

**Findings:**

- Integrity checks should precede sentiment/velocity interpretation.
- Single-window spikes are hypotheses, not trend confirmation.
- Cross-platform claims require within-platform normalization first.
- Contradictions should be preserved and confidence-adjusted, not hidden.
- Reach/likes/follower growth are weak alone; stronger claims need corroboration and authenticity checks.
- Non-probability sampling caveats should be explicit in output.

**Common misreads to block:**

- "High reach means support."
- "Follower growth proves demand."
- "No detected bots means clean data."
- "Cross-platform engagement rates are directly comparable."

**Sources:**
- [Meta inauthentic behavior policy](https://transparency.meta.com/policies/community-standards/inauthentic-behavior/)
- [Meta Q4 2024 adversarial report](https://transparency.meta.com/sr/Q4-2024-Adversarial-threat-report/)
- [TikTok integrity and authenticity guideline](https://www.tiktok.com/community-guidelines/en/integrity-authenticity/)
- [YouTube fake engagement policy](https://support.google.com/youtube/answer/3399767)
- [AAPOR margin of error explainer](https://aapor.org/wp-content/uploads/2023/01/Margin-of-Sampling-Error-508.pdf)
- [Reuters Digital News Report 2024](https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2024/dnr-executive-summary)
- [Ofcom Online Nation 2024](https://www.ofcom.org.uk/siteassets/resources/documents/research-and-data/online-research/online-nation/2024/online-nation-2024-report.pdf?v=386238)

---

### Angle 4: Failure Modes & Anti-Patterns

**Findings:**

- Astroturfed velocity mistaken for demand
- Amplification rings treated as consensus
- Single-platform monoculture
- Engagement-bait interpreted as intent
- Rate-limit truncation treated as complete data
- Ingest-lag confusion
- Snapshot non-reproducibility (no query/provenance ledger)
- Sentiment portability errors across languages/domains
- Policy-last implementation

**Sources:**
- [FTC fake reviews rule (2024)](https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials)
- [Federal Register final rule text (2024)](https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials)
- [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms)
- [TikTok Research API FAQ](https://developers.tiktok.com/doc/research-api-faq)
- [Scientific Reports coordinated sharing (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12053595/)

---

### Angle 5+: Governance, Compliance, and Regime Shifts

**Findings:**

- Policy/terms drift should be assumed and periodically revalidated.
- Public availability does not remove privacy/proportionality obligations.
- Research access paths are role/scope constrained and should be metadata in outputs.
- Enforcement metrics and user-trust outcomes can diverge and should be reported separately when possible.
- Missing authorized access should reduce confidence, not trigger unofficial fallback collection.

**Sources:**
- [Meta Platform Terms (2026)](https://developers.facebook.com/terms/dfc_platform_terms/)
- [YouTube API Services ToS revision history](https://developers.google.com/youtube/terms/revision-history)
- [EU AI Act enters force (2024)](https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en)
- [EDPB Opinion 28/2024](https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en)
- [DSA delegated act researcher data access (2025)](https://digital-strategy.ec.europa.eu/en/news/commission-adopts-delegated-act-data-access-under-digital-services-act)

---

## Synthesis

The strongest cross-source signal is procedural: reliable social/community detection now depends on quality gates, not just data volume. Teams reduce false confidence by explicitly tracking coverage, authenticity risk, contradictions, and policy constraints.

For this skill, the most important upgrades are a staged method, strict internal method-ID discipline, contradiction logging, anti-pattern warnings, and a richer output schema that encodes uncertainty and provenance.

---

## Recommendations for SKILL.md

- [x] Replace loose flow with staged evidence pipeline
- [x] Add hard gates for `strong` classification
- [x] Keep examples on existing internal method IDs only
- [x] Add coverage/freshness accounting and confidence penalties
- [x] Add contradiction protocol
- [x] Add anti-pattern warning blocks
- [x] Add compliance/policy-drift guardrails
- [x] Expand schema for provenance and confidence decomposition
- [x] Add pre-`write_artifact` quality checklist

---

## Draft Content for SKILL.md

### Draft: Core mode and evidence contract

Use evidence-first execution. You must not emit a strong signal when relevance is unclear, authenticity risk is high, key platform coverage is partial/failed, or major contradictions are unresolved.

Tag each evidence item with `source_type`, `freshness_state`, `coverage_state`, and `authenticity_risk`. If quality is constrained, downgrade strength/confidence explicitly.

### Draft: Methodology sequence

Run in order:
1. Scope lock (`query`, `region`, `language`, `time_window`)
2. Collection plan by platform role
3. Collection execution with explicit error logging
4. Relevance filtering (remove collisions/hijacks/off-topic)
5. Authenticity checks (repetition/synchronization/concentration)
6. Cross-platform corroboration (`weak`, `moderate`, `strong`)
7. Contradiction logging with confidence impact
8. Result-state assignment and artifact write

Hard stops:
- policy-blocked key data with no compliant fallback
- missing evidence refs for core claims
- unresolved high authenticity risk on core narrative

### Draft: Available Tools (existing internal method IDs only)

```python
reddit(op="call", args={"method_id": "reddit.search.posts.v1", "q": "your query", "sort": "relevance", "t": "month"})
reddit(op="call", args={"method_id": "reddit.subreddit.hot.v1", "subreddit": "relevant_subreddit"})
reddit(op="call", args={"method_id": "reddit.subreddit.new.v1", "subreddit": "relevant_subreddit"})
x(op="call", args={"method_id": "x.tweets.counts_recent.v1", "query": "your query", "granularity": "day"})
x(op="call", args={"method_id": "x.tweets.search_recent.v1", "query": "your query", "max_results": 100})
youtube(op="call", args={"method_id": "youtube.search.list.v1", "q": "your query", "type": "video", "order": "viewCount"})
youtube(op="call", args={"method_id": "youtube.videos.list.v1", "id": "video_id", "part": "statistics,snippet"})
youtube(op="call", args={"method_id": "youtube.comment_threads.list.v1", "videoId": "video_id"})
tiktok(op="call", args={"method_id": "tiktok.research.video_query.v1", "query": {"and": [{"field_name": "keyword", "filter_value": "your query"}]}})
producthunt(op="call", args={"method_id": "producthunt.graphql.posts.v1", "topic": "relevant-topic", "first": 20})
instagram(op="call", args={"method_id": "instagram.hashtag.recent_media.v1", "hashtag": "yourhashtag"})
pinterest(op="call", args={"method_id": "pinterest.trends.keywords_top.v1", "region": "US", "interests": ["your-interest"]})
```

### Draft: Classification and confidence policy

- `weak`: single-platform, sparse refs, unresolved integrity issues, or one-window spike
- `moderate`: >=2 independent platforms align; integrity acceptable
- `strong`: corroboration + persistence + acceptable authenticity risk + no unresolved major conflict

Confidence starts at `0.50`.

Adjust by:
- `+0.10` relevance quality high
- `+0.10` corroboration >=2
- `+0.10` persistence across windows
- `+0.10` low authenticity risk
- `-0.10` each unresolved major contradiction
- `-0.10` each key-platform partial/failed coverage
- `-0.10` key evidence still provisional

Caps:
- single-platform max `0.60`
- major coverage constraints max `0.75`
- unresolved high authenticity risk max `0.65`

### Draft: Anti-pattern warning blocks

- Single-platform overclaim
- Coverage illusion
- Rate-limit blindness
- Freshness mislabel
- Authenticity neglect
- Engagement-bait fallacy
- Snapshot non-reproducibility
- Cross-platform metric conflation
- Sentiment portability
- Policy-last execution

For each warning include: detection signal, consequence, and exact mitigation.

### Draft: Recording block

```python
write_artifact(
  artifact_type="signal_social_community",
  path="/signals/social-community-{YYYY-MM-DD}",
  data={...}
)
```

One artifact per query scope per run. Do not output raw JSON in chat.

Before write, require:
- relevance checks complete
- platform coverage/freshness complete
- authenticity risk assessed
- contradictions logged
- confidence + components consistent
- limitations + next checks concrete

### Draft: Schema additions (compact)

```json
{
  "signal_social_community": {
    "type": "object",
    "required": ["query", "time_window", "result_state", "platform_coverage", "signals", "confidence", "confidence_grade", "confidence_components", "limitations", "contradictions", "next_checks"],
    "additionalProperties": false
  }
}
```

---

## Gaps & Uncertainties

- Platform limits and terms are tier/version specific and change over time.
- Cross-platform metric comparability remains structurally limited.
- Bot/coordinated-behavior thresholds are context dependent.
- Some references are operational studies, not formal standards.
- This is operational research guidance, not legal advice.
