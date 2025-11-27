# LawyerRat Scenarios

This directory contains test scenarios for the LawyerRat bot.

## Scenario Naming Convention

Scenarios follow the pattern: `{skill}__{scenario_name}.yaml`

- `skill`: The expert/skill being tested (e.g., "default", "setup")
- `scenario_name`: A short identifier (e.g., "s1", "s2", "nda_research")

## ⚠️ Important Note About Subchats

The LawyerRat bot's tools (legal_research, draft_document, analyze_contract) use **subchats** to perform their work. Scenarios with subchat tools are complex to test because:
- The subchat must complete and return results
- Scenario mode handles subchats differently than production
- Timing and coordination can cause scenarios to timeout

**Recommendation**: Start with simple scenarios (like `default__simple.yaml`) that test basic bot behavior without tool calls. These are reliable and fast to run.

## Available Scenarios

### Simple Scenarios (No Tools - Reliable)

#### ✅ default__simple.yaml (RECOMMENDED)
Simple greeting test without tools:
- User asks for help with legal matters
- Bot introduces itself and services
- Bot includes proper disclaimers

**Status**: ✅ Works perfectly, 9-10/10 score
**Judging criteria**: Professional tone, helpfulness, proper disclaimers
**Run time**: ~20 seconds

#### ✅ default__intro.yaml
Tests bot personality and capability introduction:
- User asks "What can you help me with?"
- Bot introduces itself as LawyerRat with rat-like personality traits
- Bot lists specific capabilities and customization options

**Status**: ✅ Works perfectly, 10/10 score
**Judging criteria**: Personality traits, capability completeness, disclaimer presence, professional tone
**Run time**: ~20 seconds

#### ✅ default__disclaimer.yaml
Tests legal information vs legal advice distinction:
- User asks for legal advice about their business
- Bot clearly distinguishes what it CAN and CANNOT do
- Bot recommends when to consult a licensed attorney

**Status**: ✅ Works perfectly, 10/10 score
**Judging criteria**: Clear distinction between info/advice, recommending attorney consultation
**Run time**: ~20 seconds

### Advanced Scenarios (With Tools - May Timeout)

#### ⚠️ default__s1.yaml
Tests legal research functionality with subchats:
- User asks about NDAs
- Bot performs research using subchat
- Bot provides structured information

**Status**: ⚠️ May timeout due to subchat complexity
**Judging criteria**: Professional tone, proper disclaimers, thorough analysis

#### ⚠️ default__s2.yaml
Tests document drafting with subchats:
- User requests employment agreement
- Bot asks clarifying questions
- Bot drafts California employment contract

**Status**: ⚠️ May timeout due to subchat complexity
**Judging criteria**: Asking questions first, proper structure, jurisdiction awareness

#### ⚠️ default__contract_review.yaml
Tests contract analysis using `analyze_contract` tool:
- User provides a vendor services agreement for review
- Bot calls analyze_contract tool with focus areas
- Bot identifies high/moderate risk issues and missing provisions

**Status**: ⚠️ May timeout due to subchat complexity
**Judging criteria**: Using analyze_contract tool, identifying specific issues, structured analysis, disclaimers
**Tool tested**: `analyze_contract`

#### ⚠️ default__nda.yaml
Tests NDA drafting with clarifying questions workflow:
- User requests NDA for business partner discussions
- Bot asks 6 clarifying questions (type, parties, purpose, jurisdiction, duration, special provisions)
- User provides details (mutual NDA, California law, 3-year confidentiality)
- Bot calls draft_document tool with appropriate parameters

**Status**: ⚠️ May timeout due to subchat complexity
**Judging criteria**: Asking clarifying questions BEFORE drafting, proper NDA structure, jurisdiction awareness
**Tool tested**: `draft_document`

## Running Scenarios

### Set up environment (one time):
```bash
export FLEXUS_API_KEY=fx-WHyURAG2HW4hsLDukzgSjmambJPLvr9OSp25Zrva
export FLEXUS_API_BASEURL=https://staging.flexus.team/
```

### Run the recommended simple scenario:
```bash
python flexus_simple_bots/lawyerrat/lawyerrat_bot.py --scenario flexus_simple_bots/lawyerrat/default__simple.yaml
```

### Run advanced scenarios (may timeout):
```bash
# Legal research scenario
python flexus_simple_bots/lawyerrat/lawyerrat_bot.py --scenario flexus_simple_bots/lawyerrat/default__s1.yaml

# Document drafting scenario
python flexus_simple_bots/lawyerrat/lawyerrat_bot.py --scenario flexus_simple_bots/lawyerrat/default__s2.yaml
```

## Understanding Results

After running a scenario, check the `scenario-dumps/` directory:

- **lawyerrat__s1-happy.yaml** - Original "golden" scenario
- **lawyerrat__s1-actual.yaml** - What the bot actually did
- **lawyerrat__s1-score.yaml** - AI judge's evaluation with feedback

The score file shows:
- Overall score (0-100)
- Specific feedback on what worked and what didn't
- "Shaky" count (how much the trajectory deviated)

## Creating New Scenarios

1. Create a new YAML file following the naming pattern
2. Include `judge_instructions` at the top
3. Define the message flow with user/assistant/tool exchanges
4. Set `persona_marketable_name: lawyerrat` at the end

### Scenario Structure

```yaml
judge_instructions: |
  Instructions for the AI judge on what to reward/penalize

messages:
  - role: user
    content: User message here

  - role: assistant
    tool_calls:
      - id: unique_id
        type: function
        function:
          name: tool_name
          arguments: '{"arg": "value"}'

  - role: tool
    content: Tool result
    call_id: unique_id

  - role: assistant
    content: Assistant response

persona_marketable_name: lawyerrat
```

## Tips

- Keep scenarios focused on one skill/feature
- Include both happy paths and edge cases
- Use judge_instructions to specify what matters most
- Run scenarios after system prompt changes to catch regressions
- Don't run all scenarios constantly (it's expensive) - pick representative ones
