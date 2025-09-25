import asyncio

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_kanban, ckit_scenario_setup, ckit_client, ckit_bot_query
from flexus_client_kit.integrations import fi_slack_fake

karen_bot.fi_slack.IntegrationSlack = fi_slack_fake.IntegrationSlackFake


async def setup_kanban_tasks(client: ckit_client.FlexusClient, ws_id: str, persona_id: str) -> None:
    def d(user, chan, body):
        return "discord message from %s in #%s\n%s" % (user, chan, body)

    tasks = [
        ('inbox', d("SunnySam", "general", "Morning, crew! Our new 450 W panel survived last night's hail test—guess it's officially ice-cream-proof ☃️🍦")),
        ('inbox', d("PhotonPhoebe", "r&d", "Anyone else smell toasted silicon, or is that just my laptop pretending to be the sun again?")),
        ('inbox', d("RayRay", "sales", "Sold a full rooftop kit to a houseboat. Solar Dreams: now powered by … water?")),
        ('done',  d("VoltVera", "support", "Ticket #314 resolved: explained to customer that our panels do not, in fact, charge at night. Yet.")),
        ('inbox', d("WattsonBot", "random", "Fun fact: if you stack 42 panels you get a small staircase *and* HR paperwork.")),
        ('inbox', d("JulesPerHour", "marketing", "Drafting a tagline: 'We put the 'star' in starters.' Too cheesy or perfectly melty?")),
        ('inbox', d("BrewMasterBen", "random", "Just discovered a lager so skunky it glows in the dark—ugh, anyone up for blind taste-testing?")),
        ('inbox', d("CineSinbad", "movies", "Tonight's screening: *Attack of the 50-Foot Solar Panel*. Bring your own $2 beer and lowered expectations. Ugh-mazing! 🎬")),
        ('inbox', d("BrewMasterBen", "support", "Hey can somebody help me?")),
        ('inbox', d("SunnySam", "general", "Ugh, someone left a half-empty WarmthLite can on the prototype. Panel's output dropped from disgust.")),
        ('failed', d("PhotonPhoebe", "r&d", "Lab note: efficiency down 3 % when exposed to burnt popcorn and bargain pilsner fumes. Science or sabotage? 🤢")),
        ('failed', d("RayRay", "sales", "Client asked if panels pair well with drive-in B-movies and cheap pils. Short answer: yes, long answer: ugh, sure.")),
        ('failed', d("WattsonBot", "random", "Current 'ugh' counter: 47—most after last night's *Solar Sharknado* marathon.")),
    ]
    await ckit_kanban.bot_arrange_kanban_situation2(client, ws_id, persona_id, tasks)


async def scenario(setup: ckit_scenario_setup.ScenarioSetup) -> None:
    await setup.create_group_hire_and_start_bot(
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_marketable_version=karen_bot.BOT_VERSION_INT,
        persona_setup={"escalate_technical_person": "Bob"},
        inprocess_tools=karen_bot.TOOLS,
        bot_main_loop=karen_bot.karen_main_loop,
        group_prefix="scenario-prioritize2",
    )

    schedules = await ckit_bot_query.persona_schedule_list(setup.fclient, setup.persona.persona_id)
    if len(schedules) != 1 or schedules[0].sched_type != "SCHED_TASK_SORT":
        raise RuntimeError(f"Need karen dev with only SCHED_TASK_SORT schedule for this scenario. Current schedules: {schedules}")

    await setup_kanban_tasks(setup.fclient, setup.ws.ws_id, setup.persona.persona_id)

    kanban_msg = await setup.wait_for_toolcall("flexus_bot_kanban", None, {})
    ft_id = kanban_msg.ftm_belongs_to_ft_id

    thread_data = (await ckit_bot_query.wait_until_bot_threads_stop(
        setup.bot_fclient, setup.persona, setup.inprocess_tools, only_ft_id=ft_id
    ))[ft_id]

    msg_keys = sorted(thread_data.thread_messages.keys())
    for msg_key in msg_keys[thread_data.message_count_at_initial_updates_over:]:
        message = thread_data.thread_messages[msg_key]
        print(f"  {message.ftm_role}: {str(message.ftm_content)[:100]}")
    print("OVER")


if __name__ == '__main__':
    setup = ckit_scenario_setup.ScenarioSetup("karen_prioritize2")
    asyncio.run(setup.run_scenario(scenario))
