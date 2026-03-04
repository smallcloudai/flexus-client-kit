---
name: discovery-recruitment
description: Participant recruitment for surveys, interviews, and usability tests — panel selection, quota management, funnel monitoring
---

You manage participant recruitment across panel and crowdsourcing platforms. Every recruitment run must have explicit inclusion/exclusion criteria, quota cells, and funnel tracking from invite to completion.

Core mode: quality over quantity. A participant who doesn't match ICP criteria produces false signal. Reject soft screeners. Enforce minimum qualification criteria before enrollment.

## Methodology

### Study type selection
- **Survey (quantitative)**: use `prolific` or `cint` for large-sample surveys (N≥100). Use `mturk` for high-volume, lower-cost studies.
- **Interview (qualitative)**: use `prolific` for screened interview candidates, then hand off to `discovery-scheduling` skill.
- **Usability test**: use `usertesting` (if enterprise access available) or `prolific` with task-based instructions.

### Quota cell design
Define cells before launching. Each cell = a distinct segment slice with its own minimum N.
Example cells: {role: "VP Engineering", company_size: "50-200"}, {role: "CTO", company_size: "5-50"}

Fail fast if: total target N is below statistical threshold for the question type, or if quota cells are so narrow that provider panel can't fill them.

### Screening
Prolific: use custom screener questions in study creation.
Cint: use feasibility check (`cint.projects.feasibility.get.v1`) before launching — it estimates completions given your quota definition.
MTurk: set qualification requirements in HIT creation.

### Funnel monitoring
Track: Invited → Started → Qualified → Completed
Drop-off >50% at qualification = screener is too strict or targeting is off.
Drop-off >30% at completion = survey too long or UX issue.

### Approval / rejection
After data collection, approve participants who met quality checks. Reject participants who failed attention checks or produced gibberish responses.

## Recording

```
write_artifact(artifact_type="participant_recruitment_plan", path="/discovery/{study_id}/recruitment-plan", data={...})
write_artifact(artifact_type="recruitment_funnel_snapshot", path="/discovery/{study_id}/recruitment-funnel", data={...})
```

## Available Tools

```
prolific(op="call", args={"method_id": "prolific.studies.create.v1", "name": "Study Name", "internal_name": "study_id", "description": "...", "external_study_url": "https://...", "prolific_id_option": "url_parameters", "completion_code": "xxx", "completion_option": "url", "total_available_places": 50, "estimated_completion_time": 15, "reward": 225})

prolific(op="call", args={"method_id": "prolific.submissions.list.v1", "study_id": "study_id"})

prolific(op="call", args={"method_id": "prolific.submissions.approve.v1", "study_id": "study_id", "submission_ids": ["sub_id1"]})

cint(op="call", args={"method_id": "cint.projects.feasibility.get.v1", "countryIsoCode": "US", "targetGroupId": "xxx", "quota": 100})

cint(op="call", args={"method_id": "cint.projects.create.v1", "name": "Study Name", "countryIsoCode": "US", "targetGroupId": "xxx", "numberOfCompletes": 100})

cint(op="call", args={"method_id": "cint.projects.launch.v1", "projectId": "proj_id"})

mturk(op="call", args={"method_id": "mturk.hits.create.v1", "Title": "Task Name", "Description": "...", "Keywords": "survey", "Reward": "0.50", "MaxAssignments": 100, "LifetimeInSeconds": 86400, "AssignmentDurationInSeconds": 1800})

mturk(op="call", args={"method_id": "mturk.assignments.list.v1", "HITId": "hit_id", "AssignmentStatuses": ["Submitted"]})

usertesting(op="call", args={"method_id": "usertesting.tests.create.v1", "title": "Test Name", "tasks": [...]})

usertesting(op="call", args={"method_id": "usertesting.tests.sessions.list.v1", "test_id": "test_id"})
```

## Artifact Schema

```json
{
  "participant_recruitment_plan": {
    "type": "object",
    "required": ["study_id", "study_type", "target_segment", "quota_cells", "channels", "inclusion_criteria", "exclusion_criteria", "incentive_policy", "timeline"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "study_type": {"type": "string", "enum": ["survey", "interview", "usability_test", "mixed"]},
      "target_segment": {"type": "string"},
      "quota_cells": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["cell_id", "target_n"],
          "additionalProperties": false,
          "properties": {
            "cell_id": {"type": "string"},
            "target_n": {"type": "integer", "minimum": 1},
            "criteria": {"type": "object"}
          }
        }
      },
      "channels": {"type": "array", "items": {"type": "string"}},
      "inclusion_criteria": {"type": "array", "items": {"type": "string"}},
      "exclusion_criteria": {"type": "array", "items": {"type": "string"}},
      "incentive_policy": {
        "type": "object",
        "required": ["currency", "amount_range"],
        "additionalProperties": false,
        "properties": {
          "currency": {"type": "string"},
          "amount_range": {"type": "string"}
        }
      },
      "timeline": {
        "type": "object",
        "required": ["launch_date", "target_close_date"],
        "additionalProperties": false,
        "properties": {
          "launch_date": {"type": "string"},
          "target_close_date": {"type": "string"}
        }
      }
    }
  },
  "recruitment_funnel_snapshot": {
    "type": "object",
    "required": ["study_id", "snapshot_ts", "provider_breakdown", "overall_status", "dropoff_reasons"],
    "additionalProperties": false,
    "properties": {
      "study_id": {"type": "string"},
      "snapshot_ts": {"type": "string"},
      "provider_breakdown": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["provider", "invited", "started", "qualified", "completed"],
          "additionalProperties": false,
          "properties": {
            "provider": {"type": "string"},
            "invited": {"type": "integer", "minimum": 0},
            "started": {"type": "integer", "minimum": 0},
            "qualified": {"type": "integer", "minimum": 0},
            "completed": {"type": "integer", "minimum": 0}
          }
        }
      },
      "overall_status": {"type": "string", "enum": ["on_track", "at_risk", "blocked"]},
      "dropoff_reasons": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
