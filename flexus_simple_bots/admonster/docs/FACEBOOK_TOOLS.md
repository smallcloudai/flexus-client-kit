# Facebook Tools Reference

Available `facebook()` tool operations for the admonster bot.

**Legend:**
- ✅ Implemented & Tested
- 🔧 Implemented, needs testing
- ⚠️ Implemented, blocked by external constraints
- ⬜ Not implemented

---

## Ad Account Operations

Source: `fb_ad_account.py`

### list_ad_accounts ✅

List all ad accounts, grouped by business portfolio and personal.

**Request:**
```
facebook(op="list_ad_accounts")
```

**Response:**
```
Found 3 ad accounts:

🏢 **Business Portfolio: My Agency** (2 accounts)

   📊 Client Project Alpha
      ID: act_111222333444
      Currency: USD
      Status: Active
      ...

👤 **Personal Account** (1 account)

   📊 My Personal Ads
      ID: act_555666777888
      ...
```

---

### get_ad_account_info ✅

Get detailed info about a specific ad account.

**Request:**
```
facebook(op="get_ad_account_info", args={"ad_account_id": "act_111222333444"})
```

**Response:**
```
Ad Account Details:

📊 Client Project Alpha
   ID: act_111222333444
   Currency: USD
   Timezone: America/New_York
   Status: Active
   Created: 2024-01-15

💰 Financial Info:
   Balance: 0.00 USD
   Total Spent: 1500.00 USD
   Spend Cap: 10000.00 USD
   Remaining: 8500.00 USD

🏢 Business: My Agency (ID: 999888777)
```

---

### update_spending_limit ⚠️

Update the spending cap for an ad account.

**Request:**
```
facebook(op="update_spending_limit", args={
    "ad_account_id": "act_111222333444",
    "spending_limit": 500000
})
```
Note: `spending_limit` is in cents (500000 = 5000.00)

**Status:** Requires active ad account with billing configured. May fail on restricted/old accounts.

**Response:**
```
✅ Spending limit updated to 5000.00 USD for account act_111222333444
```

---

## Campaign Operations (Core)

Source: `fi_facebook.py`

### status 🔧

Show current ad account status and active campaigns.

**Request:**
```
facebook(op="status")
```

**Response:**
```
Facebook Ads Account: act_111222333444

Active Campaigns (2):
  📊 Summer Sale (ID: 23456789)
     Status: ACTIVE, Objective: OUTCOME_TRAFFIC, Daily Budget: 50.00
  📊 New Product Launch (ID: 23456790)
     Status: ACTIVE, Objective: OUTCOME_SALES, Daily Budget: 100.00
```

---

### list_campaigns 🔧

List campaigns with optional status filter.

**Request:**
```
facebook(op="list_campaigns")
facebook(op="list_campaigns", args={"status": "ACTIVE"})
facebook(op="list_campaigns", args={"status": "PAUSED"})
```

**Response:**
```
Found 5 campaigns:
  Summer Sale (ID: 123) - ACTIVE
  Winter Promo (ID: 456) - PAUSED
  ...
```

---

### create_campaign 🔧

Create a new campaign.

**Request:**
```
facebook(op="create_campaign", args={
    "name": "My New Campaign",
    "objective": "OUTCOME_TRAFFIC",
    "daily_budget": 5000,
    "status": "PAUSED"
})
```
Note: `daily_budget` in cents. Valid objectives: OUTCOME_TRAFFIC, OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_AWARENESS, OUTCOME_LEADS, OUTCOME_APP_PROMOTION

**Response:**
```
✅ Campaign created: My New Campaign (ID: 789)
   Status: PAUSED, Objective: OUTCOME_TRAFFIC
```

---

### get_insights 🔧

Get performance metrics for a campaign.

**Request:**
```
facebook(op="get_insights", args={
    "campaign_id": "123456",
    "days": 30
})
```

**Response:**
```
Insights for Campaign 123456 (Last 30 days):
  Impressions: 125,000
  Clicks: 3,450
  Spend: 500.00
  CTR: 2.76%
  CPC: 0.14
```

---

## Campaign Operations (Extended)

Source: `fb_campaign.py`

### update_campaign 🔧

Update campaign settings.

**Request:**
```
facebook(op="update_campaign", args={
    "campaign_id": "123",
    "name": "Updated Name",
    "status": "PAUSED",
    "daily_budget": 7500
})
```

---

### duplicate_campaign 🔧

Duplicate an existing campaign.

**Request:**
```
facebook(op="duplicate_campaign", args={
    "campaign_id": "123",
    "new_name": "Copy of Campaign"
})
```

---

### archive_campaign 🔧

Archive (soft delete) a campaign.

**Request:**
```
facebook(op="archive_campaign", args={"campaign_id": "123"})
```

---

### bulk_update_campaigns 🔧

Update multiple campaigns at once.

**Request:**
```
facebook(op="bulk_update_campaigns", args={
    "campaign_ids": ["123", "456", "789"],
    "status": "PAUSED"
})
```

---

## Ad Set Operations

Source: `fb_adset.py`

### list_adsets 🔧

List ad sets for a campaign.

**Request:**
```
facebook(op="list_adsets", args={"campaign_id": "123"})
```

---

### create_adset 🔧

Create ad set with targeting.

**Request:**
```
facebook(op="create_adset", args={
    "campaign_id": "123",
    "name": "US 18-35 Interest",
    "daily_budget": 2000,
    "targeting": {
        "geo_locations": {"countries": ["US"]},
        "age_min": 18,
        "age_max": 35
    }
})
```

---

### update_adset 🔧

Update ad set settings.

**Request:**
```
facebook(op="update_adset", args={
    "adset_id": "456",
    "daily_budget": 3000,
    "status": "ACTIVE"
})
```

---

### validate_targeting 🔧

Validate targeting spec and get audience estimate.

**Request:**
```
facebook(op="validate_targeting", args={
    "targeting": {
        "geo_locations": {"countries": ["US", "CA"]},
        "age_min": 25,
        "age_max": 45,
        "interests": [{"id": "6003139266461", "name": "Technology"}]
    }
})
```

---

## Creative & Ads Operations

Source: `fb_creative.py`

### upload_image 🔧

Upload an image for use in ads.

**Request:**
```
facebook(op="upload_image", args={
    "image_url": "https://example.com/product.jpg"
})
```

**Response:**
```
✅ Image uploaded successfully
   Hash: abc123def456
   Use this hash in create_creative
```

---

### create_creative 🔧

Create an ad creative.

**Request:**
```
facebook(op="create_creative", args={
    "name": "Product Creative",
    "image_hash": "abc123def456",
    "link": "https://example.com/product",
    "message": "Check out our new product!",
    "headline": "New Arrival",
    "call_to_action": "SHOP_NOW"
})
```

---

### create_ad 🔧

Create an ad using creative and ad set.

**Request:**
```
facebook(op="create_ad", args={
    "adset_id": "456",
    "creative_id": "789",
    "name": "Product Ad v1",
    "status": "PAUSED"
})
```

---

### preview_ad 🔧

Get HTML preview of an ad.

**Request:**
```
facebook(op="preview_ad", args={"creative_id": "789"})
```

---

## Utility

### help 🔧

Show available operations.

**Request:**
```
facebook(op="help")
```

---

## Notes

- All budget values are in **cents** (5000 = 50.00 in currency)
- Ad account IDs must start with `act_`
- Write operations default to **PAUSED** status for safety
- Campaign objectives: OUTCOME_TRAFFIC, OUTCOME_SALES, OUTCOME_ENGAGEMENT, OUTCOME_AWARENESS, OUTCOME_LEADS, OUTCOME_APP_PROMOTION

