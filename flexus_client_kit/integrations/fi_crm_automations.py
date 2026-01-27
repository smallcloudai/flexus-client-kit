import json
import logging
import re
import time
from typing import Dict, Any, Optional, List

import gql

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_erp, ckit_kanban, ckit_bot_exec

logger = logging.getLogger("crmau")


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


AUTOMATIONS_PROMPT = """## CRM Automations

You can configure CRM automations to react to ERP table changes and perform actions automatically.

Structure:
- **Triggers**: What event fires the automation (e.g., new contact inserted or updated)
- **Actions**: What to do when triggered (e.g., post a task into inbox, update contact tags)

Common use cases:
- Welcome emails when new contacts arrive
- Follow-up tasks after initial contact
- Automatic task creation based on deal stage changes

Working with Automations:
- Call crm_automation(op="help") and check available ERP tables and schema first with erp_table_meta
- List existing automations
- Do not react to just insert of erp tables, react also to update

Template Variables:

Use `{{trigger.new_record.field_name}}` or `{{trigger.old_record.field_name}}`:
- `{{trigger.new_record.contact_id}}`
- `{{trigger.old_record.contact_email}}` (for updates/deletes)

Special functions:
- `{{now()}}` - current Unix timestamp
- `{{now() + 86400}}` - timestamp calculations

Important Notes:
- Actions execute in sequence
- Failed actions are logged but don't stop subsequent actions
- Automations can be enabled/disabled
- NEVER use my_setup() to set up crm_automations - it will kill the configured automations, only use this tool to manage them"""


CRM_AUTOMATION_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
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
      "provenance": "CRM automation: welcome_email",
      "fexp_name": "nurturing"
    },
    {
      "type": "update_erp_record",
      "table": "crm_contact",
      "record_id": "{{trigger.new_record.contact_id}}",
      "fields": {
        "contact_tags": {"op": "append", "values": ["welcome_email_sent"]}
      }
    }
  ]
}
```

## Template Variables

Use {{path.to.value}} to reference trigger data:
- {{trigger.new_record.contact_id}}
- {{trigger.old_record.contact_email}} (for updates/deletes)

Special functions:
- {{now()}} - current Unix timestamp
- {{now() + 86400}} - timestamp one day from now
- {{now() - 3600}} - timestamp one hour ago

## Field Operations

For atomic operations on fields:

```json
"fields": {
  "contact_tags": {"op": "append", "values": ["tag1", "tag2"]},
  "contact_score": {"op": "increment", "value": 10}
}
```

Supported operations:
- append: Add items to a list field
- remove: Remove items from a list field
- increment: Add to a numeric field
- decrement: Subtract from a numeric field
- set: Set value directly (default when using string)

Template values work in operations:
```json
"contact_tags": {"op": "append", "values": ["{{trigger.new_record.source_tag}}"]}
```

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
        available_erp_tables: List[str],
    ):
        self.client = client
        self.rcx = rcx
        self.get_setup = get_setup_func
        self.available_erp_tables = available_erp_tables or []
        self._setup_automation_handlers()

    def _load_automations(self) -> Dict[str, Any]:
        setup = self.get_setup()
        crm_automations_str = setup.get("crm_automations", "{}")
        try:
            return json.loads(crm_automations_str) if isinstance(crm_automations_str, str) else crm_automations_str
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse crm_automations from setup: {e}")
            return {}

    async def _save_automation(self, automation_name: str, automation_config: Optional[Dict[str, Any]]) -> None:
        http = await self.client.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""mutation PersonaSetupSetKey($persona_id: String!, $set_key: String!, $set_val: String) {
                    persona_setup_set_key(
                        persona_id: $persona_id,
                        set_key: $set_key,
                        set_val: $set_val
                    )
                }"""),
                variable_values={
                    "persona_id": self.rcx.persona.persona_id,
                    "set_key": f"crm_automations.{automation_name}",
                    "set_val": json.dumps(automation_config) if automation_config is not None else None,
                },
            )
        logger.info(f"{'Deleted' if automation_config is None else 'Updated'} automation '{automation_name}' in backend")

    async def handle_crm_automation(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_args: Dict[str, Any]) -> str:
        args, err = ckit_cloudtool.sanitize_args(model_args)
        if err:
            return f"❌ {err}"

        op = ckit_cloudtool.try_best_to_find_argument(args, model_args, "op", "").lower()

        if op == "help":
            help_text = HELP_TEXT
            if self.available_erp_tables:
                help_text += f"\n\n## Available ERP Tables for Triggers you can ONLY create automations for: {', '.join(self.available_erp_tables)}"
            return help_text

        ops = {
            "list": self._op_list, "get": self._op_get,
            "create": self._op_create, "update": self._op_update, "delete": self._op_delete,
        }
        if handler := ops.get(op):
            return await handler(args, model_args)
        return f"❌ Unknown operation '{op}'. Use: {', '.join(ops.keys())}"

    async def _op_list(self, args: Dict[str, Any], model_args: Dict[str, Any]) -> str:
        automations = self._load_automations()
        if not automations:
            return "No CRM automations configured."

        lines = [f"CRM Automations ({len(automations)} total):\n"]
        for name, cfg in automations.items():
            status = "✅ enabled" if cfg.get("enabled", False) else "❌ disabled"
            lines.append(f"• {name}: {status}\n  Triggers: {len(cfg.get('triggers', []))}, Actions: {len(cfg.get('actions', []))}\n")
        return "\n".join(lines)

    async def _op_get(self, args: Dict[str, Any], model_args: Dict[str, Any]) -> str:
        if not (name := str(ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_name", "")).strip()):
            return "❌ Error: automation_name is required"
        automations = self._load_automations()
        if name not in automations:
            return f"❌ Error: Automation '{name}' not found"
        return f"Automation: {name}\n\n{json.dumps(automations[name], indent=2)}"

    async def _op_create(self, args: Dict[str, Any], model_args: Dict[str, Any]) -> str:
        if not (name := str(ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_name", "")).strip()):
            return "❌ Error: automation_name is required"
        if not (config := ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_config", {})):
            return "❌ Error: automation_config is required"
        if not isinstance(config, dict):
            return "❌ Error: automation_config must be a dict"

        automations = self._load_automations()
        if name in automations:
            return f"❌ Error: Automation '{name}' already exists. Use op='update' to modify it."
        if len(automations) >= 30:
            return "❌ Error: Maximum 30 automations per bot. Delete unused automations first."

        if "enabled" not in config:
            config["enabled"] = True

        if err := validate_automation_config(config):
            return err

        await self._save_automation(name, config)
        return f"✅ Created automation '{name}'"

    async def _op_update(self, args: Dict[str, Any], model_args: Dict[str, Any]) -> str:
        if not (name := str(ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_name", "")).strip()):
            return "❌ Error: automation_name is required"
        if not (config := ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_config", {})):
            return "❌ Error: automation_config is required"
        if not isinstance(config, dict):
            return "❌ Error: automation_config must be a dict"

        automations = self._load_automations()
        if name not in automations:
            return f"❌ Error: Automation '{name}' not found. Use op='create' to create it."

        if err := validate_automation_config(config):
            return err

        await self._save_automation(name, config)
        return f"✅ Updated automation '{name}'"

    async def _op_delete(self, args: Dict[str, Any], model_args: Dict[str, Any]) -> str:
        if not (name := str(ckit_cloudtool.try_best_to_find_argument(args, model_args, "automation_name", "")).strip()):
            return "❌ Error: automation_name is required"

        automations = self._load_automations()
        if name not in automations:
            return f"❌ Error: Automation '{name}' not found"

        await self._save_automation(name, None)
        return f"✅ Deleted automation '{name}'"

    def _setup_automation_handlers(self):
        automations = self._load_automations()
        tables = sorted({t["table"] for cfg in automations.values() if cfg.get("enabled", True)
                        for t in cfg.get("triggers", []) if t.get("type") == "erp_table" and t.get("table")})

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
        for trigger in auto_config.get("triggers", []):
            if trigger.get("type") != "erp_table" or trigger.get("table") != table_name:
                continue
            if operation.upper() not in [op.upper() for op in trigger.get("operations", [])]:
                continue
            if trigger_filters := trigger.get("filters", []):
                rec = ckit_erp.dataclass_or_dict_to_dict(old_record if operation.upper() == "DELETE" else new_record)
                if not ckit_erp.check_record_matches_filters(rec, trigger_filters):
                    logger.debug(f"Automation '{auto_name}' filtered out for {table_name}.{operation}")
                    continue

            ctx = {"trigger": {
                "type": "erp_table", "table": table_name, "operation": operation,
                "new_record": ckit_erp.dataclass_or_dict_to_dict(new_record) if new_record else None,
                "old_record": ckit_erp.dataclass_or_dict_to_dict(old_record) if old_record else None,
            }}
            await _execute_actions(rcx, auto_config.get("actions", []), ctx)
            logger.info(f"Automation '{auto_name}' executed for {table_name}.{operation}")


async def _execute_actions(rcx: ckit_bot_exec.RobotContext, actions: List[Dict[str, Any]], ctx: Dict[str, Any]) -> None:
    for action in actions:
        try:
            action_type = action.get("type")
            if action_type == "post_task_into_bot_inbox":
                await ckit_kanban.bot_kanban_post_into_inbox(
                    rcx.fclient, rcx.persona.persona_id,
                    _resolve_template(action.get("title", ""), ctx),
                    json.dumps({k: _resolve_template(v, ctx) if isinstance(v, str) else v for k, v in action.get("details", {}).items()}),
                    _resolve_template(action.get("provenance", "CRM automation"), ctx),
                    action.get("fexp_name", "default"),
                )
                logger.info(f"Posted task into inbox: {action.get('title', '')}")

            elif action_type == "create_erp_record":
                table = action.get("table")
                fields = {k: _resolve_field_value(v, ctx, k) for k, v in action.get("fields", {}).items()}
                fields["ws_id"] = rcx.persona.ws_id
                new_id = await ckit_erp.create_erp_record(rcx.fclient, table, rcx.persona.ws_id, fields)
                logger.info(f"Created ERP record in {table}: {new_id}")

            elif action_type == "update_erp_record":
                table = action.get("table")
                record_id = _resolve_template(action.get("record_id", ""), ctx)
                fields = {k: _resolve_field_value(v, ctx, k) for k, v in action.get("fields", {}).items()}
                logger.info(f"update_erp_record: table={table} record_id={record_id} resolved_fields={fields}")
                await ckit_erp.patch_erp_record(rcx.fclient, table, rcx.persona.ws_id, record_id, fields)
                logger.info(f"Updated ERP record in {table}: {record_id}")

            elif action_type == "delete_erp_record":
                table = action.get("table")
                record_id = _resolve_template(action.get("record_id", ""), ctx)
                await ckit_erp.delete_erp_record(rcx.fclient, table, rcx.persona.ws_id, record_id)
                logger.info(f"Deleted ERP record from {table}: {record_id}")

            else:
                logger.warning(f"Unknown action type: {action_type}")
        except Exception as e:
            logger.error(f"Action '{action.get('type')}' failed: {e}", exc_info=True)


def _resolve_path(path: str, context: Dict[str, Any]) -> Any:
    value = context
    for part in path.strip().split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _resolve_template(template: str, context: Dict[str, Any]) -> str:
    result = template
    for match in re.findall(r'\{\{(.+?)\}\}', template):
        if (value := _resolve_path(match, context)) is not None:
            result = result.replace(f"{{{{{match}}}}}", str(value))
    return result


def _resolve_field_value(field_value: Any, context: Dict[str, Any], field_name: str) -> Any:
    if isinstance(field_value, dict) and "op" in field_value:
        op = field_value["op"]
        if op in ("append", "remove"):
            return {f"${op}": [_resolve_template(str(v), context) for v in field_value.get("values", [])]}
        if op in ("increment", "decrement"):
            return {f"${op}": float(_resolve_template(str(field_value.get("value", 0)), context))}
        if op == "set":
            return _resolve_template(str(field_value.get("value")), context)

    if not isinstance(field_value, str):
        return field_value

    value = field_value.strip()
    for match in re.findall(r'\{\{(.+?)\}\}', value):
        match_content = match.strip()
        if any(c in match_content for c in '+-*/()'):
            try:
                value = value.replace(f"{{{{{match}}}}}", str(eval(match_content, {"__builtins__": {}, "now": lambda: time.time()}, {})))
                continue
            except Exception:
                pass
        if (resolved := _resolve_path(match_content, context)) is not None:
            value = value.replace(f"{{{{{match}}}}}", str(resolved))

    if field_name.endswith('_ts'):
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert timestamp field '{field_name}' value '{value}' to float")
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
