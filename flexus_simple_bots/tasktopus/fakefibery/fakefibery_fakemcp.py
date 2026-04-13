import json
import copy
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("fakefibery")


@dataclass
class FakeTask:
    task_id: str
    board: str
    title: str
    state: str
    assignees: list[str]           # person ids
    priority: str = "medium"       # low/medium/high/blocker
    effort: str = ""               # xs/s/m/l/xl
    description: str = ""
    depends_on: list[str] = field(default_factory=list)   # task ids
    sprint: str = ""
    due_date: str = ""             # YYYY-MM-DD or ""
    created_ts: float = 0
    modified_ts: float = 0
    tags: list[str] = field(default_factory=list)


@dataclass
class FakePerson:
    person_id: str
    name: str
    email: str
    role: str = "member"           # admin/member


@dataclass
class FakeBoard:
    board_id: str
    name: str
    states: list[str]              # ordered workflow: ["backlog", "todo", "in_progress", "done", "archived"]
    task_prefix: str = ""          # e.g. "SD" -> SD-42


@dataclass
class FakeDocument:
    doc_id: str
    path: str                      # e.g. "/engineering/runbook"
    title: str
    content: str
    board: str = ""                # attached to board or ""
    task_id: str = ""              # attached to task or ""


FUNCTIONS = {
    "list_people": {
        "description": "List all workspace members.",
        "args": {},
    },
    "list_boards": {
        "description": "List all boards with their workflow states.",
        "args": {},
    },
    "list_tasks": {
        "description": "List tasks with optional filters. Returns up to 100 tasks sorted by modified_ts desc.",
        "args": {
            "type": "object",
            "properties": {
                "board": {"type": "string", "description": "Filter by board name (exact match)"},
                "assignee": {"type": "string", "description": "Filter by person_id of assignee"},
                "state": {"type": "string", "description": "Filter by state name (exact match)"},
                "states_not": {"type": "array", "items": {"type": "string"}, "description": "Exclude these states"},
                "tag": {"type": "string", "description": "Filter by tag"},
                "text": {"type": "string", "description": "Search title and description (case-insensitive substring)"},
                "since_days": {"type": "integer", "description": "Only tasks modified within last N days"},
                "stale_days": {"type": "integer", "description": "Only tasks NOT modified in last N days"},
                "limit": {"type": "integer", "description": "Max results (default 100)"},
            },
        },
    },
    "get_task": {
        "description": "Get full details of a single task by task_id, including description, comments, dependencies.",
        "args": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
            },
            "required": ["task_id"],
        },
    },
    "set_task_state": {
        "description": "Move a task to a new workflow state.",
        "args": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "state": {"type": "string", "description": "New state name (must be valid for the board)"},
            },
            "required": ["task_id", "state"],
        },
    },
    "update_task": {
        "description": "Update task fields: assignees, priority, effort, due_date, sprint, tags, description, title, depends_on.",
        "args": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
                "assignees": {"type": "array", "items": {"type": "string"}, "description": "Replace assignee list (person_ids)"},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "blocker"]},
                "effort": {"type": "string", "enum": ["xs", "s", "m", "l", "xl"]},
                "due_date": {"type": "string", "description": "YYYY-MM-DD or empty to clear"},
                "sprint": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "description": {"type": "string"},
                "title": {"type": "string"},
                "depends_on": {"type": "array", "items": {"type": "string"}, "description": "Task IDs this task depends on"},
            },
            "required": ["task_id"],
        },
    },
    "create_task": {
        "description": "Create a new task on a board.",
        "args": {
            "type": "object",
            "properties": {
                "board": {"type": "string", "description": "Board name"},
                "title": {"type": "string"},
                "state": {"type": "string", "description": "Initial state (default: first state of the board)"},
                "assignees": {"type": "array", "items": {"type": "string"}},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "blocker"]},
                "effort": {"type": "string", "enum": ["xs", "s", "m", "l", "xl"]},
                "due_date": {"type": "string"},
                "description": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "depends_on": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["board", "title"],
        },
    },
    "search": {
        "description": "BM25 keyword search across tasks and documents. Returns ranked results.",
        "args": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords"},
                "scope": {"type": "string", "enum": ["tasks", "docs", "all"], "description": "What to search (default: all)"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["query"],
        },
    },
    "list_documents": {
        "description": "List knowledge documents, optionally filtered by path prefix.",
        "args": {
            "type": "object",
            "properties": {
                "path_prefix": {"type": "string", "description": "Filter by path prefix, e.g. '/engineering'"},
            },
        },
    },
    "get_document": {
        "description": "Read full content of a knowledge document.",
        "args": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "string", "description": "Document ID"},
            },
            "required": ["doc_id"],
        },
    },
    "activity_log": {
        "description": "Recent changes across workspace: task state changes, assignments, edits. Returns last N events.",
        "args": {
            "type": "object",
            "properties": {
                "person_id": {"type": "string", "description": "Filter by person"},
                "board": {"type": "string", "description": "Filter by board"},
                "since_days": {"type": "integer", "description": "Only events within last N days (default 7)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"},
            },
        },
    },
}


@dataclass
class ActivityEvent:
    ts: float
    person_id: str
    action: str       # "state_change", "assigned", "created", "updated", "commented"
    task_id: str
    detail: str       # e.g. "todo -> in_progress"


class FakeFibery:
    def __init__(
        self,
        people: list[FakePerson],
        boards: list[FakeBoard],
        tasks: list[FakeTask],
        documents: list[FakeDocument],
        activity: list[ActivityEvent],
        now_ts: float = 0,
    ):
        self.people = {p.person_id: p for p in people}
        self.boards = {b.name: b for b in boards}
        self.tasks: dict[str, FakeTask] = {}
        self.documents = {d.doc_id: d for d in documents}
        self.activity = list(activity)
        self.now_ts = now_ts or time.time()
        self._next_id = 1000
        for t in tasks:
            if not t.created_ts:
                t.created_ts = self.now_ts - 86400
            if not t.modified_ts:
                t.modified_ts = t.created_ts
            self.tasks[t.task_id] = t

    def _new_id(self) -> str:
        self._next_id += 1
        return str(self._next_id)

    def _person_name(self, pid: str) -> str:
        p = self.people.get(pid)
        return p.name if p else pid

    def _task_to_dict(self, t: FakeTask, full: bool = False) -> dict:
        d = {
            "task_id": t.task_id,
            "board": t.board,
            "title": t.title,
            "state": t.state,
            "assignees": [{"person_id": a, "name": self._person_name(a)} for a in t.assignees],
            "priority": t.priority,
            "tags": t.tags,
            "due_date": t.due_date,
            "modified_ts": t.modified_ts,
        }
        if full:
            d.update({
                "effort": t.effort,
                "description": t.description,
                "depends_on": t.depends_on,
                "sprint": t.sprint,
                "created_ts": t.created_ts,
            })
        return d

    def handle(self, op: str, name: str, args: dict) -> str:
        if op == "list":
            lines = []
            for fn, info in FUNCTIONS.items():
                desc = info["description"][:60]
                if len(info["description"]) > 60:
                    desc += "…"
                lines.append(json.dumps({"function": fn, "description": desc}, ensure_ascii=False))
            return "\n".join(lines)

        if op == "help":
            if not name:
                return "Missing name parameter"
            info = FUNCTIONS.get(name)
            if not info:
                return "Unknown function '%s'" % name
            return json.dumps({"function": name, "description": info["description"], "args_schema": info["args"]}, indent=2, ensure_ascii=False)

        if op == "call":
            if not name:
                return "Missing name parameter"
            fn = getattr(self, "_call_" + name, None)
            if not fn:
                return "Unknown function '%s'" % name
            try:
                return fn(args or {})
            except Exception as e:
                return "Error: %s" % e

        return "Unknown op '%s', use list/help/call" % op

    # --- function implementations ---

    def _call_list_people(self, args: dict) -> str:
        rows = [{"person_id": p.person_id, "name": p.name, "email": p.email, "role": p.role} for p in self.people.values()]
        return json.dumps(rows, ensure_ascii=False)

    def _call_list_boards(self, args: dict) -> str:
        rows = []
        for b in self.boards.values():
            task_count = sum(1 for t in self.tasks.values() if t.board == b.name)
            rows.append({"board_id": b.board_id, "name": b.name, "states": b.states, "task_prefix": b.task_prefix, "task_count": task_count})
        return json.dumps(rows, ensure_ascii=False)

    def _call_list_tasks(self, args: dict) -> str:
        out = list(self.tasks.values())
        if v := args.get("board"):
            out = [t for t in out if t.board == v]
        if v := args.get("assignee"):
            out = [t for t in out if v in t.assignees]
        if v := args.get("state"):
            out = [t for t in out if t.state == v]
        if v := args.get("states_not"):
            out = [t for t in out if t.state not in v]
        if v := args.get("tag"):
            out = [t for t in out if v in t.tags]
        if v := args.get("text"):
            low = v.lower()
            out = [t for t in out if low in t.title.lower() or low in t.description.lower()]
        if v := args.get("since_days"):
            cutoff = self.now_ts - v * 86400
            out = [t for t in out if t.modified_ts >= cutoff]
        if v := args.get("stale_days"):
            cutoff = self.now_ts - v * 86400
            out = [t for t in out if t.modified_ts < cutoff]
        out.sort(key=lambda t: t.modified_ts, reverse=True)
        limit = args.get("limit", 100)
        out = out[:limit]
        return json.dumps([self._task_to_dict(t) for t in out], ensure_ascii=False)

    def _call_get_task(self, args: dict) -> str:
        t = self.tasks.get(args.get("task_id", ""))
        if not t:
            return "Error: task not found"
        return json.dumps(self._task_to_dict(t, full=True), ensure_ascii=False)

    def _call_set_task_state(self, args: dict) -> str:
        t = self.tasks.get(args.get("task_id", ""))
        if not t:
            return "Error: task not found"
        new_state = args.get("state", "")
        board = self.boards.get(t.board)
        if board and new_state not in board.states:
            return "Error: invalid state '%s' for board '%s', valid: %s" % (new_state, t.board, board.states)
        old_state = t.state
        t.state = new_state
        t.modified_ts = self.now_ts
        self.activity.append(ActivityEvent(self.now_ts, self.me_person_id, "state_change", t.task_id, "%s -> %s" % (old_state, new_state)))
        return json.dumps({"ok": True, "task_id": t.task_id, "old_state": old_state, "new_state": new_state})

    def _call_update_task(self, args: dict) -> str:
        t = self.tasks.get(args.get("task_id", ""))
        if not t:
            return "Error: task not found"
        changed = []
        for f in ["assignees", "priority", "effort", "due_date", "sprint", "tags", "description", "title", "depends_on"]:
            if f in args:
                old = getattr(t, f)
                setattr(t, f, args[f])
                changed.append(f)
                if f == "assignees":
                    self.activity.append(ActivityEvent(self.now_ts, self.me_person_id, "assigned", t.task_id, "assignees: %s" % args[f]))
        if changed:
            t.modified_ts = self.now_ts
            self.activity.append(ActivityEvent(self.now_ts, self.me_person_id, "updated", t.task_id, "fields: %s" % ", ".join(changed)))
        return json.dumps({"ok": True, "task_id": t.task_id, "changed": changed})

    def _call_create_task(self, args: dict) -> str:
        board_name = args.get("board", "")
        board = self.boards.get(board_name)
        if not board:
            return "Error: board '%s' not found" % board_name
        title = args.get("title", "")
        if not title:
            return "Error: title required"
        state = args.get("state", board.states[0])
        if state not in board.states:
            return "Error: invalid state '%s' for board '%s'" % (state, board_name)
        tid = "%s-%s" % (board.task_prefix, self._next_id) if board.task_prefix else str(self._next_id)
        self._next_id += 1
        t = FakeTask(
            task_id=tid, board=board_name, title=title, state=state,
            assignees=args.get("assignees", []),
            priority=args.get("priority", "medium"),
            effort=args.get("effort", ""),
            description=args.get("description", ""),
            depends_on=args.get("depends_on", []),
            due_date=args.get("due_date", ""),
            tags=args.get("tags", []),
            created_ts=self.now_ts,
            modified_ts=self.now_ts,
        )
        self.tasks[t.task_id] = t
        self.activity.append(ActivityEvent(self.now_ts, self.me_person_id, "created", t.task_id, "created: %s" % title))
        return json.dumps({"ok": True, "task_id": t.task_id})

    def _call_search(self, args: dict) -> str:
        query = args.get("query", "").lower()
        if not query:
            return "Error: query required"
        scope = args.get("scope", "all")
        limit = args.get("limit", 20)
        results = []
        words = query.split()
        if scope in ("tasks", "all"):
            for t in self.tasks.values():
                blob = (t.title + " " + t.description + " " + " ".join(t.tags)).lower()
                score = sum(blob.count(w) for w in words)
                if score > 0:
                    results.append({"type": "task", "task_id": t.task_id, "title": t.title, "board": t.board, "state": t.state, "score": score})
        if scope in ("docs", "all"):
            for d in self.documents.values():
                blob = (d.title + " " + d.content + " " + d.path).lower()
                score = sum(blob.count(w) for w in words)
                if score > 0:
                    results.append({"type": "doc", "doc_id": d.doc_id, "path": d.path, "title": d.title, "score": score})
        results.sort(key=lambda r: r["score"], reverse=True)
        return json.dumps(results[:limit], ensure_ascii=False)

    def _call_list_documents(self, args: dict) -> str:
        prefix = args.get("path_prefix", "")
        docs = self.documents.values()
        if prefix:
            docs = [d for d in docs if d.path.startswith(prefix)]
        return json.dumps([{"doc_id": d.doc_id, "path": d.path, "title": d.title, "board": d.board, "task_id": d.task_id} for d in docs], ensure_ascii=False)

    def _call_get_document(self, args: dict) -> str:
        d = self.documents.get(args.get("doc_id", ""))
        if not d:
            return "Error: document not found"
        return json.dumps({"doc_id": d.doc_id, "path": d.path, "title": d.title, "content": d.content, "board": d.board, "task_id": d.task_id}, ensure_ascii=False)

    def _call_activity_log(self, args: dict) -> str:
        out = list(self.activity)
        if v := args.get("person_id"):
            out = [e for e in out if e.person_id == v]
        if v := args.get("board"):
            out = [e for e in out if self.tasks.get(e.task_id, FakeTask("", v, "", "", [])).board == v]
        since_days = args.get("since_days", 7)
        cutoff = self.now_ts - since_days * 86400
        out = [e for e in out if e.ts >= cutoff]
        out.sort(key=lambda e: e.ts, reverse=True)
        limit = args.get("limit", 50)
        out = out[:limit]
        rows = []
        for e in out:
            rows.append({
                "ts": e.ts,
                "person": self._person_name(e.person_id),
                "action": e.action,
                "task_id": e.task_id,
                "task_title": self.tasks[e.task_id].title if e.task_id in self.tasks else "",
                "detail": e.detail,
            })
        return json.dumps(rows, ensure_ascii=False)


FAKEFIBERY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="mcp_taskman",
    description='Project tracker. Start with op="list" to see available functions, then op="help" name="function_name" for details, then op="call" name="function_name" args={...}.',
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["list", "help", "call"]},
            "name": {"type": "string", "description": "Function name"},
            "args": {"type": "object", "description": 'Function arguments, use op="help" first'},
        },
    },
)
