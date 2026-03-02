import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.ckit_bunch_of_functions import BunchOfPythonFunctions
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
from flexus_client_kit.integrations.facebook import accounts
from flexus_client_kit.integrations.facebook import campaigns
from flexus_client_kit.integrations.facebook import adsets
from flexus_client_kit.integrations.facebook import ads

logger = logging.getLogger("fb")

bunch = BunchOfPythonFunctions("facebook", "Facebook/Instagram Marketing API.", ContextType=FacebookAdsClient)
bunch.add("account.", [accounts.list_ad_accounts, accounts.get_ad_account_info, accounts.update_spending_limit])
bunch.add("campaign.", [campaigns.list_campaigns, campaigns.create_campaign, campaigns.update_campaign, campaigns.duplicate_campaign, campaigns.archive_campaign, campaigns.bulk_update_campaigns, campaigns.get_insights])
bunch.add("adset.", [adsets.list_adsets, adsets.create_adset, adsets.update_adset, adsets.validate_targeting])
bunch.add("ad.", [ads.upload_image, ads.create_creative, ads.create_ad, ads.preview_ad])
FACEBOOK_TOOL = bunch.make_tool()


class IntegrationFacebook2:
    def __init__(
        self,
        fclient: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        ad_account_id: str = "",
    ):
        self.client = FacebookAdsClient(fclient, rcx, ad_account_id)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        auth_err = await self.client.ensure_auth()
        if auth_err:
            return auth_err
        return await bunch.called_by_model(self.client, toolcall, model_produced_args)
