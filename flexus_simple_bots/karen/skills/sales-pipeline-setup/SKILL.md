---
name: sales-pipeline-setup
description: Guide the user through creating a sales pipeline — name, stages with probabilities, deal creation rules, and deal movement automations.
---

# Sales Pipeline Setup

Guide the user through:

1. **Pipeline Name** — ask what this pipeline is for (e.g., "Inbound Sales", "Partner Onboarding", "Enterprise Deals")
2. **Stages** — ask the user to describe their sales process steps. Suggest common ones as starting points:
   - New Lead -> Qualified -> Proposal Sent -> Negotiation -> Won / Lost
   - Application -> Review -> Trial -> Approved / Rejected
   Help them define stage_probability (win %) and stage_status (OPEN/WON/LOST) for each.
3. **Create pipeline and stages** using erp_table_crud
4. **Deal creation rules** — ask when deals should be created:
   - Automatically when a new contact arrives? (automation on crm_contact insert/update)
   - When a communication/activity is sent?
   - When a contact reaches a certain BANT score?
   Suggest automations accordingly.
5. **Deal movement rules** — ask what should trigger moving a deal between stages:
   - When a contact replies (inbound activity)?
   - When a meeting is scheduled?
   - When a proposal is sent?
   - After N days without activity (follow-up)?
   Set up move_deal_stage automations based on their answers.
