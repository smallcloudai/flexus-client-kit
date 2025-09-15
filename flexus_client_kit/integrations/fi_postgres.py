import asyncio
import logging
import re
import time
from typing import Dict, Any, Optional
from pymongo.collection import Collection

from flexus_client_kit import ckit_cloudtool, ckit_mongo

logger = logging.getLogger("fi_postgres")


POSTGRES_TOOL = ckit_cloudtool.CloudTool(
    name="postgres",
    description="Execute PostgreSQL queries via psql command line utility",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute, if there's data then it's on your to escape it according to SQL rules. This does not go via shell so no shell escape necessary."
            }
        },
        "required": ["query"]
    },
)

_STRIP_SQL_LITERALS = re.compile(r"""
    ('(?:''|[^'])*')                             |  # single-quoted strings
    ("(?:""|[^"])*")                             |  # double-quoted identifiers/strings
    (\$([A-Za-z_][A-Za-z_0-9]*)?\$.*?\$\4?\$)    |  # $tag$...$tag$ or $$...$$
    (--[^\n]*)                                   |  # line comments
    (/\*.*?\*/)                                     # block comments (non-nesting)
""", re.IGNORECASE | re.DOTALL | re.VERBOSE)

_WRITE_VERBS = re.compile(r"\b(?:INSERT|UPDATE|DELETE)\b", re.IGNORECASE)

def _is_write_sql(query: str) -> bool:
    cleaned = _STRIP_SQL_LITERALS.sub(" ", query)
    return bool(_WRITE_VERBS.search(cleaned))


class IntegrationPostgres:
    def __init__(self, personal_mongo: Optional[Collection] = None, save_to_mongodb_threshold_bytes: int = 100):
        self.personal_mongo = personal_mongo
        self.save_to_mongodb_threshold_bytes = save_to_mongodb_threshold_bytes

    async def execute_query(self, query: str, have_human_confirmation: bool) -> str:
        if _is_write_sql(query) and not have_human_confirmation:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="",
                confirm_command=query,
                confirm_explanation="Write operation, human confirmation needed.",
            )
        try:
            # psql -c "SET default_transaction_read_only = on;" -c "INSERT INTO hello_world (a, b) VALUES (1, 2);"
            cmd = ["psql", "--csv", "-c", query]
            logger.info("Running %s", query[:30])   # Maybe there is user data so we cut it short

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace').strip()
                return f"{error_msg}"

            result = stdout.decode('utf-8', errors='replace').strip()
            if not result:
                return "Query executed successfully"

            result_bytes = result.encode('utf-8')
            lines = result.split('\n')
            row_count = len(lines) - 1

            if len(result_bytes) > self.save_to_mongodb_threshold_bytes and self.personal_mongo is not None and len(lines) > 7:
                timestamp = str(int(time.time()))
                file_path = f"postgres/query_{timestamp}.csv"
                await ckit_mongo.store_file(self.personal_mongo, file_path, result_bytes)

                header_and_first_3 = '\n'.join(lines[:4])
                last_3 = '\n'.join(lines[-3:])

                preview = header_and_first_3 +  "\n...\n" + last_3

                explanation  = "Query executed successfully, in the preview below the first line is CSV headers, then first 3 lines, dot dot dot, and last 3 lines of data. There are %d lines of data total.\n" % (row_count,)
                explanation += "Full CSV is accessible via mongo_store() tool using path: %s\n\n" % (file_path,)
                return explanation + preview

            explanation = "Query executed successfully, first line is CSV headers, then %d lines of data, %d lines total:\n\n" % (row_count, row_count+1)
            return explanation + result

        except FileNotFoundError:
            return "Error: this integration relies on psql command line utility and it doesn't work"

        except Exception:
            logger.exception("Unexpected problem")
            return "Internal error, more information in the bot logs :/"

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        query = model_produced_args.get("query")
        if not query:
            return "Error: specify `query` parameter"
        return await self.execute_query(query, toolcall.confirmed_by_human)


if __name__ == "__main__":
    def regexp_test():
        read_only = """
        SELECT * FROM hello_world WHERE a IN (SELECT a FROM u);
        WITH s AS (SELECT 1) SELECT * FROM s;
        EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM hello_world;
        """
        read_write = """
        INSERT INTO hello_world SELECT * FROM u;
        WITH i AS (INSERT INTO hello_world (a, b) VALUES (1, 2) RETURNING *) SELECT * FROM i;
        UPDATE hello_world SET a = a + 1 WHERE a IN (SELECT a FROM u);
        DELETE FROM hello_world USING u WHERE hello_world.a = u.a;
        INSERT INTO hello_world (a, b) VALUES (1, 2) ON CONFLICT (a) DO UPDATE SET b = EXCLUDED.b;
        """
        for ro in read_only.split("\n"):
            assert not _is_write_sql(ro), f"Should be read-only: {ro}"
            assert not _is_write_sql(ro.strip()), f"Should be read-only: {ro.strip()}"
        for rw in read_write.split("\n"):
            if not rw.strip():
                continue
            assert _is_write_sql(rw), f"Should be write: {rw}"
            assert _is_write_sql(rw.strip()), f"Should be write: {rw.strip()}"

    async def test():
        regexp_test()
        postgres = IntegrationPostgres()
        result = await postgres.execute_query("SELECT 2*2;", have_human_confirmation=False)
        print("Test result:", result)

    asyncio.run(test())
