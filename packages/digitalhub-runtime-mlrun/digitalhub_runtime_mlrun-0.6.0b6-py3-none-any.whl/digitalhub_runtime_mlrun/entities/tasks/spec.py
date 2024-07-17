from __future__ import annotations

from digitalhub_core.entities.tasks.spec import TaskParamsK8s, TaskSpec, TaskSpecK8s


class TaskSpecJob(TaskSpecK8s):
    """Task Job specification."""


class TaskParamsJob(TaskParamsK8s):
    """
    TaskParamsJob model.
    """


class TaskSpecBuild(TaskSpec):
    """Task Build specification."""

    def __init__(
        self,
        function: str,
        target_image: str | None = None,
        commands: list[str] | None = None,
        force_build: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)
        self.target_image = target_image
        self.commands = commands
        self.force_build = force_build


class TaskParamsBuild(TaskParamsK8s):
    """
    TaskParamsBuild model.
    """

    target_image: str = None
    """Target image."""

    commands: list[str] = None
    """List of docker build (RUN) commands e.g. ['pip install pandas']"""

    force_build: bool = False
    """Force build even if no changes have been made."""
