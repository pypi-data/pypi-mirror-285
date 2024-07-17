from __future__ import annotations

from digitalhub_core.entities.runs.spec import RunParams, RunSpec


class RunSpecContainer(RunSpec):
    """Run Container specification."""

    def __init__(
        self,
        task: str,
        local_execution: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(task, local_execution)

        self.image = kwargs.get("image")
        self.base_image = kwargs.get("base_image")
        self.command = kwargs.get("command")
        self.args = kwargs.get("args")

        self.function = kwargs.get("function")
        self.node_selector = kwargs.get("node_selector")
        self.volumes = kwargs.get("volumes")
        self.resources = kwargs.get("resources")
        self.affinity = kwargs.get("affinity")
        self.tolerations = kwargs.get("tolerations")
        self.env = kwargs.get("env")
        self.secrets = kwargs.get("secrets")

        self.backoff_limit = kwargs.get("backoff_limit")
        self.schedule = kwargs.get("schedule")

        self.replicas = kwargs.get("replicas")

        self.service_ports = kwargs.get("service_ports")
        self.service_type = kwargs.get("service_type")

        self.instructions = kwargs.get("instructions")


class RunParamsContainer(RunParams):
    """Run Container parameters."""

    # Function parameters
    image: str = None
    base_image: str = None
    command: str = None
    args: list[str] = None

    # Task parameters
    function: str = None
    node_selector: list[dict] = None
    volumes: list[dict] = None
    resources: dict = None
    affinity: dict = None
    tolerations: list[dict] = None
    env: list[dict] = None
    secrets: list[str] = None

    # Task job
    backoff_limit: int = None
    schedule: str = None

    # Task deploy
    replicas: int = None

    # Task serve
    service_ports: list[dict] = None
    service_type: str = None

    # Task build
    instructions: list[str] = None
