from flexus_client_kit import ckit_cloudtool


MEMORY_PROMPT = """
# Daily Memory Collection

You run once per day to extract reusable Q&A knowledge from recent customer conversations.

## Process

1. Determine `since_ts`:
   - Call flexus_policy_document(op="list", args={"p": "/memory/"}) and find the newest `/memory/YYYYMMDD-daily` document.
   - If found, read it with flexus_policy_document(op="cat") and use `faq.meta.processed_until_ts` as `since_ts`.
   - If no previous doc or no `processed_until_ts`, fall back to last 24 hours.

2. Query recent inbound CRM activities:
   erp_table_data(table_name="crm_activity", options={"filters": {"AND": ["activity_direction:=:INBOUND", "activity_occurred_ts:>:SINCE_TS"]}, "sort_by": ["activity_occurred_ts:ASC"], "limit": 100})
   These are real customer conversations linked to threads.

3. Extract Q&A pairs from `activity_summary` fields — the summary already contains what the customer asked and how it was resolved.
   - Skip greetings, test pings, chitchat, bot-only interactions
   - Only store Q&A where the answer provides procedural steps, specific policies, limits, or non-obvious information. Skip promotions, discounts, stock availability, or other things that change too fast to memorize.
   - Group by topic (billing, product, onboarding, technical, shipping, etc.)
   - Anonymize: replace names, emails, phone numbers, platform IDs with placeholders
   - Merge similar questions from different conversations into one

4. Set `processed_until_ts` to the maximum `activity_occurred_ts` you processed. If nothing processed, use current time.

5. Save results:
   - If Q&A pairs extracted → write /memory/YYYYMMDD-daily with flexus_policy_document(op="create" or "overwrite").
   - If no Q&A but previous doc exists → just update its timestamp:
     flexus_policy_document(op="update_at_location", args={"p": "/memory/PREV-daily", "updates": [["faq.meta.processed_until_ts", NEW_TS]]})
   - If no Q&A and no previous doc → create one with just meta to persist the timestamp.

## QA Document Format

```json
{
    "faq": {
        "meta": {
            "author": "memory-expert",
            "created": "YYYYMMDD",
            "processed_from_ts": 0,
            "processed_until_ts": 0
        },
        "section01-TOPIC": {
            "title": "Topic Name",
            "question01-SLUG": {"q": "Customer question in generic form", "a": "Correct answer based on actual resolution"}
        }
    }
}
```

Use kebab-case slugs. Number sections and questions sequentially.

## After Writing

Resolve with a brief summary: how many activities reviewed, how many Q&A pairs created.
"""

SCHED_MEMORY_DAILY = {
    "sched_type": "SCHED_ANY",
    "sched_when": "WEEKDAYS:MO:TU:WE:TH:FR:SA:SU/23:00",
    "sched_first_question": "Run daily memory collection.",
    "sched_fexp_name": "memory",
}

TOOLS_MEMORY = {"flexus_policy_document", "erp_table_meta", "erp_table_data"} | ckit_cloudtool.KANBAN_SAFE
