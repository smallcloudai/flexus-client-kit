# Research: signal-news-events

**Skill path:** `flexus_simple_bots/researcher/skills/signal-news-events/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`signal-news-events` detects news/event momentum for one query scope per run.

The existing skill has good provider coverage but needs stronger quality gates: dedupe, corroboration, degraded-mode handling, contradiction logging, and provenance.

This research was produced from template + brief + skill context, using five internal sub-research angles.

---

## Definition of Done

- [x] At least 4 distinct research angles are covered
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to
- [x] Tool/API landscape maps at least 3-5 options
- [x] At least one failure mode is documented
- [x] Schema recommendations are grounded in real data shapes
- [x] Gaps section lists uncertainty honestly
- [x] Findings are 2024-2026 or explicitly evergreen

---

## Quality Gates

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources noted explicitly: **passed**
- Findings volume target met: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices

**Findings:**

Mature workflows are staged: collect -> dedupe -> corroborate -> interpret -> verdict. Raw article count alone is not a valid signal. 2025 EIOS evaluations reinforce measuring monitoring quality with detection/timeliness, not just volume.

Google Trends and Wikimedia pageviews are useful confirmation layers, but both are non-absolute proxies (normalized/sampled trend index; pageview traffic-class semantics). Platform reach and trust can diverge, so reach and credibility should be scored separately.

**Sources:**
- https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-025-21998-9
- https://iris.who.int/server/api/core/bitstreams/f2febe97-8fcc-47d7-9019-2285d74fa4ce/content
- https://support.google.com/trends/answer/4365533?hl=en
- https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html
- https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2025/dnr-executive-summary
- https://www.ap.org/verify

---

### Angle 2: Tool & API Landscape

**Findings:**

A practical stack combines broad feed + event clustering + attention proxy.

| Provider | Verified endpoint/method | Typical role |
| --- | --- | --- |
| GDELT DOC 2.0 | `GET https://api.gdeltproject.org/api/v2/doc/doc` | High-breadth global scan |
| Event Registry | `GET /api/v1/article/getArticles`, `GET /api/v1/event/getEvents` | Event clustering and aggregation |
| NewsAPI | `GET /v2/everything`, `GET /v2/top-headlines` | Broad retrieval |
| GNews | `GET /api/v4/search`, `GET /api/v4/top-headlines` | Independent corroboration |
| NewsData.io | `GET /api/1/latest`, `GET /api/1/archive`, `GET /api/1/count` | Breadth + archive |
| Newscatcher v3 | `POST /api/search`, `POST /api/latest_headlines` | Rich filtered retrieval |
| Wikimedia AQS | `GET /metrics/pageviews/per-article/...` | Public-interest confirmation |

Perigon is available in current skill tooling, but endpoint-level public docs were less transparent in this pass.

**Sources:**
- https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- https://eventregistry.org/static/api.yaml
- https://newsapi.org/docs/endpoints/everything
- https://newsapi.org/docs/endpoints/top-headlines
- https://docs.gnews.io/endpoints/search-endpoint
- https://docs.gnews.io/endpoints/top-headlines-endpoint
- https://newsdata.io/documentation
- https://www.newscatcherapi.com/docs/v3/api-reference/endpoints/search/search-articles-post
- https://www.newscatcherapi.com/docs/v3/api-reference/overview/rate-limits
- https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits

---

### Angle 3: Data Interpretation & Signal Quality

**Findings:**

Interpretation failures dominate production errors. Relative trend movement and raw counts are not interchangeable. Always inspect raw + deduped counts and require persistence checks (`7d`, `30d`, `90d`). Source independence matters more than outlet count because syndication inflates naive volume.

**Common misreads:**
- "Trend up" means absolute demand up.
- Many articles means many independent confirmations.
- Coverage down means true decline (may be quota/truncation).

**Sources:**
- https://blog.gdeltproject.org/gdelt-2-0-api-now-supports-raw-result-counts/
- https://blog.gdeltproject.org/gcp-timeseries-api-explorations-time-horizons-trending-versus-breaking-news/
- https://help.eventregistry.org/media-monitoring-hiding-article-duplicates/
- https://aclanthology.org/2024.findings-emnlp.275/

---

### Angle 4: Failure Modes & Anti-Patterns

**Findings:**

Key anti-patterns: duplicate inflation, single-provider certainty, PR-wave contamination, rate-limit blindness, stale recirculation, virality-as-truth, AI-summary substitution, timezone drift.

**Anti-pattern template for skill:** what it looks like -> detection signal -> consequence -> exact mitigation.

**Sources:**
- https://help.eventregistry.org/media-monitoring-hiding-article-duplicates/
- https://www.newscatcherapi.com/docs/v3/documentation/guides-and-concepts/articles-deduplication
- https://newsapi.org/docs/errors
- https://docs.gnews.io/error-handling
- https://www.reuters.com/fact-check/old-video-istanbul-protest-shared-new-following-may-26-rafah-strike-2024-05-31/
- https://www.reuters.com/world/uk/pm-starmer-warns-social-media-firms-after-southport-misinformation-fuels-uk-2024-08-01/
- https://www.bbc.com/news/articles/cd0elzk24dno

---

### Angle 5+: Integration, Governance, and Compliance

**Findings:**

Provider terms and collection constraints can invalidate otherwise correct technical outputs; governance uncertainty must be explicit in artifacts. Major collection degradation should force `insufficient_data` over directional claims.

Provenance fields are mandatory for reproducibility: query hash, provider/method, retrieval time, source link, and collection notes.

**Sources:**
- https://newsapi.org/terms
- https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy
- https://raw.githubusercontent.com/cloudevents/spec/v1.0/spec.md
- https://www.w3.org/TR/prov-dm/
- https://c2pa.org/specifications/specifications/2.0/specs/C2PA_Specification.html
- https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en
- https://www.edpb.europa.eu/news/news/2024/edpb-opinion-ai-models-gdpr-principles-support-responsible-ai_en

---

## Synthesis

Reliable news-event signaling is a quality-gated inference problem, not a feed-retrieval problem. Tooling is mature, but provider constraints make infrastructure state part of analytical state.

Best outcomes come from enforcing: dedupe, independent corroboration, persistence checks, contradiction logging, and explicit degraded-mode behavior.

---

## Recommendations for SKILL.md

- [x] Add strict staged pipeline (`collect -> dedupe -> corroborate -> score -> verdict`)
- [x] Add hard gates before `strong` classification
- [x] Add provider-run telemetry + degraded-mode handling
- [x] Expand tools guidance with verified endpoint behavior and fallback order
- [x] Add explicit interpretation rubric + confidence caps
- [x] Add named anti-pattern warning blocks
- [x] Add contradiction/uncertainty policy
- [x] Expand schema with provenance and rights uncertainty

---

## Draft Content for SKILL.md

### Draft: Core mode and quality gates

Use an evidence-first operating contract. You must not call a signal strong unless dedupe, corroboration, and collection-quality gates pass.

Before any strong claim, verify all:
1. At least two independent providers support the claim.
2. Deduped counts still support the claim.
3. Collection quality is acceptable (no unresolved major throttling/truncation).
4. Source diversity is sufficient.
5. Contradictions and unresolved assumptions are explicitly logged.

If any check fails, downgrade strength and consider `result_state=\"insufficient_data\"`.

### Draft: Methodology sequence

Run this exact sequence:
1. Scope lock (`query`, `geo_scope`, `time_window`, `event_intent`)
2. Multi-provider collection (at least 2 broad providers + at least 1 event provider)
3. Dedupe/normalize (raw vs deduped counts + source diversity)
4. Corroboration gate (`independent_provider_count >= 2`)
5. Window interpretation (`7d`, `30d`, `90d` burst vs persistence)
6. Independent attention confirmation (Wikimedia pageviews direction)
7. Quality-adjusted scoring + confidence assignment
8. Result-state assignment (`ok`, `zero_results`, `insufficient_data`, `technical_failure`)

When provider limits degrade coverage, record exact degradation and avoid directional overclaims.

### Draft: Available Tools text

```python
newsapi(op="call", args={"method_id":"newsapi.everything.v1","q":"your query","language":"en","from":"2026-02-01","sortBy":"publishedAt"})
gnews(op="call", args={"method_id":"gnews.search.v1","q":"your query","lang":"en","country":"us","max":25})
newsdata(op="call", args={"method_id":"newsdata.news.search.v1","q":"your query","language":"en"})
newscatcher(op="call", args={"method_id":"newscatcher.search.v1","q":"your query","lang":"en","page_size":100})
gdelt(op="call", args={"method_id":"gdelt.doc.search.v1","query":"your query","mode":"artlist","maxrecords":100,"timespan":"30d"})
event_registry(op="call", args={"method_id":"event_registry.article.get_articles.v1","keyword":"your query","lang":"eng","dataType":["news"],"dateStart":"2026-02-01","dateEnd":"2026-03-05"})
event_registry(op="call", args={"method_id":"event_registry.event.get_events.v1","keyword":"your query","lang":"eng"})
wikimedia(op="call", args={"method_id":"wikimedia.pageviews.per_article.v1","article":"Article_Title","project":"en.wikipedia.org","granularity":"daily","start":"2026020100","end":"2026030500"})
```

Runtime requirements:
- Never hide provider failures.
- If multiple core providers degrade, use `insufficient_data`.
- Preserve provider-level status for auditability.

### Draft: Interpretation + anti-pattern blocks

Required scoring fields:
- `article_count_raw`
- `article_count_deduped`
- `duplicate_ratio`
- `independent_provider_count`
- `unique_source_domains`

Confidence caps:
- Cap confidence at `0.80` if major contradiction is unresolved.
- Cap confidence at `0.80` if major collection degradation exists.
- Cap confidence at `0.80` if core evidence is single-provider.

Named warning blocks:
- Duplicate inflation
- Quota-induced decline
- Virality-as-truth
- AI-summary substitution

For each warning include: detection signal, consequence, and exact mitigation steps.

### Draft: Schema additions

```json
{
  "signal_news_events": {
    "type": "object",
    "required": ["query", "time_window", "result_state", "provider_runs", "signals", "confidence", "limitations", "next_checks", "provenance"],
    "additionalProperties": false,
    "properties": {
      "query": {"type": "string"},
      "time_window": {"type": "object", "required": ["start_date", "end_date"], "additionalProperties": false, "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}},
      "result_state": {"type": "string", "enum": ["ok", "zero_results", "insufficient_data", "technical_failure"]},
      "provider_runs": {"type": "array", "items": {"type": "object", "required": ["provider", "method_id", "api_status", "article_count_raw", "article_count_deduped", "degraded_mode"], "additionalProperties": false}},
      "signals": {"type": "array", "items": {"type": "object", "required": ["signal_type", "description", "strength", "evidence", "corroboration"], "additionalProperties": false}},
      "confidence": {"type": "object", "required": ["value", "band", "rationale", "unresolved_assumptions"], "additionalProperties": false},
      "limitations": {"type": "array", "items": {"type": "string"}},
      "next_checks": {"type": "array", "items": {"type": "string"}},
      "provenance": {"type": "object", "required": ["generated_at_utc", "query_hash", "api_docs_verified", "collection_notes", "rights_uncertainty"], "additionalProperties": false}
    }
  }
}
```

---

## Gaps & Uncertainties

- Provider-overlap benchmarks are sparse; dedupe thresholds remain environment-specific.
- Some docs are evergreen/undated and can drift from runtime behavior.
- Perigon endpoint details were not fully transparent via public docs in this pass.
- Attention proxies measure attention, not commercial intent.
- Governance/legal interpretation is jurisdiction-specific; this is operational guidance, not legal advice.
