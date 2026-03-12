# Research: signal-talent-tech

**Skill path:** `flexus_simple_bots/researcher/skills/signal-talent-tech/`
**Bot:** researcher
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`signal-talent-tech` detects hiring-demand and technology-adoption signals for one domain or technology per run. It is a cross-source signal skill: job postings reflect market demand intent, while developer activity reflects ecosystem momentum and implementation reality.

The current `SKILL.md` has a good high-level framing (lagging hiring + leading developer activity), but it needs stronger operational guardrails so runs are reproducible, source-safe, and resistant to common data traps. This research focuses on 2024-2026 evidence for five areas: methodology, tools/APIs, interpretation quality, anti-pattern handling, and representativeness limits.

The goal of this research is not to rewrite the skill directly. The goal is to provide enough precise draft language that a future editor can paste sections into `SKILL.md` with minimal invention and without introducing fake endpoints or unsupported confidence claims.

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

- Practitioners increasingly treat job posting counts as a directional demand-intent signal, not a literal opening count. Indeed explicitly documents that one posting can represent multiple openings and postings can remain visible after fill, so absolute counts are not vacancy truth.
- Method-first teams normalize before interpreting: index-based and seasonally adjusted series come first, then domain slicing by occupation/sector, then directional interpretation. Indeed's methodology revisions in late 2024 reinforced the need to annotate method breakpoints.
- Modern workflows separate "mention volume" from "usage-context quality." In 2025 analysis of AI mentions in postings, a meaningful share of postings had weak context, showing that keyword presence alone is not sufficient evidence of actual skill demand depth.
- Better hiring signal systems score at role/industry level before aggregate rollups. 2026 labor updates show AI-mention demand can grow while total hiring remains soft, so aggregate-only conclusions are frequently wrong.
- Talent supply estimation has shifted from title matching toward skills-overlap and observed transition feasibility. LinkedIn's 2025 skills-based hiring framework emphasizes overlap thresholds and observed transitions to reduce false-positive talent pool estimates.
- Skills-gap analysis quality improves when mismatch is weighted by skill relevance and outlier handling, not raw count difference. LinkedIn technical notes describe weighted shortage/surplus approaches that are more stable than naive demand-minus-supply.
- The most reliable talent-tech methodology in 2025-2026 is a leading+lagging stack: labor demand signals (job boards), ecosystem activity (GitHub), and practitioner community demand (Stack Overflow/Stack Exchange), with survey priors used as context not ground truth.
- Developer telemetry is operationally useful but scope-limited. Public GitHub activity is observable and timely, but it undercounts private enterprise work, so confidence should explicitly reflect public-only observability limits.
- Trend calls are increasingly gated by cross-source directional agreement, not exact metric matching. If two independent sources agree on direction and data quality checks pass, confidence can rise; if they diverge, contradiction must be recorded.
- Mature teams now publish confidence with evidence-class labels (`direct`, `sampled`, `modeled`) because mixing classes without labels causes overconfident and non-auditable outputs.

**Contradictions to preserve in skill logic:**

- Strong employer expectation for AI transformation can coexist with broad hiring weakness; domain slices may rise while totals stay flat.
- Mentions can increase while practical usage context remains weak in a non-trivial subset of postings.
- Open-source activity may indicate ecosystem momentum while missing private adoption reality.

**Sources:**

- [Indeed job postings tracker and methodology](https://hiring-lab.github.io/job_postings_tracker/)
- [Indeed data FAQ (posting vs opening caveats)](https://www.hiringlab.org/indeed-data-faq-2/)
- [Indeed AI mention context analysis (2025)](https://www.hiringlab.org/2025/10/28/how-employers-are-talking-about-ai-in-job-postings/)
- [Indeed labor update (2026)](https://www.hiringlab.org/2026/01/22/january-labor-market-update-jobs-mentioning-ai-are-growing-amid-broader-hiring-weakness/)
- [LinkedIn skills-based hiring report (2025)](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/skills-based-hiring-march-2025.pdf)
- [LinkedIn technical note: skills mismatch](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/technicalnote-skills-mismatch.pdf)
- [WEF Future of Jobs 2025](https://www.weforum.org/publications/the-future-of-jobs-report-2025/in-full/)
- [GitHub Octoverse 2025 (public activity scope caveats)](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)
- [Stack Overflow survey methodology (2025)](https://survey.stackoverflow.co/2025/methodology/)
- [ILO online labor market data representativeness (evergreen)](https://webapps.ilo.org/static/english/intserv/working-papers/wp068/index.html)

---

### Angle 2: Tool & API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

- **Adzuna** official Jobs API exposes country-scoped endpoints with query credential auth (`app_id`, `app_key`). Verified endpoint patterns include `GET /v1/api/jobs/{country}/search/{page}` and `GET /v1/api/jobs/{country}/categories`.
- **TheirStack** provides hiring + technographic endpoints under bearer auth. Verified endpoints include `POST /v1/jobs/search`, `POST /v1/companies/search`, and `POST /v1/companies/technologies`.
- **TheirStack** rate-limit guidance is explicitly documented by plan, including `429` behavior and `RateLimit-*` response headers; this enables deterministic backoff and throughput planning.
- **CoreSignal** provides jobs and company APIs with API-key auth via request header. Verified jobs endpoints include `POST /v2/job_base/search/filter`, `POST /v2/job_base/search/es_dsl`, and `GET /v2/job_base/collect/{job_id}`.
- **CoreSignal** publishes endpoint-class rate limits (for example search vs collect), which is more actionable than single global quota assumptions and should be encoded in retry policy.
- **CoreSignal** company multi-source endpoints (`/v2/company_multi_source/...`) include fields like active postings count and technologies used, useful for employer-level adoption scoring.
- **GitHub REST API** remains the most direct source for repository, issue, and issue-event telemetry (`/repos/{owner}/{repo}`, `/repos/{owner}/{repo}/issues`, `/repos/{owner}/{repo}/issues/events`), with a separate GraphQL endpoint at `POST https://api.github.com/graphql`.
- **GitHub** publishes both primary and secondary rate-limit behavior; analysis pipelines must respect point/hour and abuse protections, not only naive requests/hour assumptions.
- **Stack Exchange API v2.3** supports question and tag analytics via endpoints such as `/2.3/questions`, `/2.3/tags`, `/2.3/tags/{tags}/info`, and `/2.3/tags/{tags}/related`, with `backoff` and quota signals in wrapper metadata.
- **Wikimedia Pageviews API** provides stable pageview time-series via `GET /api/rest_v1/metrics/pageviews/per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}`.
- **Wikimedia** rate-limit documentation is partially conflicting across official pages (some guidance says no fixed hard limit while other docs describe explicit throttling and `429` behavior), so defensive client behavior is mandatory.
- De-facto 2024-2026 stack quality rule: mix job-demand source(s) + code ecosystem source(s) + Q&A activity + context proxy (for example pageviews), and never assume one API family is sufficient for robust confidence.

| Provider | Verified API surface (examples) | Auth model | Limit caveats |
|---|---|---|---|
| Adzuna | `GET /v1/api/jobs/{country}/search/{page}`, `GET /v1/api/jobs/{country}/categories` | `app_id` + `app_key` query params | Numeric hard quota not clearly published in one canonical place; treat as uncertain |
| TheirStack | `POST /v1/jobs/search`, `POST /v1/companies/search`, `POST /v1/companies/technologies` | Bearer token | Tiered rate limits; `429` + `RateLimit-*` headers |
| CoreSignal | `POST /v2/job_base/search/filter`, `POST /v2/job_base/search/es_dsl`, `GET /v2/job_base/collect/{job_id}` | `apikey` header | Endpoint-class req/sec limits documented |
| GitHub | `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/issues`, `POST https://api.github.com/graphql` | Bearer token (or unauth for low limits) | Primary + secondary limits; GraphQL points/node constraints |
| Stack Exchange | `GET /2.3/questions`, `GET /2.3/tags/{tags}/info` | Optional OAuth/app key | Per-IP throttle, daily quota, dynamic `backoff` |
| Wikimedia | `GET /api/rest_v1/metrics/pageviews/per-article/...` | No OAuth needed for basic reads | Conflicting public rate-limit docs; use conservative pacing and user-agent policy |

**Sources:**

- [Adzuna search endpoint docs](https://developer.adzuna.com/docs/search)
- [Adzuna categories endpoint docs](https://developer.adzuna.com/docs/categories)
- [Adzuna endpoints index](https://api.adzuna.com/v1/doc/Endpoints.md)
- [TheirStack API reference (jobs)](https://theirstack.com/en/docs/api-reference/jobs/search_jobs_v1)
- [TheirStack API reference (companies)](https://theirstack.com/en/docs/api-reference/companies/search_companies_v1)
- [TheirStack API reference (technographics)](https://theirstack.com/en/docs/api-reference/companies/technographics_v1)
- [TheirStack rate limits](https://theirstack.com/en/docs/api-reference/rate-limit)
- [CoreSignal authorization](https://docs.coresignal.com/api-introduction/authorization)
- [CoreSignal rate limits](https://docs.coresignal.com/api-introduction/rate-limits)
- [CoreSignal base jobs API](https://docs.coresignal.com/jobs-api/base-jobs-api)
- [CoreSignal jobs search filter endpoint](https://docs.coresignal.com/jobs-api/base-jobs-api/endpoints/search-filters)
- [CoreSignal company multi-source API](https://docs.coresignal.com/company-api/multi-source-company-api/elasticsearch-dsl)
- [GitHub REST rate limits](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api)
- [GitHub REST issues endpoint](https://docs.github.com/en/rest/issues/issues#list-repository-issues)
- [GitHub REST issue events endpoint](https://docs.github.com/en/rest/issues/events#list-issue-events-for-a-repository)
- [GitHub GraphQL rate and node limits](https://docs.github.com/en/graphql/overview/rate-limits-and-node-limits-for-the-graphql-api)
- [Stack Exchange API docs root](https://api.stackexchange.com/docs)
- [Stack Exchange throttle behavior](https://api.stackexchange.com/docs/throttle)
- [Stack Exchange questions endpoint docs](https://api.stackexchange.com/docs/questions)
- [Wikimedia analytics API docs](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/)
- [Wikimedia pageviews concept](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html)
- [Wikimedia API rate limits page](https://m.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits)

---

### Angle 3: Data Interpretation & Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

- Hiring trend interpretation should default to seasonally adjusted or at least matched-period YoY comparisons. Raw month-over-month movement is vulnerable to hiring seasonality and reporting artifacts.
- Job postings are a proxy for demand intent, not exact openings; interpretation must separate directional movement from absolute level claims.
- Methodology revisions and first-release revisions are common in labor datasets. Analysts should annotate breakpoint dates and downgrade confidence around methodological transitions.
- Geographic and occupational coverage differences can distort comparisons; confidence should be lower when comparing slices with known platform coverage imbalance.
- GitHub stars and forks are attention/structure signals, not quality verdicts. They need companion maintenance metrics (issue response time, release cadence, contributor concentration).
- Issue volume must be interpreted by issue type and workflow context, because issues contain bugs, tasks, and feature requests, not only defects.
- Contributor and activity views can be scope-limited; for example, some views are capped or branch-constrained. Output should state what part of activity is actually observed.
- Stack Exchange trend signals require synonym and taxonomy handling. Naive raw tag counts can drift because tags evolve and questions are multi-tagged.
- Leading indicators should be interpreted as turning-point direction signals, not precise level forecasts. Confidence should fall when component availability is low or data is preliminary.
- Interpretation quality improves when each signal carries provenance class and a freshness marker, and when conflicts are written as contradictions rather than averaged away.

**Common misinterpretations and corrections:**

- Misread: "Posting count +12% means openings +12%."  
  Correction: posting volume is directional demand intent; opening counts require separate validation.
- Misread: "Star spike proves production adoption spike."  
  Correction: star movement can reflect attention events; require maintenance and usage corroboration.
- Misread: "Tag count jump means immediate labor demand jump."  
  Correction: taxonomy/synonym changes and multi-tag behavior can alter counts without real demand shift.
- Misread: "Leading indicator predicts exact hiring level in six months."  
  Correction: leading indicators are directional; level forecasting needs additional modeling and uncertainty bounds.
- Misread: "One-week trend reversal means structural shift."  
  Correction: require rolling windows and revision-aware checks before directional verdict changes.

**Sources:**

- [LinkedIn hiring rate methodology (2024)](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/linkedin-hiring-rate-methodology.pdf)
- [Indeed tracker methodology and revisions](https://hiring-lab.github.io/job_postings_tracker/)
- [Indeed data FAQ (posting interpretation caveats)](https://www.hiringlab.org/indeed-data-faq/)
- [BLS JOLTS FAQ (revisions)](https://www.bls.gov/jlt/jltfaq.htm)
- [GitHub stars docs](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub forks docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks)
- [GitHub issues docs](https://docs.github.com/articles/about-issues)
- [CHAOSS issue response time metric](https://chaoss.community/kb/metric-issue-response-time)
- [CHAOSS release frequency metric](https://chaoss.community/kb/metric-release-frequency)
- [Stack Exchange tag synonym type](https://api.stackexchange.com/docs/types/tag-synonym)
- [Stack Exchange data dump / SEDE caveats (evergreen)](https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede)
- [OECD CLI FAQ (2024)](https://www.oecd.org/en/data/insights/data-explainers/2024/04/composite-leading-indicators-frequently-asked-questions.html)
- [OECD CLI methodology PDF](https://www.oecd.org/content/dam/oecd/en/data/methods/OECD-System-of-Composite-Leading-Indicators.pdf)
- [OpenSSF scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does "bad output" look like vs "good output"? Case studies of failure if available.

**Findings:**

- **Posting-to-opening conflation:** treating job board volume as literal vacancies creates pseudo-precision and broken forecasts.
  - Detection signal: dashboard claims exact open roles from posting counts without caveat.
  - Mitigation: explicitly label postings as demand intent; calibrate against official vacancy/hire datasets when possible.
- **Dedup trust fallacy:** assuming source-side dedup is perfect causes overcounting from reposts and channel duplication.
  - Detection signal: unstable unique/raw ratios and repeated near-identical posting payloads.
  - Mitigation: apply local semantic+metadata dedup and monitor dedup ratio drift.
- **Coverage bias blindness:** interpreting platform samples as full labor market representation.
  - Detection signal: unsupported claims in sectors/regions with known weak coverage.
  - Mitigation: add coverage maps, suppression rules, and confidence penalties.
- **Short-window overfitting:** reacting to weekly spikes/noise as structural trend shifts.
  - Detection signal: major recommendation swings from one short window.
  - Mitigation: require rolling windows, seasonality checks, and breakpoint annotation.
- **Popularity proxy abuse:** treating GitHub stars as direct quality/adoption truth.
  - Detection signal: tool ranking driven by stars alone.
  - Mitigation: blend with issue responsiveness, contributor health, release discipline, and security signals.
- **Q&A representativeness overreach:** treating Stack Overflow trend as whole-developer-population truth.
  - Detection signal: "market-level demand" claims from single-community data.
  - Mitigation: triangulate with postings and repository telemetry; state representativeness limitations.
- **Unsupported confidence math:** publishing precise confidence values with no calibration explanation.
  - Detection signal: confidence decimals with no uncertainty method and no downgrade rationale.
  - Mitigation: define transparent additive/penalty confidence policy and include reasons in output.
- **API truncation blindness:** silently accepting capped or partial results as complete scans.
  - Detection signal: ignored `429`, timeout, backoff, or paging truncation flags.
  - Mitigation: enforce pagination completion checks and coverage telemetry fields.
- **Public-only telemetry overgeneralization:** inferring private enterprise adoption from public OSS traces.
  - Detection signal: enterprise adoption claim with no private-source caveat.
  - Mitigation: scope label all ecosystem signals and cap confidence when only public traces exist.
- **Invented endpoint anti-pattern:** hardcoding non-existent method IDs/endpoints in skills.
  - Detection signal: method syntax not present in official docs or runtime tool help.
  - Mitigation: canonical endpoint map + runtime `op="help"` verification before calls.

**Case-like examples (2024-2026):**

- Large fake-star analyses in 2024-2025 show popularity manipulation risk in GitHub-only scoring.
- European and OECD discussions on online job-ad coverage keep emphasizing representativeness constraints despite improved timeliness.

**Sources:**

- [Indeed data FAQ](https://www.hiringlab.org/indeed-data-faq/)
- [Indeed vs public employment stats comparison (2024)](https://www.hiringlab.org/2024/09/20/comparing-indeed-data-with-public-employment-statistics/)
- [Eurostat online job advertisement rate](https://ec.europa.eu/eurostat/web/experimental-statistics/online-job-advertisement-rate)
- [OECD LEED reference on online job posting representativeness (2024)](https://ideas.repec.org/p/oec/cfeaaa/2024-01-en.html)
- [Google Trends data FAQ (evergreen)](https://support.google.com/trends/answer/4365533)
- [GitHub search API docs (timeouts and incomplete results)](https://docs.github.com/en/rest/search/search)
- [Stack Exchange throttle docs](https://api.stackexchange.com/docs/throttle)
- [Fake GitHub stars research summary (2025)](https://www.cs.cmu.edu/news/2025/fake-github-stars)
- [Fake stars paper (2024/2025)](https://arxiv.org/abs/2412.13459)
- [NIST AI evaluation uncertainty framing (2026)](https://www.nist.gov/publications/expanding-ai-evaluation-toolbox-statistical-models)

---

### Angle 5+: Representativeness, Segmentation, and Signal Transferability
> Additional domain angle: where talent-tech signals transfer well, where they break, and how to keep outputs decision-safe.

**Findings:**

- Talent-tech signals are highly segment-sensitive. Country, occupation family, and seniority segmentation can reverse aggregate conclusions.
- Signals transfer poorly across labor market structures: a metric that tracks software demand in one market can be weak in regions with different posting behaviors.
- Skills-based matching improves talent pool realism, but transition friction (credentialing, domain expertise, regulated-role constraints) prevents naive transferability.
- Public developer activity is useful for momentum detection but should be tagged as "ecosystem-visible" rather than "market-total."
- Survey-based developer indicators provide directional context but carry recruitment and channel bias; they should influence priors, not final verdict alone.
- The most resilient output format is dual-layer: (1) signal statement and (2) representativeness caveat. This preserves usability while preventing overclaiming.
- Confidence should be explicitly capped when a run lacks cross-segment corroboration (for example one geography + one channel only).
- A "next_checks" field is essential for transferability risk reduction: it forces concrete follow-up data collection instead of false certainty.

**Sources:**

- [WEF Future of Jobs 2025](https://www.weforum.org/publications/the-future-of-jobs-report-2025/in-full/)
- [LinkedIn skills-based hiring (2025)](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/skills-based-hiring-march-2025.pdf)
- [LinkedIn technical note: skills mismatch](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/technicalnote-skills-mismatch.pdf)
- [Stack Overflow methodology (2025)](https://survey.stackoverflow.co/2025/methodology/)
- [Indeed tracker methodology and caveats](https://hiring-lab.github.io/job_postings_tracker/)
- [ILO online labor market data representativeness (evergreen)](https://webapps.ilo.org/static/english/intserv/working-papers/wp068/index.html)

---

## Synthesis

The strongest pattern across sources is that talent-tech signaling quality depends more on measurement discipline than on any single provider. Job posting data remains a high-value demand indicator, but it is not vacancy truth and can mislead when interpreted without seasonality, dedup, and coverage context. At the same time, developer telemetry is a useful leading indicator for ecosystem momentum, but it is public-surface-biased and cannot stand in for full enterprise adoption.

Tooling has matured into a practical multi-provider stack with real endpoint-level constraints. Adzuna, TheirStack, and CoreSignal cover different slices of hiring signals and must be treated as complementary rather than interchangeable. GitHub and Stack Exchange add ecosystem and practitioner activity context, while Wikimedia offers a lightweight attention proxy. The operational risk is not "missing one provider"; it is assuming all sources have equivalent semantics, coverage, and rate-limit behavior.

Interpretation is where most preventable failures occur. Signals drift when teams skip methodology breakpoint annotation, overreact to short windows, or treat popularity metrics as outcome metrics. Cross-source directional agreement, provenance labeling, and explicit confidence penalties are now table stakes for trustworthy analysis.

A second major synthesis point is contradiction handling. Sources can disagree for valid reasons (for example, demand-intent rise with weak total hiring, or high star growth with weak maintenance health). The right behavior is to preserve contradiction in output and downgrade confidence, not collapse disagreement into a simplistic final score.

Overall, `signal-talent-tech` should evolve from "collect indicators and summarize" to "collect, classify, gate, and only then verdict." This requires: stronger run protocol, endpoint-safe tool guidance, anti-pattern warning blocks, and a richer schema that stores provenance and unresolved conflicts.

---

## Recommendations for SKILL.md

> Concrete, actionable list of what should change / be added in the SKILL.md based on research.
> Each item here has a corresponding draft in the section below.

- [x] Replace broad narrative methodology with a strict run protocol (collect -> normalize -> triangulate -> segment -> classify -> verdict).
- [x] Add evidence provenance classes (`direct`, `sampled`, `modeled`) and confidence penalties for class conflicts.
- [x] Add explicit interpretation gates for freshness, seasonality, method revisions, and coverage.
- [x] Replace unverified tool method examples with endpoint-safe guidance: canonical real endpoint map plus runtime `op="help"` method discovery.
- [x] Add practical API error-handling rules for rate limits, pagination completeness, and partial results.
- [x] Add anti-pattern warning blocks with detection signal and mitigation steps.
- [x] Expand signal taxonomy to separate demand-intent, ecosystem momentum, and representativeness risk.
- [x] Add confidence policy and result-state policy for contradictions and sparse evidence.
- [x] Expand artifact schema with provenance, endpoint trace, contradiction records, and segmentation metadata.
- [x] Add an explicit pre-write quality checklist so low-quality runs are downgraded automatically.

---

## Draft Content for SKILL.md

> This is the most important section. For every recommendation above, write the **actual text** that should go into SKILL.md - as if you were writing it. Be verbose and comprehensive. The future editor will cut what they don't need; they should never need to invent content from scratch.
>
> Rules:
> - Write full paragraphs and bullet lists, not summaries
> - For methodology changes: write the actual instruction text in second person ("You should...", "Before doing X, always verify Y")
> - For schema changes: write the full JSON fragment with all fields, types, descriptions, enums, and `additionalProperties: false`
> - For anti-patterns: write the complete warning block including detection signal and mitigation steps
> - For tool recommendations: write the actual `## Available Tools` section text with real method syntax
> - Do not hedge or abbreviate - if a concept needs 3 paragraphs to explain properly, write 3 paragraphs
> - Mark sections with `### Draft: <topic>` headers so the editor can navigate

### Draft: Core operating principle and evidence contract

---
You are detecting talent and technology adoption signals for one domain, role family, or technology per run. Your primary operating rule is **evidence-first, confidence-second, verdict-last**.

Before writing any signal, classify each input metric into exactly one evidence class:
- `direct`: observed first-party or platform-native measurement with clear collection semantics.
- `sampled`: normalized or sampled index (for example relative trend/index systems).
- `modeled`: vendor-estimated or inferred values (for example inferred traffic, inferred skills, modeled hiring intensity).

You must keep evidence class labels in every signal record. You must not merge classes into one implied "ground truth score." If classes disagree, preserve the contradiction and downgrade confidence.

You should explicitly distinguish three concepts in every run:
1. **Demand intent** (employer-side signal from hiring sources),
2. **Ecosystem momentum** (developer/community activity),
3. **Representativeness risk** (how much of reality the chosen sources can see).

A run is high quality only when all three are addressed. A run with strong demand intent and weak representativeness controls is not high confidence.
---

### Draft: Methodology protocol (collect -> normalize -> triangulate -> segment -> classify -> verdict)

---
### Methodology

Run this sequence exactly. Do not skip steps.

1. **Define analysis scope and taxonomy first**
   - Before any API call, declare domain scope with positive and negative examples. For example: include "data engineer", "ml engineer", "ai platform engineer"; exclude generic "software engineer" unless explicitly in-scope.
   - Define segmentation axes up front: geography, seniority, role family, industry, and date window.
   - If taxonomy is ambiguous, your run quality is capped at `low` confidence regardless of data volume.

2. **Collect hiring-demand evidence from at least two independent hiring sources when available**
   - Pull source A (broad jobs coverage) and source B (company/technographic enriched coverage).
   - Keep raw counts, deduplicated counts (if available), and query filters used.
   - Treat posting count as demand-intent, not opening count. Never state literal vacancies unless a source explicitly measures vacancies.

3. **Normalize for comparability before trend interpretation**
   - Align date window, geography, and language.
   - Prefer seasonally adjusted or matched-period YoY interpretation for hiring trend statements.
   - Annotate method-revision windows and first-release/preliminary periods to avoid false trend breaks.
   - If comparability is weak, add limitation and apply confidence penalty.

4. **Collect ecosystem momentum evidence**
   - Pull GitHub repository and issue activity for domain-representative projects.
   - Pull Stack Exchange tag/question activity for domain tags and adjacent tags.
   - Optionally pull Wikimedia pageviews as broad attention proxy.
   - Label all ecosystem metrics as public-surface evidence unless private coverage is explicitly available.

5. **Triangulate direction, not exact levels**
   - Ask: do at least two independent sources agree on direction (growth/stable/decline)?
   - Do not require numeric equality across sources with different collection logic.
   - Record conflicts explicitly. Contradiction is valid output and should not be silently resolved.

6. **Apply segmentation checks before final claims**
   - Validate whether aggregate trend still holds by geography and role family.
   - If aggregate and segment directions diverge, report segment divergence and lower overall confidence.
   - Avoid global claims from one-country or one-role slices.

7. **Classify signal strength and write verdict**
   - `strong`: directional agreement across at least two independent sources, no critical quality-gate failure.
   - `moderate`: plausible direction with one significant unresolved caveat.
   - `weak`: single-source signal, unresolved contradiction, or severe comparability issue.
   - If evidence is insufficient, set `result_state` to `insufficient_data` and stop.

Decision rules:
- If hiring sources grow but ecosystem momentum is flat/declining, classify as demand-intent growth with ecosystem caution.
- If ecosystem momentum grows but hiring is flat, classify as early adoption watch signal.
- If hiring and ecosystem both decline, classify as decline signal unless methodology breakpoints explain most movement.
- If major source contradiction remains unexplained, set `result_state` to `ok_with_conflicts` and include concrete `next_checks`.

Do NOT:
- Infer structural trend from one short window.
- Treat keyword mentions as proof of skill depth without context check.
- Treat public OSS activity as full enterprise adoption.
---

### Draft: Interpretation quality gates and confidence policy

---
### Interpretation Quality Gates

You must pass these gates before assigning any `strong` signal:

1. **Freshness and revision gate**
   - Confirm whether source period is preliminary/revision-prone.
   - If yes, either exclude newest unstable slice or apply confidence penalty.

2. **Comparability gate**
   - Confirm aligned geography, language, and time window across core sources.
   - If mismatch exists, include it in `limitations` and downgrade confidence.

3. **Coverage gate**
   - Check representativeness by segment (role, region, sector).
   - If coverage is known weak for a key segment, cap confidence.

4. **Cross-source direction gate**
   - Require at least two independent signals for `strong`.
   - Single-source runs cannot exceed `moderate`.

5. **Contradiction gate**
   - If high-value sources disagree, write contradiction object and confidence penalty reason.
   - Contradiction without explanation cannot be `strong`.

6. **Anti-manipulation gate**
   - Popularity metrics (stars, mentions, pageviews) must be paired with quality/maintenance indicators.
   - If popularity and maintenance diverge, avoid positive overstatement.

Confidence scoring policy:
- Start at `0.50`.
- Add `+0.10` for each passed gate (max `+0.50`).
- Subtract `-0.10` for each unresolved major contradiction.
- Subtract `-0.10` if taxonomy ambiguity remains unresolved.
- Subtract `-0.10` if only one evidence class is present.
- Cap confidence at `0.60` when only one provider family is used.
- Cap confidence at `0.70` when all ecosystem signals are public-only with no hiring corroboration.

Confidence grade mapping:
- `0.80-1.00`: `high`
- `0.60-0.79`: `medium`
- `0.40-0.59`: `low`
- `<0.40`: `insufficient`
---

### Draft: Signal taxonomy and interpretation rules

---
Use this signal taxonomy to keep outputs consistent:

- `hiring_growth`: hiring demand-intent rising after seasonality/revision-aware checks.
- `hiring_decline`: hiring demand-intent falling with corroboration.
- `hiring_stable`: no meaningful directional movement within declared window.
- `adoption_early`: ecosystem momentum rising before broad hiring confirmation.
- `adoption_mainstream`: both hiring and ecosystem layers show sustained strength.
- `adoption_declining`: broad decline across hiring and ecosystem signals.
- `ecosystem_active`: repository/issues/Q&A evidence shows active technical discourse and maintenance.
- `ecosystem_stagnant`: ecosystem activity weak or declining with no compensating evidence.
- `compensation_pressure`: hiring context suggests demand pressure (for example salary bands widening upward where available).
- `coverage_risk`: representativeness or data-coverage weakness materially affects interpretability.

Interpretation rules:
- Demand and adoption are related but not identical. You may output demand growth with adoption uncertainty.
- Ecosystem activity should not be converted directly into labor demand without hiring corroboration.
- Compensation pressure requires explicit unit and source context; never infer salary trend from mention trend alone.
- `coverage_risk` can coexist with any positive signal and should reduce confidence rather than suppress evidence.
---

### Draft: Available Tools section (endpoint-safe, no invented method IDs)

---
## Available Tools

You must avoid invented method IDs. Before making any call, inspect runtime methods first:

```python
adzuna(op="help")
theirstack(op="help")
coresignal(op="help")
github(op="help")
stackexchange(op="help")
wikimedia(op="help")
```

Use only methods that exist in runtime help output. Map chosen runtime methods to these canonical real API endpoints:

- Adzuna Jobs API:
  - `GET /v1/api/jobs/{country}/search/{page}`
  - `GET /v1/api/jobs/{country}/categories`
- TheirStack API:
  - `POST /v1/jobs/search`
  - `POST /v1/companies/search`
  - `POST /v1/companies/technologies`
- CoreSignal:
  - `POST /v2/job_base/search/filter`
  - `POST /v2/job_base/search/es_dsl`
  - `GET /v2/job_base/collect/{job_id}`
  - `POST /v2/company_multi_source/search/es_dsl`
  - `GET /v2/company_multi_source/collect/{company_id}`
- GitHub:
  - `GET /repos/{owner}/{repo}`
  - `GET /repos/{owner}/{repo}/issues`
  - `GET /repos/{owner}/{repo}/issues/events`
  - `POST https://api.github.com/graphql`
- Stack Exchange:
  - `GET /2.3/questions`
  - `GET /2.3/tags`
  - `GET /2.3/tags/{tags}/info`
  - `GET /2.3/tags/{tags}/related`
- Wikimedia:
  - `GET /api/rest_v1/metrics/pageviews/per-article/{project}/{access}/{agent}/{article}/{granularity}/{start}/{end}`

Call-sequencing guidance:
1. Pull hiring-demand base first (`adzuna` + one of `theirstack`/`coresignal`).
2. Pull ecosystem evidence (`github` + `stackexchange`).
3. Pull attention proxy (`wikimedia`) only as secondary context.
4. If any provider fails or throttles, continue with remaining sources and downgrade confidence.

Example runtime-safe pattern:

```python
# 1) Inspect available methods at runtime
adzuna(op="help")

# 2) Choose only a method ID shown in help that maps to:
#    GET /v1/api/jobs/{country}/search/{page}
adzuna(
  op="call",
  args={
    "method_id": "<runtime-verified-method-id>",
    "country": "us",
    "page": 1,
    "what": "machine learning engineer",
    "where": "new york",
    "results_per_page": 50,
  },
)
```

API behavior rules:
- Respect provider throttling and `429` responses with exponential backoff.
- Complete pagination before making trend claims.
- Record when a query was truncated, timed out, or partially unavailable.
- Never fabricate missing fields; emit limitation instead.
---

### Draft: Anti-pattern warning blocks

---
### WARNING: Posting Count Literalism
**What it looks like:** You report job posting totals as exact open vacancies.  
**Detection signal:** Output states exact vacancy counts without caveat.  
**Consequence if missed:** False precision and incorrect demand sizing decisions.  
**Mitigation steps:**  
1. Label posting-based metrics as demand intent.  
2. Add limitation text when vacancy truth is unavailable.  
3. Use direction-focused language unless validated against vacancy/hiring sources.

### WARNING: Dedup Blindness
**What it looks like:** You trust source-side dedup as complete and do no local QA.  
**Detection signal:** Sudden count spikes with repeated posting signatures across sources.  
**Consequence if missed:** Artificial growth calls and noisy alerts.  
**Mitigation steps:**  
1. Track dedup ratio (raw vs unique where possible).  
2. Flag abnormal dedup-ratio shifts in limitations.  
3. Downgrade confidence when duplication cannot be assessed.

### WARNING: Popularity-as-Truth
**What it looks like:** You rank technology strength using stars or mentions only.  
**Detection signal:** No maintenance, issue-response, or release-quality metrics in output.  
**Consequence if missed:** Susceptibility to hype/manipulation and brittle decisions.  
**Mitigation steps:**  
1. Pair popularity metrics with maintenance-health evidence.  
2. Add contradiction if popularity rises while maintenance weakens.  
3. Cap confidence when quality indicators are missing.

### WARNING: Segment Collapse
**What it looks like:** You publish one global verdict without role/geography segmentation checks.  
**Detection signal:** Aggregate trend claim with no segment table or caveat.  
**Consequence if missed:** Local misallocation and false "universal" conclusions.  
**Mitigation steps:**  
1. Validate trend on core segments before final verdict.  
2. If segment divergence is material, emit `coverage_risk` signal.  
3. Keep global claim at moderate/low confidence.

### WARNING: Endpoint Invention
**What it looks like:** You use method IDs or endpoints not verifiable in docs/runtime help.  
**Detection signal:** Method syntax cannot be mapped to official endpoint docs.  
**Consequence if missed:** Broken runs and unmaintainable skill behavior.  
**Mitigation steps:**  
1. Start each provider with `op="help"`.  
2. Use canonical endpoint map as truth source.  
3. If mapping is unclear, stop and record uncertainty instead of guessing.
---

### Draft: Result-state policy

---
Set `result_state` using this policy:

- `ok`: Evidence supports a defensible verdict with no unresolved major contradiction.
- `ok_with_conflicts`: Evidence supports a tentative verdict but major contradictions remain.
- `zero_results`: Query returned valid-empty results across core providers.
- `insufficient_data`: Data exists but quality/comparability is too weak for a defensible verdict.
- `technical_failure`: Run failed due to provider/network/auth/tool errors that prevented minimum evidence collection.

Selection rules:
- Prefer `insufficient_data` over overconfident `ok` when quality gates fail.
- Use `ok_with_conflicts` instead of forcing a single narrative when sources disagree.
- Use `technical_failure` only when collection failed, not when evidence is contradictory.
---

### Draft: Output checklist before write_artifact

---
Before calling `write_artifact`, verify all checks:

1. At least two provider families used unless unavailable.
2. Every signal has provider + evidence class + key metric value + observed timestamp.
3. Demand-intent and ecosystem momentum are both assessed (or explicit limitation explains why not).
4. Segment checks are either performed or explicitly listed as missing with confidence penalty.
5. Contradictions are recorded, not hidden.
6. Confidence score and grade are consistent with quality gates.
7. Result state matches actual evidence quality.
8. Next checks are concrete and operational (not generic).

If any check fails, downgrade confidence and/or set `insufficient_data`.
---

### Draft: Schema additions

```json
{
  "signal_talent_tech": {
    "type": "object",
    "required": [
      "domain",
      "time_window",
      "geo_scope",
      "result_state",
      "signals",
      "confidence",
      "confidence_grade",
      "limitations",
      "next_checks"
    ],
    "additionalProperties": false,
    "properties": {
      "domain": {
        "type": "string",
        "description": "Technology, role family, or domain analyzed in this run."
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
      "geo_scope": {
        "type": "object",
        "required": [
          "primary_country"
        ],
        "additionalProperties": false,
        "properties": {
          "primary_country": {
            "type": "string",
            "description": "Primary country/market code used in the run."
          },
          "subregions": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Optional subregions covered by this run."
          }
        }
      },
      "result_state": {
        "type": "string",
        "enum": [
          "ok",
          "ok_with_conflicts",
          "zero_results",
          "insufficient_data",
          "technical_failure"
        ],
        "description": "Overall run outcome based on evidence quality and execution success."
      },
      "signals": {
        "type": "array",
        "items": {
          "type": "object",
          "required": [
            "signal_type",
            "description",
            "strength",
            "provider",
            "evidence_class",
            "metric_name",
            "metric_value",
            "metric_unit",
            "observed_at"
          ],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": [
                "hiring_growth",
                "hiring_decline",
                "hiring_stable",
                "adoption_early",
                "adoption_mainstream",
                "adoption_declining",
                "ecosystem_active",
                "ecosystem_stagnant",
                "compensation_pressure",
                "coverage_risk"
              ],
              "description": "Type of signal emitted by the run."
            },
            "description": {
              "type": "string",
              "description": "Human-readable explanation of this signal and why it matters."
            },
            "strength": {
              "type": "string",
              "enum": [
                "strong",
                "moderate",
                "weak"
              ],
              "description": "Signal strength after quality-gate checks."
            },
            "provider": {
              "type": "string",
              "description": "Provider/tool namespace that produced this signal."
            },
            "endpoint": {
              "type": "string",
              "description": "Canonical endpoint path or method reference used to collect this signal."
            },
            "evidence_class": {
              "type": "string",
              "enum": [
                "direct",
                "sampled",
                "modeled"
              ],
              "description": "Provenance class for this metric."
            },
            "metric_name": {
              "type": "string",
              "description": "Metric identifier used in interpretation (for example posting_count, stars_growth_30d)."
            },
            "metric_value": {
              "type": "string",
              "description": "Observed metric value serialized as text to preserve source precision."
            },
            "metric_unit": {
              "type": "string",
              "description": "Metric unit or format (count, percent, index, ratio, etc.)."
            },
            "observed_at": {
              "type": "string",
              "description": "ISO-8601 timestamp when this value was captured."
            },
            "segment": {
              "type": "string",
              "description": "Optional segment label (for example us/software-engineering/senior)."
            }
          }
        }
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Overall confidence after quality-gate pass/fail and contradiction penalties."
      },
      "confidence_grade": {
        "type": "string",
        "enum": [
          "high",
          "medium",
          "low",
          "insufficient"
        ],
        "description": "Bucketed label derived from numeric confidence."
      },
      "contradictions": {
        "type": "array",
        "description": "Explicit unresolved source disagreements affecting confidence.",
        "items": {
          "type": "object",
          "required": [
            "topic",
            "source_a",
            "source_b",
            "impact"
          ],
          "additionalProperties": false,
          "properties": {
            "topic": {
              "type": "string",
              "description": "Contradiction topic label."
            },
            "source_a": {
              "type": "string",
              "description": "First conflicting source identifier."
            },
            "source_b": {
              "type": "string",
              "description": "Second conflicting source identifier."
            },
            "impact": {
              "type": "string",
              "enum": [
                "minor",
                "moderate",
                "major"
              ],
              "description": "Estimated impact on final confidence."
            }
          }
        }
      },
      "limitations": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Known caveats that limit interpretation quality."
      },
      "next_checks": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Concrete follow-up checks that would reduce uncertainty."
      }
    }
  }
}
```

### Draft: Recording guidance block

---
### Recording

After collecting and interpreting evidence, call:

```python
write_artifact(
  artifact_type="signal_talent_tech",
  path="/signals/talent-tech-{YYYY-MM-DD}",
  data={...}
)
```

One artifact per domain per run. Do not dump raw JSON in chat.

Before writing:
1. Confirm `result_state` matches evidence quality.
2. Confirm every signal has provenance (`evidence_class`) and metric context.
3. Confirm contradiction entries exist when sources disagree materially.
4. Confirm confidence penalties were applied for unresolved quality-gate failures.
5. Confirm `next_checks` are specific enough to execute in the next run.
---

## Gaps & Uncertainties

- TheirStack and CoreSignal plan features and limits can change by contract tier; endpoint surfaces are stable but exact entitlements are tenant-specific.
- Wikimedia rate-limit behavior has conflicting public guidance across official pages; implementation should assume conservative pacing and robust retry.
- There is no single universal threshold set for "strong/moderate/weak" talent-tech signals across all industries; thresholds should remain context-aware and calibrated over time.
- Some foundational representativeness references are older than 2024 but still operationally relevant; these are marked evergreen.
- Public GitHub and Stack Exchange signals do not capture private enterprise workstreams; confidence should remain capped when private corroboration is unavailable.
