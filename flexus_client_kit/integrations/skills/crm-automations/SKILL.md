---
name: crm-automations
description: How to create and manage CRM automations — triggers, actions, template variables, filter syntax, and examples. Fetch before creating or updating automations.
---

# CRM Automations

Use crm_automation() tool to manage automations. Never use flexus_my_setup() to set crm_automations directly.

## Structure

Each automation has:
- enabled: bool
- triggers: list of trigger configs, erp_table trigger fires when ERP table records change
- actions: list of action configs: post_task_into_bot_inbox, create/update/delete_erp_record, move_deal_stage.

## Example: Welcome Email

```json
{
  "enabled": true,
  "triggers": [
    {
      "type": "erp_table",
      "table": "crm_contact",
      "operations": ["insert", "update"],
      "filters": [
        "contact_tags:not_contains:welcome_email_sent"
      ]
    }
  ],
  "actions": [
    {
      "type": "post_task_into_bot_inbox",
      "title": "Send welcome email to {{trigger.new_record.contact_first_name}}",
      "details": {
        "contact_id": "{{trigger.new_record.contact_id}}"
      },
      "provenance": "CRM automation: welcome_email",
      "fexp_name": "nurturing"
    },
    {
      "type": "update_erp_record",
      "table": "crm_contact",
      "record_id": "{{trigger.new_record.contact_id}}",
      "fields": {
        "contact_tags": {"op": "append", "values": ["welcome_email_sent"]}
      }
    }
  ]
}
```

## Example: Follow-up Email (Scheduled for Future)

Use `comingup_ts` to schedule tasks for future execution. Tasks with comingup_ts won't appear
in inbox until that time arrives.

```json
{
  "enabled": true,
  "triggers": [
    {
      "type": "erp_table",
      "table": "crm_contact",
      "operations": ["insert", "update"],
      "filters": [
        "contact_tags:contains:welcome_email_sent",
        "contact_tags:not_contains:followup_scheduled"
      ]
    }
  ],
  "actions": [
    {
      "type": "post_task_into_bot_inbox",
      "title": "Send follow-up email to {{trigger.new_record.contact_first_name}} if they haven't replied or talked to us (no inbound CRM activity after our last outbound)",
      "details": {
        "contact_id": "{{trigger.new_record.contact_id}}"
      },
      "provenance": "CRM automation: followup_email",
      "fexp_name": "nurturing",
      "comingup_ts": "{{now() + 432000}}"
    },
    {
      "type": "update_erp_record",
      "table": "crm_contact",
      "record_id": "{{trigger.new_record.contact_id}}",
      "fields": {
        "contact_tags": {"op": "append", "values": ["followup_scheduled"]}
      }
    }
  ]
}
```

Note: 432000 seconds = 5 days.

## Example: Move Deal Stage on Activity

When a CRM activity is created (chat, call, email), move the contact's deal to a new stage.

**IMPORTANT:** Before creating this automation, query the pipeline stages to get the actual stage IDs:
```python
erp_table_data(table_name="crm_pipeline_stage", options={"where": {"stage_pipeline_id": "YOUR_PIPELINE_ID"}, "order_by": "stage_sequence"})
```

```json
{
  "enabled": true,
  "triggers": [
    {
      "type": "erp_table",
      "table": "crm_activity",
      "operations": ["insert", "update"],
      "filters": [
        "activity_type:=:WEB_CHAT",
        "activity_direction:=:INBOUND"
      ]
    }
  ],
  "actions": [
    {
      "type": "move_deal_stage",
      "contact_id": "{{trigger.new_record.activity_contact_id}}",
      "pipeline_id": "8f3a2b1c9d4e7890",
      "from_stages": ["1a2b3c4d5e6f7890", "7g8h9i0j1k2l3456"],
      "to_stage_id": "3m4n5o6p7q8r9012"
    }
  ]
}
```

The `move_deal_stage` action:
- `contact_id`: Contact whose deal to move (use template variable)
- `pipeline_id`: Pipeline to search for the deal
- `from_stages`: Only move if deal is currently in one of these stages (array of stage IDs)
- `to_stage_id`: Target stage ID

Finds the most recently modified deal for that contact in the pipeline. Skipped silently if no deal found or deal not in from_stages.

## Template Variables

Use {{path.to.value}} to reference trigger data:
- {{trigger.new_record.contact_id}}
- {{trigger.old_record.contact_email}} (for updates/deletes)

Special functions:
- {{now()}} - current Unix timestamp
- {{now() + 86400}} - timestamp one day from now (86400 = 24*60*60)
- {{now() - 3600}} - timestamp one hour ago

## Field Operations

For atomic operations on fields:

```
"fields": {
  "contact_tags": {"op": "append", "values": ["tag1", "tag2"]},
  "contact_score": {"op": "increment", "value": 10}
}
```

Supported operations:
- append: Add items to a list field
- remove: Remove items from a list field
- increment: Add to a numeric field
- decrement: Subtract from a numeric field
- set: Set value directly (default when using string)

Template values work in operations:
```
"contact_tags": {"op": "append", "values": ["{{trigger.new_record.source_tag}}"]}
```

## Trigger Filter Syntax

Format: "field:op:value"

Operators for arrays: contains, not_contains
Operators for other types: =, !=, >, <, >=, <=

Examples:
- "contact_tags:not_contains:welcome_email_sent" - check array doesn't contain value
- "contact_tags:contains:vip" - check array contains value
- "contact_email:!=:" - check field is not empty

## Important Notes

- Before creating automations, check `erp_table_meta(table_name="...")` for available fields and required fields
- Actions execute in sequence
- Failed actions are logged but don't stop subsequent actions
- Triggers fire IMMEDIATELY when the event happens. Time-based filters check conditions at that moment, they don't delay execution
- For delayed tasks (follow-ups after N days), use `comingup_ts` in post_task_into_bot_inbox action
- **ALWAYS use `["insert", "update"]` for operations, not just `["insert"]`!** If the bot is offline when a record is inserted, it will receive an "update" event when it comes back online. Using only "insert" means you'll miss records created while the bot was down.
- Multiple follow-ups: all automations trigger at the same moment (when tag is added), so comingup_ts is relative to that moment. If you want follow-up 1 at 3 days, and follow-up 2 to be 4 days after follow-up 1, set follow-up 2 comingup_ts to 7 days (3+4), not 4
- Chain follow-ups via tags: follow-up 2 should trigger on "followup_1_scheduled" tag (added by follow-up 1), not on "welcome_email_sent". Otherwise there may be a data race creating duplicate tasks
- When creating automations that post tasks, use `fexp_name` to route to the right expert: `"nurturing"` for simple templated tasks (welcome emails, follow-ups, status checks), `"support_and_sales"` for full sales conversations
