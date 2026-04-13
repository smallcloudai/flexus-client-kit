# Tasktopus Process Manager Bot


## Milestone 1

- Every morning, generate a today's most important 5, based on deadlines, blockers, and dependency chains
- If there is no progress on a task for more than a day, ask human what's happening
- Offer to split a blocked task
- Detect zombie tasks: close/archive/revive
- If no tasks assigned to a human, contact them and offer something that matches their skills and recent activity
- Summarize weekly progress
  - Completed tasks
  - What moved fast
  - Slipped deadlines
  - Engagement score for humans
  - Gaps in process (work uncovered by tasks)
- Prepare topics for upcoming meetings
- Description
  - Clarify from authors
  - Reduce size if someone posts AI-generated description
- Assign a person who might test the changes


## Milestone 2

- Suspiciously similar tasks detection: suggest merging or clarifying ownership
- Hot potato detection (tasks that keep changing assignees) initiate converstation
- Find changes in git:
  - Mention changes in task
  - Auto send to testing task
  - Detect fake progress


## Deprioritize but valid

- Track outside deadlines
- Task dep, no progress on dep for 2 business days, rise up issue
- Detect overloaded humans and recommend rebalancing work
- Meeting notes transfer to action items
- Listening to slack for action items
- Spot tasks waiting on external approvals, contracts, or payments and group them into one "administrative friction" report
- Help morale: chronic overload, invisible work, and unfair assignment patterns


## Thinking

I have very specific Fibery calls that sort of work (but model needs to explore schema first each run, for example no
standard for a task to be "Done", in my db it's "🎉 Done")
OTOH I don't actually want to specialize on Fibery, it might be Notion, Jira, or whatever else,
neither I want to specialize on Slack.
The goal of scenarios is to set priorities and rules for a model to work right.
Write useful scenarios to test model without getting trapped in Fibery specifics -- that's a good intermediate goal.


## One Way to Do It

Create FakeFibery, an integration that requires no live connection, its state can be set up at scenario start. Structure it NOT like Fibery
and make it idealized instead, what if tools exactly matched what we are trying to query or change.

Then a leap of faith: if /tasktopus/cheatsheet has a mapping between idealized commands and real sequence of Fibery calls,
then a big enough model will manage. The cheat sheet must contain workspace-specific data such as "🎉 Done" that is unknowable at install
time.

Left to do: tune models to behave nicely in all of Milestone 1. Turn on real Fibery, fill cheat sheet, enjoy because everything works.

Maintaining /tasktopus/cheatsheet policy doc then need to be taken seriously, at least two ways to do it:
- Filled randomly as exploration of Fibery happens, by reviewing past threads by a specialized expert that improves the cheatsheet.
- Run special skill to discover the structure. Also update something breaks, then a discovery mechanism is needed to
detect when something breaks, then regular Tasktopus threads need a tool to complain about inefficiency, or we are back to
reviewing past threads by a specialized expert.


## Situation 1: Volcano Theme Park Launch

Investors demand a grand opening for a luxury resort built on an active volcano. Marketing wants fireworks, geology wants evacuation
drills, and legal wants literally anything to stop happening.


## Kanban Confusion

Flexus has kanban for bots, it's technical for orchestration, tasks are unmovable by humans, the name is rather for intuition,
not for planning projects.

Fibery has a lot of kanban boards (we have 14) on different topics, moveable and editable by humans, tasks are also more
complex, allowing comments, pictures, references to Sprint, Feature, and actually any arbitrary fields and references.

The bot needs to clearly understand those are not the same.


## Users Confusion

Slack has users, Fibery has users, Flexus has users. If this bot is going to talk to all these people, it needs to know
everybody and their handles on each platform.

Fibery is connected to each bot separately. For what we know, the other bot can be connected to a completely different Fibery
workspace, the same for Slack, so it's our database to keep. The drawback is other bots don't know the mapping or they have to
borrow ours, I just don't see a global users database that will work without logical problems if we have bot-connected
integrations.

More confusion: Fibery is connected on behalf of a user that connects it (clicks a button in their account). There is nothing we
can do about it. The get_me() function will return the same person over and over again, likely irrelevant admin, not
active participant, hopefully (because that will add to confusion). The lesson here is not to rely on get_me for anything.



tasktopus_*.py and PLAN.md nearby
karen_*.py
frog_*.py
flexus_simple_bots/karen/very_limited__actual_support.yaml
don't use explore

