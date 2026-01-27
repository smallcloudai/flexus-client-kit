# Artifact Structure

## Design Principle: Single Document Per Workflow

Each major workflow produces **one accumulating document** rather than many small files.

Why:
- UI shows 1 doc at a time → user sees live progress
- Score/progress tracking natural within single doc
- Easier resume — everything in one place
- Simpler A2A handoffs (one path to pass)
- Strict tools can update specific sections without rewriting entire doc


## File Structure

```
/company/
├── summary                                     # A very compressed version of what the company is
├── product                                     # Product details
├── style-guide                                 # Brand colors, fonts
└── ad-ops-config                               # Facebook/LinkedIn account IDs

/gtm/
├── product/
│   └── core-truth                              # What the product actually does (not features)
│
├── discovery/
│   ├── archived/
│   └── {idea-slug}/
│       ├── idea                                # First Principles Canvas
│       └── {hypothesis-slug}/
│           └── hypothesis                      # ICP + Magic Formula + Survey results
│
├── strategy/
│   ├── archived/
│   └── {idea-slug}--{hypothesis-slug}/
│       └── strategy                            # SINGLE DOC: all steps + progress score
│
├── execution/
│   ├── archived/
│   └── {idea-slug}--{hypothesis-slug}/
│       └── runtime                             # SINGLE DOC: campaigns + spend + signals
│
└── learning/
    ├── verdicts/
    │   └── {idea}--{hyp}--verdict              # Scale/Iterate/Kill decision
    ├── insights                                # Accumulated market truths
    └── knowledge-graph                         # What works for which ICP
```


## Documents

### Strategy (Owl)

Path: `/gtm/strategy/{idea}--{hyp}/strategy`

Single doc with: `meta`, `progress`, `calibration`, `diagnostic`, `metrics`, `segment`, `messaging`, `channels`, `tactics`

Score calculated from non-null steps.


### Runtime (AdMonster)

Path: `/gtm/execution/{idea}--{hyp}/runtime`

Single doc with: `meta`, `status`, `campaigns`, `spend`, `signals`, `rules_triggered`, `notes`


### Verdict (Boss)

Path: `/gtm/learning/verdicts/{idea}--{hyp}--verdict`

Single doc with: `meta`, `decision` (scale/iterate/kill), `reasoning`, `key_learnings`, `recommendations`


## Handoff Chain

```
discovery/hypothesis
    ↓
strategy/strategy (single doc, score tracked)
    ↓
execution/runtime (single doc, live signals)
    ↓
learning/verdict
```

Each handoff passes ONE document path.


## Naming Conventions

- `{idea-slug}` — 2-4 words kebab-case capturing product concept (e.g., `unicorn-horn-car`)
- `{hypothesis-slug}` — 2-4 words kebab-case capturing customer segment (e.g., `social-media-influencers`)
- Compound paths use `--` to separate lineage: `{idea}--{hypothesis}`
- Single doc per workflow stage eliminates need for experiment-slug (strategy IS the experiment)


## UI Integration

Custom forms show progress bar based on `progress.score`, expandable sections for each step.

Form filename matches top-level key: `strategy.html`, `runtime.html`, `verdict.html`
