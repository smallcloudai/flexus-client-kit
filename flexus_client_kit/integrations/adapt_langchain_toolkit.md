Adapt the following langchain toolkit to this flexus repo, take a look at another langchain adapted toolkits as inspiration, like @flexus_client_kit/integrations/fi_google_calendar.py

### Phase 1. Research

Research for all needed information, relevant packages, tools that will be added, how auth needs to be handled. Which configuration is needed

### Phase 2. Implementation

1. If there is just one tool, as it is, if there is more, then do like fi_google_calendar.py and compress them in one using op and args.
2. If the auth is with oauth2, do it like in fi_google_calendar.py so user has to click the link to give permission, if it is api key or similar variable, add it in the bot setup, if it only needs one api key from our side (flexus, the system), just use the env var.
3. Ensure to follow rules in @AGENTS.md and follow the coding standards in this repo.

### Phase 3. Prepare for testing

If it needs oauth, configure the oauth provider in flexus, and set up the CLIENT_ID and CLIENT_SECRET as env vars (also put them in .env of flexus/).

Start the backend `python -m flexus_backend.flexus_v1_server --dev`

Then, add the integration to frog_bot to test it, reinstall frog after that, `python -m flexus_simple_bots.frog.frog_install --ws solarsystem` and configure `persona_setup` of the bot in database if needed.

Create a happy trajectory, that showcases how to use the tool in a simple way, take an inspiration from @flexus_simple_bots/admonster/admonster_s1.yaml

### Phase 4. Testing

Test the tool using the created trajectory:

`python -m flexus_simple_bots.frog.frog_bot --scenario path/to/trajectory`

If it is oauth, it should fail and provide a link to authorize, print that link so I can authorize it, then try again

If there is any errors, fix them, reinstall the bot, and rerun the trajectory until you fix the problem, if a change/restart in the bot definition is made, reinstall it, if a change in back end is made, restart it.

Continue until trajectory runs without errors and the tool works as expected.

The langchain toolkit to adapt and the variables needed are:

{FILL_THIS}