from typing import List, Type, TypeVar
import asyncio
import gql

from flexus_client_kit import ckit_client, gql_utils

T = TypeVar('T')


async def query_erp_table(
    client: ckit_client.FlexusClient,
    table_name: str,
    ws_id: str,
    result_class: Type[T],
    skip: int = 0,
    limit: int = 100,
    sort_by: List[str] = [],
    filters: List[str] = [],
) -> List[T]:
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
                $filters: [String!]!
            ) {
                erp_table_data(
                    schema_name: $schema_name,
                    table_name: $table_name,
                    ws_id: $ws_id,
                    skip: $skip,
                    limit: $limit,
                    sort_by: $sort_by,
                    filters: $filters
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
            },
        )
        rows = r["erp_table_data"]
        return [gql_utils.dataclass_from_dict(row, result_class) for row in rows]


async def test():
    from flexus_client_kit.erp.product_template import ProductTemplate
    client = ckit_client.FlexusClient("ckit_erp_test")
    ws_id = "solarsystem"
    products = await query_erp_table(
        client,
        "product_template",
        ws_id,
        ProductTemplate,
        limit=10,
        filters=[],
        sort_by=["prodt_name:ASC"],
    )
    print(f"Found {len(products)} active products:")
    for p in products:
        print(p)


if __name__ == "__main__":
    asyncio.run(test())
