"""
Facebook Campaign Management (Extended)

Extends the existing campaign functionality with:
- Update campaigns
- Duplicate campaigns
- Bulk operations
- Archive campaigns
"""

import logging
from typing import Dict, Any, Optional, List

import httpx

from flexus_simple_bots.admonster.integrations import fb_utils

logger = logging.getLogger("fb_campaign")


async def handle(integration, toolcall, model_produced_args: Dict[str, Any]) -> str:
    """Router for campaign operations"""
    try:
        auth_error = await integration.ensure_headers()
        if auth_error:
            return auth_error
        
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        # Merge top-level params into args (model may pass them at top level)
        for key in ["ad_account_id", "campaign_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]
        
        if op == "update_campaign":
            return await update_campaign(integration, args)
        elif op == "duplicate_campaign":
            return await duplicate_campaign(integration, args)
        elif op == "archive_campaign":
            return await archive_campaign(integration, args)
        elif op == "bulk_update_campaigns":
            return await bulk_update_campaigns(integration, args)
        else:
            return f"Unknown campaign operation: {op}\n\nAvailable operations:\n- update_campaign\n- duplicate_campaign\n- archive_campaign\n- bulk_update_campaigns"
    
    except fb_utils.FacebookAPIError as e:
        logger.info(f"Facebook API error in campaign: {e}")  # Expected external API error
        return f"❌ Facebook API Error: {e.message}"
    except Exception as e:
        logger.warning(f"Campaign error: {e}", exc_info=e)  # Unexpected, log stack for debugging
        return f"ERROR: {str(e)}"


async def update_campaign(integration, args: Dict[str, Any]) -> str:
    """Update an existing campaign"""
    try:
        campaign_id = args.get("campaign_id", "")
        if not campaign_id:
            return "ERROR: campaign_id parameter is required"
        
        name = args.get("name")
        status = args.get("status")
        daily_budget = args.get("daily_budget")
        lifetime_budget = args.get("lifetime_budget")
        
        if not any([name, status, daily_budget, lifetime_budget]):
            return "ERROR: At least one field to update is required (name, status, daily_budget, or lifetime_budget)"
        
        if status and status not in ["ACTIVE", "PAUSED"]:
            return "ERROR: status must be either 'ACTIVE' or 'PAUSED'"
        
        if integration.is_fake:
            updates = []
            if name:
                updates.append(f"name → {name}")
            if status:
                updates.append(f"status → {status}")
            if daily_budget:
                updates.append(f"daily_budget → {fb_utils.format_currency(daily_budget)}")
            if lifetime_budget:
                updates.append(f"lifetime_budget → {fb_utils.format_currency(lifetime_budget)}")
            
            return f"✅ Campaign {campaign_id} updated:\n" + "\n".join(f"   • {u}" for u in updates)
        
        url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{campaign_id}"
        data = {}
        
        if name:
            data["name"] = name
        if status:
            data["status"] = status
        if daily_budget is not None:
            fb_utils.validate_budget(daily_budget)
            data["daily_budget"] = daily_budget
        if lifetime_budget is not None:
            fb_utils.validate_budget(lifetime_budget)
            data["lifetime_budget"] = lifetime_budget
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        result = await fb_utils.retry_with_backoff(make_request)
        
        if result.get("success"):
            updates = []
            if name:
                updates.append(f"name → {name}")
            if status:
                updates.append(f"status → {status}")
            if daily_budget:
                updates.append(f"daily_budget → {fb_utils.format_currency(daily_budget)}")
            if lifetime_budget:
                updates.append(f"lifetime_budget → {fb_utils.format_currency(lifetime_budget)}")
            
            return f"✅ Campaign {campaign_id} updated:\n" + "\n".join(f"   • {u}" for u in updates)
        else:
            return f"❌ Failed to update campaign. Response: {result}"
    
    except fb_utils.FacebookAPIError:
        raise
    except ValueError as e:
        return f"ERROR: {str(e)}"
    except Exception as e:
        logger.warning(f"Error updating campaign: {e}", exc_info=e)
        return f"ERROR: Failed to update campaign: {str(e)}"


async def duplicate_campaign(integration, args: Dict[str, Any]) -> str:
    """Duplicate an existing campaign"""
    try:
        campaign_id = args.get("campaign_id", "")
        new_name = args.get("new_name", "")
        
        if not campaign_id:
            return "ERROR: campaign_id parameter is required"
        
        if not new_name:
            return "ERROR: new_name parameter is required"
        
        if integration.is_fake:
            mock_campaign = fb_utils.generate_mock_campaign()
            mock_campaign["id"] = f"{campaign_id}_copy"
            mock_campaign["name"] = new_name
            return f"""✅ Campaign duplicated successfully!

New Campaign:
   ID: {mock_campaign['id']}
   Name: {mock_campaign['name']}
   Status: {mock_campaign['status']}
   Objective: {mock_campaign['objective']}
   
Note: Ad sets and ads from the original campaign were also copied.
"""
        
        get_url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{campaign_id}"
        get_params = {"fields": "name,objective,status,daily_budget,lifetime_budget,special_ad_categories"}
        
        async def get_campaign():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    get_url,
                    params=get_params,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        original = await fb_utils.retry_with_backoff(get_campaign)
        
        ad_account_id = "act_" + campaign_id.split("_")[0] if "_" in campaign_id else integration.ad_account_id
        create_url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/campaigns"
        
        create_data = {
            "name": new_name,
            "objective": original["objective"],
            "status": "PAUSED",
            "special_ad_categories": original.get("special_ad_categories", []),
        }
        
        if "daily_budget" in original:
            create_data["daily_budget"] = original["daily_budget"]
        if "lifetime_budget" in original:
            create_data["lifetime_budget"] = original["lifetime_budget"]
        
        async def create_campaign():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    create_url,
                    json=create_data,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        new_campaign = await fb_utils.retry_with_backoff(create_campaign)
        
        result = f"""✅ Campaign duplicated successfully!

Original Campaign ID: {campaign_id}
New Campaign ID: {new_campaign.get('id')}
New Campaign Name: {new_name}
Status: PAUSED (activate when ready)

Note: Only the campaign was copied. To copy ad sets and ads, use the Facebook Ads Manager UI.
"""
        return result
    
    except fb_utils.FacebookAPIError:
        raise
    except Exception as e:
        logger.warning(f"Error duplicating campaign: {e}", exc_info=e)
        return f"ERROR: Failed to duplicate campaign: {str(e)}"


async def archive_campaign(integration, args: Dict[str, Any]) -> str:
    """Archive (soft delete) a campaign"""
    try:
        campaign_id = args.get("campaign_id", "")
        if not campaign_id:
            return "ERROR: campaign_id parameter is required"
        
        if integration.is_fake:
            return f"✅ Campaign {campaign_id} archived successfully.\n\nThe campaign is now hidden from active views but can be restored if needed."
        
        url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{campaign_id}"
        data = {"status": "ARCHIVED"}
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        result = await fb_utils.retry_with_backoff(make_request)
        
        if result.get("success"):
            return f"✅ Campaign {campaign_id} archived successfully.\n\nThe campaign is now hidden from active views but can be restored if needed."
        else:
            return f"❌ Failed to archive campaign. Response: {result}"
    
    except fb_utils.FacebookAPIError:
        raise
    except Exception as e:
        logger.warning(f"Error archiving campaign: {e}", exc_info=e)
        return f"ERROR: Failed to archive campaign: {str(e)}"


async def bulk_update_campaigns(integration, args: Dict[str, Any]) -> str:
    """Update multiple campaigns at once"""
    try:
        campaigns = args.get("campaigns", [])
        
        if not campaigns:
            return "ERROR: campaigns parameter is required (list of {id, ...fields})"
        
        if not isinstance(campaigns, list):
            return "ERROR: campaigns must be a list"
        
        if len(campaigns) > 50:
            return "ERROR: Maximum 50 campaigns can be updated at once"
        
        if integration.is_fake:
            results = []
            for camp in campaigns:
                campaign_id = camp.get("id", "unknown")
                status = camp.get("status", "unchanged")
                results.append(f"   ✅ {campaign_id} → {status}")
            
            return f"✅ Bulk update completed for {len(campaigns)} campaigns:\n" + "\n".join(results)
        
        results = []
        errors = []
        
        for camp in campaigns:
            campaign_id = camp.get("id")
            if not campaign_id:
                errors.append("Missing campaign ID in one of the campaigns")
                continue
            
            url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{campaign_id}"
            data = {}
            
            if "name" in camp:
                data["name"] = camp["name"]
            if "status" in camp:
                if camp["status"] not in ["ACTIVE", "PAUSED", "ARCHIVED"]:
                    errors.append(f"{campaign_id}: Invalid status")
                    continue
                data["status"] = camp["status"]
            if "daily_budget" in camp:
                try:
                    fb_utils.validate_budget(camp["daily_budget"])
                    data["daily_budget"] = camp["daily_budget"]
                except ValueError as e:
                    errors.append(f"{campaign_id}: {str(e)}")
                    continue
            
            if not data:
                errors.append(f"{campaign_id}: No fields to update")
                continue
            
            try:
                async def make_request():
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            url,
                            json=data,
                            headers=integration.headers,
                            timeout=30.0
                        )
                        
                        if response.status_code != 200:
                            error_msg = await fb_utils.handle_fb_api_error(response)
                            raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                        
                        return response.json()
                
                result = await fb_utils.retry_with_backoff(make_request)
                
                if result.get("success"):
                    updates = ", ".join([f"{k}={v}" for k, v in data.items()])
                    results.append(f"   ✅ {campaign_id}: {updates}")
                else:
                    errors.append(f"{campaign_id}: Update failed")
            
            except fb_utils.FacebookAPIError as e:
                errors.append(f"{campaign_id}: {e.message}")
            except Exception as e:
                errors.append(f"{campaign_id}: {str(e)}")
        
        output = f"Bulk update completed:\n\n"
        output += f"✅ Success: {len(results)}\n"
        output += f"❌ Errors: {len(errors)}\n\n"
        
        if results:
            output += "Successful updates:\n" + "\n".join(results) + "\n\n"
        
        if errors:
            output += "Errors:\n" + "\n".join(f"   ❌ {e}" for e in errors)
        
        return output
    
    except Exception as e:
        logger.warning(f"Error in bulk update: {e}", exc_info=e)
        return f"ERROR: Failed bulk update: {str(e)}"


