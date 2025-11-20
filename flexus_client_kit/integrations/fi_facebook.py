import asyncio
import hashlib
import logging
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_bot_exec


logger = logging.getLogger("facebook")


# Default/Fallback ID if not provided in setup
AD_ACCOUNT_ID = "act_123456789" 

CLIENT_ID = os.getenv("FACEBOOK_APP_ID", "")
CLIENT_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
REDIRECT_URI = "http://localhost:3000/"

API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"


FACEBOOK_TOOL = ckit_cloudtool.CloudTool(
    name="facebook",
    description="Interact with Facebook/Instagram Marketing API. Call with op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Operation name (e.g., 'status', 'create_campaign')"},
            "args": {"type": "object", "description": "Arguments for the operation"},
        },
        "required": ["op"]
    },
)


HELP = """
Help:

facebook(op="status")
    Shows current Ad Account status, lists active campaigns.

facebook(op="list_campaigns", args={"status": "ACTIVE"})
    Lists campaigns. Optional filters: status (ACTIVE, PAUSED, ARCHIVED).

facebook(op="create_campaign", args={
    "name": "Summer Sale 2025",
    "objective": "OUTCOME_TRAFFIC",
    "daily_budget": 5000,
    "status": "PAUSED"
})
    Creates a new campaign.
    Valid objectives: OUTCOME_TRAFFIC, OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_AWARENESS, OUTCOME_LEADS, OUTCOME_APP_PROMOTION.
    Budget is in cents (e.g., 5000 = $50.00).

facebook(op="create_ad_set", args={
    "campaign_id": "123456",
    "name": "US 18-35 Interests",
    "daily_budget": 2000,
    "status": "PAUSED",
    "targeting": {"geo_locations": {"countries": ["US"]}}
})
    Creates an ad set within a campaign.

facebook(op="get_insights", args={"campaign_id": "123456", "days": 30})
    Gets performance metrics (impressions, clicks, spend, cpc, ctr).
"""

@dataclass
class Campaign:
    id: str
    name: str
    status: str
    objective: str
    daily_budget: Optional[int] = None # In cents
    lifetime_budget: Optional[int] = None # In cents

@dataclass
class Insights:
    impressions: int
    clicks: int
    spend: float
    cpc: float
    ctr: float


class IntegrationFacebook:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        app_id: str,
        app_secret: str,
        ad_account_id: str,
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = ""
        self.ad_account_id = ad_account_id or AD_ACCOUNT_ID
        # Ensure ad_account_id starts with 'act_'
        if self.ad_account_id and not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"
            
        self.problems = []
        self.is_fake = self.rcx.running_test_scenario

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        auth_searchable = None
        if not self.is_fake and not self.access_token:
            auth_searchable = hashlib.md5((self.app_id + self.ad_account_id).encode()).hexdigest()[:30]
            auth_json = await ckit_external_auth.decrypt_external_auth(self.fclient, auth_searchable)
            self.access_token = auth_json.get("access_token", "")

        if not self.is_fake and not self.access_token:
            assert auth_searchable
            auth_json = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "ad_account_id": self.ad_account_id,
            }
            await ckit_external_auth.upsert_external_auth(
                self.fclient,
                self.rcx.persona.persona_id,
                auth_searchable,
                f"Facebook Ads {self.ad_account_id}",
                "facebook",
                auth_json,
            )
            web_url = os.getenv("FLEXUS_WEB_URL", "http://localhost:3000")
            oauth_params = {
                "client_id": self.app_id,
                "redirect_uri": f"{web_url}/v1/external-auth/facebook",
                "scope": "ads_management,ads_read,read_insights",
                "state": auth_searchable,
                "response_type": "code",
            }
            auth_url = f"https://www.facebook.com/{API_VERSION}/dialog/oauth?{urlencode(oauth_params)}"
            return f"Facebook Authorization Required:\n\n{auth_url}\n\nAfter authorization, try your request again."

        if not self.is_fake:
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        r = ""

        if not op or "help" in op:
            r += HELP

        elif op == "status":
            if self.is_fake:
                return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
            
            r += f"Facebook Ads Account: {self.ad_account_id}\n"
            campaigns = await self._list_campaigns(status_filter="ACTIVE")
            if campaigns:
                r += f"Active Campaigns ({len(campaigns)}):\n"
                for c in campaigns:
                    budget_str = ""
                    if c.daily_budget:
                        budget_str = f"Daily Budget: ${c.daily_budget/100:.2f}"
                    elif c.lifetime_budget:
                        budget_str = f"Lifetime Budget: ${c.lifetime_budget/100:.2f}"
                    
                    r += f"  📊 {c.name} (ID: {c.id})\n"
                    r += f"     Status: {c.status}, Objective: {c.objective}, {budget_str}\n"
            else:
                r += "No active campaigns found.\n"

        elif op == "list_campaigns":
            status_filter = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "status", None)
            if self.is_fake:
                return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
            
            campaigns = await self._list_campaigns(status_filter=status_filter)
            if campaigns:
                r += f"Found {len(campaigns)} campaigns:\n"
                for c in campaigns:
                    r += f"  {c.name} (ID: {c.id}) - {c.status}\n"
            else:
                r += "No campaigns found.\n"

        elif op == "create_campaign":
            name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "name", "")
            objective = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "objective", "OUTCOME_TRAFFIC")
            daily_budget = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "daily_budget", None)
            status = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "status", "PAUSED")

            if not name:
                return "ERROR: name parameter required for create_campaign\n"

            if self.is_fake:
                return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

            result = await self._create_campaign(name, objective, status, daily_budget)
            if result:
                r += f"✅ Campaign created: {result.name} (ID: {result.id})\n"
                r += f"   Status: {result.status}, Objective: {result.objective}\n"
            else:
                r += "❌ Failed to create campaign. Check logs.\n"

        elif op == "get_insights":
            campaign_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "campaign_id", "")
            days = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "days", "30"))
            
            if not campaign_id:
                return "ERROR: campaign_id required\n"

            if self.is_fake:
                return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

            insights = await self._get_insights(campaign_id, days)
            if insights:
                r += f"Insights for Campaign {campaign_id} (Last {days} days):\n"
                r += f"  Impressions: {insights.impressions:,}\n"
                r += f"  Clicks: {insights.clicks:,}\n"
                r += f"  Spend: ${insights.spend:.2f}\n"
                r += f"  CTR: {insights.ctr:.2f}%\n"
                r += f"  CPC: ${insights.cpc:.2f}\n"
            else:
                r += "No insights found or error occurred.\n"

        else:
            r += f"Unknown operation {op!r}, try \"help\"\n"

        if self.problems:
            r += "\nProblems:\n" + "\n".join(self.problems)

        return r

    async def _list_campaigns(self, status_filter: Optional[str] = None) -> Optional[List[Campaign]]:
        url = f"{API_BASE}/{API_VERSION}/{self.ad_account_id}/campaigns"
        params = {
            "fields": "id,name,status,objective,daily_budget,lifetime_budget",
            "limit": 50
        }
        if status_filter:
            params["effective_status"] = f"['{status_filter}']"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    campaigns = []
                    for item in data.get("data", []):
                        campaigns.append(Campaign(
                            id=item["id"],
                            name=item["name"],
                            status=item["status"],
                            objective=item.get("objective", "UNKNOWN"),
                            daily_budget=int(item["daily_budget"]) if "daily_budget" in item else None,
                            lifetime_budget=int(item["lifetime_budget"]) if "lifetime_budget" in item else None,
                        ))
                    return campaigns
                else:
                    self.problems.append(f"List campaigns failed: {response.text}")
                    return None
        except Exception as e:
            self.problems.append(f"Exception listing campaigns: {e}")
            return None

    async def _create_campaign(self, name: str, objective: str, status: str, daily_budget: Optional[int]) -> Optional[Campaign]:
        url = f"{API_BASE}/{API_VERSION}/{self.ad_account_id}/campaigns"
        payload = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": [], # Required field, empty for general ads
        }
        if daily_budget:
            payload["daily_budget"] = daily_budget

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    return Campaign(
                        id=data["id"],
                        name=name,
                        status=status,
                        objective=objective,
                        daily_budget=daily_budget
                    )
                else:
                    self.problems.append(f"Create campaign failed: {response.text}")
                    return None
        except Exception as e:
            self.problems.append(f"Exception creating campaign: {e}")
            return None

    async def _get_insights(self, campaign_id: str, days: int) -> Optional[Insights]:
        url = f"{API_BASE}/{API_VERSION}/{campaign_id}/insights"
        params = {
            "fields": "impressions,clicks,spend,cpc,ctr",
            "date_preset": "last_30d" if days == 30 else "maximum", # Simplified mapping
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("data"):
                        return Insights(0, 0, 0.0, 0.0, 0.0)
                    
                    item = data["data"][0]
                    return Insights(
                        impressions=int(item.get("impressions", 0)),
                        clicks=int(item.get("clicks", 0)),
                        spend=float(item.get("spend", 0.0)),
                        cpc=float(item.get("cpc", 0.0)),
                        ctr=float(item.get("ctr", 0.0))
                    )
                else:
                    self.problems.append(f"Get insights failed: {response.text}")
                    return None
        except Exception as e:
            self.problems.append(f"Exception getting insights: {e}")
            return None
