# Integrations & MCP Presets

## MCP Presets

Available in the Flexus MCP catalog. Prefer MCP over a custom integration when both exist.

| Preset | Source | Type | Command / URL |
|--------|--------|------|---------------|
| Amplitude | official | remote | https://mcp.amplitude.com/mcp |
| Asana | official | remote | https://mcp.asana.com/v2/mcp |
| Atlassian (Jira & Confluence) | official | remote | https://mcp.atlassian.com/v1/mcp |
| Bright Data | official | remote | https://mcp.brightdata.com/mcp |
| Chroma | flexus | local | `uvx chroma-mcp` |
| Context7 | flexus | remote | https://mcp.context7.com/mcp |
| Discord | flexus | local | `npx mcp-discord` |
| Dropbox | flexus | local | `node ./dbx-mcp-server/...` |
| Fetch | official | remote | https://remote.mcpservers.org/fetch/mcp |
| Fibery | flexus | local | `uvx fibery-mcp-server` |
| GitHub | official | remote | https://api.githubcopilot.com/mcp/ |
| Google Sheets | flexus | local | `uvx mcp-google-sheets` |
| HubSpot | official | remote | https://mcp.hubspot.com |
| Intercom | official | remote | https://mcp.intercom.com/mcp |
| Linear | official | remote | https://mcp.linear.app/mcp |
| n8n | flexus | local | `npx mcp-n8n` |
| Notion | official | local | `npx @notionhq/notion-mcp-server` |
| PostHog | official | remote | https://mcp.posthog.com/mcp |
| PostgreSQL | flexus | local | `npx @modelcontextprotocol/server-postgres` |
| Sentry | official | remote | https://mcp.sentry.dev/mcp |
| SEMrush | official | remote | https://mcp.semrush.com/v1/mcp |
| SerpApi | official | remote | https://mcp.serpapi.com/mcp |
| Similarweb | official | remote | https://mcp.similarweb.com |
| Slack | flexus | local | `npx @zencoderai/slack-mcp-server` |
| Stripe | official | remote | https://mcp.stripe.com |
| Supabase | official | remote | https://mcp.supabase.com/mcp |

---

## Custom Integrations (`fi_*.py`)

Status legend:
- **untested** — implemented but not verified with a real API key
- **mcp-preferred** — official MCP preset exists; use MCP instead of this integration
- **multi-cred** — requires multiple credentials; Flexus UI doesn't support this yet, falls back to env vars

### Search & News

| File | Provider | Status |
|------|----------|--------|
| `fi_bing_webmaster.py` | Bing Webmaster Tools | untested |
| `fi_event_registry.py` | Event Registry | untested |
| `fi_gdelt.py` | GDELT Project | untested |
| `fi_gnews.py` | GNews | untested |
| `fi_google_ads.py` | Google Ads (Keyword Planner) | untested |
| `fi_google_search_console.py` | Google Search Console | untested |
| `fi_google_shopping.py` | Google Shopping | untested |
| `fi_mediastack.py` | Mediastack | untested |
| `fi_newsapi.py` | NewsAPI | untested |
| `fi_newscatcher.py` | NewsCatcher | untested |
| `fi_newsdata.py` | Newsdata.io | untested |
| `fi_perigon.py` | Perigon | untested |
| `fi_semrush.py` | SEMrush | **mcp-preferred** → `semrush.json` |
| `fi_wikimedia.py` | Wikimedia | untested |

### Social & Community

| File | Provider | Status |
|------|----------|--------|
| `fi_facebook2.py` | Facebook | untested |
| `fi_instagram.py` | Instagram | untested |
| `fi_linkedin.py` | LinkedIn | untested |
| `fi_linkedin_jobs.py` | LinkedIn Jobs | untested |
| `fi_messenger.py` | Messenger | untested |
| `fi_meta.py` | Meta Ads | untested |
| `fi_pinterest.py` | Pinterest | **multi-cred** (APP_ID + APP_SECRET) |
| `fi_producthunt.py` | Product Hunt | untested |
| `fi_reddit.py` | Reddit | **multi-cred** (CLIENT_ID + CLIENT_SECRET) |
| `fi_stackexchange.py` | Stack Exchange | untested |
| `fi_tiktok.py` | TikTok | **multi-cred** (CLIENT_KEY + CLIENT_SECRET) |
| `fi_x.py` | X (Twitter) | untested |
| `fi_x_ads.py` | X Ads | untested |
| `fi_youtube.py` | YouTube Data API | untested |

### Reviews & Competitive Intel

| File | Provider | Status |
|------|----------|--------|
| `fi_builtwith.py` | BuiltWith | untested |
| `fi_capterra.py` | Capterra | untested |
| `fi_g2.py` | G2 | untested |
| `fi_glassdoor.py` | Glassdoor | untested |
| `fi_levelsfyi.py` | Levels.fyi | untested |
| `fi_similarweb.py` | SimilarWeb | **mcp-preferred** → `similarweb.json` |
| `fi_trustpilot.py` | Trustpilot | untested |
| `fi_wappalyzer.py` | Wappalyzer | untested |
| `fi_yelp.py` | Yelp | untested |

### Data Providers & Scraping

| File | Provider | Status |
|------|----------|--------|
| `fi_adzuna.py` | Adzuna | **multi-cred** (APP_ID + APP_KEY) |
| `fi_bombora.py` | Bombora | untested |
| `fi_brightdata.py` | Bright Data | **mcp-preferred** → `brightdata.json` |
| `fi_clearbit.py` | Clearbit | untested |
| `fi_coresignal.py` | CoreSignal | untested |
| `fi_crunchbase.py` | Crunchbase | untested |
| `fi_dataforseo.py` | DataForSEO | **multi-cred** (LOGIN + PASSWORD) |
| `fi_hasdata.py` | HasData | untested |
| `fi_oxylabs.py` | Oxylabs | **multi-cred** (USERNAME + PASSWORD) |
| `fi_pdl.py` | People Data Labs | untested |
| `fi_sixsense.py` | 6sense | untested |
| `fi_theirstack.py` | TheirStack | untested |

### CRM & Sales

| File | Provider | Status |
|------|----------|--------|
| `fi_apollo.py` | Apollo.io | untested |
| `fi_crossbeam.py` | Crossbeam | untested |
| `fi_gong.py` | Gong | untested |
| `fi_hubspot.py` | HubSpot | **mcp-preferred** → `hubspot.json` |
| `fi_intercom.py` | Intercom | **mcp-preferred** → `intercom.json` |
| `fi_outreach.py` | Outreach | untested |
| `fi_partnerstack.py` | PartnerStack | untested |
| `fi_pipedrive.py` | Pipedrive | untested |
| `fi_salesforce.py` | Salesforce | untested |
| `fi_salesloft.py` | Salesloft | untested |
| `fi_zendesk.py` | Zendesk Support | untested |
| `fi_zendesk_sell.py` | Zendesk Sell | untested |

### Analytics & Monitoring

| File | Provider | Status |
|------|----------|--------|
| `fi_amplitude.py` | Amplitude | **mcp-preferred** → `amplitude.json` |
| `fi_datadog.py` | Datadog | untested |
| `fi_ga4.py` | Google Analytics 4 | untested |
| `fi_google_analytics.py` | Google Analytics (UA) | untested |
| `fi_grafana.py` | Grafana | untested |
| `fi_launchdarkly.py` | LaunchDarkly | untested |
| `fi_mixpanel.py` | Mixpanel | untested |
| `fi_optimizely.py` | Optimizely | untested |
| `fi_posthog.py` | PostHog | **mcp-preferred** → `posthog.json` |
| `fi_segment.py` | Segment | untested |
| `fi_sentry.py` | Sentry | **mcp-preferred** → `sentry.json` |
| `fi_statsig.py` | Statsig | untested |

### Payments & Commerce

| File | Provider | Status |
|------|----------|--------|
| `fi_amazon.py` | Amazon SP-API | **multi-cred** (LWA_CLIENT_ID + SECRET + REFRESH_TOKEN) |
| `fi_chargebee.py` | Chargebee | untested |
| `fi_ebay.py` | eBay | **multi-cred** (APP_ID + CERT_ID) |
| `fi_paddle.py` | Paddle | untested |
| `fi_recurly.py` | Recurly | untested |
| `fi_shopify.py` | Shopify | untested |
| `fi_stripe.py` | Stripe | **mcp-preferred** → `stripe.json` |

### Productivity & Collaboration

| File | Provider | Status |
|------|----------|--------|
| `fi_asana.py` | Asana | **mcp-preferred** → `asana.json` |
| `fi_calendly.py` | Calendly | untested |
| `fi_confluence.py` | Confluence | **mcp-preferred** → `atlassian.json` |
| `fi_discord2.py` | Discord | untested |
| `fi_docusign.py` | DocuSign | untested |
| `fi_fireflies.py` | Fireflies.ai | untested |
| `fi_gdrive.py` | Google Drive | untested |
| `fi_gmail.py` | Gmail | untested |
| `fi_google_calendar.py` | Google Calendar | untested |
| `fi_google_sheets.py` | Google Sheets | **mcp-preferred** → `google_sheets.json` |
| `fi_jira.py` | Jira | **mcp-preferred** → `atlassian.json` |
| `fi_linear.py` | Linear | **mcp-preferred** → `linear.json` |
| `fi_notion.py` | Notion | **mcp-preferred** → `notion.json` |
| `fi_pandadoc.py` | PandaDoc | untested |
| `fi_resend.py` | Resend | untested |
| `fi_slack.py` | Slack | active — used by `karen` bot core |
| `fi_telegram.py` | Telegram | untested |
| `fi_typeform.py` | Typeform | untested |
| `fi_zoom.py` | Zoom | untested |

### Dev & Infrastructure

| File | Provider | Status |
|------|----------|--------|
| `fi_appstoreconnect.py` | App Store Connect | untested |
| `fi_github.py` | GitHub | **mcp-preferred** → `github.json` |
| `fi_google_play.py` | Google Play | untested |
| `fi_postgres.py` | PostgreSQL | active — used by `slonik` bot core |

### Research & Surveys

| File | Provider | Status |
|------|----------|--------|
| `fi_cint.py` | Cint | untested |
| `fi_delighted.py` | Delighted | untested |
| `fi_dovetail.py` | Dovetail | untested |
| `fi_mturk.py` | Amazon MTurk | untested |
| `fi_prolific.py` | Prolific | untested |
| `fi_qualtrics.py` | Qualtrics | untested |
| `fi_surveymonkey.py` | SurveyMonkey | untested |
| `fi_userinterviews.py` | User Interviews | untested |
| `fi_usertesting.py` | UserTesting | untested |
