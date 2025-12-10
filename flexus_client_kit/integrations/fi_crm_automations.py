import json
import logging
from typing import Dict, Any, Optional, List
import re

import gql

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_erp, ckit_kanban, ckit_bot_exec

logger = logging.getLogger("fi_crm_automations")


CRM_AUTOMATIONS_SETUP_SCHEMA = [
    {
        "bs_name": "crm_automations",
        "bs_type": "string_multiline",
        "bs_default": "{}",
        "bs_group": "CRM",
        "bs_order": 100,
        "bs_importance": 1,
        "bs_description": "CRM automation rules (JSON format). Use crm_automation tool to manage.",
    }
]


AUTOMATIONS_PROMPT = """
## CRM Automations

You can configure CRM automations to react to ERP table changes and perform actions automatically.

Structure:
- **Triggers**: What event fires the automation (e.g., new contact inserted or updated)
- **Actions**: What to do when triggered (e.g., post a task into inbox, update contact tags)

Common use cases:
- Welcome emails when new contacts arrive
- Follow-up tasks after initial contact
- Automatic task creation based on deal stage changes

Working with Automations:
- Call crm_automation(op="help") and check ERP schema first with erp_table_meta
- List existing automations
- Do not react to just insert of erp tables, react also to update

Template Variables:

Use `{{trigger.new_record.field_name}}` or `{{trigger.old_record.field_name}}`:
- `{{trigger.new_record.contact_id}}`
- `{{trigger.new_record.contact_first_name}}`
- `{{trigger.old_record.contact_email}}` (for updates/deletes)
- `{{now()}}` - current Unix timestamp

Python expressions (templates resolved first, then evaluated):
- `{{trigger.new_record.contact_tags}} + ['new_tag']` - append to array
- `{{now()}} + 86400` - timestamp one day from now

Important Notes:
- Actions execute in sequence
- Failed actions are logged but don't stop subsequent actions
- Automations can be enabled/disabled
- NEVER use my_setup() to set up crm_automations - it will kill the configured automations, only use this tool to manage them
""".strip()


CRM_AUTOMATION_TOOL = ckit_cloudtool.CloudTool(
    name="crm_automation",
    description="Manage CRM automations. Start with op='help' to see complete documentation. IMPORTANT: Never use flexus_my_setup to modify 'crm_automations' - only use this tool!",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["help", "list", "get", "create", "update", "delete"],
                "description": "Operation to perform",
                "order": 1
            },
            "args": {
                "type": "object",
                "description": "Arguments for the operation",
                "order": 2,
                "properties": {
                    "automation_name": {"type": "string", "description": "Name of the automation"},
                    "automation_config": {"type": "object", "description": "Automation configuration"},
                }
            }
        },
        "required": ["op"],
    },
)


HELP_TEXT = """
CRM Automations Help
====================

## Structure

Each automation has:
- enabled: bool
- triggers: list of trigger configs, erp_table trigger fires when ERP table records change
- actions: list of action configs, like post task into inbox, create, update, or delete an erp record.

## Example

```json
{
  "enabled": true,
  "triggers": [
    {
      "type": "erp_table",
      "table": "crm_contact",
      "operations": ["insert", "update"],
      "filters": [
        "contact_tags:not_contains:welcome_email_sent"
      ]
    }
  ],
  "actions": [
    {
      "type": "post_task_into_bot_inbox",
      "title": "Send welcome email to {{trigger.new_record.contact_first_name}}",
      "details": {
        "contact_id": "{{trigger.new_record.contact_id}}"
      },
      "provenance": "CRM automation: welcome_email"
    },
    {
      "type": "update_erp_record",
      "table": "crm_contact",
      "record_id": "{{trigger.new_record.contact_id}}",
      "fields": {
        "contact_tags": "{{trigger.new_record.contact_tags}} + ['welcome_email_sent']"
      }
    }
  ]
}
```

## Template Variables

Use {{path.to.value}} to reference trigger data:
- {{trigger.new_record.contact_id}}
- {{trigger.new_record.contact_first_name}}
- {{trigger.old_record.contact_email}} (for updates/deletes)
- {{now()}} - current Unix timestamp

Python expressions (templates are resolved first, then expression is evaluated):
- {{trigger.new_record.contact_tags}} + ['new_tag'] - append to array
- {{now()}} + 86400 - timestamp one day from now
- {{now()}} - 3600 - timestamp one hour ago

Note: Leading '=' is stripped from field values automatically.

## Trigger Filter Syntax

Format: "field:op:value"

Operators for arrays: contains, not_contains
Operators for other types: =, !=, >, <, >=, <=

Examples:
- "contact_tags:not_contains:welcome_email_sent" - check array doesn't contain value
- "contact_tags:contains:vip" - check array contains value
- "contact_email:!=:" - check field is not empty
"""


class IntegrationCrmAutomations:
    def __init__(
        self,
        client: ckit_client.FlexusClient,
        rcx: ckit_bot_exec.RobotContext,
        get_setup_func: callable,
    ):
        self.client = client
        self.rcx = rcx
        self.get_setup = get_setup_func
        self._pending_save = None
        self._setup_automation_handlers()

    def _load_automations(self) -> Dict[str, Any]:
        setup = self.get_setup()
        crm_automations_str = setup.get("crm_automations", "{}")
        try:
            return json.loads(crm_automations_str) if isinstance(crm_automations_str, str) else crm_automations_str
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse crm_automations from setup: {e}")
            return {}

    async def _save_automations(self, automations: Dict[str, Any]) -> None:
        setup = self.get_setup()
        setup["crm_automations"] = json.dumps(automations, indent=2)

        http = await self.client.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""mutation PersonaUpdateSetup($persona_id: String!, $persona_setup: String!) {
                    persona_patch_setup(
                        persona_id: $persona_id,
                        persona_setup: $persona_setup
                    )
                }"""),
                variable_values={
                    "persona_id": self.rcx.persona.persona_id,
                    "persona_setup": json.dumps(setup),
                },
            )
        logger.info("Updated persona setup in backend")

    async def handle_crm_automation(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_args: Dict[str, Any]) -> str:
        op = model_args.get("op", "").lower()
        args = model_args.get("args", {})

        if op == "help":
            return HELP_TEXT

        elif op == "list":
            return await self._op_list(args)

        elif op == "get":
            return await self._op_get(args)

        elif op == "create":
            return await self._op_create(args)

        elif op == "update":
            return await self._op_update(args)

        elif op == "delete":
            return await self._op_delete(args)

        else:
            return f"❌ Unknown operation '{op}'. Use: help, list, get, create, update, delete"

    async def _op_list(self, args: Dict[str, Any]) -> str:
        automations = self._load_automations()

        if not automations:
            return "No CRM automations configured."

        result = f"CRM Automations ({len(automations)} total):\n\n"
        for name, config in automations.items():
            enabled = config.get("enabled", False)
            status = "✅ enabled" if enabled else "❌ disabled"
            triggers = config.get("triggers", [])
            actions = config.get("actions", [])
            result += f"• {name}: {status}\n"
            result += f"  Triggers: {len(triggers)}, Actions: {len(actions)}\n"

        return result

    async def _op_get(self, args: Dict[str, Any]) -> str:
        automation_name = args.get("automation_name", "").strip()

        if not automation_name:
            return "❌ Error: automation_name is required"

        automations = self._load_automations()

        if automation_name not in automations:
            return f"❌ Error: Automation '{automation_name}' not found"

        config = automations[automation_name]
        return f"Automation: {automation_name}\n\n{json.dumps(config, indent=2)}"

    async def _op_create(self, args: Dict[str, Any]) -> str:
        automation_name = args.get("automation_name", "").strip()
        automation_config = args.get("automation_config", {})

        if not automation_name:
            return "❌ Error: automation_name is required"

        if not automation_config:
            return "❌ Error: automation_config is required"

        if not isinstance(automation_config, dict):
            return "❌ Error: automation_config must be a dict"

        automations = self._load_automations()

        if automation_name in automations:
            return f"❌ Error: Automation '{automation_name}' already exists. Use op='update' to modify it."

        if len(automations) >= 30:
            return "❌ Error: Maximum 30 automations per bot. Delete unused automations first."

        # Set defaults
        if "enabled" not in automation_config:
            automation_config["enabled"] = True
        if "actions" not in automation_config:
            automation_config["actions"] = []

        # Validate using the same structure that execution expects
        validation_error = validate_automation_config(automation_config)
        if validation_error:
            return validation_error

        automations[automation_name] = automation_config
        await self._save_automations(automations)

        return f"✅ Created automation '{automation_name}'"

    async def _op_update(self, args: Dict[str, Any]) -> str:
        automation_name = args.get("automation_name", "").strip()
        automation_config = args.get("automation_config", {})

        if not automation_name:
            return "❌ Error: automation_name is required"

        if not automation_config:
            return "❌ Error: automation_config is required"

        if not isinstance(automation_config, dict):
            return "❌ Error: automation_config must be a dict"

        automations = self._load_automations()

        if automation_name not in automations:
            return f"❌ Error: Automation '{automation_name}' not found. Use op='create' to create it."

        # Validate using the same structure that execution expects
        validation_error = validate_automation_config(automation_config)
        if validation_error:
            return validation_error

        automations[automation_name] = automation_config
        await self._save_automations(automations)

        return f"✅ Updated automation '{automation_name}'"

    async def _op_delete(self, args: Dict[str, Any]) -> str:
        automation_name = args.get("automation_name", "").strip()

        if not automation_name:
            return "❌ Error: automation_name is required"

        automations = self._load_automations()

        if automation_name not in automations:
            return f"❌ Error: Automation '{automation_name}' not found"

        del automations[automation_name]
        await self._save_automations(automations)

        return f"✅ Deleted automation '{automation_name}'"

    def _setup_automation_handlers(self):
        automations = self._load_automations()
        tables = get_erp_tables_from_automations(automations)

        def make_handler(table_name):
            async def handler(operation: str, new_record: Any, old_record: Any):
                automations_dict = self._load_automations()
                if automations_dict:
                    await execute_automations_for_erp_event(
                        self.rcx,
                        table_name,
                        operation,
                        new_record,
                        old_record,
                        automations_dict,
                    )
            return handler

        for t in tables:
            self.rcx._handler_per_erp_table_change[t] = make_handler(t)

        if set(self.rcx._handler_per_erp_table_change.keys()) != set(self.rcx.wanted_erp_tables):
            self.rcx.wanted_erp_tables = sorted(self.rcx._handler_per_erp_table_change.keys())
            self.rcx.erp_tables_dirty = True


def get_erp_tables_from_automations(automations_dict: Dict[str, Any]) -> List[str]:
    tables = set()
    for auto_config in automations_dict.values():
        if not auto_config.get("enabled", True):
            continue
        for trigger in auto_config.get("triggers", []):
            if trigger.get("type") == "erp_table":
                t = trigger.get("table")
                if t:
                    tables.add(t)
    return sorted(tables)


async def execute_automations_for_erp_event(
    rcx: ckit_bot_exec.RobotContext,
    table_name: str,
    operation: str,
    new_record: Optional[Any],
    old_record: Optional[Any],
    automations_dict: Dict[str, Any],
) -> None:
    for auto_name, auto_config in automations_dict.items():
        if not auto_config.get("enabled", True):
            continue

        triggers = auto_config.get("triggers", [])

        for trigger in triggers:
            if trigger.get("type") != "erp_table":
                continue

            if trigger.get("table") != table_name:
                continue

            trigger_ops = [op.upper() for op in trigger.get("operations", [])]
            if operation.upper() not in trigger_ops:
                continue

            trigger_context = {
                "trigger": {
                    "type": "erp_table",
                    "table": table_name,
                    "operation": operation,
                    "new_record": ckit_erp.dataclass_or_dict_to_dict(new_record) if new_record else None,
                    "old_record": ckit_erp.dataclass_or_dict_to_dict(old_record) if old_record else None,
                }
            }

            # Check trigger filters if present
            trigger_filters = trigger.get("filters", [])
            if trigger_filters:
                record_to_check = old_record if operation.upper() == "DELETE" else new_record
                if not record_to_check:
                    logger.info(f"Automation '{auto_name}' skipped: no record to check filters against")
                    continue

                record_dict = ckit_erp.dataclass_or_dict_to_dict(record_to_check)
                logger.debug(f"Checking filters for '{auto_name}': filters={trigger_filters}, record_dict keys={list(record_dict.keys())}")
                if not ckit_erp.check_record_matches_filters(record_dict, trigger_filters):
                    logger.info(f"Automation '{auto_name}' filtered out for {table_name}.{operation}")
                    continue

            actions = auto_config.get("actions", [])
            await _execute_actions(rcx, actions, trigger_context)
            logger.info(f"Automation '{auto_name}' executed for {table_name}.{operation}")


async def _execute_actions(
    rcx: ckit_bot_exec.RobotContext,
    actions: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> None:
    for action in actions:
        action_type = action.get("type")

        try:
            if action_type == "post_task_into_bot_inbox":
                title = _resolve_template(action.get("title", ""), context)
                details = action.get("details", {})
                provenance = _resolve_template(action.get("provenance", "CRM automation"), context)

                resolved_details = {}
                for k, v in details.items():
                    if isinstance(v, str):
                        resolved_details[k] = _resolve_template(v, context)
                    else:
                        resolved_details[k] = v

                await ckit_kanban.bot_kanban_post_into_inbox(
                    rcx.fclient,
                    rcx.persona.persona_id,
                    title,
                    json.dumps(resolved_details),
                    provenance,
                )
                logger.info(f"Posted task into inbox: {title}")

            elif action_type == "create_erp_record":
                table = action.get("table")
                fields = action.get("fields", {})

                resolved_fields = {}
                for k, v in fields.items():
                    if isinstance(v, str):
                        resolved_fields[k] = _resolve_field_value(v, context, k)
                    else:
                        resolved_fields[k] = v

                resolved_fields["ws_id"] = rcx.persona.ws_id

                new_id = await ckit_erp.create_erp_record(
                    rcx.fclient,
                    table,
                    rcx.persona.ws_id,
                    resolved_fields,
                )
                logger.info(f"Created ERP record in {table}: {new_id}")

            elif action_type == "update_erp_record":
                table = action.get("table")
                record_id = _resolve_template(action.get("record_id", ""), context)
                fields = action.get("fields", {})

                resolved_fields = {}
                for k, v in fields.items():
                    if isinstance(v, str):
                        resolved_fields[k] = _resolve_field_value(v, context, k)
                    else:
                        resolved_fields[k] = v

                logger.info(f"update_erp_record: table={table} record_id={record_id} resolved_fields={resolved_fields}")
                await ckit_erp.patch_erp_record(
                    rcx.fclient,
                    table,
                    rcx.persona.ws_id,
                    record_id,
                    resolved_fields,
                )
                logger.info(f"Updated ERP record in {table}: {record_id}")

            elif action_type == "delete_erp_record":
                table = action.get("table")
                record_id = _resolve_template(action.get("record_id", ""), context)

                await ckit_erp.delete_erp_record(
                    rcx.fclient,
                    table,
                    rcx.persona.ws_id,
                    record_id,
                )
                logger.info(f"Deleted ERP record from {table}: {record_id}")

            else:
                logger.warning(f"Unknown action type: {action_type}")

        except Exception as e:
            logger.error(f"Action '{action_type}' failed: {e}", exc_info=True)


def _resolve_template(template: str, context: Dict[str, Any]) -> str:
    if not isinstance(template, str):
        return template

    result = template
    matches = re.findall(r'\{\{(.+?)\}\}', template)

    for match in matches:
        parts = match.strip().split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break

        if value is not None:
            result = result.replace(f"{{{{{match}}}}}", str(value))

    return result


def _resolve_field_value(field_value: str, context: Dict[str, Any], field_name: str) -> Any:
    import time

    value = field_value.strip()
    if value.startswith('='):
        value = value[1:].strip()

    is_timestamp_field = field_name.endswith('_ts')

    matches = re.findall(r'\{\{(.+?)\}\}', value)
    for match in matches:
        match_content = match.strip()

        if any(c in match_content for c in '+-*/()'):
            try:
                result = eval(match_content, {"__builtins__": {}, "now": lambda: time.time()}, {})
                value = value.replace(f"{{{{{match}}}}}", repr(result))
                continue
            except:
                pass

        parts = match_content.split(".")
        resolved_value = context
        for part in parts:
            if isinstance(resolved_value, dict):
                resolved_value = resolved_value.get(part)
            else:
                resolved_value = None
                break

        if resolved_value is not None:
            value = value.replace(f"{{{{{match}}}}}", repr(resolved_value))
        else:
            value = value.replace(f"{{{{{match}}}}}", '[]' if field_name.endswith(('_tags', '_list')) else repr(None))

    logger.debug(f"_resolve_field_value: field_name={field_name} original={field_value!r} after_template={value!r}")

    if any(op in value for op in ['+', '-', '*', '/']):
        if re.match(r'^[\[\]\d\s+\-.*/()\'"a-zA-Z_,]+$', value):
            try:
                result = eval(value, {"__builtins__": {}}, {})
                logger.debug(f"_resolve_field_value: evaluated {value!r} to {result!r}")
                if is_timestamp_field:
                    return float(result)
                return result
            except Exception as e:
                logger.warning(f"Failed to evaluate expression '{value}': {e}")
                return None

    if is_timestamp_field:
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert timestamp field '{field_name}' value '{value}' to float")
            return value

    return value


def validate_automation_config(automation_config: Dict[str, Any]) -> Optional[str]:
    if not isinstance(automation_config, dict):
        return "❌ automation_config must be a dict"

    triggers = automation_config.get("triggers")
    if not triggers:
        return "❌ Missing required field 'triggers' (must be a non-empty list)"
    if not isinstance(triggers, list):
        return "❌ Field 'triggers' must be a list"

    for i, trigger in enumerate(triggers):
        if not isinstance(trigger, dict):
            return f"❌ triggers[{i}] must be a dict"
        if trigger.get("type") != "erp_table":
            return f"❌ triggers[{i}].type must be 'erp_table' (got {trigger.get('type')})"
        if "table" not in trigger:
            return f"❌ triggers[{i}] missing required field 'table'"
        operations = trigger.get("operations")
        if not operations or not isinstance(operations, list):
            return f"❌ triggers[{i}] missing required field 'operations' (list like ['insert', 'update'])"
        for op in operations:
            if op.upper() not in ("INSERT", "UPDATE", "DELETE"):
                return f"❌ triggers[{i}].operations contains invalid operation '{op}' (must be insert/update/delete)"

    actions = automation_config.get("actions", [])
    if not isinstance(actions, list):
        return "❌ Field 'actions' must be a list"

    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            return f"❌ actions[{i}] must be a dict"
        action_type = action.get("type")
        if action_type == "post_task_into_bot_inbox":
            if "title" not in action:
                return f"❌ actions[{i}] (post_task_into_bot_inbox) missing required field 'title'"
        elif action_type == "create_erp_record":
            if "table" not in action:
                return f"❌ actions[{i}] (create_erp_record) missing required field 'table'"
            if "fields" not in action:
                return f"❌ actions[{i}] (create_erp_record) missing required field 'fields'"
        elif action_type == "update_erp_record":
            if "table" not in action:
                return f"❌ actions[{i}] (update_erp_record) missing required field 'table'"
            if "record_id" not in action:
                return f"❌ actions[{i}] (update_erp_record) missing required field 'record_id'"
            if "fields" not in action:
                return f"❌ actions[{i}] (update_erp_record) missing required field 'fields'"
        elif action_type == "delete_erp_record":
            if "table" not in action:
                return f"❌ actions[{i}] (delete_erp_record) missing required field 'table'"
            if "record_id" not in action:
                return f"❌ actions[{i}] (delete_erp_record) missing required field 'record_id'"
        else:
            return f"❌ actions[{i}].type must be 'post_task_into_bot_inbox', 'create_erp_record', 'update_erp_record', or 'delete_erp_record' (got {action_type})"

    return None
