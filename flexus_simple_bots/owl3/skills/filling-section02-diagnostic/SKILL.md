---
name: filling-section02-diagnostic
description: How to fill section02-diagnostic of a marketing strategy.
---

# Strategy: Diagnostic Analysis

Requires section01-calibration to be completed first.

This section analyzes the hypothesis: classifies type, identifies unknowns, assesses feasibility.

Call `update_strategy_section` with section="section02-diagnostic" and data matching this schema:

```json
{
  "type": "object",
  "properties": {
    "normalized_hypothesis": {"type": "string", "description": "Clear restatement of what we're testing"},
    "primary_type": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion", "retention"]},
    "primary_type_reasoning": {"type": "string", "description": "Why this type applies"},
    "secondary_types": {"type": "array", "items": {"type": "string", "enum": ["value", "segment", "messaging", "channel", "pricing", "conversion", "retention"]}},
    "secondary_types_reasoning": {"type": "string", "description": "Why these secondary types apply"},
    "testable_with_traffic": {"type": "boolean"},
    "recommended_test_mechanisms": {"type": "array", "items": {"type": "string", "enum": ["paid_traffic", "content", "waitlist", "outbound", "partnerships"]}},
    "uncertainty_level": {"type": "string", "enum": ["low", "medium", "high", "extreme"]},
    "uncertainty_reasoning": {"type": "string", "description": "What makes it this uncertainty level"},
    "key_unknowns": {"type": "array", "items": {"type": "string"}},
    "limitations": {"type": "array", "items": {"type": "string"}},
    "needs_additional_methods": {"type": "array", "items": {"type": "string", "enum": ["none", "custdev", "desk_research", "product_experiment"]}},
    "feasibility_score": {"type": "number", "minimum": 0, "maximum": 1},
    "feasibility_reasoning": {"type": "string", "description": "What makes it feasible or not"},
    "detailed_analysis": {"type": "string", "description": "Rich markdown: what we're testing, why it matters, what the answer tells us"},
    "key_decisions_ahead": {"type": "array", "items": {"type": "string"}},
    "next_steps": {"type": "array", "items": {"type": "string"}},
    "questions_to_resolve": {"type": "array", "items": {"type": "string"}}
  },
  "required": [
    "normalized_hypothesis", "primary_type", "primary_type_reasoning",
    "secondary_types", "secondary_types_reasoning",
    "testable_with_traffic", "recommended_test_mechanisms",
    "uncertainty_level", "uncertainty_reasoning", "key_unknowns", "limitations",
    "needs_additional_methods", "feasibility_score", "feasibility_reasoning",
    "detailed_analysis", "key_decisions_ahead", "next_steps", "questions_to_resolve"
  ],
  "additionalProperties": false
}
```
