# Facebook Ads Integration

A comprehensive integration for Facebook Marketing API with type-safe Pydantic models, authenticated HTTP client with retry logic, and full CRUD operations for campaigns, ad sets, ads, and creatives.

## Features

- **Type-safe models** - Pydantic models with validation for all Facebook Ads entities
- **Authenticated client** - OAuth token management with automatic retry logic
- **Full operations** - CRUD for campaigns, ad sets, creatives, and ads
- **Test mode** - Built-in mock support for testing without hitting Facebook API
- **Error handling** - User-friendly error messages with rate limit handling

## Quick Start

```python
from flexus_client_kit.integrations.facebook import (
    IntegrationFacebook,
    FACEBOOK_TOOL,
    Campaign,
    CampaignObjective,
)

# In your bot initialization:
fb = IntegrationFacebook(fclient, rcx, ad_account_id="act_123456")

# Handle tool calls from AI model:
result = await fb.called_by_model(toolcall, {"op": "status"})
```

## Architecture

```
facebook/
├── __init__.py          # Public API, IntegrationFacebook class
├── client.py            # FacebookAdsClient HTTP client
├── models.py            # Pydantic models (Campaign, AdSet, Ad, etc.)
├── exceptions.py        # Custom exceptions
├── utils.py             # Validation and formatting utilities
├── operations/          # Operation modules
│   ├── accounts.py      # Ad account operations
│   ├── campaigns.py     # Campaign operations
│   ├── adsets.py        # Ad set operations
│   └── ads.py           # Creative and ad operations
├── testing/             # Test utilities
│   └── mocks.py         # Mock data generators
├── tests/               # Unit tests
└── docs/                # Documentation
```

## Available Operations

### Account Operations
- `list_ad_accounts` - List all accessible ad accounts
- `get_ad_account_info` - Get detailed account info
- `update_spending_limit` - Set account spend cap

### Campaign Operations
- `list_campaigns` - List campaigns with optional status filter
- `create_campaign` - Create new campaign
- `update_campaign` - Update campaign settings
- `duplicate_campaign` - Copy existing campaign
- `archive_campaign` - Soft-delete campaign
- `bulk_update_campaigns` - Update multiple campaigns
- `get_insights` - Get performance metrics

### Ad Set Operations
- `list_adsets` - List ad sets for a campaign
- `create_adset` - Create ad set with targeting
- `update_adset` - Update ad set settings
- `validate_targeting` - Validate targeting spec

### Ad Operations
- `upload_image` - Upload image for creative
- `create_creative` - Create ad creative
- `create_ad` - Create ad from creative
- `preview_ad` - Generate ad preview

## Models

All models use Pydantic with validation:

```python
from flexus_client_kit.integrations.facebook import (
    Campaign,
    CampaignObjective,
    CampaignStatus,
    AdSet,
    TargetingSpec,
    GeoLocation,
)

# Create a campaign with validation
campaign = Campaign(
    name="Summer Sale 2025",
    objective=CampaignObjective.TRAFFIC,
    status=CampaignStatus.PAUSED,
    daily_budget=5000,  # cents ($50.00)
)

# Create targeting spec
targeting = TargetingSpec(
    geo_locations=GeoLocation(countries=["US", "CA"]),
    age_min=25,
    age_max=45,
)
```

## Testing

Use the mock client for testing without hitting Facebook API:

```python
from flexus_client_kit.integrations.facebook.testing import (
    MockFacebookClient,
    generate_mock_campaign,
)

# Create mock client
client = MockFacebookClient(ad_account_id="act_test")

# Generate mock data
campaign = generate_mock_campaign(
    name="Test Campaign",
    daily_budget=5000,
)
```

Run tests:
```bash
pytest flexus_client_kit/integrations/facebook/tests/
```

## Error Handling

The integration provides user-friendly error handling:

```python
from flexus_client_kit.integrations.facebook import (
    FacebookAPIError,
    FacebookValidationError,
    FacebookRateLimitError,
)

try:
    result = await operations.create_campaign(client, ...)
except FacebookAPIError as e:
    print(e.format_for_user())  # User-friendly message
except FacebookValidationError as e:
    print(f"Validation error: {e.message}")
```

## Budget Values

All budget values are in **cents**:
- `5000` = $50.00
- `100` = $1.00 (minimum for most operations)

## See Also

- [operations.md](operations.md) - Detailed operation documentation
- [api-reference.md](api-reference.md) - Facebook API reference
