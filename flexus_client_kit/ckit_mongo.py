import json
import gql
import time
from typing import Dict, Any, List, Optional
from bson import Binary
from pymongo.collection import Collection

from flexus_client_kit import ckit_client


MAX_FILE_SIZE = 2 * 1024 * 1024


async def mongo_fetch_creds(
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


async def mongo_store_file(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
    ttl: int,
) -> str:
    assert ttl > 0
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError(f"File size {len(file_data)} exceeds maximum {MAX_FILE_SIZE}")
    existing_doc = await mongo_collection.find_one({"path": file_path}, {"_id": 1})
    if existing_doc:
        raise ValueError(f"File already exists at path: {file_path}")
    t = time.time()
    document = {
        "path": file_path,
        "mon_ctime": t,
        "mon_mtime": t,
        "mon_size": len(file_data),
        "mon_expires_ts": t + ttl,
    }

    if file_path.endswith(".json"):
        json_data = json.loads(file_data.decode("utf-8"))
        document["json"] = json_data
    else:
        document["data"] = Binary(file_data)

    result = await mongo_collection.insert_one(document)
    return str(result.inserted_id)


async def mongo_overwrite(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
    ttl: int,
) -> str:
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError(f"File size {len(file_data)} exceeds maximum {MAX_FILE_SIZE}")
    t = time.time()
    existing_doc = await mongo_collection.find_one({"path": file_path}, {"mon_ctime": 1, "_id": 1})
    if existing_doc:
        doc_id = existing_doc["_id"]
        update_doc = {
            "$set": {
                "mon_mtime": t,
                "mon_size": len(file_data),
                "mon_expires_ts": t + ttl,
            }
        }
        if file_path.endswith(".json"):
            json_data = json.loads(file_data.decode("utf-8"))
            update_doc["$set"]["json"] = json_data
            update_doc["$unset"] = {"data": ""}
        else:
            update_doc["$set"]["data"] = Binary(file_data)
            update_doc["$unset"] = {"json": ""}
        await mongo_collection.update_one({"_id": doc_id}, update_doc)
        return str(doc_id)
    return await mongo_store_file(mongo_collection, file_path, file_data, ttl)


async def mongo_retrieve_file(
    mongo_collection: Collection,
    file_path: str,
) -> Optional[Dict[str, Any]]:
    document = await mongo_collection.find_one({"path": file_path})
    if not document:
        return None

    if "mon_new_location" in document:
        return await mongo_retrieve_file(mongo_collection, document["mon_new_location"])

    document["_id"] = str(document["_id"])

    # XXX remove after 20260101, leftovers after rename
    if "mon_ctime" not in document and "ctime" in document:
        document["mon_ctime"] = document["ctime"]
    if "mon_mtime" not in document and "mtime" in document:
        document["mon_mtime"] = document["mtime"]
    if "mon_size" not in document and "size_bytes" in document:
        document["mon_size"] = document["size_bytes"]
    # /XXX

    return document


async def mongo_ls(
    mongo_collection: Collection,
    path_prefix: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    query = {"mon_archived": {"$ne": True}}
    if path_prefix:
        query["path"] = {"$regex": f"^{path_prefix}"}
    cursor = mongo_collection.find(query, {"data": 0, "json": 0}).sort("mon_ctime", -1)
    if limit:
        cursor = cursor.limit(limit)
    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])

        # XXX remove after 20260101, leftovers after rename
        if "mon_ctime" not in doc and "ctime" in doc:
            doc["mon_ctime"] = doc["ctime"]
        if "mon_mtime" not in doc and "mtime" in doc:
            doc["mon_mtime"] = doc["mtime"]
        if "mon_size" not in doc and "size_bytes" in doc:
            doc["mon_size"] = doc["size_bytes"]
        # /XXX

        documents.append(doc)
    return documents


async def mongo_ls_subdir(
    mongo_collection: Collection,
    path: str,
) -> List[Dict[str, Any]]:
    path_filter = {"path": {"$exists": True, "$ne": None}, "mon_archived": {"$ne": True}}
    if path:
        path_filter["path"] = {"$regex": f"^{path.rstrip('/')}/"}
    cursor = mongo_collection.find(path_filter, {"path": 1, "mon_ctime": 1, "mon_mtime": 1, "mon_size": 1, "ctime": 1, "mtime": 1, "size_bytes": 1, "_id": 0}).sort([("mon_mtime", -1), ("mtime", -1)])
    docs = await cursor.to_list(length=None)
    items = {}
    for doc in docs:
        relative = doc["path"][len(path.rstrip('/')) + 1:] if path else doc["path"]
        immediate = relative.split('/')[0]
        current_path = f"{path.rstrip('/')}/{immediate}" if path else immediate

        # XXX remove after 20260101, leftovers after rename
        doc_ctime = doc.get("mon_ctime") or doc.get("ctime") or 0.0
        doc_mtime = doc.get("mon_mtime") or doc.get("mtime") or 0.0
        doc_size = doc.get("mon_size") or doc.get("size_bytes") or 0
        # /XXX

        if '/' in relative:
            if current_path not in items:
                items[current_path] = {"path": current_path, "mime_type": "subdir", "mon_ctime": doc_ctime, "mon_mtime": doc_mtime, "mon_size": doc_size}
            else:
                items[current_path]["mon_ctime"] = min(items[current_path]["mon_ctime"], doc_ctime)
                items[current_path]["mon_mtime"] = max(items[current_path]["mon_mtime"], doc_mtime)
                items[current_path]["mon_size"] += doc_size
        else:
            items[current_path] = {"path": doc["path"], "mime_type": "", "mon_ctime": doc_ctime, "mon_mtime": doc_mtime, "mon_size": doc_size}
    return list(items.values())


async def mongo_mv(
    mongo_collection: Collection,
    old_path: str,
    new_path: str,
) -> bool:
    doc = await mongo_collection.find_one({"path": old_path})
    if not doc:
        return False
    doc["_id"] = None
    doc["path"] = new_path
    await mongo_collection.insert_one(doc)
    t = time.time()
    await mongo_collection.update_one(
        {"path": old_path},
        {"$set": {
            "mon_new_location": new_path,
            "mon_mtime": t,
            "mon_archived": True,
            "mon_expires_ts": t + 2*86400
        },
        "$unset": {
            "data": "",
            "json": ""
        }}
    )
    return True


async def mongo_rm(
    mongo_collection: Collection,
    file_path: str,
) -> bool:
    t = time.time()
    result = await mongo_collection.update_one(
        {"path": file_path},
        {"$set": {
            "mon_archived": True,
            "mon_expires_ts": t + 2*86400
        }}
    )
    return result.modified_count > 0
