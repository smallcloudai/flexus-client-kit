---
name: log-crm-activity
description: How to log CRM activities (conversations, emails, calls) using erp_table_crud on the crm_activity table. Fetch when you need to record an interaction with a contact.
---

# Logging CRM Activities

Use erp_table_crud to create activity records in the crm_activity table.

```python
erp_table_crud(op="create", table_name="crm_activity", fields={
    "activity_contact_id": "CONTACT_ID",
    "activity_type": "MESSENGER_CHAT",
    "activity_direction": "INBOUND",
    "activity_platform": "TELEGRAM",
    "activity_title": "Short title",
    "activity_summary": "Brief summary of what happened",
})
```

## Fields

- **activity_contact_id** (required): the contact this activity belongs to
- **activity_type** (required): WEB_CHAT, MESSENGER_CHAT, EMAIL, CALL, MEETING
- **activity_direction** (required): INBOUND (customer initiated) or OUTBOUND (we initiated)
- **activity_platform**: TELEGRAM, WHATSAPP, EMAIL, SLACK, DISCORD, PHONE, WEB
- **activity_title**: short description
- **activity_summary**: longer summary of the conversation or interaction

## When to Log

- After a messenger conversation ends (not after each message)
- After sending an outbound email or follow-up
- After a call or meeting
