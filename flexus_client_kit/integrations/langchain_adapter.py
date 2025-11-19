import json
import logging
from typing import Any, Dict, List

import langchain_core.exceptions
import langchain_core.tools
from langchain_core.utils.function_calling import convert_to_openai_tool

logger = logging.getLogger("langchain_adapter")


def langchain_tool_to_cloudtool_params(tool: langchain_core.tools.BaseTool) -> dict:
    openai_format = convert_to_openai_tool(tool)
    return openai_format.get("function", {}).get("parameters", {
        "type": "object",
        "properties": {},
        "required": []
    })


def format_tools_help(tools: List[langchain_core.tools.BaseTool]) -> str:
    help_sections = []
    for tool in tools:
        help_sections.append(f"\n{'='*60}")
        help_sections.append(f"Operation: {tool.name}")
        help_sections.append(f"Description: {tool.description}\n")

        if hasattr(tool, 'args_schema') and tool.args_schema:
            schema = tool.args_schema.model_json_schema()
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            if properties:
                help_sections.append("Arguments:")
                for prop_name, prop_schema in properties.items():
                    is_required = prop_name in required
                    req_marker = "[REQUIRED]" if is_required else "[optional]"
                    prop_desc = prop_schema.get("description", "")
                    prop_type = prop_schema.get("type", "")

                    help_sections.append(f"  - {prop_name} {req_marker}")
                    if prop_type:
                        help_sections.append(f"    type: {prop_type}")
                    if prop_desc:
                        help_sections.append(f"    {prop_desc}")
            else:
                help_sections.append("No arguments required.")
        else:
            help_sections.append("No arguments required.")

    help_sections.append(f"\n{'='*60}\n")
    return "\n".join(help_sections)


async def run_langchain_tool(tool: langchain_core.tools.BaseTool, tool_input: Dict[str, Any]) -> tuple[str, bool]:
    try:
        if hasattr(tool, 'ainvoke'):
            result = await tool.ainvoke(tool_input)
        else:
            result = tool.invoke(tool_input)

        if isinstance(result, str):
            return result, False
        elif isinstance(result, dict) or isinstance(result, list):
            return json.dumps(result, indent=2), False
        else:
            return str(result), False

    except langchain_core.tools.ToolException as e:
        logger.info("Tool error %s: %s", tool.name, e)
        return f"❌ Error: {e}", False
    except Exception as e:
        logger.info("Tool error %s", tool.name, exc_info=True)
        error_msg = str(e).lower()
        is_auth_error = (
            "401" in error_msg or
            "403" in error_msg or
            "insufficientpermissions" in error_msg or
            "insufficient permission" in error_msg
        )
        return f"❌ Error: {e}", is_auth_error
