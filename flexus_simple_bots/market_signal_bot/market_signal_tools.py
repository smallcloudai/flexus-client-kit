import importlib
import json
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit.integrations import fi_pdoc

# Signal tool definitions: each tool is a named dispatcher over a group of thematically related providers.
# The tool schema is identical across all signal tools -- op-based RPC dispatch pattern.
_SIGNAL_TOOL_PARAMS = {
    "type": "object",
    "properties": {
        "op": {"type": "string", "enum": ["help", "status", "list_providers", "list_methods", "call"]},
        "args": {"type": ["object", "null"]},
    },
    "required": ["op", "args"],
    "additionalProperties": False,
}

SIGNAL_SEARCH_DEMAND_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_search_demand_api",
    description='signal_search_demand_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_SOCIAL_TRENDS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_social_trends_api",
    description='signal_social_trends_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_NEWS_EVENTS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_news_events_api",
    description='signal_news_events_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_REVIEW_VOICE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_review_voice_api",
    description='signal_review_voice_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_MARKETPLACE_DEMAND_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_marketplace_demand_api",
    description='signal_marketplace_demand_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_WEB_TRAFFIC_INTEL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_web_traffic_intel_api",
    description='signal_web_traffic_intel_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_JOBS_DEMAND_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_jobs_demand_api",
    description='signal_jobs_demand_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_DEV_ECOSYSTEM_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_dev_ecosystem_api",
    description='signal_dev_ecosystem_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_PUBLIC_INTEREST_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_public_interest_api",
    description='signal_public_interest_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_PROFESSIONAL_NETWORK_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="signal_professional_network_api",
    description='signal_professional_network_api: provider dispatcher. Use op in [help,status,list_providers,list_methods,call].',
    parameters=_SIGNAL_TOOL_PARAMS,
)

SIGNAL_TOOLS = [
    SIGNAL_SEARCH_DEMAND_TOOL,
    SIGNAL_SOCIAL_TRENDS_TOOL,
    SIGNAL_NEWS_EVENTS_TOOL,
    SIGNAL_REVIEW_VOICE_TOOL,
    SIGNAL_MARKETPLACE_DEMAND_TOOL,
    SIGNAL_WEB_TRAFFIC_INTEL_TOOL,
    SIGNAL_JOBS_DEMAND_TOOL,
    SIGNAL_DEV_ECOSYSTEM_TOOL,
    SIGNAL_PUBLIC_INTEREST_TOOL,
    SIGNAL_PROFESSIONAL_NETWORK_TOOL,
]

# Explicit per-tool method whitelist: each signal tool may only call method_ids listed here.
# This enforces strict channel isolation and prevents cross-tool provider leakage.
TOOL_ALLOWED_METHOD_IDS: dict[str, list[str]] = {
    "signal_search_demand_api": [
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
    "signal_social_trends_api": [
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
    "signal_news_events_api": [
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
    "signal_review_voice_api": [
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
    "signal_marketplace_demand_api": [
        "amazon.catalog.search_items.v1",
        "amazon.catalog.get_item.v1",
        "amazon.pricing.get_item_offers_batch.v1",
        "amazon.pricing.get_listing_offers_batch.v1",
        "ebay.browse.get_items.v1",
        "ebay.browse.search.v1",
        "ebay.marketplace_insights.item_sales_search.v1",
        "google_shopping.reports.search_topic_trends.v1",
    ],
    "signal_web_traffic_intel_api": [
        "similarweb.traffic_and_engagement.get.v1",
        "similarweb.traffic_sources.get.v1",
        "similarweb.traffic_geography.get.v1",
        "similarweb.website_ranking.get.v1",
        "similarweb.similar_sites.get.v1",
        "shopify.analytics.reports_list.v1",
        "shopify.analytics.reports_dates.v1",
        "shopify.analytics.reports_get.v1",
    ],
    "signal_jobs_demand_api": [
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
    "signal_dev_ecosystem_api": [
        "github.search.repositories.v1",
        "github.search.issues.v1",
        "github.repos.get.v1",
        "stackexchange.questions.list.v1",
        "stackexchange.tags.info.v1",
        "stackexchange.tags.related.v1",
    ],
    "signal_public_interest_api": [
        "wikimedia.pageviews.per_article.v1",
        "wikimedia.pageviews.aggregate.v1",
    ],
    "signal_professional_network_api": [
        "linkedin.organization.posts.list.v1",
        "linkedin.organization.social_actions.list.v1",
        "linkedin.organization.followers.stats.v1",
    ],
}


def _tool_call_help(tool_name: str) -> str:
    try:
        return (
            f"{tool_name}(op=\"help\")\n"
            f"{tool_name}(op=\"status\")\n"
            f"{tool_name}(op=\"list_providers\")\n"
            f"{tool_name}(op=\"list_methods\", args={{\"provider\": \"<provider>\"}})\n"
            f"{tool_name}(op=\"call\", args={{\"method_id\": \"<provider>.<resource>.<action>.v1\"}})"
        )
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build help for {tool_name}: {e}") from e


def _tool_allowed_methods(tool_name: str) -> list[str]:
    try:
        return TOOL_ALLOWED_METHOD_IDS.get(tool_name, [])
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot get method list for {tool_name}: {e}") from e


def _tool_allowed_providers(tool_name: str) -> list[str]:
    try:
        providers: set[str] = set()
        for method_id in _tool_allowed_methods(tool_name):
            providers.add(method_id.split(".", 1)[0])
        return sorted(providers)
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot get provider list for {tool_name}: {e}") from e


def _sanitize_args(model_produced_args: Optional[Dict[str, Any]]) -> tuple[dict[str, Any], str]:
    try:
        if not model_produced_args:
            return {}, ""
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return {}, args_error
        if args is None:
            return {}, ""
        if not isinstance(args, dict):
            return {}, "Error: args must be an object."
        return args, ""
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        return {}, f"Error: cannot sanitize args: {type(e).__name__}: {e}"


async def handle_signal_tool_call(
    tool_name: str,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    """Entry point called by each signal tool handler in the bot main loop."""
    try:
        if tool_name not in TOOL_ALLOWED_METHOD_IDS:
            return "Error: unknown tool."

        allowed_method_ids = set(_tool_allowed_methods(tool_name))
        allowed_providers = _tool_allowed_providers(tool_name)

        if not model_produced_args:
            return _tool_call_help(tool_name)

        op = str(model_produced_args.get("op", "help")).strip()
        args, args_error = _sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if op == "help":
            return _tool_call_help(tool_name)

        if op == "status":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "status": "available",
                "providers_count": len(allowed_providers),
                "method_count": len(allowed_method_ids),
            }, indent=2, ensure_ascii=False)

        if op == "list_providers":
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "providers": allowed_providers,
            }, indent=2, ensure_ascii=False)

        if op == "list_methods":
            provider = str(args.get("provider", "")).strip()
            if not provider:
                return "Error: args.provider is required for op=list_methods."
            if provider not in allowed_providers:
                return "Error: unknown provider for this tool."
            return json.dumps({
                "ok": True,
                "tool_name": tool_name,
                "provider": provider,
                "method_ids": [x for x in _tool_allowed_methods(tool_name) if x.startswith(provider + ".")],
            }, indent=2, ensure_ascii=False)

        if op != "call":
            return "Error: unsupported op. Use help/status/list_providers/list_methods/call."

        method_id = str(args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id is required for op=call."
        if "." not in method_id:
            return "Error: invalid method_id format."
        if method_id not in allowed_method_ids:
            return "Error: method_id is not allowed for this tool."

        provider = method_id.split(".", 1)[0]
        if provider not in allowed_providers:
            return "Error: provider is not allowed for this tool."

        try:
            mod = importlib.import_module(f"flexus_client_kit.integrations.fi_{provider}")
        except ModuleNotFoundError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        class_name = "Integration" + "".join(w.capitalize() for w in provider.split("_"))
        integration_class = getattr(mod, class_name, None)
        if integration_class is None:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        try:
            integration = integration_class()
        except TypeError:
            return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": provider, "method_id": method_id, "message": "интеграции еще нет, но вы держитесь"}, indent=2, ensure_ascii=False)
        return await integration.called_by_model(toolcall, model_produced_args)
    except (AttributeError, KeyError, TypeError, ValueError) as e:
        return f"Error in {tool_name}: {type(e).__name__}: {e}"


# =============================================================================
# WRITE TOOLS — owl-style structured output, schema enforced by strict=True
# =============================================================================

WRITE_SNAPSHOT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_market_signal_snapshot",
    description="Write a completed market signal snapshot to a policy document. Call once per channel after gathering all evidence.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /signals/search-demand-2024-01-15"},
            "snapshot": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["market_signal_snapshot"]},
                    "version": {"type": "string"},
                    "channel": {"type": "string"},
                    "query": {"type": "string"},
                    "time_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "result_state": {"type": "string", "enum": ["ok", "zero_results", "insufficient_data", "technical_failure"]},
                    "evidence_count": {"type": "integer"},
                    "coverage_status": {"type": "string", "enum": ["full", "partial", "none"]},
                    "confidence": {"type": "number"},
                    "confidence_reason": {"type": "string"},
                    "signals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "signal_id": {"type": "string"},
                                "signal_summary": {"type": "string"},
                                "signal_strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                                "supporting_source_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["signal_id", "signal_summary", "signal_strength", "supporting_source_refs"],
                            "additionalProperties": False,
                        },
                    },
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_type": {"type": "string", "enum": ["api", "artifact", "tool_output", "event_stream", "expert_handoff", "user_directive"]},
                                "source_ref": {"type": "string"},
                            },
                            "required": ["source_type", "source_ref"],
                            "additionalProperties": False,
                        },
                    },
                    "limitations": {"type": "array", "items": {"type": "string"}},
                    "failure_code": {"type": ["string", "null"]},
                    "failure_message": {"type": ["string", "null"]},
                    "next_checks": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "artifact_type", "version", "channel", "query", "time_window",
                    "result_state", "evidence_count", "coverage_status",
                    "confidence", "confidence_reason", "signals", "sources",
                    "limitations", "failure_code", "failure_message", "next_checks",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["path", "snapshot"],
        "additionalProperties": False,
    },
)

WRITE_SIGNAL_REGISTER_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_signal_register",
    description="Write the aggregated signal register after deduplicating channel snapshots.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /signals/register-2024-01-15"},
            "register": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["signal_register"]},
                    "version": {"type": "string"},
                    "aggregation_window": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                        "required": ["start_date", "end_date"],
                        "additionalProperties": False,
                    },
                    "channels_considered": {"type": "array", "items": {"type": "string"}},
                    "register": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "register_id": {"type": "string"},
                                "signal_theme": {"type": "string"},
                                "combined_strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                                "confidence": {"type": "number"},
                                "supporting_snapshot_refs": {"type": "array", "items": {"type": "string"}},
                                "conflict_notes": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["register_id", "signal_theme", "combined_strength", "confidence", "supporting_snapshot_refs", "conflict_notes"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["artifact_type", "version", "aggregation_window", "channels_considered", "register"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "register"],
        "additionalProperties": False,
    },
)

WRITE_HYPOTHESIS_BACKLOG_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="write_hypothesis_backlog",
    description="Write the risk-ranked hypothesis backlog derived from the signal register.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /signals/hypotheses-2024-01-15"},
            "backlog": {
                "type": "object",
                "properties": {
                    "artifact_type": {"type": "string", "enum": ["hypothesis_backlog"]},
                    "version": {"type": "string"},
                    "prioritization_rule": {"type": "string", "enum": ["impact_x_confidence_x_reversibility"]},
                    "in_scope": {"type": "array", "items": {"type": "string"}},
                    "out_of_scope": {"type": "array", "items": {"type": "string"}},
                    "not_now": {"type": "array", "items": {"type": "string"}},
                    "hypotheses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "hypothesis_id": {"type": "string"},
                                "statement": {"type": "string"},
                                "priority_rank": {"type": "integer"},
                                "impact_score": {"type": "number"},
                                "confidence_score": {"type": "number"},
                                "reversibility_score": {"type": "number"},
                                "fail_fast_condition": {"type": "string"},
                                "next_validation_step": {"type": "string"},
                                "supporting_register_refs": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": [
                                "hypothesis_id", "statement", "priority_rank",
                                "impact_score", "confidence_score", "reversibility_score",
                                "fail_fast_condition", "next_validation_step", "supporting_register_refs",
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["artifact_type", "version", "prioritization_rule", "in_scope", "out_of_scope", "not_now", "hypotheses"],
                "additionalProperties": False,
            },
        },
        "required": ["path", "backlog"],
        "additionalProperties": False,
    },
)

WRITE_TOOLS = [
    WRITE_SNAPSHOT_TOOL,
    WRITE_SIGNAL_REGISTER_TOOL,
    WRITE_HYPOTHESIS_BACKLOG_TOOL,
]


async def handle_write_snapshot(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        snapshot = args.get("snapshot")
        if not path or snapshot is None:
            return "Error: path and snapshot are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"market_signal_snapshot": snapshot}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSignal snapshot saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing snapshot: {type(e).__name__}: {e}"


async def handle_write_signal_register(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        register = args.get("register")
        if not path or register is None:
            return "Error: path and register are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"signal_register": register}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nSignal register saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing signal register: {type(e).__name__}: {e}"


async def handle_write_hypothesis_backlog(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    pdoc_integration: fi_pdoc.IntegrationPdoc,
    rcx: ckit_bot_exec.RobotContext,
) -> str:
    try:
        path = str(args.get("path", "")).strip()
        backlog = args.get("backlog")
        if not path or backlog is None:
            return "Error: path and backlog are required."
        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
        doc = {"hypothesis_backlog": backlog}
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), fuser_id)
        return f"Written: {path}\n\nHypothesis backlog saved."
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as e:
        return f"Error writing hypothesis backlog: {type(e).__name__}: {e}"
