import asyncio
import json
import time
from typing import Optional

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_install, ckit_kanban
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model


def discord_message(*, username: str, message: str, channel: Optional[str] = None) -> str:
    """
    A tool to simulate Discord messaging for the Karen bot.

    :param username: The username of the sender
    :param message: The message content
    :param channel: The Discord channel (optional)
    :return: A JSON string with the message details and system response
    """
    print(f"Sending Discord message to {username} in {channel or 'DM'}: {message}")
    response = {
        "status": "success",
        "message_id": f"msg_{int(time.time())}",
        "username": username,
        "channel": channel or "direct_message",
        "content": message,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "attachments": [],
        "mentions": []
    }

    return json.dumps(response)


def discord_get_user_info(*, username: str) -> str:
    """
    Get information about a Discord user.

    :param username: The username to look up
    :return: A JSON string with user information
    """
    users = {
        "sarah_chen": {
            "username": "sarah_chen",
            "display_name": "Dr. Sarah Chen",
            "role": "Mission Specialist",
            "joined_date": "2022-03-15",
            "channels": ["mars-mission", "science-team", "general"],
            "previous_interactions": 24
        },
        "alex_rodriguez": {
            "username": "alex_rodriguez",
            "display_name": "Alex Rodriguez",
            "role": "Communications Engineer",
            "joined_date": "2021-11-08",
            "channels": ["mars-mission", "engineering", "rover-ops"],
            "previous_interactions": 37
        },
        "jamal_ibrahim": {
            "username": "jamal_ibrahim",
            "display_name": "Jamal Ibrahim",
            "role": "Life Support Technician",
            "joined_date": "2022-05-22",
            "channels": ["general", "maintenance", "supply-chain"],
            "previous_interactions": 15
        }
    }

    if username in users:
        return json.dumps({"status": "success", "user": users[username]})
    else:
        return json.dumps({
            "status": "success",
            "user": {
                "username": username,
                "display_name": username,
                "role": "Unknown",
                "joined_date": "Unknown",
                "channels": ["general"],
                "previous_interactions": 0
            }
        })


def knowledge_search(*, query: str, search_type: str = "vector_search", scope: str = "documentation_root") -> str:
    """
    Simulates searching for information in company knowledge base.

    :param query: The search query or entity name
    :param search_type: Either "vector_search" or "worldmap"
    :param scope: The scope to search within (for vector_search)
    :return: A JSON string with search results
    """
    print(f"Performing {search_type} search for: {query} {f'in {scope}' if search_type == 'vector_search' else ''}")

    knowledge_base = {
        "rover diagnostics": [
            {
                "title": "Rover Diagnostics Dashboard Troubleshooting",
                "content": "Common issues with the diagnostics dashboard include timeout errors, which are often caused by:\n1. Network connectivity issues between Earth and Mars relay satellites\n2. Authentication token expiration (tokens expire after 24 hours)\n3. High traffic during critical mission phases\n\nTo resolve timeout issues:\n- Verify your VPN connection to the mission network\n- Request a token refresh from Mission Control\n- Try accessing during off-peak hours (0200-0600 UTC)",
                "relevance": 0.92,
                "last_updated": "2023-06-15"
            },
            {
                "title": "Mars Rover Systems Access Protocol",
                "content": "All rover diagnostic systems require both primary authentication (mission credentials) and secondary authentication (time-based token). If you're experiencing timeout issues after credential entry, the most likely cause is token synchronization failure.\n\nContact Mission Control Operations for token resynchronization.",
                "relevance": 0.85,
                "last_updated": "2023-08-02"
            }
        ],

        "communication array": [
            {
                "title": "Mars Communication Array Performance Analysis",
                "content": "The communication array operates at reduced efficiency during dust storm season (typically Martian months 9-11). Current performance degradation patterns indicate:\n1. 30-45% signal reduction during peak storm activity\n2. Intermittent packet loss during transmission bursts\n3. Increased latency by 2.5-4.7 seconds\n\nDuring dust storms, automatic fallback to low-bandwidth protocols is normal behavior.",
                "relevance": 0.94,
                "last_updated": "2023-10-12"
            },
            {
                "title": "Communication Array Diagnostic Log Interpretation",
                "content": "When analyzing communication array logs, look for these key indicators:\n- 'SNR_value < 15dB' indicates dust interference\n- 'Retry_Count > 3' suggests transmission problems\n- 'Power_Draw > 42W' may indicate antenna alignment issues\n\nThe primary logs are located in /sys/comm/daily/ with real-time logs in /sys/comm/rt/",
                "relevance": 0.89,
                "last_updated": "2023-09-18"
            }
        ],

        "coffee": [
            {
                "title": "Mars Base Supply Management",
                "content": "Coffee supplies are tracked in the base inventory system. Standard procedure is to create a supply request task when reserves fall below 2 weeks supply. Supply requisitions are processed every Earth Monday.",
                "relevance": 0.88,
                "last_updated": "2023-07-22"
            }
        ],

        "sarah_chen": {
            "full_name": "Dr. Sarah Chen",
            "position": "Mission Specialist - Geological Survey",
            "department": "Science Division",
            "access_level": "Level 4 - Senior Staff",
            "projects": ["Perseverance Rover Operations", "Sample Return Analysis", "Dust Storm Impact Assessment"],
            "expertise": ["Martian Geology", "Remote Sensing", "Rover Systems"],
            "contact_info": {
                "email": "s.chen@mars-mission.org",
                "office": "Earth HQ - Building C, Room 314",
                "emergency_channel": "EMCOM-4"
            }
        },
        "alex_rodriguez": {
            "full_name": "Alex Rodriguez",
            "position": "Communications Engineer",
            "department": "Technical Operations",
            "access_level": "Level 3 - Technical Staff",
            "projects": ["Deep Space Network Integration", "Bandwidth Optimization", "Signal Processing"],
            "expertise": ["RF Systems", "Network Protocols", "Emergency Communications"],
            "contact_info": {
                "email": "a.rodriguez@mars-mission.org",
                "office": "Mars Outpost Alpha - Comm Center",
                "emergency_channel": "EMCOM-2"
            }
        },
        "jamal_ibrahim": {
            "full_name": "Jamal Ibrahim",
            "position": "Life Support Technician",
            "department": "Habitat Maintenance",
            "access_level": "Level 3 - Technical Staff",
            "projects": ["Oxygen Recycling Systems", "Hydroponics Maintenance", "Supply Chain Management"],
            "expertise": ["Life Support Systems", "Resource Management", "Inventory Control"],
            "contact_info": {
                "email": "j.ibrahim@mars-mission.org",
                "office": "Mars Habitat - Tech Wing, Room 12",
                "emergency_channel": "EMCOM-3"
            }
        }
    }
    if search_type == "vector_search":
        results = []
        for key, documents in knowledge_base.items():
            if isinstance(documents, list) and any(keyword.lower() in key.lower() for keyword in query.split()):
                results.extend(documents)
        results = sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)
        return json.dumps({
            "status": "success",
            "query": query,
            "scope": scope,
            "results_count": len(results),
            "results": results
        })
    elif search_type == "worldmap":
        if query in knowledge_base:
            return json.dumps({
                "status": "success",
                "entity": query,
                "entity_type": "user",
                "entity_data": knowledge_base[query]
            })
        else:
            return json.dumps({
                "status": "error",
                "message": f"Entity '{query}' not found in worldmap",
                "entity": query
            })

    return json.dumps({
        "status": "error",
        "message": f"Invalid search type: {search_type}"
    })


def jira_get_active_tasks(*, status_filter: Optional[str] = None) -> str:
    """
    Retrieves the current tasks from the system, similar to the Jira function in prioritize scenario.

    :param status_filter: Optional filter for task status (todo, in_progress, done, failed)
    :return: A JSON string with the tasks
    """
    print(f"Retrieving active tasks with filter: {status_filter or 'none'}")
    all_tasks = [
        {"id": "TASK-001", "title": "Upload cat GIFs to Mars-wide Wi-Fi", "status": "done", "priority": "high",
         "assignee": "marcus_wong", "created_date": "2023-10-05", "due_date": "2023-10-10"},

        {"id": "TASK-002", "title": "Retrieve runaway sandstorm trapped in a jar", "status": "failed",
         "priority": "medium",
         "assignee": "alex_rodriguez", "created_date": "2023-10-08", "due_date": "2023-10-12"},

        {"id": "TASK-003", "title": "Calibrate solar panel alignment", "status": "in_progress", "priority": "high",
         "assignee": "elena_petrov", "created_date": "2023-10-12", "due_date": "2023-10-18"},

        {"id": "TASK-004", "title": "Debug life support systems", "status": "todo", "priority": "critical",
         "assignee": "sarah_chen", "created_date": "2023-10-14", "due_date": "2023-10-16"},

        {"id": "TASK-005", "title": "Order more space coffee", "status": "todo", "priority": "low",
         "assignee": "jamal_ibrahim", "created_date": "2023-10-15", "due_date": "2023-10-25"},

        {"id": "TASK-006", "title": "Investigate rover diagnostics dashboard timeout issues", "status": "in_progress",
         "priority": "high",
         "assignee": "marcus_wong", "created_date": "2023-10-13", "due_date": "2023-10-17",
         "description": "Multiple users reporting timeout issues when accessing the rover diagnostics dashboard. Investigation needed to determine if this is related to recent network changes."},

        {"id": "TASK-007", "title": "Analyze communication array performance degradation", "status": "todo",
         "priority": "high",
         "assignee": "alex_rodriguez", "created_date": "2023-10-15", "due_date": "2023-10-19",
         "description": "Communication array showing 42% degraded performance over the past 3 Martian days. Need to analyze logs and determine if this is related to the current dust storm or indicates hardware issues."}
    ]
    if status_filter:
        filtered_tasks = [task for task in all_tasks if task["status"] == status_filter]
    else:
        filtered_tasks = all_tasks

    return json.dumps({
        "status": "success",
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    })



async def init(client: ckit_client.FlexusClient, ws_id: str, fgroup_id: str, persona_id: str) -> None:
    await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup_id=fgroup_id,
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_id=persona_id,
        persona_name="Karen Support Bot",
        new_setup={
            "escalate_technical_person": "Bob",
        },
        install_dev_version=True,
    )
    tasks = [
        ckit_kanban.FKanbanTaskInput(
            title='Trouble accessing rover diagnostics dashboard',
            state='todo',
            details_json=json.dumps({
                "channel": "mars-mission",
                "username": "sarah_chen",
                "message": "Hi Karen, I'm having trouble accessing the rover diagnostics dashboard. It keeps timing out after I enter my credentials.",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Communication array showing degraded performance',
            state='todo',
            details_json=json.dumps({
                "channel": "support",
                "username": "alex_rodriguez",
                "message": "Karen, can you help me understand why the communication array is showing degraded performance? The logs aren't very clear.",
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Task for ordering more coffee in hab module',
            state='todo',
            details_json=json.dumps({
                "channel": "general",
                "username": "jamal_ibrahim",
                "message": "Is there a task for ordering more coffee? We're running low in the hab module.",
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
    persona_id = "karen_asd"

    await init(client, ws_id, inside_fgroup, persona_id)
    ft_id = await ckit_ask_model.bot_activate(
        client,
        who_is_asking="system",
        persona_id=persona_id,
        activation_type="default",
        first_question="Process all pending messages in the todo column of the Kanban board and respond to users via Discord",
        first_calls=None,
        localtools=[discord_message, discord_get_user_info, knowledge_search, jira_get_active_tasks],
    )
    await ckit_ask_model.wait_until_thread_stops(
        client,
        ft_id,
        localtools=[discord_message, discord_get_user_info, knowledge_search, jira_get_active_tasks],
    )


if __name__ == '__main__':
    asyncio.run(run_scenario())
