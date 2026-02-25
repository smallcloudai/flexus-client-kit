# Swarm Decomposition Agreements

Last updated: 2026-02-24

## Purpose

This document is a working contract for how we decompose the idea-product phase into bots, experts, and skills.
It exists to prevent ambiguity, overengineering, and accidental role overlap.

## Canonical Terms (Grounded in Current Project)

These definitions are aligned with the actual Flexus codebase.

### Bot

A deployable logical unit with:
- its own runtime loop and handlers;
- setup schema and marketplace installation metadata;
- a set of installed experts.

Operationally, a bot is the unit that runs via `*_bot.py` and is installed via `*_install.py`.

### Expert

A runtime execution profile inside one bot, defined by:
- dedicated system prompt (`fexp_system_prompt`);
- optional kernel (`fexp_python_kernel`);
- tool constraints (`fexp_block_tools`, `fexp_allow_tools`);
- captured toolset (`fexp_app_capture_tools`);
- expert name (`fexp_name`) used for routing.

Experts are installed through `FMarketplaceExpertInput` and selected by `fexp_name` in chat/subchat/task routing.

### Skill

A reusable knowledge package used by experts.

A skill is not a first-class runtime entity in platform routing. In practice, it is prompt/kernel/domain logic that is embedded into an expert.
If it needs independent routing, tool policy, or execution lifecycle, it should be promoted to an expert.

### Tool (for decomposition context)

A callable operation used by the model. For inprocess tools, bot code must provide `@rcx.on_tool_call(...)` handlers.

### Subchat (for decomposition context)

An isolated execution thread started from a tool call, typically with a specific expert via `fexp_name`.
Use subchat when isolation and focused completion are required.

## Decomposition Workflow (Idea-Product Phase)

1. Define target artifacts first (not roles): problem signals, ICP/JTBD, value proposition, hypotheses, prioritization, validation plan.
2. Assign one artifact owner per artifact (one expert per artifact type).
3. Split by side effects:
   - if two parts write different artifact domains, split experts;
   - if one part only provides reasoning/checklists, keep it as a skill.
4. Split by tool policy/model/runtime needs:
   - different tool permissions or latency/quality requirements imply separate experts.
5. Validate each unit with one clear done-definition and one clear output contract.

## Depth Criteria

### Decomposition Is Deep Enough When

- one unit produces one artifact type;
- one unit solves one decision class;
- one unit has bounded tool scope;
- completion criteria are explicit and testable;
- failure is locally contained and diagnosable.

### Too Shallow (Needs Further Split)

- "and also..." appears in the mission repeatedly;
- one unit owns multiple unrelated artifact types;
- toolset is broad/general for convenience;
- done-definition is vague or multi-stage.

### Too Deep (Needs Merge)

- neighboring units differ only by wording, not by behavior;
- orchestration overhead is higher than quality gain;
- handoff frequency is high with no information gain;
- two units always run together with same tools and same output.

## Bot vs Expert vs Skill Decision Rules

- Create a **new bot** when integration boundaries, runtime ownership, or operational lifecycle must be separate.
- Create a **new expert** when output contract, tool policy, or reasoning mode differs.
- Create a **skill** when only domain knowledge/rules differ while execution profile stays the same.

## Definition of Done (For This Decomposition)

Decomposition of a phase is accepted only when:
- every target artifact has exactly one explicit owner expert;
- every expert has explicit input/output contract and done-definition;
- each expert has at least one happy-path scenario and one failure-path scenario;
- skills are either reused (2+ experts) or removed (YAGNI);
- no unit has hidden orchestration duties outside its scope.

## Change Policy

Changes to these agreements require explicit approval before implementation.
