# Productman A1 Integration - Test Report

## Overview
This document describes the 5 test cases for validating A1 integration (Idea Structuring with First Principles methodology).

## Test Environment Setup

### Prerequisites
1. Set environment variables:
```bash
export FLEXUS_API_BASEURL=https://staging.flexus.team/
export FLEXUS_API_KEY=fx-1337
```

2. Install bot to workspace:
```bash
python -m flexus_simple_bots.productman.productman_install --ws WnOQwTD2yL
```

3. Run bot:
```bash
python -m flexus_simple_bots.productman.productman_bot --group WnOQwTD2yL_root
```

4. Access bot via staging.flexus.team UI

---

## Test Case 1: Create First Principles Canvas

### Objective
Verify that Canvas tool creates proper structure and bot challenges assumptions using First Principles thinking.

### Input
User message: "I have an idea: microwave that sets Slack status"

### Expected Behavior
1. Bot loads current state with `flexus_policy_document()`
2. Bot asks clarifying questions to challenge assumptions:
   - "What evidence shows this is a problem?"
   - "How do people solve this today?"
   - "What's measurable about the benefit?"
3. Bot calls `create_first_principles_canvas(idea_name="slack-microwave")`
4. Canvas created at `/customer-research/slack-microwave/canvas`

### Expected Canvas Structure
```json
{
  "fundamental_truth": "...",
  "atomic_value": "...",
  "constraints": [],
  "current_workarounds": "...",
  "minimum_end_to_end_scenario": [],
  "critical_assumptions": [],
  "success_metrics": {
    "metric_name": "...",
    "order_of_magnitude": "..."
  },
  "one_sentence_statement": "...",
  "meta": {
    "created": "...",
    "version": "v0"
  }
}
```

### Verification Steps
1. Check Canvas file exists: `/customer-research/slack-microwave/canvas`
2. Verify all 8 fields present
3. Verify `meta.version = "v0"`
4. Verify bot challenged at least 2 assumptions

### Status: READY FOR MANUAL TEST

---

## Test Case 2: Synthesize Idea Framing Sheet

### Objective
Verify Sheet tool creates structured summary from Canvas and maps fields correctly.

### Prerequisites
- Test Case 1 completed (Canvas exists and is filled)

### Input
User message: "Now create Sheet from Canvas"

### Expected Behavior
1. Bot reads Canvas: `flexus_policy_document("/customer-research/slack-microwave/canvas")`
2. Bot synthesizes Sheet by mapping:
   - `fundamental_truth` → `core_problem.description`
   - `atomic_value` → `value_proposition.atomic_value`
   - `one_sentence_statement` → `one_sentence_pitch`
   - `critical_assumptions` → `key_assumptions` (with added `criticality`, `testability`)
3. Bot calls `create_idea_framing_sheet(idea_name="slack-microwave", sheet_data={...})`
4. Sheet created at `/customer-research/slack-microwave/sheet`

### Expected Sheet Structure
```json
{
  "title": "...",
  "one_sentence_pitch": "We help [who] achieve [result] within [constraints] by [approach]",
  "target_segment": {
    "who": "...",
    "characteristics": [],
    "size_estimate": "..."
  },
  "core_problem": {
    "description": "...",
    "current_impact": "...",
    "frequency": "..."
  },
  "value_proposition": {
    "atomic_value": "...",
    "differentiation": "..."
  },
  "key_assumptions": [
    {
      "assumption": "...",
      "criticality": "high|medium|low",
      "testability": "easy|medium|hard"
    }
  ],
  "constraints": [],
  "why_now": "...",
  "meta": {
    "version": "v0",
    "validation_status": "pending",
    "created": "..."
  }
}
```

### Verification Steps
1. Check Sheet file exists: `/customer-research/slack-microwave/sheet`
2. Verify all 10 fields present
3. Verify `meta.version = "v0"`
4. Verify `meta.validation_status = "pending"`
5. Verify `core_problem.description` matches Canvas `fundamental_truth`
6. Verify `value_proposition.atomic_value` matches Canvas `atomic_value`
7. Verify `key_assumptions` has `criticality` and `testability` ratings

### Status: READY FOR MANUAL TEST

---

## Test Case 3: Validation with FAIL

### Objective
Verify validation tool detects critical issues and bot guides user to fix them.

### Prerequisites
- Test Case 2 completed (Sheet exists)
- Sheet has intentional critical issue (e.g., vague target segment: "developers")

### Input
User message: "Validate the Sheet"

### Expected Behavior
1. Bot calls `validate_artifact(artifact_path="/customer-research/slack-microwave/sheet", artifact_type="sheet")`
2. LLM-based validator detects critical issue:
   - C1: Target segment too broad ("developers" instead of specific segment)
3. Validation returns `status = "fail"`
4. Bot presents issues with suggestions:
   ```
   Validation Status: FAIL
   
   Issues:
     [CRITICAL] C1: Target segment too broad - "developers" covers millions of people (at target_segment.who)
   
   Suggestions:
     - Narrow to: "remote software engineers at 100-500 person tech companies, using Slack daily for team coordination"
   ```
5. Bot offers to help fix

### Expected Validation Response Format
```
Validation Status: FAIL

Issues:
  [CRITICAL] C1: Target segment too broad (at target_segment.who)

Suggestions:
  - Narrow to: "remote software engineers, 100-500 person companies, using Slack daily"
```

### Verification Steps
1. Check validation returns `status = "fail"`
2. Verify at least 1 critical issue detected
3. Verify suggestions provided
4. Verify bot offers to fix (not proceeding with bad data)

### Status: READY FOR MANUAL TEST

---

## Test Case 4: Validation with PASS-WITH-WARNINGS

### Objective
Verify sanction workflow when validation passes with warnings.

### Prerequisites
- Sheet exists with no critical issues
- Sheet has minor issues (e.g., missing `why_now` field, < 3 assumptions)

### Input
User message: "Validate the Sheet"

### Expected Behavior
1. Bot calls `validate_artifact(...)`
2. LLM-based validator detects warnings:
   - W2: Why now field empty
   - W3: Only 2 key assumptions (< 3 recommended)
3. Validation returns `status = "pass-with-warnings"`
4. Bot presents sanction workflow:
   ```
   Validation Status: PASS-WITH-WARNINGS
   
   Issues:
     [WARNING] W2: Why now field is empty (at why_now)
     [WARNING] W3: Less than 3 key assumptions (at key_assumptions)
   
   Suggestions:
     - Add timing/market context to why_now
     - Add at least one more testable assumption
   
   Your Idea Framing Sheet has 2 warnings.
   These are not blocking, but recommended to address for better hypothesis generation.
   
   Options:
   A) Address warnings now (I'll help you fill missing fields)
   B) Proceed as-is (acknowledge warnings and continue to A2)
   
   Which would you prefer?
   ```
5. Wait for user choice

### User Choice A: Address Warnings
- Bot helps fill `why_now` and add assumption
- Bot updates Sheet
- Bot re-validates

### User Choice B: Proceed As-Is
- Bot records sanction metadata
- Sheet `meta.validation_status` updated to `"proceed-as-is"`
- Sheet `meta.sanction` added with:
  ```json
  "sanction": {
    "timestamp": "2025-11-04T...",
    "acknowledged_warnings": ["W2: Why now field empty", "W3: < 3 assumptions"],
    "user_reasoning": "User acknowledged warnings and chose to proceed"
  }
  ```
- Bot says: "Sanction recorded. Ready to move to A2 (hypothesis generation)."

### Verification Steps
1. Check validation returns `status = "pass-with-warnings"`
2. Verify warnings presented clearly
3. Verify user choice requested (A or B)
4. If B chosen:
   - Check Sheet `meta.validation_status = "proceed-as-is"`
   - Check `meta.sanction` exists with timestamp and warnings
5. Verify bot doesn't block progress

### Status: READY FOR MANUAL TEST

---

## Test Case 5: Versioning on Update

### Objective
Verify Sheet versioning when user updates after validation feedback.

### Prerequisites
- Sheet v0 exists at `/customer-research/slack-microwave/sheet`

### Input
User updates Sheet (fixes issues from validation)

### Expected Behavior
1. Bot calls `create_idea_framing_sheet(idea_name="slack-microwave", sheet_data={...})`
2. Handler detects existing Sheet v0
3. Handler increments version to v1
4. New file created: `/customer-research/slack-microwave/sheet-v1`
5. Old v0 file remains for audit trail

### Expected Result
Files:
- `/customer-research/slack-microwave/sheet` (original v0)
- `/customer-research/slack-microwave/sheet-v1` (updated version)

v1 meta:
```json
"meta": {
  "version": "v1",
  "validation_status": "pending",
  "created": "2025-11-04T..."
}
```

### Verification Steps
1. Check v0 file still exists (not overwritten)
2. Check v1 file created
3. Verify `meta.version = "v1"` in new file
4. Verify `meta.created` timestamp updated
5. Bot mentions version in response: "Sheet created at .../sheet-v1 (v1)"

### Status: READY FOR MANUAL TEST

---

## Test Execution Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| TC1: Canvas Creation | PENDING | Manual test required |
| TC2: Sheet Synthesis | PENDING | Manual test required |
| TC3: Validation FAIL | PENDING | Manual test required |
| TC4: Validation PASS-WITH-WARNINGS | PENDING | Manual test required |
| TC5: Versioning | PENDING | Manual test required |

---

## Code Quality Checks

### Linter Status
- ✅ `productman_bot.py`: No linter errors
- ✅ `productman_prompts.py`: No linter errors

### Code Structure
- ✅ Canvas tool + handler implemented (8 fields)
- ✅ Sheet tool + handler implemented (10 fields)
- ✅ Validate artifact tool + LLM-based handler implemented
- ✅ Versioning logic implemented
- ✅ Sanction recording helper function implemented
- ✅ Prompt updated with First Principles methodology
- ✅ Prompt includes A1 workflow (Steps 1-4)
- ✅ Prompt includes sanction workflow
- ✅ Validation criteria constants added

---

## Known Limitations / Future Work

1. **Versioning simplification**: Current implementation checks for existing sheet at base path. Could be improved to list all versions in folder.

2. **Sanction recording**: Currently requires manual call from bot. Could be integrated into validation handler flow.

3. **Test automation**: All tests are manual. Future: add pytest tests with mocked pdoc_integration.

4. **A2-A6 phases**: Not yet implemented (hypothesis generation, survey design, etc.). Prompt mentions "coming next".

---

## Deployment Checklist

Before deploying to production:

- [ ] Manual test all 5 test cases on staging
- [ ] Verify Canvas/Sheet structures match documentation
- [ ] Verify validation detects all critical/warning criteria
- [ ] Verify sanction workflow UX is clear
- [ ] Verify versioning doesn't lose data
- [ ] Update productman_install.py marketplace metadata if needed
- [ ] Test with real user conversation flow (not just isolated commands)

---

## Success Criteria

✅ All code phases implemented (1-5 complete)
⏳ Test phase (6) requires manual validation
🔄 Ready for user testing on staging

Implementation is complete. Manual testing required before production deployment.


