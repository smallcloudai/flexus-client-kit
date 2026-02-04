from typing import Dict, Any, Optional, List
from flexus_client_kit import ckit_cloudtool


ASK_QUESTIONS_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="ask_questions",
    description="""Ask the user one or more questions with interactive UI. Use this instead of numbered lists.

Format: "question text | type | option1, option2, ..."

Types:
- "single": pick one option
- "multi": pick multiple options
- "text": free-form input (no options needed)
- "yesno": yes/no buttons (no options needed)

Example:
ask_questions(
    q1="What kind of bot do you want? | single | Support, Sales, Analytics, Other",
    q2="Which channels should it support? | multi | Slack, Email, Discord, Telegram",
    q3="Should it run on a schedule? | yesno",
    q4="Any special requirements? | text"
)""",
    parameters={
        "type": "object",
        "properties": {
            "q1": {"type": "string", "description": "First question: 'text | type | options'"},
            "q2": {"type": "string", "description": "Second question (optional)"},
            "q3": {"type": "string", "description": "Third question (optional)"},
            "q4": {"type": "string", "description": "Fourth question (optional)"},
            "q5": {"type": "string", "description": "Fifth question (optional)"},
            "q6": {"type": "string", "description": "Sixth question (optional)"},
        },
        "required": ["q1"],
        "additionalProperties": False,
    },
)

MAX_QUESTIONS = 6
MAX_OPTIONS = 20
MAX_TEXT_LEN = 500


def parse_question(q_str: str) -> Optional[Dict[str, Any]]:
    # Split on first | to get question
    head, sep, rest = q_str.partition("|")
    if not sep:
        return None
    question = head.strip()
    if not question:
        return None
    # Split remainder on first | to get type and options
    type_part, sep2, opts_part = rest.partition("|")
    qtype = type_part.strip().lower()
    if qtype not in ["single", "multi", "text", "yesno"]:
        return None
    options = None
    if sep2 and opts_part.strip():
        options = [o.strip() for o in opts_part.split(",") if o.strip()]
    return {"q": question, "type": qtype, "options": options}


async def handle_ask_questions(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    if not model_produced_args:
        return "Error: at least q1 is required"

    validated: List[Dict[str, Any]] = []
    for i in range(1, MAX_QUESTIONS + 1):
        q_str = model_produced_args.get(f"q{i}")
        if not q_str or not isinstance(q_str, str):
            continue
        parsed = parse_question(q_str)
        if not parsed:
            return f"Error: q{i} invalid format. Use 'question | type | options'"
        if len(parsed["q"]) > MAX_TEXT_LEN:
            return f"Error: q{i} text too long"
        if parsed["type"] in ["single", "multi"]:
            if not parsed["options"]:
                return f"Error: q{i} ({parsed['type']}) requires options"
            if len(parsed["options"]) > MAX_OPTIONS:
                return f"Error: q{i} too many options"
        validated.append(parsed)

    if not validated:
        return "Error: at least one valid question required"

    summary = ", ".join(f"'{v['q'][:25]}' ({v['type']})" for v in validated)
    return f"⏸️WAIT_FOR_USER\nDisplaying {len(validated)} question(s): {summary}"
