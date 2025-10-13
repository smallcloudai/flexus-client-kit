import json
import gql
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from bson import Binary
from pymongo.collection import Collection

from flexus_client_kit import ckit_client


async def get_mongodb_creds(
    client: ckit_client.FlexusClient,
    persona_id: str,
) -> str:
    http = await client.use_http()
    # XXX use gql_with_retry
    async with http as h:
        r = await h.execute(
            gql.gql("""mutation GetMongoDbCreds($persona_id: String!) {
                bot_mongodb_creds(persona_id: $persona_id)
            }"""),
            variable_values={
                "persona_id": persona_id,
            },
        )
        return r["bot_mongodb_creds"]


async def store_file(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
    expiry_after_s: Optional[int] = -1 # -1 never expire
) -> str:
    existing_doc = await mongo_collection.find_one({"path": file_path}, {"ctime": 1})
    old_ctime = existing_doc["ctime"] if existing_doc else None

    if existing_doc:
        await mongo_collection.delete_one({"path": file_path})

    t = time.time()
    document = {
        "path": file_path,
        "ctime": old_ctime if old_ctime else t,
        "mtime": t,
        "size_bytes": len(file_data),
    }
    if expiry_after_s != -1:
        document["expires_at"] = datetime.now(timezone.utc) + timedelta(seconds = expiry_after_s)

    if file_path.endswith(".json"):
        json_data = json.loads(file_data.decode("utf-8"))
        document["json"] = json_data
    else:
        document["data"] = Binary(file_data)

    result = await mongo_collection.insert_one(document)
    return str(result.inserted_id)


async def retrieve_file(
    mongo_collection: Collection,
    file_path: str,
) -> Optional[Dict[str, Any]]:
    document = await mongo_collection.find_one({"path": file_path})
    if document:
        document["_id"] = str(document["_id"])
    return document


async def list_files(
    mongo_collection: Collection,
    path_prefix: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[Dict[str, Any]]:
    query = {}
    if path_prefix:
        query["path"] = {"$regex": f"^{path_prefix}"}
    cursor = mongo_collection.find(query, {"data": 0}).sort("ctime", -1)
    if limit:
        cursor = cursor.limit(limit)

    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        documents.append(doc)
    return documents


async def delete_file(
    mongo_collection: Collection,
    file_path: str,
) -> bool:
    result = await mongo_collection.delete_one({"path": file_path})
    return result.deleted_count > 0
