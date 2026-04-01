---
name: stall-recovery
description: Execute a stall deal check — query stalled deals, send follow-ups per stage policy, archive long-inactive deals as Lost.
---

# Stall Recovery

When triggered for stall deal check:

1. Read `/sales-pipeline/stall-deals-policy` — get stall_days, archive_days, outreach_cutoff_stage_id, stage_actions.
2. Compute stall_ts = now - stall_days x 86400. Query **only stalled deals** — never fetch all open deals. Also filter to relevant pipelines and non-WON/LOST stages at query time if the policy lists specific pipeline_ids:
```python
erp_table_data(table_name="crm_deal", options={
    "filters": {"AND": [
        "contact.contact_last_outbound_ts:<:STALL_TS",
        "contact.contact_last_inbound_ts:<:STALL_TS",
    ]},
    "include": ["contact"],
})
```
3. Per deal, look up its stage in stage_actions:
   - **skip**: stage is below outreach cutoff — do nothing
   - **email**: send follow-up only if the contact has prior engagement (stage >= cutoff) AND this stage's follow-up hasn't been sent yet (check `deal_details.last_followup_stage`). Load the template from `template_path` in the stage_actions entry (cat that policy document); if absent, use a short generic follow-up. After sending, record `last_followup_stage` in deal_details to prevent duplicates. Use email_send() tool to do it, and log_crm_activity() after.
4. If inactivity >= archive_days (contact_last_outbound_ts < now - archive_days x 86400): set deal_lost_reason and move deal to Lost stage.
5. Summarize: how many emailed, closed as Lost, skipped — and why skipped. If any deal is in a stage that is at or after the cutoff but has no entry in stage_actions, print a widget to start a chat about it:
```python
print_widget(type="start_chat", expert="default", text="Stage [stage_name] has stalled deals but no action defined — click to decide what to do.")
```
