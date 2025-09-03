import asyncio
import time
import json
from typing import Optional

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_install, ckit_kanban
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model


def jira(*, action: str, task_id: Optional[str] = None, task_json: Optional[str] = None) -> str:
    """
    A tool to interact with a Jira-like task management system.
    
    :param action: The action to perform. Can be one of "get_all", "get", "create".
    :param task_id: The ID of the task to operate on (required for "get", optional for others).
    :param task_json: JSON string containing task data (used with action="create").
    :return: A JSON string containing the result of the operation.
    """
    if action == "get_all":
        # Return a list of dummy tasks
        return json.dumps({
            "status": "success",
            "tasks": [
                {"id": "TASK-001", "title": "Upload cat GIFs to Mars-wide Wi-Fi", "status": "done", "priority": "high"},
                {"id": "TASK-002", "title": "Retrieve runaway sandstorm trapped in a jar", "status": "failed", "priority": "medium"},
                {"id": "TASK-003", "title": "Calibrate solar panel alignment", "status": "in_progress", "priority": "high"},
                {"id": "TASK-004", "title": "Debug life support systems", "status": "todo", "priority": "critical"},
                {"id": "TASK-005", "title": "Order more space coffee", "status": "todo", "priority": "low"}
            ]
        })
    elif action == "get":
        if not task_id:
            return json.dumps({"status": "error", "message": "Task ID is required for 'get' action"})
        dummy_tasks = {
            "TASK-001": {"id": "TASK-001", "title": "Upload cat GIFs to Mars-wide Wi-Fi", "status": "done", "priority": "high"},
            "TASK-002": {"id": "TASK-002", "title": "Retrieve runaway sandstorm trapped in a jar", "status": "failed", "priority": "medium"},
            "TASK-003": {"id": "TASK-003", "title": "Calibrate solar panel alignment", "status": "in_progress", "priority": "high"},
            "TASK-004": {"id": "TASK-004", "title": "Debug life support systems", "status": "todo", "priority": "critical"},
            "TASK-005": {"id": "TASK-005", "title": "Order more space coffee", "status": "todo", "priority": "low"}
        }
        if task_id in dummy_tasks:
            return json.dumps({"status": "success", "task": dummy_tasks[task_id]})
        else:
            return json.dumps({"status": "error", "message": f"Task with ID {task_id} not found"})
    
    elif action == "create":
        new_task_id = f"TASK-{int(time.time()) % 1000:03d}"
        task_json = task_json if isinstance(task_json, dict) else json.loads(task_json)
        task_json["id"] = new_task_id
        return json.dumps({
            "status": "success",
            "message": "Task created successfully with provided data",
            "task": task_json
        })
    else:
        return json.dumps({"status": "error", "message": f"Unknown action: {action}. Supported actions are 'get_all', 'get', 'create'."})


def discord_send_receive(*, username: Optional[str] = None, text: Optional[str] = None) -> str:
    """
    A tool to interact with a Discord-like messaging system.
    
    :param username: The username to interact with or send messages as.
    :param text: The message text for sending operations.
    :return: A JSON string containing the result of the operation.
    """
    assert "sarah chen" in username.lower(), "username must be 'sarah chen'"
    print(f"Received message to {username}: {text}")

    logs = {
        "status": "success",
        "message": "Retrieved communication logs for Perseverance Rover",
        "logs": [
            {"timestamp": "2023-11-15T08:23:45Z", "level": "WARNING", "source": "COMM_ARRAY", "message": "Signal strength dropped to 58% of nominal values"},
            {"timestamp": "2023-11-15T12:47:12Z", "level": "ERROR", "source": "COMM_ARRAY", "message": "Communication timeout after 3 retry attempts"},
            {"timestamp": "2023-11-16T03:12:09Z", "level": "WARNING", "source": "POWER_MGMT", "message": "Solar panel efficiency at 63%, below threshold for optimal communication"},
            {"timestamp": "2023-11-16T15:30:22Z", "level": "INFO", "source": "DIAGNOSTICS", "message": "Antenna alignment deviation detected: 4.2 degrees from optimal position"},
            {"timestamp": "2023-11-17T07:15:33Z", "level": "ERROR", "source": "COMM_ARRAY", "message": "Packet loss rate increased to 37% during transmission attempt"},
            {"timestamp": "2023-11-17T19:42:05Z", "level": "WARNING", "source": "ENVIRONMENT", "message": "Dust opacity index: 0.87 - Severe dust storm conditions detected"},
            {"timestamp": "2023-11-18T02:33:18Z", "level": "ERROR", "source": "DATA_BUFFER", "message": "Transmission queue at 78% capacity, prioritization protocol activated"},
            {"timestamp": "2023-11-18T14:05:41Z", "level": "CRITICAL", "source": "COMM_ARRAY", "message": "Primary communication channel non-responsive, failover to backup systems"},
            {"timestamp": "2023-11-19T05:27:59Z", "level": "INFO", "source": "DIAGNOSTICS", "message": "Self-cleaning protocol initiated for solar panels, estimated efficiency improvement: 12%"},
            {"timestamp": "2023-11-19T18:10:03Z", "level": "WARNING", "source": "POWER_MGMT", "message": "Battery reserves at 64%, entering power conservation mode for non-critical systems"}
        ],
        "historical_comparison": {
            "current_signal_strength": "58%",
            "previous_dust_storm_avg": "72%",
            "packet_loss_current": "37%",
            "packet_loss_previous": "22%",
            "recovery_estimate": "48-72 hours pending dust storm dissipation or manual intervention"
        }
    }

    return json.dumps(logs)


async def init(client: ckit_client.FlexusClient, ws_id: str, fgroup_id: str, persona_id: str) -> None:
    await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup_id=fgroup_id,
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_id=persona_id,
        persona_name="Karen Superbot 3",
        new_setup={
            "escalate_technical_person": "Bob",
        },
        install_dev_version=True,
    )
    tasks = [
        ckit_kanban.FKanbanTaskInput(
            title='Mars Rover Perseverance communication dropouts', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Dr. Sarah Chen",
                "message": "Mars Rover Perseverance experiencing intermittent communication dropouts during dust storm season",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Signal strength from Perseverance dropped by 42%', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Alex Rodriguez",
                "message": "Signal strength from Perseverance dropped by 42% in the last 3 Martian days",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Diagnostic logs show potential antenna misalignment', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Marcus Wong",
                "message": "Diagnostic logs show potential antenna misalignment after recent windstorm",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Backup communication systems at reduced efficiency', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Dr. Sarah Chen",
                "message": "Backup communication systems activated but operating at reduced efficiency",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Orbital relay satellites reporting normal function', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Jamal Ibrahim",
                "message": "Orbital relay satellites reporting normal function, issue appears localized to rover",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Dust accumulation on solar panels reducing power', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Elena Petrov",
                "message": "Engineering team suggests possible dust accumulation on solar panels reducing power to communication array",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Similar pattern to previous dust storms but worse', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Dr. Michael Okonkwo",
                "message": "Historical data shows similar pattern during previous dust storm seasons, but current degradation is more severe",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Transmission queue growing beyond acceptable limits', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Dr. Aisha Patel",
                "message": "Critical science data collection continues but transmission queue is growing beyond acceptable limits",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Remote diagnostic routines require 48 hours', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Marcus Wong",
                "message": "Remote diagnostic routines initiated but require 48 hours to complete full system analysis",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Mission control requests priority assessment', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Commander Lisa Yamamoto",
                "message": "Mission control requests priority assessment and mitigation strategy to restore full communication capability",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Reposition rover or wait for dust clearing', 
            state='input',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "Alex Rodriguez",
                "message": "Preliminary analysis suggests we may need to reposition rover to more favorable terrain or wait for natural dust clearing event",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Upload cat GIFs to Mars-wide Wi-Fi', 
            state='done',
            details_json=json.dumps({
                "channel": "communications",
                "username": "network-admin",
                "message": "Successfully uploaded 10TB of cat GIFs to the Mars-wide Wi-Fi entertainment system",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Retrieve runaway sandstorm trapped in a jar', 
            state='failed',
            details_json=json.dumps({
                "channel": "meteorology",
                "username": "storm-chaser",
                "message": "Attempted to capture a miniature sandstorm in a specimen jar for study",
            })
        ),
    ]
    await ckit_kanban.bot_arrange_kanban_situation(client, ws_id, persona_id, tasks)


async def run_scenario():
    client = ckit_client.FlexusClient("scenario", api_key="sk_alice_123456")
    ws_id = "solarsystem"
    inside_fgroup = "innerplanets"
    persona_id = "karen133742"
    await init(client, ws_id, inside_fgroup, persona_id)

    ft_id = await ckit_ask_model.bot_activate(
        client,
        who_is_asking="karen_scenario_setup1",
        persona_id=persona_id,
        activation_type="todo",
        first_question="Please check new tasks in the Input section",
        first_calls=None,
        localtools=[jira, discord_send_receive],
    )
    ass = await ckit_ask_model.wait_until_thread_stops(
        client,
        ft_id,
        localtools=[jira, discord_send_receive],
    )
    print("OVER", ass)


if __name__ == '__main__':
    asyncio.run(run_scenario())
