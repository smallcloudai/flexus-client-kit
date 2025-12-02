Общая картина агентов

Предлагаю такой состав:

Orchestrator — главный мозг, гоняет пайплайн.

A. Diagnostic Agent — разбирает вход, нормализует гипотезу.

B. Segment & JTBD Strategist — ICP, сегменты, JTBD, CJM.

C. Value & Messaging Strategist — ценность, позиционирование, месседжи, углы.

D. Channel & Experiment Designer — каналка, дизайн экспериментов.

E. Tactics & Spec Generator — кампании, креативы, лендинг, трекинг (машиночитаемо).

F. Risk & Compliance Checker — риски, Ads policies, privacy.

G. Metrics & Decision Framework — KPI, MDE, stop/accelerate rules, план анализа.

Можно потом дробить/укрупнять, но это хороший базовый набор.

📦 Общий рабочий формат (shared state)

Все агенты работают с одним объектом work_state, который крутит Оркестратор:

{
  "request": { /* SovaStrategyRequest */ },
  "response": { /* SovaStrategyResponse (частично заполнен) */ },
  "decision_log": [],
  "internal": {
    "diagnosis": {},
    "segment_model": {},
    "value_model": {},
    "channel_model": {},
    "experiment_model": {},
    "tactical_model": {},
    "risk_model": {},
    "metrics_model": {}
  }
}


Каждый агент:

читает: request + internal + часть response

пишет: свою часть internal, свою часть response, добавляет записи в decision_log.

1. Orchestrator

Роль: последовательное/условное выполнение агентов и сбор итогового ответа.

Вход
{
  "request": SovaStrategyRequest
}

Выход
{
  "response": SovaStrategyResponse
}

Логика

Пайплайн по шагам:

вызвать A.Diagnostic → internal.diagnosis, response.hypothesis_analysis, + decision_log

вызвать G.Metrics → internal.metrics_model, response.strategy_summary (частично), response.experiment_design (частично)

вызвать B.Segment → internal.segment_model, response.target_segment

вызвать C.ValueMessaging → internal.value_model, response.value_messaging

вызвать D.ChannelExperiment → internal.channel_model, донаполнить response.channel_strategy и response.experiment_design

вызвать E.Tactics → internal.tactical_model, response.tactical_plan, response.creative_requirements, response.landing_requirements, response.tracking_requirements, response.machine_spec

вызвать F.RiskCompliance → internal.risk_model, response.risk_assessment, response.compliance_assessment

финализировать strategy_summary, собрать decision_log, выставить version, timestamps.

2. Agent A — Diagnostic Agent

Роль: понять, что за кейс, нормализовать гипотезу, определить, что реально тестируется.

Вход (из work_state)

request.idea

request.hypothesis

request.icp

request.jtbd

request.customer_journey

request.budget

request.constraints

request.business_objectives

RAG:

JTBD по сегменту

общие паттерны по типам гипотез

Выход
В internal.diagnosis:
"diagnosis": {
  "normalized_hypothesis": "string",
  "primary_type": "value|segment|messaging|channel|pricing|conversion|retention",
  "secondary_types": ["..."],
  "testable_with_traffic": true,
  "recommended_test_mechanisms": ["paid_traffic", "content"],
  "uncertainty_level": "low|medium|high|extreme",
  "key_unknowns": ["..."],
  "limitations": ["..."],
  "needs_additional_methods": ["none|custdev|desk_research|product_experiment"],
  "feasibility_score": 0.0
}

В response.hypothesis_analysis:

Практически то же, но в финальном формате.

В decision_log:
{
  "step": "diagnosis",
  "decision": {
    "primary_type": "value",
    "testable_with_traffic": true
  },
  "rationale": "...",
  "input_refs": ["idea", "hypothesis"],
  "sources": []
}

3. Agent B — Segment & JTBD Strategist

Роль: уточнить и, при необходимости, переопределить целевой сегмент и jobs-to-be-done, чтобы стратегия не тестировала «в вакууме».

Вход

request.icp

request.jtbd

request.customer_journey

internal.diagnosis

request.geo_language

founder_profile

RAG:

06-customer-segments-jtbd

07-customer-journey

Выход
В internal.segment_model:
"segment_model": {
  "segment_id": "seg_01",
  "label": "EN side-hustle founders in US/UK",
  "icp": { /* нормализованный icp */ },
  "jtbds": { /* нормализованный jtbd */ },
  "journey": { /* ключевые моменты */ },
  "discovery_channels": ["youtube", "tiktok", "twitter"],
  "segment_risks": ["hard_to_target", "low_intent_early_stage"]
}

В response.target_segment:

Сжатая версия + human-friendly.

В decision_log:
{
  "step": "segment_selection",
  "decision": {
    "segment_id": "seg_01",
    "label": "EN side-hustle founders in US/UK"
  },
  "alternatives_considered": ["indie hackers globally", "SMB owners 35+"],
  "rationale": "matches hypothesis; accessible via Meta/TikTok; aligns with JTBD",
  "sources": ["jtbd_db.segment_x", "cjm_db.flow_y"]
}

4. Agent C — Value & Messaging Strategist

Роль: собрать ценностное предложение, основные и альтернативные углы, базу для креативов и лендинга.

Вход

internal.segment_model

internal.diagnosis

request.offer

request.idea

market_context, competitors (если есть)

RAG:

04-competitive-landscape

01-market-definition

03-pestel-trends

10-pricing-willingness-to-pay (для тональности оффера)

Выход
В internal.value_model:
"value_model": {
  "core_value_prop": "string",
  "supporting_value_props": ["..."],
  "key_messages": ["..."],
  "angles": [
    {"name": "time_saving", "description": "..."},
    {"name": "clarity", "description": "..."}
  ],
  "objections": [
    {"objection": "...", "rebuttal": "..."}
  ],
  "positioning_statement": "For X who Y, our product Z is..."
}

В response.value_messaging:

Практически то же, чуть более человекочитаемо.

В decision_log:
{
  "step": "value_messaging",
  "decision": {
    "core_value_prop": "Turn your side-hustle chaos into a clear weekly plan",
    "angles": ["time_saving", "clarity"]
  },
  "rationale": "Derived from JTBD: need clarity and time; competitors focus on tooling, not plan",
  "sources": ["competitive.prelaunch", "pestel.side_hustle_trend"]
}

5. Agent D — Channel & Experiment Designer

Роль: выбрать каналы, формат теста, дизайн эксперимента (test cells, бюджет, MDE, stop-rules) совместно с G.

Вход

internal.segment_model

internal.value_model

internal.diagnosis

request.channels_context

request.budget

request.constraints

internal.metrics_model (из G)

request.market_context (если есть)

RAG:

08-channel-benchmarks

11-scenarios-sensitivity

PESTEL (для трендов каналов)

Выход
В internal.channel_model:
"channel_model": {
  "selected_channels": [
    {
      "channel": "meta",
      "role": "primary_demand_test",
      "budget_share": 0.6
    },
    {
      "channel": "tiktok",
      "role": "angle_exploration",
      "budget_share": 0.4
    }
  ],
  "excluded_channels": [
    {"channel": "linkedin", "reason": "cac_too_high_for_b2c"}
  ],
  "test_cells": [ /* как в experiment_design */ ]
}

В response.channel_strategy и частично response.experiment_design:

список каналов + обоснование;

структура test cells и распределение бюджета.

В decision_log:
{
  "step": "channel_experiment_design",
  "decision": {
    "channels": ["meta", "tiktok"],
    "test_cells_count": 3
  },
  "rationale": "Benchmarks show lower CPC on Meta; TikTok for cheap reach and creative angle testing",
  "sources": ["benchmarks.meta", "benchmarks.tiktok", "scenarios.base_case"]
}

6. Agent G — Metrics & Decision Framework

Роль: KPI, MDE, минимальные выборки, stop/accelerate rules, план анализа.

Вход

request.metrics

request.budget

internal.diagnosis

internal.channel_model (может вызываться до/после D, лучше в два прохода)

request.business_objectives

risk_profile

RAG:

11-scenarios-sensitivity

общие статистические рекомендации (из PRD/исследований GTM)

Выход
В internal.metrics_model:
"metrics_model": {
  "primary_kpi": "waitlist_signups",
  "secondary_kpis": ["ctr", "cpc"],
  "expected_ranges_by_channel": { /* как в strategy_summary */ },
  "mde": {
    "relative_change": 0.3,
    "confidence": 0.8
  },
  "min_samples": {
    "impressions_per_cell": 3000,
    "clicks_per_cell": 100,
    "conversions_per_cell": 10
  },
  "stop_rules": [ ... ],
  "accelerate_rules": [ ... ],
  "analysis_plan": "..."
}

В response.strategy_summary (частично) и response.experiment_design:

цель, таймфрейм;

expected ranges;

min samples, stop/accel rules.

В decision_log:
{
  "step": "metrics_framework",
  "decision": {
    "primary_kpi": "waitlist_signups",
    "mde": 0.3
  },
  "rationale": "Budget and traffic constraints; 30% difference is realistic to detect in 2 weeks",
  "sources": ["scenarios.best_base_worst"]
}

7. Agent E — Tactics & Spec Generator

Роль: превратить всё выше в детальное ТЗ: кампании, аудитории, креативы, лендинг, трекинг, machine_spec.

Вход

internal.channel_model

internal.value_model

internal.segment_model

internal.metrics_model

request.existing_assets

request.geo_language

request.constraints

RAG:

channel-specific best practices

creative/landing patterns (если ты их зашьёшь/подтянешь)

Выход
В internal.tactical_model:
"tactical_model": {
  "campaigns": [ ... ],
  "creative_blueprints": [ ... ],
  "landing_blueprint": { ... },
  "tracking_blueprint": { ... }
}

В response.tactical_plan, creative_requirements, landing_requirements, tracking_requirements, machine_spec:

всё, что мы описали в прошлый раз.

В decision_log:
{
  "step": "tactical_spec",
  "decision": {
    "meta_campaigns": 1,
    "adsets_per_campaign": 2,
    "creatives_per_adset": 2
  },
  "rationale": "Balance between exploration and budget; ensure >=100 clicks per cell",
  "sources": ["metrics_model", "benchmarks.meta"]
}

8. Agent F — Risk & Compliance Checker

Роль: проверить риски (бизнес, статистика, операции) и комплаенс с Ads/Privacy.

Вход

response.value_messaging

response.tactical_plan

response.landing_requirements

response.tracking_requirements

request.constraints

request.geo_language

RAG:

09-platform-policies-risks (Meta/Google/TikTok/LinkedIn)

GDPR/CCPA summary (если есть в базе)

Выход
В internal.risk_model:
"risk_model": {
  "risks": [
    {
      "risk_id": "R1",
      "category": "budget",
      "description": "Budget might be insufficient for 3 cells",
      "probability": "medium",
      "impact": "high",
      "mitigation": "reduce cells or extend duration"
    }
  ],
  "compliance_issues": [
    {
      "policy": "meta_ads",
      "issue": "time_saved_claim_might_be_exaggerated",
      "recommendation": "use 'up to 10 hours' wording and add disclaimer"
    }
  ]
}

В response.risk_assessment и response.compliance_assessment.
В decision_log:
{
  "step": "risk_compliance",
  "decision": {
    "ads_policies_ok": true,
    "issues_count": 1
  },
  "rationale": "Only minor wording adjustment needed for claims",
  "sources": ["policies.meta_ads", "gdpr_consent_guidelines"]
}

Как всё вяжется вместе (короткий пример последовательности)

Оркестратор создаёт work_state с request.

A.Diagnostic → заполняет hypothesis_analysis.

B.Segment → уточняет ICP/JTBD.

C.ValueMessaging → формирует ценность и месседжи.

G.Metrics → задаёт KPI, MDE, min samples.

D.ChannelExperiment → каналка + test cells + budget split.

E.Tactics → кампании, креативы, лендинг, трекинг, machine_spec.

F.RiskCompliance → добавляет риски/комплаенс и рекомендации.

Оркестратор → собирает всё в SovaStrategyResponse, возвращает наружу.