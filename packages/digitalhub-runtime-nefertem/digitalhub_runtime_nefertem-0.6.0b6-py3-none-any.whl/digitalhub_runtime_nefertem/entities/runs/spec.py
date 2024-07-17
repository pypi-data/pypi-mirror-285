from __future__ import annotations

from digitalhub_data.entities.runs.spec import RunParamsData, RunSpecData


class RunSpecNefertem(RunSpecData):
    """Run Nefertem specification."""

    def __init__(
        self,
        task: str,
        local_execution: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(task, local_execution)

        self.constraints = kwargs.get("constraints")
        self.error_report = kwargs.get("error_report")
        self.metrics = kwargs.get("metrics")

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
        self.framework = kwargs.get("framework")
        self.exec_args = kwargs.get("exec_args")
        self.parallel = kwargs.get("parallel")
        self.num_worker = kwargs.get("num_worker")

        self.inputs = kwargs.get("inputs")
        self.outputs = kwargs.get("outputs")
        self.parameters = kwargs.get("parameters")


class RunParamsNefertem(RunParamsData):
    """Run Nefertem parameters."""

    # Function parameters
    constraints: list[dict] = None
    error_report: str = None
    metrics: list[dict] = None

    # Task parameters
    function: str = None
    node_selector: list[dict] = None
    volumes: list[dict] = None
    resources: dict = None
    affinity: dict = None
    tolerations: list[dict] = None
    env: list[dict] = None
    secrets: list[str] = None
    framework: str = None
    exec_args: dict = None
    parallel: bool = None
    num_worker: int = None

    # Run parameters
    inputs: dict = None
    outputs: dict = None
    parameters: dict = None
