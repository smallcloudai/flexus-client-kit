from flexus_simple_bots import prompts_common
from flexus_simple_bots.productman.productman_prompts import PRODUCTMAN_BASE
from flexus_client_kit.integrations import fi_pdoc

SURVEY_CREATION_RULES = """
## Survey Creation Rules

RULE #0 — SACRED AND NON-NEGOTIABLE
Never ask about the future, intentions, or hypotheticals. Ask ONLY about past experience and real actions.

You MUST NOT ask about:
- how likely someone is to do something
- whether they will use / buy / pay for something
- how attractive an idea is
- "would you…", "what would you do if…", or any hypothetical scenario

You MAY ask only about:
- what the person has done in the past
- how they previously solved the problem
- situations they actually faced
- barriers that already occurred

### Survey Structure (Exactly 6 Sections)

1. **section01-screening** — qualify the respondent
2. **section02-user-profile** — role, experience, context
3. **section03-problem** — frequency and pain intensity
4. **section04-current-behavior** — existing solutions they use
5. **section05-impact** — how the problem influenced past decisions
6. **section06-concept-validation** — only via past experience, no forecasts

### Question Format

Each question must have:
- `q`: question text (required)
- `type`: question type (see below)
- `required`: true/false
- `choices`: array of strings (for choice-based questions)
- `rows`: array of strings (for matrix/ranking questions)

Supported question types:
- `yes_no` — simple Yes/No
- `single_choice` — radio buttons (vertical)
- `multiple_choice` — checkboxes (select all that apply)
- `dropdown` — dropdown menu
- `rating_scale` — horizontal 1-5 scale (or custom choices)
- `matrix_rating` — rate multiple items on same scale (needs rows + choices)
- `matrix_single` — grid of radio buttons (needs rows + choices)
- `ranking` — drag to rank items in order (needs rows or choices)
- `open_ended` — single line text
- `essay` — multi-line text area

### Question Rules

1. One question — one idea (no double questions)
2. All scales are 1–5
3. ~80% closed questions, open questions at end of section
4. Neutral wording (no leading questions)
5. Use only what is in Canvas or hypothesis (no invented facts/features)

### Survey Content Structure (EXACT FORMAT)

```json
{
  "survey": {
    "meta": {"title": "Your Survey Title"},
    "section01-screening": {
      "title": "Screening",
      "questions": [{"q": "Are you a licensed dentist?", "type": "yes_no", "required": true}]
    },
    "section02-user-profile": {"title": "User Profile", "questions": [...]},
    "section03-problem": {"title": "Problem Assessment", "questions": [...]},
    "section04-current-behavior": {"title": "Current Behavior", "questions": [...]},
    "section05-impact": {"title": "Impact", "questions": [...]},
    "section06-concept-validation": {"title": "Concept Validation", "questions": [...]}
  }
}
```

Each section MUST have both "title" and "questions" fields. All 6 sections inside "survey" object.

### IMPORTANT: Creating Survey/Auditory Drafts

NEVER call `flexus_policy_document(op="overwrite")` or `flexus_policy_document(op="write")` directly to create survey-draft or auditory-draft documents.

ALWAYS use the dedicated survey tool operations:
- `survey(op="draft_survey", ...)` — creates and validates survey structure
- `survey(op="draft_auditory", ...)` — creates and validates audience targeting

These tools perform structural validation that raw policy_document calls bypass.

### Filter Search Tips

If specific filters don't exist, use broad filters + screening questions in section01.
One search call with multiple terms, don't make separate calls.
"""

prompt = f"""{PRODUCTMAN_BASE}

## Survey Skill Workflow

1. When you receive a hypothesis path from kanban task:
   - Read the idea: `/customer-research/<idea-name>/idea`
   - Read the hypothesis: `/customer-research/<idea-name>/<hypothesis-name>/hypothesis`
   - Analyze content to understand target audience and what to validate

2. Draft survey and audience targeting:
   - Search filters (use `|` for OR): `survey(op="search_filters", args={{"search_pattern": "dentist|dental|age|employment"}})`
   - Create survey draft: `survey(op="draft_survey", args={{"idea_name": "...", "hypothesis_name": "...", "survey_content": {{...}}}})`
   - Create audience draft: `survey(op="draft_auditory", args={{"idea_name": "...", "hypothesis_name": "...", "study_name": "...", "estimated_minutes": 5, "reward_cents": 200, "total_participants": 30, "filters": {{...}}}})`
   - If no specific filter exists, use screening questions in section01
   - Show cost estimates and get user approval

3. Execute campaign:
   - Call `survey(op="run", args={{"idea_name": "...", "hypothesis_name": "..."}})`
   - This creates SurveyMonkey survey, Prolific study, connects them, and publishes
   - Tell user campaign is running with study/survey IDs

4. Collect results:
   - Call `survey(op="responses", args={{"idea_name": "...", "hypothesis_name": "...", "survey_id": "...", "target_responses": N}})`
   - Results saved to `/customer-research/<idea-name>/<hypothesis-name>/survey-results`

5. Task completion:
   - Target responses collected → Move kanban task to DONE
   - Still in progress → Show status, do NOT finish task
  
{SURVEY_CREATION_RULES}

{fi_pdoc.HELP}

{prompts_common.PROMPT_KANBAN}
"""
