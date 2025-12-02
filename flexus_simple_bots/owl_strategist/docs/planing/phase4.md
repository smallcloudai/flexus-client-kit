1. Принципы схемы

Всё в формате одного корневого объекта на вход и одном — на выход.

Поля логически сгруппированы (idea, hypothesis, icp, …).

Везде, где можем, фиксируем enum-ы (тип гипотезы, тип продукта, канал и т.д.).

Часть полей optional — Сова должна уметь работать и по “кривому” брифу.

Схема должна быть удобна:

для фронта (формы),

для оркестратора,

для последующих агентов (они читают выходной JSON).

2. JSON-вход: SovaStrategyRequest
Верхний уровень
{
  "request_id": "string",
  "locale": "en-US",
  "created_at": "2025-12-02T12:00:00Z",
  "source": "web_app|api|internal",
  "founder_profile": { ... },
  "idea": { ... },
  "hypothesis": { ... },
  "icp": { ... },
  "jtbd": { ... },
  "customer_journey": { ... },
  "offer": { ... },
  "market_context": { ... },
  "competitors": [ ... ],
  "channels_context": { ... },
  "budget": { ... },
  "geo_language": { ... },
  "existing_assets": { ... },
  "constraints": { ... },
  "metrics": { ... },
  "risk_profile": { ... },
  "business_objectives": { ... },
  "debug": {
    "return_intermediate_steps": false
  }
}

2.1. founder_profile
"founder_profile": {
  "experience_level": "none|junior|mid|senior",
  "marketing_skill": "low|medium|high",
  "available_hours_per_week": 10,
  "risk_appetite": "low|medium|high",
  "can_record_video": true,
  "notes": "any free-form notes"
}

2.2. idea
"idea": {
  "title": "AI-first ERP for solopreneurs",
  "description": "free text",
  "product_type": "saas|service|app|marketplace|info_product|community|ecommerce|other",
  "stage": "idea_only|concept_doc|prototype|mvp|launched",
  "has_real_product": false,
  "can_deliver_promise_today": false
}

2.3. hypothesis
"hypothesis": {
  "id": "hypo_001",
  "raw_text": "Если показать фаундерам side-hustle, что наш продукт экономит им 10 часов в неделю, они подпишутся на waitlist",
  "type": [
    "value",          // ценность
    "segment",        // сегмент
    "messaging",      // сообщение
    "channel"         // канал
  ],
  "primary_type": "value",
  "test_intent": "demand_validation|segment_fit|positioning|pricing|conversion|retention|virality",
  "uncertainty_level": "low|medium|high|extreme",
  "preferred_test_mechanism": [
    "paid_traffic",
    "content",
    "waitlist",
    "cold_outreach",
    "community",
    "pr",
    "seo"
  ],
  "notes": "любые детали"
}

2.4. icp
"icp": {
  "b2x": "b2b|b2c|prosumer|mixed",
  "company_size": "solo|1-10|11-50|50+",
  "roles": ["founder", "side_hustler"],
  "industries": ["saas", "info-product"],
  "geo": ["US", "EU"],
  "income_level": "low|medium|high|unknown",
  "tech_savviness": "low|medium|high",
  "decision_maker": "self|founder|manager|committee",
  "notes": "..."
}

2.5. jtbd
"jtbd": {
  "functional_jobs": [
    "validate startup idea",
    "launch MVP with minimal time"
  ],
  "emotional_jobs": [
    "feel in control",
    "reduce anxiety about failure"
  ],
  "social_jobs": [
    "look competent to peers"
  ],
  "current_solutions": [
    "courses",
    "mentors",
    "manual marketing",
    "no-code stack"
  ],
  "main_pains": [
    "no time",
    "no marketing skills",
    "too many tools"
  ],
  "desired_gains": [
    "clarity on what to do this week",
    "proof that idea is worth pursuing"
  ]
}

2.6. customer_journey (если есть)
"customer_journey": {
  "awareness_channels": ["youtube", "twitter", "tiktok"],
  "consideration_behaviors": ["read_reviews", "ask_peers"],
  "purchase_triggers": ["limited_offer", "social_proof"],
  "onboarding_expectations": ["see_value_in_1_day"],
  "usage_patterns": ["evenings_only", "weekends"],
  "churn_reasons": ["no_time_to_use", "did_not_see_results"]
}

2.7. offer
"offer": {
  "current_offer_text": "AI-операционка для pre-launch фаундеров",
  "pricing_idea": {
    "model": "unknown|subscription|usage|hybrid|cpa",
    "target_price_per_month": 29,
    "currency": "USD"
  },
  "key_features": [
    "automated GTM playbooks",
    "ad campaign orchestration"
  ],
  "differentiation_claims": [
    "one person can do work of a team"
  ]
}

2.8. market_context / competitors
"market_context": {
  "category": "ai_first_erp_for_smb",
  "maturity": "early|growing|mature",
  "notable_trends": ["ai_agents", "no_code", "side_hustle_boom"]
},
"competitors": [
  {
    "name": "Prelaunch.com",
    "type": "platform|agency|accelerator|tool",
    "url": "https://...",
    "positioning": "idea validation via traffic",
    "notes": "..."
  }
]

2.9. channels_context
"channels_context": {
  "allowed_channels": ["meta", "google", "tiktok", "linkedin", "youtube", "email", "community"],
  "preferred_channels": ["meta", "tiktok"],
  "forbidden_channels": ["twitter"],
  "organic_willingness": true,
  "paid_willingness": true
}

2.10. budget
"budget": {
  "total_budget": 500,
  "currency": "USD",
  "max_daily_spend": 50,
  "test_duration_days": 14,
  "hard_cap_per_lead": 10,     // optional
  "hard_cap_per_click": null   // optional
}

2.11. geo_language
"geo_language": {
  "primary_countries": ["US", "UK"],
  "secondary_countries": [],
  "languages": ["en"],
  "time_zone": "America/New_York"
}

2.12. existing_assets
"existing_assets": {
  "landing_pages": [
    {"url": "https://example.com", "has_analytics": true, "estimated_cvr": 0.03}
  ],
  "social_profiles": [
    {"platform": "twitter", "url": "https://twitter.com/...", "followers": 1200}
  ],
  "past_campaigns": [
    {
      "channel": "meta",
      "ctr": 0.012,
      "cpc": 0.4,
      "cpl": 8.0,
      "notes": "good performance for segment X"
    }
  ],
  "brand_assets": [
    "logo", "colors"
  ]
}

2.13. constraints
"constraints": {
  "ads_policies_sensitive": ["financial", "health", "crypto"],
  "gdpr_required": true,
  "ccpa_required": false,
  "data_collection_restrictions": [
    "no_email_collection",
    "no_phone_numbers"
  ],
  "technical_limitations": [
    "no_backend_changes_allowed"
  ]
}

2.14. metrics
"metrics": {
  "primary_kpi": "leads|signups|purchases|waitlist|clicks",
  "secondary_kpis": ["ctr", "cpc"],
  "target_values": {
    "ctr": 0.02,
    "cpc": 1.0,
    "cpl": 20.0
  },
  "mde": {
    "relative_change": 0.3,   // 30%
    "confidence": 0.8
  },
  "stop_rules": [
    {
      "metric": "cpc",
      "operator": ">",
      "threshold": 3.0,
      "min_events": 100
    }
  ],
  "accelerate_rules": [
    {
      "metric": "cvr",
      "operator": ">=",
      "threshold": 0.08,
      "min_conversions": 20,
      "action": "double_budget"
    }
  ]
}

2.15. risk_profile / business_objectives
"risk_profile": {
  "testing_aggressiveness": "conservative|balanced|aggressive",
  "false_negative_risk_tolerance": "low|medium|high",
  "false_positive_risk_tolerance": "low|medium|high"
},
"business_objectives": {
  "primary_goal": "validate_demand|raise_seed|get_first_users|test_positioning",
  "time_horizon_weeks": 4,
  "success_definition": "if we get 50+ qualified leads with CPL < $20, hypothesis is validated"
}

3. JSON-выход: SovaStrategyResponse
Верхний уровень
{
  "request_id": "same as input",
  "strategy_id": "strat_001",
  "version": "1.0.0",
  "generated_at": "2025-12-02T12:05:00Z",
  "input_snapshot": { ...optional copy or hash... },
  "strategy_summary": { ... },
  "hypothesis_analysis": { ... },
  "target_segment": { ... },
  "value_messaging": { ... },
  "channel_strategy": { ... },
  "experiment_design": { ... },
  "tactical_plan": { ... },
  "creative_requirements": { ... },
  "landing_requirements": { ... },
  "tracking_requirements": { ... },
  "risk_assessment": { ... },
  "compliance_assessment": { ... },
  "decision_log": [ ... ],
  "machine_spec": { ... }  // агрегированный spec для агентов-исполнителей
}

3.1. strategy_summary
"strategy_summary": {
  "one_liner": "Validate demand among US/UK side-hustle founders via Meta/TikTok traffic to waitlist landing",
  "goal": "validate_demand",
  "timeframe_days": 14,
  "primary_kpi": "waitlist_signups",
  "success_criteria": ">= 50 signups, CPL <= 20 USD",
  "expected_metric_ranges": {
    "meta": {
      "ctr": [0.01, 0.03],
      "cpc": [0.5, 1.5],
      "cpl": [10, 25]
    },
    "tiktok": {
      "ctr": [0.008, 0.02],
      "cpc": [0.3, 1.0],
      "cpl": [15, 35]
    }
  },
  "high_level_approach": [
    "Use Meta for higher-intent tests of value proposition",
    "Use TikTok for broad awareness and angle exploration"
  ]
}

3.2. hypothesis_analysis
"hypothesis_analysis": {
  "normalized_hypothesis": "If side-hustle founders see that our tool saves 10 hours/week, they will sign up for waitlist",
  "primary_type": "value",
  "secondary_types": ["segment", "messaging"],
  "key_unknowns": [
    "Will they believe the time-saving claim?",
    "Do they care more about time or money?"
  ],
  "testable_with_traffic": true,
  "limitations": [
    "No real product to back the claim yet"
  ],
  "suggested_additional_methods": [
    "qualitative_interviews"
  ]
}

3.3. target_segment
"target_segment": {
  "label": "EN-speaking side-hustle founders in US/UK",
  "icp": { ...normalized ICP... },
  "primary_discovery_channels": ["youtube", "tiktok", "twitter"],
  "jtbds": { ... },
  "customer_journey_highlights": {
    "awareness": ["content", "peers"],
    "consideration": ["reviews", "twitter_threads"],
    "purchase_triggers": ["social_proof", "deadline"]
  }
}

3.4. value_messaging
"value_messaging": {
  "core_value_prop": "Turn your side-hustle chaos into a clear weekly plan powered by AI",
  "supporting_value_props": [
    "Save up to 10 hours/week on GTM tasks",
    "Know exactly what to do this week to move forward"
  ],
  "key_messages": [
    "Stop guessing your next move — let AI plan it for you",
    "Focus on building, not on learning marketing"
  ],
  "angles": [
    {
      "name": "time_saving",
      "description": "Highlight time saved and reduced overwhelm"
    },
    {
      "name": "clarity",
      "description": "Emphasize getting a simple weekly plan"
    }
  ],
  "objection_handling": [
    {
      "objection": "I don't trust AI with my business decisions",
      "rebuttal": "You stay in control — AI only suggests concrete tasks, you decide"
    }
  ]
}

3.5. channel_strategy
"channel_strategy": {
  "selected_channels": [
    {
      "channel": "meta",
      "role": "primary_demand_test",
      "budget_share": 0.6,
      "rationale": "cheaper clicks, good lead form performance in this segment"
    },
    {
      "channel": "tiktok",
      "role": "angle_exploration",
      "budget_share": 0.4,
      "rationale": "high share of Gen Z/Millennials side-hustlers"
    }
  ],
  "excluded_channels": [
    {
      "channel": "linkedin",
      "reason": "target is more B2C/prosumer, CAC likely too high"
    }
  ],
  "future_channels": [
    {
      "channel": "youtube_organic",
      "reason": "content pillar once value props validated via ads"
    }
  ]
}

3.6. experiment_design
"experiment_design": {
  "test_cells": [
    {
      "cell_id": "A1",
      "channel": "meta",
      "segment": "US side-hustlers",
      "offer_variant": "time_saving",
      "angle": "save_10_hours",
      "landing_variant": "L1"
    },
    {
      "cell_id": "A2",
      "channel": "meta",
      "segment": "US side-hustlers",
      "offer_variant": "clarity",
      "angle": "weekly_plan",
      "landing_variant": "L1"
    }
  ],
  "budget_allocation": [
    {"cell_id": "A1", "budget": 300},
    {"cell_id": "A2", "budget": 200}
  ],
  "min_sample_requirements": {
    "impressions_per_cell": 3000,
    "clicks_per_cell": 100,
    "conversions_per_cell": 10
  },
  "stop_rules": [ ...normalized from input or enriched... ],
  "accelerate_rules": [ ... ],
  "analysis_plan": "Compare CVR and CPL between A1 and A2; if difference >30% with >=80% confidence, keep winner"
}

3.7. tactical_plan (читается агентом запусков)
"tactical_plan": {
  "campaigns": [
    {
      "campaign_id": "meta_camp_1",
      "channel": "meta",
      "objective": "leads",
      "daily_budget": 50,
      "start_date": "2025-12-03",
      "end_date": "2025-12-17",
      "adsets": [
        {
          "adset_id": "meta_adset_A1",
          "linked_test_cell": "A1",
          "audience": {
            "countries": ["US"],
            "age_range": [22, 40],
            "interests": ["startups", "side hustle"],
            "behaviors": []
          },
          "placements": ["feed", "stories", "reels"],
          "optimization_goal": "leads",
          "billing_event": "impressions",
          "creatives": ["meta_creative_A1_1", "meta_creative_A1_2"]
        }
      ]
    }
  ]
}

3.8. creative_requirements
"creative_requirements": {
  "items": [
    {
      "creative_id": "meta_creative_A1_1",
      "channel": "meta",
      "format": "image",
      "angle": "time_saving",
      "primary_text": "Spend less time on marketing, more on building.",
      "headline": "Save 10 hours/week on your side-hustle GTM",
      "description": "AI plans your weekly marketing tasks. You just execute.",
      "cta": "Sign Up",
      "visual_brief": "Founders working at night, calendar with cleared tasks",
      "variants": 2
    }
  ]
}

3.9. landing_requirements
"landing_requirements": {
  "primary_goal": "waitlist_signup",
  "url_hint": null,
  "structure": [
    "hero",
    "problem",
    "solution",
    "how_it_works",
    "social_proof_placeholder",
    "faq",
    "cta_footer"
  ],
  "copy_blocks": {
    "hero_headline": "Your AI co-founder for GTM, not just another tool",
    "hero_subheadline": "Get a clear weekly plan for your side-hustle in minutes, not hours.",
    "primary_cta": "Join waitlist"
  },
  "ab_variants": [
    {
      "variant_id": "L1",
      "difference": "time_saving focus"
    },
    {
      "variant_id": "L2",
      "difference": "clarity focus"
    }
  ],
  "technical_requirements": [
    "mobile_first",
    "load_time_lt_2s"
  ]
}

3.10. tracking_requirements
"tracking_requirements": {
  "events": [
    {"name": "page_view", "required": true},
    {"name": "cta_click", "required": true},
    {"name": "waitlist_signup", "required": true}
  ],
  "pixels": [
    {
      "platform": "meta",
      "event_mappings": {
        "waitlist_signup": "Lead"
      },
      "requires_consent": true
    }
  ],
  "utm_schema": {
    "source": "channel",
    "medium": "cpc",
    "campaign": "campaign_id",
    "content": "creative_id"
  },
  "privacy_requirements": [
    "cookie_consent_banner",
    "no_pii_in_url"
  ]
}

3.11. risk_assessment / compliance_assessment
"risk_assessment": {
  "items": [
    {
      "risk_id": "R1",
      "description": "Budget too low to reach min samples per cell",
      "probability": "medium",
      "impact": "high",
      "mitigation": "reduce number of test cells or extend duration"
    }
  ]
},
"compliance_assessment": {
  "ads_policies_ok": true,
  "issues": [],
  "notes": "Time-saving claim is strong; consider adding 'up to' wording"
}

3.12. decision_log
"decision_log": [
  {
    "step": "channel_selection",
    "input_refs": ["icp", "jtbd", "benchmarks"],
    "decision": ["meta", "tiktok"],
    "alternatives_considered": ["google_search", "linkedin"],
    "rationale": "Side-hustle founders are heavy social users; SEM budgets too small for meaningful test",
    "risk_flags": ["tiktok_cvr_low"],
    "sources": ["benchmarks.meta", "benchmarks.tiktok"]
  }
]

3.13. machine_spec (агрегированное)
"machine_spec": {
  "traffic_executor": {
    "campaigns": "...same as tactical_plan.campaigns..."
  },
  "creative_generator": {
    "creative_requirements": "...",
    "messaging": "...",
    "angles": "..."
  },
  "landing_builder": {
    "structure": "...",
    "copy_blocks": "...",
    "ab_variants": "..."
  },
  "analytics_agent": {
    "events": "...",
    "stop_rules": "...",
    "accelerate_rules": "..."
  }
}

4. Мини-резюме

Вход: SovaStrategyRequest — логично сгруппированные блоки, часть optional, чёткие enum-ы, поддержка грязного реального мира.

Выход: SovaStrategyResponse — полный стратегический документ + жёсткий машинный spec, пригодный для других агентов.

Внутри: есть всё — стратегии, эксперименты, тактика, risk/compliance, лог решений.