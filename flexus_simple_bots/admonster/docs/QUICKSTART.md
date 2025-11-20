# Quick Start Guide - Facebook Ads Integration

## Для начала работы

### 1. Прочитайте документацию
- `facebook-ads-implementation-plan.md` - полный план с разбивкой по агентам
- `facebook-api-reference.md` - справочник по API endpoints

### 2. Структура файлов

```
flexus_simple_bots/admonster/
├── docs/
│   ├── facebook-ads-implementation-plan.md    ← Главный план
│   ├── facebook-api-reference.md              ← Справочник API
│   └── QUICKSTART.md                          ← Этот файл
├── integrations/                              ← СОЗДАТЬ
│   ├── __init__.py
│   ├── fb_utils.py          [AGENT 7 - START HERE]
│   ├── fb_ad_account.py     [AGENT 1]
│   ├── fb_campaign.py       [AGENT 2]
│   ├── fb_adset.py          [AGENT 3]
│   ├── fb_creative.py       [AGENT 4]
│   ├── fb_insights.py       [AGENT 5]
│   └── fb_audience.py       [AGENT 6]
├── tests/                                     ← СОЗДАТЬ
│   ├── test_fb_utils.py
│   ├── test_fb_ad_account.py
│   ├── test_fb_campaign.py
│   └── ...
├── admonster_bot.py         ← ОБНОВИТЬ
├── admonster_prompts.py     ← ОБНОВИТЬ
└── admonster_install.py
```

### 3. Порядок разработки

#### Фаза 0: Setup (Week 1)
**Все агенты начинают здесь:**

1. **Создать структуру папок:**
```bash
cd flexus_simple_bots/admonster
mkdir -p integrations tests
touch integrations/__init__.py
```

2. **AGENT 7 создает `fb_utils.py`** - это база для всех
   - Error handling
   - Rate limiting
   - Data validation
   - Mocking для тестов

3. **Настроить Facebook App** (один раз для всех):
   - Перейти на https://developers.facebook.com/
   - Создать приложение типа "Business"
   - Получить App ID и App Secret
   - Добавить продукт "Marketing API"
   - Создать Test Ad Account в Business Settings

4. **Получить тестовые креденшалы:**
   - System User Token (долгоживущий)
   - Test Ad Account ID (act_...)
   - Test Page ID (для креативов)

#### Фаза 1: Параллельная разработка (Week 2-3)

**AGENT 1** → `fb_ad_account.py`:
```python
# Start with:
async def list_ad_accounts(integration, args):
    # List accounts
    pass

async def get_ad_account_info(integration, args):
    # Get account details
    pass

# Test with existing account first, creation later
```

**AGENT 2** → `fb_campaign.py`:
```python
# Extend existing fi_facebook.py Campaign class
async def update_campaign(integration, args):
    pass

async def duplicate_campaign(integration, args):
    pass
```

**AGENT 3** → `fb_adset.py`:
```python
# Most complex - targeting
async def create_adset(integration, args):
    # Use fb_utils.validate_targeting()
    pass

async def validate_targeting(integration, args):
    # Call /targetingsentencelines
    pass
```

**AGENT 4** → `fb_creative.py`:
```python
# Images and ads
async def upload_image(integration, args):
    pass

async def create_creative(integration, args):
    pass

async def create_ad(integration, args):
    pass
```

#### Фаза 2: Advanced (Week 4)

**AGENT 5** → `fb_insights.py`:
- Advanced breakdowns
- Export to CSV
- Scheduled reports

**AGENT 6** → `fb_audience.py`:
- Custom audiences
- Lookalikes
- Pixel management

### 4. Пример работы каждого агента

#### AGENT 7 Example (fb_utils.py)

```python
import asyncio
import hashlib
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("fb_utils")

class FacebookAPIError(Exception):
    """Facebook API errors"""
    def __init__(self, code: int, message: str, type: str = ""):
        self.code = code
        self.message = message
        self.type = type
        super().__init__(f"FB API Error {code}: {message}")


async def handle_fb_api_error(response: httpx.Response) -> str:
    """Parse and format Facebook API errors"""
    try:
        error_data = response.json()
        if "error" in error_data:
            err = error_data["error"]
            code = err.get("code", 0)
            message = err.get("message", "Unknown error")
            error_type = err.get("type", "")
            
            # Friendly messages for common errors
            if code == 190:
                return f"❌ Authentication failed. Please re-authorize Facebook access."
            elif code in [17, 32, 4]:
                return f"⏱️ Rate limit reached. Please try again in a few minutes."
            elif code == 100:
                return f"❌ Invalid parameters: {message}"
            else:
                return f"❌ Facebook API Error ({code}): {message}"
    except Exception as e:
        logger.error(f"Error parsing FB error: {e}")
        return f"❌ Facebook API Error: {response.text[:200]}"


async def retry_with_backoff(func, max_retries: int = 3):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            await asyncio.sleep(wait_time)


def validate_ad_account_id(ad_account_id: str) -> str:
    """Ensure ad_account_id has act_ prefix"""
    if not ad_account_id:
        raise ValueError("ad_account_id is required")
    if not ad_account_id.startswith("act_"):
        return f"act_{ad_account_id}"
    return ad_account_id


def validate_budget(budget: int, min_budget: int = 100) -> bool:
    """Validate budget is above minimum (in cents)"""
    if budget < min_budget:
        raise ValueError(f"Budget must be at least ${min_budget/100:.2f}")
    return True


def format_currency(cents: int, currency: str = "USD") -> str:
    """Format cents to currency string"""
    return f"${cents/100:.2f} {currency}"


def hash_for_audience(value: str, field_type: str) -> str:
    """Hash data for Custom Audiences (PII)"""
    # Normalize
    value = value.strip().lower()
    
    if field_type == "EMAIL":
        pass  # Already normalized
    elif field_type == "PHONE":
        # Remove non-digits
        value = ''.join(c for c in value if c.isdigit())
    
    # SHA256 hash
    return hashlib.sha256(value.encode()).hexdigest()


# Mock data for testing
def generate_mock_campaign() -> Dict[str, Any]:
    return {
        "id": "123456789",
        "name": "Test Campaign",
        "status": "ACTIVE",
        "objective": "OUTCOME_TRAFFIC",
        "daily_budget": 5000
    }
```

#### AGENT 1 Example (fb_ad_account.py)

```python
import logging
from typing import Dict, Any, Optional, List
import httpx
from . import fb_utils

logger = logging.getLogger("fb_ad_account")

API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"


async def handle(integration, toolcall, model_produced_args: Dict[str, Any]) -> str:
    """Router for ad account operations"""
    try:
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        
        if op == "list_ad_accounts":
            return await list_ad_accounts(integration, args)
        elif op == "get_ad_account_info":
            return await get_ad_account_info(integration, args)
        else:
            return f"Unknown ad_account operation: {op}"
    except Exception as e:
        logger.error(f"Ad account error: {e}")
        return f"ERROR: {str(e)}"


async def list_ad_accounts(integration, args: Dict[str, Any]) -> str:
    """List all ad accounts for user"""
    try:
        url = f"{API_BASE}/{API_VERSION}/me/adaccounts"
        params = {
            "fields": "id,account_id,name,currency,timezone_name,account_status,spend_cap",
            "limit": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=integration.headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                return await fb_utils.handle_fb_api_error(response)
            
            data = response.json()
            accounts = data.get("data", [])
            
            if not accounts:
                return "No ad accounts found."
            
            result = f"Found {len(accounts)} ad accounts:\n\n"
            for acc in accounts:
                result += f"📊 {acc['name']}\n"
                result += f"   ID: {acc['id']}\n"
                result += f"   Currency: {acc['currency']}\n"
                result += f"   Status: {acc['account_status']}\n"
                if 'spend_cap' in acc:
                    result += f"   Spend Cap: ${int(acc['spend_cap'])/100:.2f}\n"
                result += "\n"
            
            return result
    
    except Exception as e:
        logger.error(f"Error listing ad accounts: {e}")
        return f"ERROR: {str(e)}"


async def get_ad_account_info(integration, args: Dict[str, Any]) -> str:
    """Get detailed info about specific ad account"""
    try:
        ad_account_id = args.get("ad_account_id", "")
        if not ad_account_id:
            return "ERROR: ad_account_id is required"
        
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
        
        url = f"{API_BASE}/{API_VERSION}/{ad_account_id}"
        params = {
            "fields": "id,account_id,name,currency,timezone_name,account_status,balance,spend_cap,amount_spent,business,funding_source_details"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers=integration.headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                return await fb_utils.handle_fb_api_error(response)
            
            acc = response.json()
            
            result = f"Ad Account: {acc['name']}\n"
            result += f"ID: {acc['id']}\n"
            result += f"Currency: {acc['currency']}\n"
            result += f"Status: {acc['account_status']}\n"
            result += f"Balance: ${int(acc.get('balance', 0))/100:.2f}\n"
            result += f"Amount Spent: ${int(acc.get('amount_spent', 0))/100:.2f}\n"
            
            if 'spend_cap' in acc:
                result += f"Spend Cap: ${int(acc['spend_cap'])/100:.2f}\n"
            
            return result
    
    except Exception as e:
        logger.error(f"Error getting ad account info: {e}")
        return f"ERROR: {str(e)}"
```

### 5. Testing Strategy

#### Unit Tests
```python
# tests/test_fb_utils.py
import pytest
from admonster.integrations import fb_utils

def test_validate_ad_account_id():
    assert fb_utils.validate_ad_account_id("123") == "act_123"
    assert fb_utils.validate_ad_account_id("act_123") == "act_123"

def test_format_currency():
    assert fb_utils.format_currency(5000) == "$50.00 USD"

def test_hash_for_audience():
    email = "test@example.com"
    hashed = fb_utils.hash_for_audience(email, "EMAIL")
    assert len(hashed) == 64  # SHA256
```

#### Integration Tests
```python
# tests/test_fb_ad_account.py
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_list_ad_accounts():
    integration = Mock()
    integration.headers = {"Authorization": "Bearer test_token"}
    
    # Mock httpx response
    # Test the function
    # Assert expected output
```

### 6. Integration Points

#### Update admonster_bot.py
```python
# Import new modules
from flexus_simple_bots.admonster.integrations import (
    fb_ad_account,
    fb_campaign,
    fb_adset,
    fb_creative,
    fb_insights,
    fb_audience,
)

# Update tool handler
@rcx.on_tool_call(fi_facebook.FACEBOOK_TOOL.name)
async def toolcall_facebook(toolcall, model_produced_args):
    try:
        op = model_produced_args.get("op", "")
        
        # Route to appropriate module
        if op.startswith("list_ad_accounts") or op.startswith("get_ad_account"):
            return await fb_ad_account.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("create_adset") or op.startswith("update_adset"):
            return await fb_adset.handle(facebook_integration, toolcall, model_produced_args)
        # ... other routes ...
        else:
            # Fallback to existing integration
            return await facebook_integration.called_by_model(toolcall, model_produced_args)
    
    except Exception as e:
        logger.error(f"Facebook tool error: {e}")
        return f"ERROR: {str(e)}"
```

### 7. Checklist for Each Agent

- [ ] Create module file with basic structure
- [ ] Implement main operations (create, list, update)
- [ ] Add error handling (use fb_utils)
- [ ] Write unit tests
- [ ] Test with real Facebook API (Test Ad Account)
- [ ] Update admonster_bot.py routing
- [ ] Update admonster_prompts.py with new operations
- [ ] Document any gotchas or issues

### 8. Common Issues & Solutions

**Issue:** "Invalid OAuth token"
**Solution:** Re-authenticate, check token expiration

**Issue:** "Rate limit exceeded"
**Solution:** Implement rate limiter in fb_utils, use batch requests

**Issue:** "Budget too low"
**Solution:** Minimum daily budget is $1.00 (100 cents)

**Issue:** "Targeting spec invalid"
**Solution:** Use validate_targeting before creating ad set

**Issue:** "Special ad category required"
**Solution:** Check if campaign needs special_ad_categories (housing, credit, employment)

### 9. Resources

- **Facebook Docs:** https://developers.facebook.com/docs/marketing-api
- **Python Business SDK:** https://github.com/facebook/facebook-python-business-sdk
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer
- **Test Ad Accounts:** Create in Business Settings

### 10. Getting Help

If stuck:
1. Check `facebook-api-reference.md` for API details
2. Check `facebook-ads-implementation-plan.md` for architecture
3. Review existing `fi_facebook.py` for patterns
4. Test in Graph API Explorer first
5. Check Facebook API changelog for breaking changes

---

**Ready to start? Begin with AGENT 7 (fb_utils.py) and work your way through!**

Good luck! 🚀


