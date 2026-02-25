import csv
import dataclasses
import io
import json
import time
import logging
from typing import Dict, Any, Optional, List, Type, Union, get_origin, get_args
from pymongo.collection import Collection

import gql.transport.exceptions

from flexus_client_kit.core import ckit_cloudtool, ckit_client, ckit_erp, ckit_mongo
from flexus_client_kit.core import erp_schema

logger = logging.getLogger("fi_erp")


ERP_TABLE_META_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="erp_table_meta",
    description=(
        "Get metadata about ERP tables including columns and relations. "
        "Use '', '*', or 'all' to list all tables with column names only. "
        "Use 'table1,table2' to get detailed info for multiple specific tables."
    ),
    parameters={
        "type": "object",
        "properties": {
            "table_name": {"type": "string", "description": "Table name, '*' for all tables, or 'table1,table2' for multiple"},
        },
        "required": ["table_name"],
    },
)


ERP_TABLE_DATA_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="erp_table_data",
    description=(
        "Query ERP table data with filtering. "
        "Operators: =, !=, >, >=, <, <=, LIKE, ILIKE, CIEQL, IN, NOT_IN, IS_NULL, IS_NOT_NULL. "
        "LIKE/ILIKE use SQL wildcards: % matches any chars. CIEQL: Case Insensitive Equal. "
        "JSON path: details->subtype:=:welcome. "
        "Examples: "
        'filters="status:=:active" for single filter, '
        'filters={"AND": ["status:=:active", "type:=:lead"]} for multiple AND, '
        'filters={"OR": ["contact_email:ILIKE:%@gmail.com", "contact_email:ILIKE:%@yahoo.com"]} for OR.'
    ),
    parameters={
        "type": "object",
        "properties": {
            "table_name": {"type": "string", "description": "Name of the ERP table to query", "order": 1},
            "options": {
                "type": "object",
                "description": "Query options",
                "order": 2,
                "properties": {
                    "skip": {"type": "integer", "description": "Number of rows to skip (default 0)", "order": 1001},
                    "limit": {"type": "integer", "description": "Maximum number of rows to return (default 100, max 1000)", "order": 1002},
                    "sort_by": {"type": "array", "items": {"type": "string"}, "description": 'Sort expressions ["column:ASC", "another:DESC"]', "order": 1003},
                    "filters": {"oneOf": [{"type": "string"}, {"type": "object"}], "description": 'String or object with AND/OR key, e.g. {"AND": ["col:op:val"]} or {"OR": [...]}', "order": 1004},
                    "include": {"type": "array", "items": {"type": "string"}, "description": 'Relation names to include ["prodt", "pcat"]', "order": 1005},
                    "safety_valve": {"type": "string", "description": 'Output character limit "5k" or "10000" (default 5k)', "order": 1006},
                },
            },
        },
        "required": ["table_name"],
    },
)


ERP_TABLE_CRUD_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="erp_table_crud",
    description=(
        "Create, update (patch), or delete records in ERP tables. "
        "First call erp_table_meta to see available columns. "
        "Example: erp_table_crud(op='create', table_name='crm_contact', fields={'contact_first_name': 'John', 'contact_last_name': 'Doe', 'contact_email': 'john@example.com'})"
    ),
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["create", "patch", "delete"], "order": 1},
            "table_name": {"type": "string", "description": "Table name", "order": 2},
            "id": {"type": "string", "description": "Record ID (for patch and delete)", "order": 3},
            "fields": {"type": "object", "description": "Field values (for create and patch)", "order": 4},
        },
        "required": ["op", "table_name"],
    },
)


ERP_CSV_IMPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="erp_csv_import",
    description=(
        "Import a normalized CSV (columns must match ERP table fields) stored via mongo_store. "
        "Provide mongo_path of the CSV, target table_name, and an optional upsert_key column."
    ),
    parameters={
        "type": "object",
        "properties": {
            "table_name": {"type": "string", "description": "Target ERP table name", "order": 1},
            "mongo_path": {"type": "string", "description": "Path of the CSV stored via mongo_store or python_execute artifacts", "order": 2},
            "upsert_key": {"type": "string", "description": "Column used to detect existing records (e.g., contact_email). Leave blank to always create.", "order": 3},
        },
        "required": ["table_name", "mongo_path"],
    },
)


def _format_table_meta_text(table_name: str, schema_class: type) -> str:
    result = f"Table: erp.{table_name}\n\nColumns:\n"
    for field_name, field_type in schema_class.__annotations__.items():
        type_str = str(field_type).replace("typing.", "")
        meta = schema_class.__dataclass_fields__[field_name].metadata
        line = f"  • {field_name}: {type_str}"
        if meta.get("pkey"):
            line += " [PRIMARY KEY]"
        if display_name := meta.get("display_name"):
            line += f" — {display_name}"
        if description := meta.get("description"):
            line += f" ({description})"
        result += line + "\n"
        if examples := meta.get("examples"):
            result += f"      examples: {examples}\n"
        if enum_values := meta.get("enum"):
            result += "      enum: " + ", ".join(f"{e['value']}" for e in enum_values) + "\n"
    return result


def _rows_to_text(rows: list, table_name: str, safety_valve_chars: int = 5000) -> tuple[str, Optional[str]]:
    """
    Convert rows to text output. If output is large, return cropped version and full json for mongo storage.
    Returns: (display_text, optional_full_json_for_mongo)
    """
    header_lines = [f"Table: {table_name}"]

    full_json = json.dumps(rows, default=str, indent=2)
    full_size = len(full_json)

    if full_size <= safety_valve_chars:
        header_lines.append(f"{len(rows)} rows")
        result = header_lines + [""] + [json.dumps(row, default=str) for row in rows]
        return "\n".join(result), None

    result = []
    ctx_left = safety_valve_chars

    for i in range(len(rows)):
        line = json.dumps(rows[i], default=str)
        if len(line) > safety_valve_chars:
            if len(result) > 0:
                header_lines.append(f"⚠️ Row {i+1} is too large, output truncated. Full result saved to mongo.")
                break
            else:
                header_lines.append(f"⚠️ Row {i+1} is {len(line)} chars, truncated. Full result saved to mongo.")
                result = [line[:safety_valve_chars]]
                break
        ctx_left -= len(line)
        result.append(line)
        if ctx_left < 0:
            header_lines.append(f"⚠️ {len(rows)} rows total, showing rows 1:{i+1}. Full result saved to mongo.")
            break

    if ctx_left >= 0 and len(rows) > len(result):
        header_lines.append(f"⚠️ {len(rows)} rows total, showing {len(result)}. Full result saved to mongo.")

    result = header_lines + [""] + result
    return "\n".join(result), full_json


def _resolve_field_type(field_type: Optional[Type[Any]]) -> Optional[Type[Any]]:
    if not field_type:
        return None
    origin = get_origin(field_type)
    if origin is Union:
        if non_none := [arg for arg in get_args(field_type) if arg is not type(None)]:
            return _resolve_field_type(non_none[0])
    if origin in (list, dict):
        return origin
    return field_type


def _convert_csv_value(raw_value: str, field_type: Optional[Type[Any]]) -> Any:
    value = raw_value.strip()
    if value == "":
        return None
    normalized_type = _resolve_field_type(field_type)
    if normalized_type is bool:
        lowered = value.lower()
        if lowered in ("true", "1", "yes", "y"):
            return True
        if lowered in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"Value {value!r} is not a valid boolean")
    if normalized_type is int:
        return int(value)
    if normalized_type is float:
        return float(value)
    if normalized_type in (list, dict):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Expected JSON for {normalized_type.__name__}: {e}")
    return value


class IntegrationErp:
    def __init__(
        self,
        client: ckit_client.FlexusClient,
        ws_id: str,
        mongo_collection: Optional[Collection] = None,
    ):
        self.client = client
        self.ws_id = ws_id
        self.mongo_collection = mongo_collection


    async def handle_erp_meta(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        table_name = args.get("table_name", "").strip()

        if table_name in ("", "*", "all"):
            result = f"ERP schema has {len(erp_schema.ERP_TABLE_TO_SCHEMA)} tables.\n"
            result += "Call again with specific table names to show column types and relations.\n\n"
            for tbl_name in sorted(erp_schema.ERP_TABLE_TO_SCHEMA.keys()):
                schema_class = erp_schema.ERP_TABLE_TO_SCHEMA[tbl_name]
                columns = list(schema_class.__annotations__.keys())
                result += json.dumps({"table": tbl_name, "columns": columns}) + "\n"
            return result

        table_names = [t.strip() for t in table_name.split(",") if t.strip()]

        if not table_names:
            return "❌ Error: table_name is required"

        if len(table_names) > 5:
            logger.warning(f"ERP table meta: requested {len(table_names)} tables, limiting to 5")
            table_names = table_names[:5]

        result_text = ""
        for tn in table_names:
            if tn not in erp_schema.ERP_TABLE_TO_SCHEMA:
                if result_text:
                    result_text += "\n\n"
                result_text += f"❌ Error: Table '{tn}' not found in schema\n"
                continue

            schema_class = erp_schema.ERP_TABLE_TO_SCHEMA[tn]
            if result_text:
                result_text += "\n\n"
            result_text += _format_table_meta_text(tn, schema_class)

        return result_text


    async def handle_erp_data(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        table_name = args.get("table_name", "").strip()
        options = args.get("options", {})

        if not table_name:
            return "❌ Error: table_name is required"

        if table_name not in erp_schema.ERP_TABLE_TO_SCHEMA:
            return f"❌ Error: Table '{table_name}' not found in schema"

        skip = options.get("skip", 0)
        limit = options.get("limit", 100)
        sort_by = options.get("sort_by", [])
        filters = options.get("filters", {})
        include = options.get("include", [])
        safety_valve = options.get("safety_valve", "5k")

        if not isinstance(sort_by, list):
            sort_by = []
        if not isinstance(filters, (str, dict)):
            filters = {}
        if not isinstance(include, list):
            include = []

        safety_valve_chars = 0
        if safety_valve.lower().endswith('k'):
            safety_valve_chars = int(safety_valve[:-1]) * 1000
        else:
            safety_valve_chars = int(safety_valve)
        safety_valve_chars = max(1000, safety_valve_chars)

        schema_class = erp_schema.ERP_TABLE_TO_SCHEMA[table_name]

        try:
            rows = await ckit_erp.query_erp_table(
                self.client,
                table_name,
                self.ws_id,
                schema_class,
                skip=skip,
                limit=min(limit, 1000),
                sort_by=sort_by,
                filters=filters,
                include=include,
            )
        except gql.transport.exceptions.TransportQueryError as e:
            logger.info(f"ERP query validation fail: {e}")
            return f"❌ Error querying table: {e}"

        rows_as_dicts = [ckit_erp.dataclass_or_dict_to_dict(r) for r in rows]

        display_text, full_json = _rows_to_text(rows_as_dicts, table_name, safety_valve_chars)

        if full_json and self.mongo_collection is not None:
            mongo_path = f"erp_query_results/{table_name}_{int(time.time())}.json"
            try:
                await ckit_mongo.mongo_overwrite(
                    self.mongo_collection,
                    mongo_path,
                    full_json.encode('utf-8'),
                    ttl=86400,
                )
                display_text += f"\n\n💾 Full results stored in mongo at: {mongo_path}"
                display_text += f"\nUse mongo_store(op='cat', args={{'path': '{mongo_path}'}}) to view full results."
            except Exception as e:
                logger.error(f"Failed to save to mongo: {e}", exc_info=e)
                display_text += f"\n\n⚠️ Failed to save full results to mongo: {e}"

        return display_text

    async def handle_erp_crud(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        op = model_produced_args.get("op", "")

        if not op:
            return "❌ Error: op parameter required (create, patch, or delete)"

        table_name = model_produced_args.get("table_name", "")

        if not table_name:
            return "❌ Error: table_name parameter required"

        if not (schema_class := erp_schema.ERP_TABLE_TO_SCHEMA.get(table_name)):
            return f"❌ Error: Table '{table_name}' not found in schema"

        if op == "create":
            fields = model_produced_args.get("fields", {})

            if not fields or not isinstance(fields, dict):
                return "❌ Error: fields parameter required and must be a dict for create operation"

            try:
                new_id = await ckit_erp.create_erp_record(
                    self.client,
                    table_name,
                    self.ws_id,
                    fields,
                )
                return f"✅ Created new record in {table_name} with ID: {new_id}"
            except gql.transport.exceptions.TransportQueryError as e:
                logger.info(f"ERP create validation fail: {e}")
                return f"❌ Error creating record: {e}"

        elif op == "patch":
            record_id = model_produced_args.get("id")
            fields = model_produced_args.get("fields", {})

            if record_id is None:
                return "❌ Error: id parameter required for patch operation"

            if not fields or not isinstance(fields, dict):
                return "❌ Error: fields parameter required and must be a dict for patch operation"

            record_id = str(record_id)

            try:
                success = await ckit_erp.patch_erp_record(
                    self.client,
                    table_name,
                    self.ws_id,
                    record_id,
                    fields,
                )
                if success:
                    return f"✅ Updated record {record_id} in {table_name}"
                else:
                    return f"❌ Failed to update record {record_id} in {table_name}"
            except gql.transport.exceptions.TransportQueryError as e:
                logger.info(f"ERP patch validation fail: {e}")
                return f"❌ Error updating record: {e}"

        elif op == "delete":
            record_id = model_produced_args.get("id")

            if record_id is None:
                return "❌ Error: id parameter required for delete operation"

            record_id = str(record_id)

            try:
                success = await ckit_erp.delete_erp_record(
                    self.client,
                    table_name,
                    self.ws_id,
                    record_id,
                )
                if success:
                    return f"✅ Deleted record {record_id} from {table_name}"
                else:
                    return f"❌ Failed to delete record {record_id} from {table_name} (may not exist)"
            except gql.transport.exceptions.TransportQueryError as e:
                logger.info(f"ERP delete validation fail: {e}")
                return f"❌ Error deleting record: {e}"

        else:
            return f"❌ Error: Unknown operation '{op}'. Use create, patch, or delete."


    async def handle_csv_import(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        if self.mongo_collection is None:
            return "❌ Cannot read CSV because MongoDB storage is unavailable for this bot."

        if not (table_name := args.get("table_name", "").strip()) or not (mongo_path := args.get("mongo_path", "").strip()):
            return "❌ table_name and mongo_path are required"
        upsert_key = args.get("upsert_key", "").strip()

        if not (schema_class := erp_schema.ERP_TABLE_TO_SCHEMA.get(table_name)):
            return f"❌ Unknown table '{table_name}'. Run erp_table_meta for available tables."
        pk_field = erp_schema.get_pkey_field(schema_class)

        if not (document := await ckit_mongo.mongo_retrieve_file(self.mongo_collection, mongo_path)):
            return f"❌ File {mongo_path!r} not found in MongoDB."

        if not (file_bytes := document.get("data") or (json.dumps(document["json"]).encode("utf-8") if document.get("json") is not None else None)):
            return f"❌ File {mongo_path!r} is empty."

        try:
            csv_text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            return "❌ CSV must be UTF-8 encoded."

        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames:
            return "❌ CSV header row is missing."
        reader.fieldnames = trimmed_headers = [(name or "").strip() for name in reader.fieldnames]

        allowed_fields = set(schema_class.__annotations__.keys())
        details_field = next((f for f in allowed_fields if f.endswith("_details")), None)

        if unknown_headers := [h for h in trimmed_headers if h and h not in allowed_fields]:
            fix_hint = f"Fix: Remove them, add to '{details_field}' as JSON, or map to existing columns." if details_field else "Fix: Remove them or map to existing columns (use erp_table_meta to see valid columns)."
            return f"❌ Unknown columns: {', '.join(unknown_headers)}\n\n{fix_hint}"

        if upsert_key and upsert_key not in trimmed_headers:
            return f"❌ upsert_key '{upsert_key}' is not present in the CSV header."

        field_types = schema_class.__annotations__
        required_fields = {name for name, field_info in schema_class.__dataclass_fields__.items() if field_info.default == dataclasses.MISSING and field_info.default_factory == dataclasses.MISSING and name != pk_field and name != "ws_id"}

        errors: List[str] = []
        records = []
        for row_idx, row in enumerate(reader, start=1):
            try:
                record = {}
                for column in trimmed_headers:
                    if column and column != pk_field and (raw_value := str(row.get(column, "")).strip()):
                        record[column] = _convert_csv_value(raw_value, field_types.get(column))

                if "ws_id" in allowed_fields and not record.get("ws_id"):
                    record["ws_id"] = self.ws_id

                if upsert_key and not (key_value := str(row.get(upsert_key, "")).strip()):
                    raise ValueError(f"Missing value for upsert_key '{upsert_key}'")

                if missing := required_fields - record.keys():
                    raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

                records.append(record)
            except Exception as e:
                errors.append(f"Row {row_idx}: {e}")

        BATCH_SIZE = 1000
        total_created = total_updated = 0
        total_failed = sum(1 for e in errors if e.startswith('Row '))
        batch_errors = 0

        for i in range(0, len(records), BATCH_SIZE):
            try:
                result = await ckit_erp.erp_table_batch_upsert(self.client, table_name, self.ws_id, upsert_key or "", records[i:i+BATCH_SIZE])
                total_created += result.get("created", 0)
                total_updated += result.get("updated", 0)
                total_failed += result.get("failed", 0)
                errors.extend(f"Batch {i//BATCH_SIZE + 1}: {err}" for err in result.get("errors", []))
            except Exception as e:
                total_failed += len(records[i:i+BATCH_SIZE])
                errors.append(f"Batch {i//BATCH_SIZE + 1} failed: {e}")
                batch_errors += 1
                if batch_errors > 3:
                    errors.append("Aborting: too many batch errors")
                    break

        lines = [
            f"Processed {len(records) + sum(1 for e in errors if e.startswith('Row '))} row(s) from {mongo_path}.",
            f"Created: {total_created}, Updated: {total_updated}, Failed: {total_failed}.",
        ]
        if errors:
            lines.append("Errors:")
            lines.extend(f"  • {err}" for err in errors[:5])
            if len(errors) > 5:
                lines.append(f"  …and {len(errors) - 5} more errors.")

        return "\n".join(lines)
