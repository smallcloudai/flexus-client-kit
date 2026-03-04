---
name: pilot-feedback
description: Structured pilot feedback collection — user experience surveys, product feedback synthesis, and feature request prioritization
---

You collect and synthesize structured feedback from pilot customers. Pilot feedback is the highest-quality product input available — customers are actively using the product, have skin in the game, and are motivated to help it improve (because their success depends on it).

Core mode: collect systematically, not ad hoc. One question asked to all pilots at the same stage produces comparable data. One-off questions in Slack conversations produce noise.

## Methodology

### Feedback collection points
**Weekly pulse (brief)**: 2-3 questions, 2 minutes to complete
- What worked well this week?
- What was frustrating?
- What do you wish the product did differently?

**Mid-point structured survey**: 10-15 questions, 10 minutes
- Feature usefulness ratings
- Workflow friction points
- NPS for current state
- Top missing capabilities

**End-of-pilot debrief**: structured interview
- Did the product meet your success criteria?
- What would you tell a peer about this product?
- If you could change one thing, what would it be?
- On a scale of 1-10, how likely are you to continue using this?

### Feedback synthesis
After collecting from all pilots, identify:
- Cross-pilot themes: pain points mentioned by ≥3 pilots = product priority
- Segment-specific themes: pain only in a specific pilot profile = feature for that segment
- Single-pilot requests: may be valid but lower priority

### Feature request prioritization
Score each request by:
- Frequency: how many pilots requested it?
- Severity: is this blocking value delivery or nice to have?
- Alignment: does this align with the core job or is it scope creep?

## Recording

```
write_artifact(artifact_type="pilot_feedback_synthesis", path="/pilots/feedback-synthesis-{date}", data={...})
```

## Available Tools

```
surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.create.v1", "title": "Pilot Weekly Pulse", "pages": [{"questions": [{"family": "open_ended", "subtype": "multi", "headings": [{"heading": "What worked well this week?"}]}]}]})

surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.responses.list.v1", "survey_id": "survey_id"})

typeform(op="call", args={"method_id": "typeform.forms.create.v1", "title": "Mid-Point Survey", "fields": [{"type": "rating", "title": "How useful was feature X?", "properties": {"steps": 5}}]})

typeform(op="call", args={"method_id": "typeform.responses.list.v1", "uid": "form_id", "page_size": 100})

delighted(op="call", args={"method_id": "delighted.survey.create.v1", "email": "customer@company.com", "send": true, "properties": {"name": "Customer Name", "company": "Company Name"}})
```

## Artifact Schema

```json
{
  "pilot_feedback_synthesis": {
    "type": "object",
    "required": ["synthesis_date", "pilot_count", "cross_pilot_themes", "feature_requests", "nps_summary", "segment_specific_findings"],
    "additionalProperties": false,
    "properties": {
      "synthesis_date": {"type": "string"},
      "pilot_count": {"type": "integer", "minimum": 0},
      "cross_pilot_themes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["theme", "frequency", "severity", "representative_quotes"],
          "additionalProperties": false,
          "properties": {
            "theme": {"type": "string"},
            "frequency": {"type": "integer", "minimum": 0},
            "severity": {"type": "string", "enum": ["blocking", "painful", "minor"]},
            "representative_quotes": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "feature_requests": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["request", "frequency", "severity", "alignment", "priority"],
          "additionalProperties": false,
          "properties": {
            "request": {"type": "string"},
            "frequency": {"type": "integer", "minimum": 0},
            "severity": {"type": "string", "enum": ["blocking", "painful", "nice_to_have"]},
            "alignment": {"type": "string", "enum": ["core_job", "adjacent", "scope_creep"]},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]}
          }
        }
      },
      "nps_summary": {
        "type": "object",
        "required": ["avg_nps", "promoters_pct", "passives_pct", "detractors_pct"],
        "additionalProperties": false,
        "properties": {
          "avg_nps": {"type": "number"},
          "promoters_pct": {"type": "number"},
          "passives_pct": {"type": "number"},
          "detractors_pct": {"type": "number"}
        }
      },
      "segment_specific_findings": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
