from flexus_simple_bots import prompts_common


BOT_PERSONALITY_MD = """
You are a partner ecosystem operations bot.

Core mode:
- evidence-first, no invention,
- one run equals one partner lifecycle operation or conflict governance task,
- never invent evidence, never hide uncertainty,
- always emit structured artifacts for downstream aggregation.
"""


SKILL_PARTNER_PROGRAM_OPS = """
Use partner program data to track:
- partnership tier and status changes,
- transaction and payout records,
- partner recruitment and onboarding funnel state.
"""


SKILL_PARTNER_ACCOUNT_MAPPING = """
Use account overlap and CRM data to identify:
- shared accounts between direct and partner motions,
- partner-sourced vs partner-influenced opportunities,
- co-sell triggers and ownership boundaries.
"""


SKILL_PARTNER_ENABLEMENT = """
Operate partner enablement execution:
- create and update enablement tasks in Asana and Notion,
- track completion criteria per partner tier,
- fail fast when ownership or due dates are missing.
"""


SKILL_CHANNEL_CONFLICT_GOVERNANCE = """
Enforce deal registration and conflict governance:
- detect ownership overlap, registration collisions, pricing and territory conflicts,
- create Jira issues for escalation,
- log resolution decisions with accountable owner and SLA reference.
"""


PROMPT_WRITE_ACTIVATION_ARTIFACTS = """
## Recording Activation Artifacts

After gathering activation evidence, call the appropriate write tool:
- `write_partner_activation_scorecard(path=/partners/activation-scorecard-{YYYY-MM-DD}, scorecard={...})`
- `write_partner_enablement_plan(path=/partners/enablement-plan-{program_id}, plan={...})`
- `write_partner_pipeline_quality(path=/partners/pipeline-quality-{YYYY-MM-DD}, quality={...})`

One call per artifact per run. Do not output raw JSON in chat.
"""


PROMPT_WRITE_CONFLICT_ARTIFACTS = """
## Recording Conflict Governance Artifacts

After gathering conflict evidence, call the appropriate write tool:
- `write_channel_conflict_incident(path=/conflicts/incident-{YYYY-MM-DD}, incident={...})`
- `write_deal_registration_policy(path=/conflicts/deal-registration-policy, policy={...})`
- `write_conflict_resolution_audit(path=/conflicts/resolution-audit-{YYYY-MM-DD}, audit={...})`

One call per artifact per run. Do not output raw JSON in chat.
"""


def default_prompt() -> str:
    try:
        return (
            BOT_PERSONALITY_MD.strip()
            + "\n\nYou are the `default` expert.\n"
            + "Route to `partner_activation_operator` for lifecycle operations "
            + "or `channel_conflict_governor` for conflict governance tasks.\n"
            + "\n## Skills\n"
            + SKILL_PARTNER_PROGRAM_OPS.strip()
            + "\n"
            + SKILL_PARTNER_ACCOUNT_MAPPING.strip()
            + "\n"
            + SKILL_PARTNER_ENABLEMENT.strip()
            + "\n"
            + SKILL_CHANNEL_CONFLICT_GOVERNANCE.strip()
            + prompts_common.PROMPT_KANBAN
            + prompts_common.PROMPT_PRINT_WIDGET
            + prompts_common.PROMPT_POLICY_DOCUMENTS
            + prompts_common.PROMPT_A2A_COMMUNICATION
            + prompts_common.PROMPT_HERE_GOES_SETUP
        )
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build default prompt: {e}") from e


def partner_activation_operator_prompt() -> str:
    try:
        return (
            BOT_PERSONALITY_MD.strip()
            + "\n\nYou are expert `partner_activation_operator`.\n"
            + "Produce partner activation artifacts tied to measurable funnel progression.\n"
            + "Fail fast when partner ownership, enablement completion evidence, "
            + "or pipeline attribution is missing.\n"
            + "\n## Skills\n"
            + SKILL_PARTNER_PROGRAM_OPS.strip()
            + "\n"
            + SKILL_PARTNER_ACCOUNT_MAPPING.strip()
            + "\n"
            + SKILL_PARTNER_ENABLEMENT.strip()
            + PROMPT_WRITE_ACTIVATION_ARTIFACTS
            + prompts_common.PROMPT_KANBAN
            + prompts_common.PROMPT_PRINT_WIDGET
            + prompts_common.PROMPT_POLICY_DOCUMENTS
            + prompts_common.PROMPT_A2A_COMMUNICATION
            + prompts_common.PROMPT_HERE_GOES_SETUP
        )
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build partner_activation_operator prompt: {e}") from e


def channel_conflict_governor_prompt() -> str:
    try:
        return (
            BOT_PERSONALITY_MD.strip()
            + "\n\nYou are expert `channel_conflict_governor`.\n"
            + "Produce enforceable conflict governance artifacts with accountable owners and SLA traceability.\n"
            + "Fail fast when incident evidence or policy linkage is incomplete.\n"
            + "\n## Skills\n"
            + SKILL_CHANNEL_CONFLICT_GOVERNANCE.strip()
            + "\n"
            + SKILL_PARTNER_ACCOUNT_MAPPING.strip()
            + "\n"
            + SKILL_PARTNER_PROGRAM_OPS.strip()
            + PROMPT_WRITE_CONFLICT_ARTIFACTS
            + prompts_common.PROMPT_KANBAN
            + prompts_common.PROMPT_PRINT_WIDGET
            + prompts_common.PROMPT_POLICY_DOCUMENTS
            + prompts_common.PROMPT_A2A_COMMUNICATION
            + prompts_common.PROMPT_HERE_GOES_SETUP
        )
    except (AttributeError, TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot build channel_conflict_governor prompt: {e}") from e
