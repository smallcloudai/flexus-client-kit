from typing import Dict, Any, Optional, List
from flexus_client_kit import ckit_cloudtool


ASK_QUESTIONS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="ask_questions",
    description="""Ask the user one or more questions with interactive UI. Use this instead of numbered lists.

Types: "single" (pick one), "multi" (pick several), "text" (free-form), "yesno" (yes/no buttons).

Example:
ask_questions(questions=[
    {"text": "What kind of bot do you want?", "type": "single", "options": ["Support", "Sales", "Analytics", "Other"]},
    {"text": "Which channels should it support?", "type": "multi", "options": ["Slack", "Email", "Discord", "Telegram"]},
    {"text": "Should it run on a schedule?", "type": "yesno"},
    {"text": "Any special requirements?", "type": "text"}
])""",
    parameters={
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "description": "List of questions to ask",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The question text"},
                        "type": {"type": "string", "enum": ["single", "multi", "text", "yesno"]},
                        "options": {"type": "array", "items": {"type": "string"}, "description": "Options for single/multi"},
                    },
                    "required": ["text", "type"],
                },
            },
        },
        "required": ["questions"],
        "additionalProperties": False,
    },
)

MAX_QUESTIONS = 6
MAX_OPTIONS = 20
MAX_TEXT_LEN = 500


def _parse_legacy_question(q_str: str) -> Optional[Dict[str, Any]]:
    head, sep, rest = q_str.partition("|")
    if not sep:
        return None
    question = head.strip()
    if not question:
        return None
    type_part, sep2, opts_part = rest.partition("|")
    qtype = type_part.strip().lower()
    if qtype not in ["single", "multi", "text", "yesno"]:
        return None
    options = None
    if sep2 and opts_part.strip():
        options = [o.strip() for o in opts_part.split(";") if o.strip()]
        if not options:
            options = [o.strip() for o in opts_part.split(",") if o.strip()]
    return {"q": question, "type": qtype, "options": options}


def _validate_questions(raw: List[Dict[str, Any]]) -> tuple:
    validated: List[Dict[str, Any]] = []
    for i, item in enumerate(raw[:MAX_QUESTIONS]):
        q = item.get("q", "")
        qtype = item.get("type", "")
        options = item.get("options")
        if not q or qtype not in ["single", "multi", "text", "yesno"]:
            return None, f"Error: question {i+1} invalid"
        if len(q) > MAX_TEXT_LEN:
            return None, f"Error: question {i+1} text too long"
        if qtype in ["single", "multi"]:
            if not options:
                return None, f"Error: question {i+1} ({qtype}) requires options"
            if len(options) > MAX_OPTIONS:
                return None, f"Error: question {i+1} too many options"
        validated.append({"q": q, "type": qtype, "options": options})
    if not validated:
        return None, "Error: at least one valid question required"
    return validated, None


async def handle_ask_questions(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    if not model_produced_args:
        return "Error: questions array is required"

    raw: List[Dict[str, Any]] = []
    if "questions" in model_produced_args and isinstance(model_produced_args["questions"], list):
        for item in model_produced_args["questions"]:
            if not isinstance(item, dict):
                continue
            raw.append({"q": item.get("text", ""), "type": item.get("type", ""), "options": item.get("options")})
    else:
        # legacy q1..q6 string format
        for i in range(1, MAX_QUESTIONS + 1):
            q_str = model_produced_args.get(f"q{i}")
            if not q_str or not isinstance(q_str, str):
                continue
            parsed = _parse_legacy_question(q_str)
            if not parsed:
                return f"Error: q{i} invalid format"
            raw.append(parsed)

    validated, err = _validate_questions(raw)
    if err:
        return err

    summary = ", ".join(f"'{v['q'][:25]}' ({v['type']})" for v in validated)
    return f"⏸️WAIT_FOR_USER\nDisplaying {len(validated)} question(s): {summary}"
