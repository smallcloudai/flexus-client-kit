"""
Facebook Ad Account Management

Handles operations related to Facebook Ad Accounts:
- List ad accounts
- Get ad account details
- Update account settings
- Manage spending limits
"""

import logging
from typing import Dict, Any, Optional, List

import httpx

from flexus_simple_bots.admonster.integrations import fb_utils

logger = logging.getLogger("fb_ad_account")


def _format_account(acc: Dict[str, Any]) -> str:
    """Format a single ad account for display"""
    account_status = acc.get("account_status", 1)
    status_text = "Active" if account_status == 1 else "Disabled" if account_status == 2 else f"Status {account_status}"
    
    result = f"   📊 {acc.get('name', 'Unnamed')}\n"
    result += f"      ID: {acc['id']}\n"
    result += f"      Currency: {acc.get('currency', 'N/A')}\n"
    result += f"      Timezone: {acc.get('timezone_name', 'N/A')}\n"
    result += f"      Status: {status_text}\n"
    
    if 'balance' in acc:
        result += f"      Balance: {fb_utils.format_currency(int(acc['balance']), acc.get('currency', 'USD'))}\n"
    if 'amount_spent' in acc:
        result += f"      Total Spent: {fb_utils.format_currency(int(acc['amount_spent']), acc.get('currency', 'USD'))}\n"
    if 'spend_cap' in acc and int(acc.get('spend_cap', 0)) > 0:
        result += f"      Spend Cap: {fb_utils.format_currency(int(acc['spend_cap']), acc.get('currency', 'USD'))}\n"
    
    result += "\n"
    return result


async def handle(integration, toolcall, model_produced_args: Dict[str, Any]) -> str:
    """Router for ad account operations"""
    try:
        auth_error = await integration.ensure_headers()
        if auth_error:
            return auth_error
        
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        # Merge top-level params into args (model may pass them at top level)
        for key in ["ad_account_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]
        
        if op == "list_ad_accounts":
            return await list_ad_accounts(integration, args)
        elif op == "get_ad_account_info":
            return await get_ad_account_info(integration, args)
        elif op == "update_spending_limit":
            return await update_spending_limit(integration, args)
        else:
            return f"Unknown ad_account operation: {op}\n\nAvailable operations:\n- list_ad_accounts\n- get_ad_account_info\n- update_spending_limit"
    
    except fb_utils.FacebookAPIError as e:
        logger.error(f"Facebook API error in ad_account: {e}", exc_info=e)
        return f"❌ Facebook API Error: {e.message}"
    except Exception as e:
        logger.error(f"Ad account error: {e}", exc_info=e)
        return f"ERROR: {str(e)}"


async def list_ad_accounts(integration, args: Dict[str, Any]) -> str:
    """List all ad accounts accessible by the authenticated user, grouped by portfolio"""
    try:
        if integration.is_fake:
            mock_account = fb_utils.generate_mock_ad_account()
            return f"""Found 1 ad account:

📊 {mock_account['name']}
   ID: {mock_account['id']}
   Currency: {mock_account['currency']}
   Status: Active
   Balance: ${int(mock_account['balance'])/100:.2f}
   Spend Cap: ${int(mock_account['spend_cap'])/100:.2f}
"""
        
        url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/me/adaccounts"
        params = {
            "fields": "id,account_id,name,currency,timezone_name,account_status,balance,amount_spent,spend_cap,business{id,name}",
            "limit": 50
        }
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        data = await fb_utils.retry_with_backoff(make_request)
        accounts = data.get("data", [])
        
        if not accounts:
            return "No ad accounts found. You may need to:\n1. Create an ad account in Facebook Business Manager\n2. Ensure you have proper permissions"
        
        # Group accounts by business portfolio
        business_accounts: Dict[str, List[Any]] = {}  # business_name -> accounts
        personal_accounts: List[Any] = []
        
        for acc in accounts:
            business = acc.get("business")
            if business:
                biz_name = business.get("name", f"Business {business.get('id', 'Unknown')}")
                if biz_name not in business_accounts:
                    business_accounts[biz_name] = []
                business_accounts[biz_name].append(acc)
            else:
                personal_accounts.append(acc)
        
        result = f"Found {len(accounts)} ad account{'s' if len(accounts) != 1 else ''}:\n\n"
        
        # Display business portfolio accounts
        for biz_name, biz_accounts in business_accounts.items():
            result += f"🏢 **Business Portfolio: {biz_name}** ({len(biz_accounts)} account{'s' if len(biz_accounts) != 1 else ''})\n\n"
            for acc in biz_accounts:
                result += _format_account(acc)
        
        # Display personal accounts
        if personal_accounts:
            result += f"👤 **Personal Account** ({len(personal_accounts)} account{'s' if len(personal_accounts) != 1 else ''})\n\n"
            for acc in personal_accounts:
                result += _format_account(acc)
        
        return result
    
    except fb_utils.FacebookAPIError:
        raise
    except Exception as e:
        logger.error(f"Error listing ad accounts: {e}", exc_info=e)
        return f"ERROR: Failed to list ad accounts: {str(e)}"


async def get_ad_account_info(integration, args: Dict[str, Any]) -> str:
    """Get detailed information about a specific ad account"""
    try:
        ad_account_id = args.get("ad_account_id", "")
        if not ad_account_id:
            return "ERROR: ad_account_id parameter is required\n\nExample: facebook(op=\"get_ad_account_info\", args={\"ad_account_id\": \"act_123456\"})"
        
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
        
        if integration.is_fake:
            mock_account = fb_utils.generate_mock_ad_account()
            mock_account['id'] = ad_account_id
            return f"""Ad Account Details:

📊 {mock_account['name']}
   ID: {mock_account['id']}
   Account ID: {mock_account['account_id']}
   Currency: {mock_account['currency']}
   Timezone: {mock_account['timezone_name']}
   Status: Active
   
💰 Financial Info:
   Balance: ${int(mock_account['balance'])/100:.2f}
   Total Spent: ${int(mock_account['amount_spent'])/100:.2f}
   Spend Cap: ${int(mock_account['spend_cap'])/100:.2f}
   Remaining: ${(int(mock_account['spend_cap']) - int(mock_account['amount_spent']))/100:.2f}
"""
        
        url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}"
        params = {
            "fields": "id,account_id,name,currency,timezone_name,account_status,balance,amount_spent,spend_cap,business,funding_source_details,min_daily_budget,created_time"
        }
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=integration.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                
                return response.json()
        
        acc = await fb_utils.retry_with_backoff(make_request)
        
        account_status = acc.get("account_status", 1)
        status_text = "Active" if account_status == 1 else "Disabled" if account_status == 2 else f"Status {account_status}"
        
        result = "Ad Account Details:\n\n"
        result += f"📊 {acc['name']}\n"
        result += f"   ID: {acc['id']}\n"
        result += f"   Account ID: {acc.get('account_id', 'N/A')}\n"
        result += f"   Currency: {acc['currency']}\n"
        result += f"   Timezone: {acc.get('timezone_name', 'N/A')}\n"
        result += f"   Status: {status_text}\n"
        result += f"   Created: {acc.get('created_time', 'N/A')}\n"
        
        result += "\n💰 Financial Info:\n"
        balance = int(acc.get('balance', 0))
        amount_spent = int(acc.get('amount_spent', 0))
        spend_cap = int(acc.get('spend_cap', 0))
        
        result += f"   Balance: {fb_utils.format_currency(balance, acc['currency'])}\n"
        result += f"   Total Spent: {fb_utils.format_currency(amount_spent, acc['currency'])}\n"
        
        if spend_cap > 0:
            result += f"   Spend Cap: {fb_utils.format_currency(spend_cap, acc['currency'])}\n"
            remaining = spend_cap - amount_spent
            result += f"   Remaining: {fb_utils.format_currency(remaining, acc['currency'])}\n"
            
            percent_used = (amount_spent / spend_cap) * 100 if spend_cap > 0 else 0
            if percent_used > 90:
                result += f"   ⚠️ Warning: {percent_used:.1f}% of spend cap used!\n"
        
        if 'min_daily_budget' in acc:
            result += f"   Min Daily Budget: {fb_utils.format_currency(int(acc['min_daily_budget']), acc['currency'])}\n"
        
        if 'business' in acc:
            business = acc['business']
            result += f"\n🏢 Business: {business.get('name', 'N/A')} (ID: {business.get('id', 'N/A')})\n"
        
        return result
    
    except fb_utils.FacebookAPIError:
        raise
    except ValueError as e:
        return f"ERROR: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting ad account info: {e}", exc_info=e)
        return f"ERROR: Failed to get ad account info: {str(e)}"


async def update_spending_limit(integration, args: Dict[str, Any]) -> str:
    """Update spending limit for an ad account"""
    try:
        ad_account_id = args.get("ad_account_id", "")
        spending_limit = args.get("spending_limit")
        
        if not ad_account_id:
            return "ERROR: ad_account_id parameter is required"
        
        if spending_limit is None:
            return "ERROR: spending_limit parameter is required (in cents)\n\nExample: facebook(op=\"update_spending_limit\", args={\"ad_account_id\": \"act_123\", \"spending_limit\": 100000})"
        
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
        spending_limit = int(spending_limit)
        
        if spending_limit < 0:
            return "ERROR: spending_limit must be a positive number"
        
        if integration.is_fake:
            return f"✅ Spending limit updated to {fb_utils.format_currency(spending_limit)} for account {ad_account_id}\n\n(Note: This is a test/mock operation)"
        
        url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}"
        data = {
            "spend_cap": spending_limit
        }
        
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
            return f"✅ Spending limit updated to {fb_utils.format_currency(spending_limit)} for account {ad_account_id}"
        else:
            return f"❌ Failed to update spending limit. Response: {result}"
    
    except fb_utils.FacebookAPIError:
        raise
    except ValueError as e:
        return f"ERROR: {str(e)}"
    except Exception as e:
        logger.error(f"Error updating spending limit: {e}", exc_info=e)
        return f"ERROR: Failed to update spending limit: {str(e)}"


