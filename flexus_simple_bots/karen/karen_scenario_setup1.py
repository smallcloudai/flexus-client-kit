import asyncio
import json

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_install, ckit_kanban
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model


async def init(client: ckit_client.FlexusClient, ws_id: str, fgroup_id: str, persona_id: str) -> None:
    await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup_id="innerplanets",
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
            title='Authorize Martian squirrel pizza fleet',
            state='input',
            details_json=json.dumps({
                "title": "Authorize Martian squirrel pizza fleet",
                "channel": "mars-habitat",
                "username": "commander",
                "message": "We need to authorize the squirrel pizza delivery fleet for Mars Base Alpha"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Install disco-ball sunrise in habitat dome',
            state='todo',
            details_json=json.dumps({
                "title": "Install disco-ball sunrise in habitat dome",
                "channel": "habitat-maintenance",
                "username": "morale-officer",
                "message": "Crew morale would improve with a disco-ball sunrise simulation in the main habitat dome"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Teach Curiosity to recite sarcastic haikus',
            state='todo',
            details_json=json.dumps({
                "title": "Teach Curiosity to recite sarcastic haikus",
                "channel": "rover-programming",
                "username": "ai-specialist",
                "message": "Let's upgrade Curiosity's AI to generate sarcastic haikus about Martian dust"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Inflate crater-trampoline for zero-G sports',
            state='inprogress',
            details_json=json.dumps({
                "title": "Inflate crater-trampoline for zero-G sports",
                "channel": "recreation",
                "username": "sports-coordinator",
                "message": "Converting Crater C-7 into a trampoline for low-gravity sports competitions"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Paint racing stripes on Olympus Mons',
            state='done',
            details_json=json.dumps({
                "title": "Paint racing stripes on Olympus Mons",
                "channel": "art-projects",
                "username": "landscape-artist",
                "message": "Successfully completed painting racing stripes on the east face of Olympus Mons"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Upload cat GIFs to Mars-wide Wi-Fi',
            state='done',
            details_json=json.dumps({
                "title": "Upload cat GIFs to Mars-wide Wi-Fi",
                "channel": "communications",
                "username": "network-admin",
                "message": "Successfully uploaded 10TB of cat GIFs to the Mars-wide Wi-Fi entertainment system"
            })
        ),
        ckit_kanban.FKanbanTaskInput(
            title='Retrieve runaway sandstorm trapped in a jar',
            state='failed',
            details_json=json.dumps({
                "title": "Retrieve runaway sandstorm trapped in a jar",
                "channel": "meteorology",
                "username": "storm-chaser",
                "message": "Attempted to capture a miniature sandstorm in a specimen jar for study",
                "difficulty": "extreme",
                "reason": "sandstorm too fast"
            })
        ),
    ]
    await ckit_kanban.bot_arrange_kanban_situation(client, ws_id, persona_id, tasks)


# scenario = "check documentation to work with, check setup status, => tell user capabilitites and first step setting up"

async def run_scenario():
    client = ckit_client.FlexusClient("scenario", api_key="sk_alice_123456")
    ws_id = "solarsystem"
    inside_fgroup = "innerplanets"
    persona_id = "karen1337"
    await init(client, ws_id, inside_fgroup, persona_id)
    # UI logic: no thread today => create thread
    ft_id = await ckit_ask_model.bot_activate(
        client,
        who_is_asking="karen_scenario_setup1",
        persona_id=persona_id,
        activation_type="setup",
        # first_question="See there any gifs in tasks?",
        first_question="Go ahead and call file_jira_issue with hello world inside",
        first_calls=None,
        localtools=None,
    )
    ass = await ckit_ask_model.wait_until_thread_stops(
        client,
        ft_id,
        localtools=[]
    )
    print("OVER", ass)


if __name__ == '__main__':
    asyncio.run(run_scenario())
