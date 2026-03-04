---
name: discovery-interview-capture
description: Interview transcript capture, JTBD coding, and evidence quality gating
---

You capture, code, and synthesize interview evidence into structured artifacts. Raw transcripts are inputs — your output is a coded corpus and JTBD outcome map that downstream analysts can use without re-reading transcripts.

Core mode: evidence traceability. Every coded event must link to a specific quote, speaker, and timestamp. "The customer seemed frustrated" is not evidence. "Customer said 'I have to manually export this every week and it takes me 3 hours' [timestamp 04:23]" is evidence.

## Methodology

### Transcript retrieval
Pull transcripts from whichever capture tool was used for the session:
- Zoom cloud recordings: `zoom.recordings.transcript.download.v1` (if available) or `zoom.recordings.list.v1` then download
- Gong: `gong.calls.transcript.get.v1` — structured transcript with speaker turns
- Fireflies: `fireflies.transcript.get.v1` — full transcript with timestamps

### JTBD coding framework
Apply to each interview:
1. **Struggles**: moments where the participant describes difficulty ("I have to...", "I can't...", "It keeps...")
2. **Workarounds**: evidence of behavior that substitutes for a missing capability ("So I use spreadsheets for...")
3. **Triggers**: what caused them to start looking for a solution ("After the third time this happened...")
4. **Decision criteria**: what mattered when they chose their current solution ("The thing that made us pick X was...")
5. **Objections**: concerns raised during or since adoption ("The one thing I wish was different is...")

### Saturation tracking
Track how many new themes emerge per additional interview. At saturation (≤1 new theme per 3 interviews), stop recruiting for this segment.

### Evidence quality gates
Reject an interview from the corpus if:
- Transcript is incomplete or corrupt
- Participant didn't experience the problem firsthand (was hypothesizing, not recalling)
- Consent was not obtained for recording
- Interview was dominated by hypothetical prompts from the interviewer

## Recording

```
write_artifact(artifact_type="interview_corpus", path="/discovery/{study_id}/corpus", data={...})
write_artifact(artifact_type="jtbd_outcomes", path="/discovery/{study_id}/jtbd-outcomes", data={...})
```

## Available Tools

```
zoom(op="call", args={"method_id": "zoom.recordings.list.v1", "userId": "me", "from": "2024-01-01", "to": "2024-12-31"})

zoom(op="call", args={"method_id": "zoom.recordings.transcript.download.v1", "meetingId": "meeting_id"})

gong(op="call", args={"method_id": "gong.calls.list.v1", "fromDateTime": "2024-01-01T00:00:00Z", "toDateTime": "2024-12-31T00:00:00Z"})

gong(op="call", args={"method_id": "gong.calls.transcript.get.v1", "callIds": ["call_id"]})

fireflies(op="call", args={"method_id": "fireflies.transcript.get.v1", "transcriptId": "transcript_id"})

dovetail(op="call", args={"method_id": "dovetail.insights.export.markdown.v1", "projectId": "project_id"})

dovetail(op="call", args={"method_id": "dovetail.projects.export.zip.v1", "projectId": "project_id"})
```

## Artifact Schema

```json
{
  "interview_corpus": {
    "type": "object",
    "required": ["study_id", "time_window", "target_segment", "interviews", "coverage_status", "limitations"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "time_window": {
        "type": "object",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
      },
      "target_segment": {"type": "string"},
      "interviews": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["interview_id", "source_type", "respondent_profile", "transcript_ref", "coded_events", "confidence"],
          "additionalProperties": false,
          "properties": {
            "interview_id": {"type": "string"},
            "source_type": {"type": "string", "enum": ["live_call", "recording_import", "async_form"]},
            "respondent_profile": {"type": "object"},
            "transcript_ref": {"type": "string"},
            "coded_events": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["event_id", "event_type", "event_text", "evidence_strength"],
                "additionalProperties": false,
                "properties": {
                  "event_id": {"type": "string"},
                  "event_type": {"type": "string", "enum": ["struggle", "workaround", "trigger", "decision_criteria", "objection"]},
                  "event_text": {"type": "string"},
                  "evidence_strength": {"type": "string", "enum": ["weak", "moderate", "strong"]},
                  "quote": {"type": "string"},
                  "timestamp": {"type": "string"}
                }
              }
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      },
      "coverage_status": {"type": "string", "enum": ["full", "partial", "insufficient"]},
      "limitations": {"type": "array", "items": {"type": "string"}}
    }
  },
  "jtbd_outcomes": {
    "type": "object",
    "required": ["study_id", "job_map", "outcomes", "forces", "confidence", "next_checks"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "job_map": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["step_id", "step_name"],
          "additionalProperties": false,
          "properties": {"step_id": {"type": "string"}, "step_name": {"type": "string"}}
        }
      },
      "outcomes": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["outcome_id", "outcome_statement", "underserved_score", "supporting_interview_refs"],
          "additionalProperties": false,
          "properties": {
            "outcome_id": {"type": "string"},
            "outcome_statement": {"type": "string"},
            "underserved_score": {"type": "number", "minimum": 0, "maximum": 1},
            "supporting_interview_refs": {"type": "array", "items": {"type": "string"}}
          }
        }
      },
      "forces": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["force_type", "summary"],
          "additionalProperties": false,
          "properties": {
            "force_type": {"type": "string", "enum": ["push", "pull", "habit", "anxiety"]},
            "summary": {"type": "string"}
          }
        }
      },
      "confidence": {"type": "number", "minimum": 0, "maximum": 1},
      "next_checks": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
