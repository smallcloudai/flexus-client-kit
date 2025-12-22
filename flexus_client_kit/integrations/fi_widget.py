from typing import Dict, Any, Optional
from flexus_client_kit import ckit_cloudtool

PRINT_WIDGET_TOOL = ckit_cloudtool.CloudTool(
    name="print_widget",
    description="Print UI widgets for the user to interact with.",
    parameters={
        "type": "object",
        "properties": {
            "t": {
                "type": "string",
                "description": "Widget type: 'upload-files', 'open-bot-setup-dialog', 'restart-chat', 'open-form-popup'",
                "order": 1,
            },
            "q": {
                "type": "string",
                "description": "For restart-chat: question for new chat. For open-form-popup: form name (e.g. 'email-template')",
                "order": 2,
            },
            "data": {
                "type": "string",
                "description": "For open-form-popup: JSON data to pass to the form",
                "order": 3,
            },
        },
        "required": ["t"],
    },
)


async def handle_print_widget(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    if not model_produced_args:
        return "Error: widget type 't' required"

    widget_type = model_produced_args.get("t", "")
    question = model_produced_args.get("q", "")

    if not widget_type:
        return "Error: widget type 't' required"

    if widget_type == "restart-chat":
        if not question:
            return "Error: for restart-chat, non empty question q=\"...\" is also required"

    if widget_type == "open-form-popup":
        if not question:
            return "Error: for open-form-popup, form name q=\"...\" is required"

    return f"Printing UI widget: {widget_type}"
