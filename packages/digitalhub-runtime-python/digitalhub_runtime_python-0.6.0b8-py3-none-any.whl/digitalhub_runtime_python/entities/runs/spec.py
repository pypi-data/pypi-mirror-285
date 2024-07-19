from __future__ import annotations

from digitalhub_ml.entities.runs.spec import RunParamsMl, RunSpecMl


class RunSpecPython(RunSpecMl):
    """Run Python specification."""

    def __init__(
        self,
        task: str,
        local_execution: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(task, local_execution)

        self.source = kwargs.get("source")
        self.image = kwargs.get("image")
        self.base_image = kwargs.get("base_image")
        self.python_version = kwargs.get("python_version")
        self.requirements = kwargs.get("requirements")

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

        # Task job

        # Task build
        self.instructions = kwargs.get("instructions")

        self.inputs = kwargs.get("inputs")
        self.outputs = kwargs.get("outputs")
        self.parameters = kwargs.get("parameters")


class RunParamsPython(RunParamsMl):
    """Run Python parameters."""

    # Function parameters
    source: dict = None
    image: str = None
    base_image: str = None
    python_version: str = None
    requirements: list = None

    # Task parameters
    function: str = None
    node_selector: list[dict] = None
    volumes: list[dict] = None
    resources: list[dict] = None
    affinity: dict = None
    tolerations: list[dict] = None
    env: list[dict] = None
    secrets: list[str] = None

    # Task job
    backoff_limit: int = None

    # Task serve
    service_type: str = None
    replicas: int = None

    # Task build
    instructions: list[str] = None

    # Run parameters
    inputs: dict = None
    outputs: dict = None
    parameters: dict = None
