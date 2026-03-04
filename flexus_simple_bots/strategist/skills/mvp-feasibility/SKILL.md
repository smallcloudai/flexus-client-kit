---
name: mvp-feasibility
description: MVP feasibility assessment — technical, resource, timeline, and dependency risk evaluation before committing to build
---

You assess the feasibility of a proposed MVP scope before resources are committed. Feasibility is not a veto — it is a risk inventory that allows the team to make go/no-go decisions with full awareness of constraints.

Core mode: surface all blockers and risks explicitly. Optimism kills feasibility assessments. The purpose of this skill is to find the things that will go wrong, not to confirm the things that will go right.

## Methodology

### Technical feasibility
Review the in-scope features from `mvp_scope` against:
- Required technical capabilities (does the team have them or need to hire?)
- Required external dependencies (APIs, infrastructure, integrations)
- Data requirements (is the required data available, owned, or licensable?)
- Security / compliance implications (GDPR, SOC2, industry regulations)

For each capability gap, classify:
- Build: can be built in-house within timeline
- Buy: needs licensed component or vendor
- Partner: requires a third-party to provide (adds timeline risk)
- Block: cannot be resolved within MVP timeline

### Resource feasibility
For the proposed MVP scope:
- Engineering estimate (story points or t-shirt sizes per feature)
- Design estimate (screens, components, flow design required)
- QA estimate (testing scope)
- Total estimate vs. available capacity

If capacity is insufficient: recommend which features to defer to keep timeline.

### Timeline feasibility
Given resource estimate and available capacity:
- Can MVP be delivered within the window required for hypothesis testing?
- What are the critical path dependencies (what must be done before what)?
- What is the risk multiplier? (First time building this type of system = 1.5x-2x estimate)

### Dependencies and risks
External dependencies that create timeline risk:
- Third-party API access and approval processes
- Legal/compliance reviews
- Hardware procurement (if relevant)
- Beta customer commitment timelines

## Recording

```
write_artifact(artifact_type="mvp_feasibility_assessment", path="/strategy/mvp-feasibility", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
```

## Artifact Schema

```json
{
  "mvp_feasibility_assessment": {
    "type": "object",
    "required": ["assessed_at", "overall_feasibility", "technical_risks", "resource_estimate", "timeline_estimate", "blockers", "recommendations"],
    "additionalProperties": false,
    "properties": {
      "assessed_at": {"type": "string"},
      "overall_feasibility": {"type": "string", "enum": ["feasible", "feasible_with_changes", "infeasible"]},
      "technical_risks": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["risk", "resolution_type", "severity"],
          "additionalProperties": false,
          "properties": {
            "risk": {"type": "string"},
            "resolution_type": {"type": "string", "enum": ["build", "buy", "partner", "block"]},
            "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
            "mitigation": {"type": "string"}
          }
        }
      },
      "resource_estimate": {
        "type": "object",
        "required": ["engineering_weeks", "design_weeks", "qa_weeks"],
        "additionalProperties": false,
        "properties": {
          "engineering_weeks": {"type": "number", "minimum": 0},
          "design_weeks": {"type": "number", "minimum": 0},
          "qa_weeks": {"type": "number", "minimum": 0},
          "estimate_confidence": {"type": "string", "enum": ["high", "medium", "low"]}
        }
      },
      "timeline_estimate": {
        "type": "object",
        "required": ["optimistic_weeks", "realistic_weeks", "pessimistic_weeks"],
        "additionalProperties": false,
        "properties": {
          "optimistic_weeks": {"type": "number", "minimum": 0},
          "realistic_weeks": {"type": "number", "minimum": 0},
          "pessimistic_weeks": {"type": "number", "minimum": 0},
          "critical_path": {"type": "array", "items": {"type": "string"}}
        }
      },
      "blockers": {"type": "array", "items": {"type": "string"}},
      "recommendations": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
