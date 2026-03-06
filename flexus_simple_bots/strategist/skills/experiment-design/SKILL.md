---
name: experiment-design
description: Experiment design — variant definition, control conditions, sample size calculation, instrumentation plan, and statistical validity
---

You design the execution details of a specific experiment from the hypothesis stack. Each experiment needs a control, variants, success metrics, sample size, instrumentation plan, and timeline before launch.

Core mode: pre-register everything before running. Any decision made after seeing data is post-hoc and produces false signals. Success criteria, sample size, and analysis method must be locked before the experiment starts.

## Methodology

### Experiment type selection
- **A/B test**: split traffic between control and variant. Use for: landing pages, email subject lines, onboarding flows, pricing page.
- **Holdout test**: give a segment the old experience, another the new. Use for: feature launches, algorithm changes.
- **Pre/post test**: measure before and after an intervention. Low validity (confounds with time), use only when A/B is impossible.
- **Bayesian test**: update beliefs continuously from evidence. Use for: low-traffic, high-stakes decisions where sequential testing is preferable.

### Sample size calculation
Before starting: calculate minimum sample size using:
- Baseline conversion rate (current state)
- Minimum detectable effect (smallest change worth detecting)
- Statistical power (standard: 80%)
- Significance threshold (standard: α=0.05)

Rule of thumb: 5% baseline, 20% relative lift wanted → need ~4,000 per variant for 80% power.

Never launch an experiment without verifying you have enough sample to reach significance before making a decision.

### Variant design
Control: exact current state, no changes.
Variant: exactly one change from control. Multiple changes = can't isolate cause.

Document for each variant:
- What is different vs. control?
- How is it different? (screenshot, copy, logic)
- Why this specific change? (hypothesis link)

### Instrumentation plan
What events need to be tracked to measure the primary metric and secondary metrics?
- Primary metric: the one number that determines win/lose
- Secondary (guardrail) metrics: metrics that must not get worse (e.g., retention while testing signup flow)
- Data pipeline: where does event data go? Is it instrumented before launch?

## Recording

```
write_artifact(path="/experiments/{experiment_id}/spec", data={...})
```

## Available Tools

```
flexus_policy_document(op="activate", args={"p": "/strategy/hypothesis-stack"})
flexus_policy_document(op="list", args={"p": "/experiments/"})
```
