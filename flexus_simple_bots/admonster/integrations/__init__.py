"""
AdMonster Facebook Integrations Package

Exports dispatch_facebook_operation() for routing tool calls to specialized handlers.
"""

from flexus_simple_bots.admonster.integrations import fb_ad_account
from flexus_simple_bots.admonster.integrations import fb_campaign
from flexus_simple_bots.admonster.integrations import fb_adset
from flexus_simple_bots.admonster.integrations import fb_creative


# Operation prefixes → handler modules
_OPERATION_HANDLERS = {
    # Ad Account operations
    "list_ad_accounts": fb_ad_account,
    "get_ad_account": fb_ad_account,
    "update_spending": fb_ad_account,
    # Campaign operations (extended)
    "update_campaign": fb_campaign,
    "duplicate_campaign": fb_campaign,
    "archive_campaign": fb_campaign,
    "bulk_update": fb_campaign,
    # Ad Set operations
    "create_adset": fb_adset,
    "list_adsets": fb_adset,
    "update_adset": fb_adset,
    "validate_targeting": fb_adset,
    # Creative & Ad operations
    "upload_image": fb_creative,
    "create_creative": fb_creative,
    "create_ad": fb_creative,
    "preview_ad": fb_creative,
}


async def dispatch_facebook_operation(integration, toolcall, model_produced_args) -> str:
    """
    Route Facebook tool call to appropriate handler.
    
    Returns None if operation should be handled by base IntegrationFacebook.
    Returns str result if handled by extended handler.
    """
    op = model_produced_args.get("op", "")
    
    # Find handler by matching operation prefix
    for prefix, handler in _OPERATION_HANDLERS.items():
        if op.startswith(prefix):
            return await handler.handle(integration, toolcall, model_produced_args)
    
    # No match - let base integration handle it
    return None
