# Artifact Structure

```
/gtm/
+-- product/
|   +-- core-truth                              # What the product actually does (not features)
|
+-- discovery/
|   +-- archived/
|   +-- {idea-slug}/
|       +-- idea                                # First Principles Canvas
|       +-- {hypothesis-slug}/
|       |   +-- hypothesis                      # ICP + Magic Formula
|       |   +-- survey-draft                    # Research design
|       |   +-- auditory-draft                  # Who to ask
|       |   +-- survey-results                  # Market signal
|       +-- {hypothesis-slug}/
|           +-- ...
|
+-- strategy/
|   +-- archived/
|   +-- {idea-slug}--{hypothesis-slug}/
|       +-- {experiment-slug}/
|       |   +-- diagnostic                      # Hypothesis classification, unknowns
|       |   +-- metrics                         # KPIs, stop/accelerate rules, MDE
|       |   +-- segment                         # ICP deep-dive, JTBD, journey
|       |   +-- messaging                       # Value prop, angles, objections
|       |   +-- channels                        # Channel selection, test cells
|       |   +-- tactics                         # Campaign specs, creatives brief
|       +-- {experiment-slug}/
|           +-- ...
|
+-- execution/
|   +-- archived/
|   +-- {idea-slug}--{hypothesis-slug}--{experiment-slug}/
|       +-- pictures/                           # Generated creatives
|       +-- runtime                             # Live campaign state, Facebook/LinkedIn IDs
|       +-- spend-log                           # Budget tracking
|       +-- signals                             # Raw metrics from platforms
|
+-- learning/
|   +-- verdicts/
|   |   +-- {idea}--{hyp}--{exp}--verdict       # Scale/Iterate/Kill decision
|   +-- insights                                # Accumulated market truths
|   +-- knowledge-graph                         # What works for which ICP
|
+-- company/
    +-- strategy                                # Mission, constraints
    +-- style-guide                             # Brand colors, fonts
    +-- ad-ops-config                           # Facebook/LinkedIn account IDs
```


## Handoff Chain

```
discovery/idea → discovery/hypothesis → strategy/tactics → execution/runtime → learning/verdict
```


## Naming Conventions

- `{idea-slug}` — 2-4 words kebab-case capturing product concept (e.g., `unicorn-horn-car`)
- `{hypothesis-slug}` — 2-4 words kebab-case capturing customer segment (e.g., `social-media-influencers`)
- `{experiment-slug}` — 2-4 words kebab-case capturing test approach (e.g., `meta-engagement-test`)
- Compound paths use `--` to separate lineage: `{idea}--{hypothesis}--{experiment}`
