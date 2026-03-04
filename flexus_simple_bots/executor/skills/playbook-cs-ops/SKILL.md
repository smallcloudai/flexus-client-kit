---
name: playbook-cs-ops
description: Customer success operations playbook — segmented CS model, QBR process, renewal management, and CS team scaling
---

You codify the customer success operations process: how accounts are segmented, how QBRs are run, how renewals are managed, and how the CS team structure scales with customer count.

Core mode: CS resources are finite. Not every customer deserves the same attention. Define tiers based on ACV and strategic value, then allocate CS resources accordingly. The goal is high-touch where it matters, automated where it doesn't.

## Methodology

### Customer segmentation for CS coverage
Tier customer base by ACV (adjust thresholds to your revenue profile):

**Enterprise (ACV ≥$50k)**: named CSM, weekly check-in, quarterly QBR, executive sponsor matched
**Mid-Market (ACV $10k-$50k)**: named CSM, bi-weekly check-in, quarterly check-in call (not full QBR)
**SMB (ACV <$10k)**: scaled/pooled CS model, automated lifecycle campaigns, reactive support
**Freemium/PLG**: fully automated — product-led activation, no CSM contact until upgrade signal

This segmentation determines staffing ratios. Typical:
- Enterprise CSM: 30-50 accounts per CSM
- Mid-Market CSM: 80-120 accounts per CSM
- SMB: no CSM (automated)

### QBR process (Enterprise and select Mid-Market)
QBR = Quarterly Business Review. It is NOT a product demo — it's a business impact discussion.

Agenda:
1. Success metrics review: how is the customer tracking against their goals?
2. Usage analysis: who is using the product and how? Are there underutilized features?
3. Strategic discussion: what are their priorities for next quarter?
4. Roadmap alignment: how does your roadmap address their needs?
5. Expansion discussion: based on their goals, what's the natural next investment?

QBR preparation checklist:
- [ ] Customer's success metrics pulled from `pilot_status_report` or usage data
- [ ] Usage report generated from analytics
- [ ] NPS score and any open support tickets reviewed
- [ ] Expansion opportunity identified (from `retention_expansion_signals`)

### Renewal management
- 90 days before renewal: confirm renewal intent with champion
- 60 days before: formal renewal proposal sent
- 30 days before: contract signature expected
- 14 days before: escalate if not signed to senior CS / sales

Automate reminder calendar events at each milestone.

## Recording

```
write_artifact(artifact_type="cs_ops_playbook", path="/ops/cs-ops-playbook", data={...})
```

## Available Tools

```
google_calendar(op="call", args={"method_id": "google_calendar.events.insert.v1", "calendarId": "primary", "summary": "QBR - [Company]", "start": {"dateTime": "2024-04-01T10:00:00-05:00"}})

salesforce(op="call", args={"method_id": "salesforce.query.v1", "query": "SELECT AccountId, Name, Amount, ContractEndDate FROM Contract WHERE ContractEndDate = NEXT_N_DAYS:90 ORDER BY ContractEndDate ASC"})

chargebee(op="call", args={"method_id": "chargebee.subscriptions.list.v1", "cancel_at[after]": "2024-01-01", "limit": 50})

zendesk(op="call", args={"method_id": "zendesk.tickets.list.v1", "priority": "high", "status": "open"})
```

## Artifact Schema

```json
{
  "cs_ops_playbook": {
    "type": "object",
    "required": ["created_at", "segmentation_model", "coverage_model", "qbr_process", "renewal_process"],
    "additionalProperties": false,
    "properties": {
      "created_at": {"type": "string"},
      "segmentation_model": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["tier_name", "acv_threshold", "coverage_type", "csm_ratio", "touch_cadence"],
          "additionalProperties": false,
          "properties": {
            "tier_name": {"type": "string"},
            "acv_threshold": {"type": "string"},
            "coverage_type": {"type": "string", "enum": ["high_touch_named", "mid_touch_named", "scaled_pooled", "fully_automated"]},
            "csm_ratio": {"type": "string"},
            "touch_cadence": {"type": "string"}
          }
        }
      },
      "coverage_model": {
        "type": "object",
        "required": ["current_csm_headcount", "account_distribution", "capacity_headroom"],
        "additionalProperties": false,
        "properties": {
          "current_csm_headcount": {"type": "integer", "minimum": 0},
          "account_distribution": {"type": "object"},
          "capacity_headroom": {"type": "string"}
        }
      },
      "qbr_process": {
        "type": "object",
        "required": ["eligible_tiers", "agenda_template", "preparation_checklist"],
        "additionalProperties": false,
        "properties": {
          "eligible_tiers": {"type": "array", "items": {"type": "string"}},
          "agenda_template": {"type": "array", "items": {"type": "string"}},
          "preparation_checklist": {"type": "array", "items": {"type": "string"}}
        }
      },
      "renewal_process": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["days_before_renewal", "action", "owner"],
          "additionalProperties": false,
          "properties": {
            "days_before_renewal": {"type": "integer"},
            "action": {"type": "string"},
            "owner": {"type": "string"}
          }
        }
      }
    }
  }
}
```
