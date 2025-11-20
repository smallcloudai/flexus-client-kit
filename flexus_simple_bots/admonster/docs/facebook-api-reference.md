# Facebook Marketing API Reference

## Quick Reference

**Base URL:** `https://graph.facebook.com/v19.0`  
**Auth:** Bearer token в query parameter `access_token` или в header

---

## Ad Account

### List Ad Accounts
```
GET /me/adaccounts
Fields: id, account_id, name, currency, timezone_name, account_status, spend_cap
```

### Get Ad Account Details
```
GET /{ad_account_id}
Fields: все поля + balance, business, funding_source_details
```

### Create Ad Account (requires Business Manager)
```
POST /{business_id}/adaccounts
Body: {
  "name": "Account Name",
  "currency": "USD",
  "timezone_id": 1,  // См. timezone list
  "end_advertiser": "{end_advertiser_id}",
  "media_agency": "{media_agency_id}",  // optional
  "partner": "{partner_id}"  // optional
}
```

---

## Campaigns

### List Campaigns
```
GET /{ad_account_id}/campaigns
Fields: id, name, objective, status, daily_budget, lifetime_budget, created_time, updated_time
Filters: effective_status=[ACTIVE, PAUSED, DELETED, ARCHIVED]
```

### Create Campaign
```
POST /{ad_account_id}/campaigns
Body: {
  "name": "Campaign Name",
  "objective": "OUTCOME_TRAFFIC",  // См. objectives ниже
  "status": "PAUSED",  // ACTIVE, PAUSED
  "daily_budget": 5000,  // cents, optional (либо daily либо lifetime)
  "lifetime_budget": 100000,  // cents, optional
  "special_ad_categories": [],  // ["HOUSING", "CREDIT", "EMPLOYMENT"] для специальных категорий
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"  // optional
}
```

**Valid Objectives:**
- `OUTCOME_TRAFFIC` - Website visits
- `OUTCOME_ENGAGEMENT` - Post engagement
- `OUTCOME_AWARENESS` - Brand awareness
- `OUTCOME_LEADS` - Lead generation
- `OUTCOME_SALES` - Conversions/Sales
- `OUTCOME_APP_PROMOTION` - App installs

### Update Campaign
```
POST /{campaign_id}
Body: { "status": "PAUSED", "name": "New Name", "daily_budget": 7500 }
```

### Delete Campaign
```
DELETE /{campaign_id}
```

---

## Ad Sets

### List Ad Sets
```
GET /{campaign_id}/adsets
Fields: id, name, campaign_id, status, daily_budget, lifetime_budget, optimization_goal, billing_event, bid_amount, targeting
```

### Create Ad Set
```
POST /{ad_account_id}/adsets
Body: {
  "name": "Ad Set Name",
  "campaign_id": "{campaign_id}",
  "optimization_goal": "LINK_CLICKS",  // См. optimization goals
  "billing_event": "IMPRESSIONS",  // или LINK_CLICKS, etc
  "bid_amount": 150,  // cents (optional, автоматическое если не указано)
  "daily_budget": 5000,  // cents
  "status": "PAUSED",
  "start_time": "2025-01-01T00:00:00+0000",  // ISO 8601
  "end_time": "2025-12-31T23:59:59+0000",  // optional
  "targeting": {
    "geo_locations": {
      "countries": ["US"],
      "regions": [{"key": "3847"}],  // optional, см. geo targeting
      "cities": [{"key": "2418779", "radius": 10, "distance_unit": "mile"}]  // optional
    },
    "age_min": 18,
    "age_max": 65,
    "genders": [1],  // 1=male, 2=female
    "interests": [{"id": "6003139266461", "name": "Technology"}],  // см. interest search
    "behaviors": [],
    "life_events": [],
    "device_platforms": ["mobile", "desktop"],  // "mobile", "desktop", "connected_tv"
    "publisher_platforms": ["facebook", "instagram", "messenger", "audience_network"],
    "facebook_positions": ["feed", "right_hand_column", "instant_article", "instream_video", "marketplace"],
    "instagram_positions": ["stream", "story", "explore"],
    "messenger_positions": ["messenger_home"]
  },
  "promoted_object": {  // для некоторых objectives
    "pixel_id": "{pixel_id}",
    "custom_event_type": "PURCHASE"
  }
}
```

**Optimization Goals:**
- `REACH` - Maximize reach
- `IMPRESSIONS` - Maximize impressions
- `LINK_CLICKS` - Link clicks
- `LANDING_PAGE_VIEWS` - Landing page views
- `OFFSITE_CONVERSIONS` - Conversions
- `POST_ENGAGEMENT` - Post engagement
- `VIDEO_VIEWS` - Video views (3sec)
- `THRUPLAY` - Video views (15sec or complete)

**Billing Events:**
- `IMPRESSIONS`
- `LINK_CLICKS`
- `POST_ENGAGEMENT`
- `THRUPLAY`

### Update Ad Set
```
POST /{adset_id}
Body: { "status": "ACTIVE", "daily_budget": 7500 }
```

### Validate Targeting
```
GET /{ad_account_id}/targetingsentencelines
Params: targeting_spec={JSON encoding of targeting object}
Returns: Human-readable description of targeting + estimated audience size
```

---

## Creatives & Ads

### Upload Image
```
POST /{ad_account_id}/adimages
Body (multipart/form-data): {
  "filename": file bytes
}
Returns: {"images": {"filename.jpg": {"hash": "abc123"}}}
```

### Create Creative
```
POST /{ad_account_id}/adcreatives
Body: {
  "name": "Creative Name",
  "object_story_spec": {
    "page_id": "{page_id}",
    "link_data": {
      "image_hash": "abc123",  // from upload_image
      "link": "https://example.com",
      "message": "Ad text here",
      "name": "Headline",  // optional
      "description": "Description",  // optional
      "call_to_action": {
        "type": "SHOP_NOW"  // LEARN_MORE, SIGN_UP, DOWNLOAD, etc
      }
    }
  },
  "degrees_of_freedom_spec": {  // optional, для dynamic creative
    "creative_features_spec": {
      "standard_enhancements": {
        "enroll_status": "OPT_IN"
      }
    }
  }
}

// Для video
"object_story_spec": {
  "page_id": "{page_id}",
  "video_data": {
    "video_id": "{video_id}",  // from video upload
    "message": "Video ad text",
    "call_to_action": {"type": "LEARN_MORE", "value": {"link": "https://..."}}
  }
}

// Для carousel
"object_story_spec": {
  "page_id": "{page_id}",
  "link_data": {
    "link": "https://example.com",
    "child_attachments": [
      {
        "link": "https://example.com/product1",
        "image_hash": "hash1",
        "name": "Product 1",
        "description": "Description 1",
        "call_to_action": {"type": "SHOP_NOW"}
      },
      {
        "link": "https://example.com/product2",
        "image_hash": "hash2",
        "name": "Product 2",
        "description": "Description 2"
      }
    ]
  }
}
```

**Call to Action Types:**
- `SHOP_NOW`, `LEARN_MORE`, `SIGN_UP`, `DOWNLOAD`, `WATCH_MORE`, `CONTACT_US`, `APPLY_NOW`, `BOOK_TRAVEL`, `GET_OFFER`, `SUBSCRIBE`, `INSTALL_APP`, `USE_APP`

### Create Ad
```
POST /{ad_account_id}/ads
Body: {
  "name": "Ad Name",
  "adset_id": "{adset_id}",
  "creative": {"creative_id": "{creative_id}"},
  "status": "PAUSED"  // ACTIVE, PAUSED
}
```

### Preview Ad
```
GET /{ad_id}/previews
Params: ad_format=DESKTOP_FEED_STANDARD
Formats: DESKTOP_FEED_STANDARD, MOBILE_FEED_STANDARD, INSTAGRAM_STANDARD, etc
Returns: {"data": [{"body": "<html>..."}]}
```

---

## Insights (Analytics)

### Get Insights
```
GET /{object_id}/insights
Params:
  level=campaign|adset|ad
  date_preset=today|yesterday|last_7d|last_14d|last_30d|this_month|last_month|maximum
  time_range={"since":"2025-01-01","until":"2025-01-31"}
  time_increment=1  // days, or "monthly", "all_days"
  breakdowns=age,gender,placement,device_platform,publisher_platform  // comma-separated
  fields=impressions,clicks,spend,reach,frequency,ctr,cpc,cpm,cpp,actions,cost_per_action_type,conversions

Returns: {
  "data": [{
    "impressions": "12345",
    "clicks": "567",
    "spend": "123.45",
    "ctr": "4.59",
    "cpc": "0.22",
    "actions": [
      {"action_type": "link_click", "value": "567"},
      {"action_type": "page_engagement", "value": "123"}
    ],
    "date_start": "2025-01-01",
    "date_stop": "2025-01-31"
  }]
}
```

**Breakdowns:**
- `age` - Age ranges (18-24, 25-34, etc)
- `gender` - Male/Female/Unknown
- `country` - Country
- `region` - State/Province
- `dma` - Designated Market Area (US)
- `placement` - Where ad showed (feed, story, etc)
- `device_platform` - Mobile/Desktop
- `publisher_platform` - Facebook/Instagram/Messenger/Audience Network
- `impression_device` - Device type

**Action Types:**
- `link_click` - Link clicks
- `post_engagement` - Post engagement
- `page_engagement` - Page engagement
- `post` - Post shares
- `video_view` - Video views
- `offsite_conversion` - Website conversions
- `onsite_conversion.purchase` - Purchases

### Async Reporting (for large datasets)
```
POST /{ad_account_id}/insights
Body: same as GET params
Returns: {"report_run_id": "123"}

GET /{ad_account_id}/insights  // check status
Params: report_run_id=123
Returns: {"async_status": "Job Completed", "async_percent_completion": 100}

GET /{report_run_id}/insights  // get results
```

---

## Custom Audiences

### Create Custom Audience
```
POST /{ad_account_id}/customaudiences
Body: {
  "name": "Website Visitors",
  "subtype": "WEBSITE",  // CUSTOM, LOOKALIKE, WEBSITE, APP, OFFLINE_CONVERSION, ENGAGEMENT, etc
  "description": "People who visited website",
  "customer_file_source": "USER_PROVIDED_ONLY",  // or "PARTNER_PROVIDED_ONLY", "BOTH_USER_AND_PARTNER_PROVIDED"
  "retention_days": 180  // optional, how long to keep users
}

// For pixel-based
Body: {
  "name": "Pixel Audience",
  "subtype": "WEBSITE",
  "rule": {
    "url": {"i_contains": "product"}  // visited URL containing "product"
  },
  "pixel_id": "{pixel_id}",
  "retention_days": 30
}
```

### Add Users to Custom Audience
```
POST /{custom_audience_id}/users
Body: {
  "schema": ["EMAIL", "PHONE"],  // or FN, LN, ZIP, CT, ST, COUNTRY, DOBY, DOBM, DOBD, GEN, MADID, etc
  "data": [
    ["email1@example.com", "1234567890"],  // Already hashed with SHA256 + lowercase + trim
    ["email2@example.com", "0987654321"]
  ]
}

Note: Data must be normalized and hashed:
1. Lowercase
2. Trim whitespace
3. SHA256 hash
4. For phone: remove +, -, (), spaces; include country code
```

### Remove Users from Audience
```
DELETE /{custom_audience_id}/users
Body: same as add
```

### Create Lookalike Audience
```
POST /{ad_account_id}/customaudiences
Body: {
  "name": "Lookalike 1%",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "{custom_audience_id}",
  "lookalike_spec": {
    "type": "SIMILARITY",
    "ratio": 0.01,  // 1% (0.01 to 0.20)
    "country": "US",  // single country
    "starting_ratio": 0.0,  // optional, for tiered lookalikes
    "target_countries": ["US"]  // deprecated, use country
  }
}
```

---

## Facebook Pixel

### Create Pixel
```
POST /{ad_account_id}/pixels  // DEPRECATED, use Business Manager
```

**Better:** Create via Business Manager UI or Business API

### Get Pixel Stats
```
GET /{pixel_id}
Fields: id, name, code, last_fired_time

GET /{pixel_id}/stats
Params: 
  start_time=1609459200  // Unix timestamp
  end_time=1612137600
  aggregation=event  // or custom_data_field
```

### List Pixel Events
```
GET /{pixel_id}/stats
Returns pixel event data (page views, purchases, etc)
```

---

## Targeting Search

### Search Interests
```
GET /search
Params:
  type=adinterest
  q=technology
  limit=10
Returns: {"data": [{"id": "6003139266461", "name": "Technology", "audience_size": 123456}]}
```

### Search Behaviors
```
GET /search
Params: type=adbehavior, q=travel
```

### Geo Targeting
```
GET /search
Params:
  type=adgeolocation
  location_types=["country", "region", "city", "zip"]
  q=New York
```

---

## Batch Requests

### Execute Multiple Operations
```
POST /
Body: {
  "batch": [
    {"method": "GET", "relative_url": "me/adaccounts"},
    {"method": "POST", "relative_url": "{ad_account_id}/campaigns", "body": "name=Test&objective=OUTCOME_TRAFFIC"}
  ]
}
Returns: Array of responses (same order)
```

**Limits:**
- Max 50 operations per batch
- Faster than individual requests
- All operations must use same access token

---

## Error Codes

| Code | Type | Description | Action |
|------|------|-------------|--------|
| 190 | OAuthException | Invalid token | Re-authenticate |
| 100 | Invalid parameter | Bad request | Check params |
| 17 | User request limit | Rate limit | Wait and retry |
| 32 | Page request limit | Rate limit | Wait and retry |
| 4 | API Too Many Calls | Rate limit | Wait longer |
| 80004 | Insufficient permissions | Missing scope | Request permission |
| 2635 | Ad Account Disabled | Account issue | Contact support |
| 1487387 | Budget too low | Min budget not met | Increase budget |

---

## Rate Limits

**Standard Limits:**
- 200 calls per hour per user (varies by app and account)
- Batch requests count as 1 call + (operations / 2)
- Rate limit headers in response:
  - `X-Business-Use-Case-Usage`: Current usage
  - `X-App-Usage`: App-level usage
  - `X-Ad-Account-Usage`: Ad account usage

**Best Practices:**
- Use batch requests
- Cache data when possible
- Monitor usage headers
- Implement exponential backoff

---

## Useful Links

- **Marketing API Docs:** https://developers.facebook.com/docs/marketing-apis
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer
- **Error Reference:** https://developers.facebook.com/docs/graph-api/using-graph-api/error-handling
- **Targeting Specs:** https://developers.facebook.com/docs/marketing-api/audiences/reference/targeting
- **Business SDK (Python):** https://github.com/facebook/facebook-python-business-sdk

---

**Note:** API может меняться. Всегда проверяй актуальную документацию для используемой версии API.


