---
name: channel-partner-overlap
description: Partner account overlap analysis using Crossbeam — identify shared customers, warm intro opportunities, and co-sell targets
---

You use Crossbeam to analyze account overlap between your company and partner companies. Overlap data reveals co-sell opportunities (prospects in both pipelines) and referral opportunities (partner customers who would benefit from your product).

Core mode: warm introductions from partner overlap convert 3-5x better than cold outreach to the same account. Overlap data is only useful if you act on it within the pipeline window — stale overlap is worthless.

## Methodology

### Overlap types
Crossbeam compares account lists between two companies in four categories:

1. **Customer × Prospect**: your customer is in the partner's pipeline → mutual validation, potential co-sell
2. **Prospect × Customer**: your prospect is the partner's customer → warm intro opportunity (highest value)
3. **Prospect × Prospect**: both companies are chasing the same account → co-sell to beat competition
4. **Customer × Customer**: both companies already have this customer → integration/expansion opportunity

### Prioritization framework
Prioritize actions by overlap type:
- **Prospect × Customer** (your prospect, their customer): request warm intro. They can vouch for credibility.
- **Prospect × Prospect**: synchronize timing. Who's further along? Can we joint pitch?
- **Customer × Customer**: schedule a joint QBR to explore integration or expansion.

### Requesting introductions
Only request introductions when:
- The overlap account is in an active deal stage (not just a name in the pipeline)
- You have a specific, mutually beneficial reason (not "we want a meeting")
- The partner has agreed to your intro protocol (defined in partner agreement)

Bad: "Can you intro us to Company X?"
Good: "Company X is in both our pipelines at proposal stage. We think a joint session would help them evaluate the integration use case — can we co-present together?"

### Cadence
Pull overlap data weekly when active deals are present. Generate overlap report for weekly partner sync.

## Recording

```
write_artifact(artifact_type="partner_overlap_report", path="/partners/overlap-{partner_id}-{date}", data={...})
```

## Available Tools

```
crossbeam(op="call", args={"method_id": "crossbeam.reports.overlap.v1", "partner_id": "partner_id", "population": "prospects"})

crossbeam(op="call", args={"method_id": "crossbeam.reports.overlap_accounts.v1", "partner_id": "partner_id", "type": "prospect_x_customer"})

crossbeam(op="call", args={"method_id": "crossbeam.partners.list.v1"})

salesforce(op="call", args={"method_id": "salesforce.query.v1", "query": "SELECT Id, Name, StageName, Amount FROM Opportunity WHERE StageName NOT IN ('Closed Won','Closed Lost') ORDER BY Amount DESC LIMIT 100"})
```

## Artifact Schema

```json
{
  "partner_overlap_report": {
    "type": "object",
    "required": ["partner_name", "report_date", "overlap_summary", "action_items"],
    "additionalProperties": false,
    "properties": {
      "partner_name": {"type": "string"},
      "report_date": {"type": "string"},
      "overlap_summary": {
        "type": "object",
        "required": ["prospect_x_customer_count", "prospect_x_prospect_count", "customer_x_customer_count"],
        "additionalProperties": false,
        "properties": {
          "prospect_x_customer_count": {"type": "integer", "minimum": 0},
          "prospect_x_prospect_count": {"type": "integer", "minimum": 0},
          "customer_x_customer_count": {"type": "integer", "minimum": 0}
        }
      },
      "action_items": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["account_name", "overlap_type", "action", "priority"],
          "additionalProperties": false,
          "properties": {
            "account_name": {"type": "string"},
            "overlap_type": {"type": "string", "enum": ["prospect_x_customer", "prospect_x_prospect", "customer_x_customer"]},
            "action": {"type": "string"},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
            "deal_stage": {"type": "string"}
          }
        }
      }
    }
  }
}
```
