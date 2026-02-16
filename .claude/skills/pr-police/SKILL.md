---
name: pr-police
description: Whacking diffs and PRs into sanity
allowed-tools: Read, Grep, Glob, Bash(git diff*), Bash(gh pr view*), Bash(gh pr diff*), Bash(gh api *)
---

# PR Review

Review `git diff` (unstaged) and `git diff --cached` (staged) for the current changes.

Read flexus-client-kit/AGENTS.md to understand the project values.

For each changed file, read enough surrounding context to understand what the change does.


## Stoopids

### Avoid "Best Behavior"

Sweeping problems under the rug is bad. Some examples: `result.data?.field`, `x || ""`, `if (result.something_useful) { use it }`.

Catching exceptions is bad, especially Exception/BaseException, instead investigate what the calling code would do with the exception,
in all likelihood it already does the right thing. Catching a specific error might be a good idea, such as SlackApiError.
If it's hard to predict what the exception will be, then write log, crash. Crash is easy to fix later.

Writing isinstance(x, type1) is bad. Decide what type the data should be and stick with it. Make sure the code
crashes if the type is wrong. Crash is easy to fix later.

### Don't Allow Generic Names

Names must indicate purpose, intent, joke, be unique/searchable, and not already exist in hundreds of places. Avoid: `event`, `data`, `handler`.
Local variables should be one letter like `i` or `x` to indicate short life. Flexus uses prefixes for field names (should be `fgroup_name` not `name`).
It's more of an issue for Flexus backend than in an individual bot that is not imported in other places, but still keep an eye for bad naming,
especially in integrations.

### Don't Allow Docstrings

Instead write comments about: tricks, hacks, ugliness, places for future improvement (should start with XXX), facts hard to grasp just by looking at code,
reasons for a piece of code to exist.

Don't pass ugly code without a comment why it exists.


## Slop

### Bot Spec

Code should cover the spec of a bot (typically located in BOT_SPEC.md), in a simple straightforward way, not
reinvent 100 other things.

### Value of Code

Writing a ton of code is easy, value of a marginal line of code is negative. Not just text is bad for clogging context,
any logical gates are bad, making it harder to understand what the code actually does.

Generally simplicity and deleting code is good. Complexity and adding code is bad.

### Prompt

Oh yes, it's easy to write a ton of prompts and instructions as well. Value of additional instructions is negative.
Shorter prompts work better. What is the justification for adding new instructions, does it actually build a consistent
case for the model to follow?

Are the new instructions more atomized, cheating particular use cases to pass, at the expense of instructions being
short and simple?

### Scenarios

It might be a next step from the current diff, sure, but prompts need testing. Scenarios are the tool for that,
the whole utility of a bot from beginning to end should be demonstrated using a scenario.
Accept a PR with changes in instructions if it handles scenario better: responses are better or
the same, more models work.

### Review

Before a bot becomes public, it goes through a review. The review looks at:

- Sending user data to 3rd parties (instant ban)
- Potential for mixing data of several users, for example via global variables
- Bad practices starting / stopping coroutines
- Using obscure libraries

Your role is to flag those things before it gets to review: reject crazy libraries, make sure coroutines are 200% reliable, etc.

### Forms

Bots allow Microfrontends, html files that show an editor for Policy Documents to work together with the user. Does not
mean this particular bot should use it! Use QA or Schemed to avoid large hard-to-debug html blobs. Should be
a really good case for Microfrontends, like a map or something.


## Output format

Stick to 1 or 2 main issues. Write it as a short, opinionated review, a paragraph or less.

When there's no global problems, and only issues with files, then quote what is wrong and point out small problems.

If the diff is clean, say so. Don't invent problems. Be direct — "this is bad because...".
