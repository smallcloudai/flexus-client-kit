import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable, Awaitable

from flexus_client_kit.core import ckit_cloudtool


@dataclass(frozen=True)
class SignalToolSpec:
    name: str
    integration_mode: str
    apis: list[str]
    method_ids: list[str]
    notes: list[str]
    allowed_ops: list[str]


_COMMON_OPS = ["help", "status", "list_providers", "list_methods"]
_COMMON_NOTES = ["Call contract: <tool_name>(op=\"<operation>\", args={...})"]


def _mk_spec(
    name: str,
    integration_mode: str,
    apis: list[str],
    method_ids: list[str],
    notes: Optional[list[str]] = None,
    allowed_ops: Optional[list[str]] = None,
) -> SignalToolSpec:
    try:
        merged_notes = list(_COMMON_NOTES) + list(notes or [])
        merged_ops = list(_COMMON_OPS) + list(allowed_ops or [])
        return SignalToolSpec(
            name=name,
            integration_mode=integration_mode,
            apis=apis,
            method_ids=method_ids,
            notes=merged_notes,
            allowed_ops=merged_ops,
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build signal tool spec for {name}: {e}") from e


SIGNAL_TOOL_SPECS: dict[str, SignalToolSpec] = {
    "signal_search_demand_api": _mk_spec(
        name="signal_search_demand_api",
        integration_mode="Request/Response",
        apis=[
            "Google Search Console API",
            "Google Ads API (Keyword Planning)",
            "DataForSEO Trends API",
            "SerpApi (Google Search, Google Trends, Google Shopping engines)",
            "Semrush API (Trends + Keyword reports)",
            "Bing Webmaster API",
        ],
        method_ids=[
            "google_search_console.searchanalytics.query.v1",
            "google_ads.keyword_planner.generate_keyword_ideas.v1",
            "google_ads.keyword_planner.generate_historical_metrics.v1",
            "google_ads.keyword_planner.generate_forecast_metrics.v1",
            "dataforseo.trends.explore.live.v1",
            "dataforseo.trends.subregion_interests.live.v1",
            "dataforseo.trends.demography.live.v1",
            "dataforseo.trends.merged_data.live.v1",
            "serpapi.search.google.v1",
            "serpapi.search.google_trends.v1",
            "serpapi.search.google_shopping.v1",
            "semrush.trends.traffic_summary.v1",
            "semrush.trends.daily_traffic.v1",
            "semrush.analytics.keyword_reports.v1",
            "bing_webmaster.get_page_stats.v1",
            "bing_webmaster.get_page_query_stats.v1",
            "bing_webmaster.get_rank_and_traffic_stats.v1",
        ],
        notes=["Default op fallback is help"],
        allowed_ops=[
            "query_interest_timeseries",
            "query_related_queries",
            "query_keyword_volume",
            "query_serp_snapshot",
            "query_competitor_traffic",
        ],
    ),
    "signal_social_trends_api": _mk_spec(
        name="signal_social_trends_api",
        integration_mode="Request/Response",
        apis=[
            "Reddit API",
            "X API v2",
            "YouTube Data API v3",
            "TikTok Research API",
            "Instagram Graph API",
            "Pinterest API",
            "Product Hunt GraphQL API",
        ],
        method_ids=[
            "reddit.subreddit.new.v1",
            "reddit.subreddit.hot.v1",
            "reddit.search.posts.v1",
            "reddit.comments.list.v1",
            "x.tweets.counts_recent.v1",
            "x.tweets.search_recent.v1",
            "youtube.search.list.v1",
            "youtube.videos.list.v1",
            "youtube.comment_threads.list.v1",
            "tiktok.research.video_query.v1",
            "instagram.hashtag.search.v1",
            "instagram.hashtag.recent_media.v1",
            "instagram.hashtag.top_media.v1",
            "pinterest.trends.keywords_top.v1",
            "producthunt.graphql.posts.v1",
            "producthunt.graphql.topics.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_news_events_api": _mk_spec(
        name="signal_news_events_api",
        integration_mode="Request/Response",
        apis=[
            "GDELT API",
            "Event Registry API",
            "NewsAPI",
            "GNews API",
            "NewsData.io API",
            "MediaStack API",
            "NewsCatcher API",
            "Perigon API",
        ],
        method_ids=[
            "gdelt.doc.search.v1",
            "gdelt.events.search.v1",
            "event_registry.article.get_articles.v1",
            "event_registry.event.get_events.v1",
            "newsapi.everything.v1",
            "newsapi.top_headlines.v1",
            "gnews.search.v1",
            "gnews.top_headlines.v1",
            "newsdata.news.search.v1",
            "mediastack.news.search.v1",
            "newscatcher.search.v1",
            "newscatcher.latest_headlines.v1",
            "perigon.all.search.v1",
            "perigon.topics.search.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_review_voice_api": _mk_spec(
        name="signal_review_voice_api",
        integration_mode="Request/Response",
        apis=[
            "Trustpilot API",
            "Yelp Fusion API",
            "G2 data provider API",
            "Capterra data provider API",
        ],
        method_ids=[
            "trustpilot.business_units.find.v1",
            "trustpilot.business_units.get_public.v1",
            "trustpilot.reviews.list.v1",
            "yelp.businesses.search.v1",
            "yelp.businesses.get.v1",
            "yelp.businesses.reviews.v1",
            "g2.vendors.list.v1",
            "g2.reviews.list.v1",
            "g2.categories.benchmark.v1",
            "capterra.products.list.v1",
            "capterra.reviews.list.v1",
            "capterra.categories.list.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_marketplace_demand_api": _mk_spec(
        name="signal_marketplace_demand_api",
        integration_mode="Request/Response",
        apis=[
            "Amazon SP-API",
            "eBay Browse API",
            "eBay Marketplace Insights API",
            "Google Shopping Content API",
        ],
        method_ids=[
            "amazon.catalog.search_items.v1",
            "amazon.catalog.get_item.v1",
            "amazon.pricing.get_item_offers_batch.v1",
            "amazon.pricing.get_listing_offers_batch.v1",
            "ebay.browse.get_items.v1",
            "ebay.browse.search.v1",
            "ebay.marketplace_insights.item_sales_search.v1",
            "google_shopping.reports.search_topic_trends.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_web_traffic_intel_api": _mk_spec(
        name="signal_web_traffic_intel_api",
        integration_mode="Request/Response",
        apis=["Similarweb API", "Shopify Admin analytics surface"],
        method_ids=[
            "similarweb.traffic_and_engagement.get.v1",
            "similarweb.traffic_sources.get.v1",
            "similarweb.traffic_geography.get.v1",
            "similarweb.website_ranking.get.v1",
            "similarweb.similar_sites.get.v1",
            "shopify.analytics.reports_list.v1",
            "shopify.analytics.reports_dates.v1",
            "shopify.analytics.reports_get.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_jobs_demand_api": _mk_spec(
        name="signal_jobs_demand_api",
        integration_mode="Request/Response",
        apis=[
            "Adzuna API",
            "Bright Data Jobs API",
            "Coresignal API",
            "TheirStack API",
            "Oxylabs jobs data API",
            "HasData jobs APIs",
            "Levels.fyi API",
            "LinkedIn Jobs data provider API (restricted/compliance-sensitive)",
            "Glassdoor data provider API (restricted/compliance-sensitive)",
        ],
        method_ids=[
            "adzuna.jobs.search_ads.v1",
            "adzuna.jobs.regional_data.v1",
            "brightdata.jobs.data_feed.v1",
            "brightdata.jobs.dataset_query.v1",
            "coresignal.jobs.posts.v1",
            "coresignal.companies.profile.v1",
            "theirstack.jobs.search.v1",
            "theirstack.companies.hiring.v1",
            "oxylabs.jobs.source_query.v1",
            "hasdata.indeed.jobs.v1",
            "hasdata.glassdoor.jobs.v1",
            "levelsfyi.compensation.benchmark.v1",
            "linkedin_jobs.provider.search.v1",
            "glassdoor.provider.search.v1",
        ],
        notes=[
            "restricted: linkedin_jobs.provider.search.v1",
            "restricted: glassdoor.provider.search.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_dev_ecosystem_api": _mk_spec(
        name="signal_dev_ecosystem_api",
        integration_mode="Request/Response",
        apis=["GitHub REST API", "Stack Exchange API"],
        method_ids=[
            "github.search.repositories.v1",
            "github.search.issues.v1",
            "github.repos.get.v1",
            "stackexchange.questions.list.v1",
            "stackexchange.tags.info.v1",
            "stackexchange.tags.related.v1",
        ],
        allowed_ops=["query_signals"],
    ),
    "signal_public_interest_api": _mk_spec(
        name="signal_public_interest_api",
        integration_mode="Request/Response",
        apis=["Wikimedia Pageviews API"],
        method_ids=["wikimedia.pageviews.per_article.v1", "wikimedia.pageviews.aggregate.v1"],
        allowed_ops=["query_signals"],
    ),
    "signal_professional_network_api": _mk_spec(
        name="signal_professional_network_api",
        integration_mode="Request/Response (restricted)",
        apis=["LinkedIn Marketing API"],
        method_ids=[
            "linkedin.organization.posts.list.v1",
            "linkedin.organization.social_actions.list.v1",
            "linkedin.organization.followers.stats.v1",
        ],
        notes=[
            "Use only where provider terms allow this exact use case.",
            "Treat as restricted integration by default.",
        ],
        allowed_ops=["query_signals"],
    ),
}


def _mk_tool(spec: SignalToolSpec) -> ckit_cloudtool.CloudTool:
    try:
        return ckit_cloudtool.CloudTool(
            strict=False,
            name=spec.name,
            description=f"{spec.name}: market signal retrieval router. Start with op=\"help\".",
            parameters={
                "type": "object",
                "properties": {
                    "op": {"type": "string"},
                    "args": {"type": "object"},
                },
            },
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot create CloudTool for {spec.name}: {e}") from e


SIGNAL_CLOUD_TOOLS: dict[str, ckit_cloudtool.CloudTool] = {
    name: _mk_tool(spec)
    for name, spec in SIGNAL_TOOL_SPECS.items()
}


def _provider_from_method_id(method_id: str) -> str:
    try:
        return method_id.split(".", 1)[0]
    except (AttributeError, TypeError) as e:
        raise RuntimeError(f"Cannot parse method id provider from {method_id!r}: {e}") from e


def _providers(spec: SignalToolSpec) -> list[str]:
    try:
        out = sorted({_provider_from_method_id(x) for x in spec.method_ids})
        return out
    except RuntimeError:
        raise


def _help_text(spec: SignalToolSpec) -> str:
    try:
        return (
            f"{spec.name}(op=\"help\")\n"
            f"{spec.name}(op=\"status\")\n"
            f"{spec.name}(op=\"list_providers\")\n"
            f"{spec.name}(op=\"list_methods\", args={{\"provider\": \"<provider>\"}})\n"
            f"{spec.name}(op=\"<query_op>\", args={{...}})\n\n"
            f"Allowed ops: {', '.join(spec.allowed_ops)}\n"
            f"Integration mode: {spec.integration_mode}\n"
            f"Providers: {', '.join(_providers(spec))}\n"
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build help text for {spec.name}: {e}") from e


def _unknown_op_error(spec: SignalToolSpec, op: str) -> str:
    try:
        return f"Error: unknown op '{op}'. Allowed: {', '.join(spec.allowed_ops)}\n\n{_help_text(spec)}"
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot render unknown-op error for {spec.name}: {e}") from e


def _validate_provider(spec: SignalToolSpec, provider: Optional[str]) -> Optional[str]:
    try:
        if provider is None:
            return None
        if provider not in _providers(spec):
            return f"Error: unknown provider '{provider}'. Allowed providers: {', '.join(_providers(spec))}"
        return None
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot validate provider for {spec.name}: {e}") from e


def _validate_method_id(spec: SignalToolSpec, method_id: Optional[str]) -> Optional[str]:
    try:
        if method_id is None:
            return None
        if method_id not in spec.method_ids:
            return f"Error: unknown method_id '{method_id}'. Use op='list_methods' first."
        return None
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot validate method_id for {spec.name}: {e}") from e


def _query_not_implemented_payload(spec: SignalToolSpec, op: str, args: dict[str, Any]) -> str:
    try:
        payload = {
            "ok": False,
            "error_code": "NOT_IMPLEMENTED",
            "message": "Provider-backed execution is not wired in this runtime yet.",
            "tool_name": spec.name,
            "op": op,
            "args": args,
            "allowed_providers": _providers(spec),
            "allowed_method_ids": spec.method_ids,
            "notes": spec.notes,
        }
        return (
            "Execution contract accepted, but provider call path is not implemented yet.\n"
            "Use status/list_providers/list_methods for discovery.\n\n"
            + json.dumps(payload, indent=2)
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot render not-implemented payload for {spec.name}: {e}") from e


def make_signal_handler(tool_name: str) -> Callable[[ckit_cloudtool.FCloudtoolCall, Dict[str, Any]], Awaitable[str]]:
    try:
        spec = SIGNAL_TOOL_SPECS[tool_name]
    except KeyError as e:
        raise RuntimeError(f"Unknown signal tool name: {tool_name}") from e

    async def _handler(
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        _ = toolcall
        try:
            if not model_produced_args:
                return _help_text(spec)

            op = model_produced_args.get("op", "help")
            args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
            if args_error:
                return args_error

            if op not in spec.allowed_ops:
                return _unknown_op_error(spec, str(op))

            if op == "help":
                return _help_text(spec)

            if op == "status":
                return json.dumps({
                    "ok": True,
                    "tool_name": spec.name,
                    "status": "registered",
                    "provider_execution": "not_implemented",
                    "integration_mode": spec.integration_mode,
                }, indent=2)

            if op == "list_providers":
                return json.dumps({
                    "ok": True,
                    "tool_name": spec.name,
                    "providers": _providers(spec),
                    "apis": spec.apis,
                }, indent=2)

            if op == "list_methods":
                provider = args.get("provider")
                provider_error = _validate_provider(spec, provider)
                if provider_error:
                    return provider_error
                if provider:
                    methods = [m for m in spec.method_ids if m.startswith(f"{provider}.")]
                else:
                    methods = list(spec.method_ids)
                return json.dumps({
                    "ok": True,
                    "tool_name": spec.name,
                    "provider": provider,
                    "method_ids": methods,
                }, indent=2)

            provider = args.get("provider")
            method_id = args.get("method_id")

            provider_error = _validate_provider(spec, provider)
            if provider_error:
                return provider_error

            method_error = _validate_method_id(spec, method_id)
            if method_error:
                return method_error

            return _query_not_implemented_payload(spec, str(op), args)
        except (TypeError, ValueError, KeyError) as e:
            return f"Error in {spec.name}: {type(e).__name__}: {e}"

    return _handler
