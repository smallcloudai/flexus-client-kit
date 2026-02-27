import logging
import time
from typing import Any, Dict, Optional

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_bot_exec, ckit_cloudtool

logger = logging.getLogger("sched")


SCHED_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_schedule",
    description=(
        "Manage bot schedules — recurring triggers that activate the bot on a timer "
        "to sort inbox, work on tasks, or run any custom job. Start with op='help'."
    ),
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string"},
            "args": {"type": "object"},
        },
    },
)


HELP = """
flexus_schedule(op="list")
    List all schedules for this bot.

flexus_schedule(op="upsert", args={"sched_type": "SCHED_TODO", "sched_when": "EVERY:5m", "sched_first_question": "Work on the assigned task.", "sched_fexp_name": "default", "sched_enable": true})
    Create or update a schedule. Pass sched_id in args to update existing.
    sched_type: SCHED_TODO (run when todo has tasks), SCHED_TASK_SORT (run when inbox has tasks),
                SCHED_PICK_ONE (pick one inbox task), SCHED_ANY (time-based, always runs),
                SCHED_CREATE_TASK (time-based, creates a task)
    sched_when: EVERY:5m, EVERY:2h, WEEKDAYS:MO:TU:WE:TH:FR/09:00, MONTHDAY:1/09:00, MONTHDAY:-1/09:00

flexus_schedule(op="delete", args={"sched_id": "..."})
    Delete a schedule by sched_id.
"""


def _gql_error(e: Exception) -> str:
    if isinstance(e, gql.transport.exceptions.TransportQueryError):
        return f"Error: {e}"
    raise e


def _fmt_ts(ts: Any) -> str:
    if not ts:
        return "never"
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(float(ts)))


class IntegrationSched:
    def __init__(self, rcx: ckit_bot_exec.RobotContext):
        self.rcx = rcx

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP
        args, err = ckit_cloudtool.sanitize_args(model_produced_args)
        if err:
            return err
        op = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "op", "help")
        if op == "help":
            return HELP
        try:
            if op == "list":
                return await self._list()
            if op == "upsert":
                return await self._upsert(args, model_produced_args)
            if op == "delete":
                return await self._delete(args, model_produced_args)
            return f"Unknown op '{op}'\n\n{HELP}"
        except Exception as e:
            return _gql_error(e)

    async def _list(self) -> str:
        http = await self.rcx.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql("""
                    query SchedList($persona_id: String!) {
                        persona_schedule_list(persona_id: $persona_id) {
                            sched_id sched_type sched_when sched_fexp_name sched_enable
                            sched_marketplace sched_last_run_ts sched_first_question
                        }
                    }"""),
                variable_values={"persona_id": self.rcx.persona.persona_id},
            )
        records = result.get("persona_schedule_list", [])
        if not records:
            return "No schedules."
        lines = []
        for r in records:
            builtin = " [builtin]" if r.get("sched_marketplace") else ""
            enabled = "on" if r.get("sched_enable") else "off"
            lines.append(
                f"• {r['sched_id']}{builtin}: {r['sched_type']} {r['sched_when']}"
                f" fexp={r.get('sched_fexp_name')} {enabled} last_run={_fmt_ts(r.get('sched_last_run_ts'))}\n"
                f"  {r['sched_first_question']}"
            )
        return "\n".join(lines)

    async def _upsert(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        def get(k): return ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, k, None)

        required = {k: get(k) for k in ("sched_type", "sched_when", "sched_first_question")}
        if missing := [k for k, v in required.items() if not v]:
            return f"Error: missing required fields: {', '.join(missing)}"

        _VALID_TYPES = {"SCHED_TODO", "SCHED_TASK_SORT", "SCHED_PICK_ONE", "SCHED_ANY", "SCHED_CREATE_TASK"}
        if required["sched_type"] not in _VALID_TYPES:
            return f"Error: sched_type must be one of {', '.join(sorted(_VALID_TYPES))}"

        inp = {
            **required,
            "sched_fexp_name": get("sched_fexp_name") or "",
            "sched_enable": get("sched_enable") if get("sched_enable") is not None else True,
            "sched_marketplace": False,
        }
        if sched_id := get("sched_id"):
            inp["sched_id"] = sched_id

        http = await self.rcx.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql("""
                    mutation SchedUpsert($persona_id: String!, $input: PersonaScheduleInput!) {
                        persona_schedule_upsert(persona_id: $persona_id, input: $input) {
                            sched_id
                        }
                    }"""),
                variable_values={"persona_id": self.rcx.persona.persona_id, "input": inp},
            )
        sched_id = result.get("persona_schedule_upsert", {}).get("sched_id", "")
        return f"✅ Schedule {sched_id}"

    async def _delete(self, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
        sched_id = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "sched_id", "")
        if not sched_id:
            return "Error: sched_id required"
        http = await self.rcx.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation SchedDelete($sched_id: String!) {
                        persona_schedule_delete(sched_id: $sched_id)
                    }"""),
                variable_values={"sched_id": sched_id},
            )
        return f"✅ Deleted {sched_id}"
