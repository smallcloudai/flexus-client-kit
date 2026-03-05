---
name: stall-deals
description: Guide the user through setting up a stall deal recovery policy — timing thresholds, per-stage actions, and an automated schedule. Use when the user asks about inactive deals, follow-up automation, or stale leads.
---

# Stall Deal Recovery Setup

## Step 1: Timing thresholds

Ask:
- **Stall threshold**: how many days of no activity before a deal is stalled? Suggest 7 or 14.
- **Archive threshold**: Suggest ~3× stall (e.g. 21 if stall=7, 45 if stall=14). After this, move to Lost.

## Step 2: Outreach cutoff stage

Load the user's pipelines and stages, then ask: from which stage onwards is it safe to reach out? Only stages where the contact has shown real intent (signed up, filled a form, had a conversation) should get emails. Stages before that cutoff are cold/non-compliant — skip them entirely.

```python
erp_table_data(table_name="crm_pipeline", options={})
erp_table_data(table_name="crm_pipeline_stage", options={})
```

## Step 3: Per-stage action above the cutoff

- Early-ish (low probability): soft value-add message, no sales pitch
- Mid (25–70%): follow-up email with urgency or competitive angle
- Late (70%+): direct personal check-in, ask if anything changed

## Step 4: Save and schedule

Ask the user what time they'd like the daily stall check to run. Suggest 11:00 on weekdays as a sensible default. Confirm before saving.

Use `flexus_schedule()` for the periodic stall check — never CRM automations (those are for event-driven reactions, not time-based sweeps).

Create schedule with first question exactly like the one below:

```python
flexus_policy_document(op="write", args={
    "p": "/sales-pipeline/stall-deals-policy",
    "content": {
        "stall-deals-policy": {
            "meta": {"author": "...", "created": "YYYYMMDD", "updated": "YYYYMMDD"},
            "stall_days": 14,
            "archive_days": 45,
            "outreach_cutoff_stage_id": "...",
            "stage_actions": [
                {"stage_id": "...", "stage_name": "...", "action": "skip|email|checkin", "tone": "value_add|urgency|direct"}
            ]
        }
    }
})

flexus_schedule(op="upsert", args={
    "sched_type": "SCHED_ANY",
    "sched_when": "WEEKDAYS:MO:TU:WE:TH:FR/11:00",  # use time confirmed with user
    "sched_first_question": "Run stall deal check per /sales-pipeline/stall-deals-policy.",
    "sched_fexp_name": "nurturing",
    "sched_enable": True
})
```

Confirm with a short summary: stall/archive thresholds, cutoff stage, action per stage group, schedule frequency.
