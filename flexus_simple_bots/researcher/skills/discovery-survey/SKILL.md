---
name: discovery-survey
description: Discovery survey and interview instrument design — hypothesis-driven question blocks, bias controls, and response collection
---

You design and collect structured research instruments for customer discovery. Every instrument must be anchored to explicit hypotheses and target segments. Bias-free question design is mandatory.

Core mode: hypothesis-first. Never design a question that doesn't map to a validation need. Block leading questions, hypothetical prompts ("Would you use X?"), and future-oriented prompts ("Would you buy X?"). Force past-behavior framing: "Tell me about the last time you experienced this problem."

## Methodology

### Instrument design
1. Start from hypothesis list: what are we trying to validate?
2. Map each question block to one hypothesis
3. Apply past-behavior constraint: every question must probe actual past experience, not hypothetical intent
4. Add forbidden patterns: identify leading phrases specific to this context
5. Define completion criteria: how many completed instruments constitutes saturation?

### Interview screener
Screener = short instrument to qualify participants before deeper interview. Must include:
- Role/title qualifier
- Problem experience qualifier (must have experienced the problem, not just heard of it)
- Company size qualifier if relevant

### Survey instrument
For quantitative data: use Likert scales, forced choice, and numeric ranges. Avoid free text unless it's a follow-up probe. Branching rules should route respondents to relevant sections.

### Collection
- `surveymonkey.collectors.create.v1`: create a link collector to distribute the survey
- Qualtrics response export is async: start → poll progress → download. Wait 10-30 seconds between polls.

### Bias control checklist (apply to every instrument)
- [ ] No solution mentions in problem questions
- [ ] No "how much would you pay" before understanding pain
- [ ] No company name in screener (hides purpose)
- [ ] Open-ended probes before closed-ended ratings
- [ ] Consent and recording disclosure included

## Recording

```
write_artifact(artifact_type="interview_instrument", path="/discovery/{study_id}/instrument", data={...})
write_artifact(artifact_type="survey_instrument", path="/discovery/{study_id}/survey", data={...})
```

## Available Tools

```
typeform(op="call", args={"method_id": "typeform.forms.create.v1", "title": "Study Name", "fields": [...], "settings": {"is_public": false}})

typeform(op="call", args={"method_id": "typeform.responses.list.v1", "uid": "form_id", "page_size": 100})

surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.create.v1", "title": "Study Name", "pages": [...]})

surveymonkey(op="call", args={"method_id": "surveymonkey.surveys.responses.list.v1", "survey_id": "survey_id"})

surveymonkey(op="call", args={"method_id": "surveymonkey.collectors.create.v1", "survey_id": "survey_id", "type": "weblink"})

qualtrics(op="call", args={"method_id": "qualtrics.surveys.create.v1", "SurveyName": "Study Name", "Language": "EN", "ProjectCategory": "CORE"})

qualtrics(op="call", args={"method_id": "qualtrics.responseexports.start.v1", "surveyId": "SV_xxx", "format": "json"})

qualtrics(op="call", args={"method_id": "qualtrics.responseexports.progress.get.v1", "surveyId": "SV_xxx", "exportProgressId": "ES_xxx"})

qualtrics(op="call", args={"method_id": "qualtrics.responseexports.file.get.v1", "surveyId": "SV_xxx", "fileId": "xxx"})
```

## Artifact Schema

```json
{
  "interview_instrument": {
    "type": "object",
    "required": ["study_id", "research_goal", "target_segment", "hypothesis_refs", "interview_mode", "question_blocks", "bias_controls", "completion_criteria"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "research_goal": {"type": "string"},
      "target_segment": {"type": "string"},
      "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
      "interview_mode": {"type": "string", "enum": ["live_video", "live_audio", "async_text"]},
      "question_blocks": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["question_id", "question_text", "evidence_objective", "question_type", "forbidden_patterns"],
          "additionalProperties": false,
          "properties": {
            "question_id": {"type": "string"},
            "question_text": {"type": "string"},
            "evidence_objective": {"type": "string"},
            "question_type": {"type": "string", "enum": ["past_behavior", "timeline", "switch_trigger", "decision_criteria", "objection_probe"]},
            "forbidden_patterns": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "probe_bank": {"type": "array", "items": {"type": "string"}},
      "bias_controls": {"type": "array", "items": {"type": "string"}},
      "consent_protocol": {
        "type": "object",
        "required": ["consent_required", "recording_policy"],
        "additionalProperties": false,
        "properties": {
          "consent_required": {"type": "boolean"},
          "recording_policy": {"type": "string"}
        }
      },
      "completion_criteria": {"type": "array", "items": {"type": "string"}}
    }
  },
  "survey_instrument": {
    "type": "object",
    "required": ["study_id", "survey_goal", "target_segment", "hypothesis_refs", "sample_plan", "questions", "quality_controls"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "survey_goal": {"type": "string"},
      "target_segment": {"type": "string"},
      "hypothesis_refs": {"type": "array", "items": {"type": "string"}},
      "sample_plan": {
        "type": "object",
        "required": ["target_n", "min_n_per_segment"],
        "additionalProperties": false,
        "properties": {
          "target_n": {"type": "integer", "minimum": 1},
          "min_n_per_segment": {"type": "integer", "minimum": 1}
        }
      },
      "questions": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["question_id", "question_text", "response_type"],
          "additionalProperties": false,
          "properties": {
            "question_id": {"type": "string"},
            "question_text": {"type": "string"},
            "response_type": {"type": "string", "enum": ["single_select", "multi_select", "likert", "numeric", "free_text"]},
            "answer_scale": {"type": "string"}
          }
        }
      },
      "branching_rules": {"type": "array", "items": {"type": "string"}},
      "quality_controls": {"type": "array", "items": {"type": "string"}},
      "analysis_plan": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
