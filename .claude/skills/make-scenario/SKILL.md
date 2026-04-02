---
name: make-scenario
description: Convert an exported chat YAML into a bot scenario file.
---

# Make Scenario from Chat

Convert a real chat YAML into a scenario for bot testing.

Read about scenario naming convention in AGENTS.md.


## Input

User usually provides a chat YAML file path, e.g. `flexus_simple_bots/karen/chat_xxx123.yaml`.
Read it fully before doing anything. Copy it using `cp` to the right place, and then do some edits.


## Goal

Scenarios are idealized examples of behavior. A judge will compare ideal and real behavior.

Judge needs to see unnecessary steps against the background of minimal number of steps. So your
goal is to delete unnecessary steps, or information that later turns out to be
false.

Maybe you can improve wording of assistant having the benefit of hindsight (you see future steps and hints,
assistant didn't at the time)


## Scenario Improvement Steps

1. Remove role=hint messages if any. They are part of scenario generating process to steer the model.

2. Remove skill text from `flexus_fetch_skill` tool calls. Replace the full content with `<explanation>` (unquoted in YAML).
Just makes the scenarios smaller with no loss because there's skill text right there in the same repo.

3. Remove dead-end explorations and failed calls — delete both the call and its tool response. Don't leave orphan
references to removed things in assistant text. Remember, we are making idealized trajectory here.



## Judge Instructions

Most of judge instructions are already in the judge system prompt. Only very specific things about a particular
scenario are needed, and most of the time you don't know what they are until you try running a judge on real
trajectories.

It's something like "relax don't penalize this much", "omg humans really don't like that". Comes from
experimentation.

So write "No additional instructions" as a placeholder. The bot author might edit it later.
