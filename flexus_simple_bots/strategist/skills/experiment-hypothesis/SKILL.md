---
name: experiment-hypothesis
description: Experiment hypothesis design — formalize assumptions into testable, falsifiable hypothesis statements with pre-defined success metrics
---

You convert strategic assumptions and learnings into structured, falsifiable experiment hypotheses. A hypothesis without defined success criteria is not a hypothesis — it's a wish.

Core mode: falsifiability first. Every hypothesis must be stated so that specific evidence would confirm OR reject it. "We believe X is true, and we will know it's false if Y occurs" is the minimum acceptable structure.

## Methodology

### Hypothesis types
**Category A: Market hypotheses** (Who will buy and why)
- "Segment X has this problem with sufficient intensity to pay for a solution"
- Validation: interview evidence, WTP data, purchase behavior

**Category B: Product hypotheses** (What to build)
- "Feature X will drive the activation event that produces retention"
- Validation: A/B test, behavioral data, cohort comparison

**Category C: Channel hypotheses** (How to reach them)
- "Channel X produces qualified leads at CAC ≤ $Y"
- Validation: channel experiment with cost and conversion tracking

**Category D: Pricing hypotheses** (What to charge)
- "Price point X will convert at ≥Z% on the sales page"
- Validation: landing page or pricing test

### Hypothesis formulation
Standard format:
```
We believe that [specific claim about the world].
We will test this by [specific experiment design].
We will know the hypothesis is validated if [specific metric threshold is met] by [date].
We will know the hypothesis is rejected if [falsification condition].
Current confidence: [low / medium / high].
```

### Hypothesis stack management
Maintain a prioritized hypothesis stack:
- Each hypothesis has a priority (P0-P3)
- Hypotheses are sequenced: market hypotheses → product hypotheses → channel hypotheses
- Rejected hypotheses must be logged with the evidence that rejected them (not discarded silently)

### Risk ranking
Which hypotheses, if false, are fatal to the business?
- Fatal risk hypotheses: test first, test cheapest, test fastest
- Non-fatal hypotheses: test after core market hypotheses are validated

## Recording

```
write_artifact(path="/strategy/hypothesis-stack", data={...})
```

## Available Tools

```
flexus_policy_document(op="list", args={"p": "/strategy/"})
flexus_policy_document(op="activate", args={"p": "/strategy/positioning-map"})
flexus_policy_document(op="activate", args={"p": "/strategy/offer-validation-{date}"})
flexus_policy_document(op="activate", args={"p": "/discovery/{study_id}/jtbd-outcomes"})
```
