from typing import Dict, Any, Optional
from flexus_client_kit.core import ckit_cloudtool

PRINT_WIDGET_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="print_widget",
    description="Print UI widgets for the user to interact with.",
    parameters={
        "type": "object",
        "properties": {
            "t": {"type": "string", "description": "Widget type: 'upload-files', 'open-bot-setup-dialog', 'restart-chat'", "order": 1},
            "q": {"type": "string", "description": "Only required for restart-chat, give the assistant an idea of what to do after the restart, in a sentence or two.", "order": 2},
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

    return f"⏸️WAIT_FOR_USER\nPrinting UI widget: {widget_type}"
