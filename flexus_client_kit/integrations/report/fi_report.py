import itertools
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from zoneinfo import ZoneInfo

from jinja2 import Template
from pymongo.collection import Collection

from flexus_client_kit import ckit_cloudtool, ckit_mongo, ckit_ask_model
from flexus_client_kit.integrations.report.report_registry import list_available_reports, load_report_config
from flexus_client_kit.integrations.report.report_validator import (
    validate_html_content, sanitize_html, validate_json_content
)

logger = logging.getLogger("report")

CREATE_REPORT_TOOL = ckit_cloudtool.CloudTool(
    name="create_report",
    description="Initialize a new report with arbitrary parameters. Arrays will be used for iteration, scalars for interpolation.",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Base name for the report"},
            "report_type": {"type": "string", "description": "Type of report (e.g., 'adspy')"},
            "parameters": {"type": "string", "description": "JSON object with report parameters. Arrays will be iterated over, scalars used for string interpolation."},
        },
        "required": ["name", "report_type", "parameters"],
    },
)

PROCESS_REPORT_TOOL = ckit_cloudtool.CloudTool(
    name="process_report",
    description="Process all sections in the next incomplete phase using parallel subchats",
    parameters={
        "type": "object",
        "properties": {
            "report_id": {"type": "string", "description": "Report ID"},
        },
        "required": ["report_id"],
    },
)

FILL_SECTION_TOOL = ckit_cloudtool.CloudTool(
    name="fill_report_section",
    description="Fill a report section with content",
    parameters={
        "type": "object",
        "properties": {
            "report_id": {"type": "string", "description": "Report ID"},
            "section_name": {"type": "string", "description": "Section name to fill"},
            "content": {"type": "string", "description": "Data that will be stored in the section. Use null if there is no data to report"},
        },
        "required": ["report_id", "section_name"],
    },
)

REPORT_STATUS_TOOL = ckit_cloudtool.CloudTool(
    name="get_report_status",
    description="Get status and progress of report(s)",
    parameters={
        "type": "object",
        "properties": {
            "report_id": {"type": "string", "description": "Report ID (optional, lists all if not provided)"},
        },
        "required": [],
    },
)

LOAD_METADATA_TOOL = ckit_cloudtool.CloudTool(
    name="load_report_metadata",
    description="Load metadata and statistics from a previous report for comparison",
    parameters={
        "type": "object",
        "properties": {
            "report_id": {"type": "string"},
            "safety_valve": {"type": "integer", "description": "Max output size in KB (default 20KB)"},
        },
        "required": ["report_id"],
    },
)

REPORT_TOOLS = [
    CREATE_REPORT_TOOL,
    PROCESS_REPORT_TOOL,
    FILL_SECTION_TOOL,
    REPORT_STATUS_TOOL,
    LOAD_METADATA_TOOL
]


def _extract_entity_from_section_name(section_name: str, report_params: Dict[str, Any]) -> Optional[str]:
    for param_name, param_value in report_params.items():
        if isinstance(param_value, list):
            for entity in param_value:
                entity_str = str(entity)
                if section_name.endswith(f"_{entity_str}"):
                    return entity_str
                entity_normalized = entity_str.replace(" ", "_").replace("-", "_")
                if entity_normalized in section_name:
                    return entity_str
    return None


def _format_parameters_summary(params: Dict[str, Any]) -> str:
    """Format parameters for display in status messages."""
    if not params:
        return "None"
    
    summary = []
    for key, value in params.items():
        if isinstance(value, list):
            summary.append(f"{key}({len(value)} items)")
        else:
            summary.append(f"{key}:{value}")
    return ', '.join(summary)


def _fix_unicode_corruption(text: str) -> str:
    """Fix corrupted Unicode characters in text."""
    if not text or not isinstance(text, str):
        return text

    def fix_unicode(match):
        hex_part = match.group(1)
        # Convert \x00XX to \u00XX (proper Unicode)
        return f'\\u00{hex_part}'

    fixed_text = re.sub(r'\x00([0-9a-fA-F]{2})', fix_unicode, text)
    if fixed_text != text:
        logger.warning(f"Fixed corrupted Unicode: {repr(text[:100])} -> {repr(fixed_text[:100])}")

    return fixed_text


def _build_iteration_combinations(report_params: Dict[str, Any], sections: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    combos_map = {}
    for section_id, config in sections.items():
        pattern = config.get("iteration")
        iterators = config.get("iterators", {})

        if pattern:
            values_lists = []
            keys = []
            for key, source in iterators.items():
                keys.append(key)
                if source == "from_input":
                    # Look for this key in report_params
                    if key in report_params:
                        param_value = report_params[key]
                        if isinstance(param_value, list):
                            values_lists.append(param_value)
                        else:
                            values_lists.append([param_value])
                    else:
                        logger.warning(f"Parameter '{key}' not found in report_params for section '{section_id}', using empty list")
                        values_lists.append([])
                        # This will result in no tasks for this section
                elif isinstance(source, list):
                    values_lists.append(source)
                else:
                    values_lists.append([source])
            combos = []
            for combo_values in itertools.product(*values_lists):
                combo_dict = dict(zip(keys, combo_values))
                combos.append(combo_dict)

            combos_map[section_id] = combos
        else:
            combos_map[section_id] = [{}]
    return combos_map


def _create_todo_queue(report_id: str, report_params: Dict[str, Any], sections: Dict[str, Any]) -> List[Dict[str, Any]]:
    combos_map = _build_iteration_combinations(report_params, sections)
    tasks = []

    sorted_sections = sorted(sections.items(), key=lambda x: x[1].get("phase", 1))
    for section_id, config in sorted_sections:
        pattern = config.get("iteration")
        description = config.get("description", "")
        example = config.get("example", "")
        is_meta = config["is_meta_section"]

        for combo in combos_map[section_id]:
            if pattern and combo:
                try:
                    formatted = pattern.format(**combo)
                    section_name = f"{section_id}_{formatted}"
                except Exception as e:
                    logger.error(f"Failed to format pattern '{pattern}' with {combo}: {e}")
                    section_name = section_id
            else:
                section_name = section_id

            depends_on = []
            for dep_id in config.get("depends_on", []):
                if dep_id not in combos_map:
                    continue
                dep_config = sections.get(dep_id, {})
                dep_pattern = dep_config.get("iteration")
                for dep_combo in combos_map[dep_id]:
                    # Check if this dependency matches our current combo
                    # (same entity values for shared dimensions)
                    shared_keys = set(combo.keys()) & set(dep_combo.keys())
                    if all(combo.get(k) == dep_combo.get(k) for k in shared_keys):
                        if dep_pattern and dep_combo:
                            dep_formatted = dep_pattern.format(**dep_combo)
                            depends_on.append(f"{dep_id}_{dep_formatted}")
                        else:
                            depends_on.append(dep_id)

            depends_on = list(dict.fromkeys(depends_on))
            formatted_desc = description
            formatted_example = example
            
            interpolation_context = dict(combo)
            for key, value in report_params.items():
                if not isinstance(value, list):  # Only use scalar values for interpolation
                    interpolation_context[key] = value
            
            for key, value in interpolation_context.items():
                formatted_desc = formatted_desc.replace(f"{{{key}}}", str(value))
                formatted_example = formatted_example.replace(f"{{{key}}}", str(value))
            task_text = f"""Task for report: {report_id}
Section: {section_name}
Description: {formatted_desc}"""
            if depends_on:
                task_text += f"\nDependencies: {', '.join(depends_on)} (content will be provided when processing)"
            if formatted_example:
                task_text += f"\n\n=== Expected Format ===\n{formatted_example}"
            extra_instructions = config.get("extra_instructions", [])
            task_text += f"\n\n=== Instructions ===\n"
            if extra_instructions:
                for idx, instruction in enumerate(extra_instructions, 1):
                    formatted_instruction = instruction
                    for key, value in interpolation_context.items():
                        formatted_instruction = formatted_instruction.replace(f"{{{key}}}", str(value))
                    task_text += f"{formatted_instruction}\n"

            task_text += f"\nCall: fill_report_section(report_id='{report_id}', section_name='{section_name}', content=<your_content>)\n\nNote: If there is no data to report for this section, you can use content=null"
            tasks.append({
                "section_name": section_name,
                "section_id": section_id,
                "section_config": config,
                "depends_on": depends_on,
                "is_meta_section": is_meta,
                "task": task_text
            })
    return tasks


async def _export_report_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        report_id: str,
) -> str:
    report_id = _fix_unicode_corruption(report_id)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    template_datetime = datetime.now(tz).strftime("%H:%M UTC")

    try:
        report_doc = await _get_report_doc_by_report_id(mongo_collection, ws_timezone, report_id)
    except Exception as e:
        return f"{e}"

    if len(report_doc["json"]["todo_queue"]) > 0:
        return (
            f"Error: There are still {len(report_doc['json']['todo_queue'])} pending tasks in the report '{report_id}'. "
            f"Please complete them first.")

    report_data = report_doc["json"]
    sections_config, template_html = load_report_config(report_doc["json"]["report_type"])

    template_data = {
        "analysis_date": datetime.now(tz).strftime("%B %d, %Y"),
        "datetime": template_datetime,
        "sections": {},  # All sections by their full name
    }
    
    if "parameters" in report_data:
        template_data.update(report_data["parameters"])

    for section_name, section in report_data["sections"].items():
        placeholder = section["cfg"].get("placeholder")
        if placeholder:
            # Handle null content - convert to empty string for template rendering
            content = section["content"] if section["content"] is not None else ""
            
            template_data["sections"][section_name] = {
                "content": content,
                "placeholder": placeholder,
                "name": section_name
            }

            section_base_id = section.get("section_id", section_name)
            section_config = sections_config.get(section_base_id, {})

            if not section_config.get("iteration"):
                if placeholder not in template_data:
                    template_data[placeholder] = content
                else:
                    existing = template_data[placeholder]
                    if isinstance(existing, str) and content:  # Only append if content is not empty
                        template_data[placeholder] = existing + "\n\n" + content

    report_params = report_data.get("parameters", {})
    all_entities = set()
    for param_name, param_value in report_params.items():
        if isinstance(param_value, list):
            all_entities.update(str(item) for item in param_value)
    
    if all_entities:
        template_data["entities_data"] = {}

        for entity in all_entities:
            template_data["entities_data"][entity] = {}

            for section_name, section_info in template_data["sections"].items():
                entity_from_name = _extract_entity_from_section_name(section_name, report_params)
                if entity_from_name == entity:
                    placeholder = section_info["placeholder"]
                    # Handle null content - use empty string for template rendering
                    content = section_info["content"] if section_info["content"] is not None else ""
                    template_data["entities_data"][entity][placeholder] = content

    providers = set()
    for section_id, config in sections_config.items():
        if iterators := config.get("iterators", {}):
            if provider_list := iterators.get("provider"):
                if isinstance(provider_list, list):
                    providers.update(provider_list)

    if providers:
        template_data["providers"] = sorted(list(providers))

    jinja_template = Template(template_html)
    template_html = jinja_template.render(**template_data)

    report_name = f"report_{report_id}.html"
    await ckit_mongo.store_file(mongo_collection, report_name, template_html.encode('utf-8'))

    try:
        deleted_count = await _cleanup_temporary_files(mongo_collection, report_id)
        cleanup_msg = f"\n🧹 Cleaned up {deleted_count} temporary files" if deleted_count > 0 else ""
    except Exception as e:
        logger.error(f"Cleanup failed but report was generated successfully: {e}")
        cleanup_msg = "\n⚠️ Note: Temporary file cleanup failed, but report was generated successfully"

    return f"""[{current_time} in {tz}]

Successfully generated report!
Report ID: {report_id}
Saved as: {report_name}
Size: {len(template_html.encode('utf-8'))} bytes{cleanup_msg}

Send the report to clients
"""


async def _get_report_doc_by_report_id(mongo_collection: Collection, ws_timezone: str, report_id: str) -> Dict[
    str, Any]:
    report_id = _fix_unicode_corruption(report_id)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    report_doc = await ckit_mongo.retrieve_file(mongo_collection, f"report_{report_id}.json")
    if not report_doc:
        all_files = await ckit_mongo.list_files(mongo_collection)
        report_files = [f for f in all_files if f["path"].startswith("report_") and f["path"].endswith(".json")]
        if report_files:
            available_reports = []
            for f in report_files[:50]:
                rdata = f["json"]
                tasks_remaining = len(rdata.get('todo_queue', []))
                updated_at = rdata.get('updated_at', 'unknown')
                status_info = f"({rdata.get('status', 'unknown')}, {tasks_remaining} tasks left, updated: {updated_at})"
                available_reports.append(f"  - {rdata.get('_id', 'unknown')} {status_info}")
            available = list_available_reports()
            types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
            raise RuntimeError(f"""[{current_time} in {tz}]

Error: Report '{report_id}' not found.

Available reports:
{chr(10).join(available_reports)}

Available report types:
{types_list}

Use one of the report IDs above or create a new report with:
  create_report(name=<report_name>, report_type=<type>, parameters=<dict_parameters>)""")
        else:
            available = list_available_reports()
            types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])

            raise RuntimeError(f"""[{current_time} in {tz}]

Error: Report '{report_id}' not found.

No reports available.

Available report types:
{types_list}""")

    return report_doc


async def handle_create_report_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        name: Optional[str],
        parameters: Optional[str],
        report_type: Optional[str],
) -> str:
    if not name:
        return "Error: 'name' parameter is required"
    if not parameters:
        return "Error: 'parameters' parameter is required"
    if not report_type:
        available = list_available_reports()
        types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
        return f"Error: 'report_type' parameter is required.\n\nAvailable report types:\n{types_list}"

    name = _fix_unicode_corruption(name)
    parameters = _fix_unicode_corruption(parameters)
    report_type = _fix_unicode_corruption(report_type)

    tz = ZoneInfo(ws_timezone)
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    report_id = f"{name}_{timestamp}"

    try:
        report_params = json.loads(parameters)
        if not isinstance(report_params, dict):
            raise ValueError("Parameters must be a JSON object")
    except Exception as e:
        return f"Error: Invalid parameters format: {e}. Use JSON format: '{{\"param1\": \"value1\", \"param2\": [\"item1\", \"item2\"]}}'"

    # Validate that we have at least one iterable parameter or backward compatibility with entities
    has_iterables = any(isinstance(v, list) and len(v) > 0 for v in report_params.values())
    if not has_iterables:
        return "Error: At least one parameter must be an array with values for iteration"

    sections, _ = load_report_config(report_type)

    try:
        todo_queue = _create_todo_queue(report_id, report_params, sections)
    except Exception as e:
        return f"Error creating task queue: {e}"

    await ckit_mongo.store_file(
        mongo_collection,
        f"report_{report_id}.json",
        json.dumps({
            "_id": report_id,
            "report_name": name,
            "report_type": report_type,
            "created_at": datetime.now(tz).isoformat(),
            "updated_at": datetime.now(tz).isoformat(),
            "parameters": report_params,
            "status": "in_progress",
            "sections": {},
            "todo_queue": todo_queue,
        }).encode('utf-8')
    )

    total_tasks = len(todo_queue)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # Format parameters for display
    param_summary = []
    for key, value in report_params.items():
        if isinstance(value, list):
            param_summary.append(f"{key}: {len(value)} items")
        else:
            param_summary.append(f"{key}: {value}")

    return f"""[{current_time} in {tz}]

Created report: {report_id}
Type: {report_type}
Parameters: {', '.join(param_summary)}
Total tasks to complete: {total_tasks}

Use process_report(report_id="{report_id}") to start processing phases."""


async def handle_fill_section_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        report_id: Optional[str] = None,
        section_name: Optional[str] = None,
        content: Optional[str] = None,
) -> str:
    if report_id is None:
        return "Error: No report_id provided"
    if section_name is None:
        return "Error: No section_name provided"
    if content == "null" or content == "":
        content = None

    report_id = _fix_unicode_corruption(report_id)
    section_name = _fix_unicode_corruption(section_name)
    
    # Handle null content case - convert to empty string or None based on context
    if content is not None:
        content = _fix_unicode_corruption(content)
    else:
        # Content is explicitly null - this is valid when there's no data
        content = None

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        report_doc = await _get_report_doc_by_report_id(mongo_collection, ws_timezone, report_id)
    except Exception as e:
        return f"{e}"

    todo_infos = [todo for todo in report_doc["json"]["todo_queue"] if todo["section_name"] == section_name]
    assert len(todo_infos) <= 1, f"Problem in the config, non-unique name in sections:\n{todo_infos}"
    if len(todo_infos) == 0:
        sections = ", ".join([todo["section_name"] for todo in report_doc["json"]["todo_queue"]])
        return f"Error: Section '{section_name}' not found in the report '{report_id}'. Available sections:\n{sections}"

    report_data = report_doc["json"]
    todo = todo_infos[0]

    # Handle validation for non-null content
    if content is not None:
        if json_rules := todo["section_config"].get("json_validation", {}):
            is_valid, errors = validate_json_content(content, json_rules)
            try:
                content = json.loads(content)
            except Exception as e:
                return f"Error decoding JSON: {e}. Please fix the JSON and try again."
            if not is_valid:
                return f"Error: JSON validation failed:\n" + "\n".join(errors) + "\n\nPlease fix the JSON and try again."
        elif validation_rules := todo["section_config"].get("html_validation", {}):
            content = sanitize_html(content)
            is_valid, errors = validate_html_content(content, validation_rules)
            if not is_valid:
                return f"Error: HTML validation failed:\n" + "\n".join(errors) + "\n\nPlease fix the HTML and try again."

    json_data_file = None
    if todo.get("is_meta_section", False) and content is not None:
        try:
            json_filename = f"meta_data_{report_id}_{section_name}.json"
            json_content = json.dumps(content, indent=2).encode('utf-8')
            await ckit_mongo.store_file(mongo_collection, json_filename, json_content)
            json_data_file = json_filename
            logger.info(f"Stored meta section data to {json_filename} ({len(json_content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to store meta section JSON data: {e}")
    section_data = {
        "content": content,
        "name": section_name,
        "cfg": todo["section_config"],
        "section_id": todo.get("section_id", section_name),
        "task": todo["task"],
        "depends_on": todo.get("depends_on", []),
        "is_meta_section": todo.get("is_meta_section", False),
        "timestamp": datetime.now(tz).isoformat(),
    }
    if json_data_file:
        section_data["json_data_file"] = json_data_file
    report_data["sections"][section_name] = section_data
    report_data["updated_at"] = datetime.now(tz).isoformat()
    report_data["todo_queue"] = [task for task in report_data["todo_queue"] if task["section_name"] != section_name]
    if len(report_data["todo_queue"]) == 0:
        report_data["status"] = "completed"

    await ckit_mongo.store_file(
        mongo_collection,
        f"report_{report_id}.json",
        json.dumps(report_data).encode('utf-8')
    )

    # Create appropriate success message based on content
    content_msg = "with null content (no data)" if content is None else "with content"
    
    result = [
        f"[{current_time} in {tz}]\n",
        f"Successfully filled section '{section_name}' {content_msg}",
        f"Remaining tasks: {len(report_data['todo_queue'])}"
    ]
    if len(report_data['todo_queue']) == 0:
        result.append(f"\n✅ Report complete!")
        export_result = await _export_report_tool(ws_timezone, mongo_collection, report_id=report_id)
        result.append(export_result)
    else:
        result.append(
            f"Remaining tasks: {len(report_data['todo_queue'])}. "
            f"Use process_report(report_id='{report_id}') to process the next phase."
        )
    return "\n".join(result)


async def handle_report_status_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        report_id: Optional[str] = None,
) -> str:
    if report_id:
        report_id = _fix_unicode_corruption(report_id)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    async def _generate_reports_list(error_msg: str = "", max_reports=50) -> str:
        all_files = await ckit_mongo.list_files(mongo_collection)
        report_files = [f for f in all_files if f["path"].startswith("report_") and f["path"].endswith(".json")]
        html_reports = {f["path"].replace(".html", "").replace("report_", ""): f
                        for f in all_files if f["path"].startswith("report_") and f["path"].endswith(".html")}

        if not report_files:
            available = list_available_reports()
            types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
            return f"""[{current_time} in {tz}]

No reports found in the database.

Create a new report with:
  create_report(name=<report_name>, report_type=<type>, parameters={{}})

Available report types:
{types_list}"""

        result = [
            f"[{current_time} in {tz}]\n",
            f"Found {len(report_files)} reports:\n"
        ]
        for f in report_files[:max_reports]:
            rdata = f["json"]
            report_name = rdata.get('_id', 'unknown')
            report_type = rdata.get('report_type', 'unknown')
            status = rdata.get('status', 'unknown')
            created = rdata.get('created_at', 'unknown')

            filled_count = len(rdata.get("sections", {}))
            todo_count = len(rdata.get("todo_queue", []))
            total_tasks = filled_count + todo_count
            completion_pct = (filled_count / total_tasks * 100) if total_tasks > 0 else 0

            status_emoji = "✅" if status == "completed" else "🔄" if status == "in_progress" else "❓"
            html_exists = report_name in html_reports
            html_indicator = " 📄" if html_exists else ""

            result.append(f"📊 {report_name}{html_indicator}")
            result.append(f"   Type: {report_type}")
            result.append(f"   Status: {status_emoji} {status}")
            result.append(f"   Progress: {filled_count}/{total_tasks} tasks ({completion_pct:.1f}%)")

            params = rdata.get('parameters', {})
            if params:
                param_summary = []
                for key, value in params.items():
                    if isinstance(value, list):
                        param_summary.append(f"{key}({len(value)})")
                    else:
                        param_summary.append(f"{key}:{value}")
                result.append(f"   Parameters: {', '.join(param_summary)}")
            else:
                result.append(f"   Legacy format")
            result.append(f"   Created: {created}")
            if html_exists:
                result.append(f"   📄 HTML: report_{report_name}.html")
            result.append("")

        if len(report_files) > max_reports:
            result.append(f"... and {len(report_files) - max_reports} more reports")

        if error_msg:
            result.extend([
                "💡 Usage:",
                f"  • Use get_report_status(report_id=<report_id>) with one of the IDs above",
                f"  • Or create a new report with: create_report(name=<report_name>, entities=<entities_list>, type=\"<report_type>\")"
            ])
        else:
            result.append(
                "Use get_report_status(report_id=<report_id>) to get detailed status for a specific report."
            )

        result.append("")
        available = list_available_reports()
        types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
        result.append("Available report types:")
        result.append(types_list)

        return "\n".join(result)

    if not report_id:
        return await _generate_reports_list()

    report_doc = await ckit_mongo.retrieve_file(mongo_collection, f"report_{report_id}.json")

    if not report_doc:
        return await _generate_reports_list(f"❌ Error: Report '{report_id}' not found.\n\n📋 ")

    report_data = report_doc["json"]

    filled_count = len(report_data["sections"])
    total_tasks = filled_count + len(report_data["todo_queue"])
    completion_pct = (filled_count / total_tasks * 100) if total_tasks > 0 else 0

    html_report_name = f"report_{report_id}.html"
    html_exists = await ckit_mongo.retrieve_file(mongo_collection, html_report_name)
    if report_data['status'] == "completed" and not html_exists:
        await _export_report_tool(ws_timezone, mongo_collection, report_id=report_id)
        html_exists = await ckit_mongo.retrieve_file(mongo_collection, html_report_name)

    status_emoji = "✅" if report_data['status'] == "completed" else "🔄"
    result = [
        f"[{current_time} in {tz}]\n",
        f"📊 Report Details: {report_id}",
        f"Type: {report_data.get('report_type', 'unknown')}",
        f"Status: {status_emoji} {report_data['status']}",
        f"Created: {report_data['created_at']}",
        f"Updated: {report_data['updated_at']}",
        f"Parameters: {_format_parameters_summary(report_data.get('parameters', {}))}",
        f"Progress: {filled_count}/{total_tasks} tasks ({completion_pct:.1f}%)\n"
    ]
    if html_exists:
        result.append(f"📄 **HTML Report Available**: {html_report_name}")
        result.append(f"   You can access the report using the path: {html_report_name}, i.e. send it to clients")
        result.append("")

    if report_data["sections"]:
        result.append("✅ Completed sections:")
        for section_name in list(report_data["sections"].keys())[:20]:
            result.append(f"  ✓ {section_name}")
        if len(report_data["sections"]) > 20:
            result.append(f"  ... and {len(report_data['sections']) - 20} more")
        result.append("")

    if report_data["todo_queue"]:
        result.append("⏳ Pending tasks:")
        for i, task in enumerate(report_data["todo_queue"][:10], 1):
            result.append(f"  {i}. {task['section_name']}")
        if len(report_data["todo_queue"]) > 10:
            result.append(f"  ... and {len(report_data['todo_queue']) - 10} more tasks")
        result.append("")
        result.append(f"🚀 Continue with: process_report(report_id='{report_id}')")
    else:
        result.append("🎉 All tasks completed!")
        if not html_exists:
            result.append("⚠️ Note: HTML export may have failed. Check logs for details.")

    # Add available report types
    result.append("")
    available = list_available_reports()
    types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
    result.append("Available report types:")
    result.append(types_list)

    return "\n".join(result)


async def handle_load_metadata_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        report_id: str,
        safety_valve: Optional[int] = 200
) -> str:
    report_id = _fix_unicode_corruption(report_id)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        report_doc = await _get_report_doc_by_report_id(mongo_collection, ws_timezone, report_id)
    except Exception as e:
        return f"{e}"

    report_data = report_doc["json"]
    max_bytes = safety_valve * 1024

    result = [
        f"[{current_time} in {tz}]",
        f"Report Metadata: {report_id}",
        f"Type: {report_data.get('report_type', 'unknown')}",
        f"Created: {report_data.get('created_at', 'unknown')}",
        f"Updated: {report_data.get('updated_at', 'unknown')}",
        f"Status: {report_data.get('status', 'unknown')}",
        f"Parameters: {_format_parameters_summary(report_data.get('parameters', {}))}",
        "",
        "=== SECTIONS ===",
    ]

    for section_name, section_data in report_data.get("sections", {}).items():
        result.append(f"\n📌 **{section_name}**")
        result.append("─" * 50)
        if section_data.get("scraped_data_files"):
            result.append(f"📁 Scraped data: {section_data['scraped_data_files']}")
        if section_data.get("json_data_file"):
            result.append(f"📄 JSON data file: {section_data['json_data_file']}")
        if section_data.get("timestamp"):
            result.append(f"🕒 Completed: {section_data['timestamp']}")
        if section_data.get("is_meta_section", False):
            result.append("📊 Meta Section Content:")
            try:
                content = section_data.get("content")
                if content is None:
                    result.append("[No data - content is null]")
                else:
                    result.append(json.dumps(content, indent=2))
            except Exception as e:
                result.append(f"⚠️ Error parsing section: {e}")
        else:
            result.append("📝 Report Section Content (first 500 chars):")
            content = section_data.get("content")
            if content is None:
                content_str = "[No data - content is null]"
            else:
                content_str = str(content)
            result.append(content_str[:500] + ("..." if len(content_str) > 500 else ""))

    output = "\n".join(result)
    if len(output.encode('utf-8')) > max_bytes:
        output = output[:max_bytes]
        last_newline = output.rfind('\n')
        if last_newline > 0:
            output = output[:last_newline]
        output += "\n... [truncated - increase safety_valve to see more]"

    return output


def _format_dependency_content(
        dependency_sections: List[str],
        completed_sections: Dict[str, Any],
) -> str:
    if not dependency_sections:
        return ""

    dependency_text = "\n\n=== DEPENDENCY DATA ===\n"

    json_data_files = []
    for dep_name in dependency_sections:
        if dep_name in completed_sections:
            section_data = completed_sections[dep_name]
            json_data_file = section_data.get("json_data_file", None)
            content = section_data.get("content")
            dependency_text += f"\n--- {dep_name} ---\n"
            if json_data_file:
                json_data_files.append(json_data_file)
                dependency_text += f"📄 JSON Data File: {json_data_file}\n"
            
            # Handle null content in dependencies
            if content is None:
                dependency_text += "[No data available for this section]\n"
            else:
                dependency_text += f"{content}\n"

    dependency_text += f"""\n
Use python to read and analyze json files:
```
import json
filenames = [{", ".join(json_data_files)}]
with open(filenames[0], 'r') as f:
    data = json.load(f)
    print(data)
```
\n
"""
    return dependency_text


async def _cleanup_temporary_files(mongo_collection: Collection, report_id: str) -> int:
    try:
        all_files = await ckit_mongo.list_files(mongo_collection)
        temp_files = [f for f in all_files if not f["path"].startswith("report_")]
        deleted_count = 0
        for file_info in temp_files:
            file_path = file_info["path"]
            try:
                success = await ckit_mongo.delete_file(mongo_collection, file_path)
                if success:
                    deleted_count += 1
                    logger.info(f"Cleaned up temporary file: {file_path}")
                else:
                    logger.warning(f"Failed to delete temporary file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary file {file_path}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleanup completed: removed {deleted_count} temporary files for report {report_id}")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during temporary files cleanup for report {report_id}: {e}")
        return 0


async def handle_process_report_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        fclient,
        persona_id: str,
        toolcall,
        *,
        report_id: Optional[str] = None,
) -> str:
    from collections import defaultdict

    if report_id is None:
        return "Error: No report_id provided"

    report_id = _fix_unicode_corruption(report_id)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        report_doc = await _get_report_doc_by_report_id(mongo_collection, ws_timezone, report_id)
    except Exception as e:
        return f"{e}"

    report_data = report_doc["json"]
    todo = report_data.get("todo_queue", [])

    if not todo:
        return f"[{current_time} in {tz}]\n\nReport {report_id} is already complete."

    sections_config, _ = load_report_config(report_data["report_type"])
    phases = defaultdict(list)
    for task in todo:
        section_base = task["section_id"]
        phase_num = sections_config.get(section_base, {}).get("phase", 1)
        phases[phase_num].append(task)

    next_phase = min(phases.keys())
    tasks_in_phase = phases[next_phase]
    completed_sections = report_data.get("sections", {})

    first_questions = []
    first_calls = []
    titles = []

    for task in tasks_in_phase:
        task_text = task["task"]
        if task.get("depends_on"):
            dependency_placeholder = f"\nDependencies: {', '.join(task['depends_on'])} (content will be provided when processing)"
            dependency_content = _format_dependency_content(task["depends_on"], completed_sections)
            task_text = task_text.replace(dependency_placeholder, dependency_content)
        first_questions.append(task_text)
        first_calls.append("null")
        titles.append(f"Report {report_id}: {task['section_name']}")

    await ckit_ask_model.bot_subchat_create_multiple(
        fclient,
        "adspy_process_report",
        persona_id,
        first_questions,
        first_calls,
        titles,
        toolcall.fcall_id,
        max_tokens=16000
    )

    return "WAIT_SUBCHATS"
