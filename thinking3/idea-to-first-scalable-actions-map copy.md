
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

#### 2.1 Segment map and beachhead selection

- Inputs: candidate segments, trigger events, accessibility notes, TAM assumptions.
- Execution: segment by firmographic/behavioral/trigger criteria and enforce beachhead tests (word of mouth, same sales process, same product).
- Output artifact: `Beachhead Decision Memo`.
- Local evidence gate: one beachhead selected and alternatives explicitly parked.
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
- Output artifact: `Value Proposition Canvas per Beachhead`.
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

This section keeps only fields that map to current builder schema:

- bot config schema (`bot_config_schema.json`)
- expert frontmatter schema (rendered by `bot_registry_engine.py`)
- optional runtime metadata supported by `no_special_code_bot.py`

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
  - APIs:
    - `Google Search Console API`
    - `Google Ads API (Keyword Planning)`
    - `DataForSEO Trends API`
    - `SerpApi (Google Search, Google Trends, Google Shopping engines)`
    - `Semrush API (Trends + Keyword reports)`
    - `Bing Webmaster API`
  - Required methods:
    - `Google Search Console`: `searchanalytics.query`
    - `Google Ads`: `GenerateKeywordIdeas`, `GenerateKeywordHistoricalMetrics`, `GenerateKeywordForecastMetrics`
    - `DataForSEO Trends`: `keywords_data/dataforseo_trends/explore/live`, `.../subregion_interests/live`, `.../demography/live`, `.../merged_data/live`
    - `SerpApi`: `/search?engine=google`, `/search?engine=google_trends`, `/search?engine=google_shopping`
    - `Semrush`: `Trends API traffic_summary`, `Trends API daily_traffic`, `Analytics keyword reports`
    - `Bing Webmaster`: `GetPageStats`, `GetPageQueryStats`, `GetRankAndTrafficStats`
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
  - APIs:
    - `Reddit API`
    - `X API v2`
    - `YouTube Data API v3`
    - `TikTok Research API`
    - `Instagram Graph API`
    - `Pinterest API`
    - `Product Hunt GraphQL API`
  - Required methods:
    - `Reddit`: `/r/{subreddit}/new`, `/r/{subreddit}/hot`, `/search`, `/comments/{article}`
    - `X`: `GET /2/tweets/counts/recent`, `GET /2/tweets/search/recent`
    - `YouTube`: `search.list`, `videos.list`, `commentThreads.list`
    - `TikTok`: `POST /v2/research/video/query/`
    - `Instagram`: `GET /ig_hashtag_search`, `GET /{ig-hashtag-id}/recent_media`, `GET /{ig-hashtag-id}/top_media`
    - `Pinterest`: `/trends/keywords/{region}/top/{trend_type}`
    - `Product Hunt`: GraphQL `posts`, `topics`, `votesCount` queries

- `signal_news_events_api`
  - APIs:
    - `GDELT API`
    - `Event Registry API`
    - `NewsAPI`
    - `GNews API`
    - `NewsData.io API`
    - `MediaStack API`
    - `NewsCatcher API`
    - `Perigon API`
  - Required methods:
    - `GDELT`: `doc`, `events`
    - `Event Registry`: `article/getArticles`, `event/getEvents`
    - `NewsAPI`: `/v2/everything`, `/v2/top-headlines`
    - `GNews`: `/api/v4/search`, `/api/v4/top-headlines`
    - `NewsData.io`: `/api/1/news`
    - `MediaStack`: `/v1/news`
    - `NewsCatcher`: `/v3/search`, `/v3/latest_headlines`
    - `Perigon`: `/v1/all`, `/v1/topics`

- `signal_review_voice_api`
  - APIs:
    - `Trustpilot API`
    - `Yelp Fusion API`
    - `G2 data provider API`
    - `Capterra data provider API`
  - Required methods:
    - `Trustpilot`: `GET /v1/business-units/find`, `GET /v1/business-units/{businessUnitId}`, `GET /v1/business-units/{businessUnitId}/reviews`
    - `Yelp`: `GET /v3/businesses/search`, `GET /v3/businesses/{id}`, `GET /v3/businesses/{id}/reviews`
    - `G2`: `vendor listing endpoint`, `reviews endpoint`, `category benchmark endpoint`
    - `Capterra`: `product listing endpoint`, `reviews endpoint`, `category endpoint`

- `signal_marketplace_demand_api`
  - APIs:
    - `Amazon SP-API`
    - `eBay Browse API`
    - `eBay Marketplace Insights API`
    - `Google Shopping Content API`
  - Required methods:
    - `Amazon`: `searchCatalogItems`, `getCatalogItem`, `getItemOffersBatch`, `getListingOffersBatch`
    - `eBay Browse`: `getItems`, `search`
    - `eBay Marketplace Insights`: `item_sales/search`
    - `Google Shopping Content`: `reports.search` with Topic Trends fields

- `signal_web_traffic_intel_api`
  - APIs:
    - `Similarweb API`
    - `Shopify Admin analytics surface`
  - Required methods:
    - `Similarweb`: `traffic-and-engagement`, `traffic-sources`, `traffic-geography`, `website-ranking`, `similar-sites`
    - `Shopify`: `reports list`, `reports dates`, `reports get`

- `signal_jobs_demand_api`
  - APIs:
    - `Adzuna API`
    - `Bright Data Jobs API`
    - `Coresignal API`
    - `TheirStack API`
    - `Oxylabs jobs data API`
    - `HasData jobs APIs`
    - `Levels.fyi API`
    linkedind jobs?
    glassdoor?

  - Required methods:
    - `Adzuna`: `search ads`, `regional data`
    - `Bright Data`: `jobs data feed`, `jobs dataset query`
    - `Coresignal`: `job posts endpoint`, `company profile endpoint`
    - `TheirStack`: `job search endpoint`, `company hiring endpoint`
    - `Oxylabs`: `jobs source query endpoint`
    - `HasData`: `Indeed jobs endpoint`, `Glassdoor endpoint`
    - `Levels.fyi`: `compensation benchmark endpoint`

- `signal_dev_ecosystem_api`
  - APIs:
    - `GitHub REST API`
    - `Stack Exchange API`
  - Required methods:
    - `GitHub`: `/search/repositories`, `/search/issues`, `/repos/{owner}/{repo}`
    - `Stack Exchange`: `/questions`, `/tags/{tags}/info`, `/tags/{tags}/related`

- `signal_public_interest_api`
  - APIs:
    - `Wikimedia Pageviews API`
  - Required methods:
    - `Wikimedia`: `/metrics/pageviews/per-article/...`, `/metrics/pageviews/aggregate/...`

- `signal_professional_network_api`
  - APIs:
    - `LinkedIn Marketing API`
  - Required methods:
    - `organization posts endpoint`
    - `organization social actions endpoint`
    - `organization follower statistics endpoint`
  - Constraint note:
    - `Use only where provider terms allow this exact use case; treat as restricted integration by default.`

### Expert 01A - `market_signal_detector`

- `name`: `market_signal_detector`
- `fexp_description`: `Detect and normalize market signals for one channel per run`
- `fexp_allow_tools`: `flexus_policy_document,print_widget,signal_search_demand_api,signal_social_trends_api,signal_news_events_api,signal_review_voice_api,signal_marketplace_demand_api,signal_web_traffic_intel_api,signal_jobs_demand_api,signal_dev_ecosystem_api,signal_public_interest_api,signal_professional_network_api`
- `fexp_block_tools`: ``
- `skills`: [`skill_google_trends_signal_detection`, `skill_x_signal_detection`, `skill_reddit_signal_detection`, `skill_web_change_detection`]
- `pdoc_output_schemas`: [`market_signal_snapshot_schema`, `market_signal_error_schema`]
- `body_md`: `Create a channel signal snapshot with evidence links and confidence notes.`

### Expert 01B - `signal_boundary_analyst`

- `name`: `signal_boundary_analyst`
- `fexp_description`: `Aggregate channel snapshots and produce bounded opportunity artifacts`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`signal_register_schema`, `hypothesis_backlog_schema`]
- `body_md`: `Aggregate snapshots, define boundaries, and produce risk-ranked artifact payloads.`

### Bot 02 - `customer_discovery_bot`

- `accent_color`: `#0D9488`
- `title1`: `Customer Discovery`
- `title2`: `Interview and survey evidence operations`
- `occupation`: `Discovery Operator`
- `typical_group`: `GTM / Discovery`
- `intro_message`: `I run structured discovery workflows and keep evidence quality high.`
- `tags`: [`Discovery`, `JTBD`, `Research`]
- `featured_actions`: [`Prepare next interview instrument` -> `discovery_instrument_designer`]
- `experts`: [`discovery_instrument_designer`, `jtbd_interview_operator`]
- `skills`: [`skill_past_behavior_questioning`, `skill_jtbd_outcome_formatting`, `skill_qualitative_coding`]
- `tools`: [`flexus_policy_document`, `print_widget`]

### Expert 02A - `discovery_instrument_designer`

- `name`: `discovery_instrument_designer`
- `fexp_description`: `Design high-quality interview and survey instruments`
- `fexp_allow_tools`: `flexus_policy_document,print_widget`
- `fexp_block_tools`: ``
- `skills`: [`skill_past_behavior_questioning`, `skill_jtbd_outcome_formatting`]
- `pdoc_output_schemas`: [`interview_instrument_schema`, `survey_instrument_schema`]
- `body_md`: `Design and version discovery instruments mapped to explicit hypotheses.`

### Expert 02B - `jtbd_interview_operator`

- `name`: `jtbd_interview_operator`
- `fexp_description`: `Operate JTBD interviews and produce coded evidence artifacts`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: [`skill_qualitative_coding`]
- `pdoc_output_schemas`: [`interview_corpus_schema`, `jtbd_outcomes_schema`]
- `body_md`: `Run interviews, code outcomes, and emit structured evidence payloads.`

### Bot 03 - `segment_qualification_bot`

- `accent_color`: `#0284C7`
- `title1`: `Segment Qualification`
- `title2`: `Enrichment and beachhead selection`
- `occupation`: `Segment Analyst`
- `typical_group`: `GTM / Qualification`
- `intro_message`: `I enrich segment candidates and produce one explicit beachhead decision.`
- `tags`: [`ICP`, `Segmentation`, `Beachhead`]
- `featured_actions`: [`Enrich candidate segments` -> `segment_data_enricher`]
- `experts`: [`segment_data_enricher`, `beachhead_decision_analyst`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 03A - `segment_data_enricher`

- `name`: `segment_data_enricher`
- `fexp_description`: `Enrich candidate segments with structured data fields`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`segment_enrichment_schema`]
- `body_md`: `Enrich segments and output complete per-segment payload records.`

### Expert 03B - `beachhead_decision_analyst`

- `name`: `beachhead_decision_analyst`
- `fexp_description`: `Select a single beachhead with explicit rejection rationale`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`beachhead_decision_schema`]
- `body_md`: `Score enriched segments and output one decision artifact with rationale.`

### Bot 04 - `pain_alternatives_bot`

- `accent_color`: `#7C3AED`
- `title1`: `Pain and Alternatives`
- `title2`: `Pain quantification and alternative mapping`
- `occupation`: `Problem Analyst`
- `typical_group`: `GTM / Qualification`
- `intro_message`: `I quantify pain and map alternatives in structured artifacts.`
- `tags`: [`Pain`, `Alternatives`, `Evidence`]
- `featured_actions`: [`Quantify top customer pains` -> `pain_quantifier`]
- `experts`: [`pain_quantifier`, `alternative_mapper`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 04A - `pain_quantifier`

- `name`: `pain_quantifier`
- `fexp_description`: `Convert pain evidence into numeric ranges and uncertainty bands`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`pain_economics_schema`]
- `body_md`: `Produce a numeric pain-economics payload with confidence indicators.`

### Expert 04B - `alternative_mapper`

- `name`: `alternative_mapper`
- `fexp_description`: `Map direct, indirect, and status-quo alternatives`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`alternative_landscape_schema`]
- `body_md`: `Produce an alternatives payload with adoption and failure reasons.`

### Bot 05 - `positioning_offer_bot`

- `accent_color`: `#0F766E`
- `title1`: `Positioning and Offer`
- `title2`: `Value proposition and package architecture`
- `occupation`: `Positioning Architect`
- `typical_group`: `GTM / Messaging`
- `intro_message`: `I turn validated pains into positioning and offer artifacts.`
- `tags`: [`Positioning`, `Offer`, `Messaging`]
- `featured_actions`: [`Draft value proposition` -> `value_proposition_synthesizer`]
- `experts`: [`value_proposition_synthesizer`, `positioning_test_operator`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`]

### Expert 05A - `value_proposition_synthesizer`

- `name`: `value_proposition_synthesizer`
- `fexp_description`: `Build value proposition and package boundaries`
- `fexp_allow_tools`: `flexus_policy_document,print_widget`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [`value_prop_schema`, `offer_packaging_schema`]
- `body_md`: `Generate value proposition and packaging payloads.`

### Expert 05B - `positioning_test_operator`

- `name`: `positioning_test_operator`
- `fexp_description`: `Run positioning test iterations and select winner`
- `fexp_allow_tools`: `flexus_policy_document,print_widget`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [`positioning_test_schema`]
- `body_md`: `Generate tested positioning brief payloads with explicit winner.`

### Bot 06 - `pricing_validation_bot`

- `accent_color`: `#B45309`
- `title1`: `Pricing Validation`
- `title2`: `Price corridor and commitment evidence`
- `occupation`: `Pricing Analyst`
- `typical_group`: `GTM / Pricing`
- `intro_message`: `I validate pricing hypotheses with structured evidence artifacts.`
- `tags`: [`Pricing`, `WTP`, `Validation`]
- `featured_actions`: [`Estimate initial price corridor` -> `price_corridor_modeler`]
- `experts`: [`price_corridor_modeler`, `commitment_evidence_verifier`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 06A - `price_corridor_modeler`

- `name`: `price_corridor_modeler`
- `fexp_description`: `Estimate floor/target/ceiling corridor with confidence`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`preliminary_price_corridor_schema`]
- `body_md`: `Produce a preliminary price corridor payload and assumptions list.`

### Expert 06B - `commitment_evidence_verifier`

- `name`: `commitment_evidence_verifier`
- `fexp_description`: `Verify stated willingness-to-pay against commitment signals`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`validated_price_hypothesis_schema`]
- `body_md`: `Produce a validated pricing payload tied to commitment evidence.`

### Bot 07 - `experiment_design_bot`

- `accent_color`: `#475569`
- `title1`: `Experiment Design`
- `title2`: `Test-design and reliability checks`
- `occupation`: `Experiment Architect`
- `typical_group`: `GTM / Experiments`
- `intro_message`: `I turn risks into executable experiment  with guardrails.`
- `tags`: [`Experiment`, `Hypothesis`, `Reliability`]
- `featured_actions`: [`Draft experiment ` -> `hypothesis_architect`]
- `experts`: [`hypothesis_architect`, `reliability_checker`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 07A - `hypothesis_architect`

- `name`: `hypothesis_architect`
- `fexp_description`: `Convert risk backlog into executable experiment `
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`experiment_card_draft_schema`]
- `body_md`: `Produce experiment payloads with hypothesis and metric definitions.`

### Expert 07B - `reliability_checker`

- `name`: `reliability_checker`
- `fexp_description`: `Validate reliability conditions before experiment execution`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`experiment_approval_schema`]
- `body_md`: `Validate experiment  and emit approval or rejection payload.`

### Bot 08 - `mvp_validation_bot`

- `accent_color`: `#1D4ED8`
- `title1`: `MVP Validation`
- `title2`: `MVP run operations and telemetry integrity`
- `occupation`: `MVP Operator`
- `typical_group`: `GTM / Validation`
- `intro_message`: `I run MVP tests and produce auditable decision artifacts.`
- `tags`: [`MVP`, `Telemetry`, `Validation`]
- `featured_actions`: [`Run approved MVP test` -> `mvp_flow_operator`]
- `experts`: [`mvp_flow_operator`, `telemetry_integrity_analyst`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 08A - `mvp_flow_operator`

- `name`: `mvp_flow_operator`
- `fexp_description`: `Execute approved MVP flow on bounded cohort`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`mvp_run_log_schema`]
- `body_md`: `Run MVP flows and emit run-log payloads.`

### Expert 08B - `telemetry_integrity_analyst`

- `name`: `telemetry_integrity_analyst`
- `fexp_description`: `Validate telemetry quality and produce threshold-based decision`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`telemetry_decision_memo_schema`]
- `body_md`: `Evaluate telemetry and emit decision memo payloads.`

### Bot 09 - `pipeline_qualification_bot`

- `accent_color`: `#0369A1`
- `title1`: `Pipeline Qualification`
- `title2`: `Prospecting and qualification mapping`
- `occupation`: `Pipeline Operator`
- `typical_group`: `GTM / Pipeline`
- `intro_message`: `I generate qualified early pipeline and qualification artifacts.`
- `tags`: [`Pipeline`, `Prospecting`, `Qualification`]
- `featured_actions`: [`Run prospecting batch` -> `prospect_acquisition_operator`]
- `experts`: [`prospect_acquisition_operator`, `qualification_mapper`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`, `print_widget`]

### Expert 09A - `prospect_acquisition_operator`

- `name`: `prospect_acquisition_operator`
- `fexp_description`: `Source and contact ICP-aligned prospects`
- `fexp_allow_tools`: `flexus_policy_document,print_widget`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [`prospecting_batch_schema`]
- `body_md`: `Produce prospecting batch and outreach log payloads.`

### Expert 09B - `qualification_mapper`

- `name`: `qualification_mapper`
- `fexp_description`: `Map qualification state and buying blockers`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`qualification_map_schema`]
- `body_md`: `Produce qualification rubric and deal-map payloads.`

### Bot 10 - `creative_paid_channels_bot`

- `accent_color`: `#BE185D`
- `title1`: `Creative and Paid Channels`
- `title2`: `Creative variants and one-platform paid tests`
- `occupation`: `Paid Growth Operator`
- `typical_group`: `GTM / Demand`
- `intro_message`: `I create testable creatives and run controlled paid-channel tests.`
- `tags`: [`Creative`, `Paid`, `Acquisition`]
- `featured_actions`: [`Generate creative variant pack` -> `creative_producer`]
- `experts`: [`creative_producer`, `paid_channel_operator`]
- `skills`: [`skill_meta_ads_execution`, `skill_google_ads_execution`, `skill_x_ads_execution`]
- `tools`: [`flexus_policy_document`, `print_widget`]

### Expert 10A - `creative_producer`

- `name`: `creative_producer`
- `fexp_description`: `Generate and version creative variants`
- `fexp_allow_tools`: `flexus_policy_document,print_widget`
- `fexp_block_tools`: ``
- `skills`: `[]`
- `pdoc_output_schemas`: [`creative_variant_pack_schema`]
- `body_md`: `Produce creative variant payloads linked to hypotheses.`

### Expert 10B - `paid_channel_operator`

- `name`: `paid_channel_operator`
- `fexp_description`: `Run one-platform paid tests with guardrails`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: [`skill_meta_ads_execution`, `skill_google_ads_execution`, `skill_x_ads_execution`]
- `pdoc_output_schemas`: [`paid_channel_result_schema`]
- `body_md`: `Execute one-platform tests and emit spend + performance payloads.`

### Bot 11 - `pilot_delivery_bot`

- `accent_color`: `#15803D`
- `title1`: `Pilot Delivery`
- `title2`: `Paid pilot contracting and first value delivery`
- `occupation`: `Pilot Delivery Manager`
- `typical_group`: `GTM / Delivery`
- `intro_message`: `I convert qualified opportunities into paid pilot outcomes.`
- `tags`: [`Pilot`, `Delivery`, `Activation`]
- `featured_actions`: [`Prepare pilot contracting packet` -> `pilot_contracting_operator`]
- `experts`: [`pilot_contracting_operator`, `first_value_delivery_operator`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 11A - `pilot_contracting_operator`

- `name`: `pilot_contracting_operator`
- `fexp_description`: `Define and finalize paid pilot terms`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`pilot_contract_packet_schema`]
- `body_md`: `Produce signed pilot packet payload candidates.`

### Expert 11B - `first_value_delivery_operator`

- `name`: `first_value_delivery_operator`
- `fexp_description`: `Drive first value delivery and collect proof artifacts`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`first_value_evidence_schema`]
- `body_md`: `Produce first-win evidence payloads and repeatability notes.`

### Bot 12 - `retention_intelligence_bot`

- `accent_color`: `#0E7490`
- `title1`: `Retention Intelligence`
- `title2`: `Cohort and PMF confidence synthesis`
- `occupation`: `Retention Analyst`
- `typical_group`: `GTM / Retention`
- `intro_message`: `I synthesize retention, revenue, and PMF confidence evidence.`
- `tags`: [`Retention`, `PMF`, `Cohorts`]
- `featured_actions`: [`Run cohort retention analysis` -> `cohort_revenue_analyst`]
- `experts`: [`cohort_revenue_analyst`, `pmf_survey_interpreter`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 12A - `cohort_revenue_analyst`

- `name`: `cohort_revenue_analyst`
- `fexp_description`: `Diagnose activation-retention-revenue behavior`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`cohort_revenue_review_schema`]
- `body_md`: `Produce activation funnel, cohort, and revenue quality payloads.`

### Expert 12B - `pmf_survey_interpreter`

- `name`: `pmf_survey_interpreter`
- `fexp_description`: `Interpret PMF survey evidence with behavioral context`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`pmf_confidence_scorecard_schema`]
- `body_md`: `Produce PMF confidence scorepayloads.`

### Bot 13 - `churn_learning_bot`

- `accent_color`: `#7C2D12`
- `title1`: `Churn Learning`
- `title2`: `Churn interviews and root-cause classification`
- `occupation`: `Churn Analyst`
- `typical_group`: `GTM / Retention`
- `intro_message`: `I extract churn root causes into prioritized fix artifacts.`
- `tags`: [`Churn`, `RootCause`, `Fixes`]
- `featured_actions`: [`Run churn interview batch` -> `churn_interview_operator`]
- `experts`: [`churn_interview_operator`, `rootcause_classifier`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 13A - `churn_interview_operator`

- `name`: `churn_interview_operator`
- `fexp_description`: `Run structured churn interviews`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`churn_interview_corpus_schema`]
- `body_md`: `Produce churn interview corpus payloads.`

### Expert 13B - `rootcause_classifier`

- `name`: `rootcause_classifier`
- `fexp_description`: `Classify churn drivers and prioritize fixes`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`churn_rootcause_backlog_schema`]
- `body_md`: `Produce churn root-cause backlog payloads.`

### Bot 14 - `gtm_economics_rtm_bot`

- `accent_color`: `#334155`
- `title1`: `GTM Economics and RTM`
- `title2`: `Unit economics and route-to-market rules`
- `occupation`: `GTM Economist`
- `typical_group`: `GTM / Economics`
- `intro_message`: `I lock viable GTM economics and codify RTM rules.`
- `tags`: [`UnitEconomics`, `RTM`, `GTM`]
- `featured_actions`: [`Evaluate unit economics readiness` -> `unit_economics_modeler`]
- `experts`: [`unit_economics_modeler`, `rtm_rules_architect`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 14A - `unit_economics_modeler`

- `name`: `unit_economics_modeler`
- `fexp_description`: `Model payback and margin viability`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`unit_economics_review_schema`]
- `body_md`: `Produce unit economics review and channel stack payloads.`

### Expert 14B - `rtm_rules_architect`

- `name`: `rtm_rules_architect`
- `fexp_description`: `Define enforceable RTM ownership and engagement rules`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`rtm_rules_schema`]
- `body_md`: `Produce RTM rules-of-engagement payloads.`

### Bot 15 - `partner_ecosystem_bot`

- `accent_color`: `#166534`
- `title1`: `Partner Ecosystem`
- `title2`: `Partner activation and channel conflict governance`
- `occupation`: `Partner Program Operator`
- `typical_group`: `GTM / Partners`
- `intro_message`: `I run partner lifecycle operations and conflict governance artifacts.`
- `tags`: [`Partners`, `PRM`, `Channel`]
- `featured_actions`: [`Run partner activation cycle` -> `partner_activation_operator`]
- `experts`: [`partner_activation_operator`, `channel_conflict_governor`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 15A - `partner_activation_operator`

- `name`: `partner_activation_operator`
- `fexp_description`: `Operate partner recruit/onboard/enable/activate cycle`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`partner_activation_scorecard_schema`]
- `body_md`: `Produce partner activation scorepayloads.`

### Expert 15B - `channel_conflict_governor`

- `name`: `channel_conflict_governor`
- `fexp_description`: `Enforce deal registration and channel conflict handling`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`channel_conflict_incident_schema`]
- `body_md`: `Produce conflict incident logs and closure payloads.`

### Bot 16 - `scale_governance_bot`

- `accent_color`: `#1E293B`
- `title1`: `Scale Governance`
- `title2`: `Playbooks, guardrails, and controlled scaling`
- `occupation`: `Operations Governor`
- `typical_group`: `Ops / Governance`
- `intro_message`: `I codify operating playbooks and guardrail-controlled scale increments.`
- `tags`: [`Scale`, `Governance`, `Playbooks`]
- `featured_actions`: [`Generate playbook draft` -> `playbook_codifier`]
- `experts`: [`playbook_codifier`, `scale_guardrail_controller`]
- `skills`: `[]`
- `tools`: [`flexus_policy_document`]

### Expert 16A - `playbook_codifier`

- `name`: `playbook_codifier`
- `fexp_description`: `Convert proven operations into versioned playbooks`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`playbook_library_schema`]
- `body_md`: `Produce playbook library and ownership model payloads.`

### Expert 16B - `scale_guardrail_controller`

- `name`: `scale_guardrail_controller`
- `fexp_description`: `Operate scale increments with explicit guardrail criteria`
- `fexp_allow_tools`: `flexus_policy_document`
- `fexp_block_tools`: `print_widget`
- `skills`: `[]`
- `pdoc_output_schemas`: [`scale_increment_plan_schema`, `scale_rollback_decision_schema`]
- `body_md`: `Produce scale increment plan and rollback decision payloads.`

## Level 3 Skill Definitions (Schema-Aligned)

### Skill 01

- `name`: `skill_google_trends_signal_detection`
- `description`: `Google Trends signal detection method`
- `body_md`: `Use Google Trends data to detect seasonality, breakout terms, region deltas, and baseline shifts.`

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
