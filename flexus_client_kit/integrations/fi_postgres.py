import asyncio
import logging
from typing import Dict, Any

from flexus_client_kit import ckit_cloudtool

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


class IntegrationPostgres:
    async def execute_query(self, query: str) -> str:
        try:
            cmd = ["psql", "-c", query]
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
            return result if result else "Query executed successfully"

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
        return await self.execute_query(query)


if __name__ == "__main__":
    async def test():
        postgres = IntegrationPostgres()
        result = await postgres.execute_query("SELECT 2*2;")
        print("Test result:", result)
    asyncio.run(test())
