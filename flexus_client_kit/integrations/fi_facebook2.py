import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.ckit_bunch_of_functions import BunchOfPythonFunctions
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("fb")

ALL_FACEBOOK_GROUPS = ["account", "campaign", "adset", "ad"]


def make_facebook_bunch(groups: list[str] | None = None) -> BunchOfPythonFunctions:
    b = BunchOfPythonFunctions("facebook", "Facebook/Instagram Marketing API.", ContextType=FacebookAdsClient)
    for g in (groups or ALL_FACEBOOK_GROUPS):
        if g == "account":
            from flexus_client_kit.integrations.facebook import accounts
            b.add("account.", [accounts.list_ad_accounts, accounts.get_ad_account_info, accounts.update_spending_limit])
        elif g == "campaign":
            from flexus_client_kit.integrations.facebook import campaigns
            b.add("campaign.", [campaigns.list_campaigns, campaigns.create_campaign, campaigns.update_campaign, campaigns.duplicate_campaign, campaigns.archive_campaign, campaigns.bulk_update_campaigns, campaigns.get_insights])
        elif g == "adset":
            from flexus_client_kit.integrations.facebook import adsets
            b.add("adset.", [adsets.list_adsets, adsets.create_adset, adsets.update_adset, adsets.validate_targeting])
        elif g == "ad":
            from flexus_client_kit.integrations.facebook import ads
            b.add("ad.", [ads.upload_image, ads.create_creative, ads.create_ad, ads.preview_ad])
        else:
            raise ValueError(f"Unknown facebook group {g!r}")
    return b


class IntegrationFacebook2:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        bunch: BunchOfPythonFunctions,
        ad_account_id: str = "",
    ):
        self.client = FacebookAdsClient(fclient, rcx, ad_account_id)
        self._bunch = bunch

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        auth_err = await self.client.ensure_auth()
        if auth_err:
            return auth_err
        return await self._bunch.called_by_model(self.client, toolcall, model_produced_args)
