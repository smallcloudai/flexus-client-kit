# Telegram GroupMod

A Telegram bot for group moderation, built on Flexus.


## Functions

### Message Filtering
- Delete messages matching custom word/phrase blocklist
- Block links except from whitelisted domains
- Auto-delete excessive forwarded messages or spam patterns

### New Member Gating
- Challenge new joins with a captcha or simple question
- Kick users who don't pass within a timeout
- Optional welcome message after verification

### User Moderation
- Warn, mute, kick, or ban users via admin commands
- Auto-escalation: warn → mute → ban after repeated violations
- Track per-user warning history

### Logging
- Log all mod actions (who did what, when) to a policy document
- Log deleted messages for admin review
- Daily summary report of moderation activity



## Choice of Tooling

Flexus has:
 * ERP database including CRM, the CrmContact and CrmActivity tables are of particular interest.
 * Bot settings aka user preferences, always the first message in every bot thread, meant to seldom change, only after a malfunction or a setup
   problem is detected.
 * MongoDB database personal for each bot, personal meaning there's no convenient way to share a file with another bot. It's suitable for
   temporary files, data persistence, reports, running random python code -- there's an isolation mechanism that allows to run a model-generated
   script and receive the answer via mongodb.
 * Policy documents accessible via fi_pdoc.py, the main way for bots to communicate, result of one bot often the input for the other. Those change
   often, seeking optimal solution.
 * Kanban tasks, accessible via ckit_kanban.bot_kanban_post_into_inbox() kanban_task_update_details(), completed tasks summaries are visible in
   context, making it work like medium-term memory.


## Milestone 1

Assignment of functions to tooling:
 * **Bot settings** — blocklist words/phrases, whitelisted link domains, captcha on/off, welcome message text,
   escalation thresholds (warns before mute, mutes before ban), moderation rules, offtopic policy.
   These rarely change.
 * **MongoDB** — per-user warning history (user_id, reason, timestamp), deleted message log, mute/ban records.
   High-write, append-heavy data that doesn't need to be shared with other bots.
   Write reports mongo_store_file() into root, /report-20260215-GROUPNAME.html
 * **Policy documents** — not used.
 * **Kanban** — Most of the moderation actions are reactive and instant. But also accumulate messages into a buffer,
   after bot restart re-accumulate the buffer by reading via telegram API.
   Each hour post an inbox task to review the buffer, this activates the bot = starts a chat thread.
   Task details should have the buffer in a text form (who said what), or maybe json form.
   Bot can decide there if additional deletes (offtopic is only detectable by a model) or bans needed.
 * **ERP/CRM** — not used. Group members are not CRM contacts.


## Milestone 2

 * **ERP/CRM** — There is an option in bot settings, to turn on sync from telegram chat to CrmContact and CrmActivity.
   Each private messaging session, significan activity within hour-long buffer turns into a CrmActivity record.
 * When joining group, bot asks questions that help to create non-trivial CrmContact, like interests, position of that person.

