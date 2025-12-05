from typing import List, Type, TypeVar, Any, Union
import asyncio
import dataclasses
import json
import gql

from flexus_client_kit import ckit_client, gql_utils

T = TypeVar('T')


def dataclass_or_dict_to_dict(x: Any) -> dict:
    if dataclasses.is_dataclass(x):
        result = dataclasses.asdict(x)
        return {k: v for k, v in result.items() if v is not None}
    elif isinstance(x, dict):
        return {k: v for k, v in x.items() if v is not None}
    else:
        raise ValueError(f"must be a dataclass or dict, got {type(x)}")


async def query_erp_table(
    client: ckit_client.FlexusClient,
    table_name: str,
    ws_id: str,
    result_class: Type[T],
    skip: int = 0,
    limit: int = 100,
    sort_by: List[str] = [],
    filters: List[str] = [],
    include: List[str] = [],
) -> List[T]:
    if include:
        for inc_field in include:
            assert inc_field in result_class.__annotations__, f"Field {inc_field!r} not in {result_class.__name__}"

    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""query ErpTableQuery(
                $schema_name: String!,
                $table_name: String!,
                $ws_id: String!,
                $skip: Int!,
                $limit: Int!,
                $sort_by: [String!]!,
                $filters: [String!]!,
                $include: [String!]!
            ) {
                erp_table_data(
                    schema_name: $schema_name,
                    table_name: $table_name,
                    ws_id: $ws_id,
                    skip: $skip,
                    limit: $limit,
                    sort_by: $sort_by,
                    filters: $filters,
                    include: $include
                )
            }"""),
            variable_values={
                "schema_name": "erp",
                "table_name": table_name,
                "ws_id": ws_id,
                "skip": skip,
                "limit": limit,
                "sort_by": sort_by,
                "filters": filters,
                "include": include,
            },
        )
        rows = r["erp_table_data"]
        return [gql_utils.dataclass_from_dict(row, result_class) for row in rows]


async def create_erp_record(
    client: ckit_client.FlexusClient,
    table_name: str,
    ws_id: str,
    record: Any,
) -> int:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(gql.gql("""
            mutation ErpTableCreate($schema_name: String!, $table_name: String!, $ws_id: String!, $record_json: String!) {
                erp_table_create(schema_name: $schema_name, table_name: $table_name, ws_id: $ws_id, record_json: $record_json)
            }"""),
            variable_values={
                "schema_name": "erp",
                "table_name": table_name,
                "ws_id": ws_id,
                "record_json": json.dumps(dataclass_or_dict_to_dict(record)),
            },
        )
        return r["erp_table_create"]


async def patch_erp_record(
    client: ckit_client.FlexusClient,
    table_name: str,
    ws_id: str,
    pk_value: str,
    updates: Any,
) -> bool:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(gql.gql("""
            mutation ErpTablePatch($schema_name: String!, $table_name: String!, $ws_id: String!, $pk_value: String!, $updates_json: String!) {
                erp_table_patch(schema_name: $schema_name, table_name: $table_name, ws_id: $ws_id, pk_value: $pk_value, updates_json: $updates_json)
            }"""),
            variable_values={
                "schema_name": "erp",
                "table_name": table_name,
                "ws_id": ws_id,
                "pk_value": pk_value,
                "updates_json": json.dumps(dataclass_or_dict_to_dict(updates)),
            },
        )
        return r["erp_table_patch"]


async def delete_erp_record(
    client: ckit_client.FlexusClient,
    table_name: str,
    ws_id: str,
    pk_value: str,
) -> bool:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(gql.gql("""
            mutation ErpTableDelete($schema_name: String!, $table_name: String!, $ws_id: String!, $pk_value: String!) {
                erp_table_delete(schema_name: $schema_name, table_name: $table_name, ws_id: $ws_id, pk_value: $pk_value)
            }"""),
            variable_values={
                "schema_name": "erp",
                "table_name": table_name,
                "ws_id": ws_id,
                "pk_value": pk_value,
            },
        )
        return r["erp_table_delete"]


def check_record_matches_filters(record: dict, filters: List[Union[str, dict]], col_names: set = None) -> bool:
    """
    Check if a record (dict) matches all filters.
    Supports string filters like "col:op:val" and dict filters like {"OR": [...], "AND": [...], "NOT": {...}}.

    Examples:
      "contact_id:=:4"
      "name:ILIKE:%john%"
      "status:IN:active,pending"
      "deleted_ts:IS_NULL"
      "task_details->email_subtype:=:welcome"
      {"OR": ["status:=:active", "status:=:pending"]}

    If col_names is None, any column name is accepted (useful for dynamic schemas).
    """
    for f in filters:
        if isinstance(f, dict):
            if "OR" in f:
                if not any(check_record_matches_filter(record, sub, col_names) for sub in f["OR"]):
                    return False
            elif "AND" in f:
                if not all(check_record_matches_filter(record, sub, col_names) for sub in f["AND"]):
                    return False
            elif "NOT" in f:
                if check_record_matches_filter(record, f["NOT"], col_names):
                    return False
        else:
            if not check_record_matches_filter(record, f, col_names):
                return False
    return True


def check_record_matches_filter(record: dict, f: str, col_names: set = None) -> bool:
    """
    Check if a single record matches a single filter string.
    Filter format: "col:op:val" or "col:op"

    Standard operators: =, !=, >, >=, <, <=, IN, NOT_IN, LIKE, ILIKE, IS_NULL, IS_NOT_NULL
    Array operators: contains, not_contains
    JSON path: "task_details->email_subtype:=:welcome"
    """
    parts = f.split(":", 2)
    if len(parts) < 2:
        return True

    col_spec = parts[0].strip()
    op = parts[1].strip().upper()

    # Parse JSON path
    if "->" in col_spec:
        col_parts = col_spec.split("->")
        col = col_parts[0].strip()
        if col_names and col not in col_names:
            return False
        if col not in record:
            return False
        val = record[col]
        for p in col_parts[1:]:
            if not isinstance(val, dict) or p not in val:
                return False
            val = val[p]
    else:
        col = col_spec
        if col_names and col not in col_names:
            return False
        if col not in record:
            val = None
        else:
            val = record[col]

    # Null checks
    if op in ("IS_NULL", "IS NULL"):
        return val is None
    if op in ("IS_NOT_NULL", "IS NOT NULL"):
        return val is not None

    if len(parts) != 3:
        return True

    filter_val = parts[2].strip()

    # Array operators
    if op == "CONTAINS":
        if val is None or not isinstance(val, list):
            return False
        return filter_val in val

    if op == "NOT_CONTAINS":
        if val is None:
            return True
        if not isinstance(val, list):
            return False
        return filter_val not in val

    # Type coerce for numeric comparisons
    if isinstance(val, (int, float)):
        try:
            filter_val = type(val)(filter_val)
        except (ValueError, TypeError):
            return False

    # Standard operators
    if op == "=":
        return val == filter_val
    if op == "!=":
        return val != filter_val
    if op == ">":
        return val > filter_val
    if op == ">=":
        return val >= filter_val
    if op == "<":
        return val < filter_val
    if op == "<=":
        return val <= filter_val
    if op == "IN":
        vals = [v.strip() for v in filter_val.split(",")]
        return str(val) in vals
    if op in ("NOT_IN", "NOT IN"):
        vals = [v.strip() for v in filter_val.split(",")]
        return str(val) not in vals
    if op in ("LIKE", "ILIKE"):
        s = str(val).lower() if op == "ILIKE" else str(val)
        pattern = filter_val.lower() if op == "ILIKE" else filter_val
        if pattern.startswith("%") and pattern.endswith("%"):
            return pattern[1:-1] in s
        if pattern.startswith("%"):
            return s.endswith(pattern[1:])
        if pattern.endswith("%"):
            return s.startswith(pattern[:-1])
        return s == pattern

    return True


async def test():
    from flexus_client_kit.erp_schema import ProductTemplate, ProductProduct
    client = ckit_client.FlexusClient("ckit_erp_test")
    ws_id = "solarsystem"
    products = await query_erp_table(
        client,
        "product_product",
        ws_id,
        ProductProduct,
        limit=10,
        include=["prodt"],
    )
    print(f"Found {len(products)} products:")
    for p in products:
        print(p)


if __name__ == "__main__":
    asyncio.run(test())
