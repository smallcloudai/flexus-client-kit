# Research: pilot-conversion

**Skill path:** `executor/skills/pilot-conversion/`
**Bot:** executor (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pilot-conversion` manages the final stage: converting a completed pilot into a commercial contract, with expansion planning embedded from the start. The current SKILL.md is the strongest of the five executor skills — the pre-conversion preparation steps, success review agenda, and contract generation flow are all sound. The gaps are: objection handling for the three most common post-success-review stalls is entirely absent; the expansion planning section is underspecified (no signals, triggers, or NRR targets); partial success handling (some criteria met, some not) has no documented protocol; and the "conditional close" framing — where the contract is the pre-agreed natural outcome of success, not a fresh decision — is implied but not explicit.

---

## Definition of Done

- [x] At least 4 distinct research angles covered
- [x] Each finding has a source URL
- [x] Methodology covers practical how-to
- [x] Tool/API landscape with current limits
- [x] Failure modes documented
- [x] Schema grounded in real data shapes
- [x] Gaps listed

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> What does a high-conversion success review and close process look like in 2025?

**Findings:**

**Conversion rates and what drives them.** Properly structured B2B SaaS pilots convert at 30-60%. Pilots with predefined, quantitative success criteria are 3.2x more likely to convert than open-ended evaluations. The differentiator is not product quality — it is commercial structure. [M1][M2]

**The conditional close framing.** The most powerful conversion mechanism is framing the pilot itself, from Day 1, as a conditional purchase decision: "If we hit metrics X, Y, and Z, we proceed to a 12-month contract at [price]." When the success review arrives, the customer has already committed to a decision rule. The executor's job is to present proof that the rule was met — not to re-open the decision. The current SKILL.md implies this logic but does not state it explicitly. The success review should be framed as "let's walk through the evidence together and confirm the conversion" — not "what do you want to do now that the pilot is done?" [M1][M3]

**Pre-loaded commercial readiness.** Before the success review, prepare: SOC 2 / security documentation, production MSA with pre-completed company details, SOW or order form with the agreed tier, and procurement portal registration if required by the customer. Nothing should be "we'll send you something next week." Momentum decays by roughly 20-30% per week after the success review closes. Every item that pushes first signature past Day 3 post-success-review is a deal risk. [M1]

**Paid pilot credit as a conversion accelerator.** If the pilot was priced (5-15% of ACV or 1-2 months of list price), credit 100% toward the full contract upon conversion. This removes the "I already paid for the pilot, now you want full price?" objection and reinforces that the pilot price was always part of the full contract. If the pilot was free, a time-limited conversion incentive (e.g., 20% discount if signed within 10 business days of success review) creates urgency without discounting the product permanently. [M2][M4]

**Partial success protocol.** Not all pilots end with every criterion met. The current SKILL.md mentions "acknowledge gaps" in the agenda but gives no protocol. The correct approach for partial success:
1. Separate criteria into: Met, On Track (would have met with more time), and Genuinely Missed.
2. For "Genuinely Missed": diagnose whether it was a product capability gap, an adoption/setup failure, or an external factor (data quality, IT delays, personnel changes).
3. If the cause is diagnosable and correctable: document a remediation plan as an addendum to the contract. Price the full contract at full rate — do not discount for a failure caused by the customer's own adoption execution.
4. If the cause is a product gap: escalate to product team for roadmap inclusion. Offer a conditional contract clause (a milestone to be met in 90 days post-conversion) rather than walking away. [M3]

**Sources:**
- [M1] nēdl Labs: Escaping Pilot Purgatory: https://nedllabs.com/blog/escaping-pilot-purgatory
- [M2] DoWhatMatter: Pilot Pricing for Seed SaaS That Converts: https://dowhatmatter.com/guides/pilot-pricing-seed-saas
- [M3] Medium: B2B SaaS Pilots — Disciplined Approach: https://medium.com/@dipam.iitm/b2b-saas-pilots-a-disciplined-approach-d586e912063a
- [M4] Getmonetizely: Enterprise Pilot Program Pricing: https://www.getmonetizely.com/articles/how-to-structure-enterprise-pilot-program-pricing-effective-proof-of-concept-strategies

---

### Angle 2: Tool & API Landscape
> Current API capabilities and limits for PandaDoc, DocuSign, and Salesforce.

**Findings:**

**PandaDoc:**
- `pandadoc.documents.create.v1`: creates a document from template with token substitution. Rate limit: **500 RPM** (create from template, 60-second sliding window). [T1]
- `pandadoc.documents.send.v1`: sends the document for signature. Rate limit: **400 RPM**. [T1]
- Download: **100 RPM** — slowest operation. Don't download in bulk.
- Sandbox API key: **10 RPM** across all endpoints — testing must account for this.
- Request body: **2MB max**. PDF attachments: **50MB max**. [T1]
- Tokens in templates: populate contract-specific fields (company name, price, contract length, tier, success criteria as SLAs). Template tokens must exactly match the template's token names — mismatch silently leaves the field blank.
- PandaDoc supports embedded signing (recipient signs within your platform without redirect). [T2]

**DocuSign:**
- `docusign.envelopes.create.v1`: the current SKILL.md uses `documentBase64` to pass the document as a base64-encoded string. This requires pre-generating the contract PDF before calling DocuSign — more complex than PandaDoc's template-token approach.
- DocuSign + Salesforce integration: when a DocuSign envelope reaches "Completed" / "Signed" status, an Apex trigger can automatically update the Salesforce Opportunity stage to "Closed Won." This automation is available via the DocuSign for Salesforce AppExchange package. [T3]
- Practical implication: if the tenant uses DocuSign + Salesforce, the Salesforce Opportunity update should be triggered by the signature event, not called manually in parallel by the bot. Calling `salesforce.sobjects.opportunity.update.v1` with "Closed Won" before the contract is actually signed is a data integrity error. [T4]

**Salesforce:**
- `salesforce.sobjects.opportunity.update.v1`: use to update opportunity stage and close date. Stage progression for conversion flow: move to "Contract Sent" when PandaDoc/DocuSign document is sent; move to "Closed Won" when signature is received (either manually by executor or automatically via DocuSign trigger). Do not mark "Closed Won" before signature is confirmed. [T4]

**Sources:**
- [T1] PandaDoc API Limits: https://developers.pandadoc.com/reference/limits
- [T2] PandaDoc: API vs DocuSign: https://www.pandadoc.com/api/docusign-api-vs-pandadoc-api/
- [T3] DocuSign: Salesforce Integration: https://docusign.com/integrations/esignature-for-salesforce
- [T4] Salesforce StackExchange: Update Opportunity on DocuSign Signed: https://salesforce.stackexchange.com/questions/115336/update-opportunity-stage-when-docusign-envelope-status-is-signed

---

### Angle 3: Data Interpretation & Expansion Planning
> What signals drive expansion, and what NRR targets should inform expansion planning?

**Findings:**

**NRR as the valuation driver.** Companies with NRR > 110% command 20-30% higher valuations than those below 100%. In 2026, 40% of new ARR in high-performing SaaS companies comes from existing customers. A pilot conversion that lands at minimal scope is not a failure — it is an expansion opportunity if the expansion plan is documented and activated. [D1]

**Land-and-expand probability math.** The probability of selling to an existing customer is 60-70% vs. 5-20% for a new prospect. Expansion conversations initiated within 60-90 days of conversion, when product adoption is accelerating, are dramatically easier than expansions attempted after the relationship has plateaued. The expansion plan must be written at conversion, not when someone asks "should we expand?" months later. [D2]

**Four expansion levers (prioritized by execution speed):**
1. **Seat expansion:** additional users within the same team as adoption proves value. Fastest trigger: license utilization approaching 80% of current allocation. [D3]
2. **Feature upsells:** upgrading to higher tier for premium capabilities. Trigger: champion requests a feature that is only in a higher tier, or usage patterns indicate workflows blocked by tier limits.
3. **Module / adjacent use case expansion:** activating a second use case or department. Trigger: champion introduces the product to a peer in another function; or a new champion is identified through product usage data.
4. **Value-metric pricing expansion:** if pricing is usage-based, expansion happens automatically as customer success grows. Trigger: usage volume crosses the next pricing band.

**Expansion signals to track from conversion day:**
- License utilization %: auto-trigger expansion outreach at 80%
- Seat count vs. total team size: if only 3 of 15 team members are licensed, 12 are a natural expansion audience
- Feature request patterns from the champion: high-tier feature requests signal readiness for an upsell
- New champion identified: department peer who starts using the product or attending reviews
- NPS score at 90 days: high NPS without expansion is a missed opportunity [D1][D4]

**Expansion timing.** Set the first expansion conversation at 60 days post-conversion for seat/feature expansions. Set a broader QBR (Quarterly Business Review) at 90 days to review business impact and introduce adjacent use cases. Do not wait for the annual renewal to discuss expansion — by that point, renewal and expansion are competing conversations and price sensitivity is highest. [D4]

**Sources:**
- [D1] IdeaPlan: Expansion Revenue & NRR Playbook: https://www.ideaplan.io/strategy/expansion-revenue-nrr-playbook
- [D2] Phi Consulting: Land and Expand GTM Model Mid-Market: https://phi.consulting/post/land-and-expand-gtm-model-mid-market-saas
- [D3] Getmonetizely: Land and Expand Pricing Models: https://www.getmonetizely.com/articles/land-and-expand-pricing-models-that-support-upsells-and-expansion-revenue
- [D4] Land and Expand Academy: Complete Guide: https://www.landandexpand.academy/blog/land-and-expand-methodology

---

### Angle 4: Failure Modes & Anti-Patterns
> Where do conversions stall after a successful pilot? How to diagnose and handle?

**Findings:**

**"Budget not available" objection.** Research shows 72% of budget objections disappear when the rep uses a structured ROI quantification sequence instead of defending price. The objection is almost never literally about budget — it is about the buyer not being able to justify the spend internally. The response protocol: [F1]
1. "What would this need to deliver to justify the investment?" — gets the buyer to state their own ROI hurdle.
2. "Based on the pilot results, you achieved [X outcome] worth [Y financial value]. How does that compare to the investment?" — the buyer answers their own objection.
3. If still stalled: "Is this a timing issue, a budget source issue, or a value conviction issue?" — forces diagnosis instead of vague delay.
Never discount in response to "budget not available" unless you have confirmed it is a genuine LOB budget constraint, not a value perception issue.

**"Need more time to evaluate" objection.** This almost always signals fear of making the wrong decision, not genuine need for more data. The pilot already provided the data. Response protocol: [F2]
1. Acknowledge the concern: "That makes sense — this is a significant commitment."
2. Identify the specific fear: "What specifically are you worried about getting wrong?"
3. Address with structure: milestone-based rollout plan, a defined rollback or off-ramp clause in the first contract, a phased deployment scope.
4. Create urgency without pressure: reference the conversion incentive expiry date and the fact that procurement/legal review takes time. "If we start the contract now, your team can keep building on the pilot momentum. If we wait 30 days, we're starting onboarding from a standing start."

**"Need to talk to [person not in the room]" objection.** This signals an unengaged stakeholder who was not properly involved during the pilot. Response: [F2]
1. Do not agree to "I'll send them the proposal" — that is a dead end.
2. Request a multi-stakeholder call instead: "Let's schedule a 30-minute session with you, [person], and me to walk through the results together. That way any questions come up in context, not over email."
3. If the person is the economic buyer who was not engaged during the pilot: escalate to AE. This is a commercial track failure from `pilot-success-tracking`, not an objection to be handled at the conversion stage alone.

**Marking Salesforce Closed Won before contract is signed.** The current SKILL.md includes a Salesforce Opportunity update as one of the "available tools" but does not specify the trigger condition. Marking "Closed Won" when the contract is merely sent (not signed) corrupts pipeline reporting and triggers premature revenue recognition in financial systems. Closed Won = signature confirmed, not contract sent. Contract sent = "Contract Sent" stage. [F3]

**Presenting the contract as a fresh decision, not a conditional close confirmation.** The success review agenda in the current SKILL.md ends with "commercial proposal (15 min): present options, discuss terms." This framing — presenting options and discussing terms at the success review — treats the commercial decision as new information. If the MAP was correctly structured, the commercial terms were agreed in principle before the pilot started. The success review presents proof that the agreed conditions were met; the contract is the pre-agreed consequence. Presenting "options" at this stage re-opens the decision and invites scope-and-price negotiation. [F4]

**Expansion planning deferred to "we'll schedule a QBR in 3 months."** Without a documented expansion plan written at conversion, expansion conversations are reactive — they happen only when the customer asks, not when the vendor identifies the signal. 40% of new ARR in high-performing SaaS companies comes from existing customers, but only companies with proactive expansion playbooks capture this systematically. Document the expansion plan at conversion: named expansion signals, trigger thresholds, next-conversation dates, and responsible owners. [F5]

**Sources:**
- [F1] Leedin: 3 Questions That Slash Budget Objections: https://www.leedinsight.com/blog/saas-budget-objections-questions
- [F2] Sellible: Objection Handling Playbook for B2B SaaS: https://blog.sellible.ai/objection-handling-playbook-for-b2b-saas/
- [F3] Salesforce StackExchange: Stage on Signature: https://salesforce.stackexchange.com/questions/115336/update-opportunity-stage-when-docusign-envelope-status-is-signed
- [F4] nēdl Labs: Pilot Purgatory: https://nedllabs.com/blog/escaping-pilot-purgatory
- [F5] IdeaPlan: NRR Playbook: https://www.ideaplan.io/strategy/expansion-revenue-nrr-playbook

---

## Synthesis

The current SKILL.md is the strongest starting point of any skill in this research series. The evidence-first framing, the pre-conversion preparation checklist, and the contract generation flow are all correct. The three additions that will most improve conversion rates:

1. **Objection handling playbook.** The three stalls — "budget not available," "need more time," "need to talk to someone" — have specific response protocols. Without them, the executor will improvise or defer. The ROI quantification sequence resolves 72% of budget objections without discounting.

2. **Conditional close enforcement.** The success review must not re-open the commercial decision. Frame it as: "We agreed that if criteria X, Y, Z were met, we'd proceed to contract. Here is the evidence. Let's confirm the contract details." This is distinct from "here are results, what do you want to do?"

3. **Expansion plan at conversion, not 3 months later.** Document named signals, trigger thresholds, and expansion conversation dates as part of the conversion artifact. Seat utilization at 80% = expansion trigger. 60-day post-conversion = first expansion conversation. 90-day = QBR.

The Salesforce Closed Won timing issue is a data integrity risk that is easy to mishandle — needs explicit instruction: Closed Won only on confirmed signature.

---

## Recommendations for SKILL.md

- Add objection handling playbook as a named methodology section with protocols for three objections: budget, time, missing stakeholder.
- Reframe success review agenda step 5 ("present options") to "confirm contract details" — options were discussed at MAP stage, not at success review.
- Add partial success protocol: Met / On Track / Genuinely Missed triage, with different responses for each.
- Add Salesforce stage sequencing: Contract Sent → Closed Won (on signature only, not on send).
- Add expansion plan as a required pre-conversion output: four expansion levers, named trigger signals, next-conversation dates.
- Add conversion incentive guidance: pilot credit (if paid pilot) or time-limited discount (if free pilot).
- Expand schema: add objections_raised, partial_success_remediations, expansion_plan, conversion_incentive, and signature_confirmed fields.

---

## Draft Content for SKILL.md

### Draft: Updated core mode

You manage pilot-to-contract conversion and embed the expansion plan from Day 1 of the customer relationship. Conversion is not a negotiation that starts at the success review — it is the execution of a conditional close that was agreed at the MAP stage. Your job at the success review is to confirm that conditions were met, present evidence, and move to signature. If the conditions were only partially met, triage the gap before the meeting and have a remediation plan ready. Do not re-open commercial terms at the success review.

---

### Draft: Methodology additions

**Objection handling (add as a named section):**

Three stalls occur most often in the 1-5 business days after a successful review. Prepare responses in advance — do not improvise.

**"Budget not available":**
1. Do not defend price or offer a discount immediately.
2. "What would this solution need to deliver to justify the investment from your team's perspective?"
3. "Based on your pilot data: [specific outcome] is worth approximately [financial value]. Is the gap between that value and the contract price a risk you're taking on, or a justification gap to your budget committee?"
4. If it is a justification gap: offer to co-author the internal business case with specific ROI numbers from the pilot.
5. If it is a genuine LOB budget constraint: ask "which budget cycle would unlock this, and what do we need to prepare for that conversation?"
6. Do not discount unless you have confirmed this is a real budget ceiling, not a value conviction issue.

**"Need more time to evaluate":**
1. "What specifically are you worried about getting wrong?" — force specificity.
2. If concern is implementation risk: offer a milestone-based contract clause (first 90 days as a defined rollout scope with an off-ramp if adoption targets are not met).
3. If concern is executive buy-in: request a multi-stakeholder call with the champion, economic buyer, and yourself — do not let the champion relay the results alone.
4. Reference momentum: "We've built onboarding context and team relationships during the pilot. Starting from scratch in 60 days means rebuilding that context."
5. Reference conversion incentive expiry if one exists.

**"Need to talk to [person]":**
1. Do not agree to send the proposal by email for the absent person to review alone.
2. "Let's schedule a 30-minute call with you, [person], and me — I'll walk through the pilot results and we can address any questions in real time."
3. If the person is the economic buyer who was never engaged: this is an escalation to the AE, not an objection to handle at conversion stage. The commercial track in `pilot-success-tracking` was incomplete.

**Partial success triage (add before success review agenda):**
Before the success review call, classify each criterion:
- **Met:** threshold achieved or ≥80% reached within window. Present as evidence.
- **On Track:** would have met with more time; external factor or ramp time explains the shortfall. Present trajectory data, not just final number.
- **Genuinely Missed:** threshold not met for a diagnosable reason.
  - Product gap: document for roadmap. Propose a conditional contract clause (milestone within 90 days post-conversion). Do not discount — this is a product commitment, not a price concession.
  - Adoption/setup failure (customer's own execution): document a remediation plan as a contract addendum. The failure does not change the product's value proposition.
  - External factor (IT delays, personnel change, data quality): document as a known constraint. Offer to restart the measurement window post-conversion.

If any P0 criterion is Genuinely Missed with no path to remediation: do not present a conversion offer. Offer a structured extension (15-30 days, scoped remediation plan) or a mutual exit. A contract signed after a failed pilot on key criteria is a churn event waiting to happen.

**Expansion plan (required conversion-day artifact):**
Document at conversion, not at 90-day QBR:
- Seat expansion: current licensed seats vs. total team size. Trigger: utilization >80%. Next outreach date: 60 days post-conversion.
- Feature upsell: identify the highest-tier feature the champion would benefit from. Trigger: champion requests it or usage pattern shows the need. Timeline: include in 90-day QBR agenda.
- Module/adjacent use case: identify one adjacent department or use case that the champion can internally introduce. Trigger: new champion identified from that team. Timeline: 90-day QBR.
- Value-metric expansion (if usage-based pricing): identify the next pricing band threshold. The customer will expand automatically — ensure they know the pricing model so it is not a surprise.

---

### Draft: Anti-patterns

#### Salesforce Closed Won Before Signature
**What it looks like:** Executor calls `salesforce.sobjects.opportunity.update.v1` with `StageName: "Closed Won"` at the same time as sending the DocuSign/PandaDoc envelope.
**Detection signal:** Opportunity is marked Closed Won but no signed document exists in the CRM or document system.
**Consequence:** Revenue is recognized before the contract is legally binding. If the customer does not sign, a reversal is required — corrupting pipeline metrics and financial reporting.
**Mitigation:** Stage sequence is: (1) Contract Sent stage when document is sent. (2) Closed Won only when signature event is confirmed. If using DocuSign + Salesforce integration, the Salesforce stage update should be triggered by the DocuSign "Completed" webhook, not by the bot calling Salesforce directly.

#### Re-Opening Commercial Terms at Success Review
**What it looks like:** Success review agenda item says "present options, discuss terms." The customer is shown multiple tier options and asked to choose.
**Detection signal:** Commercial terms were not agreed at the MAP stage and are being introduced for the first time at the success review.
**Consequence:** The success review becomes a negotiation. Customers who expected to evaluate the product are now being asked to make a commercial decision they are unprepared for. Deal cycles extend 2-4 weeks while they "think about it."
**Mitigation:** Commercial structure (tier, price, contract length) must be agreed in principle at the MAP stage, before the pilot starts. The success review presents the contract as the documented consequence of the conditions being met — not as a new commercial conversation.

#### Discounting in Response to "Budget Not Available"
**What it looks like:** Customer says "budget is tight, could you do 30% off?" Executor offers 20%.
**Detection signal:** Discount offered without first diagnosing whether the objection is a value perception gap or a real budget ceiling.
**Consequence:** 72% of budget objections are actually value perception issues. Discounting addresses the wrong problem, permanently anchors the customer's pricing expectations lower, and signals that the original price was not grounded in value.
**Mitigation:** Use the ROI quantification sequence before offering any discount. Only offer a discount if the customer explicitly confirms: (a) the value justification is clear, and (b) the constraint is a documented LOB budget ceiling, not a preference for a lower price.

---

### Draft: Artifact Schema

```json
{
  "pilot_conversion": {
    "type": "object",
    "description": "Conversion summary: success evidence, contract status, objections handled, and expansion plan.",
    "required": [
      "account_id",
      "conversion_date",
      "success_review_outcome",
      "evidence_summary",
      "contract",
      "expansion_plan",
      "status"
    ],
    "additionalProperties": false,
    "properties": {
      "account_id": {
        "type": "string"
      },
      "conversion_date": {
        "type": "string",
        "format": "date",
        "description": "Date the success review was conducted."
      },
      "success_review_outcome": {
        "type": "object",
        "description": "Aggregated outcome across all success criteria.",
        "required": ["criteria_results", "overall_verdict"],
        "additionalProperties": false,
        "properties": {
          "criteria_results": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["criterion_id", "description", "threshold", "actual_value", "status", "priority"],
              "additionalProperties": false,
              "properties": {
                "criterion_id": {"type": "string"},
                "description": {"type": "string"},
                "threshold": {"type": "string"},
                "actual_value": {"type": ["string", "number"]},
                "status": {
                  "type": "string",
                  "enum": ["met", "on_track", "genuinely_missed_product_gap", "genuinely_missed_adoption_failure", "genuinely_missed_external_factor"]
                },
                "priority": {"type": "string", "enum": ["P0", "P1", "P2"]},
                "remediation_plan": {
                  "type": ["string", "null"],
                  "description": "For genuinely_missed criteria: the agreed remediation plan or contract clause."
                }
              }
            }
          },
          "overall_verdict": {
            "type": "string",
            "enum": ["full_success", "partial_success_proceed", "partial_success_extension", "failure_exit"],
            "description": "full_success: all P0 criteria Met. partial_success_proceed: some P1/P2 missed but P0s all Met; proceed with remediation addendum. partial_success_extension: a P0 was missed with a diagnosable cause; offer structured extension. failure_exit: P0 missed with no remediation path."
          }
        }
      },
      "evidence_summary": {
        "type": "object",
        "description": "Compiled business value evidence for the success review presentation.",
        "required": ["financial_value_delivered", "key_outcomes"],
        "additionalProperties": false,
        "properties": {
          "financial_value_delivered": {
            "type": "number",
            "minimum": 0,
            "description": "Total quantified financial value delivered during the pilot (annualized, in account currency)."
          },
          "financial_value_methodology": {
            "type": "string",
            "description": "How the financial value was calculated. E.g. 'Hours saved (40/week) × fully-loaded cost ($85/hr) × 52 weeks'."
          },
          "key_outcomes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["outcome_description", "before_value", "after_value", "improvement_pct"],
              "additionalProperties": false,
              "properties": {
                "outcome_description": {"type": "string"},
                "before_value": {"type": "string"},
                "after_value": {"type": "string"},
                "improvement_pct": {"type": "number"}
              }
            }
          }
        }
      },
      "objections_raised": {
        "type": "array",
        "description": "Objections raised at or after the success review, with resolution status.",
        "items": {
          "type": "object",
          "required": ["objection_type", "raised_at", "resolution", "resolved"],
          "additionalProperties": false,
          "properties": {
            "objection_type": {
              "type": "string",
              "enum": ["budget_not_available", "need_more_time", "missing_stakeholder", "criteria_dispute", "product_gap", "scope_concern", "other"]
            },
            "raised_at": {"type": "string", "format": "date"},
            "resolution": {"type": "string", "description": "How it was addressed."},
            "resolved": {"type": "boolean"},
            "discount_offered": {
              "type": ["number", "null"],
              "minimum": 0,
              "maximum": 100,
              "description": "Discount % offered in response to this objection, if any. Track to detect pattern of price-based closes."
            }
          }
        }
      },
      "conversion_incentive": {
        "type": "object",
        "description": "Pilot credit or time-limited discount applied to drive conversion.",
        "required": ["type", "value", "expiry_date"],
        "additionalProperties": false,
        "properties": {
          "type": {
            "type": "string",
            "enum": ["pilot_credit", "time_limited_discount", "none"]
          },
          "value": {
            "type": ["string", "null"],
            "description": "Credit amount or discount %. E.g. '$2,000 pilot credit' or '20% off Year 1'."
          },
          "expiry_date": {
            "type": ["string", "null"],
            "format": "date",
            "description": "Date after which the incentive lapses. Must be communicated to customer in writing."
          }
        }
      },
      "contract": {
        "type": "object",
        "description": "Contract generation and signature tracking.",
        "required": ["tool_used", "document_id", "sent_at", "signature_confirmed", "salesforce_stage"],
        "additionalProperties": false,
        "properties": {
          "tool_used": {
            "type": "string",
            "enum": ["pandadoc", "docusign"]
          },
          "document_id": {
            "type": "string",
            "description": "Document ID from PandaDoc or DocuSign."
          },
          "sent_at": {
            "type": ["string", "null"],
            "format": "date-time"
          },
          "signed_at": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "Timestamp when all signatories completed signing. Only set on confirmed signature event."
          },
          "signature_confirmed": {
            "type": "boolean",
            "description": "True only after signature webhook or manual confirmation. Must be true before Salesforce Closed Won is updated."
          },
          "salesforce_stage": {
            "type": "string",
            "enum": ["contract_sent", "closed_won"],
            "description": "Salesforce opportunity stage. contract_sent = document sent, not signed. closed_won = signature_confirmed = true only."
          },
          "tier": {"type": "string"},
          "monthly_value": {"type": "number", "minimum": 0},
          "contract_length_months": {"type": "integer", "minimum": 1},
          "start_date": {"type": ["string", "null"], "format": "date"}
        }
      },
      "expansion_plan": {
        "type": "object",
        "description": "Documented expansion strategy at conversion. Must be set at conversion, not deferred.",
        "required": ["seat_expansion", "feature_upsell", "adjacent_use_case", "next_qbr_date"],
        "additionalProperties": false,
        "properties": {
          "seat_expansion": {
            "type": "object",
            "required": ["current_licensed_seats", "total_team_size", "trigger_utilization_pct", "next_outreach_date"],
            "additionalProperties": false,
            "properties": {
              "current_licensed_seats": {"type": "integer", "minimum": 1},
              "total_team_size": {"type": ["integer", "null"], "minimum": 1},
              "trigger_utilization_pct": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "License utilization % at which expansion outreach is triggered. Default: 80."
              },
              "next_outreach_date": {"type": "string", "format": "date", "description": "Default: 60 days post-conversion."}
            }
          },
          "feature_upsell": {
            "type": "object",
            "required": ["target_tier", "trigger_signal", "timeline"],
            "additionalProperties": false,
            "properties": {
              "target_tier": {"type": ["string", "null"], "description": "The tier or add-on the customer would benefit from."},
              "trigger_signal": {"type": "string", "description": "What event or behavior triggers the upsell conversation."},
              "timeline": {"type": "string", "description": "When to raise the upsell. Default: 90-day QBR."}
            }
          },
          "adjacent_use_case": {
            "type": "object",
            "required": ["target_department", "champion_intro_required", "timeline"],
            "additionalProperties": false,
            "properties": {
              "target_department": {"type": ["string", "null"], "description": "The adjacent team or department for expansion."},
              "champion_intro_required": {"type": "boolean", "description": "Whether the current champion needs to introduce the product to the target department."},
              "timeline": {"type": "string"}
            }
          },
          "next_qbr_date": {
            "type": "string",
            "format": "date",
            "description": "Date of the 90-day Quarterly Business Review. Schedule at conversion."
          }
        }
      },
      "status": {
        "type": "string",
        "enum": ["converted", "pending_signature", "extended", "exited"],
        "description": "converted = signed. pending_signature = document sent, awaiting signature. extended = partial success, structured extension agreed. exited = mutual exit after failure."
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- **Salesforce Closed Won auto-trigger via DocuSign.** The automated stage update requires the DocuSign for Salesforce AppExchange package and Apex trigger configuration. Whether this is set up in the customer's Salesforce environment cannot be determined by the executor — must be confirmed during the parallel commercial track. If not set up, the executor must update Salesforce manually after receiving signature confirmation.
- **PandaDoc template token mismatch failure mode.** The SKILL.md uses tokens like `{"name": "Client.Company", "value": "Company Name"}`. If the template's token names are different (case-sensitive, different separators), the contract is generated with blank fields. This should be verified at onboarding against the actual template in the tenant's PandaDoc account, not assumed.
- **Conversion rate benchmark source.** The 30-60% conversion rate and the 3.2x figure from predefined criteria come from practitioner sources (DoWhatMatter, Getmonetizely), not controlled academic research. The ranges are widely cited but may reflect survivor bias from companies that implement structured pilot programs.
- **Discount tracking.** The artifact's `discount_offered` field on objections enables tracking of whether discounts are being systematically required for conversion. If patterns emerge (>X% of conversions require a discount to close), this signals a pricing or value-communication problem upstream, not a conversion tactic problem. This insight belongs in the strategist's `pricing-tier-structure` skill review cycle, not here.
- **"Conditional close" legal validity.** Framing the MAP as a "binding commitment" to proceed to contract if criteria are met may have legal implications depending on jurisdiction and contract form. The MAP is not a contract — it is a mutual commitment document. Final commercial terms are still executed via the formal agreement sent through PandaDoc or DocuSign.
