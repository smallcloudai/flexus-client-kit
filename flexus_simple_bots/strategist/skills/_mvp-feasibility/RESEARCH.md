# Research: mvp-feasibility

**Skill path:** `strategist/skills/mvp-feasibility/`
**Bot:** strategist (researcher | strategist | executor)
**Research date:** 2026-03-04
**Status:** complete

---

## Context

`mvp-feasibility` is the strategist skill used before build commitment to determine whether the proposed MVP scope is realistically deliverable under technical, resource, timeline, dependency, and governance constraints. The skill is not a veto mechanism; it is a structured risk inventory that supports explicit go / no-go / scope-cut decisions.

The current `SKILL.md` already establishes the core structure (`build | buy | partner | block`, capacity and timeline estimates, dependency risks, and a base artifact schema). This research extends that base with 2024-2026 evidence on: modern pre-build feasibility workflows, constraints and tooling limits, evidence quality interpretation, and recurring failure modes seen in major incidents and delivery postmortems. Older sources are explicitly labeled as evergreen when they remain operationally valid.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered (see Research Angles section)
- [x] Each finding has a source URL or named reference
- [x] Methodology section covers practical how-to, not just theory
- [x] Tool/API landscape is mapped with at least 3-5 concrete options
- [x] At least one "what not to do" / common failure mode is documented
- [x] Output schema recommendations are grounded in real-world data shapes
- [x] Gaps section honestly lists what was NOT found or is uncertain
- [x] All findings are from 2024-2026 unless explicitly marked as evergreen

---

## Quality Gates

Before marking status `complete`, verify:

- [x] No generic filler without concrete backing
- [x] No invented tool names, method IDs, or API endpoints - only verified real ones
- [x] Contradictions between sources are explicitly noted, not silently resolved
- [x] Volume: findings sections are within 800-4000 words combined
- [x] Volume: `Draft Content for SKILL.md` is longer than all Findings sections combined

---

## Research Angles

### Angle 1: Domain Methodology and Best Practices
> How do practitioners actually do this in 2025-2026? What frameworks, mental models, step-by-step processes exist? What has changed recently?

**Findings:**

1. **High-performing teams now run feasibility as a staged pre-build workflow, not one meeting.**  
   Practical sequence seen across Atlassian and Microsoft playbooks: problem framing (`Project Poster`), structured risk discovery (`Premortem`), dependency inventory (`Dependency Mapping`), uncertainty reduction (`Engineering Feasibility Spikes`), option comparison (`Trade Study`), decision record (`ADR/Decision Log`), then final go/no-go review. This materially reduces hidden assumptions before engineering commitment.  
   Sources: https://www.atlassian.com/team-playbook/plays/project-poster, https://www.atlassian.com/wac/team-playbook/plays/pre-mortem, https://www.atlassian.com/team-playbook/plays/dependency-mapping, https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/recipes/engineering-feasibility-spikes/, https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/trade-studies/, https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/

2. **Premortem moved from "brainstorming exercise" to operational gate.**  
   Atlassian specifies concrete session design (3-11 participants, timeboxed, voting, owner assignment), making it a repeatable risk surfacing method rather than informal discussion.  
   Source: https://www.atlassian.com/wac/team-playbook/plays/pre-mortem (evergreen process, currently maintained)

3. **Dependency mapping now includes ownership and review cadence, not just diagrams.**  
   Current dependency mapping guidance requires risks, mitigations, owners, and cadence (weekly/monthly/quarterly), aligning with feasibility needs for external blockers and cross-team sequencing.  
   Source: https://www.atlassian.com/team-playbook/plays/dependency-mapping

4. **Feasibility spikes are increasingly formalized as pre-build de-risking artifacts.**  
   Microsoft guidance (updated 2024) positions spikes between design review and engineering sprints, with explicit pre-mortem and weekly feedback loops.  
   Source: https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/recipes/engineering-feasibility-spikes/

5. **Trade studies and decision logs are now treated as mandatory traceability in uncertain architecture choices.**  
   The combination prevents undocumented decision drift and supports post-hoc explanation of why a path was chosen under uncertainty.  
   Sources: https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/trade-studies/, https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/ (evergreen methods, currently maintained)

6. **Reliability feasibility shifted to continuously updated cloud checklists in 2024-2026.**  
   AWS, Azure, and GCP all shipped meaningful framework updates, including AI/ML perspectives and revised reliability practices. Feasibility methods therefore need periodic refresh; static checklists decay quickly.  
   Sources: https://aws.amazon.com/blogs/architecture/announcing-updates-to-the-aws-well-architected-framework-guidance-3/, https://aws.amazon.com/about-aws/whats-new/2025/11/new-aws-well-architected-lenses-ai-ml-workloads/, https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist, https://docs.cloud.google.com/architecture/framework/whats-new, https://docs.cloud.google.com/architecture/framework/reliability

7. **AI-heavy MVPs need explicit risk framework triggers, not generic software feasibility only.**  
   NIST AI RMF GenAI Profile (2024) adds concrete risk categories and governance actions; EU AI Act timeline introduces phased legal dependencies that can become launch blockers.  
   Sources: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence, https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958388, https://airc.nist.gov/airmf-resources/playbook, https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline

8. **Delivery feasibility must now separate local productivity from system-level delivery performance.**  
   DORA 2024 reports cases where AI adoption improves local coding/review activity while aggregate throughput/stability can decline, making "faster coding" an insufficient feasibility argument.  
   Sources: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report, https://services.google.com/fh/files/misc/2024_final_dora_report.pdf

**Sources:**
- https://www.atlassian.com/team-playbook/plays/project-poster
- https://www.atlassian.com/wac/team-playbook/plays/pre-mortem
- https://www.atlassian.com/team-playbook/plays/dependency-mapping
- https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/recipes/engineering-feasibility-spikes/
- https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/trade-studies/
- https://microsoft.github.io/code-with-engineering-playbook/design/design-reviews/decision-log/
- https://aws.amazon.com/blogs/architecture/announcing-updates-to-the-aws-well-architected-framework-guidance-3/
- https://aws.amazon.com/about-aws/whats-new/2025/11/new-aws-well-architected-lenses-ai-ml-workloads/
- https://learn.microsoft.com/en-us/azure/well-architected/reliability/checklist
- https://docs.cloud.google.com/architecture/framework/whats-new
- https://docs.cloud.google.com/architecture/framework/reliability
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958388
- https://airc.nist.gov/airmf-resources/playbook
- https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline
- https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- https://services.google.com/fh/files/misc/2024_final_dora_report.pdf

---

### Angle 2: Tool and API Landscape
> What tools, APIs, and data providers exist for this domain? What are their actual capabilities, limitations, pricing tiers, rate limits? What are the de-facto industry standards?

**Findings:**

1. **Cloud quota services are first-line feasibility controls for technical constraints.**  
   AWS Service Quotas, GCP Quotas, and Azure Quotas reveal hard limits and increase workflows that directly affect launch feasibility and lead time.  
   Sources: https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html, https://cloud.google.com/docs/quotas/overview, https://learn.microsoft.com/en-us/azure/quotas/quotas-overview

2. **Quota increase pathways themselves are feasibility risks.**  
   Quotas differ by region/service, many are non-adjustable, and some increase workflows require support paths or preconditions. MVP plans without increase lead-time assumptions often understate timeline risk.  
   Sources: https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html, https://cloud.google.com/docs/quotas/view-manage, https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits

3. **Roadmap/capacity tools are useful but frequently plan-gated.**  
   Jira Advanced Roadmaps capacity planning is available only on specific cloud tiers, so feasibility methods must check tool access assumptions early.  
   Sources: https://support.atlassian.com/jira-software-cloud/docs/enable-capacity-planning-in-advanced-roadmaps/, https://www.atlassian.com/software/jira/pricing?tab=cloud

4. **Data ingestion pipelines for feasibility telemetry are rate-limit-constrained by design.**  
   Jira Cloud, GitHub REST, and GitHub GraphQL enforce quotas and secondary/resource limits. Forecasting pipelines must be budget-aware and retry-aware to remain reliable.  
   Sources: https://developer.atlassian.com/cloud/jira/platform/rate-limiting/, https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api, https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api, https://github.blog/changelog/2025-09-01-graphql-api-resource-limits/

5. **Dependency risk needs multi-source security evidence, not one feed.**  
   Dependabot, NVD, OSV, and CISA KEV each provide different signal quality and coverage. Single-source approaches miss either exploit prioritization or breadth.  
   Sources: https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts, https://nvd.nist.gov/developers/start-here, https://google.github.io/osv.dev/api/, https://www.cisa.gov/known-exploited-vulnerabilities-catalog

6. **Compliance tooling introduces licensing and scope constraints that directly impact feasibility.**  
   AWS Audit Manager, Google Assured Workloads, and Microsoft Purview Compliance Manager expose practical evidence and policy workflows but have tier/licensing caveats and non-equivalence to legal sign-off.  
   Sources: https://aws.amazon.com/audit-manager/pricing/, https://cloud.google.com/assured-workloads/docs/restrictions-limitations, https://learn.microsoft.com/en-us/purview/compliance-manager-faq?view=o365-worldwide

7. **Cost feasibility tooling is directional, not authoritative.**  
   AWS Pricing Calculator is useful for scenario comparisons but requires explicit assumption logging and sensitivity bands.  
   Source: https://aws.amazon.com/aws-cost-management/aws-pricing-calculator/pricing/

8. **Timeline confidence improves when flow-history forecasting is used.**  
   Monte Carlo style flow forecasting tools (for example ActionableAgile) support probabilistic schedule ranges rather than single-point commitments.  
   Sources: https://marketplace.atlassian.com/apps/1216661/actionableagile-analytics-kanban-agile-metrics-forecasts?hosting=cloud&tab=overview, https://www.55degrees.se/products/actionableagileanalytics/pricing

**Sources:**
- https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html
- https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html
- https://cloud.google.com/docs/quotas/overview
- https://cloud.google.com/docs/quotas/view-manage
- https://learn.microsoft.com/en-us/azure/quotas/quotas-overview
- https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits
- https://support.atlassian.com/jira-software-cloud/docs/enable-capacity-planning-in-advanced-roadmaps/
- https://www.atlassian.com/software/jira/pricing?tab=cloud
- https://developer.atlassian.com/cloud/jira/platform/rate-limiting/
- https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api
- https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api
- https://github.blog/changelog/2025-09-01-graphql-api-resource-limits/
- https://docs.github.com/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts
- https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference
- https://nvd.nist.gov/developers/start-here
- https://google.github.io/osv.dev/api/
- https://osv.dev/docs/
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- https://github.com/cisagov/kev-data
- https://aws.amazon.com/audit-manager/pricing/
- https://cloud.google.com/assured-workloads/docs/restrictions-limitations
- https://learn.microsoft.com/en-us/purview/compliance-manager-faq?view=o365-worldwide
- https://aws.amazon.com/aws-cost-management/aws-pricing-calculator/pricing/
- https://marketplace.atlassian.com/apps/1216661/actionableagile-analytics-kanban-agile-metrics-forecasts?hosting=cloud&tab=overview
- https://www.55degrees.se/products/actionableagileanalytics/pricing

---

### Angle 3: Data Interpretation and Signal Quality
> How do practitioners interpret the data from these tools? What thresholds matter? What's signal vs noise? What are common misinterpretations? What benchmarks exist?

**Findings:**

1. **Data integrity checks should gate interpretation, not decorate it.**  
   Microsoft ExP and Statsig both treat SRM and health checks as blockers for trustworthy interpretation. Thresholds differ by implementation (`p < 0.0005` and `p < 0.01` are both used), but the core pattern is consistent: invalid randomization invalidates conclusions.  
   Sources: https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/, https://docs.statsig.com/stats-engine/methodologies/srm-checks/, https://www.statsig.com/blog/sample-ratio-mismatch

2. **Decision quality improves with explicit rule-based ship logic.**  
   Spotify's risk-aware decision framework demonstrates practical rules combining success metrics, guardrails, and validity checks, reducing ad-hoc interpretation drift.  
   Sources: https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/, https://arxiv.org/abs/2402.11609, https://confidence.spotify.com/blog/better-decisions-with-guardrails

3. **Uncertainty reporting is required for practical feasibility interpretation.**  
   NIST guidance emphasizes expanded uncertainty and transparent reporting, showing why point estimates alone are inadequate for decisions with delivery risk exposure.  
   Sources: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-6-expanded-uncertainty, https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-7-reporting-uncertainty (evergreen, still operationally valid)

4. **Continuous monitoring requires sequential-valid methods.**  
   If teams repeatedly "peek" and stop when significance appears, false positive risk inflates. Always-valid sequential methods are the accepted mitigation.  
   Source: https://arxiv.org/abs/1512.04922 (evergreen)

5. **Operational feasibility should use error-budget policy as a hard decision signal.**  
   Google SRE recommends freeze-style policy responses when budget is exhausted; this converts reliability from narrative to enforceable gate.  
   Sources: https://sre.google/workbook/error-budget-policy/, https://sre.google/workbook/implementing-slos/ (evergreen)

6. **Technical readiness should be level-based for critical capabilities.**  
   NASA TRL and GAO readiness guidance remain useful to avoid committing MVP timelines against immature core components.  
   Sources: https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/, https://www.gao.gov/products/gao-20-48g (evergreen)

7. **Delivery signal must combine throughput and stability dimensions.**  
   DORA guidance warns against reading speed metrics in isolation; stability and rework characteristics change feasibility outcomes.  
   Sources: https://dora.dev/guides/dora-metrics/, https://dora.dev/guides/dora-metrics/history, https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report

8. **Business feasibility signals are stronger when retention/efficiency are included.**  
   Private SaaS surveys and benchmark analyses show retention and growth-quality metrics are better early feasibility signals than vanity growth alone.  
   Sources: https://sapphireventures.com/press/keybanc-capital-markets-and-sapphire-ventures-private-saas-company-survey-reveals-a-continued-focus-on-operational-efficiency-and-profitability/, https://www.saas-capital.com/blog-posts/growth-benchmarks-for-private-saas-companies/, https://www.saas-capital.com/blog-posts/growth-profitability-and-the-rule-of-40-for-private-saas-companies/

9. **Vanity metrics still drive false confidence when guardrails are absent.**  
   This remains a known failure mode from Lean Startup era to modern delivery metrics discourse (Goodhart effect in practice).  
   Sources: https://www.startuplessonslearned.com/2009/12/why-vanity-metrics-are-dangerous.html (evergreen), https://dora.dev/guides/dora-metrics/, https://pmc.ncbi.nlm.nih.gov/articles/PMC7901608/ (evergreen)

**Sources:**
- https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/
- https://docs.statsig.com/stats-engine/methodologies/srm-checks/
- https://www.statsig.com/blog/sample-ratio-mismatch
- https://engineering.atspotify.com/2024/03/risk-aware-product-decisions-in-a-b-tests-with-multiple-metrics/
- https://arxiv.org/abs/2402.11609
- https://confidence.spotify.com/blog/better-decisions-with-guardrails
- https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-6-expanded-uncertainty
- https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-7-reporting-uncertainty
- https://arxiv.org/abs/1512.04922
- https://sre.google/workbook/error-budget-policy/
- https://sre.google/workbook/implementing-slos/
- https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/
- https://www.gao.gov/products/gao-20-48g
- https://dora.dev/guides/dora-metrics/
- https://dora.dev/guides/dora-metrics/history
- https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- https://sapphireventures.com/press/keybanc-capital-markets-and-sapphire-ventures-private-saas-company-survey-reveals-a-continued-focus-on-operational-efficiency-and-profitability/
- https://www.saas-capital.com/blog-posts/growth-benchmarks-for-private-saas-companies/
- https://www.saas-capital.com/blog-posts/growth-profitability-and-the-rule-of-40-for-private-saas-companies/
- https://www.startuplessonslearned.com/2009/12/why-vanity-metrics-are-dangerous.html
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7901608/

---

### Angle 4: Failure Modes and Anti-Patterns
> What goes wrong in practice? What are the most common mistakes, gotchas, and traps? What does bad output look like vs good output?

**Findings:**

1. **Single-point estimate theater**  
   Detection: one delivery date and one budget, no probabilistic range, no confidence rationale.  
   Consequence: false feasibility confidence and predictable slip.  
   Mitigation: require at least P50/P80 ranges and explicit optimism-bias adjustment.  
   Sources: https://www.bcg.com/publications/2024/most-large-scale-tech-programs-fail-how-to-succeed, https://www.gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias, https://www.gao.gov/products/gao-09-3sp (evergreen)

2. **Missing critical path and dependency ownership**  
   Detection: local team plans exist, but no integrated critical path with owners.  
   Consequence: late blocker discovery and cascade delays.  
   Mitigation: single master dependency plan with owner and review cadence.  
   Sources: https://www.bcg.com/publications/2024/most-large-scale-tech-programs-fail-how-to-succeed, https://www.nao.org.uk/insights/governments-approach-to-technology-suppliers-addressing-the-challenges/

3. **Unverified assumptions marked as closed**  
   Detection: assumption status says done, but no direct validation evidence.  
   Consequence: production impact from hidden false premise.  
   Mitigation: mandatory machine+human verification checkpoints before irreversible changes.  
   Source: https://blog.cloudflare.com/cloudflare-incident-on-september-17-2024

4. **Legacy impact blind spot**  
   Detection: risk register ignores legacy paths because they are "stable".  
   Consequence: regressions via poorly understood old logic.  
   Mitigation: legacy hotspot mapping and additional uncertainty buffer.  
   Source: https://blog.cloudflare.com/cloudflare-incident-on-september-17-2024

5. **Uneven quality gates for non-code updates**  
   Detection: config/content update pipelines have weaker testing than code release pipelines.  
   Consequence: high-blast-radius incidents from seemingly minor updates.  
   Mitigation: parity testing policy across code/config/content release artifacts.  
   Sources: https://www.techtarget.com/searchsecurity/news/366596579/CrowdStrike-Content-validation-bug-led-to-global-outage, https://www.techtarget.com/searchsecurity/news/366602392/CrowdStrike-details-errors-that-led-to-mass-IT-outage, https://www.crowdstrike.com/en-us/blog/channel-file-291-rca-available/

6. **Big-bang rollout default**  
   Detection: full-fleet deployment without progressive ring/canary rules.  
   Consequence: maximum blast radius on defect.  
   Mitigation: staged rollout + measurable promotion gates + automatic rollback thresholds.  
   Sources: https://sre.google/workbook/canarying-releases/ (evergreen), https://www.techtarget.com/searchsecurity/news/366602392/CrowdStrike-details-errors-that-led-to-mass-IT-outage

7. **Fail-safe path exists on paper but is untested under load/misconfiguration**  
   Detection: "we have fallback" without overload validation evidence.  
   Consequence: cascade failures when fallback path itself breaks.  
   Mitigation: regular overload and misconfiguration drills as launch gate.  
   Source: https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/

8. **Late security discovery and remediation bottlenecks**  
   Detection: vulnerabilities discovered primarily after merge, with process friction blocking fixes.  
   Consequence: security debt converts directly into schedule debt.  
   Mitigation: shift-left controls plus pre-approved remediation escalation paths.  
   Source: https://about.gitlab.com/press/releases/2024-06-25-gitlab-survey-reveals-tension-around-ai-security-and-developer-productivity-within-organizations/

9. **Supply-chain visibility gap**  
   Detection: no SBOM or vendor criticality model in feasibility package.  
   Consequence: underestimating third-party incident likelihood and duration.  
   Mitigation: mandatory SBOM and vendor tiering in MVP readiness checks.  
   Sources: https://about.gitlab.com/press/releases/2024-06-25-gitlab-survey-reveals-tension-around-ai-security-and-developer-productivity-within-organizations/, https://www.verizon.com/about/news/2025-data-breach-investigations-report

10. **Compliance treated as post-MVP concern**  
    Detection: no legal/regulatory milestones on delivery timeline.  
    Consequence: launch block or forced de-scope near release.  
    Mitigation: regulation-dependent milestones and evidence obligations in baseline feasibility plan.  
    Sources: https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en, https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline, https://www.federalregister.gov/documents/2023/08/04/2023-16194/cybersecurity-risk-management-strategy-governance-and-incident-disclosure (evergreen regulatory baseline)

11. **Identity baseline missing for internet-facing systems**  
    Detection: critical external systems without MFA-by-default.  
    Consequence: preventable compromise with severe downstream business impact.  
    Mitigation: MFA-by-default and explicit external asset control attestation before go decision.  
    Sources: https://www.cnbc.com/2024/05/01/unitedhealth-ceo-says-company-paid-hackers-22-million-ransom.html, https://www.cisa.gov/securebydesign, https://www.cisa.gov/securebydesign/pledge

12. **AI productivity illusion in feasibility narratives**  
    Detection: claims of faster coding without explicit controls on batch size, testing rigor, and stability impact.  
    Consequence: local speed gains with system-level delivery degradation.  
    Mitigation: treat throughput and stability as dual hard gates when AI tools are involved.  
    Sources: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report, https://dora.dev/research/2024/dora-report

**Sources:**
- https://www.bcg.com/publications/2024/most-large-scale-tech-programs-fail-how-to-succeed
- https://www.bcg.com/publications/2024/software-projects-dont-have-to-be-late-costly-and-irrelevant
- https://www.gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias
- https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/191507/Optimism_bias.pdf
- https://www.gao.gov/products/gao-09-3sp
- https://www.nao.org.uk/insights/governments-approach-to-technology-suppliers-addressing-the-challenges/
- https://blog.cloudflare.com/cloudflare-incident-on-september-17-2024
- https://blog.cloudflare.com/cloudflare-incident-on-november-14-2024-resulting-in-lost-logs/
- https://www.techtarget.com/searchsecurity/news/366596579/CrowdStrike-Content-validation-bug-led-to-global-outage
- https://www.techtarget.com/searchsecurity/news/366602392/CrowdStrike-details-errors-that-led-to-mass-IT-outage
- https://www.crowdstrike.com/en-us/blog/channel-file-291-rca-available/
- https://sre.google/workbook/canarying-releases/
- https://about.gitlab.com/press/releases/2024-06-25-gitlab-survey-reveals-tension-around-ai-security-and-developer-productivity-within-organizations/
- https://www.verizon.com/about/news/2025-data-breach-investigations-report
- https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en
- https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline
- https://www.federalregister.gov/documents/2023/08/04/2023-16194/cybersecurity-risk-management-strategy-governance-and-incident-disclosure
- https://www.cnbc.com/2024/05/01/unitedhealth-ceo-says-company-paid-hackers-22-million-ransom.html
- https://www.cisa.gov/securebydesign
- https://www.cisa.gov/securebydesign/pledge
- https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
- https://dora.dev/research/2024/dora-report

---

### Angle 5: Regulatory and Governance Timing Constraints
> What legal/governance timing dependencies commonly shift feasibility outcomes?

**Findings:**

1. **EU AI Act creates phased obligations (2025-2027) that can turn into hard timeline blockers for AI MVPs.**  
   Feasibility assessment must explicitly map target-market obligations to launch window.  
   Sources: https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en, https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline

2. **NIST AI RMF GenAI Profile is voluntary but operationally useful as readiness structure.**  
   It provides concrete risk categories and control planning language that can be converted into artifact-level checks.  
   Sources: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence, https://airc.nist.gov/airmf-resources/playbook

3. **Disclosure obligations (for example SEC cyber incident disclosure timing) affect operational feasibility assumptions.**  
   Even if not directly in MVP feature scope, incident reporting requirements influence readiness, detection, and governance process design.  
   Source: https://www.federalregister.gov/documents/2023/08/04/2023-16194/cybersecurity-risk-management-strategy-governance-and-incident-disclosure (evergreen legal baseline)

4. **Compliance score tooling is not equivalent to legal compliance proof.**  
   Vendor compliance platforms provide evidence support, but legal/regulatory sufficiency remains contextual and often requires separate review.  
   Sources: https://learn.microsoft.com/en-us/purview/compliance-manager-faq?view=o365-worldwide, https://aws.amazon.com/audit-manager/pricing/

**Sources:**
- https://commission.europa.eu/news/ai-act-enters-force-2024-08-01_en
- https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- https://airc.nist.gov/airmf-resources/playbook
- https://www.federalregister.gov/documents/2023/08/04/2023-16194/cybersecurity-risk-management-strategy-governance-and-incident-disclosure
- https://learn.microsoft.com/en-us/purview/compliance-manager-faq?view=o365-worldwide
- https://aws.amazon.com/audit-manager/pricing/

---

## Synthesis

The evidence converges on one core shift: feasibility is now a workflow with hard gates, not a one-time estimate. The strongest 2024-2026 pattern is staged de-risking before build commitment, combining lightweight discovery methods (problem framing, premortem, dependency mapping, spikes) with explicit decision traceability (trade studies and decision logs). Teams that skip this sequence tend to carry implicit assumptions into implementation, where correction is more expensive.

A second convergence is "constraints realism." Tooling for quotas, rate limits, compliance evidence, and dependency risk is mature, but each tool carries access tiers, scope limits, and operational caveats. This means the feasibility process must evaluate both business idea viability and instrumentation viability: can the team continuously gather reliable feasibility evidence without violating API budgets, quota ceilings, or governance boundaries?

The biggest interpretation risk remains false confidence. Across experimentation, delivery, and operations literature, high-quality decisions require data-integrity checks first, uncertainty reporting, and explicit decision rules. Point estimates, vanity metrics, and isolated speed metrics consistently correlate with avoidable wrong-way commitments.

The most actionable contradiction is speed vs rigor. Lightweight methods improve tempo; governance and reliability checks add overhead. The practical answer is not to choose one side globally, but to define escalation triggers: start lightweight, escalate when dependency criticality, external exposure, AI/regulatory risk, or reliability blast radius increases. This lets feasibility stay fast for low-risk MVPs while remaining strict for high-consequence launches.

---

## Recommendations for SKILL.md

- [x] Replace current methodology with a mandatory staged feasibility workflow (problem framing -> premortem -> dependency mapping -> spikes -> trade study -> decision record -> verdict).
- [x] Add explicit evidence-quality gates (`data_integrity`, `uncertainty`, `decision_rule_passed`) before allowing `overall_feasibility` verdict.
- [x] Add probabilistic timeline guidance (at least P50/P80) and prohibit single-point estimate decisions.
- [x] Add dual delivery signal rule (throughput + stability) and error-budget gate for operational feasibility.
- [x] Add escalation policy: lightweight default, heavyweight governance path for high-criticality or regulated contexts.
- [x] Expand `Available Tools` guidance with concrete usage order, including `flexus_policy_document(op="list", ...)` and artifact write discipline.
- [x] Add named anti-pattern warning blocks with detection, consequence, and mitigation procedures.
- [x] Extend artifact schema to include confidence, evidence links, dependency ownership, assumptions, and decision trace.
- [x] Add AI/regulatory trigger checks (NIST AI RMF profile and timeline mapping where applicable).

---

## Draft Content for SKILL.md

### Draft: Core stance rewrite

You assess MVP feasibility to expose delivery failure points before commitment. Your job is to make hidden risk explicit early enough to support intelligent scope decisions.

Feasibility is not optimism scoring and not a veto theater. You do not ask "can we maybe do this?" You ask "under what constraints can this scope be delivered with acceptable risk, and what must change if constraints fail?"

Default mindset is risk-first realism:
- Assume estimates are optimistic until evidence proves otherwise.
- Treat unknown dependencies as schedule risk, not as neutral placeholders.
- Treat absent evidence as low confidence, never as implicit support.
- Separate local productivity signals (for example faster coding) from system-level delivery feasibility (throughput, stability, and rework).

Mark older but still valid methods explicitly when you use them (for example premortem, TRL, error budget policy), and always attach current evidence where possible.

**Source basis:** Atlassian Team Playbook, Microsoft engineering playbook updates, DORA 2024, SRE workbook.

### Draft: Mandatory feasibility workflow

Before writing any feasibility verdict, you must execute this workflow in order. If any stage is skipped, the assessment is incomplete and cannot be marked `feasible`.

#### Stage 1: Scope grounding (problem and unknowns)

1. Activate MVP scope context:
   - Confirm in-scope features and explicit out-of-scope boundaries.
   - Extract critical assumptions from scope language.
2. Convert assumptions into testable statements:
   - Each assumption must be either evidence-backed now or scheduled for validation.
3. Write an "unknowns list":
   - Unknown technical capability
   - Unknown dependency lead time
   - Unknown compliance impact
   - Unknown reliability exposure

If scope boundaries are ambiguous, pause verdicting and request clarification through recommendations. Do not infer scope silently.

#### Stage 2: Structured risk discovery (premortem)

Run a premortem mindset pass:
- Assume the MVP failed six months after launch.
- List plausible failure causes across technical, resource, timeline, dependency, and governance domains.
- Prioritize the highest-consequence and highest-likelihood risks.

For each top risk, capture:
- Failure mechanism
- Early signal
- Mitigation owner
- Earliest decision checkpoint

Do not accept generic risks such as "integration issues." Rewrite into concrete statements like "third-party API approval lead time exceeds release window by 4 weeks."

#### Stage 3: Dependency mapping with ownership

Build a dependency register with explicit owner and timing:
- Internal team dependency
- External vendor/API dependency
- Legal or compliance review dependency
- Infrastructure capacity dependency
- Customer/beta partner dependency

For each dependency, record:
- Required milestone date
- Lead-time assumption
- Confidence (`high`, `medium`, `low`)
- Fallback path if missed

If no owner is assigned, treat the dependency as unresolved and include it in blockers.

#### Stage 4: Feasibility spikes and option comparison

When critical uncertainty is present, run timeboxed feasibility spikes before final verdict:
- Spike output is evidence, not production code.
- Each spike must answer one decision-relevant uncertainty.

Then run option comparison:
- Compare at least two plausible paths when uncertainty is material.
- Document trade-offs: delivery speed, reliability risk, operating cost, compliance burden, reversibility.
- Record chosen option and rejected option with reasons.

If one option appears clearly dominant and evidence is strong, you may skip formal comparison table, but you must still record rationale in decision trace.

#### Stage 5: Quantitative feasibility scoring

Score feasibility on five axes:
1. Technical feasibility
2. Resource feasibility
3. Timeline feasibility
4. Dependency feasibility
5. Regulatory/operational feasibility (required when relevant)

Use `0..5` score per axis:
- `5`: strong evidence, low uncertainty
- `4`: credible evidence, manageable uncertainty
- `3`: mixed evidence, requires scoped changes
- `2`: weak evidence, unresolved blockers likely
- `1`: unsupported, high risk
- `0`: impossible within MVP constraints

For each score, include:
- Confidence (`high`, `medium`, `low`)
- Evidence references
- One-sentence rationale

#### Stage 6: Hard gate checks

Before final verdict, enforce hard gates:
- No unresolved critical dependency owner
- No single-point timeline estimate (must have range)
- No critical capability with unknown validation path
- No compliance-critical gap without mitigation plan
- No operational reliability plan for high-exposure launch

If any hard gate fails, verdict cannot be `feasible`.

#### Stage 7: Verdict and change path

Use verdict rules:
- `feasible`: all hard gates pass, no axis score below `4`
- `feasible_with_changes`: hard gates pass after explicit scope changes, at least one axis is `3`
- `infeasible`: any hard gate fails or any axis is `0..2` without credible mitigation in MVP window

Always provide:
- Scope-cut options
- Risk transfer options (`buy` / `partner`)
- Reassessment trigger date

**Source basis:** Atlassian premortem/dependency/project-poster plays, Microsoft feasibility spikes + decision log, SAFe planning rigor, NIST AI RMF profile guidance.

### Draft: Interpretation and confidence rules

You must separate evidence quality from business desirability. A desirable outcome with low-quality evidence is still low confidence.

Apply these interpretation rules:

1. **Evidence integrity first**
   - If upstream data integrity is known-bad, mark confidence `low` regardless of apparent upside.
   - Example indicators: sampling mismatch, stale telemetry windows, unresolved metric-definition drift.

2. **Uncertainty is mandatory**
   - Avoid point-only interpretation.
   - Report assumptions and uncertainty bounds (at least optimistic/realistic/pessimistic for schedule and capacity-sensitive estimates).

3. **Decision-rule discipline**
   - Do not conclude from a single favorable metric.
   - Use at least one outcome signal and one guardrail signal for each critical claim.

4. **Dual delivery lens**
   - Never treat speed-only improvements as feasibility proof.
   - Check both throughput and stability trends where data exists.

5. **Operational gate**
   - If reliability risk is material and error budget process is absent, downgrade operational confidence.

6. **Readiness gating**
   - Critical technical components with low maturity evidence should downgrade technical score and may force scope reduction.

**Source basis:** Microsoft ExP SRM guidance, Statsig SRM docs, Spotify risk-aware decision framework, NIST uncertainty reporting, DORA metrics guidance, SRE error budget policy, NASA/GAO readiness framing.

### Draft: Available tools section rewrite

Use internal tools in this order:

1. Activate scope source of truth.
2. Optionally list strategy documents when scope context is incomplete.
3. Write one consolidated feasibility artifact at the end of the run (do not scatter partial artifacts across multiple ad-hoc paths).

```text
flexus_policy_document(op="activate", args={"p": "/strategy/mvp-scope"})
flexus_policy_document(op="list", args={"p": "/strategy/"})
write_artifact(artifact_type="mvp_feasibility_assessment", path="/strategy/mvp-feasibility", data={...})
```

Tool-usage rules:
- Use `activate` on `/strategy/mvp-scope` before scoring any axis.
- Use `list` only when required context is missing or scope references are unclear.
- Call `write_artifact` only after all five feasibility axes and hard gates are complete.
- If evidence is incomplete, write explicit uncertainty and set lower confidence instead of inventing facts.

External evidence handling rules:
- When using vendor or regulator documentation, store source URLs in artifact evidence fields.
- Prefer 2024-2026 sources. If using older source, label it as evergreen and explain why it still applies.
- Never claim tool limits or pricing without source reference.

### Draft: Anti-pattern blocks

#### Anti-pattern: Single-point estimate decision

What it looks like in practice:
- One delivery date, one budget, no confidence range.

Detection signal:
- Timeline field has one value only and no uncertainty narrative.

Consequence if missed:
- Predictable timeline and budget overrun with delayed scope cuts.

Mitigation steps:
1. Require optimistic/realistic/pessimistic values at minimum.
2. Require confidence annotation and assumption list.
3. Downgrade verdict to `feasible_with_changes` or `infeasible` if no ranges can be justified.

#### Anti-pattern: No integrated dependency ownership

What it looks like in practice:
- Dependency list exists, but owner or deadline is blank.

Detection signal:
- Any critical dependency missing owner, lead time, or fallback.

Consequence if missed:
- Hidden blockers appear late and force unplanned de-scope.

Mitigation steps:
1. Require owner + date + fallback for each critical dependency.
2. Reclassify unresolved dependency as blocker.
3. Add reassessment date before final go recommendation.

#### Anti-pattern: Assumption marked as validated without proof

What it looks like in practice:
- Status says "done" but no direct evidence link.

Detection signal:
- Assumption record lacks validation method and evidence reference.

Consequence if missed:
- Irreversible decisions made on false premise.

Mitigation steps:
1. Require validation type (`test`, `documented confirmation`, `measured telemetry`).
2. Require evidence URI or source citation.
3. Downgrade confidence to `low` until evidence exists.

#### Anti-pattern: Legacy impact ignored

What it looks like in practice:
- Risk analysis models only modern path and excludes legacy flow.

Detection signal:
- No legacy-specific risks despite known legacy components in scope.

Consequence if missed:
- Side effects appear after release with limited rollback options.

Mitigation steps:
1. Add explicit legacy hotspot check in technical feasibility.
2. Add extra uncertainty buffer when legacy understanding is low.
3. Require fallback or phased exposure for legacy-touching changes.

#### Anti-pattern: Big-bang rollout by default

What it looks like in practice:
- Full rollout first, rollback strategy second.

Detection signal:
- No ring/canary progression and no rollback threshold.

Consequence if missed:
- Maximum blast radius from a single defect.

Mitigation steps:
1. Define staged exposure progression.
2. Define objective promotion criteria.
3. Define automatic rollback trigger per stage.

#### Anti-pattern: Safeguard exists but is untested

What it looks like in practice:
- Team claims fallback exists but cannot show stress validation.

Detection signal:
- No overload/misconfiguration test evidence for fail-safe path.

Consequence if missed:
- Fallback path fails during incident conditions.

Mitigation steps:
1. Add safeguard stress test as launch prerequisite.
2. Record expected behavior under degraded mode.
3. Include rollback command path in operational plan.

#### Anti-pattern: Security discovered mostly after merge

What it looks like in practice:
- Late vulnerability discovery repeatedly delays release.

Detection signal:
- Majority of critical findings emerge post-merge.

Consequence if missed:
- Security debt becomes timeline debt.

Mitigation steps:
1. Add shift-left checks to feasibility constraints.
2. Define remediation SLA by severity.
3. Add pre-approved exception path for urgent mitigation.

#### Anti-pattern: Supply-chain risk absent from feasibility

What it looks like in practice:
- OSS and vendor dependencies are listed but not risk-ranked.

Detection signal:
- No SBOM, no criticality tiering, no third-party fallback narrative.

Consequence if missed:
- Third-party incidents produce unplanned outage window.

Mitigation steps:
1. Require dependency inventory and criticality levels.
2. Require exploit-priority source in risk assessment.
3. Add vendor incident response assumptions to dependency axis.

#### Anti-pattern: Compliance deferred to "after MVP"

What it looks like in practice:
- Regulatory requirements acknowledged but not scheduled.

Detection signal:
- No compliance milestones in timeline estimate.

Consequence if missed:
- Late launch block or emergency de-scope.

Mitigation steps:
1. Map applicable obligations to timeline checkpoints.
2. Record required evidence artifacts and responsible owner.
3. Block `feasible` verdict if obligations conflict with release window.

#### Anti-pattern: AI productivity interpreted as automatic feasibility

What it looks like in practice:
- Team cites coding acceleration but ignores stability and rework impact.

Detection signal:
- Throughput claim present, stability signal absent.

Consequence if missed:
- Delivery reliability degrades while local speed appears improved.

Mitigation steps:
1. Require throughput and stability evidence together.
2. Require explicit small-batch and test-rigor controls when AI coding tools are used.
3. Downgrade confidence if system-level stability evidence is missing.

### Draft: Decision output rules

Your final recommendations must include both verdict and action path:

- If `feasible`: provide critical assumptions that must remain true and monitoring triggers.
- If `feasible_with_changes`: provide explicit scope cuts and sequencing plan.
- If `infeasible`: provide minimum condition set required for reassessment.

Recommendation quality requirements:
- Every recommendation must be linked to at least one evidence item.
- Every recommendation must include expected risk reduction.
- Every recommendation must include owner type (`engineering`, `product`, `ops`, `legal`, `security`, `vendor`).

Do not provide recommendation lists that are not actionable. Replace vague text like "improve architecture" with concrete text like "replace custom auth module with managed identity provider to remove compliance and incident response burden from MVP scope."

### Draft: Schema additions

```json
{
  "mvp_feasibility_assessment": {
    "type": "object",
    "required": [
      "assessed_at",
      "assessment_version",
      "scope_ref",
      "overall_feasibility",
      "confidence",
      "signal_scores",
      "technical_risks",
      "resource_estimate",
      "timeline_estimate",
      "dependency_register",
      "critical_assumptions",
      "hard_gate_results",
      "blockers",
      "recommendations",
      "decision_trace",
      "sources"
    ],
    "additionalProperties": false,
    "properties": {
      "assessed_at": {
        "type": "string",
        "description": "ISO-8601 timestamp when the assessment was finalized."
      },
      "assessment_version": {
        "type": "string",
        "description": "Version label for the feasibility method used (for reproducibility across iterations)."
      },
      "scope_ref": {
        "type": "string",
        "description": "Path or identifier of the MVP scope source used for this assessment."
      },
      "overall_feasibility": {
        "type": "string",
        "enum": [
          "feasible",
          "feasible_with_changes",
          "infeasible"
        ],
        "description": "Final verdict after axis scoring and hard gate checks."
      },
      "confidence": {
        "type": "object",
        "required": [
          "level",
          "rationale"
        ],
        "additionalProperties": false,
        "properties": {
          "level": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Overall confidence in the verdict given evidence quality and uncertainty."
          },
          "rationale": {
            "type": "string",
            "description": "Plain-language explanation of why this confidence level is assigned."
          }
        }
      },
      "signal_scores": {
        "type": "object",
        "required": [
          "technical",
          "business",
          "operational",
          "dependency",
          "regulatory"
        ],
        "additionalProperties": false,
        "properties": {
          "technical": {
            "$ref": "#/$defs/axisScore"
          },
          "business": {
            "$ref": "#/$defs/axisScore"
          },
          "operational": {
            "$ref": "#/$defs/axisScore"
          },
          "dependency": {
            "$ref": "#/$defs/axisScore"
          },
          "regulatory": {
            "$ref": "#/$defs/axisScore"
          }
        },
        "description": "Normalized 0-5 feasibility evidence scores by axis."
      },
      "technical_risks": {
        "type": "array",
        "description": "Technical risk items discovered during feasibility workflow.",
        "items": {
          "type": "object",
          "required": [
            "risk",
            "resolution_type",
            "severity",
            "owner",
            "status"
          ],
          "additionalProperties": false,
          "properties": {
            "risk": {
              "type": "string",
              "description": "Concrete technical failure mode statement."
            },
            "resolution_type": {
              "type": "string",
              "enum": [
                "build",
                "buy",
                "partner",
                "block"
              ],
              "description": "Primary strategy to resolve this risk."
            },
            "severity": {
              "type": "string",
              "enum": [
                "critical",
                "high",
                "medium",
                "low"
              ],
              "description": "Impact severity if unresolved."
            },
            "owner": {
              "type": "string",
              "description": "Role or team accountable for mitigation."
            },
            "status": {
              "type": "string",
              "enum": [
                "open",
                "mitigated",
                "accepted",
                "blocked"
              ],
              "description": "Current mitigation status."
            },
            "mitigation": {
              "type": "string",
              "description": "Specific mitigation plan for the risk."
            }
          }
        }
      },
      "resource_estimate": {
        "type": "object",
        "required": [
          "engineering_weeks",
          "design_weeks",
          "qa_weeks",
          "estimate_confidence"
        ],
        "additionalProperties": false,
        "properties": {
          "engineering_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Estimated engineering effort in person-weeks."
          },
          "design_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Estimated design effort in person-weeks."
          },
          "qa_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Estimated quality/testing effort in person-weeks."
          },
          "estimate_confidence": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Confidence in resource estimate quality."
          },
          "capacity_notes": {
            "type": "string",
            "description": "Constraints on available team capacity and competing work."
          }
        }
      },
      "timeline_estimate": {
        "type": "object",
        "required": [
          "optimistic_weeks",
          "realistic_weeks",
          "pessimistic_weeks",
          "critical_path"
        ],
        "additionalProperties": false,
        "properties": {
          "optimistic_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Best-case estimate under favorable assumptions."
          },
          "realistic_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Most likely timeline estimate."
          },
          "pessimistic_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Conservative timeline estimate including known uncertainties."
          },
          "p50_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Optional probabilistic median schedule estimate if modeled."
          },
          "p80_weeks": {
            "type": "number",
            "minimum": 0,
            "description": "Optional probabilistic high-confidence schedule estimate if modeled."
          },
          "critical_path": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Ordered list of tasks/dependencies that define minimum delivery duration."
          }
        }
      },
      "dependency_register": {
        "type": "array",
        "description": "Dependencies with ownership and lead-time assumptions.",
        "items": {
          "type": "object",
          "required": [
            "name",
            "type",
            "owner",
            "required_by",
            "lead_time_weeks",
            "confidence",
            "fallback"
          ],
          "additionalProperties": false,
          "properties": {
            "name": {
              "type": "string",
              "description": "Dependency identifier (team, service, vendor, regulator, or partner)."
            },
            "type": {
              "type": "string",
              "enum": [
                "internal",
                "external_api",
                "vendor",
                "legal_compliance",
                "infrastructure",
                "customer"
              ],
              "description": "Dependency category used for risk interpretation."
            },
            "owner": {
              "type": "string",
              "description": "Accountable owner for dependency tracking."
            },
            "required_by": {
              "type": "string",
              "description": "ISO-8601 date by which dependency must be satisfied."
            },
            "lead_time_weeks": {
              "type": "number",
              "minimum": 0,
              "description": "Estimated lead time to satisfy dependency."
            },
            "confidence": {
              "type": "string",
              "enum": [
                "high",
                "medium",
                "low"
              ],
              "description": "Confidence in lead-time estimate quality."
            },
            "fallback": {
              "type": "string",
              "description": "Fallback path if dependency misses required date."
            }
          }
        }
      },
      "critical_assumptions": {
        "type": "array",
        "description": "Assumptions that materially change feasibility outcome.",
        "items": {
          "type": "object",
          "required": [
            "assumption",
            "status",
            "validation_method",
            "evidence_ref"
          ],
          "additionalProperties": false,
          "properties": {
            "assumption": {
              "type": "string",
              "description": "Plain-language assumption statement."
            },
            "status": {
              "type": "string",
              "enum": [
                "validated",
                "partially_validated",
                "unvalidated",
                "invalidated"
              ],
              "description": "Current validation state."
            },
            "validation_method": {
              "type": "string",
              "description": "How assumption was validated (test, metric, contract, legal review, or equivalent)."
            },
            "evidence_ref": {
              "type": "string",
              "description": "URL or internal evidence identifier supporting status."
            }
          }
        }
      },
      "hard_gate_results": {
        "type": "array",
        "description": "Mandatory gate checks evaluated before final verdict.",
        "items": {
          "type": "object",
          "required": [
            "gate",
            "passed",
            "reason"
          ],
          "additionalProperties": false,
          "properties": {
            "gate": {
              "type": "string",
              "description": "Name of hard gate rule."
            },
            "passed": {
              "type": "boolean",
              "description": "Whether the gate passed."
            },
            "reason": {
              "type": "string",
              "description": "Explanation for pass/fail outcome."
            }
          }
        }
      },
      "blockers": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Critical unresolved items blocking feasible verdict."
      },
      "recommendations": {
        "type": "array",
        "items": {
          "$ref": "#/$defs/recommendation"
        },
        "description": "Actionable recommendations tied to evidence and risk reduction."
      },
      "decision_trace": {
        "type": "string",
        "description": "Concise explanation of how evidence and scores led to final verdict."
      },
      "sources": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Source URLs used in this assessment."
      }
    },
    "$defs": {
      "axisScore": {
        "type": "object",
        "required": [
          "score",
          "confidence",
          "rationale",
          "evidence"
        ],
        "additionalProperties": false,
        "properties": {
          "score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 5,
            "description": "Feasibility score for this axis where 0 is impossible and 5 is strongly feasible."
          },
          "confidence": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ],
            "description": "Confidence in the score based on evidence quality."
          },
          "rationale": {
            "type": "string",
            "description": "Reasoning for axis score."
          },
          "evidence": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Source references supporting this score."
          }
        }
      },
      "recommendation": {
        "type": "object",
        "required": [
          "action",
          "owner",
          "expected_risk_reduction",
          "priority",
          "evidence_refs"
        ],
        "additionalProperties": false,
        "properties": {
          "action": {
            "type": "string",
            "description": "Specific action statement."
          },
          "owner": {
            "type": "string",
            "enum": [
              "engineering",
              "product",
              "design",
              "qa",
              "ops",
              "security",
              "legal",
              "vendor"
            ],
            "description": "Primary owner role for implementation."
          },
          "expected_risk_reduction": {
            "type": "string",
            "description": "What risk is reduced if this recommendation is executed."
          },
          "priority": {
            "type": "string",
            "enum": [
              "p0",
              "p1",
              "p2",
              "p3"
            ],
            "description": "Recommendation urgency."
          },
          "evidence_refs": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Evidence links that justify the recommendation."
          }
        }
      }
    }
  }
}
```

### Draft: Quality checklist for skill execution

Before finalizing the artifact, verify:
- You did not skip any mandatory workflow stage.
- Every axis score has confidence and evidence links.
- Every blocker is either mitigated or reflected in verdict downgrade.
- Every recommendation has owner and expected risk reduction.
- Sources are attached for all major claims.
- Older sources are explicitly marked as evergreen.

If any item above is missing, do not output `feasible`.

---

## Gaps and Uncertainties

- Public sources do not provide universal numeric thresholds for many feasibility dimensions (for example "acceptable dependency approval lead time"). Teams still need local baselines.
- Several practical tool constraints are plan- and tenant-specific; published docs are directional but not always complete for every enterprise contract variant.
- Some valuable methods are evergreen rather than new; they remain included because current 2024-2026 operational guidance still depends on them.
- Cross-industry evidence linking specific feasibility checklists to quantified launch success rates remains limited; most available data is postmortem-oriented.
- Regulatory applicability is jurisdiction and product-context dependent; this research identifies timing frameworks but not legal advice.

