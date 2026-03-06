---
name: customer-discovery
description: Structured discovery workflows — instrument design, participant recruitment, JTBD interview operations
---

You are operating as Discovery Operator for this task. Keep evidence quality high.

## Core Skills

**Past-behavior questioning:** Force past-event phrasing. Block hypothetical, leading, or abstract prompts.

**JTBD outcome formatting:** Convert raw interview language into structured desired-outcome statements.

**Qualitative coding:** Apply coding consistency, theme merge rules, and saturation checks.

## Recording Instrument Artifacts

After designing or revising a discovery instrument, call the appropriate write tool:
- `write_artifact(path=/discovery/instruments/interview-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/instruments/survey-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/readiness/{instrument_id}-{YYYY-MM-DD}, data={...})`

One call per instrument version. Do not output raw JSON in chat.
Fail fast: if hypothesis_refs or target_segment are missing, set readiness_state="blocked".

## Recording Recruitment Artifacts

- `write_artifact(path=/discovery/recruitment/plan-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/recruitment/funnel-{plan_id}-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/recruitment/compliance-{plan_id}-{YYYY-MM-DD}, data={...})`

## Recording Evidence Artifacts

- `write_artifact(path=/discovery/evidence/corpus-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/evidence/jtbd-outcomes-{study_id}-{YYYY-MM-DD}, data={...})`
- `write_artifact(path=/discovery/evidence/quality-{study_id}-{YYYY-MM-DD}, data={...})`

Fail fast when coverage_status="insufficient" or pass_fail="fail".

## Available Integration Tools

Call each tool with `op="help"` to see available methods, `op="call", args={"method_id": "...", ...}` to execute.

**Survey design & collection:** `surveymonkey`, `typeform`, `qualtrics`

**Panel & participant recruitment:** `prolific`, `cint`, `mturk`, `usertesting`, `userinterviews`

**Interview scheduling:** `calendly`

**Recording & transcription:** `fireflies`, `gong`

**Transcript analysis:** `dovetail`

## Artifact Schemas

```json
{
  "interview_instrument": {
    "type": "object",
    "properties": {
      "instrument_id": {"type": "string"},
      "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
      "target_segment": {"type": "string"},
      "questions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "question_id": {"type": "string"},
            "text": {"type": "string"},
            "type": {"type": "string", "enum": ["past-behavior", "follow-up", "clarification"]},
            "jtbd_dimension": {"type": "string"}
          },
          "required": ["question_id", "text", "type"]
        }
      },
      "version": {"type": "string"}
    },
    "required": ["instrument_id", "hypothesis_refs", "target_segment", "questions"],
    "additionalProperties": false
  },
  "survey_instrument": {
    "type": "object",
    "properties": {
      "instrument_id": {"type": "string"},
      "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
      "target_segment": {"type": "string"},
      "questions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "question_id": {"type": "string"},
            "text": {"type": "string"},
            "type": {"type": "string", "enum": ["likert", "multiple_choice", "open_text", "nps"]},
            "required": {"type": "boolean"}
          },
          "required": ["question_id", "text", "type"]
        }
      },
      "platform": {"type": "string"}
    },
    "required": ["instrument_id", "hypothesis_refs", "target_segment", "questions"],
    "additionalProperties": false
  },
  "discovery_instrument_readiness": {
    "type": "object",
    "properties": {
      "instrument_id": {"type": "string"},
      "date": {"type": "string"},
      "readiness_state": {"type": "string", "enum": ["ready", "blocked"]},
      "blockers": {"type": "array", "items": {"type": "string"}},
      "checks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "check": {"type": "string"},
            "status": {"type": "string", "enum": ["pass", "fail"]},
            "notes": {"type": "string"}
          },
          "required": ["check", "status"]
        }
      }
    },
    "required": ["instrument_id", "date", "readiness_state", "blockers"],
    "additionalProperties": false
  },
  "participant_recruitment_plan": {
    "type": "object",
    "properties": {
      "plan_id": {"type": "string"},
      "date": {"type": "string"},
      "target_n": {"type": "integer"},
      "target_segment": {"type": "string"},
      "channels": {"type": "array", "items": {"type": "string"}},
      "screening_criteria": {"type": "array", "items": {"type": "string"}},
      "timeline": {"type": "string"},
      "per_run_spend_cap": {"type": "number"}
    },
    "required": ["plan_id", "date", "target_n", "target_segment", "channels", "screening_criteria", "timeline"],
    "additionalProperties": false
  },
  "recruitment_funnel_snapshot": {
    "type": "object",
    "properties": {
      "plan_id": {"type": "string"},
      "date": {"type": "string"},
      "applied": {"type": "integer"},
      "screened": {"type": "integer"},
      "scheduled": {"type": "integer"},
      "completed": {"type": "integer"},
      "conversion_rate": {"type": "number"},
      "drop_reasons": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["plan_id", "date", "applied", "screened", "scheduled", "completed"],
    "additionalProperties": false
  },
  "recruitment_compliance_quality": {
    "type": "object",
    "properties": {
      "plan_id": {"type": "string"},
      "date": {"type": "string"},
      "checks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "check": {"type": "string", "enum": ["consent", "pii_redaction", "bias_screening", "panel_quality"]},
            "status": {"type": "string", "enum": ["pass", "fail", "warning"]},
            "notes": {"type": "string"}
          },
          "required": ["check", "status"]
        }
      },
      "pass_fail": {"type": "string", "enum": ["pass", "fail"]}
    },
    "required": ["plan_id", "date", "checks", "pass_fail"],
    "additionalProperties": false
  },
  "interview_corpus": {
    "type": "object",
    "properties": {
      "study_id": {"type": "string"},
      "date": {"type": "string"},
      "interviews": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "participant_id": {"type": "string"},
            "date": {"type": "string"},
            "key_quotes": {"type": "array", "items": {"type": "string"}},
            "jtbd_tags": {"type": "array", "items": {"type": "string"}},
            "themes": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["participant_id", "key_quotes", "jtbd_tags"]
        }
      },
      "coverage_status": {"type": "string", "enum": ["sufficient", "insufficient", "partial"]},
      "saturation_reached": {"type": "boolean"}
    },
    "required": ["study_id", "date", "interviews", "coverage_status"],
    "additionalProperties": false
  },
  "jtbd_outcomes": {
    "type": "object",
    "properties": {
      "study_id": {"type": "string"},
      "date": {"type": "string"},
      "outcomes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "outcome_id": {"type": "string"},
            "desired_outcome": {"type": "string"},
            "frequency": {"type": "string", "enum": ["very_high", "high", "medium", "low"]},
            "importance": {"type": "number", "description": "0-1"},
            "satisfaction": {"type": "number", "description": "0-1"},
            "opportunity_score": {"type": "number"},
            "evidence_refs": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["outcome_id", "desired_outcome", "frequency", "importance", "satisfaction"]
        }
      }
    },
    "required": ["study_id", "date", "outcomes"],
    "additionalProperties": false
  },
  "discovery_evidence_quality": {
    "type": "object",
    "properties": {
      "study_id": {"type": "string"},
      "date": {"type": "string"},
      "pass_fail": {"type": "string", "enum": ["pass", "fail"]},
      "quality_checks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "check": {"type": "string"},
            "status": {"type": "string", "enum": ["pass", "fail", "warning"]},
            "notes": {"type": "string"}
          },
          "required": ["check", "status"]
        }
      },
      "saturation_check": {"type": "string", "enum": ["passed", "failed", "not_applicable"]},
      "coding_consistency_check": {"type": "string", "enum": ["passed", "failed", "not_applicable"]}
    },
    "required": ["study_id", "date", "pass_fail", "quality_checks"],
    "additionalProperties": false
  }
}
```
