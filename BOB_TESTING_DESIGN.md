# BOB Bot Testing Design

How BOB tests newly created bots.

## Quick Reference

| Test | BOB Can Do | How |
|------|------------|-----|
| Syntax validation | ✅ Yes | `bash` + `py_compile` |
| Import checking | ✅ Yes | `bash` + `python -c` |
| Tool unit tests | ✅ Yes | `bash` + `pytest` |
| Install to marketplace | ✅ Yes | `bash` + env vars |
| Scenario testing | ✅ Yes | `--scenario` flag + LLM judge |
| Real external APIs | ❌ No | User configures after deployment |
| Real Slack/Discord | ❌ No | User completes OAuth after deployment |


## Testing Flow

After `claude_code` creates a bot, BOB validates in stages:

### Stage 1: Syntax Check
```bash
python -m py_compile mybot/mybot_bot.py mybot/mybot_prompts.py mybot/mybot_install.py
```

### Stage 2: Import Check
```bash
cd mybot && python -c 'import mybot_bot; import mybot_prompts; import mybot_install; print("OK")'
```

### Stage 3: Tool Unit Tests
```bash
cd mybot && python -m pytest mybot_test.py -v
```

For each custom tool, BOB must create a unit test that validates the tool's logic:

```python
# mybot_test.py

import pytest
from mybot_bot import handle_weather, WEATHER_TOOL

@pytest.mark.asyncio
async def test_handle_weather_missing_api_key():
    """Tool returns error when API key not configured."""
    result = await handle_weather(
        toolcall=None,
        args={"city": "Paris"},
        rcx=None,
        setup={},  # No API key
    )
    assert "not configured" in result.lower()

@pytest.mark.asyncio
async def test_handle_weather_valid_response(mocker):
    """Tool correctly parses API response."""
    mock_resp = {"main": {"temp": 291.15, "humidity": 60}, "weather": [{"main": "Cloudy"}]}
    mocker.patch("aiohttp.ClientSession.get", return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value=mock_resp)
    ))

    result = await handle_weather(
        toolcall=None,
        args={"city": "Paris"},
        rcx=None,
        setup={"OPENWEATHER_API_KEY": "test-key"},
    )
    data = json.loads(result)
    assert data["temp_c"] == pytest.approx(18, rel=0.1)
    assert data["condition"] == "Cloudy"

def test_weather_tool_schema():
    """Tool definition has required fields."""
    assert WEATHER_TOOL.name == "check_weather"
    assert "city" in str(WEATHER_TOOL.parameters)
```

**Unit test requirements:**
- Test error handling (missing config, API errors)
- Test response parsing with mocked external calls
- Test tool schema is valid
- Use `pytest` + `pytest-asyncio` + `pytest-mock`

### Stage 4: Install to Marketplace
```bash
export FLEXUS_API_BASEURL=http://127.0.0.1:8008
export FLEXUS_API_KEY=sk_alice_123456
python mybot/mybot_install.py --ws=solarsystem
```

### Stage 5: Scenario Test (Optional)
```bash
python -m mybot.mybot_bot --scenario mybot/mybot__s1.yaml
# Results in scenario-dumps/mybot__s1-*-score.yaml
```

If any stage fails → show error → ask claude_code to fix → retry.


## Scenario Testing

Scenarios verify bot behavior without needing real external services.

### How It Works

1. **Bot runs normally** - real model calls, real tool handlers
2. **Platform intercepts tool calls** - cloudtools detect `fcall_ft_btest_name` flag
3. **LLM generates fake responses** - based on happy path + tool source code
4. **LLM judge rates result** - compares actual vs expected trajectory (1-10)

**Key insight:** The bot code is REAL. The platform fakes external responses during tests.
No mock code needed in the bot itself.

### Scenario YAML Format

```yaml
# Naming: BOTNAME__SCENARIO.yaml (double underscore)
# e.g., frog__s1.yaml, productman__survey.yaml

judge_instructions: |
  Reward: Professional responses, using correct tools
  Penalize: Making up data, not asking clarifying questions
  Ignore: Minor formatting differences

messages:
- role: user
  content: "What's the weather in Paris?"
- role: assistant
  tool_calls:
  - id: call_12345
    type: function
    function:
      name: check_weather
      arguments: '{"city": "Paris"}'
- role: tool
  call_id: call_12345
  content: '{"temp_c": 18, "condition": "cloudy"}'
- role: assistant
  content: "It's 18°C and cloudy in Paris."

persona_marketable_name: weather_bot
```

### Score File Output

```yaml
# scenario-dumps/mybot__s1-*-score.yaml
actual_rating: 8        # 1-10 scale
actual_feedback: "Bot handled request correctly..."
shaky_human: 0          # Human messages not in happy path
shaky_tool: 1           # Tool responses LLM had to invent
stop_reason: "goal_achieved"
```

**Rating scale:**
- 1-4: Poor, doesn't solve the problem
- 5-7: Acceptable but has issues
- 8-9: High quality
- 10: Perfect


## What BOB Creates vs What User Configures

### BOB Creates (Real Code)

```python
# mybot_bot.py - REAL implementation, not mocks

WEATHER_TOOL = CloudTool(
    name="check_weather",
    description="Get weather for a city",
    parameters={...}
)

async def handle_weather(toolcall, args, rcx, setup):
    city = args.get("city")
    api_key = setup.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not configured"

    async with aiohttp.ClientSession() as session:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        async with session.get(url) as resp:
            data = await resp.json()
            return json.dumps({
                "temp_c": data["main"]["temp"] - 273.15,
                "condition": data["weather"][0]["main"],
            })
```

### User Configures After Deployment

1. Merge PR
2. Run install script: `python mybot_install.py --ws=myworkspace`
3. In Flexus UI → Bot Setup → Enter `OPENWEATHER_API_KEY`
4. Send test message to verify real API works


## What BOB Cannot Test

| Gap | Why | User Action |
|-----|-----|-------------|
| Real API calls | No credentials in dev container | Configure API keys in UI after install |
| Slack/Discord | OAuth requires browser | Complete OAuth flow in UI |
| Email sending | Could get banned | Test manually with caution |
| Webhooks | No public URL | Deploy first, then test |


## BOB's Post-Creation Message

After creating a bot, BOB should tell the user:

```
✅ Bot created and validated!

Syntax: PASS
Imports: PASS
Unit Tests: 3/3 PASS
Scenario: 8/10

I've verified the code structure. However, I cannot test:
- Real API connections (configure API keys after deployment)
- Messenger integrations (complete OAuth in the UI)

After merging the PR:
1. Install: python mybot_install.py --ws=your_workspace
2. Configure API keys in bot setup UI
3. Send a test message to verify real behavior
```


## Creating Scenarios from Real Chats

After a successful conversation in the UI:
1. Thread menu → "Create Scenario"
2. Backend creates kanban task for BOB
3. BOB proposes `judge_instructions` based on conversation
4. BOB creates `mybot__s2.yaml` and submits PR


## Implementation Checklist

- [ ] BOB runs syntax/import checks after claude_code
- [ ] BOB creates unit tests for each custom tool
- [ ] BOB runs pytest and fixes failures
- [ ] BOB runs install test with inline env vars
- [ ] BOB generates scenario YAML with judge_instructions
- [ ] BOB reads score.yaml and reports results
- [ ] BOB informs user what cannot be tested
