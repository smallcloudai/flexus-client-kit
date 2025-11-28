from typing import List, Type, TypeVar, Any
import asyncio
import dataclasses
import json
import gql

from flexus_client_kit import ckit_client, gql_utils

T = TypeVar('T')


def dataclass_or_dict_to_dict(x: Any) -> dict:
    if dataclasses.is_dataclass(x):
        return dataclasses.asdict(x)
    elif isinstance(x, dict):
        return x
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
        r = await h.execute(
            gql.gql("""mutation ErpTableCreate(
                $schema_name: String!,
                $table_name: String!,
                $ws_id: String!,
                $record_json: String!
            ) {
                erp_table_create(
                    schema_name: $schema_name,
                    table_name: $table_name,
                    ws_id: $ws_id,
                    record_json: $record_json
                )
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
    pk_value: int,
    updates: Any,
) -> bool:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation ErpTablePatch(
                $schema_name: String!,
                $table_name: String!,
                $ws_id: String!,
                $pk_value: Int!,
                $updates_json: String!
            ) {
                erp_table_patch(
                    schema_name: $schema_name,
                    table_name: $table_name,
                    ws_id: $ws_id,
                    pk_value: $pk_value,
                    updates_json: $updates_json
                )
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
    pk_value: int,
) -> bool:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation ErpTableDelete(
                $schema_name: String!,
                $table_name: String!,
                $ws_id: String!,
                $pk_value: Int!
            ) {
                erp_table_delete(
                    schema_name: $schema_name,
                    table_name: $table_name,
                    ws_id: $ws_id,
                    pk_value: $pk_value
                )
            }"""),
            variable_values={
                "schema_name": "erp",
                "table_name": table_name,
                "ws_id": ws_id,
                "pk_value": pk_value,
            },
        )
        return r["erp_table_delete"]


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
