---
name: superforecasting
description: Superforecasting methodology, signal taxonomy, probability calibration, and Brier scores
---

## Tetlock's Superforecasting Principles

1. **Triage**: Focus on questions that are neither too easy nor too hard
2. **Break problems down**: Decompose into sub-questions
3. **Balance inside and outside views**: Use both domain knowledge and base rates
4. **Update incrementally**: Adjust probabilities based on new evidence
5. **Synthesize diverse views**: Consider multiple perspectives
6. **Be precise**: Use specific probabilities, not vague language
7. **Track results**: Measure accuracy over time
8. **Postmortem**: Analyze both hits and misses
9. **Distinguish signal from noise**: Not all information is useful
10. **Stay humble**: Recognize the limits of prediction

## Signal Taxonomy

### Leading Indicators
- Patent filings → technology commercialization
- Job postings → company strategy shifts
- Regulatory proposals → policy changes
- Venture capital trends → market direction

### Lagging Indicators
- Quarterly earnings → financial health
- Market share data → competitive position
- Adoption metrics → technology maturity
- Policy outcomes → regulatory impact

### Base Rate Sources
- Historical event frequency databases
- Industry benchmarks
- Academic meta-analyses
- Prediction market archives

## Probability Calibration Scale

| Probability | Verbal Expression | Typical Usage |
|------------|-------------------|---------------|
| 5% | Almost certainly not | Base rate for rare events |
| 15% | Very unlikely | Strong evidence against |
| 25% | Unlikely | More evidence against than for |
| 35% | Somewhat unlikely | Slightly more against |
| 45% | Roughly even, leaning no | Near toss-up |
| 55% | Roughly even, leaning yes | Near toss-up |
| 65% | Somewhat likely | Slightly more evidence for |
| 75% | Likely | More evidence for than against |
| 85% | Very likely | Strong evidence for |
| 95% | Almost certainly | Overwhelming evidence |

## Brier Score

### Calculation
Brier Score = (forecast probability - actual outcome)^2

Where outcome = 1 if event occurred, 0 if not.

### Benchmarks
- 0.00: Perfect prediction
- 0.10: Excellent (superforecaster level)
- 0.15: Good (above average)
- 0.20: Fair (informed guessing)
- 0.25: Random (coin flip baseline)
- 0.50+: Worse than random

### Calibration Check
Group predictions by confidence level and compare:
- Of 70% predictions, ~70% should resolve true
- If 70% predictions resolve true 90% of the time → underconfident
- If 70% predictions resolve true 50% of the time → overconfident

## Prediction Ledger Format
```json
{
  "id": "pred_001",
  "prediction": "Specific falsifiable claim",
  "probability": 0.65,
  "domain": "technology",
  "created_at": "2025-01-15",
  "deadline": "2025-07-01",
  "reasoning_chain": "1. Base rate: 30%. 2. Recent signals suggest +20%. 3. Expert consensus adds +15%.",
  "key_assumptions": ["Assumes no major regulation change", "Assumes current R&D pace continues"],
  "resolution_criteria": "Event X occurs as reported by source Y before deadline",
  "status": "active",
  "resolution": null
}
```

## Cognitive Bias Checklist

1. **Anchoring**: Am I anchored to the first number/estimate?
2. **Availability**: Am I over-weighting recent/vivid events?
3. **Confirmation**: Am I seeking only confirming evidence?
4. **Overconfidence**: Should my range be wider?
5. **Status Quo**: Am I assuming stability when change is possible?
6. **Narrative**: Am I fitting facts to a compelling story?
7. **Dunning-Kruger**: Am I less expert than I think?
8. **Groupthink**: Am I following consensus uncritically?
