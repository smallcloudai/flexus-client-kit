import json
import logging
import os
from typing import Any, Dict

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("serpapi")

PROVIDER_NAME = "serpapi"
_BASE_URL = "https://serpapi.com"

_SEARCH_METHOD_ROWS = [
    ("serpapi.search.amazon_product.v1", "amazon-product-api", "amazon_product"),
    ("serpapi.search.amazon.v1", "amazon-search-api", "amazon"),
    ("serpapi.search.apple_app_store.v1", "apple-app-store", "apple_app_store"),
    ("serpapi.search.baidu_news.v1", "baidu-news-api", "baidu_news"),
    ("serpapi.search.baidu.v1", "baidu-search-api", "baidu"),
    ("serpapi.search.bing_copilot.v1", "bing-copilot-api", "bing_copilot"),
    ("serpapi.search.bing_images.v1", "bing-images-api", "bing_images"),
    ("serpapi.search.bing_maps.v1", "bing-maps-api", "bing_maps"),
    ("serpapi.search.bing_news.v1", "bing-news-api", "bing_news"),
    ("serpapi.search.bing_reverse_image.v1", "bing-reverse-image-api", "bing_reverse_image"),
    ("serpapi.search.bing.v1", "bing-search-api", "bing"),
    ("serpapi.search.bing_shopping.v1", "bing-shopping-api", "bing_shopping"),
    ("serpapi.search.bing_videos.v1", "bing-videos-api", "bing_videos"),
    ("serpapi.search.direct_answer_box.v1", "direct-answer-box-api", "direct_answer_box"),
    ("serpapi.search.duckduckgo_light.v1", "duckduckgo-light-api", "duckduckgo_light"),
    ("serpapi.search.duckduckgo_maps.v1", "duckduckgo-maps-api", "duckduckgo_maps"),
    ("serpapi.search.duckduckgo_news.v1", "duckduckgo-news-api", "duckduckgo_news"),
    ("serpapi.search.duckduckgo.v1", "duckduckgo-search-api", "duckduckgo"),
    ("serpapi.search.duckduckgo_search_assist.v1", "duckduckgo-search-assist-api", "duckduckgo_search_assist"),
    ("serpapi.search.ebay_product.v1", "ebay-product-api", "ebay_product"),
    ("serpapi.search.ebay.v1", "ebay-search-api", "ebay"),
    ("serpapi.search.facebook_profile.v1", "facebook-profile-api", "facebook_profile"),
    ("serpapi.search.google_ads_transparency_center.v1", "google-ads-transparency-center-api", "google_ads_transparency_center"),
    ("serpapi.search.google_ai_mode.v1", "google-ai-mode-api", "google_ai_mode"),
    ("serpapi.search.google_ai_overview.v1", "google-ai-overview-api", "google_ai_overview"),
    ("serpapi.search.google_autocomplete.v1", "google-autocomplete-api", "google_autocomplete"),
    ("serpapi.search.google_events.v1", "google-events-api", "google_events"),
    ("serpapi.search.google_finance.v1", "google-finance-api", "google_finance"),
    ("serpapi.search.google_flights.v1", "google-flights-api", "google_flights"),
    ("serpapi.search.google_flights_autocomplete.v1", "google-flights-autocomplete-api", "google_flights_autocomplete"),
    ("serpapi.search.google_forums.v1", "google-forums-api", "google_forums"),
    ("serpapi.search.google_hotels.v1", "google-hotels-api", "google_hotels"),
    ("serpapi.search.google_hotels_autocomplete.v1", "google-hotels-autocomplete-api", "google_hotels_autocomplete"),
    ("serpapi.search.google_hotels_photos.v1", "google-hotels-photos-api", "google_hotels_photos"),
    ("serpapi.search.google_hotels_reviews.v1", "google-hotels-reviews-api", "google_hotels_reviews"),
    ("serpapi.search.google_images.v1", "google-images-api", "google_images"),
    ("serpapi.search.google_images_light.v1", "google-images-light-api", "google_images_light"),
    ("serpapi.search.google_images_related_content.v1", "google-images-related-content-api", "google_images_related_content"),
    ("serpapi.search.google_immersive_product.v1", "google-immersive-product-api", "google_immersive_product"),
    ("serpapi.search.google_jobs.v1", "google-jobs-api", "google_jobs"),
    ("serpapi.search.google_jobs_listing.v1", "google-jobs-listing-api", "google_jobs_listing"),
    ("serpapi.search.google_lens_about_this_image.v1", "google-lens-about-this-image-api", "google_lens_about_this_image"),
    ("serpapi.search.google_lens.v1", "google-lens-api", "google_lens"),
    ("serpapi.search.google_lens_exact_matches.v1", "google-lens-exact-matches-api", "google_lens_exact_matches"),
    ("serpapi.search.google_lens_image_sources.v1", "google-lens-image-sources-api", "google_lens_image_sources"),
    ("serpapi.search.google_lens_products.v1", "google-lens-products-api", "google_lens_products"),
    ("serpapi.search.google_lens_visual_matches.v1", "google-lens-visual-matches-api", "google_lens_visual_matches"),
    ("serpapi.search.google_light.v1", "google-light-api", "google_light"),
    ("serpapi.search.google_light_fast.v1", "google-light-fast-api", "google_light"),
    ("serpapi.search.google_local.v1", "google-local-api", "google_local"),
    ("serpapi.search.google_local_services.v1", "google-local-services-api", "google_local_services"),
    ("serpapi.search.google_maps.v1", "google-maps-api", "google_maps"),
    ("serpapi.search.google_maps_autocomplete.v1", "google-maps-autocomplete-api", "google_maps_autocomplete"),
    ("serpapi.search.google_maps_contributor_reviews.v1", "google-maps-contributor-reviews-api", "google_maps_contributor_reviews"),
    ("serpapi.search.google_maps_directions.v1", "google-maps-directions-api", "google_maps_directions"),
    ("serpapi.search.google_maps_photo_meta.v1", "google-maps-photo-meta-api", "google_maps_photo_meta"),
    ("serpapi.search.google_maps_photos.v1", "google-maps-photos-api", "google_maps_photos"),
    ("serpapi.search.google_maps_posts.v1", "google-maps-posts-api", "google_maps_posts"),
    ("serpapi.search.google_maps_reviews.v1", "google-maps-reviews-api", "google_maps_reviews"),
    ("serpapi.search.google_news.v1", "google-news-api", "google_news"),
    ("serpapi.search.google_news_light.v1", "google-news-light-api", "google_news_light"),
    ("serpapi.search.google_patents.v1", "google-patents-api", "google_patents"),
    ("serpapi.search.google_patents_details.v1", "google-patents-details-api", "google_patents_details"),
    ("serpapi.search.google_play.v1", "google-play-api", "google_play"),
    ("serpapi.search.google_play_product.v1", "google-play-product-api", "google_play_product"),
    ("serpapi.search.google_related_questions.v1", "google-related-questions-api", "google_related_questions"),
    ("serpapi.search.google_reverse_image.v1", "google-reverse-image", "google_reverse_image"),
    ("serpapi.search.google_scholar.v1", "google-scholar-api", "google_scholar"),
    ("serpapi.search.google_scholar_author.v1", "google-scholar-author-api", "google_scholar_author"),
    ("serpapi.search.google_scholar_cite.v1", "google-scholar-cite-api", "google_scholar_cite"),
    ("serpapi.search.google_scholar_profiles.v1", "google-scholar-profiles-api", "google_scholar_profiles"),
    ("serpapi.search.google_shopping.v1", "google-shopping-api", "google_shopping"),
    ("serpapi.search.google_shopping_filters.v1", "google-shopping-filters-api", "google_shopping_filters"),
    ("serpapi.search.google_shopping_light.v1", "google-shopping-light-api", "google_shopping_light"),
    ("serpapi.search.google_short_videos.v1", "google-short-videos-api", "google_short_videos"),
    ("serpapi.search.google_travel_explore.v1", "google-travel-explore-api", "google_travel_explore"),
    ("serpapi.search.google_trends.v1", "google-trends-api", "google_trends"),
    ("serpapi.search.google_videos.v1", "google-videos-api", "google_videos"),
    ("serpapi.search.google_videos_light.v1", "google-videos-light-api", "google_videos_light"),
    ("serpapi.search.home_depot.v1", "home-depot-search-api", "home_depot"),
    ("serpapi.search.naver_ai_overview.v1", "naver-ai-overview-api", "naver_ai_overview"),
    ("serpapi.search.naver_images.v1", "naver-images-api", "naver_images"),
    ("serpapi.search.naver.v1", "naver-search-api", "naver"),
    ("serpapi.search.open_table_reviews.v1", "open-table-reviews-api", "open_table_reviews"),
    ("serpapi.search.google.v1", "search-api", "google"),
    ("serpapi.search.search_index.v1", "search-index-api", "search_index"),
    ("serpapi.search.tripadvisor_place.v1", "tripadvisor-place-api", "tripadvisor_place"),
    ("serpapi.search.tripadvisor.v1", "tripadvisor-search-api", "tripadvisor"),
    ("serpapi.search.walmart_product.v1", "walmart-product-api", "walmart_product"),
    ("serpapi.search.walmart_product_reviews.v1", "walmart-product-reviews-api", "walmart_product_reviews"),
    ("serpapi.search.walmart_product_sellers.v1", "walmart-product-sellers-api", "walmart_product_sellers"),
    ("serpapi.search.walmart.v1", "walmart-search-api", "walmart"),
    ("serpapi.search.yahoo_images.v1", "yahoo-images-api", "yahoo_images"),
    ("serpapi.search.yahoo.v1", "yahoo-search-api", "yahoo"),
    ("serpapi.search.yahoo_shopping.v1", "yahoo-shopping-search-api", "yahoo_shopping"),
    ("serpapi.search.yahoo_videos.v1", "yahoo-videos-api", "yahoo_videos"),
    ("serpapi.search.yandex_images.v1", "yandex-images-api", "yandex_images"),
    ("serpapi.search.yandex.v1", "yandex-search-api", "yandex"),
    ("serpapi.search.yandex_videos.v1", "yandex-videos-api", "yandex_videos"),
    ("serpapi.search.yelp_reviews.v1", "yelp-reviews-api", "yelp_reviews"),
    ("serpapi.search.yelp.v1", "yelp-search-api", "yelp"),
    ("serpapi.search.youtube.v1", "youtube-search-api", "youtube"),
    ("serpapi.search.youtube_video.v1", "youtube-video-api", "youtube_video"),
]

_SEARCH_METHODS = {
    method_id: {
        "kind": "search",
        "slug": slug,
        "engine": engine,
        "docs_url": f"{_BASE_URL}/{slug}",
    }
    for method_id, slug, engine in _SEARCH_METHOD_ROWS
}

_EXTRA_METHODS = {
    "serpapi.account.get.v1": {
        "kind": "account",
        "docs_url": f"{_BASE_URL}/account-api",
    },
    "serpapi.locations.search.v1": {
        "kind": "locations",
        "docs_url": f"{_BASE_URL}/locations-api",
    },
    "serpapi.search_archive.get.v1": {
        "kind": "search_archive",
        "docs_url": f"{_BASE_URL}/search-archive-api",
    },
    "serpapi.pixel_position.search.v1": {
        "kind": "pixel_position_search",
        "docs_url": f"{_BASE_URL}/pixel-position-api",
    },
    "serpapi.pixel_position.archive.v1": {
        "kind": "pixel_position_archive",
        "docs_url": f"{_BASE_URL}/pixel-position-api",
    },
}

METHOD_IDS = [*_SEARCH_METHODS.keys(), *_EXTRA_METHODS.keys()]
METHOD_SPECS = {**_SEARCH_METHODS, **_EXTRA_METHODS}


class IntegrationSerpapi:
    def __init__(self, rcx=None):
        self.rcx = rcx

    def _auth(self) -> Dict[str, Any]:
        if self.rcx is not None:
            return self.rcx.external_auth.get(PROVIDER_NAME) or {}
        return {}

    def _api_key(self) -> str:
        auth = self._auth()
        return str(
            auth.get("api_key", "")
            or auth.get("token", "")
            or os.environ.get("SERPAPI_API_KEY", "")
        ).strip()

    def _status(self) -> str:
        api_key = self._api_key()
        return json.dumps({
            "ok": True,
            "provider": PROVIDER_NAME,
            "status": "ready" if api_key else "missing_credentials",
            "has_api_key": bool(api_key),
            "method_count": len(METHOD_IDS),
        }, indent=2, ensure_ascii=False)

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            "call args: method_id plus the documented SerpApi query params for that method\n"
            "special methods: serpapi.account.get.v1, serpapi.locations.search.v1, serpapi.search_archive.get.v1, serpapi.pixel_position.search.v1, serpapi.pixel_position.archive.v1\n"
            f"methods={len(METHOD_IDS)}"
        )

    def _clean_params(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            k: v
            for k, v in args.items()
            if k not in {"method_id", "include_raw"}
            and v is not None
            and (not isinstance(v, str) or v.strip() != "")
        }

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({
                "ok": True,
                "provider": PROVIDER_NAME,
                "method_ids": METHOD_IDS,
                "methods": METHOD_SPECS,
            }, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_SPECS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id in _SEARCH_METHODS:
            return await self._search(method_id, args, _SEARCH_METHODS[method_id])
        if method_id == "serpapi.account.get.v1":
            return await self._account()
        if method_id == "serpapi.locations.search.v1":
            return await self._locations(args)
        if method_id == "serpapi.search_archive.get.v1":
            return await self._search_archive(args)
        if method_id == "serpapi.pixel_position.search.v1":
            return await self._pixel_position_search(args)
        if method_id == "serpapi.pixel_position.archive.v1":
            return await self._pixel_position_archive(args)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)

    async def _get(self, path: str, params: Dict[str, Any]) -> str:
        api_key = self._api_key()
        if not api_key:
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_MISSING",
                "message": "Set api_key in serpapi auth or SERPAPI_API_KEY env var.",
            }, indent=2, ensure_ascii=False)
        req_params = {**params, "api_key": api_key}
        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                r = await client.get(_BASE_URL + path, params=req_params)
            if r.status_code >= 400:
                logger.info("%s GET %s HTTP %s: %s", PROVIDER_NAME, path, r.status_code, r.text[:200])
                return json.dumps({
                    "ok": False,
                    "error_code": "PROVIDER_ERROR",
                    "status": r.status_code,
                    "detail": r.text[:300],
                }, indent=2, ensure_ascii=False)
            if path.endswith(".html") or str(req_params.get("output", "")).strip() == "html":
                return r.text
            try:
                return json.dumps(r.json(), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return r.text
        except httpx.TimeoutException:
            return json.dumps({"ok": False, "error_code": "TIMEOUT", "provider": PROVIDER_NAME}, indent=2, ensure_ascii=False)
        except httpx.HTTPError as e:
            return json.dumps({"ok": False, "error_code": "HTTP_ERROR", "detail": f"{type(e).__name__}: {e}"}, indent=2, ensure_ascii=False)

    async def _search(self, method_id: str, args: Dict[str, Any], spec: Dict[str, Any]) -> str:
        params = self._clean_params(args)
        supplied_engine = str(params.pop("engine", "")).strip()
        if supplied_engine and supplied_engine != spec["engine"]:
            return json.dumps({
                "ok": False,
                "error_code": "ENGINE_MISMATCH",
                "message": f"{method_id} is bound to engine={spec['engine']}.",
            }, indent=2, ensure_ascii=False)
        if not params:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARGS",
                "message": "Provide the documented SerpApi query params for this method.",
            }, indent=2, ensure_ascii=False)
        return await self._get("/search", {"engine": spec["engine"], **params})

    async def _account(self) -> str:
        return await self._get("/account.json", {})

    async def _locations(self, args: Dict[str, Any]) -> str:
        params = self._clean_params(args)
        return await self._get("/locations.json", params)

    async def _search_archive(self, args: Dict[str, Any]) -> str:
        params = self._clean_params(args)
        search_id = str(params.pop("search_id", params.pop("id", ""))).strip()
        if not search_id:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARG",
                "message": "search_id is required.",
            }, indent=2, ensure_ascii=False)
        output = str(params.pop("output", "json")).strip() or "json"
        if output not in {"json", "html", "json_with_pixel_position"}:
            return json.dumps({
                "ok": False,
                "error_code": "INVALID_OUTPUT",
                "message": "output must be one of: json, html, json_with_pixel_position.",
            }, indent=2, ensure_ascii=False)
        return await self._get(f"/searches/{search_id}.{output}", params)

    async def _pixel_position_search(self, args: Dict[str, Any]) -> str:
        params = self._clean_params(args)
        supplied_engine = str(params.pop("engine", "google")).strip() or "google"
        if supplied_engine != "google":
            return json.dumps({
                "ok": False,
                "error_code": "ENGINE_UNSUPPORTED",
                "message": "Pixel Position currently supports only engine=google.",
            }, indent=2, ensure_ascii=False)
        if not params:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARGS",
                "message": "Provide Google Search params such as q, gl, hl, location, or similar.",
            }, indent=2, ensure_ascii=False)
        return await self._get("/search.json_with_pixel_position", {"engine": "google", **params})

    async def _pixel_position_archive(self, args: Dict[str, Any]) -> str:
        params = self._clean_params(args)
        search_id = str(params.pop("search_id", params.pop("id", ""))).strip()
        if not search_id:
            return json.dumps({
                "ok": False,
                "error_code": "MISSING_ARG",
                "message": "search_id is required.",
            }, indent=2, ensure_ascii=False)
        return await self._get(f"/searches/{search_id}.json_with_pixel_position", params)
