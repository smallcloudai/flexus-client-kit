import asyncio
import logging
import os
import time
import secrets
import webbrowser
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse

import httpx

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("linkedin")

APP_ID = "227061705"
AD_ACCOUNT_ID = "513489554"

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:3000/"

API_BASE = "https://api.linkedin.com"
API_VERSION = "202509"


LINKEDIN_TOOL = ckit_cloudtool.CloudTool(
    name="linkedin",
    description="Interact with LinkedIn Ads API, call with op=\"help\" to print usage, call with op=\"status+help\" to see both status and help in one call",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": []
    },
)


HELP = """
Help:

linkedin(op="status")
    Shows current LinkedIn Ads account status, lists all campaign groups with their campaigns.

linkedin(op="list_campaign_groups")
    Lists all campaign groups for the ad account.

linkedin(op="list_campaigns", args={"campaign_group_id": "123456", "status": "ACTIVE"})
    Lists campaigns. Optional filters: campaign_group_id, status (ACTIVE, PAUSED, ARCHIVED, etc).

linkedin(op="create_campaign_group", args={
    "name": "Q1 2024 Campaigns",
    "total_budget": 1000.0,
    "currency": "USD",
    "status": "ACTIVE"
})
    Creates a new campaign group with specified budget.

linkedin(op="create_campaign", args={
    "campaign_group_id": "123456",
    "name": "Brand Awareness Campaign",
    "objective": "BRAND_AWARENESS",
    "daily_budget": 50.0,
    "currency": "USD",
    "status": "PAUSED"
})
    Creates a campaign in a campaign group.
    Valid objectives: BRAND_AWARENESS, WEBSITE_VISITS, ENGAGEMENT, VIDEO_VIEWS, LEAD_GENERATION, WEBSITE_CONVERSIONS, JOB_APPLICANTS

linkedin(op="get_campaign", args={"campaign_id": "123456"})
    Gets details for a specific campaign.

linkedin(op="update_campaign", args={"campaign_id": "123456", "status": "ACTIVE", "daily_budget": 100.0})
    Updates campaign settings. Optional: status, daily_budget, name.

linkedin(op="get_analytics", args={"campaign_id": "123456", "days": 30})
    Gets analytics for a campaign. Default: last 30 days.
"""

LINKEDIN_SETUP_SCHEMA = [
    {
        "bs_name": "LINKEDIN_ACCESS_TOKEN",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "LinkedIn",
        "bs_importance": 0,
        "bs_description": "LinkedIn API Access Token (obtain via OAuth flow)",
    },
    {
        "bs_name": "LINKEDIN_AD_ACCOUNT_ID",
        "bs_type": "string",
        "bs_default": AD_ACCOUNT_ID,
        "bs_group": "LinkedIn",
        "bs_importance": 0,
        "bs_description": "LinkedIn Ads Account ID",
    },
]


@dataclass
class Budget:
    amount: str
    currency_code: str


@dataclass
class CampaignGroup:
    id: str
    name: str
    status: str
    total_budget: Optional[Budget] = None


@dataclass
class Campaign:
    id: str
    name: str
    status: str
    objective_type: str
    daily_budget: Budget
    campaign_group_id: Optional[str] = None


@dataclass
class Analytics:
    impressions: int
    clicks: int
    cost: float


class IntegrationLinkedIn:
    def __init__(self, access_token: str, ad_account_id: str):
        if not access_token:
            raise ValueError("LinkedIn access token is required")
        self.access_token = access_token
        self.ad_account_id = ad_account_id or AD_ACCOUNT_ID
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": API_VERSION,
        }
        self.problems = []
        self._campaign_groups_cache = None
        self._campaigns_cache = None

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = False
        print_status = False
        r = ""

        if not op or "help" in op:
            print_help = True
        if not op or "status" in op:
            print_status = True

        if print_status:
            r += f"LinkedIn Ads Account: {self.ad_account_id}\n"
            r += f"Access Token: ...{self.access_token[-10:]}\n\n"

            # List all campaign groups with their campaigns
            await self._refresh_cache()
            if self._campaign_groups_cache:
                r += f"Campaign Groups ({len(self._campaign_groups_cache)}):\n"
                for group in self._campaign_groups_cache:
                    r += f"  📁 {group.name} (ID: {group.id}, Status: {group.status})"
                    if group.total_budget:
                        r += f" - Budget: {group.total_budget.amount} {group.total_budget.currency_code}"
                    r += "\n"

                    # List campaigns in this group
                    group_campaigns = [c for c in (self._campaigns_cache or []) if c.campaign_group_id == group.id]
                    if group_campaigns:
                        for campaign in group_campaigns:
                            r += f"    📊 {campaign.name} (ID: {campaign.id}, Status: {campaign.status})\n"
                            r += f"       Objective: {campaign.objective_type}, Daily Budget: {campaign.daily_budget.amount} {campaign.daily_budget.currency_code}\n"
                    else:
                        r += f"    (no campaigns)\n"
            else:
                r += "No campaign groups found or failed to fetch.\n"

            if self.problems:
                r += "\nProblems:\n"
                for problem in self.problems:
                    r += f"  {problem}\n"
            r += "\n"

        if print_help:
            r += HELP

        elif print_status:
            pass

        elif op == "list_campaign_groups":
            result = await self._list_campaign_groups()
            if result:
                r += f"Found {len(result)} campaign groups:\n"
                for group in result:
                    r += f"  {group.name} (ID: {group.id}, Status: {group.status})"
                    if group.total_budget:
                        r += f" - Budget: {group.total_budget.amount} {group.total_budget.currency_code}"
                    r += "\n"
            else:
                r += "No campaign groups found.\n"

        elif op == "list_campaigns":
            campaign_group_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "campaign_group_id", None)
            status_filter = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "status", None)
            result = await self._list_campaigns(status_filter=status_filter)
            if result:
                campaigns = result
                if campaign_group_id:
                    campaigns = [c for c in campaigns if c.campaign_group_id == campaign_group_id]
                r += f"Found {len(campaigns)} campaigns:\n"
                for campaign in campaigns:
                    r += f"  {campaign.name} (ID: {campaign.id})\n"
                    r += f"    Status: {campaign.status}, Objective: {campaign.objective_type}\n"
                    r += f"    Daily Budget: {campaign.daily_budget.amount} {campaign.daily_budget.currency_code}\n"
            else:
                r += "No campaigns found.\n"

        elif op == "create_campaign_group":
            name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "name", "")
            total_budget = float(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "total_budget", "1000.0"))
            currency = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "currency", "USD")
            status = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "status", "ACTIVE")

            if not name:
                return "ERROR: name parameter required for create_campaign_group\n"

            result = await self._create_campaign_group(name, total_budget, currency, status)
            if result:
                self._campaign_groups_cache = None  # Invalidate cache
                r += f"✅ Campaign group created: {result.name} (ID: {result.id})\n"
            else:
                r += "❌ Failed to create campaign group. Check logs for details.\n"

        elif op == "create_campaign":
            campaign_group_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "campaign_group_id", "")
            name = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "name", "")
            objective = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "objective", "BRAND_AWARENESS")
            daily_budget = float(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "daily_budget", "10.0"))
            currency = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "currency", "USD")
            status = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "status", "PAUSED")

            if not campaign_group_id or not name:
                return "ERROR: campaign_group_id and name parameters required for create_campaign\n"

            result = await self._create_campaign(campaign_group_id, name, objective, daily_budget, currency, status)
            if result:
                self._campaigns_cache = None  # Invalidate cache
                r += f"✅ Campaign created: {result.name} (ID: {result.id})\n"
                r += f"   Status: {result.status}, Objective: {result.objective_type}\n"
                r += f"   Daily Budget: {result.daily_budget.amount} {result.daily_budget.currency_code}\n"
            else:
                r += "❌ Failed to create campaign. Check logs for details.\n"

        elif op == "get_campaign":
            campaign_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "campaign_id", "")
            if not campaign_id:
                return "ERROR: campaign_id parameter required for get_campaign\n"

            result = await self._get_campaign(campaign_id)
            if result:
                r += f"Campaign: {result.name} (ID: {result.id})\n"
                r += f"  Status: {result.status}\n"
                r += f"  Objective: {result.objective_type}\n"
                r += f"  Daily Budget: {result.daily_budget.amount} {result.daily_budget.currency_code}\n"
            else:
                r += f"❌ Failed to get campaign {campaign_id}\n"

        elif op == "get_analytics":
            campaign_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "campaign_id", "")
            days = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "days", "30"))

            if not campaign_id:
                return "ERROR: campaign_id parameter required for get_analytics\n"

            result = await self._get_campaign_analytics(campaign_id, days)
            if result:
                r += f"Analytics for campaign {campaign_id} (last {days} days):\n"
                r += f"  Impressions: {result.impressions:,}\n"
                r += f"  Clicks: {result.clicks:,}\n"
                r += f"  Cost: ${result.cost:.2f}\n"
                if result.impressions > 0:
                    ctr = (result.clicks / result.impressions) * 100
                    r += f"  CTR: {ctr:.2f}%\n"
                if result.clicks > 0:
                    cpc = result.cost / result.clicks
                    r += f"  CPC: ${cpc:.2f}\n"
            else:
                r += f"❌ Failed to get analytics for campaign {campaign_id}\n"

        else:
            r += f"Unknown operation {op!r}, try \"help\"\n\n"

        return r

    async def _refresh_cache(self):
        """Refresh campaign groups and campaigns cache"""
        self._campaign_groups_cache = await self._list_campaign_groups()
        self._campaigns_cache = await self._list_campaigns()

    async def _list_campaign_groups(self) -> Optional[List[CampaignGroup]]:
        url = f"{API_BASE}/rest/adAccounts/{self.ad_account_id}/adCampaignGroups?q=search"
        logger.info(f"Listing campaign groups for account: {self.ad_account_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    groups = []
                    for elem in elements:
                        budget_data = elem.get("totalBudget")
                        groups.append(CampaignGroup(
                            id=elem["id"],
                            name=elem["name"],
                            status=elem["status"],
                            total_budget=Budget(
                                amount=budget_data["amount"],
                                currency_code=budget_data["currencyCode"],
                            ) if budget_data else None,
                        ))
                    return groups
                else:
                    logger.error(f"Failed to list campaign groups: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to list campaign groups: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception listing campaign groups")
            self.problems.append(f"Exception listing campaign groups: {e}")
            return None

    async def _list_campaigns(self, status_filter: Optional[str] = None) -> Optional[List[Campaign]]:
        params = {"q": "search"}
        if status_filter:
            params["search"] = f"(status:(values:List({status_filter})))"
        url = f"{API_BASE}/rest/adAccounts/{self.ad_account_id}/adCampaigns"
        logger.info(f"Listing campaigns for account: {self.ad_account_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    campaigns = []
                    for elem in elements:
                        budget_data = elem["dailyBudget"]
                        campaign_group_urn = elem.get("campaignGroup", "")
                        campaign_group_id = campaign_group_urn.split(":")[-1] if campaign_group_urn else None
                        campaigns.append(Campaign(
                            id=elem["id"],
                            name=elem["name"],
                            status=elem["status"],
                            objective_type=elem["objectiveType"],
                            daily_budget=Budget(
                                amount=budget_data["amount"],
                                currency_code=budget_data["currencyCode"],
                            ),
                            campaign_group_id=campaign_group_id,
                        ))
                    return campaigns
                else:
                    logger.error(f"Failed to list campaigns: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to list campaigns: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception listing campaigns")
            self.problems.append(f"Exception listing campaigns: {e}")
            return None

    async def _create_campaign_group(
        self,
        name: str,
        total_budget_amount: float,
        total_budget_currency: str,
        status: str,
    ) -> Optional[CampaignGroup]:
        account_urn = f"urn:li:sponsoredAccount:{self.ad_account_id}"
        start_time = int(time.time() * 1000)
        end_time = start_time + (30 * 86400 * 1000)
        payload = {
            "account": account_urn,
            "name": name,
            "status": status,
            "runSchedule": {
                "start": start_time,
                "end": end_time,
            },
            "totalBudget": {
                "amount": str(total_budget_amount),
                "currencyCode": total_budget_currency,
            },
        }
        url = f"{API_BASE}/rest/adAccounts/{self.ad_account_id}/adCampaignGroups"
        logger.info(f"Creating campaign group: {name}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                if response.status_code == 201:
                    campaign_group_id = response.headers["x-restli-id"]
                    return CampaignGroup(
                        id=campaign_group_id,
                        name=name,
                        status=status,
                        total_budget=Budget(
                            amount=str(total_budget_amount),
                            currency_code=total_budget_currency,
                        ),
                    )
                else:
                    logger.error(f"Failed to create campaign group: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to create campaign group: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception creating campaign group")
            self.problems.append(f"Exception creating campaign group: {e}")
            return None

    async def _create_campaign(
        self,
        campaign_group_id: str,
        name: str,
        objective_type: str,
        daily_budget_amount: float,
        daily_budget_currency: str,
        status: str,
    ) -> Optional[Campaign]:
        valid_objectives = ["BRAND_AWARENESS", "WEBSITE_VISITS", "ENGAGEMENT", "VIDEO_VIEWS", "LEAD_GENERATION", "WEBSITE_CONVERSIONS", "JOB_APPLICANTS"]
        if objective_type not in valid_objectives:
            logger.error(f"Invalid objective_type: {objective_type}")
            self.problems.append(f"Invalid objective_type: {objective_type}. Valid: {', '.join(valid_objectives)}")
            return None

        account_urn = f"urn:li:sponsoredAccount:{self.ad_account_id}"
        campaign_group_urn = f"urn:li:sponsoredCampaignGroup:{campaign_group_id}"
        payload = {
            "account": account_urn,
            "campaignGroup": campaign_group_urn,
            "name": name,
            "type": "SPONSORED_UPDATES",
            "objectiveType": objective_type,
            "status": status,
            "dailyBudget": {
                "amount": str(daily_budget_amount),
                "currencyCode": daily_budget_currency,
            },
            "unitCost": {
                "amount": "10.0",
                "currencyCode": daily_budget_currency,
            },
            "costType": "CPM",
            "offsiteDeliveryEnabled": False,
            "locale": {"country": "US", "language": "en"},
            "runSchedule": {
                "start": int(time.time() * 1000),
            },
            "politicalIntent": "NOT_POLITICAL",
        }
        url = f"{API_BASE}/rest/adAccounts/{self.ad_account_id}/adCampaigns"
        logger.info(f"Creating campaign: {name}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                if response.status_code == 201:
                    logger.info(f"Campaign created - headers: {dict(response.headers)}")
                    campaign_id = response.headers["x-restli-id"]
                    return Campaign(
                        id=campaign_id,
                        name=name,
                        status=status,
                        objective_type=objective_type,
                        daily_budget=Budget(
                            amount=str(daily_budget_amount),
                            currency_code=daily_budget_currency,
                        ),
                        campaign_group_id=campaign_group_id,
                    )
                else:
                    logger.error(f"Failed to create campaign: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to create campaign: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception creating campaign")
            self.problems.append(f"Exception creating campaign: {e}")
            return None

    async def _get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        url = f"{API_BASE}/rest/adAccounts/{self.ad_account_id}/adCampaigns/{campaign_id}"
        logger.info(f"Fetching campaign: {campaign_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    budget_data = data["dailyBudget"]
                    campaign_group_urn = data.get("campaignGroup", "")
                    campaign_group_id = campaign_group_urn.split(":")[-1] if campaign_group_urn else None
                    return Campaign(
                        id=data["id"],
                        name=data["name"],
                        status=data["status"],
                        objective_type=data["objectiveType"],
                        daily_budget=Budget(
                            amount=budget_data["amount"],
                            currency_code=budget_data["currencyCode"],
                        ),
                        campaign_group_id=campaign_group_id,
                    )
                else:
                    logger.error(f"Failed to get campaign: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to get campaign: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception fetching campaign")
            self.problems.append(f"Exception fetching campaign: {e}")
            return None

    async def _get_campaign_analytics(
        self,
        campaign_id: str,
        days: int = 30,
    ) -> Optional[Analytics]:
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        date_range = (
            f"(start:(year:{start_date.year},month:{start_date.month},day:{start_date.day}),"
            f"end:(year:{end_date.year},month:{end_date.month},day:{end_date.day}))"
        )

        campaign_urn = f"urn%3Ali%3AsponsoredCampaign%3A{campaign_id}"

        url = (
            f"{API_BASE}/rest/adAnalytics?"
            f"q=analytics&"
            f"pivot=CAMPAIGN&"
            f"campaigns=List({campaign_urn})&"
            f"timeGranularity=DAILY&"
            f"dateRange={date_range}&"
            f"fields=impressions,clicks,costInLocalCurrency"
        )
        logger.info(f"Fetching analytics for campaign: {campaign_id}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
                request = httpx.Request("GET", url, headers=headers)
                response = await client.send(request)
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    if not elements:
                        return Analytics(impressions=0, clicks=0, cost=0.0)

                    # Aggregate all daily data
                    total_impressions = sum(e.get("impressions", 0) for e in elements)
                    total_clicks = sum(e.get("clicks", 0) for e in elements)
                    total_cost = sum(float(e.get("costInLocalCurrency", 0) or 0) for e in elements)

                    return Analytics(
                        impressions=total_impressions,
                        clicks=total_clicks,
                        cost=total_cost,
                    )
                else:
                    logger.error(f"Failed to get analytics: {response.status_code} - {response.text}")
                    self.problems.append(f"Failed to get analytics: {response.status_code}")
                    return None
        except Exception as e:
            logger.exception("Exception fetching analytics")
            self.problems.append(f"Exception fetching analytics: {e}")
            return None


def linkedin_access_token() -> str:
    """Standalone function to obtain LinkedIn OAuth access token"""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set")
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "rw_ads r_ads_reporting",
        "state": state,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    print(f"Opening browser for LinkedIn authorization...")
    print(f"Auth URL: {auth_url}")
    webbrowser.open(auth_url)
    print("\nAfter authorizing, paste the full redirect URL here:")
    redirect_response = input("URL: ").strip()
    parsed = urlparse(redirect_response)
    query_params = parse_qs(parsed.query)
    if "error" in query_params:
        raise RuntimeError(f"Authorization failed: {query_params['error'][0]}")
    if "code" not in query_params:
        raise RuntimeError("No authorization code in response")
    code = query_params["code"][0]
    returned_state = query_params.get("state", [None])[0]
    if returned_state != state:
        raise RuntimeError("State mismatch - possible CSRF attack")
    token_params = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    response = httpx.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=token_params,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise RuntimeError(f"Token exchange failed: {response.text}")
    data = response.json()
    access_token = data["access_token"]
    expires_in = data["expires_in"]
    print(f"\nAccess token obtained! Expires in {expires_in} seconds")
    print(f"Access token: {access_token}")
    return access_token


async def test():
    """Test function to demonstrate the LinkedIn integration"""
    logging.basicConfig(level=logging.INFO)
    print("=" * 80)
    print("LinkedIn Ads API Test")
    print("=" * 80)
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    if not access_token:
        print("No LINKEDIN_ACCESS_TOKEN found, starting OAuth flow...")
        access_token = linkedin_access_token()

    integration = IntegrationLinkedIn(access_token=access_token, ad_account_id=AD_ACCOUNT_ID)

    class MockToolCall:
        def __init__(self):
            self.fcall_ft_id = "test_ft_id"
            self.fcall_created_ts = time.time()

    toolcall = MockToolCall()

    print("\n" + "=" * 80)
    print("TEST: Status")
    print("=" * 80)
    result = await integration.called_by_model(toolcall, {"op": "status"})
    print(result)


if __name__ == "__main__":
    asyncio.run(test())
