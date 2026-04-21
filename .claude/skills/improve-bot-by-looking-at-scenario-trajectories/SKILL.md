---
name: improve-bot-by-looking-at-scenario-trajectories
description: Read scenario scores and trajectories in scenario-dumps/, diagnose patterns across models, understand root causes, propose and apply changes to skill/prompt files.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash(ls *)
---

# Improve Bot by Looking at Scenario Trajectories

You are diagnosing why a bot underperforms in scenario runs and fixing the root causes in skill or prompt files.


## Step 1: Read All Score Files

Pattern: `scenario-dumps/BOT__SCENARIO-*-score.yaml`

User will point you at score files.

Or just find the most recent runs by looking at creation timestamp of -score.yaml

Most likely you will see bot running different models, but some kind of A/B test is possible too, to study which
code is better, in that case experiment name (goes right after bot version) is important.

Read all score pointed by human or belonging to the most recent experiment.


## Step 2: Read Actual Trajectories

Trajectories -actual.yaml are bigger in size, in fact might be huge. Pick 1 or 2 to improve your understanding of the
problems, think which will be most informative.

The -happy.yaml files are all equal within an experiment, so read one if you are curious, it's also mostly equal
to scenario file in the bot, only formatting changes, and expansion of !PYTHON[] notation to include some json from
source code so it does not have to be copy-pasted.


## Step 3: Ask Human What to Fix

First, list every problem you can identify.

BTW not every trajectory is indicative of a problem, sometimes it's random noise.

Then be critical of your ability to fix things. What you think you can fix are only hypotheses at this point.
Pick 1-3 points you are likely to successfully fix and go investigate the source code.

Look up bot code, skills, flexus-client-kit sources, other bots, confirm or disprove your potential solutions.

For each of 1-3 problems you have solutions at all, offer to the human alternatives how to fix it.
Sometimes solutions are worse than the problems, right.
Fix only what the human chooses.


## Anti-Patterns

- Don't add "IMPORTANT" or "CRITICAL" to every instruction. If everything is critical, nothing is, also avoid **bold**
- Of course you can fix every scenario by writing "at step X do Y", for your work to be useful go to the root cause,
take a zoomed-out view, try to reframe, make tools easier to use, delete something, etc, don't fix small
scenario-specific things, that's lazy.

