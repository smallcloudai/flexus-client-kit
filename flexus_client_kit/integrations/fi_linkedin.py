import asyncio
import logging
import os
import time
import secrets
import webbrowser
from typing import List, Optional
from dataclasses import dataclass
from urllib.parse import urlencode, parse_qs, urlparse

import httpx

logger = logging.getLogger("linkedin")

APP_ID = "227061705"
AD_ACCOUNT_ID = "513489554"

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:3000/"

API_BASE = "https://api.linkedin.com"
API_VERSION = "202509"


def linkedin_access_token() -> str:
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
    # http://localhost:3000/?code=AQRbXcm1yYJ3Q2EM6Ba7Ag
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


@dataclass
class Budget:
    amount: str
    currency_code: str


@dataclass
class CampaignGroup:
    id: str
    name: str
    status: str


@dataclass
class Campaign:
    id: str
    name: str
    status: str
    objective_type: str
    daily_budget: Budget


@dataclass
class Analytics:
    impressions: int
    clicks: int
    cost: float


@dataclass
class CampaignResult:
    success: bool
    message: str
    campaign: Optional[Campaign] = None
    campaigns: Optional[List[Campaign]] = None
    analytics: Optional[Analytics] = None
    campaign_group: Optional[CampaignGroup] = None


class LinkedInAdsClient:
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("LinkedIn access token is required")
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": API_VERSION,
        }

    async def create_campaign_group(
        self,
        ad_account_id: str,
        name: str,
        total_budget_amount: float,
        total_budget_currency: str,
        status: str,
    ) -> CampaignResult:
        account_urn = f"urn:li:sponsoredAccount:{ad_account_id}"
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
        url = f"{API_BASE}/rest/adAccounts/{ad_account_id}/adCampaignGroups"
        logger.info(f"Creating campaign group: {name}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                if response.status_code == 201:
                    campaign_group_id = response.headers["x-restli-id"]
                    campaign_group = CampaignGroup(
                        id=campaign_group_id,
                        name=name,
                        status=status,
                    )
                    return CampaignResult(
                        success=True,
                        message=f"Campaign group created: {campaign_group.id}",
                        campaign_group=campaign_group,
                    )
                else:
                    logger.error(f"Failed to create campaign group: {response.status_code} - {response.text}")
                    return CampaignResult(success=False, message=f"Error {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Exception creating campaign group")
            return CampaignResult(success=False, message="Exception during campaign group creation")

    async def create_campaign(
        self,
        ad_account_id: str,
        campaign_group_id: str,
        name: str,
        objective_type: str,
        daily_budget_amount: float,
        daily_budget_currency: str,
        status: str,
    ) -> CampaignResult:
        assert objective_type in ["BRAND_AWARENESS", "WEBSITE_VISITS", "ENGAGEMENT", "VIDEO_VIEWS", "LEAD_GENERATION", "WEBSITE_CONVERSIONS", "JOB_APPLICANTS"]
        account_urn = f"urn:li:sponsoredAccount:{ad_account_id}"
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
        url = f"{API_BASE}/rest/adAccounts/{ad_account_id}/adCampaigns"
        logger.info(f"Creating campaign: {name}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers, timeout=30.0)
                if response.status_code == 201:
                    logger.info(f"Campaign created - headers: {dict(response.headers)}")
                    campaign_id = response.headers["x-restli-id"]
                    campaign = Campaign(
                        id=campaign_id,
                        name=name,
                        status=status,
                        objective_type=objective_type,
                        daily_budget=Budget(
                            amount=str(daily_budget_amount),
                            currency_code=daily_budget_currency,
                        ),
                    )
                    return CampaignResult(
                        success=True,
                        message=f"Campaign created: {campaign.id}",
                        campaign=campaign,
                    )
                else:
                    logger.error(f"Failed to create campaign: {response.status_code} - {response.text}")
                    return CampaignResult(success=False, message=f"Error {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Exception creating campaign")
            return CampaignResult(success=False, message="Exception during campaign creation")

    async def get_campaign(self, ad_account_id: str, campaign_id: str) -> CampaignResult:
        url = f"{API_BASE}/rest/adAccounts/{ad_account_id}/adCampaigns/{campaign_id}"
        logger.info(f"Fetching campaign: {campaign_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    budget_data = data["dailyBudget"]
                    campaign = Campaign(
                        id=data["id"],
                        name=data["name"],
                        status=data["status"],
                        objective_type=data["objectiveType"],
                        daily_budget=Budget(
                            amount=budget_data["amount"],
                            currency_code=budget_data["currencyCode"],
                        ),
                    )
                    return CampaignResult(success=True, message=f"Campaign: {campaign.name}", campaign=campaign)
                else:
                    logger.error(f"Failed to get campaign: {response.status_code} - {response.text}")
                    return CampaignResult(success=False, message=f"Error {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Exception fetching campaign")
            return CampaignResult(success=False, message="Exception fetching campaign")

    async def get_campaign_analytics(
        self,
        ad_account_id: str,
        campaign_id: str,
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None,
    ) -> CampaignResult:
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        date_range = (
            f"(start:(year:{start_date.year},month:{start_date.month},day:{start_date.day}),"
            f"end:(year:{end_date.year},month:{end_date.month},day:{end_date.day}))"
        )

        # Build URL with properly encoded URNs but unencoded commas in fields
        # URNs must be URL-encoded (: becomes %3A)
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
        logger.info(f"URL: {url}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
                # Use httpx.Request to prevent any URL manipulation
                request = httpx.Request("GET", url, headers=headers)
                response = await client.send(request)
                logger.info(f"Actual request URL: {response.request.url}")
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])
                    if not elements:
                        return CampaignResult(success=True, message="No analytics data yet")
                    e0 = elements[0]
                    analytics = Analytics(
                        impressions=e0.get("impressions", 0),
                        clicks=e0.get("clicks", 0),
                        cost=float(e0.get("costInLocalCurrency", 0) or 0),
                    )
                    return CampaignResult(success=True, message="Analytics retrieved", analytics=analytics)
                else:
                    logger.error(f"Failed to get analytics: {response.status_code} - {response.text}")
                    return CampaignResult(success=False, message=f"Error {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Exception fetching analytics")
            return CampaignResult(success=False, message="Exception fetching analytics")

    async def list_campaigns(self, ad_account_id: str, status_filter: Optional[str] = None) -> CampaignResult:
        params = {"q": "search"}
        if status_filter:
            params["search"] = f"(status:(values:List({status_filter})))"
        url = f"{API_BASE}/rest/adAccounts/{ad_account_id}/adCampaigns"
        logger.info(f"Listing campaigns for account: {ad_account_id}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=self.headers, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    elements = data["elements"]
                    campaigns = []
                    for elem in elements:
                        budget_data = elem["dailyBudget"]
                        campaigns.append(Campaign(
                            id=elem["id"],
                            name=elem["name"],
                            status=elem["status"],
                            objective_type=elem["objectiveType"],
                            daily_budget=Budget(
                                amount=budget_data["amount"],
                                currency_code=budget_data["currencyCode"],
                            ),
                        ))
                    return CampaignResult(success=True, message=f"Found {len(campaigns)} campaigns", campaigns=campaigns)
                else:
                    logger.error(f"Failed to list campaigns: {response.status_code} - {response.text}")
                    return CampaignResult(success=False, message=f"Error {response.status_code}: {response.text}")
        except Exception:
            logger.exception("Exception listing campaigns")
            return CampaignResult(success=False, message="Exception listing campaigns")


async def test():
    logging.basicConfig(level=logging.INFO)
    print("=" * 80)
    print("LinkedIn Ads API Test")
    print("=" * 80)
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    if not access_token:
        print("No LINKEDIN_ACCESS_TOKEN found, starting OAuth flow...")
        access_token = linkedin_access_token()
    print(f"\nUsing Ad Account ID: {AD_ACCOUNT_ID}")
    print(f"Access Token: {access_token[:10]}...{access_token[-10:]}\n")
    client = LinkedInAdsClient(access_token)

    print("\n" + "=" * 80)
    print("TEST 1: List existing campaigns")
    print("=" * 80)
    result = await client.list_campaigns(AD_ACCOUNT_ID)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.campaigns:
        for campaign in result.campaigns[:3]:
            print(f"  - {campaign.name} (ID: {campaign.id}, Status: {campaign.status})")
    print()

    print("\n" + "=" * 80)
    print("TEST 2: Create a campaign group")
    print("=" * 80)
    group_name = f"Test Group {int(time.time())}"
    result = await client.create_campaign_group(
        ad_account_id=AD_ACCOUNT_ID,
        name=group_name,
        total_budget_amount=1000.0,
        total_budget_currency="USD",
        status="ACTIVE",
    )
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if not result.campaign_group:
        print("Failed to create campaign group")
        return
    campaign_group_id = result.campaign_group.id
    print(f"Campaign Group ID: {campaign_group_id}")
    print()

    print("\n" + "=" * 80)
    print("TEST 3: Create a test campaign")
    print("=" * 80)
    test_campaign_name = f"Test Campaign {int(time.time())}"
    result = await client.create_campaign(
        ad_account_id=AD_ACCOUNT_ID,
        campaign_group_id=campaign_group_id,
        name=test_campaign_name,
        objective_type="BRAND_AWARENESS",
        daily_budget_amount=10.0,
        daily_budget_currency="USD",
        status="PAUSED",
    )
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.campaign:
        print(f"Campaign ID: {result.campaign.id}")
        created_campaign_id = result.campaign.id
    else:
        print("Failed to create campaign")
        return
    print()

    print("\n" + "=" * 80)
    print("TEST 4: Get campaign details")
    print("=" * 80)
    result = await client.get_campaign(AD_ACCOUNT_ID, created_campaign_id)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.campaign:
        campaign = result.campaign
        print(f"  Name: {campaign.name}")
        print(f"  Status: {campaign.status}")
        print(f"  Objective: {campaign.objective_type}")
        print(f"  Daily Budget: {campaign.daily_budget.amount} {campaign.daily_budget.currency_code}")
    print()

    print("\n" + "=" * 80)
    print("TEST 5: Get campaign analytics")
    print("=" * 80)
    result = await client.get_campaign_analytics(AD_ACCOUNT_ID, created_campaign_id)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.analytics:
        analytics = result.analytics
        print(f"  Impressions: {analytics.impressions}")
        print(f"  Clicks: {analytics.clicks}")
        print(f"  Cost: {analytics.cost}")
    print()
    print("=" * 80)
    print("Tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test())
