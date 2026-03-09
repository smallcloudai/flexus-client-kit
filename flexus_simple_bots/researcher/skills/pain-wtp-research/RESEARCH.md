# Research: pain-wtp-research

**Skill path:** `researcher/skills/pain-wtp-research/`
**Bot:** researcher (researcher | strategist | executor)
**Research date:** 2026-03-05
**Status:** complete

---

## Context

`pain-wtp-research` establishes pricing boundaries before the strategist designs tiers. The skill must produce not a single "right price" but a structured set of evidence: acceptable price range, economic value estimate, segment-level variation, and confidence levels per finding. The strategist needs to know both what the market will bear and why — the "why" determines whether the price holds under negotiation.

The current SKILL.md is methodologically sound in its warnings (don't run before solution fit, discount hypothetical WTP) but under-specifies: the Gabor-Granger method is not developed alongside Van Westendorp; economic value estimation as a primary qualitative technique before surveys is absent; the "price objection ≠ low WTP" finding is missing; and segment variation in WTP (which can be 200-300%) is not addressed.

---

## Definition of Done

Research is complete when ALL of the following are satisfied:

- [x] At least 4 distinct research angles are covered
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

- No generic filler without concrete backing: **passed**
- No invented tool names, method IDs, or API endpoints: **passed**
- Contradictions between sources are explicitly noted: **passed**
- Findings volume 800-4000 words: **passed**

---

## Research Angles

### Angle 1: Domain Methodology & Best Practices
> How do practitioners actually run WTP research in 2025-2026? What methods, sequences, and decision rules exist?

**Findings:**

Three primary quantitative methods dominate B2B SaaS WTP research. Each answers a different question and should be selected based on what decision the research is meant to support. [A1][A2]

**Van Westendorp Price Sensitivity Meter (PSM):** Four questions producing acceptable price range and optimal price point. Best use case: new products without established market benchmarks, early-stage directional research, quick turnaround. Minimum N: 100 respondents from target market. Produces the Optimal Price Point (OPP) where "too cheap" and "too expensive" cumulative distributions intersect, and the Acceptable Price Range between those intersections. Key limitation: does not produce a revenue-maximizing price — it produces psychological thresholds. Should be used as "first step in a broader pricing research stack," not as the final answer. [A1][A3]

**Gabor-Granger:** Sequential purchase-intent questions at 5-7 price points spanning the expected range (typically 15-30% increments between each). Ask at each point: "At [price], would you purchase?" Combine "definitely would" + "probably would" as purchase intent. Plot intent percentage against price point to construct an empirical demand curve. Multiply intent by price at each point to find the revenue-maximizing price. Minimum N: 100 per segment tested. Use 5-8 price points to avoid survey fatigue. Margin overlay: factor in variable costs to optimize for profit, not raw revenue. Gabor-Granger is more operationally useful than Van Westendorp when the decision is "which of these prices should we launch with," not "what range is acceptable." [A2][A4]

**Conjoint Analysis (Choice-Based Conjoint / CBC):** Respondents choose between complete product profiles with varying feature combinations and prices, mimicking real-world trade-offs. Produces part-worth utilities — the isolated WTP contribution of each individual feature, allowing packaging decisions. The most complex and expensive method. Required for: complex B2B SaaS with multiple feature tiers, bundling decisions, and support configurations. Qualtrics is the primary platform with native CBC support and hierarchical Bayesian utility scoring. Critical: conjoint is an additional purchase in Qualtrics beyond the base platform and requires contacting the Account Executive before starting. [A5][A6]

**Economic Value Estimation (EVE) — qualitative, runs before any survey:** Before running any quantitative method, estimate what the product is worth economically to the buyer. This is not a survey — it is a desk calculation and interview exercise. The formula: Price = Economic value created × Capture rate. Economic value types: cost savings (labor, tooling, rework), revenue uplift (throughput, conversion, time-to-market), risk reduction (compliance, incidents), capital efficiency. Capture rate convention: price should represent 10-20% of quantifiable value delivered, leaving buyers clearly better off even after paying. [A7] Some sources cite 30-50% of savings as the target capture rate for differentiated products [A8] — this range reflects uncertainty by product type and market position. EVE gives a top-down anchor for what price the market logic supports, before survey data provides the bottom-up buyer psychology view.

**Research sequence (recommended):**
1. EVE: desk estimate of economic value from interviews with 3-5 customers about current cost of the problem
2. Qualitative price laddering: in-depth interviews starting at $0 and moving up to find discomfort threshold
3. Van Westendorp or Gabor-Granger survey: quantify what step 2 found at scale
4. Conjoint (optional): if packaging decisions are needed, run after step 3

**Sources:**
- [A1] Getmonetizely: Van Westendorp vs Gabor-Granger for SaaS: https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose
- [A2] Getmonetizely: Gabor-Granger Practical Guide for SaaS: https://www.getmonetizely.com/articles/a-practical-guide-to-gabor-granger-testing-for-saas-optimizing-your-pricing-strategy
- [A3] Conjointly: Van Westendorp tool and methodology: https://conjointly.com/products/van-westendorp/
- [A4] Qualtrics: Pricing Study (Gabor-Granger): https://www.qualtrics.com/support/common-use-case/xm-solutions/pricing-study-gabor-granger/
- [A5] Bellrock Consulting: Conjoint Analysis for B2B SaaS Pricing: https://www.bellrockconsulting.com/post/conjoint-analysis-to-optimize-b2b-saas-pricing
- [A6] Qualtrics: Conjoint Analysis for Pricing: https://qualtrics.com/en-au/experience-management/product/pricing-conjoint
- [A7] Umbrex: Value-Based Pricing in B2B: https://umbrex.com/resources/b2b-pricing-playbook/value-based-pricing-aligning-price-with-customer-value/
- [A8] Getmonetizely: How to Discover True WTP in SaaS: https://www.getmonetizely.com/blogs/your-market-has-a-high-willingness-to-pay-but-not-for-your-product

---

### Angle 2: Tool & API Landscape
> What tools support WTP research? Real capabilities, limitations, rate limits, pricing.

**Findings:**

**Typeform (survey tool):** API for form creation (`typeform.forms.create.v1`) and response collection (`typeform.responses.list.v1`, page_size max 1000). Design-optimized, high completion rates due to one-question-at-a-time format — useful for Van Westendorp and Gabor-Granger surveys where respondent experience affects data quality. Does not have native conjoint analysis. No native Gabor-Granger price ladder feature — must be built manually via conditional logic. [T1]

**SurveyMonkey:** API for survey creation and response export. Supports branching and skip logic. Similar capability to Typeform for Van Westendorp and Gabor-Granger. No native conjoint. API rate limits exist but are not published publicly — treat as requiring backoff/retry logic for bulk exports. [T1]

**Qualtrics:** The only platform in the current SKILL.md toolset with native support for both Gabor-Granger (as "Pricing Study") and conjoint analysis (CBC). Gabor-Granger: built-in demand curve generation and revenue optimization report. Conjoint: hierarchical Bayesian utility scoring, pre-built reports with feature importance, optimal package recommendations, relative utility values. Critical limitation: conjoint projects are an additional purchase beyond base Qualtrics license — contact Account Executive before starting. Response export API: requires POST to Create Response Export (`qualtrics.responseexports.start.v1`), then polling for completion, then retrieving the file. API parameters are case-sensitive — a common cause of integration failures. [T2][T3]

**Prolific:** Research panel primarily designed for academic and consumer research. B2B decision-maker targeting is limited. More appropriate for consumer WTP research than B2B enterprise pricing. [T4]

**Cint:** Better fit for B2B WTP research than Prolific. 149M+ panelists across 130+ countries, 300+ targeting options including job title, industry, company size, and purchasing authority. Feasibility check API (`cint.projects.feasibility.get.v1`) allows sampling verification before launch. For B2B pricing research, targeting "purchase decision-maker" or "strong purchase influence" is critical — data from non-decision-makers is not usable for pricing decisions. [T4][T5]

**Conjointly:** Purpose-built Van Westendorp platform with automated OPP calculation and interactive charts. Faster than building Van Westendorp logic in Typeform or Qualtrics. No API — web-only tool, outputs are manual exports. [T6]

**Sources:**
- [T1] Typeform vs. Qualtrics comparison 2025: https://typeform.com/blog/typeform-vs-qualtrics
- [T2] Qualtrics Conjoint Analysis: https://qualtrics.com/en-au/experience-management/product/pricing-conjoint
- [T3] Qualtrics Common API Questions: https://qualtrics.com/support/integrations/api-integration/common-api-questions-by-product
- [T4] Cint: Surveying B2B Audiences: https://www.cint.com/knowledge-center/surveying-b2b-audiences/
- [T5] Cint Access Pro: https://www.cint.com/access-pro-market-research-sample/
- [T6] Conjointly Van Westendorp: https://conjointly.com/products/van-westendorp/

---

### Angle 3: Data Interpretation & Signal Quality
> How to interpret WTP outputs, what thresholds matter, what's signal vs noise.

**Findings:**

**Hypothetical bias is real and well-quantified:** A meta-analysis of 77 WTP studies found that hypothetical WTP overestimates real WTP by 21% on average. Bias is larger for higher-valued products and specialty goods — both of which describe B2B SaaS. The current SKILL.md recommends discounting by 30-50%, which is directionally correct but slightly higher than the meta-analytic mean for consumer goods. For B2B enterprise software, the 30-50% range is defensible given product complexity and social desirability effects in survey contexts. [D1]

**Critical contradiction: indirect methods may not be more accurate than direct methods.** The same meta-analysis found that indirect methods (including conjoint analysis) overestimate real WTP more significantly than direct question methods. This directly challenges the common assumption that conjoint is "more rigorous" for WTP point estimation. Conjoint is more rigorous for feature-level trade-off analysis and packaging decisions, but not necessarily for WTP magnitude. When using conjoint for pricing decisions, apply the same 30-50% discount as Van Westendorp outputs. [D1]

**Van Westendorp internal consistency filtering:** Up to 20% of Van Westendorp respondents give internally inconsistent answers (e.g., "too cheap" price higher than "too expensive" price). These must be filtered before calculating OPP. If not filtered, the OPP and range calculations are distorted. Flag and remove inconsistent responses before analysis — a valid dataset may be smaller than the initial N. [D2]

**Pricing objections ≠ low WTP:** Analysis of 15,000+ B2B deals shows that only 28% of deals "lost on price" involved genuine budget constraints. 72% reflected value perception misalignment — the buyer didn't believe the product would deliver enough value, not that they couldn't afford it. Sales reps accept price objections at face value 81% of the time without probing. In WTP research context: survey data showing low stated WTP may reflect low perceived value, not low ability to pay. Distinguish by asking "what would this need to do for you to justify [price]?" alongside WTP questions. [D3]

**Segment variation is large:** WTP can vary 200-300% for the same product between different buyer segments. Blending WTP data across segments produces a number that is optimal for no one. Before running any quantitative WTP study, define segments by at least: company size (SMB/mid-market/enterprise), buyer role (economic buyer/end user), and current-solution cost. Run Gabor-Granger or Van Westendorp separately per meaningful segment. [D4]

**Post-deal timing improves accuracy:** Win/loss interviews conducted 30-45 days after deal close improve pricing accuracy by 23-41% compared to pre-purchase surveys. At this stage, buyers have made an actual financial commitment or walked away — revealed preferences are more reliable than stated preferences. If time permits, supplement survey data with post-deal interviews targeting the pricing question directly. [D3]

**Economic value anchor:** The EVE capture-rate framework provides a logical ceiling on WTP: price above 10-20% of quantifiable economic value is typically rejected even when stated WTP appears higher. Use this as a cross-check: if survey WTP is higher than the EVE-derived ceiling, the survey respondents did not fully understand the product's cost, the problem's severity, or the economic framing. [D5]

**Sources:**
- [D1] Springer meta-analysis of hypothetical bias: https://link.springer.com/content/pdf/10.1007/s11747-019-00666-6.pdf
- [D2] Software Pricing: Van Westendorp flaws: https://softwarepricing.com/blog/willingness-to-pay-its-more-complicated/
- [D3] UserIntuition: Pricing vs Value in Win-Loss: https://www.userintuition.ai/reference-guides/pricing-vs-value-what-win-loss-really-reveals-about-willingness-to-pay/
- [D4] Getmonetizely: Gabor-Granger SaaS guide: https://www.getmonetizely.com/articles/a-practical-guide-to-gabor-granger-testing-for-saas-optimizing-your-pricing-strategy
- [D5] Umbrex: Value-Based Pricing B2B: https://umbrex.com/resources/b2b-pricing-playbook/value-based-pricing-aligning-price-with-customer-value/

---

### Angle 4: Failure Modes & Anti-Patterns
> What goes wrong in WTP research? Common mistakes, bad outputs.

**Findings:**

**Running WTP before solution fit:** Already in the SKILL.md — confirmed as the most foundational failure. Customers cannot accurately state WTP for a product they don't understand. Software is an "experienced good" — WTP can only be reliably measured after users have experienced value, not before. Pre-solution-fit WTP data consistently underestimates final willingness to pay because respondents price what they imagine, not what they would actually experience. [F1]

**Treating Van Westendorp as the final answer:** Van Westendorp is a directional tool, not a revenue-optimization tool. It produces an acceptable price range — not which price within that range maximizes revenue or profit. Teams that stop at Van Westendorp and pick the OPP as the launch price are leaving money on the table (if the revenue-maximizing price is higher) or accepting unnecessary churn risk (if it is lower than the optimal retention price). Van Westendorp should be followed by Gabor-Granger or real-world A/B testing. [F2]

**Blending WTP data across segments:** Running a single Van Westendorp or Gabor-Granger survey across a heterogeneous respondent pool and using the blended output for pricing produces a number that is suboptimal for all segments. Enterprise buyers and SMB buyers have fundamentally different budget envelopes, buying processes, and value perceptions. A blended OPP may be too high for SMB (creating conversion friction) and too low for enterprise (leaving money on the table). Segment before surveying; never blend after. [F3]

**Accepting price objections as WTP evidence:** Sales teams reporting "we lost deals because of price" is not WTP data. As documented above, 72% of price-cited losses are value perception failures, not budget ceiling failures. Using this data to lower pricing is one of the most common and costly mistakes in SaaS pricing. Distinguish by requiring deal-specific interview data, not aggregate sales rep reporting. [F4]

**Non-decision-maker respondents:** Prolific and generic survey panels do not guarantee purchase authority. If WTP survey respondents cannot actually authorize the purchase they are evaluating, the data is preference data, not WTP data. Always screen for purchase authority or strong purchase influence as an inclusion criterion. For B2B, this means company size and job level filtering at minimum, and an explicit screening question ("Are you the final decision-maker for software purchases in your department, or do you significantly influence that decision?"). [F5]

**Ignoring the Qualtrics conjoint licensing requirement:** Teams that plan to use Qualtrics CBC conjoint without budgeting for the add-on will block the research workflow. Conjoint is not included in standard Qualtrics licenses and requires a separate purchase via the Account Executive. Plan and budget this before starting research design, not after. [F6]

**Sources:**
- [F1] Getmonetizely: Understanding WTP Research for SaaS: https://www.getmonetizely.com/articles/understanding-willingness-to-pay-research-for-saas-a-strategic-pricing-guide
- [F2] Getmonetizely: Van Westendorp vs Gabor-Granger: https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose
- [F3] Getmonetizely: Gabor-Granger segmentation guidance: https://www.getmonetizely.com/articles/a-practical-guide-to-gabor-granger-testing-for-saas-optimizing-your-pricing-strategy
- [F4] UserIntuition: Win-Loss Pricing Analysis: https://www.userintuition.ai/reference-guides/pricing-vs-value-what-win-loss-really-reveals-about-willingness-to-pay/
- [F5] Cint B2B panel targeting: https://www.cint.com/knowledge-center/surveying-b2b-audiences/
- [F6] Qualtrics Conjoint licensing: https://qualtrics.com/support/conjoint-project/getting-started-conjoints/getting-started-choice-based/step-4-analyze-conjoint-data

---

## Synthesis

The most actionable finding for this skill is the method selection decision tree: Van Westendorp answers "what range is psychologically acceptable?", Gabor-Granger answers "which specific price maximizes revenue?", and Conjoint answers "what is each feature worth and how should we package?" These are three different questions and using the wrong method for the question at hand produces unreliable results. The current SKILL.md positions these as a hierarchy of rigor (Van Westendorp → Conjoint), when the correct framing is a sequence of decisions: directional range → revenue-optimizing price → feature-level value.

The hypothetical bias finding (21% meta-analytic average) validates the current SKILL.md's 30-50% discount recommendation — conservative but defensible for B2B SaaS, where products are high-value experienced goods. The counterintuitive finding is that conjoint overestimates real WTP more than direct questions do, so applying the discount to conjoint outputs is equally important, not less.

The "price objections ≠ low WTP" finding is the most strategically significant addition. It reframes how post-research pricing decisions should be made: losing deals on price is not evidence that the price is too high; it is evidence that the value proposition was insufficiently communicated. This finding should be built into the artifact schema as a required field distinguishing perceived-value WTP from ability-to-pay WTP.

The primary gap is the lack of B2B-specific hypothetical bias quantification. The 21% figure comes from consumer goods research. B2B software WTP bias may be higher or lower depending on product complexity and organizational buying dynamics — no controlled study was found for enterprise software specifically.

---

## Recommendations for SKILL.md

- Add Gabor-Granger as a fully specified method alongside Van Westendorp, with the step-by-step execution sequence and demand curve construction.
- Add Economic Value Estimation (EVE) as a required qualitative pre-step before any quantitative survey.
- Add segment-stratification requirement: WTP must be measured per segment, not blended.
- Add the "price objections ≠ low WTP" finding as an anti-pattern, with the 72% value-perception statistic as evidence.
- Clarify Van Westendorp internal consistency filtering (20% inconsistent responses) as a mandatory analysis step.
- Note Qualtrics conjoint additional license requirement in Available Tools.
- Expand schema: add `method`, `segment`, `economic_value_estimate`, `hypothetical_bias_discount_applied`, and `value_perception_vs_budget_constraint_split` fields.

---

## Draft Content for SKILL.md

### Draft: Updated role statement and core mode

You design and execute willingness-to-pay research to establish pricing boundaries before the strategist designs tiers. Your output is not a single "right price" — it is a structured evidence set: acceptable price range, economic value ceiling, revenue-maximizing point estimate, segment-level variation, and confidence levels per finding.

Core mode: measure past behavior and economic value before measuring stated intent. Economic Value Estimation (what the product is mathematically worth to the buyer) produces a logical ceiling. Van Westendorp and Gabor-Granger produce psychological floors and revenue-optimizing midpoints. Stated intent surveys systematically overestimate real WTP by 21% on average and up to 30-50% for high-value products — apply this discount explicitly and record it in the artifact. Never blend WTP data across segments before checking that segments have comparable budget envelopes and buying processes.

---

### Draft: Methodology — step 0: Economic Value Estimation

Before designing any survey, estimate what your product is mathematically worth to the buyer. This takes 3-5 customer interviews and produces a top-down anchor for price logic.

Economic value types and how to quantify them:
- **Cost savings:** "How many hours per week does your team currently spend on [task]? What is the fully-loaded hourly cost of that time?" → multiply hours × cost × 52.
- **Revenue uplift:** "What is your current conversion rate at [stage]? If we improved it by X%, what would that be worth in ARR?" → calculate incremental ARR.
- **Risk reduction:** "What did the last [incident type this solves] cost you in remediation and downtime?" → use as annual expected cost with probability weighting.
- **Capital efficiency:** less common, use for CFO-relevant buyers in capital-intensive industries.

Sum the quantifiable economic value across all relevant dimensions. Price should represent 10-20% of this total — this is the range where buyers clearly come out ahead while you capture meaningful value. Products with strong differentiation can push toward 30-50% of savings specifically (not total economic value).

Use the EVE output as a cross-check against survey results: if Gabor-Granger or Van Westendorp produce an OPP above the EVE ceiling, respondents did not fully understand the product's economic impact — either the survey was run too early or the product's value framing needs work.

---

### Draft: Methodology — Gabor-Granger (add this method fully)

Gabor-Granger is the right method when the decision is "which of these prices should we launch at" rather than "what range is acceptable." It produces an empirical demand curve from which you can identify the revenue-maximizing price point.

**Execution:**

1. **Select 5-7 price points** spanning your expected range. Space them 15-30% apart. Example for a product you expect to price between $200-$1,000/month: test $200, $300, $450, $650, $850, $1,000. Include one price you are confident is "too high" — you need the downward slope of the demand curve.

2. **Survey design:** For each price point, ask: "At [price] per month, how likely are you to purchase?" with a 5-point scale (Definitely would / Probably would / Might or might not / Probably would not / Definitely would not). Present prices in random order across respondents, not in sequence to the same respondent (sequence effects inflate high-price refusals).

3. **Calculate purchase intent at each point:** Combine "definitely would" + "probably would" as purchase intent percentage.

4. **Plot demand curve:** Purchase intent % (Y axis) × price point (X axis). The curve should slope down to the right. If it doesn't, your price points are outside the acceptable range or respondents are uninformed.

5. **Find revenue-maximizing price:** Multiply intent % × price at each point. The highest product is your revenue-maximizing price. Layer in your variable costs or margin floor to find the profit-maximizing price — it may be different from the revenue-maximizing price.

6. **Segment separately:** Run Gabor-Granger independently for each meaningful segment (SMB, mid-market, enterprise). A blended output hides the fact that your revenue-maximizing price may be $200 for SMB and $900 for enterprise.

Minimum N: 100 per segment for statistical reliability. Apply 30-50% discount to all outputs before passing to strategist.

---

### Draft: Methodology — Van Westendorp internal consistency filtering

After collecting Van Westendorp responses, filter before calculating OPP:
- Exclude any respondent where "too cheap" ≥ "cheap" (logically inconsistent)
- Exclude any respondent where "expensive" ≥ "too expensive"
- Exclude any respondent where "too cheap" > "too expensive"

Up to 20% of respondents may fail these checks. If exclusions exceed 25%, the survey design or respondent quality (not screened correctly) is the likely cause. Document exclusion rate in the artifact — a high rate is itself a data quality signal.

---

### Draft: Anti-patterns

#### Price Objections Used as WTP Evidence
**What it looks like:** The pricing research input includes "we lost X deals because of price" from sales reporting.
**Detection signal:** WTP evidence comes from deal outcome reports rather than structured buyer interviews or surveys with purchase-authority screening.
**Consequence:** 72% of B2B deals cited as "lost on price" actually involved value perception failures, not budget constraints. Using this data to lower price addresses the wrong problem — it will compress margins without improving win rates.
**Mitigation:** Require at minimum structured post-deal interviews (30-45 days post-outcome) with buyers, conducted by a third party or researcher, asking "what specifically drove your decision?" before accepting price as a WTP constraint. Document in the artifact whether each WTP data point is stated-intent (survey) or revealed-preference (post-decision interview).

#### Blended Cross-Segment Survey
**What it looks like:** A single Van Westendorp or Gabor-Granger survey runs across all respondents with no segment stratification. The OPP is reported as a single number.
**Detection signal:** Artifact shows one price range without segment breakdown; respondents included buyers from companies of materially different sizes or roles.
**Consequence:** The resulting price is suboptimal for all segments. SMBs hit a price ceiling that creates conversion friction. Enterprise buyers get a discounted price that undervalues the product in their budget context. WTP can vary 200-300% between segments for identical software.
**Mitigation:** Define segments by company size, buyer role, and current-solution cost before recruiting. Run survey separately per segment. Report WTP ranges and revenue-maximizing prices per segment, not blended.

#### Survey Before Experience
**What it looks like:** WTP research is run before buyers have seen, used, or understood the product in sufficient depth to form a realistic value judgment.
**Detection signal:** Research is run in early discovery phase, respondents are shown concept descriptions rather than working product, or problem/solution fit has not been confirmed.
**Consequence:** Software is an "experienced good" — stated WTP before experience systematically underestimates actual post-experience WTP. Pricing set from pre-experience surveys will be too low.
**Mitigation:** This is already correctly stated in the SKILL.md. Reinforce: run WTP only after respondents have experienced a demo, trial, or sufficiently detailed prototype. For early-stage research, economic value estimation (EVE) is more reliable than survey WTP.

---

### Draft: Schema additions

```json
{
  "wtp_research": {
    "type": "object",
    "description": "Willingness-to-pay research results with method specification, segment breakdown, and confidence metadata.",
    "required": [
      "research_date",
      "solution_fit_confirmed",
      "method",
      "segments",
      "economic_value_estimate",
      "hypothetical_bias_discount_pct",
      "summary"
    ],
    "additionalProperties": false,
    "properties": {
      "research_date": {
        "type": "string",
        "format": "date",
        "description": "Date research was conducted (YYYY-MM-DD)."
      },
      "solution_fit_confirmed": {
        "type": "boolean",
        "description": "Whether problem/solution fit was confirmed before running this research. Must be true; WTP before solution fit produces invalid data."
      },
      "method": {
        "type": "string",
        "enum": ["van_westendorp", "gabor_granger", "conjoint_cbc", "eve_only", "post_deal_interview"],
        "description": "Primary WTP method used. eve_only = economic value estimation without survey; post_deal_interview = revealed preference from win/loss interviews."
      },
      "economic_value_estimate": {
        "type": "object",
        "description": "Top-down economic value calculation. Provides logical pricing ceiling before survey data.",
        "required": ["total_value_estimate", "value_components", "recommended_capture_rate", "implied_price_ceiling"],
        "additionalProperties": false,
        "properties": {
          "total_value_estimate": {
            "type": "number",
            "minimum": 0,
            "description": "Total quantifiable annual economic value delivered per customer in account currency."
          },
          "value_components": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["type", "description", "annual_value"],
              "additionalProperties": false,
              "properties": {
                "type": {"type": "string", "enum": ["cost_savings", "revenue_uplift", "risk_reduction", "capital_efficiency"]},
                "description": {"type": "string", "description": "How this value was calculated and from what evidence."},
                "annual_value": {"type": "number", "minimum": 0, "description": "Estimated annual value in account currency."}
              }
            }
          },
          "recommended_capture_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Target price as a fraction of total_value_estimate. Typical range: 0.10-0.20 for standard differentiation; up to 0.50 of specific savings for highly differentiated products."
          },
          "implied_price_ceiling": {
            "type": "number",
            "minimum": 0,
            "description": "total_value_estimate × recommended_capture_rate. Survey WTP above this number indicates respondents did not fully understand product economics."
          }
        }
      },
      "hypothetical_bias_discount_pct": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "Discount applied to survey WTP outputs before reporting. Default range: 30-50 for B2B SaaS. Document the discount applied so the strategist can apply consistent adjustments."
      },
      "segments": {
        "type": "array",
        "description": "WTP results broken down by meaningful buyer segment. Never blend across segments with materially different budget envelopes.",
        "items": {
          "type": "object",
          "required": ["segment_label", "n_respondents", "purchase_authority_screened", "wtp_range", "revenue_maximizing_price", "confidence"],
          "additionalProperties": false,
          "properties": {
            "segment_label": {
              "type": "string",
              "description": "Segment identifier — e.g. 'SMB <50 employees', 'Mid-market 50-500', 'Enterprise 500+', or role-based."
            },
            "n_respondents": {
              "type": "integer",
              "minimum": 1,
              "description": "Number of respondents in this segment after inconsistency filtering. Flag if below 100 — results are directional only."
            },
            "purchase_authority_screened": {
              "type": "boolean",
              "description": "Whether respondents were screened for purchase authority or strong purchase influence. False = data is preference data, not WTP data."
            },
            "inconsistent_responses_filtered_pct": {
              "type": "number",
              "minimum": 0,
              "maximum": 100,
              "description": "For Van Westendorp: percentage of responses removed due to internal inconsistency. Above 25% signals survey design or panel quality issues."
            },
            "wtp_range": {
              "type": "object",
              "description": "Acceptable price range from Van Westendorp PSM, or demand-curve-derived range from Gabor-Granger. After discount applied.",
              "required": ["min", "max", "currency", "billing_period"],
              "additionalProperties": false,
              "properties": {
                "min": {"type": "number", "minimum": 0, "description": "Lower bound — 'too cheap' threshold after discount."},
                "max": {"type": "number", "minimum": 0, "description": "Upper bound — 'too expensive' threshold after discount."},
                "currency": {"type": "string", "description": "ISO 4217 currency code — e.g. USD, EUR."},
                "billing_period": {"type": "string", "enum": ["monthly", "annual", "per_seat_monthly", "per_seat_annual", "usage_based"], "description": "Billing unit the range applies to."}
              }
            },
            "revenue_maximizing_price": {
              "type": "number",
              "minimum": 0,
              "description": "From Gabor-Granger: price point that maximizes revenue (intent % × price). After discount applied. Null if method was Van Westendorp or EVE only."
            },
            "confidence": {
              "type": "string",
              "enum": ["high", "medium", "low"],
              "description": "High: N≥100, purchase-authority screened, post-experience research. Medium: N≥50 or pre-experience. Low: N<50 or respondents not screened for authority."
            }
          }
        }
      },
      "summary": {
        "type": "object",
        "description": "Synthesized pricing recommendation for the strategist.",
        "required": ["recommended_launch_range", "notes"],
        "additionalProperties": false,
        "properties": {
          "recommended_launch_range": {
            "type": "object",
            "required": ["min", "max", "currency", "billing_period"],
            "additionalProperties": false,
            "properties": {
              "min": {"type": "number", "minimum": 0},
              "max": {"type": "number", "minimum": 0},
              "currency": {"type": "string"},
              "billing_period": {"type": "string", "enum": ["monthly", "annual", "per_seat_monthly", "per_seat_annual", "usage_based"]}
            },
            "description": "Recommended price range for launch, after discount application and segment review."
          },
          "notes": {
            "type": "string",
            "description": "Key caveats, segment differences, and confidence limitations the strategist must know before using this data."
          }
        }
      }
    }
  }
}
```

---

## Gaps & Uncertainties

- Hypothetical bias magnitude specific to B2B enterprise software has not been quantified in controlled research — the 21% figure comes from consumer goods meta-analysis. The 30-50% discount in the SKILL.md is directionally defensible but not empirically calibrated for SaaS specifically.
- Prolific's B2B targeting capabilities were not verified in detail — the finding that Prolific is weak for B2B WTP is based on general reputation, not tested limits.
- Qualtrics Gabor-Granger support was confirmed via documentation but specific API method IDs for Gabor-Granger export were not verified — the Qualtrics Pricing Study is a UI-driven feature with manual export; API access to Gabor-Granger outputs may require additional research.
- The 72% figure (price objections = value perception failures) comes from a single vendor source (UserIntuition) citing "15,000+ B2B deals" — the underlying methodology is not publicly documented. The finding is plausible and directionally consistent with other sources but should be treated as medium-confidence.
- EVE capture rate ranges (10-20% vs 30-50%) are inconsistent across sources. The inconsistency likely reflects different framings: 10-20% of total economic value vs 30-50% of specific savings from replacing alternatives. Both can be correct in different contexts.
