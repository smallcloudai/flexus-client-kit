import json
import gql
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from bson import Binary
from pymongo.collection import Collection

from flexus_client_kit import ckit_client

CHUNK_SIZE_THRESHOLD = 15 * 1024 * 1024  # 15MB in bytes
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks for safety


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
    existing_doc = await mongo_collection.find_one({"path": file_path}, {"ctime": 1, "is_chunked": 1})
    old_ctime = existing_doc["ctime"] if existing_doc else None
    if existing_doc:
        if existing_doc.get("is_chunked"):
            await mongo_collection.delete_many({"parent_path": file_path})
        await mongo_collection.delete_one({"path": file_path})

    t = time.time()
    if len(file_data) > CHUNK_SIZE_THRESHOLD:
        return await _store_chunked_file(mongo_collection, file_path, file_data, t, old_ctime)

    document = {
        "path": file_path,
        "ctime": old_ctime if old_ctime else t,
        "mtime": t,
        "size_bytes": len(file_data),
        "is_chunked": False,
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


async def _store_chunked_file(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
    mtime: float,
    old_ctime: Optional[float],
) -> str:
    if file_path.endswith(".json"):
        try:
            json_data = json.loads(file_data.decode("utf-8"))
            # If it's a list, we can chunk it intelligently
            if isinstance(json_data, list):
                return await _store_chunked_json_array(
                    mongo_collection, file_path, json_data, mtime, old_ctime
                )
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # Fall back to binary chunking

    return await _store_chunked_binary(
        mongo_collection, file_path, file_data, mtime, old_ctime
    )


async def _store_chunked_json_array(
    mongo_collection: Collection,
    file_path: str,
    json_array: List[Any],
    mtime: float,
    old_ctime: Optional[float],
) -> str:
    chunks = []
    current_chunk = []
    current_size = 0

    for item in json_array:
        item_json = json.dumps(item)
        item_size = len(item_json.encode("utf-8"))
        if current_size + item_size > CHUNK_SIZE and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [item]
            current_size = item_size
        else:
            current_chunk.append(item)
            current_size += item_size

    if current_chunk:
        chunks.append(current_chunk)

    metadata_doc = {
        "path": file_path,
        "ctime": old_ctime if old_ctime else mtime,
        "mtime": mtime,
        "size_bytes": sum(len(json.dumps(chunk).encode("utf-8")) for chunk in chunks),
        "is_chunked": True,
        "chunk_type": "json_array",
        "chunk_count": len(chunks),
        "total_items": len(json_array),
    }

    result = await mongo_collection.insert_one(metadata_doc)
    metadata_id = str(result.inserted_id)

    for i, chunk in enumerate(chunks):
        chunk_doc = {
            "parent_path": file_path,
            "parent_id": metadata_id,
            "chunk_index": i,
            "json": chunk,
        }
        await mongo_collection.insert_one(chunk_doc)

    return metadata_id


async def _store_chunked_binary(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
    mtime: float,
    old_ctime: Optional[float],
) -> str:
    chunks = []
    for i in range(0, len(file_data), CHUNK_SIZE):
        chunks.append(file_data[i:i + CHUNK_SIZE])

    metadata_doc = {
        "path": file_path,
        "ctime": old_ctime if old_ctime else mtime,
        "mtime": mtime,
        "size_bytes": len(file_data),
        "is_chunked": True,
        "chunk_type": "binary",
        "chunk_count": len(chunks),
    }

    result = await mongo_collection.insert_one(metadata_doc)
    metadata_id = str(result.inserted_id)

    for i, chunk in enumerate(chunks):
        chunk_doc = {
            "parent_path": file_path,
            "parent_id": metadata_id,
            "chunk_index": i,
            "data": Binary(chunk),
        }
        await mongo_collection.insert_one(chunk_doc)

    return metadata_id


async def retrieve_file(
    mongo_collection: Collection,
    file_path: str,
) -> Optional[Dict[str, Any]]:
    document = await mongo_collection.find_one({"path": file_path})
    if not document:
        return None

    document["_id"] = str(document["_id"])

    if document.get("is_chunked"):
        chunks_cursor = mongo_collection.find(
            {"parent_path": file_path},
            sort=[("chunk_index", 1)]
        )
        chunks = await chunks_cursor.to_list(length=None)

        if document.get("chunk_type") == "json_array":
            # Reassemble JSON array
            json_data = []
            for chunk in chunks:
                json_data.extend(chunk["json"])
            document["json"] = json_data
        else:
            # Reassemble binary data
            binary_chunks = []
            for chunk in chunks:
                binary_chunks.append(chunk["data"])
            document["data"] = b"".join(binary_chunks)

            # If it was originally JSON stored as binary, decode it
            if file_path.endswith(".json"):
                try:
                    json_data = json.loads(document["data"].decode("utf-8"))
                    document["json"] = json_data
                    del document["data"]
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass  # Keep as binary

    return document


async def list_files(
    mongo_collection: Collection,
    path_prefix: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[Dict[str, Any]]:
    query = {"path": {"$exists": True}}  # Only get main documents, not chunks
    if path_prefix:
        query["path"] = {"$regex": f"^{path_prefix}"}
    cursor = mongo_collection.find(
        query,
        {"data": 0}
    ).sort("ctime", -1)

    if limit:
        cursor = cursor.limit(limit)

    documents = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if doc.get("is_chunked"):
            doc["chunked"] = True
            doc["chunk_count"] = doc.get("chunk_count", 0)
        documents.append(doc)
    return documents


async def delete_file(
    mongo_collection: Collection,
    file_path: str,
) -> bool:
    doc = await mongo_collection.find_one({"path": file_path}, {"is_chunked": 1})
    if doc and doc.get("is_chunked"):
        await mongo_collection.delete_many({"parent_path": file_path})

    result = await mongo_collection.delete_one({"path": file_path})
    return result.deleted_count > 0


async def update_file(
    mongo_collection: Collection,
    file_path: str,
    file_data: bytes,
) -> str:
    t = time.time()
    existing_doc = await mongo_collection.find_one({"path": file_path}, {"ctime": 1, "is_chunked": 1, "_id": 1})
    
    if existing_doc:
        old_ctime = existing_doc.get("ctime", t)
        doc_id = existing_doc["_id"]
        if existing_doc.get("is_chunked") or len(file_data) > CHUNK_SIZE_THRESHOLD:
            await mongo_collection.delete_many({"parent_path": file_path})
            if len(file_data) > CHUNK_SIZE_THRESHOLD:
                await mongo_collection.delete_one({"_id": doc_id})
                return await _store_chunked_file(mongo_collection, file_path, file_data, t, old_ctime)
        update_doc = {
            "$set": {
                "mtime": t,
                "size_bytes": len(file_data),
                "is_chunked": False,
            }
        }
        if file_path.endswith(".json"):
            try:
                json_data = json.loads(file_data.decode("utf-8"))
                update_doc["$set"]["json"] = json_data
                update_doc["$unset"] = {"data": ""}
            except (json.JSONDecodeError, UnicodeDecodeError):
                update_doc["$set"]["data"] = Binary(file_data)
                update_doc["$unset"] = {"json": ""}
        else:
            update_doc["$set"]["data"] = Binary(file_data)
            update_doc["$unset"] = {"json": ""}
        
        result = await mongo_collection.update_one(
            {"_id": doc_id},
            update_doc
        )
        
        if result.modified_count > 0:
            return str(doc_id)
        else:
            return str(doc_id)
    
    else:
        return await store_file(mongo_collection, file_path, file_data)
