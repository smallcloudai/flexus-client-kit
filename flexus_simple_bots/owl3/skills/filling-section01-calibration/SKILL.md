---
name: filling-section01-calibration
description: How to fill section01-calibration of a marketing strategy.
---

# Strategy: Calibration

This is the first section. No prerequisites.

Collect initial input for marketing strategy: what we're testing, constraints, budget, timeline.

Call `update_strategy_section` with section="section01-calibration" and data matching this schema:

```json
{
  "type": "object",
  "properties": {
    "budget": {"type": "string", "description": "Budget description including channels (e.g. digital, offline)"},
    "timeline": {"type": "string", "description": "Timeline description with goals"},
    "hypothesis": {"type": "string", "description": "Full hypothesis: segment, problem, solution, test goal"},
    "additional_context": {"type": "string", "description": "Current state, test approach, constraints"},
    "product_description": {"type": "string", "description": "What the product/service is"}
  },
  "required": ["budget", "timeline", "hypothesis", "additional_context", "product_description"],
  "additionalProperties": false
}
```
