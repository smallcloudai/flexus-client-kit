import asyncio
import logging
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.boss import boss_install

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = "0.1.0"
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

ACCENT_COLOR = "#8B4513"


# Define the boss-specific tools
BOSS_APPROVE_TASK_TOOL = ckit_cloudtool.CloudTool(
    name="boss_approve_task",
    description="Approve a task from a colleague bot, optionally with modifications",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to approve"
            },
            "modification": {
                "type": "string",
                "description": "Optional modifications or instructions to add to the approved task"
            }
        },
        "required": ["task_id"]
    },
)

BOSS_REJECT_TASK_TOOL = ckit_cloudtool.CloudTool(
    name="boss_reject_task",
    description="Reject a task from a colleague bot with a reason",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to reject"
            },
            "reason": {
                "type": "string",
                "description": "Reason for rejecting the task"
            }
        },
        "required": ["task_id"]
    },
)


TOOLS = [
    BOSS_APPROVE_TASK_TOOL,
    BOSS_REJECT_TASK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]


class BossApprovalHandler:
    """Handler for boss approval/rejection operations"""

    def __init__(self, personal_mongo):
        self.personal_mongo = personal_mongo

    async def approve_task(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        """
        Approve a task from a colleague bot, optionally with modifications.
        """
        task_id = model_produced_args.get("task_id", "")
        modification = model_produced_args.get("modification", "")

        if not task_id:
            return "Error: task_id is required"

        logger.info(f"boss_approve_task called: task_id={task_id}, modification={modification}")

        # TODO: Implement task approval logic
        # This should:
        # 1. Validate that the task_id exists and is pending approval
        # 2. If modification is provided, update the task with the new instructions
        # 3. Mark the task as approved in the system
        # 4. Notify the requesting bot that their task has been approved
        # 5. Possibly move the task to a different kanban column (e.g., from "pending_approval" to "approved")

        result = f"✅ Task {task_id} approved"
        if modification:
            result += f" with modifications: {modification}"

        # TODO: Actually update the task status in the database/kanban system
        # Example implementation might look like:
        # - Query the task from MongoDB: task = await self.personal_mongo.find_one({"task_id": task_id})
        # - Update task status: await self.personal_mongo.update_one(
        #     {"task_id": task_id},
        #     {"$set": {"status": "approved", "modifications": modification, "approved_ts": time.time()}}
        # )
        # - Send notification to the requesting bot via their kanban inbox or direct message
        # - Update any related workflow state

        return result

    async def reject_task(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        """
        Reject a task from a colleague bot with a reason.
        """
        task_id = model_produced_args.get("task_id", "")
        reason = model_produced_args.get("reason", "")

        if not task_id:
            return "Error: task_id is required"

        logger.info(f"boss_reject_task called: task_id={task_id}, reason={reason}")

        # TODO: Implement task rejection logic
        # This should:
        # 1. Validate that the task_id exists and is pending approval
        # 2. Mark the task as rejected in the system
        # 3. If reason is provided, attach it to the rejection record
        # 4. Notify the requesting bot that their task has been rejected with the reason
        # 5. Possibly move the task to a different kanban column (e.g., from "pending_approval" to "rejected")
        # 6. Update any related metrics or logs

        result = f"❌ Task {task_id} rejected"
        if reason:
            result += f". Reason: {reason}"

        # TODO: Actually update the task status in the database/kanban system
        # Example implementation might look like:
        # - Query the task from MongoDB: task = await self.personal_mongo.find_one({"task_id": task_id})
        # - Update task status: await self.personal_mongo.update_one(
        #     {"task_id": task_id},
        #     {"$set": {"status": "rejected", "reason": reason, "rejected_ts": time.time()}}
        # )
        # - Send notification to the requesting bot via their kanban inbox
        # - Log the rejection for audit purposes

        return result


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.boss_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.get_mongodb_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    boss_handler = BossApprovalHandler(personal_mongo)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(BOSS_APPROVE_TASK_TOOL.name)
    async def toolcall_approve_task(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await boss_handler.approve_task(toolcall, model_produced_args)

    @rcx.on_tool_call(BOSS_REJECT_TASK_TOOL.name)
    async def toolcall_reject_task(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await boss_handler.reject_task(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

    rcx.ready()

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group = ckit_bot_exec.parse_bot_group_argument()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=boss_main_loop,
        inprocess_tools=TOOLS,
    ))


if __name__ == "__main__":
    main()
