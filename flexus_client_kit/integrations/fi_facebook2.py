import logging
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit.ckit_bunch_of_functions import BunchOfPythonFunctions
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
from flexus_client_kit.integrations.facebook import adsets

logger = logging.getLogger("fb")

bunch = BunchOfPythonFunctions("facebook", "Facebook/Instagram Marketing API.", ContextType=FacebookAdsClient)
bunch.add("adset.", [adsets.list_adsets, adsets.create_adset, adsets.update_adset, adsets.validate_targeting])
# bunch.add("campaign.", [...])
# bunch.add("account.", [...])
# bunch.add("ad.", [...])
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
