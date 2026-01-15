Instructions on how to improve existing bots or write new bots for Flexus, an agent orchestrator.


Comprehensive Documentation
---------------------------

For detailed guides on bot creation and testing, see:

- **FLEXUS_BOT_REFERENCE.md** - Complete step-by-step tutorial
  - Core concepts, terminology, and architecture
  - Structure (bot, prompts, install)
  - Tools (cloudtools vs inprocess), experts, Lark kernels
  - Kanban board, scheduling, subchats, A2A communication
  - Policy documents, custom forms, messenger integrations
  - Testing with scenarios, deployment, and complete Frog bot example

This document provides a quick reference. For in-depth guidance, consult the full tutorials above.


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


Example
-------

Before doing anything, read flexus_simple_bots/frog_*.py as an example to understand how
bots are built. The Frog bot is specifically designed as an educational, simple bot, to
showcase tricks available in this system.


What Files Define a Bot?
------------------------

NAME_bot.py        -- the file to run a bot
NAME_prompts.py    -- prompts live in a separate file
NAME_install.py    -- installation script, uses _bot and _prompts to construct a marketplace record
NAME-1024x1536.jpg -- detailed marketplace picture under 0.3M
NAME-256x256.png   -- small avatar picture with either transparent or white background
forms/             -- optional directory with custom HTML forms for policy documents


Kanban Board
------------

Flexus bots are designed to perform work, independent of user/admin. The speed at which new
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

Humans can talk to a bot, but mostly this platform is about completing work autonomously.

NAME_install.py has `marketable_schedule` among other things, it typically has SCHED_TASK_SORT to
start sorting inbox, and SCHED_TODO to get assigned a single task from todo column and work on it.
But anything can be scheduled, such as writing reports daily, or rewriting strategy weekly.

Think of those as launchers, what kind of job the bot needs to perform on schedule?


Messengers
----------

Maybe at some point there will be a UI, but today Flexus bots only have chat interface
within Flexus web UI, and you can talk to them via messengers.

Any incoming messages usually go to inbox, or if messenger's thread has captured a
Flexus thread, then the message goes directly into the captured thread in the Flexus
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


Custom Forms
------------

Bots can provide custom HTML forms to edit policy documents instead of the default JSON editor.
Forms are embedded in an iframe and communicate with the parent via postMessage.

File structure:
```
mybot/
  forms/
    my_report.html     -- form for documents with "my_report" top-level key
    survey.html        -- form for documents with "survey" top-level key
  mybot_install.py
  ...
```

The document type is determined by the top-level key that contains an object with a `meta` subobject:
```
{"my_report": {"meta": {"created_at": "..."}, "title": "...", "content": "..."}}
```

The form filename must match the top-level key. See flexus_simple_bots/frog/forms/pond_report.html for a complete example.

Protocol messages:
- Parent → Form: INIT (content, themeCss, marketplace), CONTENT_UPDATE (content), FOCUS (focused)
- Form → Parent: FORM_READY (formName), FORM_CONTENT_CHANGED (content)


### Styling - Theme-Aware Paper Pattern

Custom forms should match preexisting forms (like WorksheetEditor.vue) using theme-aware CSS variables
that automatically adapt to light/dark mode:

- `--p-primary-contrast-color` - paper background (white in light mode, black in dark mode)
- `--p-primary-color` - paper text color (black in light mode, white in dark mode)
- `--p-content-hover-background` - desk/input backgrounds (adapts to theme)
- `--p-text-color` - standard text color (adapts to theme)
- `--p-text-muted-color` - muted text, dashed border color
- `--p-surface-border` - borders
- `--p-red-500` - red for criticism/error text

**Never hardcode colors** like `white`, `#1f1f1f`, etc. - always use CSS variables.

CSS template:
```css
body { background: var(--p-content-hover-background); margin: 0; padding: 10px; }
.paper {
  width: 440px; padding: 20px; min-height: calc(100vh - 20px);
  background: var(--p-primary-contrast-color); color: var(--p-primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.meta-box {
  width: 400px; display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 3rem; padding: 1rem;
  border: 2px dashed var(--p-text-muted-color); border-radius: 8px; position: relative; font-size: 0.8rem;
}
.meta-label {
  position: absolute; top: -0.65rem; left: 1rem; background: var(--p-primary-contrast-color);
  padding: 0 0.5rem; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.05em; color: var(--p-text-muted-color);
}
h1 { font-size: 1.25rem; font-weight: 600; color: var(--p-primary-color); margin: 0 0 1.5rem 0; }
.field { margin-bottom: 1rem; width: 400px; }
.field > label { display: block; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem; }
input, textarea, select {
  border: 1px solid var(--p-surface-border); border-radius: 6px;
  padding: 0.5rem 0.75rem; font-size: 1rem; font-family: inherit; box-sizing: border-box;
  background: var(--p-content-hover-background); color: var(--p-text-color);
}
input:focus, textarea:focus, select:focus { outline: none; border-color: var(--p-primary-color); }
textarea { resize: none; field-sizing: content; min-height: 2.5rem; width: 100%; }
```

See flexus_simple_bots/frog/forms/pond_report.html for a complete example.


Bot Main Loop
-------------

This is typically the first line in bot main loop:

```
setup = ckit_bot_exec.official_setup_mixing_procedure(NAME_install.NAME_setup_schema, rcx.persona.persona_setup)
```

It returns a dict of all defaults in NAME_setup_schema that the user can override by providing
their own values in the setup dialog.

```
while not ckit_shutdown.shutdown_event.is_set():
    await rcx.unpark_collected_events(sleep_if_no_work=10.0)
```

The unpark_collected_events() processes queued events (updated messages, threads, tasks from the database)
and triggers your @rcx.on_* handlers in a sequential way and catches exceptions. If nothing is queued, it
sleeps for the specified duration. This pattern lets bots integrate with poorly-written not-coroutine-safe
external software.

Main loop allows to integrate with software that requires polling. Alternatively, it's possible to sleep on
shutdown event:

```
while 1:
    ...do something...
    if await ckit_shutdown.wait(120):
        break
```

Don't use other ways to sleep because it will make quick shutdown impossible.

Wrap your main loop into try..finally and make sure you unsubscribe from any external sources
of information, because chances are they keep an additional reference on objects you have on the stack,
they will not die on function exit, and your bot will have a hard time completely shutting down.


Using and Writing Scenarios
----------------------------

Scenarios are YAML files that represent how a bot should work, a "happy path" to verify behavior and catch regressions.

Usually scenarios do not have system prompts inside to avoid confusion, because usually scenarios are made
using the very first version of the system prompt. Scenarios might include instead "judge_instructions" from
scenario author: what should be rewarded and penalized in the behavior, what to ignore.

After making changes to a bot, run:

python flexus_simple_bots/my/my_bot.py --scenario flexus_simple_bots/my/default__s1.yaml

The naming convention is $EXPERT$__$SCENARIO$.yaml with double underscore, in this example the expert is "default" and
the scenario name is "s1".

Don't run this for all bots because it's expensive, but it's a good idea to run one scenario of your choosing
for the one bot you've just changed.

The result is saved into:

scenario-dumps/my__s1-happy.yaml
scenario-dumps/my__s1-actual.yaml
scenario-dumps/my__s1-score.yaml

Note that .gitignore has scenario-dumps/** inside.

How the bot performs is judged by a model on the backend side and saved into -score.yaml. You'll see
feedback on how the actual trajectory compares to the happy path so you can make improvements.

When running scenarios, human input is simulated by an LLM. Most tools validate their arguments and then
call an LLM, some simple tools respond without LLMs. The "shaky" you see in -score.yaml means how
many times human or tools were simulated without sufficient support in the original happy path,
in other words LLMs are making stuff up trying to have a similar conversation, so it's a measure of trajectory
deviation from the original even if the score is high.

It's a good idea to load -score.yaml into context, because it's small and informative. It MIGHT be a good
idea to load -happy.yaml and -actual.yaml and judge for yourself, but also it might so happen the trajectories
are very long and you are better off using the specialized judge feedback, and spending your context tokens on
loading source code files instead.


Improving System Prompt
-----------------------

Most likely you'll see very specific feedback, like "question 8 didn't work". This feedback comes from
human users or an automated scenario judge. Both can be very specific in what they don't like, because
that is what their particular experience was.

IMPORTANT: YOU MUST NOT FIX ANY SPECIFICS.

Changes in the system prompt must not say "oh if you see file1 then respond X". That will
fix the test essentially by cheating and will not make the bot any better.

Think what the root cause is. How do I fix the personality of this bot so an entire class of
problems (not this specific one) is no longer possible?

Avoid excessive formatting and excessive emojis. Stick to # ## ### markdown headers, paragraphs, bullet lists.
Only use emojis for technical reasons in system prompt, for example 💿 and ✍️ have special meaning in Flexus.

Minimize system prompt size. Prefer re-writing of existing language to adding more and more rules.

Iterate making small changes and running the scenarios again.

Remember each system prompt change requires bot installation, because system prompt is stored in the database:

python -m flexus_simple_bots/my/my_install.py --ws xxx1337


Lark Kernels
------------

Chats are executed on the backend side, bot only gets updates and tool calls, the reason for this design is
to make bot code smaller, relieving it of important responsibilies. Lark is a fast python-like piece of code
that executes before and after generation of an assistant message, the library used is "lark-parser/lark" on github.
What Lark can do: stop an unwanted tool call, set error, return subchat result, prevent chat from finishing, check
output format and ask for a fix, keep track of spending, post instructions to the model.

A subchat will not work at all unless it runs a Lark kernel that will return a value! See
frog_install.py on how to make an expert with a Lark kernel.

Inputs: "messages", "coins", "budget"
Outputs: "subchat_result", "post_cd_instruction", "error", "kill_tools"

Example:

print("coins %0.2d / %0.2d" % (coins, budget))
msg = messages[-1]
if msg["role"] == "assistant" and "MAGICWORD" in str(msg["content"]):  # theoretically the content might be [{"m_type": "image/png", "m_content": "..."}, ...] but the assistant only produces text
    subchat_result = msg["content"]
elif msg["role"] == "assistant" and len(msg["tool_calls"]) == 0:
    print("aww chat stops!")
    post_cd_instruction = "Don't stop, talk to me more!!!"
elif msg["role"] == "assistant" and len(msg["tool_calls"]) > 0:
    kill_tools = True
    error = "Noooo no tool calls today"

All the prints to into the assistant message as ftm_provenance = {..., "kernel1_logs": [], "kernel2_logs": []}
and the bot will receive them as regular thread message updates, that's how you debug Lark kernels.


Skills, Subchats and A2A Communication
--------------------------------------

Bot experts are necessary when you need a separate system prompt and toolset.

When you need a subtask completed, there are two choices: run subchat or use A2A to hand over the task
to your different expert, or another agent.

Subchat applicability:
- Subchats works as tool calls: it runs an additional thread, puts subchat_result produced by Lark kernel back as a
  tool response message into the original thread.
- TIMEOUT_TOOL_CALLS is 3600s (one hour), subchats as tool calls cannot last for more then that. That means: no human confirmations
  inside a subchat (might be no human available for 1 hour), no external lasting process that might last long.
- Can only return text.

A2A communication applicability:
- You can tell me model to call flexus_hand_over_task(to_bot="", description="", fexp_name=""), that will create a kanban task
  in the inbox of that bot.
- Once the task is completed (moved to kanban "done") a message will appear after the flexus_hand_over_task() call informing
  about that.
- It's slower because the task goes into a queue, not gets executed immediately.
- The original chat does not wait, it continues and the model needs to call nothing (wait for user to respond) for
  waiting to happen.


Writing Logs
------------



Improving on Logs
-----------------



Writing a New Bot
-----------------



Coding Style
------------

Don't ever write stupid comments, like "calling function f" and the next line f().

Be careful to write short code, important to not have a lot of lines or messy lines, simple code is great.

Don't write docstrings. Docstrings are silly, unless you are explaining something really really clever which rarely happens.

Prioritize code simplicity. Simplicity beats docstrings every time.

Don't create temporary variables for no reason, if you can easily inline the value to whatever needs it, do it.

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

Notice the trailing commas and indent independent of bracket position on the previous line.

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
