# Inspired from: https://github.com/n8n-io/n8n/blob/master/packages/nodes-base/nodes/Google/Analytics/v2/GoogleAnalyticsV2.node.ts

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import gql.transport.exceptions
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_external_auth

logger = logging.getLogger("google_analytics")

GOOGLE_ANALYTICS_TOOL = ckit_cloudtool.CloudTool(
    name="google_analytics",
    description="Access Google Analytics data, call with op=\"help\" to print usage",
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

google_analytics(op="status")
    Show connection status and available operations.

# Report Operations (GA4)
google_analytics(op="getReport", args={
    "propertyId": "123456",
    "dateRange": "last7days",  # Options: today, yesterday, last7days, last30days, lastWeek, lastMonth, custom
    "metrics": ["totalUsers", "sessions"],  # List of metric names
    "dimensions": ["date", "country"],  # Optional: List of dimension names
    "startDate": "2024-01-01",  # Required if dateRange="custom"
    "endDate": "2024-01-31",  # Required if dateRange="custom"
    "limit": 100,  # Optional, default 100
    "orderBy": {"metric": "totalUsers", "desc": True}  # Optional
})
    Get analytics report data. Common metrics:
    - totalUsers, activeUsers, newUsers
    - sessions, sessionsPerUser, screenPageViews
    - bounceRate, averageSessionDuration
    - conversions, totalRevenue, purchaseRevenue

    Common dimensions:
    - date, year, month, week, day
    - country, city, region, continent
    - browser, deviceCategory, operatingSystem
    - pagePath, pageTitle, landingPage
    - sessionSource, sessionMedium, sessionCampaignName

google_analytics(op="listProperties")
    List all Google Analytics properties you have access to.

google_analytics(op="getPropertyDetails", args={"propertyId": "123456"})
    Get details about a specific property.

# User Activity Operations (Universal Analytics - deprecated but still available)
google_analytics(op="getUserActivity", args={
    "viewId": "12345",
    "userId": "user123",
    "activityTypes": ["PAGEVIEW", "EVENT", "ECOMMERCE", "GOAL"]  # Optional
})
    Search for user activity by user ID.

# Common Usage Examples:

# Daily traffic for last 7 days
google_analytics(op="getReport", args={
    "propertyId": "123456",
    "dateRange": "last7days",
    "metrics": ["totalUsers", "sessions", "screenPageViews"],
    "dimensions": ["date"]
})

# Top pages by traffic
google_analytics(op="getReport", args={
    "propertyId": "123456",
    "dateRange": "last30days",
    "metrics": ["screenPageViews", "totalUsers"],
    "dimensions": ["pagePath", "pageTitle"],
    "orderBy": {"metric": "screenPageViews", "desc": True},
    "limit": 20
})

# Traffic by country
google_analytics(op="getReport", args={
    "propertyId": "123456",
    "dateRange": "last30days",
    "metrics": ["totalUsers", "sessions"],
    "dimensions": ["country"],
    "orderBy": {"metric": "totalUsers", "desc": True}
})

# Conversion tracking
google_analytics(op="getReport", args={
    "propertyId": "123456",
    "dateRange": "lastMonth",
    "metrics": ["conversions", "totalRevenue"],
    "dimensions": ["sessionSource", "sessionMedium"]
})
"""

GOOGLE_ANALYTICS_SETUP_SCHEMA = [
    {
        "bs_name": "GA_DEFAULT_PROPERTY",
        "bs_type": "string_short",
        "bs_default": "",
        "bs_group": "Google Analytics",
        "bs_description": "Default GA4 property ID (optional, e.g., '123456')",
    },
]

REQUIRED_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


@dataclass
class AnalyticsReport:
    rows: List[Dict[str, Any]]
    total_rows: int
    dimension_headers: List[str]
    metric_headers: List[str]


class IntegrationGoogleAnalytics:

    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx,  # ckit_bot_exec.RobotContext
    ):
        self.fclient = fclient
        self.rcx = rcx
        self.token_data = None
        self.service_data = None
        self.service_reporting = None
        self.admin_service = None

    async def _ensure_services(self) -> bool:
        if self.service_data and self.token_data and time.time() < self.token_data.expires_at - 60:
            return True

        try:
            self.token_data = await ckit_external_auth.get_external_auth_token(
                self.fclient,
                "google",
                self.rcx.persona.ws_id,
            )
        except gql.transport.exceptions.TransportQueryError:
            return False

        if not self.token_data:
            return False

        creds = google.oauth2.credentials.Credentials(token=self.token_data.access_token)
        self.service_data = googleapiclient.discovery.build('analyticsdata', 'v1beta', credentials=creds)
        self.service_reporting = googleapiclient.discovery.build('analyticsreporting', 'v4', credentials=creds)
        self.admin_service = googleapiclient.discovery.build('analyticsadmin', 'v1beta', credentials=creds)

        logger.info("Google Analytics services initialized for user %s", self.rcx.persona.owner_fuser_id)
        return True

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]]
    ) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        print_help = not op or "help" in op
        print_status = not op or "status" in op

        authenticated = await self._ensure_services()

        if print_status:
            r = f"Google Analytics integration status:\n"
            r += f"  Authenticated: {'✅ Yes' if authenticated else '❌ No'}\n"
            r += f"  User: {self.rcx.persona.owner_fuser_id}\n"
            r += f"  Workspace: {self.rcx.persona.ws_id}\n"
            if not authenticated:
                try:
                    auth_url = await ckit_external_auth.start_external_auth_flow(
                        self.fclient,
                        "google",
                        self.rcx.persona.ws_id,
                        REQUIRED_SCOPES,
                    )
                    r += f"\n❌ Not authenticated. Ask user to authorize at:\n{auth_url}\n"
                except gql.transport.exceptions.TransportQueryError as e:
                    r += f"\n❌ Error initiating OAuth: {e}\n"
            return r

        if print_help:
            return HELP

        if not authenticated:
            try:
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                return f"❌ Not authenticated. Ask user to authorize at:\n{auth_url}\n\nThen retry this operation."
            except gql.transport.exceptions.TransportQueryError as e:
                return f"❌ Failed to initiate OAuth: {e}"

        try:
            if op == "getReport":
                return await self._get_report(args)
            elif op == "listProperties":
                return await self._list_properties(args)
            elif op == "getPropertyDetails":
                return await self._get_property_details(args)
            elif op == "getUserActivity":
                return await self._get_user_activity(args)
            else:
                return f"❌ Unknown operation: {op}\n\nTry google_analytics(op='help') for usage."

        except googleapiclient.errors.HttpError as e:
            if e.resp.status in (401, 403):
                self.token_data = None
                self.service_data = None
                self.service_reporting = None
                self.admin_service = None
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                return f"❌ Google Analytics authentication error: {e.resp.status} - {e.error_details if hasattr(e, 'error_details') else str(e)}\n\nPlease authorize at:\n{auth_url}\n\nThen retry."
            error_msg = f"Google Analytics API error: {e.resp.status} - {e.error_details if hasattr(e, 'error_details') else str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"

    def _prepare_date_range(self, date_range: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, str]:
        today = datetime.now().date()

        if date_range == "today":
            return {"startDate": today.isoformat(), "endDate": today.isoformat()}
        elif date_range == "yesterday":
            yesterday = today - timedelta(days=1)
            return {"startDate": yesterday.isoformat(), "endDate": yesterday.isoformat()}
        elif date_range == "last7days":
            start = today - timedelta(days=7)
            return {"startDate": start.isoformat(), "endDate": today.isoformat()}
        elif date_range == "last30days":
            start = today - timedelta(days=30)
            return {"startDate": start.isoformat(), "endDate": today.isoformat()}
        elif date_range == "lastWeek":
            start_of_week = today - timedelta(days=today.weekday() + 7)
            end_of_week = start_of_week + timedelta(days=6)
            return {"startDate": start_of_week.isoformat(), "endDate": end_of_week.isoformat()}
        elif date_range == "lastMonth":
            first_of_this_month = today.replace(day=1)
            last_of_last_month = first_of_this_month - timedelta(days=1)
            first_of_last_month = last_of_last_month.replace(day=1)
            return {"startDate": first_of_last_month.isoformat(), "endDate": last_of_last_month.isoformat()}
        elif date_range == "custom":
            if not start_date or not end_date:
                raise ValueError("custom dateRange requires startDate and endDate")
            return {"startDate": start_date, "endDate": end_date}
        else:
            raise ValueError(f"Unknown dateRange: {date_range}")

    async def _get_report(self, args: Dict[str, Any]) -> str:
        property_id = args.get("propertyId", "")
        if not property_id:
            return "❌ Missing required parameter: 'propertyId'"

        date_range_type = args.get("dateRange", "last7days")
        start_date = args.get("startDate")
        end_date = args.get("endDate")

        try:
            date_range = self._prepare_date_range(date_range_type, start_date, end_date)
        except ValueError as e:
            return f"❌ {str(e)}"

        metrics_list = args.get("metrics", ["totalUsers"])
        dimensions_list = args.get("dimensions", [])
        limit = args.get("limit", 100)
        order_by = args.get("orderBy")

        body = {
            "dateRanges": [date_range],
            "metrics": [{"name": m} for m in metrics_list],
        }

        if dimensions_list:
            body["dimensions"] = [{"name": d} for d in dimensions_list]

        if order_by:
            metric_name = order_by.get("metric")
            dimension_name = order_by.get("dimension")
            desc = order_by.get("desc", False)

            if metric_name:
                body["orderBys"] = [{"metric": {"metricName": metric_name}, "desc": desc}]
            elif dimension_name:
                body["orderBys"] = [{"dimension": {"dimensionName": dimension_name}, "desc": desc}]

        body["limit"] = limit

        try:
            response = self.service_data.properties().runReport(
                property=f"properties/{property_id}",
                body=body
            ).execute()

            return self._format_report_response(response)

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 403:
                self.token_data = None
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                logger.exception("")
                return f"❌ Access denied to property {property_id}. Ask user to authorize at:\n{auth_url}\n\nEnsure they have access to this GA4 property and grant analytics.readonly scope."
            elif e.resp.status == 400:
                return f"❌ Invalid request: {e.error_details if hasattr(e, 'error_details') else str(e)}"
            raise

    def _format_report_response(self, response: Dict[str, Any]) -> str:
        dimension_headers = [h.get("name") for h in response.get("dimensionHeaders", [])]
        metric_headers = [h.get("name") for h in response.get("metricHeaders", [])]
        rows = response.get("rows", [])

        if not rows:
            return "📊 No data found for the specified criteria."

        output = ["📊 Analytics Report Results:\n"]
        output.append(f"Total rows: {len(rows)}\n")

        headers = dimension_headers + metric_headers
        output.append("  " + " | ".join(headers))
        output.append("  " + "-" * (len(" | ".join(headers))))

        for row in rows[:50]:
            dim_values = [dv.get("value", "") for dv in row.get("dimensionValues", [])]
            metric_values = [mv.get("value", "") for mv in row.get("metricValues", [])]
            all_values = dim_values + metric_values
            output.append("  " + " | ".join(all_values))

        if len(rows) > 50:
            output.append(f"\n... and {len(rows) - 50} more rows")

        return "\n".join(output)

    async def _list_properties(self, args: Dict[str, Any]) -> str:
        try:
            accounts = self.admin_service.accounts().list().execute()

            if not accounts.get("accounts"):
                return "📊 No Google Analytics accounts found."

            output = ["📊 Google Analytics Properties:\n"]

            for account in accounts.get("accounts", []):
                account_name = account.get("displayName", "Unknown")
                account_id = account.get("name", "").split("/")[-1]

                try:
                    properties = self.admin_service.properties().list(
                        filter=f"parent:{account.get('name')}"
                    ).execute()

                    if properties.get("properties"):
                        output.append(f"\n🏢 Account: {account_name} (ID: {account_id})")
                        for prop in properties.get("properties", []):
                            prop_name = prop.get("displayName", "Unknown")
                            prop_id = prop.get("name", "").split("/")[-1]
                            prop_type = "GA4"
                            output.append(f"  • {prop_name} (ID: {prop_id}, Type: {prop_type})")

                except HttpError as e:
                    output.append(f"\n🏢 Account: {account_name} (ID: {account_id})")
                    output.append(f"  ⚠️  Could not list properties: {e.resp.status}")

            return "\n".join(output)

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 403:
                self.token_data = None
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                logger.exception("")
                return f"❌ Access denied. Ask user to authorize at:\n{auth_url}\n\nEnsure analytics.readonly scope is granted."
            raise

    async def _get_property_details(self, args: Dict[str, Any]) -> str:
        property_id = args.get("propertyId", "")
        if not property_id:
            return "❌ Missing required parameter: 'propertyId'"

        try:
            prop = self.admin_service.properties().get(
                name=f"properties/{property_id}"
            ).execute()

            output = [
                "📊 Property Details:\n",
                f"Name: {prop.get('displayName', 'Unknown')}",
                f"ID: {property_id}",
                f"Create Time: {prop.get('createTime', 'Unknown')}",
                f"Update Time: {prop.get('updateTime', 'Unknown')}",
                f"Time Zone: {prop.get('timeZone', 'Unknown')}",
                f"Currency Code: {prop.get('currencyCode', 'Unknown')}",
            ]

            return "\n".join(output)

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 403:
                self.token_data = None
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                logger.exception("")
                return f"❌ Access denied to property {property_id}. Ask user to authorize at:\n{auth_url}\n\nEnsure analytics.readonly scope is granted."
            elif e.resp.status == 404:
                return f"❌ Property {property_id} not found"
            raise

    async def _get_user_activity(self, args: Dict[str, Any]) -> str:
        view_id = args.get("viewId", "")
        user_id = args.get("userId", "")

        if not view_id or not user_id:
            return "❌ Missing required parameters: 'viewId' and 'userId'"

        activity_types = args.get("activityTypes", [])

        body = {
            "viewId": view_id,
            "user": {"userId": user_id}
        }

        if activity_types:
            body["activityTypes"] = activity_types

        try:
            response = self.service_reporting.userActivity().search(body=body).execute()

            sessions = response.get("sessions", [])

            if not sessions:
                return f"📊 No activity found for user {user_id}"

            output = [f"📊 User Activity for {user_id}:\n"]
            output.append(f"Total sessions: {len(sessions)}\n")

            for i, session in enumerate(sessions[:10], 1):
                session_date = session.get("sessionDate", "Unknown")
                activities = session.get("activities", [])
                output.append(f"{i}. Session on {session_date}")
                output.append(f"   Activities: {len(activities)}")

                for act in activities[:3]:
                    activity_type = act.get("activityType", "Unknown")
                    activity_time = act.get("activityTime", "Unknown")
                    output.append(f"   - {activity_type} at {activity_time}")

                if len(activities) > 3:
                    output.append(f"   ... and {len(activities) - 3} more activities")
                output.append("")

            if len(sessions) > 10:
                output.append(f"... and {len(sessions) - 10} more sessions")

            return "\n".join(output)

        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 403:
                self.token_data = None
                logger.exception("")
                auth_url = await ckit_external_auth.start_external_auth_flow(
                    self.fclient,
                    "google",
                    self.rcx.persona.ws_id,
                    REQUIRED_SCOPES,
                )
                return f"❌ Access denied. Ask user to authorize at:\n{auth_url}\n\nUser Activity API requires Universal Analytics view access with analytics.readonly scope."
            elif e.resp.status == 400:
                return f"❌ Invalid request: This feature requires Universal Analytics (deprecated). For GA4, use getReport instead."
            raise
