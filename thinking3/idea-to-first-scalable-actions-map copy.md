### Stage 1: Opportunity Framing (Level 2)

#### 1.1 Opportunity signal intake

- Inputs: founder thesis, customer complaints, market shifts, competitor moves, regulatory changes.
- Execution: build a signal register grouped by demand, regulation, technology, channel, and cost signals.
- Output artifact: `Opportunity Signal Register`.
- Local evidence gate: at least 3 independent signal classes support the same opportunity direction.
- Fail-fast trigger: only internal opinion exists with no external signal confirmation.

#### 1.2 Job and outcome framing

- Inputs: interview notes, observed workflows, existing workaround documentation.
- Execution: define core job statements and desired outcomes using direction + metric + object + context format.
- Output artifact: `JTBD and Desired Outcomes Map`.
- Local evidence gate: top outcomes are measurable and solution-agnostic.
- Fail-fast trigger: statements contain solution bias ("build app", "add AI") instead of job outcomes.

#### 1.3 Problem-space boundaries

- Inputs: initial hypotheses, target segment candidates, operational constraints.
- Execution: define explicit in-scope, out-of-scope, and "not now" boundaries for segment, workflow, and use case.
- Output artifact: `Problem Boundary Specification`.
- Local evidence gate: clear exclusions are documented and testable.
- Fail-fast trigger: target definition is broad ("for everyone").

#### 1.4 Constraint envelope

- Inputs: team capacity, budget ceiling, compliance constraints, technical constraints.
- Execution: quantify resource envelope (time, budget, people, tools), including maximum acceptable downside.
- Output artifact: `Constraint Matrix and Risk Envelope`.
- Local evidence gate: each top hypothesis has a feasible test path inside current envelope.
- Fail-fast trigger: core hypotheses require resources outside allowed envelope.

#### 1.5 Opportunity statement and risk assumptions

- Inputs: signal register, JTBD map, boundaries, constraints.
- Execution: run assumption mapping and rank risks by impact x evidence confidence.
- Output artifact: `Risk-Ranked Hypothesis Backlog`.
- Local evidence gate: top risks have explicit validation method, threshold, and timebox.
- Fail-fast trigger: high-impact assumptions remain untestable.

### Stage 2: Problem and Segment Validation (Level 2)

#### 2.1 Segment map and primary segment selection

- Inputs: candidate segments, trigger events, accessibility notes, TAM assumptions.
- Execution: segment by firmographic/behavioral/trigger criteria and enforce primary segment tests (word of mouth, same sales process, same product).
- Output artifact: `Primary Segment Decision Memo`.
- Local evidence gate: one primary segment selected and alternatives explicitly parked.
- Fail-fast trigger: selected segment requires multiple sales motions on day one.

#### 2.2 Problem interview execution

- Inputs: screener, interview script, candidate list.
- Execution: run interviews with past-behavior focus (not future promises), track saturation by theme.
- Output artifact: `Interview Corpus and Theme Coding`.
- Local evidence gate: pattern saturation reached for core themes in target segment.
- Fail-fast trigger: evidence is dominated by compliments and hypotheticals.

#### 2.3 Pain quantification

- Inputs: interview corpus, operational logs, proxy cost signals.
- Execution: quantify pain frequency, severity, cost of inaction, and switching friction (procedural, financial, relational).
- Output artifact: `Pain Economics Sheet`.
- Local evidence gate: top pains have numeric ranges and confidence level.
- Fail-fast trigger: no way to estimate business impact of pain.

#### 2.4 Alternative and status-quo mapping

- Inputs: user-described alternatives, competitor scans, internal process substitutes.
- Execution: map direct and indirect alternatives, including "do nothing" and manual workaround.
- Output artifact: `Alternative Landscape Matrix`.
- Local evidence gate: each alternative includes adoption reason and failure reason.
- Fail-fast trigger: analysis includes only named competitors and ignores status quo.

#### 2.5 Segment-problem fit verdict

- Inputs: segment data, pain economics, alternatives matrix.
- Execution: score evidence quality and issue explicit verdict (validated, weak, rejected).
- Output artifact: `Segment-Problem Fit Verdict`.
- Local evidence gate: decision references concrete evidence and confidence.
- Fail-fast trigger: all segments remain "possible" with no prioritization.

### Stage 3: Solution and Offer Hypothesis (Level 2)

#### 3.1 Value proposition design

- Inputs: validated pains/outcomes, segment insights.
- Execution: map jobs, pains, gains to pain relievers and gain creators; isolate top value claims.
- Output artifact: `Value Proposition Canvas per Primary Segment`.
- Local evidence gate: top claims map directly to top validated pains.
- Fail-fast trigger: feature list exists without explicit customer value mapping.

#### 3.2 Positioning architecture

- Inputs: alternatives matrix, value claims, segment language.
- Execution: define competitive alternatives, unique attributes, proof points, target segment, category anchor.
- Output artifact: `Positioning Brief`.
- Local evidence gate: one sentence "why us now" is clear and testable.
- Fail-fast trigger: positioning depends on generic superlatives only.

#### 3.3 Offer packaging architecture

- Inputs: positioning brief, support constraints, delivery model.
- Execution: design offer boundary (core, optional, excluded), plus tier logic if needed.
- Output artifact: `Offer and Packaging Specification`.
- Local evidence gate: tiers differ by customer value and service level, not random feature splitting.
- Fail-fast trigger: every deal needs custom packaging.

#### 3.4 Pricing hypothesis system

- Inputs: value claims, alternatives pricing, budget signals.
- Execution: triangulate price corridor via willingness-to-pay methods and commitment tests (paid pilot/deposit/preorder).
- Output artifact: `Price Corridor and Packaging Hypothesis`.
- Local evidence gate: floor/target/ceiling and rationale are explicit.
- Fail-fast trigger: pricing is set only as "competitor minus percent".

#### 3.5 Falsifiable test plan

- Inputs: offer and pricing hypotheses, risk backlog.
- Execution: define experiments with primary metric, guardrails, threshold, minimum sample logic, stop conditions.
- Output artifact: `Experiment Set`.
- Local evidence gate: each has pre-declared success/failure criteria.
- Fail-fast trigger: criteria are rewritten after seeing results.

### Stage 4: MVP or Proof-of-Value (Level 2)

#### 4.1 MVP pattern selection

- Inputs: top assumptions and experiment .
- Execution: select minimal pattern (concierge, Wizard-of-Oz, fake door, prototype, thin-slice) by risk type.
- Output artifact: `MVP Pattern Selection Note`.
- Local evidence gate: selected pattern is the cheapest path to test highest risk.
- Fail-fast trigger: full build starts before demand signal.

#### 4.2 Instrumentation and measurement design

- Inputs: experiment .
- Execution: define event schema, one primary metric, 2-3 guardrail metrics, attribution windows.
- Output artifact: `Measurement and Event Schema`.
- Local evidence gate: metrics are actionable, auditable, and tied to decision rule.
- Fail-fast trigger: only vanity metrics are tracked.

#### 4.3 Minimal implementation and assisted onboarding

- Inputs: selected MVP pattern, measurement schema.
- Execution: implement minimal user path to first value with manual assist where needed.
- Output artifact: `Testable MVP Artifact and Onboarding Script`.
- Local evidence gate: user can reach first value under defined time-to-value target.
- Fail-fast trigger: heavy integration work starts before proof of value.

#### 4.4 Real-user experiment run

- Inputs: MVP artifact, qualified users, runbook.
- Execution: run tests in bounded cohorts, maintain experiment integrity, document deviations.
- Output artifact: `Experiment Run Log and Raw Result Set`.
- Local evidence gate: sufficient directional reliability for decision (qual saturation or quant threshold).
- Fail-fast trigger: uncontrolled experiment changes without log.

#### 4.5 Decision loop

- Inputs: run logs, metric outcomes, guardrail outcomes.
- Execution: make explicit decision (pivot, refine, persevere, kill) against predeclared thresholds.
- Output artifact: `Decision Memo and Next-Hypothesis Queue`.
- Local evidence gate: decision rationale ties to threshold and evidence quality.
- Fail-fast trigger: continuation justified only by sunk cost.

### Stage 5: Early Commercial Validation (Level 2)

#### 5.1 Founder-led demand generation

- Inputs: ICP hypothesis, positioning brief, outreach scripts.
- Execution: run direct outreach and warm introductions with tight feedback capture loops.
- Output artifact: `Early Pipeline with Source and Response Data`.
- Local evidence gate: consistent meeting/response flow from target segment.
- Fail-fast trigger: dependence on accidental inbound before repeatable signal.

#### 5.2 Lead qualification and deal anatomy

- Inputs: active pipeline, discovery notes.
- Execution: apply lightweight qualification framework fit for ACV complexity, map buyer process and blockers.
- Output artifact: `Qualification Rubric and Deal Map`.
- Local evidence gate: each active deal has clear need, authority path, timeline, and risk notes.
- Fail-fast trigger: demo-heavy pipeline with unresolved qualification basics.

#### 5.3 Paid commitment and pilot structure

- Inputs: qualified opportunities, success criteria drafts.
- Execution: structure paid pilot with 30-90 day scope, 2-3 success metrics, and conversion terms.
- Output artifact: `Pilot Template and Commitment Terms`.
- Local evidence gate: pilot has explicit business outcome and conversion trigger.
- Fail-fast trigger: free pilot with no explicit strategic justification.

#### 5.4 First-customer success and references

- Inputs: signed pilot/customers, onboarding assets.
- Execution: run high-touch implementation to first value and capture proof artifacts.
- Output artifact: `First-Win Evidence Pack (results, quote, reference status)`.
- Local evidence gate: first value achieved within expected time band for segment.
- Fail-fast trigger: handoff gaps between sale and onboarding cause avoidable delays.

#### 5.5 Repeatability check to first ten customers

- Inputs: first-customer results, deal timeline data.
- Execution: compare deal patterns for repeatability in segment, motion, and offer.
- Output artifact: `Repeatability Report v1`.
- Local evidence gate: wins show recurring pattern, not isolated exceptions.
- Fail-fast trigger: each win requires unique custom process.

### Stage 6: Fit Consolidation (PMF-Level Evidence) (Level 2)

#### 6.1 Activation hardening

- Inputs: onboarding telemetry, support tickets, user session signals.
- Execution: remove activation friction in first-value path, refine guidance and defaults.
- Output artifact: `Activation Funnel and Friction Backlog`.
- Local evidence gate: activation step drop-offs are known and improving.
- Fail-fast trigger: major activation drop-offs remain unexplained.

#### 6.2 Cohort retention stabilization

- Inputs: cohort tables by signup period and segment.
- Execution: track return/usage behavior and diagnose cohort divergence.
- Output artifact: `Cohort Retention Review`.
- Local evidence gate: retention curves show stabilization or explicit recovery plan.
- Fail-fast trigger: aggregate retention hides failing recent cohorts.

#### 6.3 Revenue quality validation

- Inputs: expansion, contraction, churn, gross margin data.
- Execution: track GRR/NRR by segment and detect revenue quality risks.
- Output artifact: `Revenue Quality Dashboard`.
- Local evidence gate: retention and expansion dynamics align with target segment economics.
- Fail-fast trigger: growth is driven only by new logos while base leaks.

#### 6.4 PMF confidence triangulation

- Inputs: retention behavior, referral signals, PMF survey signal.
- Execution: triangulate PMF from behavior + sentiment; avoid single-metric claims.
- Output artifact: `PMF Confidence Score.
- Local evidence gate: independent metrics point in the same direction.
- Fail-fast trigger: PMF claim is based only on survey sentiment.

#### 6.5 Failure closure loop

- Inputs: churn list, churn interviews, loss reasons.
- Execution: run structured churn interviews, cluster root causes, assign corrective owners.
- Output artifact: `Churn Root-Cause Backlog`.
- Local evidence gate: each top churn cause has owner, action, and verification metric.
- Fail-fast trigger: churn reason remains generic ("price") with no root-cause detail.

### Stage 7: GTM and Route-to-Market Fit (Level 2)

#### 7.1 ICP and exclusion lock

- Inputs: win/loss data, churn data, usage quality by segment.
- Execution: finalize ICP traits, buying triggers, and explicit exclusion criteria.
- Output artifact: `ICP v1 with Exclusion List`.
- Local evidence gate: GTM teams use one ICP definition and one exclusion policy.
- Fail-fast trigger: multiple inconsistent ICP definitions run in parallel.

#### 7.2 GTM motion selection

- Inputs: ACV bands, complexity profile, buyer process, onboarding load.
- Execution: choose primary motion (PLG, sales-led, hybrid) with clear handoff points.
- Output artifact: `Primary Motion Decision Memo`.
- Local evidence gate: one dominant motion is selected for current phase.
- Fail-fast trigger: mixed motions launched without ownership boundaries.

#### 7.3 Channel fit validation

- Inputs: candidate channels, cost and conversion data, message test results.
- Execution: run focused channel tests and choose one or two channel-motion winners.
- Output artifact: `Channel Scoreand Priority Stack`.
- Local evidence gate: winning channels show consistent qualified pipeline generation.
- Fail-fast trigger: budget spread across many unproven channels.

#### 7.4 RTM architecture and conflict controls

- Inputs: motion model, partner model, pricing policy.
- Execution: define direct/indirect/hybrid roles, lead routing, deal registration, territory and parity rules.
- Output artifact: `RTM Rules of Engagement`.
- Local evidence gate: conflict resolution process and SLA are explicit.
- Fail-fast trigger: ownership overlap with no enforced rules.

#### 7.5 Unit economics readiness

- Inputs: CAC, gross margin, payback, conversion, retention data by segment.
- Execution: validate economics under scaled assumptions and stress scenarios.
- Output artifact: `Unit Economics Readiness Review`.
- Local evidence gate: payback and margin profile are inside target range for chosen segment.
- Fail-fast trigger: spend scaling starts while payback is unknown.

### Stage 8: First Scalable Actions (Level 2)

#### 8.1 Codification of winning motion

- Inputs: repeatable deal and onboarding patterns.
- Execution: codify scripts, qualification, handoffs, objection handling, and implementation playbooks.
- Output artifact: `Playbook Library v1`.
- Local evidence gate: new operator can execute from docs without founder intervention.
- Fail-fast trigger: critical steps exist only as founder tacit knowledge.

#### 8.2 Controlled volume expansion

- Inputs: validated channel-motion pairs, capacity constraints.
- Execution: expand throughput in bounded increments with pre/post quality checks.
- Output artifact: `Scale Increment Plan`.
- Local evidence gate: each increment has explicit rollback threshold.
- Fail-fast trigger: abrupt scale jumps without checkpoint review.

#### 8.3 Team and ownership scaling

- Inputs: operating bottleneck analysis, capacity plan.
- Execution: assign single owners for demand, conversion, onboarding, retention, and partner ops.
- Output artifact: `Operating Ownership Model`.
- Local evidence gate: each core KPI has one accountable owner.
- Fail-fast trigger: shared ownership with no clear accountability.

#### 8.4 Continuous optimization cadence

- Inputs: experiment backlog, operating score
- Execution: run weekly experiment cycle, monthly operating review, quarterly fit reassessment.
- Output artifact: `Optimization Cadence Calendar and Logs`.
- Local evidence gate: each cycle ends with concrete decision and owner.
- Fail-fast trigger: recurring meetings produce no decisions or actions.

#### 8.5 Risk and quality guardrails

- Inputs: conflict incidents, service quality incidents, pricing exceptions.
- Execution: enforce governance for pricing boundaries, channel conflict, SLA consistency, and exception paths.
- Output artifact: `Commercial Governance Charter`.
- Local evidence gate: exceptions are logged, reviewed, and auditable.
- Fail-fast trigger: repeated ad-hoc exceptions outside formal governance.

## Level 3 Schema-Aligned Bot Definitions

This section keeps only fields that map to current builder schema and runtime:

- bot config schema (`flexus_client_kit/builder/bot_config_schema.json`)
- expert frontmatter schema (rendered by `flexus_client_kit/builder/bot_registry_engine.py`)
- optional runtime metadata supported by `flexus_client_kit/runtime/no_special_code_bot.py`

### Bot 01 - `market_signal_bot`

- `accent_color`: `#2563EB`
- `title1`: `Market Signal`
- `title2`: `Channel-specific signal detection and normalization`
- `occupation`: `Market Signal Analyst`
- `typical_group`: `GTM / Discovery`
- `intro_message`: `I detect and normalize market signals into structured artifacts.`
- `tags`: [`GTM`, `Signals`, `Discovery`]
- `featured_actions`: [`Detect market signals for one channel` -> `market_signal_detector`]
- `experts`: [`market_signal_detector`, `signal_boundary_analyst`]
- `skills`: [`skill_google_trends_signal_detection`, `skill_x_signal_detection`, `skill_reddit_signal_detection`, `skill_web_change_detection`]
- `tools`: [`flexus_policy_document`, `print_widget`, `signal_search_demand_api`, `signal_social_trends_api`, `signal_news_events_api`, `signal_review_voice_api`, `signal_marketplace_demand_api`, `signal_web_traffic_intel_api`, `signal_jobs_demand_api`, `signal_dev_ecosystem_api`, `signal_public_interest_api`, `signal_professional_network_api`]

#### Bot 01 Tool Catalog (Expert 01A)

- `signal_search_demand_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Google Search Console API`
        - `Google Ads API (Keyword Planning)`
        - `DataForSEO Trends API`
        - `SerpApi (Google Search, Google Trends, Google Shopping engines)`
        - `Semrush API (Trends + Keyword reports)`
        - `Bing Webmaster API`
    - Provider method ids (`method_id`):
        - `google_search_console.searchanalytics.query.v1`
        - `google_ads.keyword_planner.generate_keyword_ideas.v1`
        - `google_ads.keyword_planner.generate_historical_metrics.v1`
        - `google_ads.keyword_planner.generate_forecast_metrics.v1`
        - `dataforseo.trends.explore.live.v1`
        - `dataforseo.trends.subregion_interests.live.v1`
        - `dataforseo.trends.demography.live.v1`
        - `dataforseo.trends.merged_data.live.v1`
        - `serpapi.search.google.v1`
        - `serpapi.search.google_trends.v1`
        - `serpapi.search.google_shopping.v1`
        - `semrush.trends.traffic_summary.v1`
        - `semrush.trends.daily_traffic.v1`
        - `semrush.analytics.keyword_reports.v1`
        - `bing_webmaster.get_page_stats.v1`
        - `bing_webmaster.get_page_query_stats.v1`
        - `bing_webmaster.get_rank_and_traffic_stats.v1`
    - Call contract:
        - `signal_search_demand_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `query_interest_timeseries`
        - `query_related_queries`
        - `query_keyword_volume`
        - `query_serp_snapshot`
        - `query_competitor_traffic`
    - Allowed `args` schema:
        - `provider` (string, required for query operations): `google_search_console | google_ads | dataforseo | serpapi | semrush | bing_webmaster`
        - `method` (string, optional): provider-specific upstream method name; must be in provider whitelist.
        - `channel` (string, optional): must be `search` when provided.
        - `query` (string or array of strings, required for query operations): keyword or keyword list.
        - `domains` (array of strings, required for `query_competitor_traffic`): target domains.
        - `geo` (object, optional): `country` (ISO-3166-1 alpha-2), `region` (string), `city` (string).
        - `time_window` (string, optional): `last_7d | last_30d | last_90d | custom`.
        - `start_date` (string, required if `time_window=custom`): format `YYYY-MM-DD`.
        - `end_date` (string, required if `time_window=custom`): format `YYYY-MM-DD`.
        - `limit` (integer, optional): `1..1000`, default `100`.
        - `cursor` (string, optional): provider pagination token.
        - `include_raw` (boolean, optional): default `false`.
        - `normalize` (boolean, optional): default `true`.
    - Operation-specific required arguments:
        - `query_interest_timeseries`: `provider`, `query`
        - `query_related_queries`: `provider`, `query`
        - `query_keyword_volume`: `provider`, `query`
        - `query_serp_snapshot`: `provider`, `query`
        - `query_competitor_traffic`: `provider`, `domains`
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method` not allowed for selected provider.
        - Reject empty `query` or empty `domains` for respective operations.
        - Reject `time_window=custom` without `start_date` and `end_date`.
        - Reject invalid date format and invalid date order (`start_date > end_date`).
        - Reject `channel` not equal to `search`.
        - Reject `limit` outside allowed range.
    - Response format:
        - Text summary first for model readability.
        - Structured JSON block with normalized records.
        - Optional raw provider payload appended only when `include_raw=true`.
    - Example calls:
        - `signal_search_demand_api(op="status")`
        - `signal_search_demand_api(op="list_providers")`
        - `signal_search_demand_api(op="query_interest_timeseries", args={"provider":"dataforseo","method":"keywords_data/dataforseo_trends/explore/live","query":["ai sales assistant"],"geo":{"country":"US"},"time_window":"last_30d","limit":50})`
        - `signal_search_demand_api(op="query_keyword_volume", args={"provider":"google_ads","method":"GenerateKeywordHistoricalMetrics","query":["b2b lead generation"],"geo":{"country":"US"},"time_window":"custom","start_date":"2025-10-01","end_date":"2025-12-31"})`

- `signal_social_trends_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Reddit API`
        - `X API v2`
        - `YouTube Data API v3`
        - `TikTok Research API`
        - `Instagram Graph API`
        - `Pinterest API`
        - `Product Hunt GraphQL API`
    - Provider method ids (`method_id`):
        - `reddit.subreddit.new.v1`
        - `reddit.subreddit.hot.v1`
        - `reddit.search.posts.v1`
        - `reddit.comments.list.v1`
        - `x.tweets.counts_recent.v1`
        - `x.tweets.search_recent.v1`
        - `youtube.search.list.v1`
        - `youtube.videos.list.v1`
        - `youtube.comment_threads.list.v1`
        - `tiktok.research.video_query.v1`
        - `instagram.hashtag.search.v1`
        - `instagram.hashtag.recent_media.v1`
        - `instagram.hashtag.top_media.v1`
        - `pinterest.trends.keywords_top.v1`
        - `producthunt.graphql.posts.v1`
        - `producthunt.graphql.topics.v1`

- `signal_news_events_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `GDELT API`
        - `Event Registry API`
        - `NewsAPI`
        - `GNews API`
        - `NewsData.io API`
        - `MediaStack API`
        - `NewsCatcher API`
        - `Perigon API`
    - Provider method ids (`method_id`):
        - `gdelt.doc.search.v1`
        - `gdelt.events.search.v1`
        - `event_registry.article.get_articles.v1`
        - `event_registry.event.get_events.v1`
        - `newsapi.everything.v1`
        - `newsapi.top_headlines.v1`
        - `gnews.search.v1`
        - `gnews.top_headlines.v1`
        - `newsdata.news.search.v1`
        - `mediastack.news.search.v1`
        - `newscatcher.search.v1`
        - `newscatcher.latest_headlines.v1`
        - `perigon.all.search.v1`
        - `perigon.topics.search.v1`

- `signal_review_voice_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Trustpilot API`
        - `Yelp Fusion API`
        - `G2 data provider API`
        - `Capterra data provider API`
    - Provider method ids (`method_id`):
        - `trustpilot.business_units.find.v1`
        - `trustpilot.business_units.get_public.v1`
        - `trustpilot.reviews.list.v1`
        - `yelp.businesses.search.v1`
        - `yelp.businesses.get.v1`
        - `yelp.businesses.reviews.v1`
        - `g2.vendors.list.v1`
        - `g2.reviews.list.v1`
        - `g2.categories.benchmark.v1`
        - `capterra.products.list.v1`
        - `capterra.reviews.list.v1`
        - `capterra.categories.list.v1`

- `signal_marketplace_demand_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Amazon SP-API`
        - `eBay Browse API`
        - `eBay Marketplace Insights API`
        - `Google Shopping Content API`
    - Provider method ids (`method_id`):
        - `amazon.catalog.search_items.v1`
        - `amazon.catalog.get_item.v1`
        - `amazon.pricing.get_item_offers_batch.v1`
        - `amazon.pricing.get_listing_offers_batch.v1`
        - `ebay.browse.get_items.v1`
        - `ebay.browse.search.v1`
        - `ebay.marketplace_insights.item_sales_search.v1`
        - `google_shopping.reports.search_topic_trends.v1`

- `signal_web_traffic_intel_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Similarweb API`
        - `Shopify Admin analytics surface`
    - Provider method ids (`method_id`):
        - `similarweb.traffic_and_engagement.get.v1`
        - `similarweb.traffic_sources.get.v1`
        - `similarweb.traffic_geography.get.v1`
        - `similarweb.website_ranking.get.v1`
        - `similarweb.similar_sites.get.v1`
        - `shopify.analytics.reports_list.v1`
        - `shopify.analytics.reports_dates.v1`
        - `shopify.analytics.reports_get.v1`

- `signal_jobs_demand_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Adzuna API`
        - `Bright Data Jobs API`
        - `Coresignal API`
        - `TheirStack API`
        - `Oxylabs jobs data API`
        - `HasData jobs APIs`
        - `Levels.fyi API`
        - `LinkedIn Jobs data provider API (restricted/compliance-sensitive)`
        - `Glassdoor data provider API (restricted/compliance-sensitive)`
    - Provider method ids (`method_id`):
        - `adzuna.jobs.search_ads.v1`
        - `adzuna.jobs.regional_data.v1`
        - `brightdata.jobs.data_feed.v1`
        - `brightdata.jobs.dataset_query.v1`
        - `coresignal.jobs.posts.v1`
        - `coresignal.companies.profile.v1`
        - `theirstack.jobs.search.v1`
        - `theirstack.companies.hiring.v1`
        - `oxylabs.jobs.source_query.v1`
        - `hasdata.indeed.jobs.v1`
        - `hasdata.glassdoor.jobs.v1`
        - `levelsfyi.compensation.benchmark.v1`
        - `linkedin_jobs.provider.search.v1` (restricted)
        - `glassdoor.provider.search.v1` (restricted)

- `signal_dev_ecosystem_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `GitHub REST API`
        - `Stack Exchange API`
    - Provider method ids (`method_id`):
        - `github.search.repositories.v1`
        - `github.search.issues.v1`
        - `github.repos.get.v1`
        - `stackexchange.questions.list.v1`
        - `stackexchange.tags.info.v1`
        - `stackexchange.tags.related.v1`

- `signal_public_interest_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Wikimedia Pageviews API`
    - Provider method ids (`method_id`):
        - `wikimedia.pageviews.per_article.v1`
        - `wikimedia.pageviews.aggregate.v1`

- `signal_professional_network_api`
    - Integration mode: `Request/Response` (restricted)
    - APIs:
        - `LinkedIn Marketing API`
    - Provider method ids (`method_id`):
        - `linkedin.organization.posts.list.v1`
        - `linkedin.organization.social_actions.list.v1`
        - `linkedin.organization.followers.stats.v1`
    - Constraint note:
        - `Use only where provider terms allow this exact use case; treat as restricted integration by default.`

#### Bot 01 Required Tool Prompt Files

- `prompts/tool_signal_search_demand_api.md`
- `prompts/tool_signal_social_trends_api.md`
- `prompts/tool_signal_news_events_api.md`
- `prompts/tool_signal_review_voice_api.md`
- `prompts/tool_signal_marketplace_demand_api.md`
- `prompts/tool_signal_web_traffic_intel_api.md`
- `prompts/tool_signal_jobs_demand_api.md`
- `prompts/tool_signal_dev_ecosystem_api.md`
- `prompts/tool_signal_public_interest_api.md`
- `prompts/tool_signal_professional_network_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 01A - `market_signal_detector`

- `name`: `market_signal_detector`
- `fexp_description`: `Detect and normalize market signals for one channel per run`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,signal_search_demand_api,signal_social_trends_api,signal_news_events_api,signal_review_voice_api,signal_marketplace_demand_api,signal_web_traffic_intel_api,signal_jobs_demand_api,signal_dev_ecosystem_api,signal_public_interest_api,signal_professional_network_api`
- `fexp_block_tools`: ``
- `skills`: [`skill_google_trends_signal_detection`, `skill_x_signal_detection`, `skill_reddit_signal_detection`, `skill_web_change_detection`]
- `pdoc_output_schemas`:
  [
  {
  "schema_name": "market_signal_snapshot_schema",
  "schema": {
  "type": "object",
  "required": [
  "artifact_type",
  "version",
  "channel",
  "query",
  "time_window",
  "result_state",
  "evidence_count",
  "coverage_status",
  "confidence",
  "confidence_reason",
  "signals",
  "sources",
  "limitations",
  "next_checks"
  ],
  "additionalProperties": false,
  "properties": {
  "artifact_type": {
  "type": "string",
  "enum": ["market_signal_snapshot"]
  },
  "version": {
  "type": "string"
  },
  "channel": {
  "type": "string"
  },
  "query": {
  "type": "string"
  },
  "time_window": {
  "type": "object",
  "required": ["start_date", "end_date"],
  "additionalProperties": false,
  "properties": {
  "start_date": { "type": "string" },
  "end_date": { "type": "string" }
  }
  },
  "result_state": {
  "type": "string",
  "enum": ["ok", "zero_results", "insufficient_data", "technical_failure"]
  },
  "evidence_count": {
  "type": "integer",
  "minimum": 0
  },
  "coverage_status": {
  "type": "string",
  "enum": ["full", "partial", "none"]
  },
  "confidence": {
  "type": "number",
  "minimum": 0,
  "maximum": 1
  },
  "confidence_reason": {
  "type": "string"
  },
  "signals": {
  "type": "array",
  "items": {
  "type": "object",
  "required": ["signal_id", "signal_summary", "signal_strength", "supporting_source_refs"],
  "additionalProperties": false,
  "properties": {
  "signal_id": { "type": "string" },
  "signal_summary": { "type": "string" },
  "signal_strength": {
  "type": "string",
  "enum": ["weak", "moderate", "strong"]
  },
  "supporting_source_refs": {
  "type": "array",
  "items": { "type": "string" }
  }
  }
  }
  },
  "sources": {
  "type": "array",
  "items": {
  "type": "object",
  "required": ["source_type", "source_ref"],
  "additionalProperties": false,
  "properties": {
  "source_type": {
  "type": "string",
  "enum": [
  "api",
  "artifact",
  "tool_output",
  "event_stream",
  "expert_handoff",
  "user_directive"
  ]
  },
  "source_ref": { "type": "string" }
  }
  }
  },
  "limitations": {
  "type": "array",
  "items": { "type": "string" }
  },
  "failure_code": { "type": "string" },
  "failure_message": { "type": "string" },
  "next_checks": {
  "type": "array",
  "items": { "type": "string" }
  }
  }
  }
  }
  ]
- `body_md`: `Create one channel signal snapshot per run, including result_state (`ok|zero_results|insufficient_data|technical_failure`), evidence quality, and source-backed signal records.`

### Expert 01B - `signal_boundary_analyst`

- `name`: `signal_boundary_analyst`
- `fexp_description`: `Aggregate 01A channel snapshots into bounded signal register and risk-ranked hypotheses`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`:
  [
  {
  "schema_name": "signal_register_schema",
  "schema": {
  "type": "object",
  "required": [
  "artifact_type",
  "version",
  "aggregation_window",
  "channels_considered",
  "register"
  ],
  "additionalProperties": false,
  "properties": {
  "artifact_type": {
  "type": "string",
  "enum": ["signal_register"]
  },
  "version": { "type": "string" },
  "aggregation_window": {
  "type": "object",
  "required": ["start_date", "end_date"],
  "additionalProperties": false,
  "properties": {
  "start_date": { "type": "string" },
  "end_date": { "type": "string" }
  }
  },
  "channels_considered": {
  "type": "array",
  "items": { "type": "string" }
  },
  "register": {
  "type": "array",
  "items": {
  "type": "object",
  "required": [
  "register_id",
  "signal_theme",
  "combined_strength",
  "confidence",
  "supporting_snapshot_refs",
  "conflict_notes"
  ],
  "additionalProperties": false,
  "properties": {
  "register_id": { "type": "string" },
  "signal_theme": { "type": "string" },
  "combined_strength": {
  "type": "string",
  "enum": ["weak", "moderate", "strong"]
  },
  "confidence": {
  "type": "number",
  "minimum": 0,
  "maximum": 1
  },
  "supporting_snapshot_refs": {
  "type": "array",
  "items": { "type": "string" }
  },
  "conflict_notes": {
  "type": "array",
  "items": { "type": "string" }
  }
  }
  }
  }
  }
  }
  },
  {
  "schema_name": "hypothesis_backlog_schema",
  "schema": {
  "type": "object",
  "required": [
  "artifact_type",
  "version",
  "prioritization_rule",
  "in_scope",
  "out_of_scope",
  "not_now",
  "hypotheses"
  ],
  "additionalProperties": false,
  "properties": {
  "artifact_type": {
  "type": "string",
  "enum": ["hypothesis_backlog"]
  },
  "version": { "type": "string" },
  "prioritization_rule": {
  "type": "string",
  "enum": ["impact_x_confidence_x_reversibility"]
  },
  "in_scope": {
  "type": "array",
  "items": { "type": "string" }
  },
  "out_of_scope": {
  "type": "array",
  "items": { "type": "string" }
  },
  "not_now": {
  "type": "array",
  "items": { "type": "string" }
  },
  "hypotheses": {
  "type": "array",
  "items": {
  "type": "object",
  "required": [
  "hypothesis_id",
  "statement",
  "priority_rank",
  "impact_score",
  "confidence_score",
  "reversibility_score",
  "fail_fast_condition",
  "next_validation_step",
  "supporting_register_refs"
  ],
  "additionalProperties": false,
  "properties": {
  "hypothesis_id": { "type": "string" },
  "statement": { "type": "string" },
  "priority_rank": {
  "type": "integer",
  "minimum": 1
  },
  "impact_score": {
  "type": "number",
  "minimum": 0,
  "maximum": 1
  },
  "confidence_score": {
  "type": "number",
  "minimum": 0,
  "maximum": 1
  },
  "reversibility_score": {
  "type": "number",
  "minimum": 0,
  "maximum": 1
  },
  "fail_fast_condition": { "type": "string" },
  "next_validation_step": { "type": "string" },
  "supporting_register_refs": {
  "type": "array",
  "items": { "type": "string" }
  }
  }
  }
  }
  }
  }
  }
  ]
- `body_md`: `Read 01A snapshot artifacts, deduplicate and normalize cross-channel evidence, then emit signal register and hypothesis backlog payloads with explicit in-scope/out-of-scope boundaries.`

### Bot 02 - `customer_discovery_bot`

- `accent_color`: `#0D9488`
- `title1`: `Customer Discovery`
- `title2`: `Interview and survey evidence operations`
- `occupation`: `Discovery Operator`
- `typical_group`: `GTM / Discovery`
- `intro_message`: `I run structured discovery workflows and keep evidence quality high.`
- `tags`: [`Discovery`, `JTBD`, `Research`]
- `featured_actions`: [`Prepare next interview instrument` -> `discovery_instrument_designer`, `Recruit participants for interviews/tests` -> `participant_recruitment_operator`]
- `experts`: [`discovery_instrument_designer`, `participant_recruitment_operator`, `jtbd_interview_operator`]
- `skills`: [`skill_past_behavior_questioning`, `skill_jtbd_outcome_formatting`, `skill_qualitative_coding`]
- `tools`: [`flexus_policy_document`, `print_widget`, `discovery_survey_design_api`, `discovery_survey_collection_api`, `discovery_panel_recruitment_api`, `discovery_customer_panel_api`, `discovery_test_recruitment_api`, `discovery_interview_scheduling_api`, `discovery_interview_capture_api`, `discovery_transcript_coding_api`, `discovery_context_import_api`]

#### Bot 02 Tool Catalog

- `discovery_survey_design_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `SurveyMonkey API v3`
        - `Typeform Create API`
        - `Qualtrics Survey Definitions API`
    - Provider method ids (`method_id`):
        - `surveymonkey.surveys.create.v1`
        - `surveymonkey.surveys.update.v1`
        - `typeform.forms.create.v1`
        - `typeform.forms.update.v1`
        - `qualtrics.surveys.create.v1`
        - `qualtrics.surveys.update.v1`
    - Call contract:
        - `discovery_survey_design_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_interview_screener`
        - `create_survey_instrument`
        - `update_question_block`
        - `validate_instrument_bias`
    - Allowed `args` schema:
        - `provider` (string): `surveymonkey | typeform | qualtrics`
        - `method_id` (string, optional): must be from provider whitelist.
        - `instrument_id` (string, optional for updates)
        - `hypothesis_refs` (array of strings, required for create operations)
        - `target_segment` (string, required for create operations)
        - `question_block` (object, required for `update_question_block`)
        - `locale` (string, optional): IETF language tag.
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create operations without `hypothesis_refs` and `target_segment`.
        - Reject `update_question_block` without `instrument_id` and `question_block`.

- `discovery_survey_collection_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `SurveyMonkey API v3`
        - `Typeform Responses API`
        - `Qualtrics Responses Export API`
    - Provider method ids (`method_id`):
        - `surveymonkey.collectors.create.v1`
        - `surveymonkey.surveys.responses.list.v1`
        - `typeform.responses.list.v1`
        - `qualtrics.responseexports.start.v1`
        - `qualtrics.responseexports.progress.get.v1`
        - `qualtrics.responseexports.file.get.v1`
  - Constraint note:
    - `Qualtrics response export is async flow (start -> poll progress -> download file).`

- `discovery_panel_recruitment_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Prolific API`
        - `Cint API (Exchange/Demand)`
        - `Amazon Mechanical Turk API`
    - Provider method ids (`method_id`):
        - `prolific.studies.create.v1`
        - `prolific.studies.get.v1`
        - `prolific.submissions.list.v1`
        - `prolific.submissions.approve.v1`
        - `prolific.submissions.reject.v1`
        - `cint.projects.create.v1`
        - `cint.projects.feasibility.get.v1`
        - `cint.projects.launch.v1`
        - `mturk.hits.create.v1`
        - `mturk.hits.list.v1`
        - `mturk.assignments.list.v1`
        - `mturk.assignments.approve.v1`
  - Constraint note:
    - `Cint endpoints vary by tenant plan/integration profile; keep provider adapter strict and fail-fast on unsupported methods.`

- `discovery_customer_panel_api`
  - Integration mode: `Request/Response`
  - APIs:
    - `Qualtrics XM Subscribers / Mailing Lists API`
    - `User Interviews Hub API`
  - Provider method ids (`method_id`):
    - `qualtrics.mailinglists.list.v1`
    - `qualtrics.contacts.create.v1`
    - `qualtrics.contacts.list.v1`
    - `qualtrics.distributions.create.v1`
    - `userinterviews.participants.create.v1`
    - `userinterviews.participants.update.v1`
    - `userinterviews.participants.delete.v1`
  - Constraint note:
    - `User Interviews Hub API access is gated and enabled per workspace account.`

- `discovery_test_recruitment_api`
  - Integration mode: `Request/Response`
  - APIs:
    - `UserTesting API`
    - `Prolific API`
    - `Amazon Mechanical Turk API`
  - Provider method ids (`method_id`):
    - `usertesting.tests.create.v1`
    - `usertesting.tests.sessions.list.v1`
    - `usertesting.results.transcript.get.v1`
    - `prolific.studies.create.v1`
    - `prolific.submissions.list.v1`
    - `mturk.hits.create.v1`
    - `mturk.assignments.list.v1`
  - Constraint note:
    - `UserTesting API is enterprise-restricted; treat as optional provider with explicit status check before execution.`

- `discovery_interview_scheduling_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Calendly API`
        - `Google Calendar API`
    - Provider method ids (`method_id`):
        - `calendly.scheduled_events.list.v1`
        - `calendly.scheduled_events.invitees.list.v1`
        - `google_calendar.events.insert.v1`
        - `google_calendar.events.list.v1`

- `discovery_interview_capture_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Zoom Cloud Recording API`
        - `Gong API`
        - `Fireflies GraphQL API`
    - Provider method ids (`method_id`):
        - `zoom.recordings.list.v1`
        - `zoom.recordings.transcript.download.v1`
        - `gong.calls.list.v1`
        - `gong.calls.transcript.get.v1`
        - `fireflies.transcript.get.v1`

- `discovery_transcript_coding_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Dovetail API`
    - Provider method ids (`method_id`):
        - `dovetail.insights.export.markdown.v1`
        - `dovetail.projects.export.zip.v1`

- `discovery_context_import_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Zendesk Ticketing API`
        - `Intercom Conversations API`
    - Provider method ids (`method_id`):
        - `hubspot.contacts.search.v1`
        - `hubspot.notes.list.v1`
        - `hubspot.calls.list.v1`
        - `zendesk.incremental.ticket_events.comment_events.list.v1`
        - `zendesk.tickets.audits.list.v1`
        - `intercom.conversations.list.v1`

#### Bot 02 Required Tool Prompt Files

- `prompts/tool_discovery_survey_design_api.md`
- `prompts/tool_discovery_survey_collection_api.md`
- `prompts/tool_discovery_panel_recruitment_api.md`
- `prompts/tool_discovery_customer_panel_api.md`
- `prompts/tool_discovery_test_recruitment_api.md`
- `prompts/tool_discovery_interview_scheduling_api.md`
- `prompts/tool_discovery_interview_capture_api.md`
- `prompts/tool_discovery_transcript_coding_api.md`
- `prompts/tool_discovery_context_import_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 02A - `discovery_instrument_designer`

- `name`: `discovery_instrument_designer`
- `fexp_description`: `Design high-quality interview and survey instruments`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,discovery_survey_design_api,discovery_survey_collection_api,discovery_context_import_api`
- `fexp_block_tools`: ``
- `skills`: [`skill_past_behavior_questioning`, `skill_jtbd_outcome_formatting`]
- `pdoc_output_schemas`: [{"schema_name":"interview_instrument_schema","schema":{"type":"object","required":["artifact_type","version","instrument_id","research_goal","target_segment","hypothesis_refs","interview_mode","question_blocks","probe_bank","bias_controls","consent_protocol","completion_criteria"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["interview_instrument"]},"version":{"type":"string"},"instrument_id":{"type":"string"},"research_goal":{"type":"string"},"target_segment":{"type":"string"},"hypothesis_refs":{"type":"array","items":{"type":"string"}},"interview_mode":{"type":"string","enum":["live_video","live_audio","async_text"]},"question_blocks":{"type":"array","items":{"type":"object","required":["question_id","question_text","evidence_objective","question_type","forbidden_patterns"],"additionalProperties":false,"properties":{"question_id":{"type":"string"},"question_text":{"type":"string"},"evidence_objective":{"type":"string"},"question_type":{"type":"string","enum":["past_behavior","timeline","switch_trigger","decision_criteria","objection_probe"]},"forbidden_patterns":{"type":"array","items":{"type":"string"}}}}},"probe_bank":{"type":"array","items":{"type":"string"}},"bias_controls":{"type":"array","items":{"type":"string"}},"consent_protocol":{"type":"object","required":["consent_required","recording_policy"],"additionalProperties":false,"properties":{"consent_required":{"type":"boolean"},"recording_policy":{"type":"string"}}},"completion_criteria":{"type":"array","items":{"type":"string"}}}}},
  {"schema_name":"survey_instrument_schema","schema":{"type":"object","required":["artifact_type","version","instrument_id","survey_goal","target_segment","hypothesis_refs","sample_plan","questions","branching_rules","quality_controls","analysis_plan"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["survey_instrument"]},"version":{"type":"string"},"instrument_id":{"type":"string"},"survey_goal":{"type":"string"},"target_segment":{"type":"string"},"hypothesis_refs":{"type":"array","items":{"type":"string"}},"sample_plan":{"type":"object","required":["target_n","min_n_per_segment"],"additionalProperties":false,"properties":{"target_n":{"type":"integer","minimum":1},"min_n_per_segment":{"type":"integer","minimum":1}}},"questions":{"type":"array","items":{"type":"object","required":["question_id","question_text","response_type"],"additionalProperties":false,"properties":{"question_id":{"type":"string"},"question_text":{"type":"string"},"response_type":{"type":"string","enum":["single_select","multi_select","likert","numeric","free_text"]},"answer_scale":{"type":"string"}}}},"branching_rules":{"type":"array","items":{"type":"string"}},"quality_controls":{"type":"array","items":{"type":"string"}},"analysis_plan":{"type":"array","items":{"type":"string"}}}}},
{"schema_name":"discovery_instrument_readiness_schema","schema":{"type":"object","required":["artifact_type","version","instrument_id","readiness_state","blocking_issues","recommended_fixes"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["discovery_instrument_readiness"]},"version":{"type":"string"},"instrument_id":{"type":"string"},"readiness_state":{"type":"string","enum":["ready","revise","blocked"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"recommended_fixes":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Design and version discovery instruments mapped to explicit hypotheses, sample plan, and bias controls; fail fast when hypotheses or target segment are underspecified.`

### Expert 02B - `participant_recruitment_operator`

- `name`: `participant_recruitment_operator`
- `fexp_description`: `Recruit participants for surveys, interviews, and usability tests across panel providers`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,discovery_panel_recruitment_api,discovery_customer_panel_api,discovery_test_recruitment_api,discovery_interview_scheduling_api,discovery_survey_collection_api,discovery_context_import_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"participant_recruitment_plan_schema","schema":{"type":"object","required":["artifact_type","version","plan_id","study_type","target_segment","quota_cells","channels","inclusion_criteria","exclusion_criteria","incentive_policy","timeline"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["participant_recruitment_plan"]},"version":{"type":"string"},"plan_id":{"type":"string"},"study_type":{"type":"string","enum":["survey","interview","usability_test","mixed"]},"target_segment":{"type":"string"},"quota_cells":{"type":"array","items":{"type":"object","required":["cell_id","target_n"],"additionalProperties":false,"properties":{"cell_id":{"type":"string"},"target_n":{"type":"integer","minimum":1}}}},"channels":{"type":"array","items":{"type":"string"}},"inclusion_criteria":{"type":"array","items":{"type":"string"}},"exclusion_criteria":{"type":"array","items":{"type":"string"}},"incentive_policy":{"type":"object","required":["currency","amount_range"],"additionalProperties":false,"properties":{"currency":{"type":"string"},"amount_range":{"type":"string"}}},"timeline":{"type":"object","required":["launch_date","target_close_date"],"additionalProperties":false,"properties":{"launch_date":{"type":"string"},"target_close_date":{"type":"string"}}}}}},
{"schema_name":"recruitment_funnel_snapshot_schema","schema":{"type":"object","required":["artifact_type","version","plan_id","snapshot_ts","provider_breakdown","overall_status","dropoff_reasons"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["recruitment_funnel_snapshot"]},"version":{"type":"string"},"plan_id":{"type":"string"},"snapshot_ts":{"type":"string"},"provider_breakdown":{"type":"array","items":{"type":"object","required":["provider","invited","started","qualified","completed"],"additionalProperties":false,"properties":{"provider":{"type":"string"},"invited":{"type":"integer","minimum":0},"started":{"type":"integer","minimum":0},"qualified":{"type":"integer","minimum":0},"completed":{"type":"integer","minimum":0}}}},"overall_status":{"type":"string","enum":["on_track","at_risk","blocked"]},"dropoff_reasons":{"type":"array","items":{"type":"string"}}}}},
{"schema_name":"recruitment_compliance_quality_schema","schema":{"type":"object","required":["artifact_type","version","plan_id","quality_checks","fraud_signals","consent_traceability","pass_fail"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["recruitment_compliance_quality"]},"version":{"type":"string"},"plan_id":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"fraud_signals":{"type":"array","items":{"type":"string"}},"consent_traceability":{"type":"string","enum":["complete","partial","missing"]},"pass_fail":{"type":"string","enum":["pass","fail"]}}}}]
- `body_md`: `Own participant recruitment end-to-end for surveys/interviews/tests: channel selection, quotas, scheduling handoff, funnel monitoring, and compliance-quality gates with explicit fail-fast outputs.`

### Expert 02C - `jtbd_interview_operator`

- `name`: `jtbd_interview_operator`
- `fexp_description`: `Operate JTBD interviews and produce coded evidence artifacts`
- `fexp_allow_tools`: `flexus_policy_document,discovery_interview_capture_api,discovery_transcript_coding_api,discovery_context_import_api`
- `fexp_block_tools`: `print_widget`
- `skills`: [`skill_qualitative_coding`]
- `pdoc_output_schemas`: [{"schema_name":"interview_corpus_schema","schema":{"type":"object","required":["artifact_type","version","study_id","time_window","target_segment","interviews","coverage_status","limitations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["interview_corpus"]},"version":{"type":"string"},"study_id":{"type":"string"},"time_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"target_segment":{"type":"string"},"interviews":{"type":"array","items":{"type":"object","required":["interview_id","source_type","respondent_profile","transcript_ref","coded_events","confidence"],"additionalProperties":false,"properties":{"interview_id":{"type":"string"},"source_type":{"type":"string","enum":["live_call","recording_import","async_form"]},"respondent_profile":{"type":"object"},"transcript_ref":{"type":"string"},"coded_events":{"type":"array","items":{"type":"object","required":["event_id","event_type","event_text","evidence_strength"],"additionalProperties":false,"properties":{"event_id":{"type":"string"},"event_type":{"type":"string","enum":["struggle","workaround","trigger","decision_criteria","objection"]},"event_text":{"type":"string"},"evidence_strength":{"type":"string","enum":["weak","moderate","strong"]}}}},"confidence":{"type":"number","minimum":0,"maximum":1}}}},"coverage_status":{"type":"string","enum":["full","partial","insufficient"]},"limitations":{"type":"array","items":{"type":"string"}}}}},
  {"schema_name":"jtbd_outcomes_schema","schema":{"type":"object","required":["artifact_type","version","study_id","job_map","outcomes","forces","confidence","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["jtbd_outcomes"]},"version":{"type":"string"},"study_id":{"type":"string"},"job_map":{"type":"array","items":{"type":"object","required":["step_id","step_name"],"additionalProperties":false,"properties":{"step_id":{"type":"string"},"step_name":{"type":"string"}}}},"outcomes":{"type":"array","items":{"type":"object","required":["outcome_id","outcome_statement","underserved_score","supporting_interview_refs"],"additionalProperties":false,"properties":{"outcome_id":{"type":"string"},"outcome_statement":{"type":"string"},"underserved_score":{"type":"number","minimum":0,"maximum":1},"supporting_interview_refs":{"type":"array","items":{"type":"string"}}}}},"forces":{"type":"array","items":{"type":"object","required":["force_type","summary"],"additionalProperties":false,"properties":{"force_type":{"type":"string","enum":["push","pull","habit","anxiety"]},"summary":{"type":"string"}}}},"confidence":{"type":"number","minimum":0,"maximum":1},"next_checks":{"type":"array","items":{"type":"string"}}}}},
  {"schema_name":"discovery_evidence_quality_schema","schema":{"type":"object","required":["artifact_type","version","study_id","quality_checks","pass_fail","blocking_issues"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["discovery_evidence_quality"]},"version":{"type":"string"},"study_id":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"pass_fail":{"type":"string","enum":["pass","fail"]},"blocking_issues":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Run interviews, capture transcripts, code outcomes, and emit structured evidence payloads; fail fast when sample coverage, consent traceability, or evidence quality checks are below threshold.`

### Bot 03 - `segment_qualification_bot`

- `accent_color`: `#0284C7`
- `title1`: `Segment Qualification`
- `title2`: `Enrichment and primary segment selection`
- `occupation`: `Segment Analyst`
- `typical_group`: `GTM / Qualification`
- `intro_message`: `I enrich segment candidates and produce one explicit primary segment decision.`
- `tags`: [`ICP`, `Segmentation`, `PrimarySegment`]
- `featured_actions`: [`Enrich candidate segments` -> `segment_data_enricher`, `Produce primary segment decision` -> `primary_segment_decision_analyst`]
- `experts`: [`segment_data_enricher`, `primary_segment_decision_analyst`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `segment_crm_signal_api`, `segment_firmographic_enrichment_api`, `segment_technographic_profile_api`, `segment_market_traction_api`, `segment_intent_signal_api`]

#### Bot 03 Tool Catalog

- `segment_crm_signal_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Salesforce REST API`
        - `Pipedrive API`
    - Provider method ids (`method_id`):
        - `hubspot.companies.search.v1`
        - `hubspot.deals.search.v1`
        - `salesforce.query.soql.v1`
        - `pipedrive.organizations.search.v1`
        - `pipedrive.deals.search.v1`
    - Call contract:
        - `segment_crm_signal_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `search_accounts`
        - `pull_deal_signals`
        - `summarize_win_loss_patterns`
    - Allowed `args` schema:
        - `provider` (string): `hubspot | salesforce | pipedrive`
        - `method_id` (string, optional): must be from provider whitelist.
        - `segment_filters` (object, required for search/pull operations)
        - `time_window` (object, optional): `{ "start_date": "...", "end_date": "..." }`
        - `pipeline_ids` (array of strings, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject `search_accounts` and `pull_deal_signals` without `segment_filters`.
        - Reject malformed `time_window` when provided.

- `segment_firmographic_enrichment_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Clearbit Enrichment API`
        - `Apollo Organization Enrichment API`
        - `People Data Labs Company Enrichment API`
    - Provider method ids (`method_id`):
        - `clearbit.company.enrich.v1`
        - `apollo.organizations.enrich.v1`
        - `apollo.organizations.bulk_enrich.v1`
        - `pdl.company.enrich.v1`
    - Constraint note:
        - `All providers are credit-metered; enforce per-run spend cap and stop execution when budget guardrail is exceeded.`

- `segment_technographic_profile_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `BuiltWith Domain API`
        - `BuiltWith Domain Live API`
        - `Wappalyzer Lookup API`
    - Provider method ids (`method_id`):
        - `builtwith.domain.api.v1`
        - `builtwith.domain.live.v1`
        - `wappalyzer.lookup.v2`
    - Constraint note:
        - `Wappalyzer lookup requires Business-tier access; fail fast when entitlement is absent.`

- `segment_market_traction_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Crunchbase API`
        - `Similarweb API V5`
        - `Google Ads Keyword Planning API`
    - Provider method ids (`method_id`):
        - `crunchbase.organizations.lookup.v1`
        - `crunchbase.organizations.search.v1`
        - `similarweb.website.traffic_and_engagement.get.v1`
        - `similarweb.website.similar_sites.get.v1`
        - `google_ads.keywordplan.generate_historical_metrics.v1`
    - Constraint note:
        - `Google Ads historical metrics are keyword-level demand proxies and must not be treated as direct TAM truth without confidence downgrading.`

- `segment_intent_signal_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `6sense API`
        - `Bombora Company Surge API`
    - Provider method ids (`method_id`):
        - `sixsense.company.identification.v1`
        - `sixsense.people.search.v1`
        - `bombora.companysurge.topics.list.v1`
        - `bombora.companysurge.company_scores.get.v1`
    - Constraint note:
        - `6sense and Bombora access are contract/plan-gated; require explicit provider health check before any scoring operation.`

#### Bot 03 Required Tool Prompt Files

- `prompts/tool_segment_crm_signal_api.md`
- `prompts/tool_segment_firmographic_enrichment_api.md`
- `prompts/tool_segment_technographic_profile_api.md`
- `prompts/tool_segment_market_traction_api.md`
- `prompts/tool_segment_intent_signal_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 03A - `segment_data_enricher`

- `name`: `segment_data_enricher`
- `fexp_description`: `Build segment evidence packs from first-party CRM and external firmographic/technographic/intent sources`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,segment_crm_signal_api,segment_firmographic_enrichment_api,segment_technographic_profile_api,segment_market_traction_api,segment_intent_signal_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"segment_enrichment_schema","schema":{"type":"object","required":["artifact_type","version","enrichment_run_id","candidate_segments","data_coverage","gaps","next_refresh_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["segment_enrichment"]},"version":{"type":"string"},"enrichment_run_id":{"type":"string"},"candidate_segments":{"type":"array","items":{"type":"object","required":["segment_id","segment_name","source_refs","firmographics","technographics","demand_signals","crm_signals","data_completeness","confidence"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"segment_name":{"type":"string"},"source_refs":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}},"firmographics":{"type":"object","required":["employee_range","revenue_range","geo_focus"],"additionalProperties":false,"properties":{"employee_range":{"type":"string"},"revenue_range":{"type":"string"},"geo_focus":{"type":"array","items":{"type":"string"}},"ownership_type":{"type":"string"}}},"technographics":{"type":"array","items":{"type":"object","required":["stack_name","adoption_signal","source_ref"],"additionalProperties":false,"properties":{"stack_name":{"type":"string"},"adoption_signal":{"type":"string","enum":["weak","moderate","strong"]},"source_ref":{"type":"string"}}}},"demand_signals":{"type":"object","required":["search_demand_index","intent_surge_level"],"additionalProperties":false,"properties":{"search_demand_index":{"type":"number","minimum":0},"intent_surge_level":{"type":"string","enum":["low","medium","high"]},"intent_source_refs":{"type":"array","items":{"type":"string"}}}},"crm_signals":{"type":"object","required":["open_pipeline_count","win_rate_proxy","avg_sales_cycle_days"],"additionalProperties":false,"properties":{"open_pipeline_count":{"type":"integer","minimum":0},"win_rate_proxy":{"type":"number","minimum":0,"maximum":1},"avg_sales_cycle_days":{"type":"number","minimum":0}}},"data_completeness":{"type":"number","minimum":0,"maximum":1},"confidence":{"type":"number","minimum":0,"maximum":1}}}},"data_coverage":{"type":"object","required":["segments_total","segments_with_full_minimum_data"],"additionalProperties":false,"properties":{"segments_total":{"type":"integer","minimum":0},"segments_with_full_minimum_data":{"type":"integer","minimum":0}}},"gaps":{"type":"array","items":{"type":"string"}},"next_refresh_checks":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"segment_data_quality_schema","schema":{"type":"object","required":["artifact_type","version","enrichment_run_id","quality_checks","pass_fail","blocking_issues"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["segment_data_quality"]},"version":{"type":"string"},"enrichment_run_id":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"pass_fail":{"type":"string","enum":["pass","fail"]},"blocking_issues":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Enrich and normalize candidate segments into evidence-complete payloads; fail fast when minimum data coverage or source traceability requirements are not met.`

### Expert 03B - `primary_segment_decision_analyst`

- `name`: `primary_segment_decision_analyst`
- `fexp_description`: `Select one primary segment using explicit weighted scoring, risk controls, and rejection rationale`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,segment_crm_signal_api,segment_market_traction_api,segment_intent_signal_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"segment_priority_matrix_schema","schema":{"type":"object","required":["artifact_type","version","evaluation_rule","weights","candidates"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["segment_priority_matrix"]},"version":{"type":"string"},"evaluation_rule":{"type":"string","enum":["fit_x_pain_x_access_x_velocity"]},"weights":{"type":"object","required":["fit","pain","access","velocity"],"additionalProperties":false,"properties":{"fit":{"type":"number","minimum":0,"maximum":1},"pain":{"type":"number","minimum":0,"maximum":1},"access":{"type":"number","minimum":0,"maximum":1},"velocity":{"type":"number","minimum":0,"maximum":1}}},"candidates":{"type":"array","items":{"type":"object","required":["segment_id","fit_score","pain_score","access_score","velocity_score","weighted_score","risks","supporting_refs"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"fit_score":{"type":"number","minimum":0,"maximum":1},"pain_score":{"type":"number","minimum":0,"maximum":1},"access_score":{"type":"number","minimum":0,"maximum":1},"velocity_score":{"type":"number","minimum":0,"maximum":1},"weighted_score":{"type":"number","minimum":0,"maximum":1},"risks":{"type":"array","items":{"type":"string"}},"supporting_refs":{"type":"array","items":{"type":"string"}}}}}}}},{"schema_name":"primary_segment_decision_schema","schema":{"type":"object","required":["artifact_type","version","selected_primary_segment","runner_up","decision_reason","rejections","confidence","next_validation_steps"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["primary_segment_decision"]},"version":{"type":"string"},"selected_primary_segment":{"type":"object","required":["segment_id","why_now","entry_motion","risk_flags"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"why_now":{"type":"string"},"entry_motion":{"type":"string","enum":["outbound","inbound","partner_led","plg_assisted"]},"risk_flags":{"type":"array","items":{"type":"string"}}}},"runner_up":{"type":"string"},"decision_reason":{"type":"string"},"rejections":{"type":"array","items":{"type":"object","required":["segment_id","rejection_reason"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"rejection_reason":{"type":"string"}}}},"confidence":{"type":"number","minimum":0,"maximum":1},"next_validation_steps":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"primary_segment_go_no_go_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","blocking_issues","override_required"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["primary_segment_go_no_go_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"override_required":{"type":"boolean"}}}}]
- `body_md`: `Score enriched segments with explicit weights and publish one primary segment decision; fail fast to no-go when evidence confidence is low or score separation is insufficient.`

### Bot 04 - `pain_alternatives_bot`

- `accent_color`: `#7C3AED`
- `title1`: `Pain and Alternatives`
- `title2`: `Pain quantification and alternative mapping`
- `occupation`: `Problem Analyst`
- `typical_group`: `GTM / Qualification`
- `intro_message`: `I quantify pain and map alternatives in structured artifacts.`
- `tags`: [`Pain`, `Alternatives`, `Evidence`]
- `featured_actions`: [`Quantify top customer pains` -> `pain_quantifier`, `Map alternative landscape` -> `alternative_mapper`]
- `experts`: [`pain_quantifier`, `alternative_mapper`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `pain_voice_of_customer_api`, `pain_support_signal_api`, `alternatives_market_scan_api`, `alternatives_traction_benchmark_api`]

#### Bot 04 Tool Catalog

- `pain_voice_of_customer_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Trustpilot API`
        - `G2 API`
        - `Reddit API`
        - `App Store Connect API`
        - `Google Play Developer API`
    - Provider method ids (`method_id`):
        - `trustpilot.reviews.list.v1`
        - `g2.reviews.list.v1`
        - `reddit.search.posts.v1`
        - `appstoreconnect.customer_reviews.list.v1`
        - `google_play.reviews.list.v1`
    - Call contract:
        - `pain_voice_of_customer_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `collect_reviews`
        - `collect_community_posts`
        - `aggregate_feedback`
    - Allowed `args` schema:
        - `provider` (string): `trustpilot | g2 | reddit | appstoreconnect | google_play`
        - `method_id` (string, optional): must be from provider whitelist.
        - `query` (string, required for `collect_community_posts` and review keyword search)
        - `app_id` (string, required for `appstoreconnect` and `google_play`)
        - `time_window` (object, optional): `{ "start_date": "...", "end_date": "..." }`
        - `min_rating` (number, optional): `1..5`
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject `collect_community_posts` without `query`.
        - Reject `appstoreconnect` and `google_play` calls without `app_id`.
        - Reject `min_rating` outside `1..5`.

- `pain_support_signal_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Intercom Conversations API`
        - `Zendesk Ticketing API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `intercom.conversations.list.v1`
        - `intercom.conversations.search.v1`
        - `zendesk.tickets.list.v1`
        - `zendesk.ticket_comments.list.v1`
        - `hubspot.tickets.search.v1`
    - Constraint note:
        - `Support channel exports can contain PII; enforce redaction policy before producing shared pdocs.`

- `alternatives_market_scan_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `SerpApi`
        - `GNews API`
        - `Product Hunt GraphQL API`
        - `Crunchbase API`
    - Provider method ids (`method_id`):
        - `serpapi.search.google.v1`
        - `gnews.search.v1`
        - `producthunt.graphql.posts.v1`
        - `crunchbase.organizations.search.v1`
        - `crunchbase.organizations.lookup.v1`
    - Constraint note:
        - `Product Hunt and Crunchbase coverage is biased toward software/startup ecosystems; downgrade confidence for offline-heavy categories.`

- `alternatives_traction_benchmark_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Similarweb API V5`
        - `BuiltWith Domain Live API`
        - `Wappalyzer Lookup API`
    - Provider method ids (`method_id`):
        - `similarweb.website.traffic_and_engagement.get.v1`
        - `similarweb.website.marketing_channel_sources.get.v1`
        - `builtwith.domain.live.v1`
        - `wappalyzer.lookup.v2`
    - Constraint note:
        - `Traffic and stack signals are modeled estimates; treat as directional evidence, never as exact ground truth.`

#### Bot 04 Required Tool Prompt Files

- `prompts/tool_pain_voice_of_customer_api.md`
- `prompts/tool_pain_support_signal_api.md`
- `prompts/tool_alternatives_market_scan_api.md`
- `prompts/tool_alternatives_traction_benchmark_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 04A - `pain_quantifier`

- `name`: `pain_quantifier`
- `fexp_description`: `Convert multi-channel pain evidence into quantified impact ranges with confidence and source traceability`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pain_voice_of_customer_api,pain_support_signal_api,alternatives_market_scan_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"pain_signal_register_schema","schema":{"type":"object","required":["artifact_type","version","channel_window","signals","coverage_status","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pain_signal_register"]},"version":{"type":"string"},"channel_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"signals":{"type":"array","items":{"type":"object","required":["pain_id","pain_statement","affected_segment","frequency_signal","severity_signal","evidence_refs"],"additionalProperties":false,"properties":{"pain_id":{"type":"string"},"pain_statement":{"type":"string"},"affected_segment":{"type":"string"},"frequency_signal":{"type":"string","enum":["low","medium","high"]},"severity_signal":{"type":"string","enum":["low","medium","high"]},"evidence_refs":{"type":"array","items":{"type":"string"}}}}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}},"coverage_status":{"type":"string","enum":["full","partial","none"]},"limitations":{"type":"array","items":{"type":"string"}},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"pain_economics_schema","schema":{"type":"object","required":["artifact_type","version","model_id","assumptions","pain_register","total_cost_range","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pain_economics"]},"version":{"type":"string"},"model_id":{"type":"string"},"assumptions":{"type":"array","items":{"type":"string"}},"pain_register":{"type":"array","items":{"type":"object","required":["pain_id","estimated_cost_per_period","cost_unit","sensitivity_level","supporting_refs"],"additionalProperties":false,"properties":{"pain_id":{"type":"string"},"estimated_cost_per_period":{"type":"number","minimum":0},"cost_unit":{"type":"string","enum":["usd_per_month","usd_per_quarter","hours_per_month","other"]},"sensitivity_level":{"type":"string","enum":["low","medium","high"]},"supporting_refs":{"type":"array","items":{"type":"string"}}}}},"total_cost_range":{"type":"object","required":["floor","target","ceiling"],"additionalProperties":false,"properties":{"floor":{"type":"number","minimum":0},"target":{"type":"number","minimum":0},"ceiling":{"type":"number","minimum":0}}},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"pain_research_readiness_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","blocking_issues","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pain_research_readiness_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","revise","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"next_checks":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Quantify pain from review, community, and support evidence; fail fast when channel coverage is partial or cost assumptions are weakly supported.`

### Expert 04B - `alternative_mapper`

- `name`: `alternative_mapper`
- `fexp_description`: `Map direct, indirect, and status-quo alternatives with explicit adoption/failure drivers and benchmarked traction`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,alternatives_market_scan_api,alternatives_traction_benchmark_api,pain_voice_of_customer_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"alternative_landscape_schema","schema":{"type":"object","required":["artifact_type","version","target_problem","alternatives","coverage_status","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["alternative_landscape"]},"version":{"type":"string"},"target_problem":{"type":"string"},"alternatives":{"type":"array","items":{"type":"object","required":["alternative_id","alternative_name","alternative_type","positioning_claim","pricing_model","adoption_reasons","failure_reasons","supporting_refs"],"additionalProperties":false,"properties":{"alternative_id":{"type":"string"},"alternative_name":{"type":"string"},"alternative_type":{"type":"string","enum":["direct_competitor","adjacent_tool","status_quo_internal","outsourcing_service"]},"positioning_claim":{"type":"string"},"pricing_model":{"type":"string"},"adoption_reasons":{"type":"array","items":{"type":"string"}},"failure_reasons":{"type":"array","items":{"type":"string"}},"supporting_refs":{"type":"array","items":{"type":"string"}}}}},"coverage_status":{"type":"string","enum":["full","partial","none"]},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"competitive_gap_matrix_schema","schema":{"type":"object","required":["artifact_type","version","evaluation_dimensions","matrix","recommended_attack_surfaces"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["competitive_gap_matrix"]},"version":{"type":"string"},"evaluation_dimensions":{"type":"array","items":{"type":"string"}},"matrix":{"type":"array","items":{"type":"object","required":["alternative_id","dimension_scores","overall_gap_score","risk_flags"],"additionalProperties":false,"properties":{"alternative_id":{"type":"string"},"dimension_scores":{"type":"object","additionalProperties":{"type":"number","minimum":0,"maximum":1}},"overall_gap_score":{"type":"number","minimum":0,"maximum":1},"risk_flags":{"type":"array","items":{"type":"string"}}}}},"recommended_attack_surfaces":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"displacement_hypotheses_schema","schema":{"type":"object","required":["artifact_type","version","prioritization_rule","hypotheses"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["displacement_hypotheses"]},"version":{"type":"string"},"prioritization_rule":{"type":"string","enum":["impact_x_confidence_x_reversibility"]},"hypotheses":{"type":"array","items":{"type":"object","required":["hypothesis_id","statement","target_alternative","expected_switch_trigger","test_signal","confidence","supporting_refs"],"additionalProperties":false,"properties":{"hypothesis_id":{"type":"string"},"statement":{"type":"string"},"target_alternative":{"type":"string"},"expected_switch_trigger":{"type":"string"},"test_signal":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1},"supporting_refs":{"type":"array","items":{"type":"string"}}}}}}}]
- `body_md`: `Map alternatives and produce displacement hypotheses; fail fast when incumbent evidence is weak or no defensible attack surface is identified.`

### Bot 05 - `positioning_offer_bot`

- `accent_color`: `#0F766E`
- `title1`: `Positioning and Offer`
- `title2`: `Value proposition and package architecture`
- `occupation`: `Positioning Architect`
- `typical_group`: `GTM / Messaging`
- `intro_message`: `I turn validated pains into positioning and offer artifacts.`
- `tags`: [`Positioning`, `Offer`, `Messaging`]
- `featured_actions`: [`Draft value proposition` -> `value_proposition_synthesizer`, `Run positioning test` -> `positioning_test_operator`]
- `experts`: [`value_proposition_synthesizer`, `positioning_test_operator`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `positioning_message_test_api`, `positioning_competitor_intel_api`, `offer_packaging_benchmark_api`, `positioning_channel_probe_api`]

#### Bot 05 Tool Catalog

- `positioning_message_test_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Typeform Create/Responses API`
        - `SurveyMonkey API v3`
        - `Qualtrics Survey and Response Export APIs`
    - Provider method ids (`method_id`):
        - `typeform.forms.create.v1`
        - `typeform.responses.list.v1`
        - `surveymonkey.surveys.create.v1`
        - `surveymonkey.surveys.responses.list.v1`
        - `qualtrics.surveys.create.v1`
        - `qualtrics.responseexports.start.v1`
        - `qualtrics.responseexports.progress.get.v1`
        - `qualtrics.responseexports.file.get.v1`
    - Call contract:
        - `positioning_message_test_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_message_test`
        - `launch_message_test`
        - `collect_message_results`
        - `score_claim_variants`
    - Allowed `args` schema:
        - `provider` (string): `typeform | surveymonkey | qualtrics`
        - `method_id` (string, optional): must be from provider whitelist.
        - `test_id` (string, optional for read/collect operations)
        - `target_segment` (string, required for create/launch operations)
        - `message_variants` (array of objects, required for create operations)
        - `success_metrics` (array of strings, optional): e.g. `clarity`, `relevance`, `preference`.
        - `time_window` (object, optional): `{ "start_date": "...", "end_date": "..." }`
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/launch operations without `target_segment` and `message_variants`.
        - Reject malformed `time_window` when provided.
        - Reject `collect_message_results` without `test_id`.

- `positioning_competitor_intel_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `SerpApi`
        - `GNews API`
        - `Crunchbase API`
        - `Similarweb API V5`
    - Provider method ids (`method_id`):
        - `serpapi.search.google.v1`
        - `serpapi.search.news.v1`
        - `gnews.search.v1`
        - `crunchbase.organizations.search.v1`
        - `crunchbase.organizations.lookup.v1`
        - `similarweb.website.traffic_and_engagement.get.v1`
        - `similarweb.website.marketing_channel_sources.get.v1`
    - Constraint note:
        - `Search and traffic APIs provide directional intelligence, not perfect market truth; require confidence downgrade when source coverage is partial.`

- `offer_packaging_benchmark_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Stripe API`
        - `Paddle API`
    - Provider method ids (`method_id`):
        - `stripe.products.list.v1`
        - `stripe.prices.list.v1`
        - `paddle.products.list.v1`
        - `paddle.prices.list.v1`
    - Constraint note:
        - `Billing catalog APIs are authoritative for own offer structure only; competitor packaging evidence must come from explicit external sources.`

- `positioning_channel_probe_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Meta Marketing API`
        - `LinkedIn Advertising API`
        - `Google Ads API`
    - Provider method ids (`method_id`):
        - `meta.adcreatives.create.v1`
        - `meta.ads_insights.get.v1`
        - `linkedin.ad_campaigns.create.v1`
        - `linkedin.ad_analytics.get.v1`
        - `google_ads.ad_group_ad.create.v1`
        - `google_ads.search_stream.query.v1`
    - Constraint note:
        - `Channel probes require active ad accounts, policy approvals, and controlled spend caps; fail fast when budget guardrail or account readiness is missing.`

#### Bot 05 Required Tool Prompt Files

- `prompts/tool_positioning_message_test_api.md`
- `prompts/tool_positioning_competitor_intel_api.md`
- `prompts/tool_offer_packaging_benchmark_api.md`
- `prompts/tool_positioning_channel_probe_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 05A - `value_proposition_synthesizer`

- `name`: `value_proposition_synthesizer`
- `fexp_description`: `Synthesize segment-specific value proposition and offer packaging boundaries from evidence and market context`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,positioning_competitor_intel_api,offer_packaging_benchmark_api,positioning_message_test_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"value_prop_schema","schema":{"type":"object","required":["artifact_type","version","target_segment","core_claim","proof_points","differentiators","objection_handling","confidence","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["value_proposition"]},"version":{"type":"string"},"target_segment":{"type":"string"},"core_claim":{"type":"string"},"proof_points":{"type":"array","items":{"type":"string"}},"differentiators":{"type":"array","items":{"type":"string"}},"objection_handling":{"type":"array","items":{"type":"object","required":["objection","response"],"additionalProperties":false,"properties":{"objection":{"type":"string"},"response":{"type":"string"}}}},"confidence":{"type":"number","minimum":0,"maximum":1},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"offer_packaging_schema","schema":{"type":"object","required":["artifact_type","version","pricing_model_type","packages","guardrails","assumptions","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["offer_packaging"]},"version":{"type":"string"},"pricing_model_type":{"type":"string","enum":["subscription","usage_based","hybrid","one_time"]},"packages":{"type":"array","items":{"type":"object","required":["package_id","package_name","intended_segment","included_outcomes","pricing_anchor","feature_fences"],"additionalProperties":false,"properties":{"package_id":{"type":"string"},"package_name":{"type":"string"},"intended_segment":{"type":"string"},"included_outcomes":{"type":"array","items":{"type":"string"}},"pricing_anchor":{"type":"string"},"feature_fences":{"type":"array","items":{"type":"string"}},"optional_add_ons":{"type":"array","items":{"type":"string"}}}}},"guardrails":{"type":"array","items":{"type":"string"}},"assumptions":{"type":"array","items":{"type":"string"}},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"positioning_narrative_brief_schema","schema":{"type":"object","required":["artifact_type","version","narrative_id","problem_statement","old_way","new_way","reason_to_believe","tone_constraints","disallowed_claims"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["positioning_narrative_brief"]},"version":{"type":"string"},"narrative_id":{"type":"string"},"problem_statement":{"type":"string"},"old_way":{"type":"string"},"new_way":{"type":"string"},"reason_to_believe":{"type":"array","items":{"type":"string"}},"tone_constraints":{"type":"array","items":{"type":"string"}},"disallowed_claims":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Build evidence-backed value proposition and package architecture; fail fast when differentiators are weak, claims are unprovable, or package fences are not coherent.`

### Expert 05B - `positioning_test_operator`

- `name`: `positioning_test_operator`
- `fexp_description`: `Run positioning and messaging experiments across research and paid channel probes, then select winner with confidence`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,positioning_message_test_api,positioning_channel_probe_api,positioning_competitor_intel_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"messaging_experiment_plan_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","target_segment","variants","channels","success_metrics","stop_conditions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["messaging_experiment_plan"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"target_segment":{"type":"string"},"variants":{"type":"array","items":{"type":"object","required":["variant_id","headline","value_claim"],"additionalProperties":false,"properties":{"variant_id":{"type":"string"},"headline":{"type":"string"},"value_claim":{"type":"string"},"cta":{"type":"string"}}}},"channels":{"type":"array","items":{"type":"string","enum":["survey_panel","meta_ads","linkedin_ads","google_ads","email_probe"]}},"success_metrics":{"type":"array","items":{"type":"string"}},"stop_conditions":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"positioning_test_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","variants_tested","winner_variant_id","result_summary","confidence","decision_reason","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["positioning_test_result"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"variants_tested":{"type":"array","items":{"type":"object","required":["variant_id","channel_results","aggregate_score"],"additionalProperties":false,"properties":{"variant_id":{"type":"string"},"channel_results":{"type":"array","items":{"type":"object","required":["channel","metric","value"],"additionalProperties":false,"properties":{"channel":{"type":"string"},"metric":{"type":"string"},"value":{"type":"number"}}}},"aggregate_score":{"type":"number","minimum":0,"maximum":1}}}},"winner_variant_id":{"type":"string"},"result_summary":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1},"decision_reason":{"type":"string"},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"positioning_claim_risk_register_schema","schema":{"type":"object","required":["artifact_type","version","claims","compliance_flags","high_risk_claims"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["positioning_claim_risk_register"]},"version":{"type":"string"},"claims":{"type":"array","items":{"type":"object","required":["claim_id","claim_text","substantiation_status","risk_level"],"additionalProperties":false,"properties":{"claim_id":{"type":"string"},"claim_text":{"type":"string"},"substantiation_status":{"type":"string","enum":["verified","partially_verified","unverified"]},"risk_level":{"type":"string","enum":["low","medium","high"]}}}},"compliance_flags":{"type":"array","items":{"type":"string"}},"high_risk_claims":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Run message experiments and emit winner decision artifacts; fail fast when sample quality is weak, winner separation is statistically ambiguous, or claim risks remain high.`

### Bot 06 - `pricing_validation_bot`

- `accent_color`: `#B45309`
- `title1`: `Pricing Validation`
- `title2`: `Price corridor and commitment evidence`
- `occupation`: `Pricing Analyst`
- `typical_group`: `GTM / Pricing`
- `intro_message`: `I validate pricing hypotheses with structured evidence artifacts.`
- `tags`: [`Pricing`, `WTP`, `Validation`]
- `featured_actions`: [`Estimate initial price corridor` -> `price_corridor_modeler`, `Verify commitment evidence` -> `commitment_evidence_verifier`]
- `experts`: [`price_corridor_modeler`, `commitment_evidence_verifier`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `pricing_research_ops_api`, `pricing_commitment_events_api`, `pricing_sales_signal_api`, `pricing_catalog_benchmark_api`]

#### Bot 06 Tool Catalog

- `pricing_research_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Typeform Create/Responses API`
        - `SurveyMonkey API v3`
        - `Qualtrics Survey and Response Export APIs`
    - Provider method ids (`method_id`):
        - `typeform.forms.create.v1`
        - `typeform.responses.list.v1`
        - `surveymonkey.surveys.create.v1`
        - `surveymonkey.surveys.responses.list.v1`
        - `qualtrics.surveys.create.v1`
        - `qualtrics.responseexports.start.v1`
        - `qualtrics.responseexports.progress.get.v1`
        - `qualtrics.responseexports.file.get.v1`
    - Call contract:
        - `pricing_research_ops_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_wtp_instrument`
        - `launch_wtp_study`
        - `collect_wtp_results`
        - `build_price_sensitivity_points`
    - Allowed `args` schema:
        - `provider` (string): `typeform | surveymonkey | qualtrics`
        - `method_id` (string, optional): must be from provider whitelist.
        - `instrument_id` (string, optional for read/export operations)
        - `target_segment` (string, required for create/launch operations)
        - `hypothesis_refs` (array of strings, required for create operations)
        - `price_points` (array of numbers, required for sensitivity operations)
        - `time_window` (object, optional): `{ "start_date": "...", "end_date": "..." }`
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/launch operations without `target_segment` and `hypothesis_refs`.
        - Reject sensitivity operations without `price_points`.
        - Reject malformed `time_window` when provided.

- `pricing_commitment_events_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Stripe API`
        - `Paddle API`
        - `Chargebee API`
    - Provider method ids (`method_id`):
        - `stripe.checkout.sessions.list.v1`
        - `stripe.payment_intents.list.v1`
        - `stripe.subscriptions.list.v1`
        - `stripe.invoices.list.v1`
        - `paddle.transactions.list.v1`
        - `paddle.transactions.get.v1`
        - `chargebee.subscriptions.list.v1`
        - `chargebee.invoices.list.v1`
    - Constraint note:
        - `Revenue signals must be normalized for currency, refund state, and tax inclusion before cross-provider comparison.`

- `pricing_sales_signal_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Salesforce REST API`
        - `Pipedrive API`
    - Provider method ids (`method_id`):
        - `hubspot.deals.search.v1`
        - `salesforce.query.soql.v1`
        - `pipedrive.deals.search.v1`
        - `pipedrive.itemsearch.search.v1`
    - Constraint note:
        - `Deal-stage and discount fields vary by CRM customization; enforce explicit field mapping and fail fast when mandatory mappings are absent.`

- `pricing_catalog_benchmark_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Stripe API`
        - `Paddle API`
        - `SerpApi`
        - `GNews API`
    - Provider method ids (`method_id`):
        - `stripe.products.list.v1`
        - `stripe.prices.list.v1`
        - `paddle.products.list.v1`
        - `paddle.prices.list.v1`
        - `serpapi.search.google.v1`
        - `gnews.search.v1`
    - Constraint note:
        - `External pricing references can be incomplete or stale; any benchmark without timestamped source refs must be marked low confidence.`

#### Bot 06 Required Tool Prompt Files

- `prompts/tool_pricing_research_ops_api.md`
- `prompts/tool_pricing_commitment_events_api.md`
- `prompts/tool_pricing_sales_signal_api.md`
- `prompts/tool_pricing_catalog_benchmark_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 06A - `price_corridor_modeler`

- `name`: `price_corridor_modeler`
- `fexp_description`: `Estimate floor-target-ceiling pricing corridor from stated willingness-to-pay, segment fit, and benchmark context`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pricing_research_ops_api,pricing_sales_signal_api,pricing_catalog_benchmark_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"preliminary_price_corridor_schema","schema":{"type":"object","required":["artifact_type","version","currency","corridor","segment_corridors","assumptions","confidence","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["preliminary_price_corridor"]},"version":{"type":"string"},"currency":{"type":"string"},"corridor":{"type":"object","required":["floor","target","ceiling"],"additionalProperties":false,"properties":{"floor":{"type":"number","minimum":0},"target":{"type":"number","minimum":0},"ceiling":{"type":"number","minimum":0}}},"segment_corridors":{"type":"array","items":{"type":"object","required":["segment_id","floor","target","ceiling","confidence"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"floor":{"type":"number","minimum":0},"target":{"type":"number","minimum":0},"ceiling":{"type":"number","minimum":0},"confidence":{"type":"number","minimum":0,"maximum":1}}}},"assumptions":{"type":"array","items":{"type":"string"}},"confidence":{"type":"number","minimum":0,"maximum":1},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"price_sensitivity_curve_schema","schema":{"type":"object","required":["artifact_type","version","method","sample_size","curve_points","interpretation","limitations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["price_sensitivity_curve"]},"version":{"type":"string"},"method":{"type":"string","enum":["van_westendorp","gabor_granger","hybrid"]},"sample_size":{"type":"integer","minimum":1},"curve_points":{"type":"array","items":{"type":"object","required":["price","too_cheap_share","cheap_share","expensive_share","too_expensive_share"],"additionalProperties":false,"properties":{"price":{"type":"number","minimum":0},"too_cheap_share":{"type":"number","minimum":0,"maximum":1},"cheap_share":{"type":"number","minimum":0,"maximum":1},"expensive_share":{"type":"number","minimum":0,"maximum":1},"too_expensive_share":{"type":"number","minimum":0,"maximum":1}}}},"interpretation":{"type":"array","items":{"type":"string"}},"limitations":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"pricing_assumption_register_schema","schema":{"type":"object","required":["artifact_type","version","assumptions","high_risk_assumptions","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pricing_assumption_register"]},"version":{"type":"string"},"assumptions":{"type":"array","items":{"type":"object","required":["assumption_id","statement","impact_level","evidence_status"],"additionalProperties":false,"properties":{"assumption_id":{"type":"string"},"statement":{"type":"string"},"impact_level":{"type":"string","enum":["low","medium","high"]},"evidence_status":{"type":"string","enum":["supported","partially_supported","unsupported"]}}}},"high_risk_assumptions":{"type":"array","items":{"type":"string"}},"next_checks":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Model pricing corridors from research and market signals; fail fast when sample quality is weak, corridor spread is unstable, or core assumptions are unsupported.`

### Expert 06B - `commitment_evidence_verifier`

- `name`: `commitment_evidence_verifier`
- `fexp_description`: `Verify pricing hypotheses against observed commitment signals from billing and sales pipelines`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pricing_commitment_events_api,pricing_sales_signal_api,pricing_research_ops_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"pricing_commitment_evidence_schema","schema":{"type":"object","required":["artifact_type","version","time_window","signals","coverage_status","confidence","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pricing_commitment_evidence"]},"version":{"type":"string"},"time_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"signals":{"type":"array","items":{"type":"object","required":["signal_id","signal_type","segment_id","observed_value","interpretation","supporting_refs"],"additionalProperties":false,"properties":{"signal_id":{"type":"string"},"signal_type":{"type":"string","enum":["checkout_start_rate","checkout_completion_rate","trial_to_paid_rate","discount_acceptance_rate","quote_acceptance_rate","payment_failure_rate","refund_rate"]},"segment_id":{"type":"string"},"observed_value":{"type":"number"},"interpretation":{"type":"string"},"supporting_refs":{"type":"array","items":{"type":"string"}}}}},"coverage_status":{"type":"string","enum":["full","partial","none"]},"confidence":{"type":"number","minimum":0,"maximum":1},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"validated_price_hypothesis_schema","schema":{"type":"object","required":["artifact_type","version","hypothesis_status","tested_price_point","segment_id","commitment_evidence","counter_evidence","recommended_next_step","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["validated_price_hypothesis"]},"version":{"type":"string"},"hypothesis_status":{"type":"string","enum":["validated","partially_validated","rejected"]},"tested_price_point":{"type":"number","minimum":0},"segment_id":{"type":"string"},"commitment_evidence":{"type":"array","items":{"type":"string"}},"counter_evidence":{"type":"array","items":{"type":"string"}},"recommended_next_step":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"pricing_go_no_go_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","blocking_issues","override_required","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pricing_go_no_go_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"override_required":{"type":"boolean"},"next_checks":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Compare stated willingness-to-pay with observed commitment behavior and produce go/no-go outcomes; fail fast when commitment coverage is partial or evidence conflicts are unresolved.`

### Bot 07 - `experiment_design_bot`

- `accent_color`: `#475569`
- `title1`: `Experiment Design`
- `title2`: `Test-design and reliability checks`
- `occupation`: `Experiment Architect`
- `typical_group`: `GTM / Experiments`
- `intro_message`: `I turn key GTM risks into executable experiments with guardrails and explicit approval criteria.`
- `tags`: [`Experiment`, `Hypothesis`, `Reliability`]
- `featured_actions`: [`Draft experiment card` -> `hypothesis_architect`, `Run reliability approval` -> `reliability_checker`]
- `experts`: [`hypothesis_architect`, `reliability_checker`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `experiment_backlog_ops_api`, `experiment_runtime_config_api`, `experiment_guardrail_metrics_api`, `experiment_instrumentation_quality_api`]

#### Bot 07 Tool Catalog

- `experiment_backlog_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Jira REST API`
        - `Linear GraphQL API`
        - `Notion API`
    - Provider method ids (`method_id`):
        - `jira.issues.create.v1`
        - `jira.issues.search.v1`
        - `linear.issues.create.v1`
        - `linear.issues.list.v1`
        - `notion.pages.create.v1`
        - `notion.pages.search.v1`
    - Call contract:
        - `experiment_backlog_ops_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_experiment_card`
        - `update_experiment_card`
        - `list_experiment_backlog`
        - `link_hypothesis_to_card`
    - Allowed `args` schema:
        - `provider` (string): `jira | linear | notion`
        - `method_id` (string, optional): must be from provider whitelist.
        - `experiment_id` (string, optional for update/link operations)
        - `hypothesis_id` (string, required for create/link operations)
        - `owner` (string, optional)
        - `priority` (string, optional): `p0 | p1 | p2 | p3`
        - `due_date` (string, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/link operations without `hypothesis_id`.
        - Reject update operations without `experiment_id`.

- `experiment_runtime_config_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `LaunchDarkly API`
        - `Statsig Console API`
        - `Optimizely Feature Experimentation API`
    - Provider method ids (`method_id`):
        - `launchdarkly.flags.get.v1`
        - `launchdarkly.flags.patch.v1`
        - `statsig.experiments.create.v1`
        - `statsig.experiments.update.v1`
        - `optimizely.experiments.create.v1`
        - `optimizely.experiments.get.v1`
    - Constraint note:
        - `Runtime config APIs are environment-sensitive; enforce explicit environment target and refuse writes to production when approval artifact is missing.`

- `experiment_guardrail_metrics_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `PostHog Insights API`
        - `Mixpanel Query API`
        - `Amplitude Dashboard REST API`
        - `Google Analytics Data API`
    - Provider method ids (`method_id`):
        - `posthog.insights.trend.query.v1`
        - `posthog.insights.funnel.query.v1`
        - `mixpanel.retention.query.v1`
        - `mixpanel.frequency.query.v1`
        - `amplitude.dashboardrest.chart.get.v1`
        - `ga4.properties.run_report.v1`
    - Constraint note:
        - `Metric definitions must be normalized before cross-tool comparison; fail fast when denominator definitions differ between sources.`

- `experiment_instrumentation_quality_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Segment Public API`
        - `Sentry Issues API`
    - Provider method ids (`method_id`):
        - `segment.tracking_plans.list.v1`
        - `segment.tracking_plans.get.v1`
        - `sentry.organizations.issues.list.v1`
    - Constraint note:
        - `If tracking plan coverage is incomplete or critical telemetry errors are unresolved, approval must return no_go.`

#### Bot 07 Required Tool Prompt Files

- `prompts/tool_experiment_backlog_ops_api.md`
- `prompts/tool_experiment_runtime_config_api.md`
- `prompts/tool_experiment_guardrail_metrics_api.md`
- `prompts/tool_experiment_instrumentation_quality_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 07A - `hypothesis_architect`

- `name`: `hypothesis_architect`
- `fexp_description`: `Convert risk backlog into high-quality, executable experiment cards with explicit metrics and stop rules`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,experiment_backlog_ops_api,experiment_guardrail_metrics_api,experiment_instrumentation_quality_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"experiment_card_draft_schema","schema":{"type":"object","required":["artifact_type","version","experiment_cards","prioritization_rule","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_card_draft"]},"version":{"type":"string"},"prioritization_rule":{"type":"string","enum":["impact_x_confidence_x_reversibility"]},"experiment_cards":{"type":"array","items":{"type":"object","required":["experiment_id","hypothesis","target_segment","primary_metric","guardrail_metrics","sample_definition","runbook","stop_conditions","owner","priority_rank"],"additionalProperties":false,"properties":{"experiment_id":{"type":"string"},"hypothesis":{"type":"string"},"target_segment":{"type":"string"},"primary_metric":{"type":"string"},"guardrail_metrics":{"type":"array","items":{"type":"string"}},"sample_definition":{"type":"object","required":["unit","target_n","allocation"],"additionalProperties":false,"properties":{"unit":{"type":"string"},"target_n":{"type":"integer","minimum":1},"allocation":{"type":"string"}}},"runbook":{"type":"array","items":{"type":"string"}},"stop_conditions":{"type":"array","items":{"type":"string"}},"owner":{"type":"string"},"priority_rank":{"type":"integer","minimum":1}}}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"experiment_measurement_spec_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","metrics","event_requirements","quality_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_measurement_spec"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"metrics":{"type":"array","items":{"type":"object","required":["metric_id","metric_name","metric_type","formula","data_source"],"additionalProperties":false,"properties":{"metric_id":{"type":"string"},"metric_name":{"type":"string"},"metric_type":{"type":"string","enum":["primary","guardrail","diagnostic"]},"formula":{"type":"string"},"data_source":{"type":"string"}}}},"event_requirements":{"type":"array","items":{"type":"string"}},"quality_checks":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"experiment_backlog_prioritization_schema","schema":{"type":"object","required":["artifact_type","version","backlog","top_candidates","deferred_items"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_backlog_prioritization"]},"version":{"type":"string"},"backlog":{"type":"array","items":{"type":"object","required":["experiment_id","impact_score","confidence_score","reversibility_score","priority_score"],"additionalProperties":false,"properties":{"experiment_id":{"type":"string"},"impact_score":{"type":"number","minimum":0,"maximum":1},"confidence_score":{"type":"number","minimum":0,"maximum":1},"reversibility_score":{"type":"number","minimum":0,"maximum":1},"priority_score":{"type":"number","minimum":0,"maximum":1}}}},"top_candidates":{"type":"array","items":{"type":"string"}},"deferred_items":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce high-quality experiment cards and measurement specs; fail fast when metric definitions are ambiguous or instrumentation prerequisites are missing.`

### Expert 07B - `reliability_checker`

- `name`: `reliability_checker`
- `fexp_description`: `Validate reliability conditions before experiment execution`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,experiment_runtime_config_api,experiment_guardrail_metrics_api,experiment_instrumentation_quality_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"experiment_reliability_report_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","reliability_checks","pass_fail","blocking_issues","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_reliability_report"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"reliability_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"pass_fail":{"type":"string","enum":["pass","fail"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"experiment_approval_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","approval_state","approval_reason","blocking_issues","required_fixes","go_live_constraints"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_approval"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"approval_state":{"type":"string","enum":["approved","revise","rejected"]},"approval_reason":{"type":"string"},"blocking_issues":{"type":"array","items":{"type":"string"}},"required_fixes":{"type":"array","items":{"type":"string"}},"go_live_constraints":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"experiment_stop_rule_evaluation_schema","schema":{"type":"object","required":["artifact_type","version","experiment_id","evaluation_window","stop_rule_status","triggered_rules","recommended_action"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["experiment_stop_rule_evaluation"]},"version":{"type":"string"},"experiment_id":{"type":"string"},"evaluation_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"stop_rule_status":{"type":"string","enum":["not_triggered","triggered_guardrail","triggered_success","inconclusive"]},"triggered_rules":{"type":"array","items":{"type":"string"}},"recommended_action":{"type":"string","enum":["continue","pause","stop","ship_variant"]}}}}]
- `body_md`: `Run reliability gate checks and emit approval decisions; fail fast when guardrail definitions, runtime rollout controls, or telemetry quality checks are not production-safe.`

### Bot 08 - `mvp_validation_bot`

- `accent_color`: `#1D4ED8`
- `title1`: `MVP Validation`
- `title2`: `MVP run operations and telemetry integrity`
- `occupation`: `MVP Operator`
- `typical_group`: `GTM / Validation`
- `intro_message`: `I run MVP tests and produce auditable decision artifacts.`
- `tags`: [`MVP`, `Telemetry`, `Validation`]
- `featured_actions`: [`Run approved MVP test` -> `mvp_flow_operator`, `Issue telemetry decision memo` -> `telemetry_integrity_analyst`]
- `experts`: [`mvp_flow_operator`, `telemetry_integrity_analyst`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `mvp_experiment_orchestration_api`, `mvp_telemetry_api`, `mvp_feedback_capture_api`, `mvp_instrumentation_health_api`]

#### Bot 08 Tool Catalog

- `mvp_experiment_orchestration_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `LaunchDarkly API`
        - `Statsig Console API`
        - `Jira REST API`
    - Provider method ids (`method_id`):
        - `launchdarkly.flags.get.v1`
        - `launchdarkly.flags.patch.v1`
        - `statsig.experiments.create.v1`
        - `statsig.experiments.update.v1`
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
    - Call contract:
        - `mvp_experiment_orchestration_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `prepare_mvp_rollout`
        - `start_mvp_rollout`
        - `pause_mvp_rollout`
        - `rollback_mvp_rollout`
    - Allowed `args` schema:
        - `provider` (string): `launchdarkly | statsig | jira`
        - `method_id` (string, optional): must be from provider whitelist.
        - `run_id` (string, required for start/pause/rollback operations)
        - `environment` (string, required): `staging | preprod | production`
        - `rollout_percentage` (number, optional): `0..100`
        - `approval_ref` (string, required for production actions)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject lifecycle operations without `run_id`.
        - Reject production actions without `approval_ref`.
        - Reject `rollout_percentage` outside `0..100`.

- `mvp_telemetry_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `PostHog Insights API`
        - `Mixpanel Query API`
        - `Amplitude Dashboard REST API`
        - `Google Analytics Data API`
        - `Datadog Metrics API`
    - Provider method ids (`method_id`):
        - `posthog.insights.trend.query.v1`
        - `posthog.insights.funnel.query.v1`
        - `mixpanel.funnels.query.v1`
        - `mixpanel.retention.query.v1`
        - `amplitude.dashboardrest.chart.get.v1`
        - `ga4.properties.run_report.v1`
        - `datadog.metrics.timeseries.query.v1`
    - Constraint note:
        - `Metric definitions and event semantics must be normalized before decisioning; fail fast when key metric lineage is ambiguous.`

- `mvp_feedback_capture_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Intercom Conversations API`
        - `Typeform Responses API`
        - `Zendesk Ticketing API`
    - Provider method ids (`method_id`):
        - `intercom.conversations.list.v1`
        - `intercom.conversations.search.v1`
        - `typeform.responses.list.v1`
        - `zendesk.tickets.search.v1`
        - `zendesk.ticket_comments.list.v1`
    - Constraint note:
        - `Feedback channels can contain PII and non-representative outliers; require redaction and segment-weight checks before synthesis.`

- `mvp_instrumentation_health_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Segment Public API`
        - `Sentry Issues API`
    - Provider method ids (`method_id`):
        - `segment.tracking_plans.list.v1`
        - `segment.tracking_plans.get.v1`
        - `sentry.organizations.issues.list.v1`
    - Constraint note:
        - `If required events are missing in tracking plan or high-severity telemetry issues are unresolved, decision memo must downgrade confidence or fail no_go.`

#### Bot 08 Required Tool Prompt Files

- `prompts/tool_mvp_experiment_orchestration_api.md`
- `prompts/tool_mvp_telemetry_api.md`
- `prompts/tool_mvp_feedback_capture_api.md`
- `prompts/tool_mvp_instrumentation_health_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 08A - `mvp_flow_operator`

- `name`: `mvp_flow_operator`
- `fexp_description`: `Execute approved MVP rollout on bounded cohorts with strict guardrails and rollback controls`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,mvp_experiment_orchestration_api,mvp_telemetry_api,mvp_feedback_capture_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"mvp_run_log_schema","schema":{"type":"object","required":["artifact_type","version","run_id","hypothesis_ref","cohort_definition","rollout_plan","activation_path","delivery_log","guardrail_events","status"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["mvp_run_log"]},"version":{"type":"string"},"run_id":{"type":"string"},"hypothesis_ref":{"type":"string"},"cohort_definition":{"type":"object","required":["segment_id","target_n","allocation"],"additionalProperties":false,"properties":{"segment_id":{"type":"string"},"target_n":{"type":"integer","minimum":1},"allocation":{"type":"string"}}},"rollout_plan":{"type":"array","items":{"type":"string"}},"activation_path":{"type":"array","items":{"type":"string"}},"delivery_log":{"type":"array","items":{"type":"object","required":["ts","event","status"],"additionalProperties":false,"properties":{"ts":{"type":"string"},"event":{"type":"string"},"status":{"type":"string","enum":["ok","warn","fail"]},"notes":{"type":"string"}}}},"guardrail_events":{"type":"array","items":{"type":"string"}},"status":{"type":"string","enum":["planned","running","paused","rolled_back","completed"]}}}},{"schema_name":"mvp_rollout_incident_schema","schema":{"type":"object","required":["artifact_type","version","run_id","incidents","impact_summary","resolved"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["mvp_rollout_incident"]},"version":{"type":"string"},"run_id":{"type":"string"},"incidents":{"type":"array","items":{"type":"object","required":["incident_id","severity","description","mitigation"],"additionalProperties":false,"properties":{"incident_id":{"type":"string"},"severity":{"type":"string","enum":["low","medium","high","critical"]},"description":{"type":"string"},"mitigation":{"type":"string"}}}},"impact_summary":{"type":"array","items":{"type":"string"}},"resolved":{"type":"boolean"}}}},{"schema_name":"mvp_feedback_digest_schema","schema":{"type":"object","required":["artifact_type","version","run_id","feedback_window","themes","critical_quotes","sentiment_distribution","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["mvp_feedback_digest"]},"version":{"type":"string"},"run_id":{"type":"string"},"feedback_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"themes":{"type":"array","items":{"type":"object","required":["theme_id","theme_summary","evidence_count","supporting_refs"],"additionalProperties":false,"properties":{"theme_id":{"type":"string"},"theme_summary":{"type":"string"},"evidence_count":{"type":"integer","minimum":0},"supporting_refs":{"type":"array","items":{"type":"string"}}}}},"critical_quotes":{"type":"array","items":{"type":"string"}},"sentiment_distribution":{"type":"object","additionalProperties":{"type":"number","minimum":0,"maximum":1}},"next_checks":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Operate MVP rollout with strict lifecycle controls and emit auditable run artifacts; fail fast on guardrail breaches, incident escalation, or missing execution traceability.`

### Expert 08B - `telemetry_integrity_analyst`

- `name`: `telemetry_integrity_analyst`
- `fexp_description`: `Validate telemetry quality and produce threshold-based decision`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,mvp_telemetry_api,mvp_instrumentation_health_api,mvp_feedback_capture_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"telemetry_quality_report_schema","schema":{"type":"object","required":["artifact_type","version","run_id","quality_checks","coverage_status","lineage_status","blocking_issues","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["telemetry_quality_report"]},"version":{"type":"string"},"run_id":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"coverage_status":{"type":"string","enum":["full","partial","none"]},"lineage_status":{"type":"string","enum":["verified","partial","unknown"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"telemetry_decision_memo_schema","schema":{"type":"object","required":["artifact_type","version","run_id","metric_summary","decision","decision_reason","next_step","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["telemetry_decision_memo"]},"version":{"type":"string"},"run_id":{"type":"string"},"metric_summary":{"type":"object","required":["primary_metric","guardrails","window"],"additionalProperties":false,"properties":{"primary_metric":{"type":"object"},"guardrails":{"type":"array","items":{"type":"object"}},"window":{"type":"string"}}},"decision":{"type":"string","enum":["scale","iterate","stop"]},"decision_reason":{"type":"string"},"next_step":{"type":"string"},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"mvp_scale_readiness_gate_schema","schema":{"type":"object","required":["artifact_type","version","run_id","gate_status","blocking_issues","override_required","recommended_action"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["mvp_scale_readiness_gate"]},"version":{"type":"string"},"run_id":{"type":"string"},"gate_status":{"type":"string","enum":["go","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"override_required":{"type":"boolean"},"recommended_action":{"type":"string","enum":["scale","iterate","stop"]}}}}]
- `body_md`: `Audit telemetry integrity and issue final decision memos; fail fast when event coverage, metric lineage, or instrumentation health does not meet reliability thresholds.`

### Bot 09 - `pipeline_qualification_bot`

- `accent_color`: `#0369A1`
- `title1`: `Pipeline Qualification`
- `title2`: `Prospecting and qualification mapping`
- `occupation`: `Pipeline Operator`
- `typical_group`: `GTM / Pipeline`
- `intro_message`: `I generate qualified early pipeline and qualification artifacts.`
- `tags`: [`Pipeline`, `Prospecting`, `Qualification`]
- `featured_actions`: [`Run prospecting batch` -> `prospect_acquisition_operator`, `Build qualification map` -> `qualification_mapper`]
- `experts`: [`prospect_acquisition_operator`, `qualification_mapper`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `pipeline_crm_api`, `pipeline_prospecting_enrichment_api`, `pipeline_outreach_execution_api`, `pipeline_engagement_signal_api`]

#### Bot 09 Tool Catalog

- `pipeline_crm_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Salesforce REST API`
        - `Pipedrive API`
        - `Zendesk Sell API`
    - Provider method ids (`method_id`):
        - `hubspot.contacts.search.v1`
        - `hubspot.companies.search.v1`
        - `hubspot.deals.search.v1`
        - `salesforce.query.soql.v1`
        - `pipedrive.itemsearch.search.v1`
        - `pipedrive.deals.search.v1`
        - `zendesk_sell.contacts.list.v1`
        - `zendesk_sell.deals.list.v1`
    - Call contract:
        - `pipeline_crm_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `search_accounts`
        - `search_contacts`
        - `pull_pipeline_snapshot`
        - `upsert_qualification_fields`
    - Allowed `args` schema:
        - `provider` (string): `hubspot | salesforce | pipedrive | zendesk_sell`
        - `method_id` (string, optional): must be from provider whitelist.
        - `segment_filters` (object, required for search operations)
        - `pipeline_stage_filters` (array of strings, optional)
        - `account_id` (string, required for upsert operations)
        - `qualification_payload` (object, required for upsert operations)
        - `time_window` (object, optional): `{ "start_date": "...", "end_date": "..." }`
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject search operations without `segment_filters`.
        - Reject `upsert_qualification_fields` without `account_id` and `qualification_payload`.
        - Reject malformed `time_window` when provided.

- `pipeline_prospecting_enrichment_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Apollo API`
        - `Clearbit Enrichment API`
        - `People Data Labs Person Enrichment API`
    - Provider method ids (`method_id`):
        - `apollo.people.search.v1`
        - `apollo.people.enrich.v1`
        - `apollo.contacts.create.v1`
        - `clearbit.company.enrich.v1`
        - `pdl.person.enrich.v1`
    - Constraint note:
        - `Enrichment providers are credit-metered and can create duplicate contacts; enforce dedupe keys and per-run spend limits before write operations.`

- `pipeline_outreach_execution_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Apollo API`
        - `Outreach API`
        - `Salesloft API`
    - Provider method ids (`method_id`):
        - `apollo.sequences.contacts.add.v1`
        - `outreach.prospects.list.v1`
        - `outreach.prospects.create.v1`
        - `outreach.sequences.list.v1`
        - `salesloft.people.list.v1`
        - `salesloft.cadence_memberships.create.v1`
    - Constraint note:
        - `Sequence/cadence enrollment is permission-sensitive; fail fast when user/token lacks enrollment scope or sequence state is invalid.`

- `pipeline_engagement_signal_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Outreach API`
        - `Salesloft API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `outreach.prospects.list.v1`
        - `salesloft.people.list.v1`
        - `hubspot.calls.list.v1`
        - `hubspot.notes.list.v1`
    - Constraint note:
        - `Engagement fields are provider-specific and not directly comparable; normalize status definitions before qualification scoring.`

#### Bot 09 Required Tool Prompt Files

- `prompts/tool_pipeline_crm_api.md`
- `prompts/tool_pipeline_prospecting_enrichment_api.md`
- `prompts/tool_pipeline_outreach_execution_api.md`
- `prompts/tool_pipeline_engagement_signal_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 09A - `prospect_acquisition_operator`

- `name`: `prospect_acquisition_operator`
- `fexp_description`: `Source, enrich, and enroll ICP-aligned prospects into controlled outbound motions`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pipeline_prospecting_enrichment_api,pipeline_outreach_execution_api,pipeline_crm_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"prospecting_batch_schema","schema":{"type":"object","required":["artifact_type","version","batch_id","target_segment","source_channels","prospects","batch_quality","limitations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["prospecting_batch"]},"version":{"type":"string"},"batch_id":{"type":"string"},"target_segment":{"type":"string"},"source_channels":{"type":"array","items":{"type":"string"}},"prospects":{"type":"array","items":{"type":"object","required":["prospect_id","full_name","company_name","role","fit_score","contactability_score","source_refs"],"additionalProperties":false,"properties":{"prospect_id":{"type":"string"},"full_name":{"type":"string"},"company_name":{"type":"string"},"role":{"type":"string"},"fit_score":{"type":"number","minimum":0,"maximum":1},"contactability_score":{"type":"number","minimum":0,"maximum":1},"source_refs":{"type":"array","items":{"type":"string"}}}}},"batch_quality":{"type":"object","required":["total_candidates","accepted_candidates","dedupe_ratio"],"additionalProperties":false,"properties":{"total_candidates":{"type":"integer","minimum":0},"accepted_candidates":{"type":"integer","minimum":0},"dedupe_ratio":{"type":"number","minimum":0,"maximum":1}}},"limitations":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"outreach_execution_log_schema","schema":{"type":"object","required":["artifact_type","version","batch_id","sequence_plan","enrollment_events","delivery_summary","blocked_items"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["outreach_execution_log"]},"version":{"type":"string"},"batch_id":{"type":"string"},"sequence_plan":{"type":"array","items":{"type":"object","required":["provider","sequence_id","segment_target"],"additionalProperties":false,"properties":{"provider":{"type":"string"},"sequence_id":{"type":"string"},"segment_target":{"type":"string"}}}},"enrollment_events":{"type":"array","items":{"type":"object","required":["event_id","prospect_id","provider","status"],"additionalProperties":false,"properties":{"event_id":{"type":"string"},"prospect_id":{"type":"string"},"provider":{"type":"string"},"status":{"type":"string","enum":["enrolled","skipped","failed"]},"reason":{"type":"string"}}}},"delivery_summary":{"type":"object","additionalProperties":{"type":"number"}},"blocked_items":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"prospect_data_quality_schema","schema":{"type":"object","required":["artifact_type","version","batch_id","quality_checks","pass_fail","blocking_issues"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["prospect_data_quality"]},"version":{"type":"string"},"batch_id":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","result","notes"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"result":{"type":"string","enum":["pass","warn","fail"]},"notes":{"type":"string"}}}},"pass_fail":{"type":"string","enum":["pass","fail"]},"blocking_issues":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Build prospecting batches and enrollment logs with traceability; fail fast when dedupe, contactability quality, or outreach enrollment prerequisites are not met.`

### Expert 09B - `qualification_mapper`

- `name`: `qualification_mapper`
- `fexp_description`: `Map qualification state and buying blockers`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pipeline_crm_api,pipeline_engagement_signal_api,pipeline_outreach_execution_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"qualification_map_schema","schema":{"type":"object","required":["artifact_type","version","rubric","accounts","coverage_status","confidence"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["qualification_map"]},"version":{"type":"string"},"rubric":{"type":"string","enum":["icp_fit_x_pain_x_authority_x_timing"]},"accounts":{"type":"array","items":{"type":"object","required":["account_id","account_name","qualification_state","qualification_score","buying_committee","blockers","next_action"],"additionalProperties":false,"properties":{"account_id":{"type":"string"},"account_name":{"type":"string"},"qualification_state":{"type":"string","enum":["unqualified","qualified","high_priority"]},"qualification_score":{"type":"number","minimum":0,"maximum":1},"buying_committee":{"type":"array","items":{"type":"object","required":["role","contact_ref","coverage_status"],"additionalProperties":false,"properties":{"role":{"type":"string"},"contact_ref":{"type":"string"},"coverage_status":{"type":"string","enum":["covered","partial","missing"]}}}},"blockers":{"type":"array","items":{"type":"string"}},"next_action":{"type":"string"}}}},"coverage_status":{"type":"string","enum":["full","partial","none"]},"confidence":{"type":"number","minimum":0,"maximum":1}}}},{"schema_name":"buying_committee_coverage_schema","schema":{"type":"object","required":["artifact_type","version","accounts","coverage_gaps","recommended_fills"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["buying_committee_coverage"]},"version":{"type":"string"},"accounts":{"type":"array","items":{"type":"object","required":["account_id","required_roles","covered_roles","missing_roles"],"additionalProperties":false,"properties":{"account_id":{"type":"string"},"required_roles":{"type":"array","items":{"type":"string"}},"covered_roles":{"type":"array","items":{"type":"string"}},"missing_roles":{"type":"array","items":{"type":"string"}}}}},"coverage_gaps":{"type":"array","items":{"type":"string"}},"recommended_fills":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"qualification_go_no_go_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","in_scope_accounts","out_of_scope_accounts","blocking_issues","next_checks"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["qualification_go_no_go_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","no_go"]},"in_scope_accounts":{"type":"array","items":{"type":"string"}},"out_of_scope_accounts":{"type":"array","items":{"type":"string"}},"blocking_issues":{"type":"array","items":{"type":"string"}},"next_checks":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Map qualification states and decision blockers into execution-ready account views; fail fast when committee coverage is missing or qualification confidence is below threshold.`

### Bot 10 - `creative_paid_channels_bot`

- `accent_color`: `#BE185D`
- `title1`: `Creative and Paid Channels`
- `title2`: `Creative variants and one-platform paid tests`
- `occupation`: `Paid Growth Operator`
- `typical_group`: `GTM / Demand`
- `intro_message`: `I create testable creatives and run controlled paid-channel tests.`
- `tags`: [`Creative`, `Paid`, `Acquisition`]
- `featured_actions`: [`Generate creative variant pack` -> `creative_producer`, `Launch one-platform paid test` -> `paid_channel_operator`]
- `experts`: [`creative_producer`, `paid_channel_operator`]
- `skills`: [`skill_meta_ads_execution`, `skill_google_ads_execution`, `skill_x_ads_execution`]
- `tools`: [`flexus_policy_document`, `print_widget`, `creative_asset_ops_api`, `paid_channel_execution_api`, `paid_channel_measurement_api`, `creative_feedback_capture_api`]

#### Bot 10 Tool Catalog

- `creative_asset_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Meta Marketing API`
        - `Google Ads API`
        - `LinkedIn Marketing API`
    - Provider method ids (`method_id`):
        - `meta.adcreatives.create.v1`
        - `meta.adimages.create.v1`
        - `meta.adcreatives.list.v1`
        - `google_ads.ad_group_ad.create.v1`
        - `google_ads.asset.create.v1`
        - `linkedin.creatives.create.v1`
        - `linkedin.creatives.list.v1`
    - Call contract:
        - `creative_asset_ops_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_creative_variant`
        - `upload_creative_asset`
        - `validate_platform_specs`
        - `publish_creative_to_platform`
    - Allowed `args` schema:
        - `provider` (string): `meta | google_ads | linkedin`
        - `method_id` (string, optional): must be from provider whitelist.
        - `variant_id` (string, required for publish operations)
        - `asset_payload` (object, required for create/upload operations)
        - `platform_specs` (object, required for validation operations)
        - `campaign_objective` (string, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/upload operations without `asset_payload`.
        - Reject publish operations without `variant_id`.
        - Reject validation operations without `platform_specs`.

- `paid_channel_execution_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Meta Marketing API`
        - `Google Ads API`
        - `LinkedIn Marketing API`
        - `X Ads API`
    - Provider method ids (`method_id`):
        - `meta.campaigns.create.v1`
        - `meta.adsets.create.v1`
        - `meta.ads_insights.get.v1`
        - `google_ads.campaigns.mutate.v1`
        - `google_ads.search_stream.query.v1`
        - `linkedin.ad_campaign_groups.create.v1`
        - `linkedin.ad_campaigns.create.v1`
        - `linkedin.ad_analytics.get.v1`
        - `x_ads.campaigns.create.v1`
        - `x_ads.line_items.create.v1`
        - `x_ads.stats.query.v1`
    - Constraint note:
        - `Channel launch operations require account-level permissions and payment readiness; fail fast when account state is not launch-ready.`

- `paid_channel_measurement_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Google Analytics Data API`
        - `PostHog Insights API`
        - `Mixpanel Query API`
        - `Amplitude Dashboard REST API`
    - Provider method ids (`method_id`):
        - `ga4.properties.run_report.v1`
        - `posthog.insights.trend.query.v1`
        - `posthog.insights.funnel.query.v1`
        - `mixpanel.funnels.query.v1`
        - `mixpanel.retention.query.v1`
        - `amplitude.dashboardrest.chart.get.v1`
    - Constraint note:
        - `Attribution and conversion definitions differ across analytics providers; normalize metric contracts before comparing channel performance.`

- `creative_feedback_capture_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Intercom Conversations API`
        - `Typeform Responses API`
        - `SurveyMonkey API`
    - Provider method ids (`method_id`):
        - `intercom.conversations.list.v1`
        - `intercom.conversations.search.v1`
        - `typeform.responses.list.v1`
        - `surveymonkey.surveys.responses.list.v1`
    - Constraint note:
        - `Feedback samples can be biased by channel mix and response timing; require minimum sample and segment balance checks before optimization decisions.`

#### Bot 10 Required Tool Prompt Files

- `prompts/tool_creative_asset_ops_api.md`
- `prompts/tool_paid_channel_execution_api.md`
- `prompts/tool_paid_channel_measurement_api.md`
- `prompts/tool_creative_feedback_capture_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 10A - `creative_producer`

- `name`: `creative_producer`
- `fexp_description`: `Generate and version creative variants`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,creative_asset_ops_api,creative_feedback_capture_api,paid_channel_measurement_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"creative_variant_pack_schema","schema":{"type":"object","required":["artifact_type","version","hypothesis_ref","target_segment","variants","format_constraints","tone_constraints","disallowed_claims","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["creative_variant_pack"]},"version":{"type":"string"},"hypothesis_ref":{"type":"string"},"target_segment":{"type":"string"},"variants":{"type":"array","items":{"type":"object","required":["variant_id","concept","hook","primary_message","cta","channels","asset_specs"],"additionalProperties":false,"properties":{"variant_id":{"type":"string"},"concept":{"type":"string"},"hook":{"type":"string"},"primary_message":{"type":"string"},"cta":{"type":"string"},"channels":{"type":"array","items":{"type":"string"}},"asset_specs":{"type":"object","required":["format","aspect_ratio"],"additionalProperties":false,"properties":{"format":{"type":"string"},"aspect_ratio":{"type":"string"},"duration_seconds":{"type":"number","minimum":0},"max_text_density":{"type":"string"}}}}}},"format_constraints":{"type":"array","items":{"type":"string"}},"tone_constraints":{"type":"array","items":{"type":"string"}},"disallowed_claims":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"creative_asset_manifest_schema","schema":{"type":"object","required":["artifact_type","version","manifest_id","assets","qa_status","blocking_issues"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["creative_asset_manifest"]},"version":{"type":"string"},"manifest_id":{"type":"string"},"assets":{"type":"array","items":{"type":"object","required":["asset_id","variant_id","platform","asset_ref","status"],"additionalProperties":false,"properties":{"asset_id":{"type":"string"},"variant_id":{"type":"string"},"platform":{"type":"string"},"asset_ref":{"type":"string"},"status":{"type":"string","enum":["draft","ready","rejected"]},"qa_checks":{"type":"array","items":{"type":"string"}}}}},"qa_status":{"type":"string","enum":["pass","warn","fail"]},"blocking_issues":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"creative_claim_risk_register_schema","schema":{"type":"object","required":["artifact_type","version","claims","high_risk_claims","required_proofs"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["creative_claim_risk_register"]},"version":{"type":"string"},"claims":{"type":"array","items":{"type":"object","required":["claim_id","claim_text","risk_level","substantiation_status"],"additionalProperties":false,"properties":{"claim_id":{"type":"string"},"claim_text":{"type":"string"},"risk_level":{"type":"string","enum":["low","medium","high"]},"substantiation_status":{"type":"string","enum":["verified","partially_verified","unverified"]}}}},"high_risk_claims":{"type":"array","items":{"type":"string"}},"required_proofs":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Generate and QA creative variants that can be shipped to paid channels; fail fast when platform specs, claim substantiation, or asset quality gates are not satisfied.`

### Expert 10B - `paid_channel_operator`

- `name`: `paid_channel_operator`
- `fexp_description`: `Run one-platform paid tests with guardrails`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,paid_channel_execution_api,paid_channel_measurement_api,creative_asset_ops_api`
- `fexp_block_tools`: ``
- `skills`: [`skill_meta_ads_execution`, `skill_google_ads_execution`, `skill_x_ads_execution`]
- `pdoc_output_schemas`: [{"schema_name":"paid_channel_test_plan_schema","schema":{"type":"object","required":["artifact_type","version","test_id","platform","campaign_structure","targeting","budget_guardrails","run_window","success_metrics","stop_conditions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["paid_channel_test_plan"]},"version":{"type":"string"},"test_id":{"type":"string"},"platform":{"type":"string","enum":["meta","google_ads","linkedin","x_ads"]},"campaign_structure":{"type":"object","required":["objective","campaign_name","adset_or_adgroup_strategy"],"additionalProperties":false,"properties":{"objective":{"type":"string"},"campaign_name":{"type":"string"},"adset_or_adgroup_strategy":{"type":"string"}}},"targeting":{"type":"array","items":{"type":"string"}},"budget_guardrails":{"type":"object","required":["daily_cap","total_cap"],"additionalProperties":false,"properties":{"daily_cap":{"type":"number","minimum":0},"total_cap":{"type":"number","minimum":0}}},"run_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"success_metrics":{"type":"array","items":{"type":"string"}},"stop_conditions":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"paid_channel_result_schema","schema":{"type":"object","required":["artifact_type","version","platform","campaign_ref","spend","performance_summary","guardrail_status","decision","decision_reason","next_step","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["paid_channel_result"]},"version":{"type":"string"},"platform":{"type":"string"},"campaign_ref":{"type":"string"},"spend":{"type":"number","minimum":0},"performance_summary":{"type":"object","required":["impressions","clicks","ctr","cpc","conversions","cpa"],"additionalProperties":false,"properties":{"impressions":{"type":"number","minimum":0},"clicks":{"type":"number","minimum":0},"ctr":{"type":"number","minimum":0},"cpc":{"type":"number","minimum":0},"conversions":{"type":"number","minimum":0},"cpa":{"type":"number","minimum":0}}},"guardrail_status":{"type":"string","enum":["safe","warning","breached"]},"decision":{"type":"string","enum":["continue","iterate","stop"]},"decision_reason":{"type":"string"},"next_step":{"type":"string"},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"paid_channel_budget_guardrail_schema","schema":{"type":"object","required":["artifact_type","version","campaign_ref","planned_budget","actual_spend","breaches","recommended_controls"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["paid_channel_budget_guardrail"]},"version":{"type":"string"},"campaign_ref":{"type":"string"},"planned_budget":{"type":"object","required":["daily_cap","total_cap"],"additionalProperties":false,"properties":{"daily_cap":{"type":"number","minimum":0},"total_cap":{"type":"number","minimum":0}}},"actual_spend":{"type":"object","required":["daily_spend","total_spend"],"additionalProperties":false,"properties":{"daily_spend":{"type":"number","minimum":0},"total_spend":{"type":"number","minimum":0}}},"breaches":{"type":"array","items":{"type":"string"}},"recommended_controls":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Execute one-platform paid tests with strict spend and performance guardrails; fail fast when budget controls, metric quality, or channel readiness checks are insufficient.`

### Bot 11 - `pilot_delivery_bot`

- `accent_color`: `#15803D`
- `title1`: `Pilot Delivery`
- `title2`: `Paid pilot contracting and first value delivery`
- `occupation`: `Pilot Delivery Manager`
- `typical_group`: `GTM / Delivery`
- `intro_message`: `I convert qualified opportunities into paid pilot outcomes.`
- `tags`: [`Pilot`, `Delivery`, `Activation`]
- `featured_actions`: [`Prepare pilot contracting packet` -> `pilot_contracting_operator`, `Execute first value delivery` -> `first_value_delivery_operator`]
- `experts`: [`pilot_contracting_operator`, `first_value_delivery_operator`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `pilot_contracting_api`, `pilot_delivery_ops_api`, `pilot_usage_evidence_api`, `pilot_stakeholder_sync_api`]

#### Bot 11 Tool Catalog

- `pilot_contracting_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `DocuSign eSignature API`
        - `PandaDoc API`
        - `Stripe API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `docusign.envelopes.create.v1`
        - `docusign.envelopes.get.v1`
        - `docusign.envelopes.list_status_changes.v1`
        - `pandadoc.documents.create.v1`
        - `pandadoc.documents.details.get.v1`
        - `stripe.payment_links.create.v1`
        - `stripe.invoices.create.v1`
        - `hubspot.deals.update.v1`
    - Call contract:
        - `pilot_contracting_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_contract_packet`
        - `send_for_signature`
        - `check_signature_status`
        - `create_payment_commitment`
        - `mark_contract_ready`
    - Allowed `args` schema:
        - `provider` (string): `docusign | pandadoc | stripe | hubspot`
        - `method_id` (string, optional): must be from provider whitelist.
        - `pilot_id` (string, required for all operations except `help/status/list_*`)
        - `deal_id` (string, optional)
        - `template_id` (string, required for create/send operations)
        - `recipient_list` (array of objects, required for send operations)
        - `payment_terms` (object, required for payment commitment operation)
        - `currency` (string, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/send operations without `template_id`.
        - Reject send operations without `recipient_list`.
        - Reject payment commitment operation without `payment_terms`.
        - Reject contract-ready marking when signature status is not `completed`.

- `pilot_delivery_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Jira REST API`
        - `Asana API`
        - `Notion API`
        - `Calendly API`
        - `Google Calendar API`
    - Provider method ids (`method_id`):
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
        - `asana.tasks.create.v1`
        - `notion.pages.create.v1`
        - `notion.pages.update.v1`
        - `calendly.scheduled_events.list.v1`
        - `google_calendar.events.insert.v1`
        - `google_calendar.events.list.v1`
    - Constraint note:
        - `Delivery tasks must be traceable to signed scope and success criteria; fail fast when scope-task mapping is incomplete.`

- `pilot_usage_evidence_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `PostHog Insights API`
        - `Mixpanel Query API`
        - `Google Analytics Data API`
        - `Amplitude Dashboard REST API`
    - Provider method ids (`method_id`):
        - `posthog.insights.trend.query.v1`
        - `posthog.insights.funnel.query.v1`
        - `mixpanel.funnels.query.v1`
        - `mixpanel.retention.query.v1`
        - `ga4.properties.run_report.v1`
        - `amplitude.dashboardrest.chart.get.v1`
    - Constraint note:
        - `First-value evidence must be computed from instrumented events aligned to agreed success criteria; reject unverifiable evidence.`

- `pilot_stakeholder_sync_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Intercom Conversations API`
        - `Zendesk Ticketing API`
        - `Google Calendar API`
    - Provider method ids (`method_id`):
        - `intercom.conversations.list.v1`
        - `intercom.conversations.search.v1`
        - `zendesk.tickets.search.v1`
        - `zendesk.ticket_comments.list.v1`
        - `google_calendar.events.list.v1`
    - Constraint note:
        - `Stakeholder summaries must include explicit owner, risk, and ETA fields; fail fast when any mandatory governance field is missing.`

#### Bot 11 Required Tool Prompt Files

- `prompts/tool_pilot_contracting_api.md`
- `prompts/tool_pilot_delivery_ops_api.md`
- `prompts/tool_pilot_usage_evidence_api.md`
- `prompts/tool_pilot_stakeholder_sync_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 11A - `pilot_contracting_operator`

- `name`: `pilot_contracting_operator`
- `fexp_description`: `Define and finalize paid pilot terms`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pilot_contracting_api,pilot_delivery_ops_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"pilot_contract_packet_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","account_ref","scope","commercial_terms","success_criteria","stakeholders","signature_status","payment_commitment","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pilot_contract_packet"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"account_ref":{"type":"string"},"scope":{"type":"array","items":{"type":"string"}},"commercial_terms":{"type":"object","required":["contract_value","currency","billing_model"],"additionalProperties":false,"properties":{"contract_value":{"type":"number","minimum":0},"currency":{"type":"string"},"billing_model":{"type":"string"},"payment_terms":{"type":"string"}}},"success_criteria":{"type":"array","items":{"type":"string"}},"stakeholders":{"type":"array","items":{"type":"object","required":["name","role","decision_authority"],"additionalProperties":false,"properties":{"name":{"type":"string"},"role":{"type":"string"},"decision_authority":{"type":"string"}}}},"signature_status":{"type":"string","enum":["draft","sent","viewed","completed","declined"]},"payment_commitment":{"type":"string","enum":["none","pending","confirmed"]},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"pilot_risk_clause_register_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","risk_clauses","high_risk_items","required_mitigations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pilot_risk_clause_register"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"risk_clauses":{"type":"array","items":{"type":"object","required":["clause_id","clause_text","risk_level","owner"],"additionalProperties":false,"properties":{"clause_id":{"type":"string"},"clause_text":{"type":"string"},"risk_level":{"type":"string","enum":["low","medium","high","critical"]},"owner":{"type":"string"}}}},"high_risk_items":{"type":"array","items":{"type":"string"}},"required_mitigations":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"pilot_go_live_readiness_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","gate_status","blocking_issues","required_actions","target_start_date"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pilot_go_live_readiness"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"gate_status":{"type":"string","enum":["go","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"required_actions":{"type":"array","items":{"type":"string"}},"target_start_date":{"type":"string"}}}}]
- `body_md`: `Produce contract-complete pilot packets and readiness gates; fail fast when signatures, payment commitment, or scope clarity are insufficient for launch.`

### Expert 11B - `first_value_delivery_operator`

- `name`: `first_value_delivery_operator`
- `fexp_description`: `Drive first value delivery and collect proof artifacts`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,pilot_delivery_ops_api,pilot_usage_evidence_api,pilot_stakeholder_sync_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"first_value_delivery_plan_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","delivery_plan","owners","timeline","dependencies","risk_controls"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["first_value_delivery_plan"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"delivery_plan":{"type":"array","items":{"type":"object","required":["step_id","step_name","expected_outcome"],"additionalProperties":false,"properties":{"step_id":{"type":"string"},"step_name":{"type":"string"},"expected_outcome":{"type":"string"},"acceptance_check":{"type":"string"}}}},"owners":{"type":"array","items":{"type":"string"}},"timeline":{"type":"object","required":["start_date","target_first_value_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"target_first_value_date":{"type":"string"}}},"dependencies":{"type":"array","items":{"type":"string"}},"risk_controls":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"first_value_evidence_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","time_to_first_value","delivered_outcomes","proof_artifacts","usage_signals","stakeholder_confirmation","confidence","risk_flags","next_steps"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["first_value_evidence"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"time_to_first_value":{"type":"string"},"delivered_outcomes":{"type":"array","items":{"type":"string"}},"proof_artifacts":{"type":"array","items":{"type":"string"}},"usage_signals":{"type":"array","items":{"type":"object","required":["signal_name","signal_value","source_ref"],"additionalProperties":false,"properties":{"signal_name":{"type":"string"},"signal_value":{"type":"number"},"source_ref":{"type":"string"}}}},"stakeholder_confirmation":{"type":"object","required":["confirmed","confirmed_by"],"additionalProperties":false,"properties":{"confirmed":{"type":"boolean"},"confirmed_by":{"type":"array","items":{"type":"string"}}}},"confidence":{"type":"number","minimum":0,"maximum":1},"risk_flags":{"type":"array","items":{"type":"string"}},"next_steps":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"pilot_expansion_readiness_schema","schema":{"type":"object","required":["artifact_type","version","pilot_id","readiness_status","expansion_hypothesis","blocking_issues","recommended_action"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pilot_expansion_readiness"]},"version":{"type":"string"},"pilot_id":{"type":"string"},"readiness_status":{"type":"string","enum":["ready","conditional","not_ready"]},"expansion_hypothesis":{"type":"string"},"blocking_issues":{"type":"array","items":{"type":"string"}},"recommended_action":{"type":"string","enum":["expand","stabilize","stop"]}}}}]
- `body_md`: `Operate delivery toward first value and emit auditable outcome evidence; fail fast when evidence cannot be tied to agreed success criteria or stakeholder confirmation is missing.`

### Bot 12 - `retention_intelligence_bot`

- `accent_color`: `#0E7490`
- `title1`: `Retention Intelligence`
- `title2`: `Cohort and PMF confidence synthesis`
- `occupation`: `Retention Analyst`
- `typical_group`: `GTM / Retention`
- `intro_message`: `I synthesize retention, revenue, and PMF confidence evidence.`
- `tags`: [`Retention`, `PMF`, `Cohorts`]
- `featured_actions`: [`Run cohort retention and revenue review` -> `cohort_revenue_analyst`, `Score PMF confidence from behavioral and survey evidence` -> `pmf_survey_interpreter`]
- `experts`: [`cohort_revenue_analyst`, `pmf_survey_interpreter`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `retention_revenue_events_api`, `retention_product_analytics_api`, `retention_feedback_research_api`, `retention_account_context_api`]

#### Bot 12 Tool Catalog

- `retention_revenue_events_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Stripe API`
        - `Chargebee API`
        - `Recurly API`
        - `Paddle API`
    - Provider method ids (`method_id`):
        - `stripe.subscriptions.list.v1`
        - `stripe.invoices.list.v1`
        - `chargebee.subscriptions.list.v1`
        - `chargebee.invoices.list.v1`
        - `recurly.subscriptions.list.v1`
        - `paddle.subscriptions.list.v1`
    - Call contract:
        - `retention_revenue_events_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `fetch_subscriptions`
        - `fetch_invoices`
        - `compute_mrr_movement`
        - `classify_revenue_risk`
    - Allowed `args` schema:
        - `provider` (string): `stripe | chargebee | recurly | paddle`
        - `method_id` (string, optional): must be from provider whitelist.
        - `window_start` (string, required for compute operations)
        - `window_end` (string, required for compute operations)
        - `customer_ref` (string, optional)
        - `plan_filter` (array of strings, optional)
        - `status_filter` (array of strings, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject compute operations without `window_start/window_end`.
        - Reject response rows missing billing currency or status.
        - Reject risk classification when subscription event history is incomplete.

- `retention_product_analytics_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `PostHog Insights API`
        - `Mixpanel Query API`
        - `Google Analytics Data API`
        - `Amplitude Dashboard REST API`
    - Provider method ids (`method_id`):
        - `posthog.insights.retention.query.v1`
        - `posthog.insights.funnel.query.v1`
        - `mixpanel.retention.query.v1`
        - `mixpanel.funnels.query.v1`
        - `ga4.properties.run_report.v1`
        - `amplitude.dashboardrest.chart.get.v1`
    - Constraint note:
        - `Retention insights are valid only when cohort definition, event dictionary version, and time window are explicitly declared.`

- `retention_feedback_research_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `SurveyMonkey API`
        - `Typeform Responses API`
        - `Delighted API`
        - `Intercom Conversations API`
        - `Zendesk Search API`
    - Provider method ids (`method_id`):
        - `surveymonkey.responses.list.v1`
        - `typeform.responses.list.v1`
        - `delighted.metrics.get.v1`
        - `intercom.conversations.search.v1`
        - `zendesk.tickets.search.v1`
    - Constraint note:
        - `PMF interpretation must include denominator quality (response rate and segment coverage); reject statistically weak samples.`

- `retention_account_context_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Pipedrive API`
        - `Intercom Conversations API`
        - `Zendesk Search API`
    - Provider method ids (`method_id`):
        - `hubspot.deals.search.v1`
        - `hubspot.companies.search.v1`
        - `pipedrive.deals.search.v1`
        - `intercom.conversations.search.v1`
        - `zendesk.tickets.search.v1`
    - Constraint note:
        - `Account risk flags must be tied to concrete entity ids and timestamps; reject narrative-only risk statements.`

#### Bot 12 Required Tool Prompt Files

- `prompts/tool_retention_revenue_events_api.md`
- `prompts/tool_retention_product_analytics_api.md`
- `prompts/tool_retention_feedback_research_api.md`
- `prompts/tool_retention_account_context_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 12A - `cohort_revenue_analyst`

- `name`: `cohort_revenue_analyst`
- `fexp_description`: `Diagnose activation-retention-revenue behavior`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,retention_revenue_events_api,retention_product_analytics_api,retention_account_context_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"cohort_revenue_review_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","segment_filters","retention_cohorts","revenue_movement","expansion_vs_churn","risk_accounts","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["cohort_revenue_review"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"segment_filters":{"type":"array","items":{"type":"string"}},"retention_cohorts":{"type":"array","items":{"type":"object","required":["cohort_id","period","retention_rate"],"additionalProperties":false,"properties":{"cohort_id":{"type":"string"},"period":{"type":"string"},"retention_rate":{"type":"number","minimum":0,"maximum":1}}}},"revenue_movement":{"type":"object","required":["new_mrr","expansion_mrr","contraction_mrr","churn_mrr","net_mrr"],"additionalProperties":false,"properties":{"new_mrr":{"type":"number"},"expansion_mrr":{"type":"number"},"contraction_mrr":{"type":"number"},"churn_mrr":{"type":"number"},"net_mrr":{"type":"number"}}},"expansion_vs_churn":{"type":"object","required":["expansion_ratio","churn_ratio"],"additionalProperties":false,"properties":{"expansion_ratio":{"type":"number","minimum":0},"churn_ratio":{"type":"number","minimum":0}}},"risk_accounts":{"type":"array","items":{"type":"object","required":["account_ref","risk_level","risk_reason"],"additionalProperties":false,"properties":{"account_ref":{"type":"string"},"risk_level":{"type":"string","enum":["low","medium","high","critical"]},"risk_reason":{"type":"string"}}}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"retention_driver_matrix_schema","schema":{"type":"object","required":["artifact_type","version","driver_matrix","priority_actions","confidence_notes"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["retention_driver_matrix"]},"version":{"type":"string"},"driver_matrix":{"type":"array","items":{"type":"object","required":["driver_id","driver_type","impact_score","evidence_refs"],"additionalProperties":false,"properties":{"driver_id":{"type":"string"},"driver_type":{"type":"string","enum":["activation","engagement","value_realization","support_friction","commercial"]},"impact_score":{"type":"number","minimum":0,"maximum":1},"evidence_refs":{"type":"array","items":{"type":"string"}}}}},"priority_actions":{"type":"array","items":{"type":"string"}},"confidence_notes":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"retention_readiness_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","blocking_issues","required_actions","decision_owner"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["retention_readiness_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","conditional","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"required_actions":{"type":"array","items":{"type":"string"}},"decision_owner":{"type":"string"}}}}]
- `body_md`: `Produce auditable cohort and revenue diagnostics with explicit driver priority; fail fast when cohort definitions, billing joins, or event coverage are inconsistent.`

### Expert 12B - `pmf_survey_interpreter`

- `name`: `pmf_survey_interpreter`
- `fexp_description`: `Interpret PMF survey evidence with behavioral context`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,retention_feedback_research_api,retention_product_analytics_api,retention_account_context_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"pmf_confidence_scorecard_schema","schema":{"type":"object","required":["artifact_type","version","measurement_window","target_segment","survey_quality","pmf_core_metric","behavioral_corroboration","confidence","recommendation","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pmf_confidence_scorecard"]},"version":{"type":"string"},"measurement_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"target_segment":{"type":"string"},"survey_quality":{"type":"object","required":["sample_size","response_rate","coverage_notes"],"additionalProperties":false,"properties":{"sample_size":{"type":"number","minimum":0},"response_rate":{"type":"number","minimum":0,"maximum":1},"coverage_notes":{"type":"array","items":{"type":"string"}}}},"pmf_core_metric":{"type":"object","required":["metric_name","metric_value","threshold"],"additionalProperties":false,"properties":{"metric_name":{"type":"string"},"metric_value":{"type":"number","minimum":0,"maximum":1},"threshold":{"type":"number","minimum":0,"maximum":1}}},"behavioral_corroboration":{"type":"array","items":{"type":"object","required":["signal_name","signal_direction","source_ref"],"additionalProperties":false,"properties":{"signal_name":{"type":"string"},"signal_direction":{"type":"string","enum":["positive","neutral","negative"]},"source_ref":{"type":"string"}}}},"confidence":{"type":"number","minimum":0,"maximum":1},"recommendation":{"type":"string","enum":["increase_investment","targeted_fix","hold","pivot"]},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"pmf_signal_evidence_schema","schema":{"type":"object","required":["artifact_type","version","signals","negative_signals","evidence_gaps","next_research_actions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pmf_signal_evidence"]},"version":{"type":"string"},"signals":{"type":"array","items":{"type":"object","required":["signal_id","signal_type","strength","evidence_refs"],"additionalProperties":false,"properties":{"signal_id":{"type":"string"},"signal_type":{"type":"string","enum":["survey","usage","commercial","support"]},"strength":{"type":"number","minimum":0,"maximum":1},"evidence_refs":{"type":"array","items":{"type":"string"}}}}},"negative_signals":{"type":"array","items":{"type":"string"}},"evidence_gaps":{"type":"array","items":{"type":"string"}},"next_research_actions":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"pmf_research_backlog_schema","schema":{"type":"object","required":["artifact_type","version","backlog_items","priority_order","owner_map"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["pmf_research_backlog"]},"version":{"type":"string"},"backlog_items":{"type":"array","items":{"type":"object","required":["item_id","hypothesis","required_evidence","priority"],"additionalProperties":false,"properties":{"item_id":{"type":"string"},"hypothesis":{"type":"string"},"required_evidence":{"type":"array","items":{"type":"string"}},"priority":{"type":"string","enum":["p0","p1","p2"]}}}},"priority_order":{"type":"array","items":{"type":"string"}},"owner_map":{"type":"array","items":{"type":"object","required":["item_id","owner"],"additionalProperties":false,"properties":{"item_id":{"type":"string"},"owner":{"type":"string"}}}}}}]
- `body_md`: `Interpret PMF evidence with strict sample-quality and behavior corroboration checks; fail fast when survey evidence is underpowered or conflicts with observed usage trends.`

### Bot 13 - `churn_learning_bot`

- `accent_color`: `#7C2D12`
- `title1`: `Churn Learning`
- `title2`: `Churn interviews and root-cause classification`
- `occupation`: `Churn Analyst`
- `typical_group`: `GTM / Retention`
- `intro_message`: `I extract churn root causes into prioritized fix artifacts.`
- `tags`: [`Churn`, `RootCause`, `Fixes`]
- `featured_actions`: [`Run churn interview and evidence capture` -> `churn_interview_operator`, `Build root-cause fix backlog` -> `rootcause_classifier`]
- `experts`: [`churn_interview_operator`, `rootcause_classifier`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `churn_feedback_capture_api`, `churn_interview_ops_api`, `churn_transcript_analysis_api`, `churn_remediation_backlog_api`]

#### Bot 13 Tool Catalog

- `churn_feedback_capture_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Intercom Conversations API`
        - `Zendesk Search API`
        - `Stripe API`
        - `Chargebee API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `intercom.conversations.search.v1`
        - `zendesk.tickets.search.v1`
        - `stripe.subscriptions.list.v1`
        - `stripe.invoices.list.v1`
        - `chargebee.subscriptions.list.v1`
        - `hubspot.deals.search.v1`
    - Call contract:
        - `churn_feedback_capture_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `fetch_churned_accounts`
        - `fetch_cancellation_reasons`
        - `fetch_support_friction_signals`
        - `build_churn_signal_timeline`
    - Allowed `args` schema:
        - `provider` (string): `intercom | zendesk | stripe | chargebee | hubspot`
        - `method_id` (string, optional): must be from provider whitelist.
        - `window_start` (string, required for timeline and reason operations)
        - `window_end` (string, required for timeline and reason operations)
        - `segment_filter` (array of strings, optional)
        - `account_refs` (array of strings, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject timeline operations without `window_start/window_end`.
        - Reject churn records without account id and churn effective date.
        - Reject reason aggregation when source coverage is below required segment threshold.

- `churn_interview_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Calendly API`
        - `Google Calendar API`
        - `Zoom API`
    - Provider method ids (`method_id`):
        - `calendly.scheduled_events.list.v1`
        - `google_calendar.events.insert.v1`
        - `google_calendar.events.list.v1`
        - `zoom.meetings.recordings.get.v1`
    - Constraint note:
        - `Interview scheduling and capture must map every session to account_ref, churn_event_ref, and consent status.`

- `churn_transcript_analysis_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Gong API`
        - `Fireflies API`
        - `Zoom API`
    - Provider method ids (`method_id`):
        - `gong.calls.list.v1`
        - `gong.calls.transcript.get.v1`
        - `fireflies.transcript.get.v1`
        - `zoom.meetings.recordings.get.v1`
    - Constraint note:
        - `Root-cause coding is valid only when transcript snippets are linked to speaker and timestamp.`

- `churn_remediation_backlog_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Jira REST API`
        - `Asana API`
        - `Linear GraphQL API`
        - `Notion API`
    - Provider method ids (`method_id`):
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
        - `asana.tasks.create.v1`
        - `linear.issues.create.v1`
        - `notion.pages.create.v1`
        - `notion.pages.update.v1`
    - Constraint note:
        - `Every remediation task must include root_cause_id, owner, target_date, and expected retention impact.`

#### Bot 13 Required Tool Prompt Files

- `prompts/tool_churn_feedback_capture_api.md`
- `prompts/tool_churn_interview_ops_api.md`
- `prompts/tool_churn_transcript_analysis_api.md`
- `prompts/tool_churn_remediation_backlog_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 13A - `churn_interview_operator`

- `name`: `churn_interview_operator`
- `fexp_description`: `Run structured churn interviews`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,churn_feedback_capture_api,churn_interview_ops_api,churn_transcript_analysis_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"churn_interview_corpus_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","segment_filters","accounts","interview_records","coverage_summary","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_interview_corpus"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"segment_filters":{"type":"array","items":{"type":"string"}},"accounts":{"type":"array","items":{"type":"string"}},"interview_records":{"type":"array","items":{"type":"object","required":["interview_id","account_ref","churn_event_ref","interview_date","participants","transcript_ref","key_quotes"],"additionalProperties":false,"properties":{"interview_id":{"type":"string"},"account_ref":{"type":"string"},"churn_event_ref":{"type":"string"},"interview_date":{"type":"string"},"participants":{"type":"array","items":{"type":"string"}},"transcript_ref":{"type":"string"},"key_quotes":{"type":"array","items":{"type":"string"}}}}},"coverage_summary":{"type":"object","required":["scheduled_count","completed_count","coverage_rate"],"additionalProperties":false,"properties":{"scheduled_count":{"type":"number","minimum":0},"completed_count":{"type":"number","minimum":0},"coverage_rate":{"type":"number","minimum":0,"maximum":1}}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"churn_interview_coverage_schema","schema":{"type":"object","required":["artifact_type","version","target_segments","completed_interviews","coverage_gaps","required_followups"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_interview_coverage"]},"version":{"type":"string"},"target_segments":{"type":"array","items":{"type":"string"}},"completed_interviews":{"type":"array","items":{"type":"string"}},"coverage_gaps":{"type":"array","items":{"type":"string"}},"required_followups":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"churn_signal_quality_schema","schema":{"type":"object","required":["artifact_type","version","quality_checks","failed_checks","remediation_actions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_signal_quality"]},"version":{"type":"string"},"quality_checks":{"type":"array","items":{"type":"object","required":["check_id","status"],"additionalProperties":false,"properties":{"check_id":{"type":"string"},"status":{"type":"string","enum":["pass","fail"]},"notes":{"type":"string"}}}},"failed_checks":{"type":"array","items":{"type":"string"}},"remediation_actions":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce interview corpus and coverage artifacts with verifiable transcript evidence; fail fast when sampling coverage or interview traceability is insufficient.`

### Expert 13B - `rootcause_classifier`

- `name`: `rootcause_classifier`
- `fexp_description`: `Classify churn drivers and prioritize fixes`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,churn_feedback_capture_api,churn_transcript_analysis_api,churn_remediation_backlog_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"churn_rootcause_backlog_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","rootcauses","fix_backlog","confidence_notes","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_rootcause_backlog"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"rootcauses":{"type":"array","items":{"type":"object","required":["rootcause_id","theme","severity","frequency","evidence_refs","affected_segments"],"additionalProperties":false,"properties":{"rootcause_id":{"type":"string"},"theme":{"type":"string"},"severity":{"type":"string","enum":["low","medium","high","critical"]},"frequency":{"type":"number","minimum":0},"evidence_refs":{"type":"array","items":{"type":"string"}},"affected_segments":{"type":"array","items":{"type":"string"}}}}},"fix_backlog":{"type":"array","items":{"type":"object","required":["fix_id","rootcause_id","owner","target_date","expected_retention_impact","priority"],"additionalProperties":false,"properties":{"fix_id":{"type":"string"},"rootcause_id":{"type":"string"},"owner":{"type":"string"},"target_date":{"type":"string"},"expected_retention_impact":{"type":"number","minimum":0},"priority":{"type":"string","enum":["p0","p1","p2"]}}}},"confidence_notes":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"churn_fix_experiment_plan_schema","schema":{"type":"object","required":["artifact_type","version","experiment_batch_id","experiments","measurement_plan","stop_conditions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_fix_experiment_plan"]},"version":{"type":"string"},"experiment_batch_id":{"type":"string"},"experiments":{"type":"array","items":{"type":"object","required":["experiment_id","hypothesis","target_segment","owner","start_date","success_metric"],"additionalProperties":false,"properties":{"experiment_id":{"type":"string"},"hypothesis":{"type":"string"},"target_segment":{"type":"string"},"owner":{"type":"string"},"start_date":{"type":"string"},"success_metric":{"type":"string"}}}},"measurement_plan":{"type":"array","items":{"type":"string"}},"stop_conditions":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"churn_prevention_priority_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","must_fix_items","deferred_items","decision_owner"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["churn_prevention_priority_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","conditional","no_go"]},"must_fix_items":{"type":"array","items":{"type":"string"}},"deferred_items":{"type":"array","items":{"type":"string"}},"decision_owner":{"type":"string"}}}}]
- `body_md`: `Classify churn causes into an owner-linked remediation backlog; fail fast when evidence-to-cause mapping is ambiguous or fix ownership is undefined.`

### Bot 14 - `gtm_economics_rtm_bot`

- `accent_color`: `#334155`
- `title1`: `GTM Economics and RTM`
- `title2`: `Unit economics and route-to-market rules`
- `occupation`: `GTM Economist`
- `typical_group`: `GTM / Economics`
- `intro_message`: `I lock viable GTM economics and codify RTM rules.`
- `tags`: [`UnitEconomics`, `RTM`, `GTM`]
- `featured_actions`: [`Evaluate unit economics readiness` -> `unit_economics_modeler`, `Codify RTM ownership and conflict rules` -> `rtm_rules_architect`]
- `experts`: [`unit_economics_modeler`, `rtm_rules_architect`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `gtm_unit_economics_api`, `gtm_media_efficiency_api`, `rtm_pipeline_finance_api`, `rtm_territory_policy_api`]

#### Bot 14 Tool Catalog

- `gtm_unit_economics_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Stripe API`
        - `Chargebee API`
        - `Recurly API`
    - Provider method ids (`method_id`):
        - `stripe.invoices.list.v1`
        - `stripe.subscriptions.list.v1`
        - `chargebee.invoices.list.v1`
        - `chargebee.subscriptions.list.v1`
        - `recurly.subscriptions.list.v1`
    - Call contract:
        - `gtm_unit_economics_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `fetch_revenue_cost_components`
        - `compute_ltv_cac`
        - `compute_payback_period`
        - `build_margin_waterfall`
    - Allowed `args` schema:
        - `provider` (string): `stripe | chargebee | recurly`
        - `method_id` (string, optional): must be from provider whitelist.
        - `window_start` (string, required for compute operations)
        - `window_end` (string, required for compute operations)
        - `segment_filter` (array of strings, optional)
        - `currency` (string, optional)
        - `fx_table_ref` (string, required if mixed currencies detected)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject compute operations without `window_start/window_end`.
        - Reject unit economics outputs when required revenue or cost components are missing.
        - Reject mixed-currency computations without `fx_table_ref`.

- `gtm_media_efficiency_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Meta Marketing API`
        - `Google Ads API`
        - `LinkedIn Marketing API`
    - Provider method ids (`method_id`):
        - `meta.insights.query.v1`
        - `google_ads.googleads.search_stream.v1`
        - `linkedin.ad_analytics.query.v1`
    - Constraint note:
        - `Media efficiency metrics must be tied to explicit attribution window and conversion definition; reject unlabeled ROAS or CAC values.`

- `rtm_pipeline_finance_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `HubSpot CRM API`
        - `Salesforce REST API`
        - `Pipedrive API`
    - Provider method ids (`method_id`):
        - `hubspot.deals.search.v1`
        - `hubspot.companies.search.v1`
        - `salesforce.query.opportunity.v1`
        - `salesforce.query.account.v1`
        - `pipedrive.deals.search.v1`
        - `pipedrive.deals.list.v1`
    - Constraint note:
        - `Pipeline and finance evidence must use normalized stage mappings; reject cross-CRM comparisons without stage normalization metadata.`

- `rtm_territory_policy_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Salesforce REST API`
        - `HubSpot CRM API`
        - `Notion API`
    - Provider method ids (`method_id`):
        - `salesforce.query.opportunity.v1`
        - `salesforce.query.user.v1`
        - `hubspot.deals.search.v1`
        - `hubspot.owners.list.v1`
        - `notion.pages.create.v1`
        - `notion.pages.update.v1`
    - Constraint note:
        - `RTM ownership policies must define owner, segment boundary, exception path, and escalation SLA; fail fast when any governance field is missing.`

#### Bot 14 Required Tool Prompt Files

- `prompts/tool_gtm_unit_economics_api.md`
- `prompts/tool_gtm_media_efficiency_api.md`
- `prompts/tool_rtm_pipeline_finance_api.md`
- `prompts/tool_rtm_territory_policy_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 14A - `unit_economics_modeler`

- `name`: `unit_economics_modeler`
- `fexp_description`: `Model payback and margin viability`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,gtm_unit_economics_api,gtm_media_efficiency_api,rtm_pipeline_finance_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"unit_economics_review_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","segments","unit_economics","payback_profile","margin_profile","readiness_state","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["unit_economics_review"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"segments":{"type":"array","items":{"type":"string"}},"unit_economics":{"type":"array","items":{"type":"object","required":["segment","cac","ltv","ltv_cac_ratio"],"additionalProperties":false,"properties":{"segment":{"type":"string"},"cac":{"type":"number","minimum":0},"ltv":{"type":"number","minimum":0},"ltv_cac_ratio":{"type":"number","minimum":0}}}},"payback_profile":{"type":"object","required":["median_months","p75_months"],"additionalProperties":false,"properties":{"median_months":{"type":"number","minimum":0},"p75_months":{"type":"number","minimum":0}}},"margin_profile":{"type":"object","required":["gross_margin","contribution_margin"],"additionalProperties":false,"properties":{"gross_margin":{"type":"number"},"contribution_margin":{"type":"number"}}},"readiness_state":{"type":"string","enum":["ready","conditional","not_ready"]},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"channel_margin_stack_schema","schema":{"type":"object","required":["artifact_type","version","channels","cost_layers","margin_waterfall","alerts"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["channel_margin_stack"]},"version":{"type":"string"},"channels":{"type":"array","items":{"type":"string"}},"cost_layers":{"type":"array","items":{"type":"object","required":["layer_name","cost_value"],"additionalProperties":false,"properties":{"layer_name":{"type":"string"},"cost_value":{"type":"number"}}}},"margin_waterfall":{"type":"array","items":{"type":"object","required":["step","value"],"additionalProperties":false,"properties":{"step":{"type":"string"},"value":{"type":"number"}}}},"alerts":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"payback_readiness_gate_schema","schema":{"type":"object","required":["artifact_type","version","gate_status","blocking_issues","required_actions","decision_owner"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["payback_readiness_gate"]},"version":{"type":"string"},"gate_status":{"type":"string","enum":["go","conditional","no_go"]},"blocking_issues":{"type":"array","items":{"type":"string"}},"required_actions":{"type":"array","items":{"type":"string"}},"decision_owner":{"type":"string"}}}}]
- `body_md`: `Produce auditable unit economics and payback decisions; fail fast when CAC/LTV inputs, attribution settings, or cost layer completeness are insufficient.`

### Expert 14B - `rtm_rules_architect`

- `name`: `rtm_rules_architect`
- `fexp_description`: `Define enforceable RTM ownership and engagement rules`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,rtm_pipeline_finance_api,rtm_territory_policy_api,gtm_unit_economics_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"rtm_rules_schema","schema":{"type":"object","required":["artifact_type","version","target_segments","channel_roles","ownership_rules","deal_registration_rules","conflict_resolution_sla","exceptions_policy","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["rtm_rules"]},"version":{"type":"string"},"target_segments":{"type":"array","items":{"type":"string"}},"channel_roles":{"type":"array","items":{"type":"object","required":["channel","owner_role","scope"],"additionalProperties":false,"properties":{"channel":{"type":"string"},"owner_role":{"type":"string"},"scope":{"type":"string"}}}},"ownership_rules":{"type":"array","items":{"type":"string"}},"deal_registration_rules":{"type":"array","items":{"type":"string"}},"conflict_resolution_sla":{"type":"string"},"exceptions_policy":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"deal_ownership_matrix_schema","schema":{"type":"object","required":["artifact_type","version","matrix_rows","unassigned_cases","escalation_path"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["deal_ownership_matrix"]},"version":{"type":"string"},"matrix_rows":{"type":"array","items":{"type":"object","required":["segment","territory","owner_team","fallback_owner"],"additionalProperties":false,"properties":{"segment":{"type":"string"},"territory":{"type":"string"},"owner_team":{"type":"string"},"fallback_owner":{"type":"string"}}}},"unassigned_cases":{"type":"array","items":{"type":"string"}},"escalation_path":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"rtm_conflict_resolution_playbook_schema","schema":{"type":"object","required":["artifact_type","version","incident_types","decision_rules","sla_targets","audit_requirements"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["rtm_conflict_resolution_playbook"]},"version":{"type":"string"},"incident_types":{"type":"array","items":{"type":"string"}},"decision_rules":{"type":"array","items":{"type":"string"}},"sla_targets":{"type":"array","items":{"type":"object","required":["incident_type","target_hours"],"additionalProperties":false,"properties":{"incident_type":{"type":"string"},"target_hours":{"type":"number","minimum":0}}}},"audit_requirements":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce enforceable RTM ownership and conflict resolution rules; fail fast when ownership boundaries, exception policy, or SLA enforcement paths are ambiguous.`

### Bot 15 - `partner_ecosystem_bot`

- `accent_color`: `#166534`
- `title1`: `Partner Ecosystem`
- `title2`: `Partner activation and channel conflict governance`
- `occupation`: `Partner Program Operator`
- `typical_group`: `GTM / Partners`
- `intro_message`: `I run partner lifecycle operations and conflict governance artifacts.`
- `tags`: [`Partners`, `PRM`, `Channel`]
- `featured_actions`: [`Run partner activation and enablement cycle` -> `partner_activation_operator`, `Resolve channel conflict incidents` -> `channel_conflict_governor`]
- `experts`: [`partner_activation_operator`, `channel_conflict_governor`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `partner_program_ops_api`, `partner_account_mapping_api`, `partner_enablement_execution_api`, `channel_conflict_governance_api`]

#### Bot 15 Tool Catalog

- `partner_program_ops_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `PartnerStack API`
    - Provider method ids (`method_id`):
        - `partnerstack.partnerships.list.v1`
        - `partnerstack.partners.list.v1`
        - `partnerstack.transactions.list.v1`
        - `partnerstack.transactions.create.v1`
        - `partnerstack.payouts.list.v1`
    - Call contract:
        - `partner_program_ops_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `list_partner_cohorts`
        - `list_partner_transactions`
        - `create_partner_transaction`
        - `list_partner_payouts`
        - `compute_activation_funnel`
    - Allowed `args` schema:
        - `provider` (string): `partnerstack`
        - `method_id` (string, optional): must be from provider whitelist.
        - `program_ids` (array of strings, optional)
        - `partner_refs` (array of strings, optional)
        - `window_start` (string, required for funnel and payout operations)
        - `window_end` (string, required for funnel and payout operations)
        - `currency` (string, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject funnel and payout operations without `window_start/window_end`.
        - Reject transaction operations without partner reference and monetary value.
        - Reject activation funnel output when cohort denominator is missing.

- `partner_account_mapping_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Crossbeam API`
        - `Salesforce REST API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `crossbeam.partners.list.v1`
        - `crossbeam.account_mapping.overlaps.list.v1`
        - `crossbeam.exports.records.get.v1`
        - `salesforce.query.account.v1`
        - `hubspot.companies.search.v1`
    - Constraint note:
        - `Account overlap outputs must preserve partner-specific visibility constraints and explicit account_ref join keys.`

- `partner_enablement_execution_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Asana API`
        - `Notion API`
        - `HubSpot CRM API`
    - Provider method ids (`method_id`):
        - `asana.tasks.create.v1`
        - `asana.tasks.update.v1`
        - `notion.pages.create.v1`
        - `notion.pages.update.v1`
        - `hubspot.companies.search.v1`
        - `hubspot.deals.search.v1`
    - Constraint note:
        - `Enablement tasks must map to explicit partner tier, owner, and completion criteria; fail fast on missing ownership or due date.`

- `channel_conflict_governance_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Salesforce REST API`
        - `HubSpot CRM API`
        - `Pipedrive API`
        - `Jira REST API`
    - Provider method ids (`method_id`):
        - `salesforce.query.opportunity.v1`
        - `hubspot.deals.search.v1`
        - `pipedrive.deals.search.v1`
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
    - Constraint note:
        - `Conflict governance decisions require deal registration timestamp, ownership policy reference, and accountable resolver identity.`

#### Bot 15 Required Tool Prompt Files

- `prompts/tool_partner_program_ops_api.md`
- `prompts/tool_partner_account_mapping_api.md`
- `prompts/tool_partner_enablement_execution_api.md`
- `prompts/tool_channel_conflict_governance_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 15A - `partner_activation_operator`

- `name`: `partner_activation_operator`
- `fexp_description`: `Operate partner recruit/onboard/enable/activate cycle`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,partner_program_ops_api,partner_account_mapping_api,partner_enablement_execution_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"partner_activation_scorecard_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","partner_batches","activation_funnel","enablement_coverage","pipeline_contribution","risk_flags","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["partner_activation_scorecard"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"partner_batches":{"type":"array","items":{"type":"object","required":["batch_id","partner_count","tier"],"additionalProperties":false,"properties":{"batch_id":{"type":"string"},"partner_count":{"type":"number","minimum":0},"tier":{"type":"string"}}}},"activation_funnel":{"type":"object","required":["recruited","onboarded","enabled","activated"],"additionalProperties":false,"properties":{"recruited":{"type":"number","minimum":0},"onboarded":{"type":"number","minimum":0},"enabled":{"type":"number","minimum":0},"activated":{"type":"number","minimum":0}}},"enablement_coverage":{"type":"number","minimum":0,"maximum":1},"pipeline_contribution":{"type":"object","required":["sourced_pipeline","influenced_pipeline"],"additionalProperties":false,"properties":{"sourced_pipeline":{"type":"number","minimum":0},"influenced_pipeline":{"type":"number","minimum":0}}},"risk_flags":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"partner_enablement_plan_schema","schema":{"type":"object","required":["artifact_type","version","program_id","enablement_tracks","owners","timeline","completion_criteria","dependencies"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["partner_enablement_plan"]},"version":{"type":"string"},"program_id":{"type":"string"},"enablement_tracks":{"type":"array","items":{"type":"object","required":["track_id","track_name","target_tier"],"additionalProperties":false,"properties":{"track_id":{"type":"string"},"track_name":{"type":"string"},"target_tier":{"type":"string"}}}},"owners":{"type":"array","items":{"type":"string"}},"timeline":{"type":"object","required":["start_date","target_activation_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"target_activation_date":{"type":"string"}}},"completion_criteria":{"type":"array","items":{"type":"string"}},"dependencies":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"partner_pipeline_quality_schema","schema":{"type":"object","required":["artifact_type","version","pipeline_snapshot","stage_conversion","sla_breaches","recommended_actions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["partner_pipeline_quality"]},"version":{"type":"string"},"pipeline_snapshot":{"type":"array","items":{"type":"object","required":["partner_ref","open_deals","pipeline_value"],"additionalProperties":false,"properties":{"partner_ref":{"type":"string"},"open_deals":{"type":"number","minimum":0},"pipeline_value":{"type":"number","minimum":0}}}},"stage_conversion":{"type":"array","items":{"type":"object","required":["stage","conversion_rate"],"additionalProperties":false,"properties":{"stage":{"type":"string"},"conversion_rate":{"type":"number","minimum":0,"maximum":1}}}},"sla_breaches":{"type":"array","items":{"type":"string"}},"recommended_actions":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce partner activation artifacts tied to measurable funnel progression; fail fast when partner ownership, enablement completion evidence, or pipeline attribution is missing.`

### Expert 15B - `channel_conflict_governor`

- `name`: `channel_conflict_governor`
- `fexp_description`: `Enforce deal registration and channel conflict handling`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,channel_conflict_governance_api,partner_account_mapping_api,partner_program_ops_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"channel_conflict_incident_schema","schema":{"type":"object","required":["artifact_type","version","analysis_window","incidents","resolution_log","policy_updates","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["channel_conflict_incident"]},"version":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"incidents":{"type":"array","items":{"type":"object","required":["incident_id","deal_ref","accounts_involved","conflict_type","opened_at","resolution_state","owner"],"additionalProperties":false,"properties":{"incident_id":{"type":"string"},"deal_ref":{"type":"string"},"accounts_involved":{"type":"array","items":{"type":"string"}},"conflict_type":{"type":"string","enum":["ownership_overlap","registration_collision","pricing_conflict","territory_conflict"]},"opened_at":{"type":"string"},"resolution_state":{"type":"string","enum":["open","in_review","resolved","escalated"]},"owner":{"type":"string"}}}},"resolution_log":{"type":"array","items":{"type":"string"}},"policy_updates":{"type":"array","items":{"type":"string"}},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"deal_registration_policy_schema","schema":{"type":"object","required":["artifact_type","version","registration_rules","approval_flow","exception_policy","sla_targets"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["deal_registration_policy"]},"version":{"type":"string"},"registration_rules":{"type":"array","items":{"type":"string"}},"approval_flow":{"type":"array","items":{"type":"string"}},"exception_policy":{"type":"array","items":{"type":"string"}},"sla_targets":{"type":"array","items":{"type":"object","required":["stage","target_hours"],"additionalProperties":false,"properties":{"stage":{"type":"string"},"target_hours":{"type":"number","minimum":0}}}}}}},{"schema_name":"conflict_resolution_audit_schema","schema":{"type":"object","required":["artifact_type","version","audit_window","resolved_cases","sla_compliance","repeat_conflict_patterns","required_remediations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["conflict_resolution_audit"]},"version":{"type":"string"},"audit_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"resolved_cases":{"type":"array","items":{"type":"string"}},"sla_compliance":{"type":"number","minimum":0,"maximum":1},"repeat_conflict_patterns":{"type":"array","items":{"type":"string"}},"required_remediations":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce enforceable conflict governance artifacts with accountable owners and SLA traceability; fail fast when incident evidence or policy linkage is incomplete.`

### Bot 16 - `scale_governance_bot`

- `accent_color`: `#1E293B`
- `title1`: `Scale Governance`
- `title2`: `Playbooks, guardrails, and controlled scaling`
- `occupation`: `Operations Governor`
- `typical_group`: `Ops / Governance`
- `intro_message`: `I codify operating playbooks and guardrail-controlled scale increments.`
- `tags`: [`Scale`, `Governance`, `Playbooks`]
- `featured_actions`: [`Generate and version playbook set` -> `playbook_codifier`, `Approve guarded scale increment` -> `scale_guardrail_controller`]
- `experts`: [`playbook_codifier`, `scale_guardrail_controller`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`, `playbook_repo_api`, `scale_guardrail_monitoring_api`, `scale_change_execution_api`, `scale_incident_response_api`]

#### Bot 16 Tool Catalog

- `playbook_repo_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Notion API`
        - `Confluence REST API`
        - `Google Drive API`
    - Provider method ids (`method_id`):
        - `notion.pages.create.v1`
        - `notion.pages.update.v1`
        - `confluence.pages.create.v1`
        - `confluence.pages.update.v1`
        - `gdrive.files.export.v1`
    - Call contract:
        - `playbook_repo_api(op="<operation>", args={...})`
        - Request envelope: JSON object with `op` as string and `args` as object.
        - Default behavior: if `op` is missing, return `help`.
    - Allowed operations (`op`):
        - `help`
        - `status`
        - `list_providers`
        - `list_methods`
        - `create_playbook`
        - `update_playbook`
        - `record_review_cycle`
        - `export_playbook_snapshot`
    - Allowed `args` schema:
        - `provider` (string): `notion | confluence | gdrive`
        - `method_id` (string, optional): must be from provider whitelist.
        - `playbook_id` (string, required for update/review/export operations)
        - `title` (string, required for create operation)
        - `owner` (string, required for create/update operations)
        - `version` (string, required for create/update operations)
        - `review_window_start` (string, optional)
        - `review_window_end` (string, optional)
        - `include_raw` (boolean, optional): default `false`.
    - Validation and fail-fast rules:
        - Reject unknown `op`.
        - Reject unknown `provider`.
        - Reject `method_id` outside provider whitelist.
        - Reject create/update operations without owner or version.
        - Reject export operation without `playbook_id`.
        - Reject review logging without review window boundaries.

- `scale_guardrail_monitoring_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Datadog API`
        - `Grafana Alerting HTTP API`
        - `Jira REST API`
    - Provider method ids (`method_id`):
        - `datadog.metrics.query.v1`
        - `grafana.alerts.list.v1`
        - `jira.issues.search.v1`
        - `jira.issues.create.v1`
    - Constraint note:
        - `Guardrail assessments are valid only when metric query window, threshold source, and alert owner are explicit.`

- `scale_change_execution_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Jira REST API`
        - `Asana API`
        - `Linear GraphQL API`
        - `Notion API`
    - Provider method ids (`method_id`):
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
        - `asana.tasks.create.v1`
        - `linear.issues.create.v1`
        - `notion.pages.update.v1`
    - Constraint note:
        - `Every scale change must include change_owner, rollback_trigger, and verification step list; fail fast if any is missing.`

- `scale_incident_response_api`
    - Integration mode: `Request/Response`
    - APIs:
        - `Jira REST API`
        - `Notion API`
        - `Confluence REST API`
    - Provider method ids (`method_id`):
        - `jira.issues.create.v1`
        - `jira.issues.transition.v1`
        - `notion.pages.update.v1`
        - `confluence.pages.update.v1`
    - Constraint note:
        - `Rollback and incident records must reference triggering guardrail, decision owner, and closure evidence before incident closure.`

#### Bot 16 Required Tool Prompt Files

- `prompts/tool_playbook_repo_api.md`
- `prompts/tool_scale_guardrail_monitoring_api.md`
- `prompts/tool_scale_change_execution_api.md`
- `prompts/tool_scale_incident_response_api.md`
- `prompts/tool_flexus_policy_document.md`
- `prompts/tool_print_widget.md`

### Expert 16A - `playbook_codifier`

- `name`: `playbook_codifier`
- `fexp_description`: `Convert proven operations into versioned playbooks`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,playbook_repo_api,scale_change_execution_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"playbook_library_schema","schema":{"type":"object","required":["artifact_type","version","playbooks","owners","last_validation_cycle","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["playbook_library"]},"version":{"type":"string"},"playbooks":{"type":"array","items":{"type":"object","required":["playbook_id","scope","trigger_conditions","steps","owner","version","status","guardrails"],"additionalProperties":false,"properties":{"playbook_id":{"type":"string"},"scope":{"type":"string"},"trigger_conditions":{"type":"array","items":{"type":"string"}},"steps":{"type":"array","items":{"type":"string"}},"owner":{"type":"string"},"version":{"type":"string"},"status":{"type":"string","enum":["draft","active","deprecated"]},"guardrails":{"type":"array","items":{"type":"string"}}}}},"owners":{"type":"array","items":{"type":"string"}},"last_validation_cycle":{"type":"string"},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"playbook_change_log_schema","schema":{"type":"object","required":["artifact_type","version","change_window","changes","approval_log","rollback_notes"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["playbook_change_log"]},"version":{"type":"string"},"change_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"changes":{"type":"array","items":{"type":"object","required":["playbook_id","change_type","changed_by","change_reason"],"additionalProperties":false,"properties":{"playbook_id":{"type":"string"},"change_type":{"type":"string","enum":["add","update","deprecate"]},"changed_by":{"type":"string"},"change_reason":{"type":"string"}}}},"approval_log":{"type":"array","items":{"type":"string"}},"rollback_notes":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"operating_sop_compliance_schema","schema":{"type":"object","required":["artifact_type","version","compliance_window","required_processes","compliance_rate","violations","remediations"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["operating_sop_compliance"]},"version":{"type":"string"},"compliance_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"required_processes":{"type":"array","items":{"type":"string"}},"compliance_rate":{"type":"number","minimum":0,"maximum":1},"violations":{"type":"array","items":{"type":"string"}},"remediations":{"type":"array","items":{"type":"string"}}}}}]
- `body_md`: `Produce versioned, auditable operating playbooks and change logs; fail fast when ownership, approval chain, or guardrail mapping is incomplete.`

### Expert 16B - `scale_guardrail_controller`

- `name`: `scale_guardrail_controller`
- `fexp_description`: `Operate scale increments with explicit guardrail criteria`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,scale_guardrail_monitoring_api,scale_change_execution_api,scale_incident_response_api`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [{"schema_name":"scale_increment_plan_schema","schema":{"type":"object","required":["artifact_type","version","increment_id","analysis_window","capacity_delta","guardrails","verification_steps","rollback_triggers","owner","sources"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["scale_increment_plan"]},"version":{"type":"string"},"increment_id":{"type":"string"},"analysis_window":{"type":"object","required":["start_date","end_date"],"additionalProperties":false,"properties":{"start_date":{"type":"string"},"end_date":{"type":"string"}}},"capacity_delta":{"type":"object","required":["current_capacity","target_capacity"],"additionalProperties":false,"properties":{"current_capacity":{"type":"number","minimum":0},"target_capacity":{"type":"number","minimum":0}}},"guardrails":{"type":"array","items":{"type":"string"}},"verification_steps":{"type":"array","items":{"type":"string"}},"rollback_triggers":{"type":"array","items":{"type":"string"}},"owner":{"type":"string"},"sources":{"type":"array","items":{"type":"object","required":["source_type","source_ref"],"additionalProperties":false,"properties":{"source_type":{"type":"string","enum":["api","artifact","tool_output","event_stream","expert_handoff","user_directive"]},"source_ref":{"type":"string"}}}}}}},{"schema_name":"scale_rollback_decision_schema","schema":{"type":"object","required":["artifact_type","version","increment_id","decision","decision_time","triggering_guardrails","evidence","owner","actions"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["scale_rollback_decision"]},"version":{"type":"string"},"increment_id":{"type":"string"},"decision":{"type":"string","enum":["continue","pause","rollback"]},"decision_time":{"type":"string"},"triggering_guardrails":{"type":"array","items":{"type":"string"}},"evidence":{"type":"array","items":{"type":"string"}},"owner":{"type":"string"},"actions":{"type":"array","items":{"type":"string"}}}}},{"schema_name":"guardrail_breach_incident_schema","schema":{"type":"object","required":["artifact_type","version","incident_id","opened_at","breached_guardrails","impact_assessment","containment_actions","resolution_state","resolver"],"additionalProperties":false,"properties":{"artifact_type":{"type":"string","enum":["guardrail_breach_incident"]},"version":{"type":"string"},"incident_id":{"type":"string"},"opened_at":{"type":"string"},"breached_guardrails":{"type":"array","items":{"type":"string"}},"impact_assessment":{"type":"array","items":{"type":"string"}},"containment_actions":{"type":"array","items":{"type":"string"}},"resolution_state":{"type":"string","enum":["open","mitigated","resolved","postmortem_required"]},"resolver":{"type":"string"}}}}]
- `body_md`: `Control scale increments with explicit monitor-trigger-action rules; fail fast when guardrail evidence, rollback triggers, or accountable decision ownership is missing.`

---

## Level 3 Skill Definitions (Schema-Aligned)

### Skill 01

- `name`: `skill_google_trends_signal_detection`
- `description`: `Google Trends signal detection method`
- `body_md`: `Use Google Trends data to detect seasonality, breakout terms, region deltas, and baseline shifts.
как правильно пользоваться гугл трендами по бест практис`.

### Skill 02

- `name`: `skill_x_signal_detection`
- `description`: `X/Twitter signal detection method`
- `body_md`: `Detect narrative drift, velocity bursts, and noise-filtered account cluster signals.`

### Skill 03

- `name`: `skill_reddit_signal_detection`
- `description`: `Reddit signal detection method`
- `body_md`: `Score subreddit relevance, comment-depth quality, and noise-filtered discussion trends.`

### Skill 04

- `name`: `skill_web_change_detection`
- `description`: `Competitor web-change detection method`
- `body_md`: `Classify webpage diffs by pricing, positioning, CTA, and feature-claim changes.`

### Skill 05

- `name`: `skill_past_behavior_questioning`
- `description`: `Past-behavior interview design discipline`
- `body_md`: `Force past-event phrasing and block hypothetical, leading, or abstract prompts.`

### Skill 06

- `name`: `skill_jtbd_outcome_formatting`
- `description`: `JTBD outcome normalization`
- `body_md`: `Convert raw interview language into structured desired-outcome statements.`

### Skill 07

- `name`: `skill_qualitative_coding`
- `description`: `Qualitative coding and saturation control`
- `body_md`: `Apply coding consistency, theme merge rules, and saturation checks.`

### Skill 08

- `name`: `skill_meta_ads_execution`
- `description`: `Meta Ads single-platform execution discipline`
- `body_md`: `Execute one-platform Meta test, honor spend cap, and emit traceable test metrics.`

### Skill 09

- `name`: `skill_google_ads_execution`
- `description`: `Google Ads single-platform execution discipline`
- `body_md`: `Execute one-platform Google Ads test with guardrails and structured result output.`

### Skill 10

- `name`: `skill_x_ads_execution`
- `description`: `X Ads single-platform execution discipline`
- `body_md`: `Execute one-platform X Ads test with controlled spend and auditable metrics.`

## Level 3 Expert Acceptance Criteria

Expert layer is accepted only when:

- each Level 2 unit is owned by exactly one primary expert;
- each expert has explicit input provenance rules;
- each expert has explicit output contract and done-definition;
- each expert has one explicit success path (done-definition) and one failure-path escalation;
- doers for research, creatives, ads, pilots, and governance are explicitly visible.

## Bot Integration Footprint Rule

- Bot-level integrations are the union of `TG-*` groups from experts included in that bot.
- If two experts require different access to the same platform, apply the stricter permission profile.
- `Blocked` rules from any included expert remain blocked at bot scope unless boss explicitly overrides.
- Before bot assembly, export a per-bot matrix: `integration`, `purpose`, `access mode`, `owning expert`.

## SMB Model Overlays (B2B, B2C, B2B2C, B2B2B)

These overlays adjust execution logic without changing the 8-stage backbone.

### B2B

- More weight on buying committee mapping, proof artifacts, and implementation trust.
- Stage 5-7 require explicit commercial motion design (sales cycle and ROI narrative).

### B2C

- More weight on activation speed, funnel leakage, and repeated behavior signals.
- Stage 4-6 prioritize conversion/retention loops before heavy sales structures.

### B2B2C

- Requires dual validation: intermediary partner economics + end-consumer experience.
- Stage 7-8 must include partner enablement and shared CX consistency governance.

### B2B2B

- Requires partner lifecycle discipline: recruit -> onboard -> enable -> activate -> optimize.
- Stage 7-8 require lead routing, incentive alignment, and channel conflict controls early.

## Reliability Notes (For Next Decomposition Steps)

- Prefer explicit pass/fail thresholds for each substage before resource expansion.
- Keep outputs artifact-driven to reduce orchestration ambiguity later in bot design.
- Avoid parallel channel sprawl until one channel-motion pair shows repeatability.
- Treat partner operations as first-class system design in B2B2C/B2B2B cases.

## Notes

- This is a living document and should be expanded by depth levels.
- This version adds Level 3 (one step deeper than Level 2).

## Source Pack (Used For This Version)

### Opportunity and Discovery

- https://www.jpattonassociates.com/opportunity-canvas/
- https://www.alexandercowan.com/customer-discovery-handbook/
- https://steveblank.com/2009/09/17/the-path-of-warriors-and-winners/
- https://web.stanford.edu/class/me113/d_thinking.html
- https://dschool.stanford.edu/resources/the-bootcamp-bootleg

### Validation, MVP, and Early Sales

- https://blog.logrocket.com/product-management/concierge-wizard-of-oz-mvp
- https://stripe.com/blog/atlas-starting-sales
- https://www.d-eship.com/step2/
- https://www.d-eship.com/step4/
- https://www.oreilly.com/library/view/the-startup-owners/9781119690689/c10.xhtml

### PMF and Fit Consolidation

- https://www.reforge.com/guides/measure-product-market-fit-with-retention-and-growth
- https://learningloop.io/plays/product-market-fit-survey
- https://www.reforge.com/blog/four-fits-growth-framework
- https://jobs-to-be-done.com/outcome-driven-innovation-odi-is-jobs-to-be-done-theory-in-practice-2944c6ebc40e

### GTM, RTM, and Scaling

- https://www.oxx.vc/go-to-market-fit/introduction-to-go-to-market-fit/
- https://www.oxx.vc/go-to-market-fit/
- https://medium.com/@yegg/the-bullseye-framework-for-getting-traction-ef49d05bfd7e
- https://medium.com/@yegg/the-19-channels-you-can-use-to-get-traction-93c762d19339
- https://amplitude.com/blog/pirate-metrics-framework
- https://en.wikipedia.org/wiki/Crossing_the_Chasm

### Partner-Led and B2B2X Execution

- https://demandzen.com/b2b-channel-partner-lifecycle-guide/
- https://www.journeybee.io/resources/partner-lifecycle-management
- https://www.forrester.com/blogs/shared-customer-experience-what-happens-when-your-cx-depends-on-partners/
- https://umbrex.com/resources/frameworks/marketing-frameworks/channel-conflict-management-framework/

### Additional Sources Used For Level 2 and Level 3

- https://brianbalfour.com/essays/channel-model-fit-for-user-acquisition
- https://brianbalfour.com/four-fits-growth-framework
- https://review.firstround.com/0-5m-how-to-nail-founder-led-sales/
- https://www.nngroup.com/articles/success-rate-the-simplest-usability-metric/
- https://measuringu.com/task-completion/
- https://mixpanel.com/blog/guardrail-metrics
- https://support.google.com/google-ads/answer/6167129?hl=en
- https://www.klue.com/blog/churn-interviews
- https://umbrex.com/resources/frameworks/marketing-frameworks/route-to-market-design-framework/
- https://learningloop.io/plays/product-market-fit-survey
