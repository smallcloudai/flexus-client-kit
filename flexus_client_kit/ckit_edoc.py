import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Any, Optional
import gql

from flexus_client_kit import ckit_client, gql_utils

logger = logging.getLogger("edocs")

MAX_EDOCS_PER_REQ = 30

@dataclass
class FExternalDataSourceOutput:
    owner_fuser_id: str
    located_fgroup_id: str
    eds_id: str
    eds_name: str
    eds_type: str
    eds_json: Dict[str, Any]
    eds_last_scan_ts: float

@dataclass
class FExternalDataSourceSubs:
    news_ws_id: str
    news_action: str
    news_payload_id: str
    news_payload: Optional[FExternalDataSourceOutput]

@dataclass
class FEdocOutput:
    ws_id: str
    eds_id: str
    eds_type: str
    edoc_id: str
    edoc_icon: str
    edoc_title: str
    edoc_mtime: int
    edoc_size_bytes: int
    edoc_status_download: str
    edoc_status_graphdb: str
    edoc_status_vectordb: str

async def edoc_get_existing_documents_for_eds(
    client: ckit_client.FlexusClient,
    eds_id: str,
) -> Dict[str, FEdocOutput]:
    http = await client.use_http()
    async with http as h:
        r = await h.execute(
            gql.gql(
                f"""query EdocList($id: String!) {{
                    edoc_list_superuser(eds_id: $id) {{
                        {gql_utils.gql_fields(FEdocOutput)}
                    }}
                }}""",
            ),
            variable_values={"id": eds_id},
        )
    docs_raw = r["edoc_list_superuser"]
    docs_typed = [gql_utils.dataclass_from_dict(d, FEdocOutput) for d in docs_raw]
    logger.info("Found %d existing edocs for %s", len(docs_typed), eds_id)
    return {d.edoc_id: d for d in docs_typed}


async def edoc_delete_batch(
    client: ckit_client.FlexusClient,
    ws_id: str,
    eds_id: str,
    eds_type: str,
    edoc_ids: List[str],
) -> None:
    if not edoc_ids:
        return
    http = await client.use_http()
    sum_deleted_cnt = 0
    async with http as h:
        for i in range(0, len(edoc_ids), MAX_EDOCS_PER_REQ):
            batch = edoc_ids[i:i + MAX_EDOCS_PER_REQ]
            r = await h.execute(
                gql.gql(
                    """mutation EdocDel($ws_id: String!, $eds_id: String!, $eds_type: String!, $edoc_ids: [String!]!) {
                        edoc_delete_multi(ws_id: $ws_id, eds_id: $eds_id, eds_type: $eds_type, edoc_ids: $edoc_ids)
                    }""",
                ),
                variable_values={
                    "ws_id": ws_id,
                    "eds_id": eds_id,
                    "eds_type": eds_type,
                    "edoc_ids": batch,
                },
            )
            deleted_cnt = r["edoc_delete_multi"]
            assert deleted_cnt == len(batch), (
                f"After deleting edoc_ids={edoc_ids!r}, \n"
                f"server deleted {deleted_cnt} while we requested {len(edoc_ids)}"
            )
            sum_deleted_cnt += deleted_cnt
    logger.info("Deleted %d edocs from ws %s", sum_deleted_cnt, ws_id)


# A small helper needed by *edoc_create* – kept private.
_EXT_ICONS = {
    'txt': "📝", 'doc': "📝", 'docx': "📝", 'rtf': "📝", 'odt': "📝", 'md': "📝",
    'xls': "📊", 'xlsx': "📊", 'csv': "📊", 'ods': "📊",
    'ppt': "📽️", 'pptx': "📽️", 'odp': "📽️",
    'jpg': "🖼️", 'jpeg': "🖼️", 'png': "🖼️", 'gif': "🖼️", 'svg': "🖼️", 'webp': "🖼️",
    'mp4': "🎬", 'avi': "🎬", 'mov': "🎬", 'mkv': "🎬",
    'pdf': "📑",
    'py': "🐍", 'js': "📄", 'html': "📄", 'css': "📄", 'json': "📄",
    'java': "📄", 'c': "📄", 'cpp': "📄", 'h': "📄", 'hpp': "📄", 'cs': "📄",
    'go': "📄", 'rs': "📄", 'rb': "📄", 'php': "📄", 'swift': "📄", 'kt': "📄",
    'ts': "📄", 'jsx': "📄", 'tsx': "📄", 'vue': "📄", 'sql': "📄", 'sh': "📄",
    'yaml': "📄", 'yml': "📄", 'toml': "📄", 'xml': "📄",
    'zip': "📦", 'rar': "📦", 'tar': "📦", 'gz': "📦",
}


async def edoc_create(
    client: ckit_client.FlexusClient,
    ws_id: str,
    eds_id: str,
    eds_type: str,
    edoc_id: str,
    edoc_title: str,
    edoc_size_bytes: int,
    edoc_icon: Optional[str] = None,
) -> FEdocOutput:
    if not edoc_icon:
        ext = edoc_title.split(".")[-1].lower() if "." in edoc_title else ""
        edoc_icon = _EXT_ICONS.get(ext, "📎")
    payload = {
        "ws_id": ws_id,
        "eds_id": eds_id,
        "eds_type": eds_type,
        "edoc_id": edoc_id,
        "edoc_icon": edoc_icon,
        "edoc_title": edoc_title,
        "edoc_mtime": 0,
        "edoc_size_bytes": edoc_size_bytes,
        "edoc_status_download": "EDOC_FOUND",
        "edoc_status_graphdb": "",
        "edoc_status_vectordb": "",
    }
    http_client = await client.use_http()
    async with http_client as http:
        result = await http.execute(
            gql.gql(
                f"""mutation EdocUpsert($p: FEdocInput!) {{
                    edoc_upsert(p: $p) {{
                        {gql_utils.gql_fields(FEdocOutput)}
                    }}
                }}""",
            ),
            variable_values={
                "p": payload,
            },
        )
    logger.info("edoc_create: %s", edoc_title)
    return gql_utils.dataclass_from_dict(result["edoc_upsert"], FEdocOutput)

async def edoc_patch(
    client: ckit_client.FlexusClient,
    p: Dict[str, Any]
) -> bool:
    http_client = await client.use_http()
    async with http_client as http:
        result = await http.execute(
            gql.gql(
                """mutation EdocUpdate($p: FEdocUpdateInput!) {
                    edoc_update(p: $p)
                }""",
            ),
            variable_values={
                "p": p,
            },
        )
    logger.debug("edoc_patch %s updated with %s", p["edoc_id"], {k: v for k, v in p.items()})
    return result["edoc_update"]

async def edoc_upsert(
    client: ckit_client.FlexusClient,
    p: Dict[str, Any]
) -> FEdocOutput:
    http_client = await client.use_http()
    async with http_client as http:
        result = await http.execute(
            gql.gql(
                f"""mutation EdocUpsert($p: FEdocInput!) {{
                    edoc_upsert(p: $p) {{
                        {gql_utils.gql_fields(FEdocOutput)}
                    }}
                }}""",
            ),
            variable_values={
                "p": p
            }
        )
    logger.debug("edoc_upsert %s with %s", p["edoc_id"], {k: v for k, v in p.items()})
    return gql_utils.dataclass_from_dict(result["edoc_upsert"], FEdocOutput)

async def subscribe_to_eds_types(
    ws_client,
    types: List[str],
    ws_id: Optional[str] = None,
) -> AsyncGenerator[FExternalDataSourceSubs, None]:
    async with ws_client as ws:
        async for r in ws.subscribe(gql.gql(
            f"""subscription EdsSubs($types: [String!]!, $ws_id: String) {{
                eds_subs(eds_types: $types, ws_id: $ws_id) {{
                    {gql_utils.gql_fields(FExternalDataSourceSubs)}
                }}
            }}"""), variable_values={"types": types, "ws_id": ws_id}):
            subs = gql_utils.dataclass_from_dict(r["eds_subs"], FExternalDataSourceSubs)
            yield subs

async def eds_report_error(fclient: ckit_client.FlexusClient, eds_id: str, error_msg: str):
    http = await fclient.use_http()
    async with http as h:
        await h.execute(
            gql.gql(
                """mutation EdsError($eds_id: String!, $error_msg: String!) {
                    eds_error(eds_id: $eds_id, error_msg: $error_msg)
                }""",
            ),
            variable_values={"eds_id": eds_id, "error_msg": error_msg},
        )
    logger.info("eds_report_error: %s", error_msg)


async def eds_mark_success(fclient: ckit_client.FlexusClient, eds_id: str):
    http = await fclient.use_http()
    async with http as h:
        await h.execute(
            gql.gql(
                """mutation EdsMarkSuccess($eds_id: String!) {
                    eds_mark_success(eds_id: $eds_id)
                }""",
            ),
            variable_values={"eds_id": eds_id},
        )
    logger.info("eds_mark_success: %s", eds_id)
