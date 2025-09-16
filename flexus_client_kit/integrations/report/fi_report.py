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
    description="Initialize a new report",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Base name for the report"},
            "entities": {"type": "string", "description": "JSON list of entity names"},
            "report_type": {"type": "string", "description": "Type of report (e.g., 'adspy')"},
        },
        "required": ["name", "entities", "report_type"],
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
            "content": {"type": "string", "description": "Data that will be stored in the section"},
        },
        "required": ["report_id", "section_name", "content"],
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
            "safety_valve": {"type": "integer", "description": "Max output size in KB (default 200KB)"},
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


def _extract_entity_from_section_name(section_name: str, entities: List[str]) -> Optional[str]:
    """Extract entity name from a section name like 'company_overview_box_GANNI'."""
    for entity in entities:
        if section_name.endswith(f"_{entity}"):
            return entity
    for entity in entities:
        entity_normalized = entity.replace(" ", "_").replace("-", "_")
        if entity_normalized in section_name:
            return entity
    return None


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


def _build_iteration_combinations(entities: List[str], sections: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
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
                    values_lists.append(entities)
                elif isinstance(source, list):
                    values_lists.append(source)
                else:
                    values_lists.append([source])
            # Generate all combinations
            combos = []
            for combo_values in itertools.product(*values_lists):
                combo_dict = dict(zip(keys, combo_values))
                combos.append(combo_dict)

            combos_map[section_id] = combos
        else:
            # No iteration - single instance
            combos_map[section_id] = [{}]
    return combos_map


def _create_todo_queue(report_id: str, entities: List[str], sections: Dict[str, Any]) -> List[Dict[str, Any]]:
    combos_map = _build_iteration_combinations(entities, sections)
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

            # Expand dependencies
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
            for key, value in combo.items():
                formatted_desc = formatted_desc.replace(f"{{{key}}}", str(value))
                formatted_example = formatted_example.replace(f"{{{key}}}", str(value))
            task_text = f"""Task for report: {report_id}
Section: {section_name}
Description: {formatted_desc}"""
            if depends_on:
                task_text += "\nDependencies will be loaded from completed sections."
            if formatted_example:
                task_text += f"\n\n=== Expected Format ===\n{formatted_example}"
            extra_instructions = config.get("extra_instructions", [])
            task_text += f"\n\n=== Instructions ===\n"
            if extra_instructions:
                for idx, instruction in enumerate(extra_instructions, 1):
                    formatted_instruction = instruction
                    for key, value in combo.items():
                        formatted_instruction = formatted_instruction.replace(f"{{{key}}}", str(value))
                    task_text += f"{formatted_instruction}\n"

            task_text += f"\nCall: fill_report_section(report_id='{report_id}', section_name='{section_name}', content=<your_content>)"
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
        "entities": report_data.get("entities", []),
        "datetime": template_datetime,
        "sections": {},  # All sections by their full name
    }
    
    for section_name, section in report_data["sections"].items():
        placeholder = section["cfg"].get("placeholder")
        if placeholder:
            template_data["sections"][section_name] = {
                "content": section["content"],
                "placeholder": placeholder,
                "name": section_name
            }
            
            section_base_id = section.get("section_id", section_name)
            section_config = sections_config.get(section_base_id, {})
            
            if not section_config.get("iteration"):
                if placeholder not in template_data:
                    template_data[placeholder] = section["content"]
                else:
                    existing = template_data[placeholder]
                    if isinstance(existing, str):
                        template_data[placeholder] = existing + "\n\n" + section["content"]
    
    if report_data.get("entities"):
        template_data["entities_data"] = {}
        
        for entity in report_data["entities"]:
            template_data["entities_data"][entity] = {}
            
            for section_name, section_info in template_data["sections"].items():
                entity_from_name = _extract_entity_from_section_name(section_name, report_data["entities"])
                if entity_from_name == entity:
                    placeholder = section_info["placeholder"]
                    template_data["entities_data"][entity][placeholder] = section_info["content"]
    
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

    return f"""[{current_time} in {tz}]

Successfully generated report!
Report ID: {report_id}
Saved as: {report_name}
Size: {len(template_html.encode('utf-8'))} bytes

Download and send the report:
mongo_store(op="download", args={{"path": "{report_name}"}})
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
  create_report(name=<report_name>, entities='["entity1", "entity2"]', report_type=<type>)""")
        else:
            available = list_available_reports()
            types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])

            raise RuntimeError(f"""[{current_time} in {tz}]

Error: Report '{report_id}' not found.

No reports available. Create a new report with:
  create_report(name=<report_name>, entities='["entity1", "entity2"]', report_type=<type>)
  
Available report types:
{types_list}""")

    return report_doc


async def handle_create_report_tool(
        ws_timezone: str,
        mongo_collection: Collection,
        *,
        name: Optional[str],
        entities: Optional[str],
        report_type: Optional[str],
) -> str:
    if not name:
        return "Error: 'name' parameter is required"
    if not entities:
        return "Error: 'entities' parameter is required"
    if not report_type:
        available = list_available_reports()
        types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
        return f"Error: 'report_type' parameter is required.\n\nAvailable report types:\n{types_list}"

    name = _fix_unicode_corruption(name)
    entities = _fix_unicode_corruption(entities)
    report_type = _fix_unicode_corruption(report_type)

    tz = ZoneInfo(ws_timezone)
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    report_id = f"{name}_{timestamp}"

    try:
        entities_list = json.loads(entities)
        if not isinstance(entities_list, list):
            raise ValueError("Entities must be a list")
    except Exception as e:
        return f"Error: Invalid entities format: {e}. Use JSON format: '[\"entity1\", \"entity2\"]'"

    if len(entities_list) == 0:
        return "Error: No valid entities provided"

    sections, _ = load_report_config(report_type)

    try:
        todo_queue = _create_todo_queue(report_id, entities_list, sections)
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
            "entities": entities_list,
            "status": "in_progress",
            "sections": {},
            "todo_queue": todo_queue,
        }).encode('utf-8')
    )

    total_tasks = len(todo_queue)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
    
    available = list_available_reports()
    types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])

    return f"""[{current_time} in {tz}]

Created report: {report_id}
Type: {report_type}
Entities: {', '.join(entities_list)}
Total tasks to complete: {total_tasks}

Use process_report(report_id="{report_id}") to start processing phases.

Available report types:
{types_list}"""



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
    if content is None:
        return "Error: No content provided"

    report_id = _fix_unicode_corruption(report_id)
    section_name = _fix_unicode_corruption(section_name)
    content = _fix_unicode_corruption(content)

    tz = ZoneInfo(ws_timezone)
    current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        report_doc = await _get_report_doc_by_report_id(mongo_collection, ws_timezone, report_id)
    except Exception as e:
        return f"{e}"

    todo_infos = [todo for todo in report_doc["json"]["todo_queue"] if todo["section_name"] == section_name]
    assert len(todo_infos) <= 1, f"Problem we the config, non-unique name in sections:\n{todo_infos}"
    if len(todo_infos) == 0:
        sections = ", ".join([todo["section_name"] for todo in report_doc["json"]["todo_queue"]])
        return f"Error: Section '{section_name}' not found in the report '{report_id}'. Available sections:\n{sections}"

    report_data = report_doc["json"]
    todo = todo_infos[0]

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

    result = [
        f"[{current_time} in {tz}]\n",
        f"Successfully filled section '{section_name}'",
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

        if not report_files:
            available = list_available_reports()
            types_list = "\n".join([f"  - {t[0]}: {t[1]}" for t in available])
            return f"""[{current_time} in {tz}]

No reports found in the database.

Create a new report with:
  create_report(name=<report_name>, entities='["entity1", "entity2"]', report_type=<type>)

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
            entities = rdata.get('entities', [])

            filled_count = len(rdata.get("sections", {}))
            todo_count = len(rdata.get("todo_queue", []))
            total_tasks = filled_count + todo_count
            completion_pct = (filled_count / total_tasks * 100) if total_tasks > 0 else 0

            status_emoji = "✅" if status == "completed" else "🔄" if status == "in_progress" else "❓"

            result.append(f"📊 {report_name}")
            result.append(f"   Type: {report_type}")
            result.append(f"   Status: {status_emoji} {status}")
            result.append(f"   Progress: {filled_count}/{total_tasks} tasks ({completion_pct:.1f}%)")
            result.append(f"   Entities: {', '.join(entities) if entities else 'None'}")
            result.append(f"   Created: {created}")
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
        
        # Add available report types
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

    status_emoji = "✅" if report_data['status'] == "completed" else "🔄"
    result = [
        f"[{current_time} in {tz}]\n",
        f"📊 Report Details: {report_id}",
        f"Type: {report_data.get('report_type', 'unknown')}",
        f"Status: {status_emoji} {report_data['status']}",
        f"Created: {report_data['created_at']}",
        f"Updated: {report_data['updated_at']}",
        f"Entities: {', '.join(report_data.get('entities', []))}",
        f"Progress: {filled_count}/{total_tasks} tasks ({completion_pct:.1f}%)\n"
    ]

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
        f"Entities: {', '.join(report_data.get('entities', []))}",
        "",
        "=== SECTIONS ===",
    ]

    for section_name, section_data in report_data.get("sections", {}).items():
        result.append(f"\n📌 **{section_name}**")
        result.append("─" * 50)
        if section_data.get("scraped_data_files"):
            result.append(f"📁 Scraped data: {section_data['scraped_data_files']}")
        if section_data.get("timestamp"):
            result.append(f"🕒 Completed: {section_data['timestamp']}")
        if section_data.get("is_meta_section", False):
            result.append("📊 Meta Section Content:")
            try:
                content = section_data.get("content", "{}")
                result.append(json.dumps(content, indent=2))
            except Exception as e:
                result.append(f"⚠️ Error parsing section: {e}")
        else:
            result.append("📝 Report Section Content (first 500 chars):")
            content_str = str(section_data.get("content", "No content"))
            result.append(content_str[:500] + ("..." if len(content_str) > 500 else ""))

    output = "\n".join(result)
    if len(output.encode('utf-8')) > max_bytes:
        output = output[:max_bytes]
        last_newline = output.rfind('\n')
        if last_newline > 0:
            output = output[:last_newline]
        output += "\n... [truncated - increase safety_valve to see more]"

    return output


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
    
    first_questions = []
    first_calls = []
    titles = []
    
    for task in tasks_in_phase:
        first_questions.append(task["task"])
        first_calls.append("null")
        titles.append(f"Report {report_id}: {task['section_name']}")

    await ckit_ask_model.bot_subchat_create_multiple(
        fclient,
        "adspy_process_report",
        persona_id,
        first_questions,
        first_calls,
        titles,
        toolcall.fcall_ft_id,
        toolcall.fcall_ftm_alt,
        toolcall.fcall_called_ftm_num,
        toolcall.fcall_call_n,
    )

    return "WAIT_SUBCHATS"
