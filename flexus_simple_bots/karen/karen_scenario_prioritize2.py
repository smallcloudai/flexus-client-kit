import asyncio

from flexus_simple_bots.karen import karen_bot
from flexus_client_kit import ckit_bot_install, ckit_kanban
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_ask_model


async def init(client: ckit_client.FlexusClient, ws_id: str, fgroup_id: str, persona_id: str) -> None:
    await ckit_bot_install.bot_install_from_marketplace(
        client,
        ws_id=ws_id,
        inside_fgroup=fgroup_id,
        persona_marketable_name=karen_bot.BOT_NAME,
        persona_id=persona_id,
        persona_name="Karen Superbot 3",
        new_setup={
            "escalate_technical_person": "Bob",
        },
        install_dev_version=True,
    )
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


async def run_scenario():
    client = ckit_client.FlexusClient("scenario", api_key="sk_alice_123456")
    ws_id = "solarsystem"
    inside_fgroup = "innerplanets"
    persona_id = "karen1337"
    await init(client, ws_id, inside_fgroup, persona_id)
    quit()

    ft_id = await ckit_ask_model.bot_activate(
        client,
        who_is_asking="karen_scenario_prioritize2",
        persona_id=persona_id,
        activation_type="default",
        first_question="Check out Inbox, move trash to Failed column, move several one or several messages that look like you have to answer them to Todo.",
        first_calls=None,
    )
    ass = await ckit_ask_model.wait_until_thread_stops(
        client,
        ft_id,
        localtools=[],
    )
    print("OVER", ass)


if __name__ == '__main__':
    asyncio.run(run_scenario())
