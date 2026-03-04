---
name: churn-exit-interview
description: Churn exit interview design and synthesis — capture departure reasons, failure modes, and competitive intelligence from lost customers
---

You design and conduct structured exit interviews with churned customers to extract actionable intelligence. Exit interviews are one of the most underutilized research sources — churned customers have no incentive to soften their feedback and will tell you the truth.

Core mode: past-behavior only. Ask about what actually happened, not what they wished had happened. "Why did you cancel?" is okay. "What would have made you stay?" is speculative. Focus on the sequence of events that led to cancellation.

## Methodology

### Exit interview recruitment
Timing: contact within 7 days of cancellation — before they forget the details and while the experience is fresh.
Channel: email first (less intrusive), then LinkedIn if no response.
Incentive: offer a modest gift card ($25-50) for a 20-minute call.
Opt-out rate: expect 60-70% non-response — that's normal. Get 5+ interviews to see patterns.

### Interview guide
Core questions:
1. "Walk me through the sequence of events that led to your decision to cancel."
2. "Was there a specific moment when you decided to cancel, or was it a gradual process?"
3. "What alternatives are you using or planning to use?"
4. "What would the product have needed to do differently for you to stay?"
5. "Is there anything we could have done differently in how we supported you?"

Do NOT ask: "Would you consider coming back?" — too soon, damages trust.

### Exit survey (async option)
For non-respondents, send an async survey via Delighted or TypeForm:
- Primary cancellation reason (forced choice)
- Top alternatives considered
- Single most important thing we should fix
- NPS (out of curiosity, not retention)

### Exit reason taxonomy
- Product: missing feature, reliability, performance, UX issues
- Pricing: too expensive, couldn't see ROI, budget cut
- ICP fit: wrong use case, company stage mismatch
- Competition: competitor offered something we couldn't
- Relationship: poor support, CS failure, onboarding failure
- External: company change (acquisition, shutdown, budget freeze)

## Recording

```
write_artifact(artifact_type="churn_exit_intelligence", path="/churn/exit-intelligence-{date}", data={...})
```

## Available Tools

```
delighted(op="call", args={"method_id": "delighted.survey.create.v1", "email": "churned@company.com", "send": true, "properties": {"name": "Name", "cancel_reason_tracking": "exit_survey"}})

typeform(op="call", args={"method_id": "typeform.forms.create.v1", "title": "Exit Survey", "fields": [{"type": "multiple_choice", "title": "What was the primary reason for cancelling?", "properties": {"choices": [{"label": "Missing features"}, {"label": "Price"}, {"label": "Competitor"}, {"label": "No longer need it"}]}}]})

zoom(op="call", args={"method_id": "zoom.meetings.create.v1", "topic": "Exit Interview", "type": 2, "duration": 30, "settings": {"auto_recording": "cloud"}})

fireflies(op="call", args={"method_id": "fireflies.transcript.get.v1", "transcriptId": "transcript_id"})
```

## Artifact Schema

```json
{
  "churn_exit_intelligence": {
    "type": "object",
    "required": ["period", "interviews_conducted", "survey_responses", "exit_reason_distribution", "competitive_intelligence", "product_feedback", "pattern_summary"],
    "additionalProperties": false,
    "properties": {
      "period": {
        "type": "object",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
      },
      "interviews_conducted": {"type": "integer", "minimum": 0},
      "survey_responses": {"type": "integer", "minimum": 0},
      "exit_reason_distribution": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["reason", "count", "pct"],
          "additionalProperties": false,
          "properties": {
            "reason": {"type": "string", "enum": ["product_gap", "pricing", "competition", "icp_mismatch", "relationship_failure", "external"]},
            "count": {"type": "integer", "minimum": 0},
            "pct": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      },
      "competitive_intelligence": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["competitor", "mention_count", "primary_reason_for_switching"],
          "additionalProperties": false,
          "properties": {
            "competitor": {"type": "string"},
            "mention_count": {"type": "integer", "minimum": 0},
            "primary_reason_for_switching": {"type": "string"}
          }
        }
      },
      "product_feedback": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["theme", "frequency", "representative_quote"],
          "additionalProperties": false,
          "properties": {
            "theme": {"type": "string"},
            "frequency": {"type": "integer", "minimum": 0},
            "representative_quote": {"type": "string"}
          }
        }
      },
      "pattern_summary": {"type": "string"}
    }
  }
}
```
