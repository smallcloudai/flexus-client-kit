import asyncio
import logging
from typing import Dict, Any, Optional

import google.oauth2.credentials
import grpc
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_integrations_db

logger = logging.getLogger("goads")

GOOGLE_ADS_SCOPES = ckit_integrations_db.GOOGLE_OAUTH_BASE_SCOPES + [
    "https://www.googleapis.com/auth/adwords",
]

GOOGLE_ADS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="google_ads",
    description='Manage Google Ads campaigns, keywords, budgets and reporting. Call with op="help" for usage.',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage", "order": 0},
            "args": {"type": "object", "order": 1},
        },
        "required": [],
    },
)

HELP = """
Help:

google_ads(op="status")
    Connection status: auth, developer token, customer ID.

# Campaign Management
google_ads(op="listCampaigns", args={"status": "ENABLED"})  # Optional filter: ENABLED, PAUSED, REMOVED
google_ads(op="getCampaign", args={"campaignId": "123456"})
google_ads(op="pauseCampaign", args={"campaignId": "123456"})
google_ads(op="enableCampaign", args={"campaignId": "123456"})

# Ad Groups & Keywords
google_ads(op="listAdGroups", args={"campaignId": "123456"})
google_ads(op="listKeywords", args={"adGroupId": "789"})
google_ads(op="addKeyword", args={
    "adGroupId": "789",
    "text": "buy shoes online",
    "matchType": "PHRASE"  # EXACT, PHRASE, BROAD
})
google_ads(op="pauseKeyword", args={"adGroupId": "789", "criterionId": "456"})
google_ads(op="updateKeywordBid", args={
    "adGroupId": "789",
    "criterionId": "456",
    "bidMicros": 1500000  # $1.50
})

# Budget
google_ads(op="listBudgets")
google_ads(op="updateBudget", args={
    "budgetId": "111",
    "amountMicros": 50000000  # $50.00 daily
})

# Performance & Reporting
google_ads(op="getPerformance", args={
    "entity": "campaign",       # campaign, ad_group, keyword
    "dateRange": "LAST_30_DAYS", # LAST_7_DAYS, LAST_30_DAYS, THIS_MONTH, etc.
    "metrics": ["impressions", "clicks", "cost_micros", "conversions"],
    "filters": {"campaign.status": "ENABLED"},  # Optional
    "orderBy": "metrics.cost_micros DESC",       # Optional
    "limit": 20                                  # Optional, default 50
})

google_ads(op="gaqlQuery", args={
    "query": "SELECT campaign.name, metrics.clicks FROM campaign WHERE segments.date DURING LAST_7_DAYS"
})

Notes:
- All monetary values are in micros (1,000,000 micros = 1 currency unit, e.g. 1500000 = $1.50)
- Status values: ENABLED, PAUSED, REMOVED
- Match types: EXACT, PHRASE, BROAD
- gaqlQuery runs arbitrary GAQL (Google Ads Query Language) for custom reports
"""


def _format_micros(micros) -> str:
    try:
        return f"${int(micros) / 1_000_000:.2f}"
    except (ValueError, TypeError):
        return str(micros)


class IntegrationGoogleAds:

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,
        developer_token: str = "",
        customer_id: str = "",
        login_customer_id: str = "",
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.developer_token = developer_token.strip()
        self.customer_id = customer_id.strip().replace("-", "")
        self.login_customer_id = login_customer_id.strip().replace("-", "")
        self._client = None
        self._last_access_token = None

    def _access_token(self) -> str:
        auth = self.rcx.external_auth.get("google_ads") or {}
        return (auth.get("token") or {}).get("access_token", "")

    def _ensure_client(self) -> bool:
        access_token = self._access_token()
        if not access_token or not self.developer_token or not self.customer_id:
            self._client = None
            self._last_access_token = None
            return False
        if access_token == self._last_access_token and self._client:
            return True
        creds = google.oauth2.credentials.Credentials(token=access_token)
        self._client = GoogleAdsClient(
            credentials=creds,
            developer_token=self.developer_token,
            login_customer_id=self.login_customer_id or None,
            use_proto_plus=True,
        )
        self._last_access_token = access_token
        logger.info("Google Ads client initialized for customer %s, login_customer_id=%s", self.customer_id, self.login_customer_id or "(none)")
        return True

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        if print_status:
            access_token = self._access_token()
            r = "Google Ads integration status:\n"
            r += f"  OAuth: {'✅ Connected' if access_token else '❌ Not connected'}\n"
            r += f"  Developer token: {'✅ Set' if self.developer_token else '❌ Not set'}\n"
            r += f"  Customer ID: {self.customer_id or '❌ Not set'}\n"
            if self.login_customer_id:
                r += f"  Login customer ID (MCC): {self.login_customer_id}\n"
            r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
            r += f"  Workspace: {self.rcx.persona.ws_id}\n"
            if not access_token:
                r += "\n⚠️  Please connect Google Ads in bot Integrations tab.\n"
            if not self.developer_token:
                r += "\n⚠️  Developer token not configured. Reconnect Google Ads in Integrations tab.\n"
            if not self.customer_id:
                r += "\n⚠️  Customer ID not configured. Reconnect Google Ads in Integrations tab.\n"
            return r

        if print_help:
            return HELP

        authenticated = self._ensure_client()
        if not authenticated:
            missing = []
            if not self._access_token():
                missing.append("OAuth (connect Google Ads in Integrations tab)")
            if not self.developer_token:
                missing.append("developer token (reconnect Google Ads in Integrations tab)")
            if not self.customer_id:
                missing.append("customer ID (reconnect Google Ads in Integrations tab)")
            return f"❌ Google Ads not ready. Missing: {', '.join(missing)}"

        try:
            if op == "listCampaigns":
                return await self._list_campaigns(args)
            elif op == "getCampaign":
                return await self._get_campaign(args)
            elif op == "pauseCampaign":
                return await self._set_campaign_status(args, toolcall, "PAUSED")
            elif op == "enableCampaign":
                return await self._set_campaign_status(args, toolcall, "ENABLED")
            elif op == "listAdGroups":
                return await self._list_ad_groups(args)
            elif op == "listKeywords":
                return await self._list_keywords(args)
            elif op == "addKeyword":
                return await self._add_keyword(args)
            elif op == "pauseKeyword":
                return await self._pause_keyword(args, toolcall)
            elif op == "updateKeywordBid":
                return await self._update_keyword_bid(args, toolcall)
            elif op == "listBudgets":
                return await self._list_budgets(args)
            elif op == "updateBudget":
                return await self._update_budget(args, toolcall)
            elif op == "getPerformance":
                return await self._get_performance(args)
            elif op == "gaqlQuery":
                return await self._gaql_query(args)
            else:
                return f"❌ Unknown operation: {op}\n\nTry google_ads(op='help') for usage."

        except GoogleAdsException as ex:
            if ex.error.code() in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
                self._client = None
                self._last_access_token = None
                return f"❌ Authentication error (request_id={ex.request_id})\n\nPlease reconnect Google Ads in bot Integrations tab."
            logger.error("Google Ads API error request_id=%s: %r", ex.request_id, ex.failure)
            return f"❌ Google Ads API error (request_id={ex.request_id}): {ex.failure}"
    
    async def _run_gaql(self, query: str) -> list:
        def _search():
            service = self._client.get_service("GoogleAdsService")
            return list(service.search(customer_id=self.customer_id, query=query))
        return await asyncio.to_thread(_search)

    async def _gaql_query(self, args: Dict[str, Any]) -> str:
        query = args.get("query", "")
        if not query:
            return "❌ Missing required parameter: 'query' (GAQL string)"
        rows = await self._run_gaql(query)
        if not rows:
            return "📭 No results returned."
        lines = [f"📊 {len(rows)} row(s) returned:\n"]
        for i, row in enumerate(rows[:100], 1):
            lines.append(f"{i}. {_row_to_str(row)}")
        if len(rows) > 100:
            lines.append(f"\n... and {len(rows) - 100} more rows (truncated)")
        return "\n".join(lines)
    
    async def _list_campaigns(self, args: Dict[str, Any]) -> str:
        status_filter = args.get("status", "")
        query = (
            "SELECT campaign.id, campaign.name, campaign.status, "
            "campaign.advertising_channel_type, campaign_budget.amount_micros "
            "FROM campaign"
        )
        if status_filter:
            query += f" WHERE campaign.status = '{status_filter}'"
        query += " ORDER BY campaign.name"
        rows = await self._run_gaql(query)
        if not rows:
            return "📭 No campaigns found."
        lines = [f"📋 {len(rows)} campaign(s):\n"]
        for i, row in enumerate(rows, 1):
            c = row.campaign
            budget = _format_micros(row.campaign_budget.amount_micros) if row.campaign_budget.amount_micros else "N/A"
            lines.append(f"{i}. [{c.status.name}] {c.name}")
            lines.append(f"   ID: {c.id}  Type: {c.advertising_channel_type.name}  Budget: {budget}/day")
        return "\n".join(lines)
    
    async def _get_campaign(self, args: Dict[str, Any]) -> str:
        campaign_id = args.get("campaignId", "")
        if not campaign_id:
            return "❌ Missing required parameter: 'campaignId'"
        query = (
            "SELECT campaign.id, campaign.name, campaign.status, "
            "campaign.advertising_channel_type, campaign.bidding_strategy_type, "
            "campaign_budget.amount_micros "
            f"FROM campaign WHERE campaign.id = {campaign_id}"
        )
        rows = await self._run_gaql(query)
        if not rows:
            return f"📭 Campaign {campaign_id} not found."
        c = rows[0].campaign
        b = rows[0].campaign_budget
        lines = [
            "📋 Campaign Details:\n",
            f"ID: {c.id}",
            f"Name: {c.name}",
            f"Status: {c.status.name}",
            f"Channel: {c.advertising_channel_type.name}",
            f"Bidding: {c.bidding_strategy_type.name}",
            f"Budget: {_format_micros(b.amount_micros)}/day",
        ]
        return "\n".join(lines)
    
    async def _set_campaign_status(self, args: Dict[str, Any], toolcall: ckit_cloudtool.FCloudtoolCall, target_status: str) -> str:
        campaign_id = args.get("campaignId", "")
        if not campaign_id:
            return "❌ Missing required parameter: 'campaignId'"
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="google_ads_campaign",
                confirm_command=f"google_ads {target_status.lower()} campaign {campaign_id}",
                confirm_explanation=f"This will set campaign {campaign_id} to {target_status}",
            )

        def _mutate():
            service = self._client.get_service("CampaignService")
            operation = self._client.get_type("CampaignOperation")
            campaign = operation.update
            campaign.resource_name = service.campaign_path(self.customer_id, campaign_id)
            campaign.status = self._client.enums.CampaignStatusEnum[target_status].value
            field_mask = self._client.get_type("FieldMask")
            field_mask.paths.append("status")
            operation.update_mask.CopyFrom(field_mask)
            return service.mutate_campaigns(customer_id=self.customer_id, operations=[operation])

        await asyncio.to_thread(_mutate)
        return f"✅ Campaign {campaign_id} set to {target_status}"
    
    async def _list_ad_groups(self, args: Dict[str, Any]) -> str:
        campaign_id = args.get("campaignId", "")
        if not campaign_id:
            return "❌ Missing required parameter: 'campaignId'"
        query = (
            "SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type "
            f"FROM ad_group WHERE campaign.id = {campaign_id} "
            "ORDER BY ad_group.name"
        )
        rows = await self._run_gaql(query)
        if not rows:
            return f"📭 No ad groups found for campaign {campaign_id}."
        lines = [f"📋 {len(rows)} ad group(s):\n"]
        for i, row in enumerate(rows, 1):
            ag = row.ad_group
            lines.append(f"{i}. [{ag.status.name}] {ag.name}  (ID: {ag.id}, Type: {ag.type_.name})")
        return "\n".join(lines)
    
    async def _list_keywords(self, args: Dict[str, Any]) -> str:
        ad_group_id = args.get("adGroupId", "")
        if not ad_group_id:
            return "❌ Missing required parameter: 'adGroupId'"
        query = (
            "SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
            "ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
            "ad_group_criterion.effective_cpc_bid_micros "
            f"FROM ad_group_criterion WHERE ad_group.id = {ad_group_id} "
            "AND ad_group_criterion.type = 'KEYWORD' "
            "ORDER BY ad_group_criterion.keyword.text"
        )
        rows = await self._run_gaql(query)
        if not rows:
            return f"📭 No keywords found for ad group {ad_group_id}."
        lines = [f"🔑 {len(rows)} keyword(s):\n"]
        for i, row in enumerate(rows, 1):
            kw = row.ad_group_criterion
            bid = _format_micros(kw.effective_cpc_bid_micros) if kw.effective_cpc_bid_micros else "auto"
            lines.append(f"{i}. [{kw.status.name}] {kw.keyword.text} ({kw.keyword.match_type.name}) "
                         f"Bid: {bid}  CriterionID: {kw.criterion_id}")
        return "\n".join(lines)
    
    async def _add_keyword(self, args: Dict[str, Any]) -> str:
        ad_group_id = args.get("adGroupId", "")
        text = args.get("text", "")
        match_type = args.get("matchType", "BROAD").upper()
        if not ad_group_id or not text:
            return "❌ Missing required parameters: 'adGroupId' and 'text'"
        if match_type not in ("EXACT", "PHRASE", "BROAD"):
            return f"❌ Invalid matchType: {match_type}. Use EXACT, PHRASE, or BROAD."

        def _mutate():
            service = self._client.get_service("AdGroupCriterionService")
            operation = self._client.get_type("AdGroupCriterionOperation")
            criterion = operation.create
            criterion.ad_group = self._client.get_service("AdGroupService").ad_group_path(self.customer_id, ad_group_id)
            criterion.keyword.text = text
            criterion.keyword.match_type = self._client.enums.KeywordMatchTypeEnum[match_type].value
            criterion.status = self._client.enums.AdGroupCriterionStatusEnum.ENABLED.value
            return service.mutate_ad_group_criteria(customer_id=self.customer_id, operations=[operation])

        await asyncio.to_thread(_mutate)
        return f"✅ Keyword '{text}' ({match_type}) added to ad group {ad_group_id}"
    
    async def _pause_keyword(self, args: Dict[str, Any], toolcall: ckit_cloudtool.FCloudtoolCall) -> str:
        ad_group_id = args.get("adGroupId", "")
        criterion_id = args.get("criterionId", "")
        if not ad_group_id or not criterion_id:
            return "❌ Missing required parameters: 'adGroupId' and 'criterionId'"
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="google_ads_keyword",
                confirm_command=f"google_ads pause keyword {criterion_id} in ad group {ad_group_id}",
                confirm_explanation="This will pause the keyword",
            )

        def _mutate():
            service = self._client.get_service("AdGroupCriterionService")
            operation = self._client.get_type("AdGroupCriterionOperation")
            criterion = operation.update
            criterion.resource_name = service.ad_group_criterion_path(self.customer_id, ad_group_id, criterion_id)
            criterion.status = self._client.enums.AdGroupCriterionStatusEnum.PAUSED.value
            field_mask = self._client.get_type("FieldMask")
            field_mask.paths.append("status")
            operation.update_mask.CopyFrom(field_mask)
            return service.mutate_ad_group_criteria(customer_id=self.customer_id, operations=[operation])

        await asyncio.to_thread(_mutate)
        return f"✅ Keyword {criterion_id} paused in ad group {ad_group_id}"
    
    async def _update_keyword_bid(self, args: Dict[str, Any], toolcall: ckit_cloudtool.FCloudtoolCall) -> str:
        ad_group_id = args.get("adGroupId", "")
        criterion_id = args.get("criterionId", "")
        bid_micros = args.get("bidMicros", 0)
        if not ad_group_id or not criterion_id or not bid_micros:
            return "❌ Missing required parameters: 'adGroupId', 'criterionId', 'bidMicros'"
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="google_ads_keyword",
                confirm_command=f"google_ads set keyword {criterion_id} bid to {_format_micros(bid_micros)}",
                confirm_explanation=f"This will change the CPC bid to {_format_micros(bid_micros)}",
            )

        def _mutate():
            service = self._client.get_service("AdGroupCriterionService")
            operation = self._client.get_type("AdGroupCriterionOperation")
            criterion = operation.update
            criterion.resource_name = service.ad_group_criterion_path(self.customer_id, ad_group_id, criterion_id)
            criterion.cpc_bid_micros = int(bid_micros)
            field_mask = self._client.get_type("FieldMask")
            field_mask.paths.append("cpc_bid_micros")
            operation.update_mask.CopyFrom(field_mask)
            return service.mutate_ad_group_criteria(customer_id=self.customer_id, operations=[operation])

        await asyncio.to_thread(_mutate)
        return f"✅ Keyword {criterion_id} bid updated to {_format_micros(bid_micros)}"
    
    async def _list_budgets(self, args: Dict[str, Any]) -> str:
        query = (
            "SELECT campaign_budget.id, campaign_budget.name, "
            "campaign_budget.amount_micros, campaign_budget.delivery_method, "
            "campaign_budget.status "
            "FROM campaign_budget ORDER BY campaign_budget.name"
        )
        rows = await self._run_gaql(query)
        if not rows:
            return "📭 No budgets found."
        lines = [f"💰 {len(rows)} budget(s):\n"]
        for i, row in enumerate(rows, 1):
            b = row.campaign_budget
            lines.append(f"{i}. {b.name or '(unnamed)'}  ID: {b.id}  "
                         f"Amount: {_format_micros(b.amount_micros)}/day  Status: {b.status.name}")
        return "\n".join(lines)
    
    async def _update_budget(self, args: Dict[str, Any], toolcall: ckit_cloudtool.FCloudtoolCall) -> str:
        budget_id = args.get("budgetId", "")
        amount_micros = args.get("amountMicros", 0)
        if not budget_id or not amount_micros:
            return "❌ Missing required parameters: 'budgetId' and 'amountMicros'"
        if not toolcall.confirmed_by_human:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="google_ads_budget",
                confirm_command=f"google_ads set budget {budget_id} to {_format_micros(amount_micros)}/day",
                confirm_explanation=f"This will change the daily budget to {_format_micros(amount_micros)}",
            )

        def _mutate():
            service = self._client.get_service("CampaignBudgetService")
            operation = self._client.get_type("CampaignBudgetOperation")
            budget = operation.update
            budget.resource_name = service.campaign_budget_path(self.customer_id, budget_id)
            budget.amount_micros = int(amount_micros)
            field_mask = self._client.get_type("FieldMask")
            field_mask.paths.append("amount_micros")
            operation.update_mask.CopyFrom(field_mask)
            return service.mutate_campaign_budgets(customer_id=self.customer_id, operations=[operation])

        await asyncio.to_thread(_mutate)
        return f"✅ Budget {budget_id} updated to {_format_micros(amount_micros)}/day"
    
    async def _get_performance(self, args: Dict[str, Any]) -> str:
        entity = args.get("entity", "campaign")
        date_range = args.get("dateRange", "LAST_30_DAYS")
        metrics = args.get("metrics", ["impressions", "clicks", "cost_micros", "conversions"])
        filters = args.get("filters", {})
        order_by = args.get("orderBy", "")
        limit = args.get("limit", 50)

        entity_map = {
            "campaign": ("campaign", "campaign.id, campaign.name, campaign.status"),
            "ad_group": ("ad_group", "ad_group.id, ad_group.name, ad_group.status, campaign.name"),
            "keyword": ("ad_group_criterion", "ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group.name"),
        }
        if entity not in entity_map:
            return f"❌ Invalid entity: {entity}. Use: campaign, ad_group, keyword"

        resource, fields = entity_map[entity]
        metrics_fields = ", ".join(f"metrics.{m}" for m in metrics)
        query = f"SELECT {fields}, {metrics_fields} FROM {resource}"

        where_parts = [f"segments.date DURING {date_range}"]
        for k, v in filters.items():
            where_parts.append(f"{k} = '{v}'")
        query += " WHERE " + " AND ".join(where_parts)

        if order_by:
            query += f" ORDER BY {order_by}"
        query += f" LIMIT {limit}"

        rows = await self._run_gaql(query)
        if not rows:
            return f"📭 No performance data for {entity} during {date_range}."

        lines = [f"📊 {entity.replace('_', ' ').title()} Performance ({date_range}): {len(rows)} row(s)\n"]
        for i, row in enumerate(rows, 1):
            row_str = _row_to_str(row)
            lines.append(f"{i}. {row_str}")
        return "\n".join(lines)


def _row_to_str(row) -> str:
    parts = []
    if hasattr(row, 'campaign') and row.campaign.name:
        parts.append(f"Campaign: {row.campaign.name}")
        if row.campaign.status:
            parts.append(f"[{row.campaign.status.name}]")
    if hasattr(row, 'ad_group') and row.ad_group.name:
        parts.append(f"AdGroup: {row.ad_group.name}")
    if hasattr(row, 'ad_group_criterion') and row.ad_group_criterion.keyword.text:
        kw = row.ad_group_criterion
        parts.append(f"Keyword: {kw.keyword.text} ({kw.keyword.match_type.name})")
    if hasattr(row, 'campaign_budget') and row.campaign_budget.amount_micros:
        parts.append(f"Budget: {_format_micros(row.campaign_budget.amount_micros)}/day")
    if hasattr(row, 'metrics'):
        m = row.metrics
        metric_parts = []
        if m.impressions:
            metric_parts.append(f"Impr: {m.impressions:,}")
        if m.clicks:
            metric_parts.append(f"Clicks: {m.clicks:,}")
        if m.cost_micros:
            metric_parts.append(f"Cost: {_format_micros(m.cost_micros)}")
        if m.conversions:
            metric_parts.append(f"Conv: {m.conversions:.1f}")
        if m.ctr:
            metric_parts.append(f"CTR: {m.ctr:.2%}")
        if metric_parts:
            parts.append(" | ".join(metric_parts))
    return "  ".join(parts) if parts else repr(row)
