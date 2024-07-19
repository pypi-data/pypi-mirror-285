from __future__ import annotations

from typing import Literal

from digitalhub_core.entities.tasks.spec import TaskParamsK8s, TaskSpecK8s


class TaskSpecJob(TaskSpecK8s):
    """Task Job specification."""

    def __init__(
        self,
        function: str,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)

        self.backoff_limit = kwargs.get("backoff_limit")


class TaskParamsJob(TaskParamsK8s):
    """
    TaskParamsJob model.
    """

    backoff_limit: int = None
    """Backoff limit."""


class TaskSpecBuild(TaskSpecK8s):
    """Task Build specification."""

    def __init__(
        self,
        function: str,
        instructions: list | None = None,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)

        self.instructions = instructions


class TaskParamsBuild(TaskParamsK8s):
    """
    TaskParamsBuild model.
    """

    instructions: list[str] = None
    """Build instructions."""


class TaskSpecServe(TaskSpecK8s):
    """Task Serve specification."""

    def __init__(
        self,
        function: str,
        replicas: int | None = None,
        service_type: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)

        self.replicas = replicas
        self.service_type = service_type


class TaskParamsServe(TaskParamsK8s):
    """
    TaskParamsServe model.
    """

    replicas: int = None
    service_type: Literal["ClusterIP", "NodePort", "LoadBalancer"] = "NodePort"
