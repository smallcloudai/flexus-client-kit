import json
import logging
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("executor_experiment_execution")

LAUNCH_EXPERIMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="launch_experiment",
    description="Reserved executor capability for launching experiment tactics into runtime systems.",
    parameters={
        "type": "object",
        "properties": {
            "experiment_id": {
                "type": "string",
                "description": "Experiment identifier or policy-document path segment to launch.",
            },
        },
        "required": ["experiment_id"],
        "additionalProperties": False,
    },
)


class IntegrationExperimentExecution:
    def __init__(
        self,
        pdoc_integration: Any,
        fclient: Any,
        facebook_integration: Any,
    ) -> None:
        self.pdoc_integration = pdoc_integration
        self.fclient = fclient
        self.facebook_integration = facebook_integration

    async def launch_experiment(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        args: Dict[str, Any],
    ) -> str:
        experiment_id = str((args or {}).get("experiment_id", "")).strip()
        if not experiment_id:
            return json.dumps(
                {
                    "ok": False,
                    "error_code": "INVALID_ARGS",
                    "message": "experiment_id is required.",
                },
                indent=2,
                ensure_ascii=False,
            )
        logger.info("launch_experiment placeholder invoked for %s", experiment_id)
        return json.dumps(
            {
                "ok": False,
                "error_code": "NOT_IMPLEMENTED",
                "message": (
                    "launch_experiment is intentionally reserved but not implemented yet. "
                    "Executor wiring is kept in place so the future module can replace this stub without bot rewiring."
                ),
                "experiment_id": experiment_id,
            },
            indent=2,
            ensure_ascii=False,
        )

    def track_experiment_task(self, task: Any) -> None:
        task_id = str(getattr(task, "ktask_id", "") or getattr(task, "id", "")).strip()
        if task_id:
            logger.debug("experiment_execution placeholder ignoring task %s", task_id)

    async def update_active_experiments(self) -> None:
        logger.debug("experiment_execution placeholder skipping active experiment update")
