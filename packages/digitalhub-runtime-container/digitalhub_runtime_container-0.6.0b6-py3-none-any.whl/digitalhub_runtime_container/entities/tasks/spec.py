from __future__ import annotations

from digitalhub_core.entities.tasks.spec import TaskParamsK8s, TaskSpecK8s
from digitalhub_runtime_container.entities.tasks.models import CorePort


class TaskSpecJob(TaskSpecK8s):
    """Task Job specification."""

    def __init__(
        self,
        function: str,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)
        self.backoff_limit = kwargs.get("backoff_limit")
        self.schedule = kwargs.get("schedule")


class TaskParamsJob(TaskParamsK8s):
    """
    TaskParamsJob model.
    """

    backoff_limit: int = None
    """Backoff limit."""

    schedule: str = None
    """Schedule."""


class TaskSpecDeploy(TaskSpecK8s):
    """Task Deploy specification."""

    def __init__(
        self,
        function: str,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)
        self.replicas = kwargs.get("replicas")


class TaskParamsDeploy(TaskParamsK8s):
    """
    TaskParamsDeploy model.
    """

    replicas: int = None
    """Replicas."""


class TaskSpecServe(TaskSpecK8s):
    """Task Serve specification."""

    def __init__(
        self,
        function: str,
        service_ports: list[CorePort] | None = None,
        service_type: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)
        self.service_ports = service_ports
        self.service_type = service_type
        self.replicas = kwargs.get("replicas")


class TaskParamsServe(TaskParamsK8s):
    """
    TaskParamsServe model.
    """

    replicas: int = None
    """Replicas."""

    service_ports: list[CorePort] = None
    """Service ports mapper."""

    service_type: str = None
    """Service type."""


class TaskSpecBuild(TaskSpecK8s):
    """Task Build specification."""

    def __init__(
        self,
        function: str,
        **kwargs,
    ) -> None:
        super().__init__(function, **kwargs)
        self.instructions = kwargs.get("instructions")


class TaskParamsBuild(TaskParamsK8s):
    """
    TaskParamsBuild model.
    """

    instructions: list[str] = None
    """Build instructions."""
