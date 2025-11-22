import asyncio
import io
import logging
import re
import time
from typing import Dict, Any, Optional
from pymongo.collection import Collection
import pandas as pd

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

_WRITE_VERBS = re.compile(r"\b(?:INSERT|UPDATE|DELETE|MERGE|CREATE|DROP|ALTER|TRUNCATE|COPY\s+FROM|VACUUM)\b", re.IGNORECASE)

_COMMAND_TAG = re.compile(r"^(INSERT|UPDATE|DELETE|SELECT|COPY|MOVE|FETCH|CREATE|DROP|ALTER|TRUNCATE|MERGE)\s+\d+", re.IGNORECASE)

def _is_write_sql(query: str) -> bool:
    cleaned = _STRIP_SQL_LITERALS.sub(" ", query)
    return bool(_WRITE_VERBS.search(cleaned))


class IntegrationPostgres:
    def __init__(self, personal_mongo: Optional[Collection] = None, save_to_mongodb_threshold_bytes: int = 5000):
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
            if len(result_bytes) > 100_000:
                return "Error: Result size exceeds 2MB limit. Please use more specific query with LIMIT or WHERE clauses."

            # Strip command tag from end if present (e.g., "UPDATE 1", "INSERT 0 5")
            # This happens with RETURNING clauses
            lines = result.split('\n')
            command_tag = None
            if lines and _COMMAND_TAG.match(lines[-1]):
                command_tag = lines[-1]
                result_for_parsing = '\n'.join(lines[:-1])
            else:
                result_for_parsing = result

            # Try to parse as CSV to properly count rows
            try:
                df = pd.read_csv(io.StringIO(result_for_parsing))
                row_count = len(df)

                if len(result_bytes) > self.save_to_mongodb_threshold_bytes and self.personal_mongo is not None and row_count > 6:
                    # If we have actual CSV data (not just command results like "DELETE 0")
                    timestamp = str(int(time.time()))
                    file_path = f"postgres/query_{timestamp}.csv"
                    await ckit_mongo.store_file(self.personal_mongo, file_path, result_for_parsing.encode('utf-8'))

                    first_3 = df.head(3).to_csv(index=False)
                    last_3 = df.tail(3).to_csv(index=False, header=False)
                    preview = first_3.strip() + "\n...\n" + last_3.strip()

                    explanation  = "Query executed successfully, in the preview below the first line is CSV headers, then first 3 lines, dot dot dot, and last 3 lines of data. There are %d lines of data total.\n" % (row_count,)
                    if command_tag:
                        explanation += "%s\n" % (command_tag,)
                    explanation += "Full CSV is accessible via mongo_store() tool using path: %s\n\n" % (file_path,)
                    return explanation + preview

                explanation = "Query executed successfully, first line is CSV headers, then %d lines of data:\n\n" % (row_count,)
                result_to_show = result_for_parsing
                if command_tag:
                    result_to_show += '\n' + command_tag
                return explanation + result_to_show

            except Exception:
                # Not CSV format (e.g., "DELETE 0", "UPDATE 5", etc.), just return as-is
                return "Query executed successfully:\n\n" + (result or "Query returned nothing")

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
