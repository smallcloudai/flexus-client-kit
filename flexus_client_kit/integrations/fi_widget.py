from typing import Dict, Any, Optional
from flexus_client_kit import ckit_cloudtool

PRINT_WIDGET_PROMPT = """
## Printing Widgets

You are talking to the user inside a UI. Here are some simple widgets you can show to the user:

print_widget(t="upload-files")
print_widget(t="open-bot-setup-dialog")

Your toolset in this chat is fixed, after setting up a new tool (such as an MCP server) to test it
you'll need a restart, print a widget to test, parameter `q` will become the first user
message when clicked:

print_widget(t="restart-chat", q="Test this new XXX tool in this way, in user's language")
"""

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

    wait_for_user = ""
    if widget_type in []:  # none needs it so far, some widgets in Bob need it
        wait_for_user = "⏸️WAIT_FOR_USER\n\n"

    return wait_for_user + "Printing UI widget: {widget_type}"
