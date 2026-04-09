# Flexus Client Kit (ckit)

Instructions on how to improve existing bots or write new bots for Flexus, an agent orchestrator.


Example
-------

Before doing anything, read flexus_simple_bots/frog_*.py as an example to understand how
bots are built. The Frog bot is specifically designed as an educational, simple bot, to
showcase tricks available in this system.


What Files Define a Bot?
------------------------

NAME_bot.py         -- the file to run a bot
NAME_prompts.py     -- prompts live in a separate file
NAME_install.py     -- installation script, uses _bot and _prompts to construct a marketplace record
NAME-1024x1536.webp -- detailed marketplace picture under 0.3M (auto-detected by marketplace_upsert_dev_bot)
NAME-256x256.webp   -- small avatar picture with transparent background (auto-detected)
forms/              -- optional directory with custom HTML forms for policy documents
VERSION             -- one file per Python package (e.g. flexus_simple_bots/VERSION), shared by all bots in it;
                       marketplace_upsert_dev_bot() reads bot_dir.parent/VERSION for the version string

In repositories separate from flexus-client-kit, create setup.py that installs flexus_NAME module.


Writing NAME_install.py
-----------------------

The install function signature is:

    async def install(client: ckit_client.FlexusClient):

Pass bot_dir to marketplace_upsert_dev_bot() and it auto-derives:
- marketable_name          from bot_dir.name
- marketable_version       from bot_dir.parent/VERSION  (bumped automatically on version conflict)
- marketable_github_repo   from git remote get-url origin
- marketable_run_this      from the first *_bot.py found in bot_dir
- pictures                 from NAME-256x256.webp and NAME-NNNxNNN.webp in bot_dir

Do NOT pass these as separate arguments. The removed parameters are:
  marketable_name, marketable_version, marketable_github_repo, marketable_run_this,
  marketable_picture_big_b64, marketable_picture_small_b64

Model selection uses two tiers:
  marketable_preferred_model_expensive  -- default tier
  marketable_preferred_model_cheap      -- cheap tier, selected per expert via fexp_model_class="cheap"
The old single marketable_preferred_model_default parameter is removed.

Minimal example:

    async def install(client: ckit_client.FlexusClient):
        await ckit_bot_install.marketplace_upsert_dev_bot(
            client,
            ws_id=client.ws_id,
            bot_dir=MY_ROOTDIR,
            marketable_title1="My Bot",
            marketable_title2="Does something useful",
            marketable_author="Flexus",
            marketable_occupation="...",
            marketable_description="...",
            marketable_typical_group="...",
            marketable_setup_default=[],
            marketable_preferred_model_expensive="gpt-5-mini",
            marketable_preferred_model_cheap="gpt-5-mini",
            marketable_experts=[(name, exp.filter_tools(my_bot.TOOLS)) for name, exp in EXPERTS],
            marketable_schedule=[...],
            marketable_accent_color="#aabbcc",
            marketable_featured_actions=[],
            marketable_intro_message="...",
        )

    if __name__ == "__main__":
        from flexus_simple_bots.my import my_bot
        client = ckit_client.FlexusClient(f"{my_bot.BOT_NAME}_install")
        asyncio.run(install(client))


Kanban Board
------------

Flexus bots are designed to perform work, independent of user/admin. The speed at which new
tasks are coming is independent of how fast the bot can resolve them. Each bot has a
kanban board with 'inbox' column that receives new tasks.

On schedule (like "every 5 minutes") the bot gets activated (starts a chat) to triage
the inbox -- moving tasks into 'todo' column, potentially joining several tasks into one.

Scheduler automatically moves tasks from 'todo' to 'inprogress' and activates the
bot (starts a chat), keeping an eye on how many tasks can run simultaneously (usually 3-5).
On start the task is already assigned to chat, scheduler makes a predefined call on behalf of
assitant to show the status: current task with details and other tasks sorted in columns.
Other tasks with visible summaries work as medium-term memory. The board is visible to the
user in Flexus web UI.

Once the bot decides it has finished with the assigned task, it calls resolve with a summary
and resolution code, that's how tasks get into the 'done' column.

There are five kanban tool variants:

flexus_kanban_safe -- only observes tasks with the same ktask_human_id as the current task
flexus_kanban_public -- all tasks with nonempty ktask_human_id, designed to talk to humans in a public channel
flexus_kanban_triage -- move bot's own tasks (same persona_id), cannot get current task
flexus_kanban_advanced -- bot's own tasks + current task
flexus_kanban_boss -- bot's group + subgroups

...chosen at install time based on `allow_tools` in the expert definition. The variant
determines what the bot can see and do, functions are: status, fetch_details, search,
inbox_to_todo, resolve, batch_resolve, add_details, reopen, restart.



Schedule
--------

Humans can talk to a bot, but mostly this platform is about completing work autonomously.

NAME_install.py has `marketable_schedule` among other things, it typically has:

SCHED_TASK_SORT to start sorting inbox, it might be a good idea to make a separate expert to do
this work, and give it flexus_kanban_triage.

SCHED_TODO to get assigned a single task from todo column and work on it.

SCHED_PICK_ONE for bots that don't realistically have a large volume of noisy tasks and don't
have malicious actors to worry about, this skips sort/todo mechanism.

The number of tasks a bot works on simultaneously is persona_max_inprogress.


Messengers
----------

Flexus bots have chat interface within Flexus web UI and mobile, but you (or external clients) can
talk to some of them via messengers.

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

The full list of all bs_type: string_short, string_long, string_multiline, bool, int, float, list_dict


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


Choosing Where to Store Data
-----------------------------

When designing a new bot, decide early where each piece of data lives. The wrong choice leads to
awkward workarounds later.

 * Bot settings — configuration that rarely changes: feature toggles, thresholds, desirable
   behavior explanations. Editable by admin in the UI. Not suitable for data that changes
   frequently or grows over time. Settings are always the first message in every bot thread.

 * MongoDB — high-write, append-heavy, bot-private data. Various histories, event logs,
   per-user state, cached API responses, temporary files, reports.
   Use TTL indexes for automatic cleanup!
   Use `mongo_store_file()` for file-like blobs (reports, exports), use raw pymongo collections
   for structured records that need querying (insert_one, find, count_documents), don't forget
   the automatic cleanup.

 * Policy documents AKA memory — structured JSON documents shared across bots and visible/editable by humans in
   the UI. Good for: rules, strategies, forms filled together with the user, results that other bots
   consume. Bad for: high-frequency writes, daily logs, temporary data.

 * Kanban — work items that need scheduling, prioritization, and tracking. Natural fit when the bot
   accumulates work and processes it in batches on schedule. Not a good fit for instant reactive actions.
   Completed task summaries stay visible in context, acting as medium-term memory.

 * ERP/CRM — use when operating on external contacts, see erp_schema.py for details.


Using and Writing Scenarios
----------------------------

Scenarios are YAML files that represent how a bot should work, a "happy path" to verify behavior and catch regressions.

Usually scenarios do not have system prompts inside to avoid confusion, because usually scenarios are made
using the very first version of the system prompt. Scenarios might include instead "judge_instructions" from
scenario author: what should be rewarded and penalized in the behavior, what to ignore.

After making changes to a bot, run:

python flexus_simple_bots/my/my_bot.py --scenario flexus_simple_bots/my/my__s1.yaml

The naming convention is $EXPERT$__$SCENARIO$.yaml with double underscore. The 'default' expert is replaced
by the bot name, so files are easier to find. In this example the bot "my" has expert "default" so the prefix is "my".

Don't run this for all bots because it's expensive, but it's a good idea to run one scenario of your choosing
for the one bot you've just changed.

The result is saved into:

scenario-dumps/my__s1-happy.yaml
scenario-dumps/my__s1-actual.yaml
scenario-dumps/my__s1-score.yaml

Note that .gitignore has scenario-dumps/** inside.

How the bot performs is judged by a model on the backend side and saved into -score.yaml,
on a scale from 1 to 10. You'll see feedback on how the actual trajectory compares to the happy path so you
can make improvements. Per-turn feedback fields human_problem_severity, assistant_problem_severity both
have scale 0=perfect, 1=minor, 2=major.

When running scenarios, human input is simulated by an LLM. Most tools validate their arguments and then
call an LLM, some simple tools respond without LLMs. The "shaky" you see in -score.yaml means how
many times human or tools were simulated without sufficient support in the original happy path,
in other words LLMs are making stuff up trying to have a similar conversation, so it's a measure of trajectory
deviation from the original even if the score is high.

It's a good idea to load -score.yaml into context, because it's small and informative. It MIGHT be a good
idea to load -happy.yaml and -actual.yaml and judge for yourself, but also it might so happen the trajectories
are very long and you are better off using the specialized judge feedback, and spending your context tokens on
loading source code files instead. Or run a subchat to discover whatever you need without overflowing
the context.


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


Lark Kernels
------------

Chats are executed on the backend side, bot only gets updates and tool calls, the reason for this design is
to make bot code smaller, relieving it of important responsibilities (low level model calls). Lark is a fast
python-like piece of code that executes before and after generation of an assistant message, the library
used is "lark-parser/lark" on github. What Lark can do: stop an unwanted tool call, set error, return subchat
result, prevent chat from finishing, check output format and ask for a fix, keep track of spending, post
instructions to the model.

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

All the prints go into the assistant message as ftm_provenance = {..., "kernel1_logs": [], "kernel2_logs": []}
and the bot will receive them as regular thread message updates, that's how you debug Lark kernels.


Definitions: Tools, Skills, Subchats, Experts
---------------------------------------------

### Tool

Should be used for: API calls, CRUD, instant operations. Returns string visible to the model. Can raise NeedsConfirmation for dangerous ops or WaitForSubchats after spawning subchats.
Remember that tools with side effects need to be faked when running a scenario, grep scenario_generate_tool_result_via_model() for details.
Examples: flexus_policy_document, template_idea, facebook/linkedin APIs.
BTW a tool can return a multi-modal result [{"m_type": "image/png", "m_content": "base64..."}, {"m_type": "text", ...}, ...]

### Skill

Large instruction set loaded into prompt when needed. No separate context, no extra tools.
Tradeoff: more instructions we need to maintain (cost) vs accuracy on complex tasks (gain).
Implemented as tool that returns instructions as text.
Examples: idea rating rules, ad platform specifics.
Each bot can have a function for dynamic skills they can invent, client-kit a has standard mechanism for built-in skills,
means they are discoverable at install time, skill descriptions appear in the first message along with bot setup,
from db as installed.

### Subchat

A separate thread with isolated context.
Has a Lark kernel to control termination via setting subchat_result.
Subchats start as tool calls in the original thread, tools call bot_subchat_create_multiple().
Formally a subchat returns a single string that becomes the tool result, but it can have other side effects.
Must complete in 10 minutes or so (actually TIMEOUT_TOOL_CALLS), no human interaction is possible inside.
Use for focused tasks needing a specialized set of tools.
Example: productman spawns criticize_idea to receive an independent evaluation.

### Expert

Expert is a separate system prompt + toolset, installed during bot installation.
The 'default' expert is what the user talks to if they just start a conversation.
Kanban tasks can explicitly specify ktask_fexp_name to control what expert within the bot should pick up the task.
Unlimited duration, human can interact mid-task.

Use for:
 - separate pieces of work, especially using a specialized set of tools
 - or entirely separate behavior

Example: survey campaign execution in productman, has special code to interact with survey external API.


A2A Communication
-----------------

Works like this:

- You can tell the model to call flexus_hand_over_task(to_bot="", description="", fexp_name=""),
  that will create a kanban task in the inbox of that bot.
- You can send a task to your own expert, works exactly like giving a task to another bot.
- Once the task is completed (moved to kanban "done") a message will appear with role='cd_instruction' informing about that.
- It might not be real-time because the task goes into a queue, does not get executed immediately.
- The original chat does not wait, it might continue talking to user or calling other functions, tell the model
  to respond with no calls and therefore switch to 'wait for user' mode for the waiting to happen.


External Auth
-------------

Auth data for external services is in `rcx.external_auth` dict, keyed by provider. Bot and external service are
connected by user in the UI, you can't change anything about it unless you make changes in flexus backend.

OAuth providers: "google", "slack", "github", etc.
Manual API key providers: "slack_manual", "discord_manual", "resend", etc.

In NAME_install.py declare what your bot needs:

```
marketable_auth_needed=["google"],
marketable_auth_supported=["atlassian"],
marketable_auth_scopes={"google": ["https://www.googleapis.com/auth/gmail.modify"]},
```

Scopes: "read:jira-work" for Atlassian, "channels:read" for Slack, etc.

XXX make a handler in auth_providers to list these.


Marketplace Stages
------------------

marketplace_upsert_dev_bot() — Registers/updates a dev bot in the marketplace. Any next stage requires dev bot installation.

bot_install_from_marketplace() aka "hire" — User hires the bot into their workspace from marketplace.
Creates a persona instance with unique persona_id and fgroup_id. User configures settings via setup dialog.

run_bots_in_this_group() — The bot process starts. If running with user API key (dev mode), it automatically installs dev bot.
If running a scenario, it creates a temporary group and hires the bot into it.

What is happening on backend side:

MARKETPLACE_COMING_SOON — Placeholder stage. Has a picture, collects feedback.
MARKETPLACE_DEV — Default stage when marketplace_upsert_dev_bot() is called. Only visible to the dev's workspace.
MARKETPLACE_WAITING_IMAGE — Triggered when user clicks "Build" in UI.
MARKETPLACE_FAILED_IMAGE_BUILD — If docker build or smoke test fails.
MARKETPLACE_PRIVATE — After successful build+test. At this point many workspaces might have their custom bots long-term.
MARKETPLACE_ON_REVIEW — Private bot submitted for review to become public.
MARKETPLACE_BETA / MARKETPLACE_STABLE — Approved after review.


Writing Logs
------------



Improving on Logs
-----------------



Writing a New Bot
-----------------



Policy Documents and Forms
--------------------------

Policy Documents are structured json files stored on the backend side in the DB.
They are accessible to the user in 'Documents' button in the Flexus UI.
They are accessible to bots using flexus_policy_document() cloudtool.

```
/company/
├── summary                                     # A very compressed version of what the company is
├── product                                     # Product details
├── style-guide                                 # Brand colors, fonts

/gtm/
├── discovery/
│   ├── archived/
│   └── {idea-slug}/
│       ├── idea                                # First Principles Canvas
```

What should go to a policy document:
- Explanations of how bots should do their job
- Forms filled out together with the user
- Weekly experiments changing the policy

What is not a policy document:
- Daily reports, temporary files -- use mongo integration instead
- User's files -- send the user to upload folder in the UI, after that use flexus_read_original() to get contents

Naming convention for all policy documents is kebab-case. For `{idea-slug}` it's 2-4 words kebab-case capturing
product concept (e.g., `unicorn-horn-car`)

There are 3 types of forms to edit policy documents: QA, Schemed, Microfrontend.

### QA or Questions-Answers

```
{
    "styleguide": {
        "meta": {
            "author": "Human Name",
            "created": "20260209",
            "updated": "20260209",
        },
        "section01-colors": {
            "title": "🎨 Brand Colors (please verify)",
            "question01-primary": {
                "q": "Primary Brand Color",
                "a": "#0066cc",
                "t": "color"
            },
            ...
        },
        "section02-typography": {
            "title": "📝 Typography",
            ...
        },
        ...
    }
}
```

Notable features:
- Top level tag such as "styleguide" defines the document type
- "meta" has fixed fields "author", "created", "updated", it might have other fields
- "sectionXX-name" when sorted shows in the right order in the UI
- Typical path in json looks like "styleguide/section01-colors/question01-primary/a"

There's a separate code in the UI to edit QA documents.

### Schemed

```
{
    "strategy": {
        "meta": {
            "author": "Human Name",
            "created": "20260209",
            "updated": "20260209",
        },
        "schema": {
            "section03-metrics": {
                "type": "object",
                "title": "Metrics",
                "required": [
                    "mde",
                    ...
                ],
                "properties": {
                    "mde": {
                        "type": "object",
                        "order": 5,
                        "required": [
                            "relative_change",
                            "confidence"
                        ],
                        "properties": {
                            "confidence": {
                                "type": "number",
                                "order": 1
                            },
                            "relative_change": {
                                "type": "number",
                                "order": 0
                            }
                        },
                        "additionalProperties": false
                    },
        ...
        "section03-metrics": {
            "mde": {
                "confidence": 0.8,
                "relative_change": 100
            },
            ...
        }
...
```

Notable features:
- Has schema and data in the same document
- Schema is typically copy-pasted from the current bot version that created the document
- A newer version of the bot overwrites the schema when manipulating data
- "order" in fields overrides alphabet sorting, to present the form correctly in the UI

There's a separate code in the UI to edit Schemed documents.

### Microfrontend

In the "meta" section it is possible to include "microfrontend": "bot_name":

```
{"mydoc": {"meta": {"microfrontend": "mybot", "created_at": "..."}, ...}}
```

The UI will load the html from: `/v1/marketplace/{microfrontend}/{version}/forms/{top_level_key}.html`

The Frog bot has example of microfrontend, see `flexus_simple_bots/frog/frog_bot.py` and `frog/forms/pond_report.html`.

### Choosing Form Editor

Rule of thumb: use QA, if you can't, use Schemed, if you can't, use Microfrontend. QA results in
minimal handling code for the format, making it the most reliable solution. Schemed can have
questionable UI representation, especially trying to fit array of objects into a narrow view, and
requires code that writes the schema correctly. Microfrontend is more of "you are on your own" solution,
susceptible to bugs, copy-paste, requires debugging, it's more expensive in effort and less reliable
solution of the three.


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

Local variables should, in most cases, be short to prioritize code size and readability, but still make sense and be clear.
If code gets messy, use variable name length as a tool to visually distinguish between short-lived
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
