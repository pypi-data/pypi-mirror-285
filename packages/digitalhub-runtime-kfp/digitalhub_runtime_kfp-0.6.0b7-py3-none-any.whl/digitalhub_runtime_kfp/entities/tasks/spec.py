from __future__ import annotations

from digitalhub_core.entities.tasks.spec import TaskParamsK8s, TaskSpecK8s


class TaskSpecPipeline(TaskSpecK8s):
    """Task Pipeline specification."""

    def __init__(self, function: str, workflow: str | None = None, schedule: str | None = None, **kwargs) -> None:
        super().__init__(function, **kwargs)
        self.workflow = workflow
        self.schedule = schedule


class TaskParamsPipeline(TaskParamsK8s):
    """
    TaskParamsPipeline model.
    """

    workflow: str = None
    """KFP workflow specification as YAML string."""

    schedule: str = None
    """KFP schedule specification."""
