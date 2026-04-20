import json

from flexus_simple_bots.tasktopus.fakefibery import fakefibery_fakemcp as ff


# Celebrity Wedding at a half-finished volcano resort.
# Billionaire booked a wedding for 200 VIP guests in 10 days, forcing the team
# to get an unfinished resort operational. Data is a Wednesday morning snapshot.

# FakeFibery vs Real Fibery: Structural Diff
#
# Discovery overhead: Real Fibery requires a multi-step discovery dance before doing anything useful. The model must call schema to find spaces/databases, then schema_detailed to learn field names, then figure out
# the query syntax. In fibery_struggle.yaml, the model spent ~30 tool calls just trying to read one Gantt view and mostly failed. FakeFibery has list and help that return function signatures directly — one call to
# discover, one to understand args, one to execute.
#
# Query language: Fibery uses a Datalog-like query language with q/from, q/select, q/where, parameter references ($paramName), and nested sub-queries for collections. Every value in a where clause must be
# parameterized or the query silently fails. FakeFibery has named functions with simple JSON args — list_tasks(board="Engineering", state="todo").
#
# Naming: Fibery uses Space/Database namespacing (Software Development/Task), emoji-prefixed enum values (🎉 Done, 🔴 BLOCKER), and fields like workflow/state with type names like workflow/state_Software
# Development/Task. FakeFibery uses plain strings: state="in_progress", board="Engineering".
#
# Schema fragmentation: Real Fibery has tasks scattered across 5+ databases (Software Development/Task, Product/Task, Community/Task, Marketing and Growth/Daily Tasks, Community/Daily Task), each with different
# field sets, different workflow states, different relation names. FakeFibery has one tasks collection with uniform fields across boards.
#
# Documents: Fibery documents are opaque blobs accessed via secret tokens — you query the entity, get a document secret, then call get_documents_content with that secret. FakeFibery documents have a doc_id and
# content you can read directly.
#
# Views: Fibery has board/gantt/grid/timeline views as first-class objects with their own IDs, configs, and a separate fetch_view_data endpoint. In fibery_struggle.yaml, query_views kept returning validation errors
# (missing totalCount), a bug the model couldn't work around. FakeFibery has no view concept — you just query tasks with filters.
#
# The leap-of-faith bridge (from PLAN.md): the idea is that if the bot learns good behavior on FakeFibery's clean API, a /tasktopus/cheatsheet policy doc can map list_tasks(state="done") to the real Fibery
# incantation query(q/from: "Software Development/Task", q/where: ["q/equals-ignoring-case?", ["workflow/state", "enum/name"], "$s"], params: {"$s": "🎉 Done"}). The cheatsheet absorbs the workspace-specific
# weirdness so the prompt doesn't have to.


DAY = 86400
NOW = 1750000000.0   # ~2025-06-15 morning-ish, exact value doesn't matter


def build() -> ff.FakeFibery:
    people = [
        ff.FakePerson("elena",  "Elena Voss",   "elena@volcresort.com",  "admin"),   # project lead
        ff.FakePerson("lucia",  "Lucia Ferrer", "lucia@volcresort.com"),              # head chef, overloaded
        ff.FakePerson("raj",    "Raj Anand",    "raj@volcresort.com"),                # structural engineer, idle
        ff.FakePerson("mika",   "Mika Chen",    "mika@volcresort.com"),               # marketing
        ff.FakePerson("tomas",  "Tomás Reyes",  "tomas@volcresort.com"),              # ops manager
        ff.FakePerson("jun",    "Jun Watanabe", "jun@volcresort.com"),                # IT / AV
        ff.FakePerson("priya",  "Priya Sharma", "priya@volcresort.com"),              # event coordinator
    ]

    boards = [
        ff.FakeBoard("b-eng",  "Engineering",  ["backlog", "todo", "in_progress", "review", "done", "archived"], task_prefix="ENG"),
        ff.FakeBoard("b-mkt",  "Marketing",    ["backlog", "todo", "in_progress", "done"], task_prefix="MKT"),
        ff.FakeBoard("b-ops",  "Operations",   ["backlog", "todo", "in_progress", "done", "archived"], task_prefix="OPS"),
        ff.FakeBoard("b-food", "Food & Drink", ["backlog", "todo", "in_progress", "done"], task_prefix="FD"),
    ]

    tasks = [
        # ── SIMILAR TASKS (milestone 2): wedding welcome kits, two boards, two owners ──
        ff.FakeTask("MKT-20", "Marketing", "Design wedding-themed welcome packets",
            state="in_progress", assignees=["mika"], priority="high", effort="m",
            description="Create branded welcome packets for 200 VIP guests. Include resort map, itinerary card, and personalized note from the couple.",
            due_date="2025-06-23", created_ts=NOW - 6*DAY, modified_ts=NOW - 2*DAY,
            tags=["wedding", "print"]),
        ff.FakeTask("OPS-30", "Operations", "Create personalized guest welcome kits",
            state="todo", assignees=["priya"], priority="high", effort="m",
            description="Assemble 200 welcome kits for VIP wedding guests. Each kit: welcome letter, schedule, local map, small gift. Coordinate with florist for dried flower insert.",
            due_date="2025-06-24", created_ts=NOW - 4*DAY, modified_ts=NOW - 4*DAY,
            tags=["wedding", "guests"]),

        # ── CONTRADICTORY / ZOMBIE pair: flower color flip-flop ──
        ff.FakeTask("OPS-31", "Operations", "Change flower arrangements to match lava sunset palette",
            state="in_progress", assignees=["priya"], priority="medium",
            description="Bride wants warm tones: deep orange, magma red, obsidian accents. Coordinate with Isla Flora vendor. Budget approved.",
            created_ts=NOW - 5*DAY, modified_ts=NOW - 3*DAY,
            tags=["wedding", "flowers"]),
        ff.FakeTask("OPS-32", "Operations", "Change flowers back to white",
            state="todo", assignees=["priya"], priority="high",
            description="Bride changed mind. All arrangements back to white & gold. Cancel the lava palette order ASAP before vendor charges cancellation fee.",
            created_ts=NOW - 1*DAY, modified_ts=NOW - 1*DAY,
            tags=["wedding", "flowers"]),

        # ── HOT POTATO (milestone 2): helicopter pad inspection, 4 reassignments ──
        ff.FakeTask("ENG-10", "Engineering", "Helicopter landing pad inspection",
            state="todo", assignees=[], priority="high", effort="m",
            description="VIP guests arriving by helicopter. Pad needs structural cert and night lighting check. Previous owner said 'not my area'.",
            due_date="2025-06-22", created_ts=NOW - 14*DAY, modified_ts=NOW - 1*DAY,
            tags=["safety", "wedding"]),

        # ── ZOMBIE: 3 months old brainstorm idea, never touched ──
        ff.FakeTask("MKT-05", "Marketing", "Research if volcano can be lit up at night for photos",
            state="backlog", assignees=[], priority="low",
            description="Idea from initial pitch meeting. Could we install temporary uplighting on the caldera rim? Would make incredible photos.",
            created_ts=NOW - 90*DAY, modified_ts=NOW - 90*DAY,
            tags=["brainstorm"]),

        # ── OVERLOADED PERSON: Lucia has 7 tasks, none updated in 4 days ──
        ff.FakeTask("FD-40", "Food & Drink", "Design 5-course wedding dinner menu",
            state="in_progress", assignees=["lucia"], priority="blocker", effort="l",
            description="Must accommodate 12 dietary restrictions from guest list. Bride wants 'volcanic theme' but nothing too gimmicky. Tasting scheduled in 3 days.",
            due_date="2025-06-20", created_ts=NOW - 10*DAY, modified_ts=NOW - 4*DAY,
            tags=["wedding", "menu"]),
        ff.FakeTask("FD-41", "Food & Drink", "Source high-end table linens",
            state="todo", assignees=["lucia"], priority="medium", effort="s",
            description="The art of table linen selection has long been a cornerstone of formal event planning, dating back to the great banquet halls of Renaissance Europe. In the context of a luxury volcanic resort wedding, the choice of linen speaks not merely to aesthetic preference but to a deeper philosophical commitment to tactile elegance and visual harmony. One must consider thread count, weave pattern, and the subtle interplay between fabric sheen and ambient volcanic light. Furthermore, the environmental considerations of sourcing sustainable textiles in a geologically active region present unique challenges that demand both creativity and conscientiousness.",
            created_ts=NOW - 3*DAY, modified_ts=NOW - 3*DAY,
            tags=["wedding", "decor"]),
        ff.FakeTask("FD-42", "Food & Drink", "Coordinate cocktail bar setup",
            state="todo", assignees=["lucia"], priority="medium", effort="m",
            description="Signature cocktails with volcano theme. Need bar equipment, glassware, ice sculptor for lava-shaped centerpiece. Bar area is on the terrace overlooking caldera.",
            due_date="2025-06-24", created_ts=NOW - 7*DAY, modified_ts=NOW - 5*DAY,
            tags=["wedding", "bar"]),
        ff.FakeTask("FD-43", "Food & Drink", "Arrange late-night snack station",
            state="backlog", assignees=["lucia"], priority="low", effort="s",
            description="Post-party food: sliders, fries, churros. Simple setup near dance floor.",
            created_ts=NOW - 7*DAY, modified_ts=NOW - 7*DAY),
        ff.FakeTask("FD-44", "Food & Drink", "Wedding cake procurement",
            state="in_progress", assignees=["lucia"], priority="high", effort="m",
            description="6-tier cake, white fondant with gold leaf. Vendor confirmed but delivery logistics to volcano island unclear. Cake cannot sit in heat.",
            due_date="2025-06-24", created_ts=NOW - 8*DAY, modified_ts=NOW - 4*DAY,
            tags=["wedding"]),
        ff.FakeTask("FD-45", "Food & Drink", "Staff catering for setup crew",
            state="todo", assignees=["lucia"], priority="low", effort="s",
            description="Feed 40 setup crew for 5 days leading up to wedding. Budget meal plan.",
            created_ts=NOW - 6*DAY, modified_ts=NOW - 6*DAY),
        ff.FakeTask("FD-46", "Food & Drink", "Allergen documentation for all dishes",
            state="todo", assignees=["lucia"], priority="high", effort="s",
            description="Legal requires allergen cards for every dish served. 12 guests have restrictions on file, need cross-referenced matrix.",
            due_date="2025-06-23", created_ts=NOW - 5*DAY, modified_ts=NOW - 5*DAY,
            tags=["wedding", "legal"]),

        # ── IDLE PERSON's obvious match: unassigned structural task ──
        ff.FakeTask("ENG-11", "Engineering", "Reinforce glass floor over lava tube",
            state="todo", assignees=[], priority="blocker", effort="l",
            description="The glass walkway above the lava tube is the wedding ceremony location. Structural load rating currently for 50 people, need cert for 200+ standing. Glass panels may need replacing.",
            due_date="2025-06-21", created_ts=NOW - 12*DAY, modified_ts=NOW - 8*DAY,
            tags=["safety", "wedding", "structural"]),

        # ── VAGUE DESCRIPTION: no useful info ──
        ff.FakeTask("OPS-33", "Operations", "Deal with the sound problem",
            state="todo", assignees=["jun"], priority="medium",
            description="",
            created_ts=NOW - 2*DAY, modified_ts=NOW - 2*DAY,
            tags=["wedding"]),

        # ── SLIPPED DEADLINE: was due 2 days ago, still in progress ──
        ff.FakeTask("OPS-34", "Operations", "Guest transportation logistics",
            state="in_progress", assignees=["tomas"], priority="high", effort="l",
            description="Ferries from mainland, helicopter shuttles for platinum guests, golf carts on-island. Schedule needs to handle 200 arrivals in a 4-hour window. Ferry company hasn't confirmed times.",
            due_date="2025-06-13", created_ts=NOW - 14*DAY, modified_ts=NOW - 3*DAY,
            tags=["wedding", "logistics"]),

        # ── FAST MOVER: done in 1 day (contrast for weekly summary) ──
        ff.FakeTask("OPS-35", "Operations", "Install temporary restrooms near ceremony site",
            state="done", assignees=["tomas"], priority="medium", effort="s",
            description="4 luxury portable units delivered and placed. Plumbing connected to temporary line.",
            created_ts=NOW - 2*DAY, modified_ts=NOW - 1*DAY,
            tags=["wedding"]),

        # ── NEEDS TESTER / REVIEWER: dev says done, no QA ──
        ff.FakeTask("ENG-12", "Engineering", "Online RSVP and seating chart system",
            state="review", assignees=["jun"], priority="high", effort="l",
            description="Web app for guests to RSVP, pick meal preference, see seating. Jun says code complete. Needs someone to test the full flow before going live, especially payment for +1 guests.",
            due_date="2025-06-19", created_ts=NOW - 20*DAY, modified_ts=NOW - 4*DAY,
            tags=["wedding", "tech"]),

        # ── STALE: assigned but no progress for 6 days ──
        ff.FakeTask("MKT-21", "Marketing", "Produce drone light show choreography",
            state="in_progress", assignees=["mika"], priority="high", effort="l",
            description="200-drone show spelling couple's initials over volcano. Vendor needs final choreography file in 5 days. Music sync with DJ required.",
            due_date="2025-06-22", created_ts=NOW - 10*DAY, modified_ts=NOW - 6*DAY,
            tags=["wedding", "entertainment"]),

        # ── ANOTHER STALE: Elena started it, got distracted ──
        ff.FakeTask("OPS-36", "Operations", "Security plan for VIP guests",
            state="in_progress", assignees=["elena"], priority="blocker", effort="l",
            description="Billionaire's security team sent requirements doc. Need perimeter plan, credential system, and coordination with local police. Elena started reviewing requirements but no updates since.",
            due_date="2025-06-20", created_ts=NOW - 9*DAY, modified_ts=NOW - 5*DAY,
            tags=["wedding", "security"]),

        # ── COMPLETED tasks for weekly summary variety ──
        ff.FakeTask("ENG-13", "Engineering", "Fix generator backup for main stage",
            state="done", assignees=["jun"], priority="high", effort="m",
            description="Replaced faulty transfer switch. Tested 30-second failover.",
            created_ts=NOW - 8*DAY, modified_ts=NOW - 3*DAY,
            tags=["infrastructure"]),
        ff.FakeTask("MKT-22", "Marketing", "Send save-the-date reminders to guest list",
            state="done", assignees=["mika"], priority="medium", effort="xs",
            description="Email blast to 200 guests with updated logistics info.",
            created_ts=NOW - 7*DAY, modified_ts=NOW - 6*DAY),
        ff.FakeTask("OPS-37", "Operations", "Confirm vendor insurance certificates",
            state="done", assignees=["tomas"], priority="medium", effort="s",
            description="All 8 vendors submitted valid certificates. Filed in shared drive.",
            created_ts=NOW - 10*DAY, modified_ts=NOW - 5*DAY,
            tags=["legal"]),
    ]

    documents = [
        ff.FakeDocument("doc-1", "/wedding/guest-list", "VIP Guest List",
            "200 confirmed guests. 12 dietary restrictions on file. 8 platinum-tier arriving by helicopter. Bride's family: 85. Groom's family: 60. Friends & colleagues: 55."),
        ff.FakeDocument("doc-2", "/wedding/vendor-contacts", "Vendor Contact Sheet",
            "Isla Flora (flowers): Maria, +1-555-0101. SkyDrone Inc (drone show): Jake, +1-555-0202. CakeCraft (wedding cake): Anya, +1-555-0303. LuxLoo (portable restrooms): completed. VolcFerry (ferry): Miguel, +1-555-0404 — UNCONFIRMED TIMES."),
        ff.FakeDocument("doc-3", "/wedding/bride-requirements", "Bride's Requirements (v4)",
            "Latest changes (v4): flowers back to white & gold. Ceremony on glass floor. Drone show must include proposal replay. Cake must have edible gold. Sound system: 'concert quality'. No plastic anywhere. Photographer needs lava glow at golden hour."),
        ff.FakeDocument("doc-4", "/engineering/safety-certs", "Safety Certification Status",
            "Glass floor: PENDING (rated for 50, need 200+). Helicopter pad: PENDING (no inspector assigned). Generator backup: PASSED. Temporary restrooms: PASSED. Fire suppression: PASSED."),
    ]

    # Activity log tells the story of the hot potato and general chaos
    activity = [
        # Hot potato: helicopter pad bounced between 4 people
        ff.ActivityEvent(NOW - 14*DAY, "elena",  "created",      "ENG-10", "created: Helicopter landing pad inspection"),
        ff.ActivityEvent(NOW - 13*DAY, "elena",  "assigned",     "ENG-10", "assignees: [raj]"),
        ff.ActivityEvent(NOW - 10*DAY, "raj",    "assigned",     "ENG-10", "assignees: [tomas]"),
        ff.ActivityEvent(NOW - 7*DAY,  "tomas",  "assigned",     "ENG-10", "assignees: [jun]"),
        ff.ActivityEvent(NOW - 3*DAY,  "jun",    "assigned",     "ENG-10", "assignees: [priya]"),
        ff.ActivityEvent(NOW - 1*DAY,  "priya",  "assigned",     "ENG-10", "assignees: []"),

        # Flower flip-flop
        ff.ActivityEvent(NOW - 5*DAY, "priya", "created",       "OPS-31", "created: Change flower arrangements to match lava sunset palette"),
        ff.ActivityEvent(NOW - 5*DAY, "priya", "state_change",  "OPS-31", "backlog -> in_progress"),
        ff.ActivityEvent(NOW - 1*DAY, "priya", "created",       "OPS-32", "created: Change flowers back to white"),

        # Fast mover: restrooms done in a day
        ff.ActivityEvent(NOW - 2*DAY, "tomas", "created",       "OPS-35", "created: Install temporary restrooms near ceremony site"),
        ff.ActivityEvent(NOW - 2*DAY, "tomas", "state_change",  "OPS-35", "backlog -> in_progress"),
        ff.ActivityEvent(NOW - 1*DAY, "tomas", "state_change",  "OPS-35", "in_progress -> done"),

        # Jun finished RSVP system, moved to review
        ff.ActivityEvent(NOW - 4*DAY, "jun", "state_change",    "ENG-12", "in_progress -> review"),

        # Completed tasks
        ff.ActivityEvent(NOW - 3*DAY, "jun",   "state_change",  "ENG-13", "in_progress -> done"),
        ff.ActivityEvent(NOW - 6*DAY, "mika",  "state_change",  "MKT-22", "in_progress -> done"),
        ff.ActivityEvent(NOW - 5*DAY, "tomas", "state_change",  "OPS-37", "in_progress -> done"),

        # Transportation slipping
        ff.ActivityEvent(NOW - 14*DAY, "tomas", "created",      "OPS-34", "created: Guest transportation logistics"),
        ff.ActivityEvent(NOW - 10*DAY, "tomas", "state_change", "OPS-34", "todo -> in_progress"),
    ]

    return ff.FakeFibery(
        people=people,
        boards=boards,
        tasks=tasks,
        documents=documents,
        activity=activity,
        now_ts=NOW,
    )


# Can model real-world drift: incorrect or missing info
people = json.dumps(json.loads("""
{
  "people-db": {
    "meta": {
      "created": "20250601",
      "updated": "20250610"
    },
    "users": {
      "elena": {
        "full-name": "Elena Voss",
        "avatar": "/v1/avatar/032-sheep_meditating.webp",
        "aka": {"taskman": "elena", "slack": "elena.voss", "telegram": "elenavoss"},
        "primary-messenger": "slack",
        "prefs": "Project lead. Prefers morning briefings, hates midday interruptions."
      },
      "lucia": {
        "full-name": "Lucia Ferrer",
        "avatar": "/v1/avatar/299-fox-sitting.webp",
        "aka": {"taskman": "lucia", "slack": "lucia.ferrer", "telegram": "luciaferrer"},
        "primary-messenger": "slack",
        "prefs": "Head chef. Kitchen hours 6:00–22:00, DMs OK anytime but she replies in bursts."
      },
      "raj": {
        "full-name": "Raj Anand",
        "avatar": "/v1/avatar/048-opossum_wearing_spacesuit.webp",
        "aka": {"taskman": "raj", "slack": "raj.anand", "telegram": ""},
        "prefs": "Structural engineer. Long reply latency, works best with very specific questions."
      }
    },
    "schema": {
      "users": {
        "type": "object",
        "order": 0,
        "title": "Tasktopus People Database",
        "additionalProperties": {
          "type": "object",
          "required": ["full-name"],
          "properties": {
            "full-name": {"type": "string", "order": 0, "title": "Full name"},
            "avatar":    {"type": "string", "order": 1, "title": "Avatar URL", "ui:avatar": true},
            "aka": {
              "type": "object",
              "order": 2,
              "title": "Messengers",
              "properties": {
                "taskman":  {"type": "string", "order": 0},
                "slack":    {"type": "string", "order": 1},
                "telegram": {"type": "string", "order": 2}
              },
              "additionalProperties": false
            },
            "primary-messenger": {"type": "string", "order": 3, "title": "Primary messenger", "enum": ["taskman", "slack", "telegram"]},
            "prefs": {"type": "string", "order": 4, "title": "Preferences", "ui:multiline": true}
          },
          "additionalProperties": false
        }
      }
    }
  }
}
"""), ensure_ascii=False, indent=2)


cheatsheet = "does not exist yet"
