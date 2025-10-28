Instructions on how to improve existing bots or write new bots for Flexus, an agent orchestrator.


Flexus Client Kit (ckit)
------------------------

fi_discord.py
fi_gmail.py
fi_mongo_store.py
fi_report.py
fi_slack.py

ckit_ask_model.py
ckit_bot_exec.py
ckit_bot_install.py
ckit_client.py
ckit_cloudtool.py
ckit_edoc.py
ckit_expert.py
ckit_kanban.py
ckit_localtool.py
ckit_logs.py
ckit_mongo.py
ckit_passwords.py
ckit_schedule.py
ckit_service_exec.py
ckit_shutdown.py
ckit_utils.py
gql_utils.py


What Files Define a Bot?
------------------------

NAME_bot.py        -- the file to run a bot
NAME_prompts.py    -- prompts live in a separate file
NAME_install.py    -- installation script, uses _bot and _prompts to construct a marketplace record
NAME-1024x1536.jpg -- detailed marketplace picture under 0.3M
NAME-256x256.png   -- small avatar picture with either transparent or white background


Kanban Board
------------

Flexus bots designed to perform work, independent of user/admin. The speed that new
tasks are coming is independent of how fast the bot can resolve them. Each bot has a
kanban board with 'inbox' column that receives new tasks.

On schedule (like "every 5 minutes") the bot gets activated (starts a chat) and
prioritizes the inbox tasks by moving them into 'todo' column by calling flexus_bot_kanban(),
potentially joining several tasks into one todo task.

Scheduler automatically moves tasks from 'todo' to 'inprogress' and activates the
bot (starts a chat), keeping an eye on how many tasks can run simultaneously (usually 3-5).

Once the bot decides it has finished with the assigned task, it calls flexus_bot_kanban() to
resolve the task, that's how tasks get into the 'done' column.

The kanban board is visible to the user in Flexus web UI.


Schedule
--------

Human can talk to a bot, but mostly this platform is about completing work autonomously.

NAME_install.py has `marketable_schedule` among other things, it typically has SCHED_TASK_SORT to
start sorting inbox, and SCHED_TODO to get assigned a single task from todo column and work on it.
But anything can be scheduled, such as writing reports daily, or rewriting strategy weekly.

Think of those as launchers, what kind of job the bot needs to perform on schedule?


Messengers
----------

Maybe at some point there will be a UI, but today Flexus bots only have chat interface
within Flexus web UI, and you can talk to them via messengers.

Any incoming messages usually go to inbox, or if messenger's thread has captured a
Flexus thread, then the messsage goes directly into the captured thread in the Flexus
database. Messenger's code does the checking on where to put it.

flexus_client_kit/integrations/fi_slack.py    -- slack is full-featured
flexus_client_kit/integrations/fi_discord.py  -- thread creation is weird
flexus_client_kit/integrations/fi_telegram.py -- doesn't have threads, but can capture
                                                 an entire chat with a person instead
flexus_client_kit/integrations/fi_gmail.py    -- cannot capture anything, mail goes into kanban inbox

All the traffic goes through NAME_bot.py script, where you can react on incoming messages
programmatically or put them into kanban inbox. You can also send outgoing messages
programmatically. Sending email is dangerous, a small glitch and you'll get
banned for life, so fi_gmail.py has some guardrails against that. Flooding
slack or telegram is usually harmless.


Bot Setup
---------

Bot defines its own setup, in blocks like this:

```
    "SLACK_BOT_TOKEN": {
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "slack",
        "bs_description": "Bot User OAuth Token from Slack app settings (starts with xoxb-)",
    },
```

A setup dialog is visible to the user in Flexus UI, automatically generated based on bs_* fields.
Panels or tabs are generated based on bs_group, so related parameters group together.

The full list of all bs_type: string_short, string_long, string_multiline, bool, int, float.


Bot Main Loop
-------------

This is typically the first line in bot main loop:

```
setup = ckit_bot_exec.official_setup_mixing_procedure(NAME_install.NAME_setup_default, rcx.persona.persona_setup)
```

It retuns a dict of all defaults in NAME_setup_default that the user can override by providing
their own values in the setup dialog.

```
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(sleep_if_no_work=10.0)  # calls all your rcx.on_* inside and catches exceptions
```

The main loop typically sleeps on rcx.unpark_collected_events() if it has nothing new to process. By having this main loop,
a bot can integrate any poorly-written software that has no python library or immediate reactions possible,
and require polling.

Alternatively, it's possible to sleep on shutdown event:

```
while 1:
    ...do something...
    if await ckit_shutdown.wait(120):
        break
```

Don't use other ways sleep because it will make quick shutdown impossible.

Wrap your main loop into try..finally and make sure you unsubscribe from any external sources
of information, because chances are they keep a reference on your objects you have on stack,
and your bot will have a hard time completely shutting down.


Writing Daily/Weekly/Monthly Reports
------------------------------------

Humans love to see reports, especially about work they didn't have to perform.

Reports can be long or short, but in any case they require a lot of information to
summarize. This makes it hard for LLMs to continue calling the right functions after
processing a lot of input, so writing reports is organized using report() call.

System prompt in NAME_prompts.py needs to explain this. It needs to tell the model
running the bot to complete one section of the report(), restart the chat to take
care of the next.

The report() tool can export a PDF.


Maintaining Scenarios
---------------------



Helping the User to Setup
-------------------------



Writing Logs
------------



Improving on Logs
-----------------



Testing Changes
---------------



Writing a New Bot
-----------------




Coding Style
------------

Don't ever write stupid comments, like "calling function f" and the next line f().

Be careful to write short code, important to not have a lot of lines or messy lines, simple code is great.

Don't write docstrings. Docstrings are silly, unless you are explaining something really really clever which rarely happens.

Prioritize code simplicity. Simplicity beats docstrings every time.

Don't create temporary variables for no reason, if you can easily inline the value to whatever it needs it, do it.

Don't split into many lines things that can be more readable in just one that is not super long.

Comments should appear for:

 * Tricks
 * Hacks
 * Ugliness
 * Places for future improvement, should start with XXX
 * Facts hard to grasp just by looking at code (python duck typing!)

This project uses prefixes in naming, especially for data schema fields.
For example `fgroup_name` is a name for a group in Flexus. It's not the same as `name` which can refer to a name of anything,
and it's not searchable, meaning you can't trace it to its usages everywhere including JavaScript.
Always prefer names with prefixes over generic names, including parameter names and external GraphQL interfaces.

Local variables should, in most cases, be short to prioritize code size and readability, but still make sense and be clear. If code gets messy, use variable name length as a tool to visually distinguish between short-lived
truly local variables and ugly/clever variables that persist on the stack for a long time -- give them a longer name.

Formatting for python, screw the PEP8:

def my_func(
    x: int,
    y: int,
) -> int:
    return x + y

my_func(
    5,
    6,
)

Notice the trailing commas and indent independent of brackets position on the previous line.

For imports, prefer `import xxx` and `xxx.f()` over `from xxx import f` and `f()`. The goal here is to make code locally
readable, so you know where "f" comes from. This rule applies to Flexus own modules and libraries it uses, but does not
apply to very standard python things like "from typing import Any" because "typing.Any" everywhere would not make
readability any better, and you know where Any comes from anyway.

Good example: "from flexus_client_kit import ckit_shutdown" then in code "ckit_shutdown.wait(30)".


Another stupid idea is to define:

MY_CONSTANT = "my_constant"

...and then use MY_CONSTANT as if it was a huge improvement over just using "my_constant". It's not better it's worse,
because a search for "\bmy_constant\b" will not find all its usages. Use strings in code directly.

Good formatting for python graphql client code:

await http_session.execute(gql.gql("""
    mutation WhoCallsAndWhy($input: SomeInputType!) {
        real_name(input: $input) { ... }
    }"""),
    variable_values={
        "input": {
            ...
        }
    },
)

Note WhoCallsAndWhy appears in the backend logs in addition to real_name, so it's clear why the call was necessary, and it's searchable as well.
