from __future__ import annotations

from digitalhub_data.entities.runs.spec import RunParamsData, RunSpecData


class RunSpecDbt(RunSpecData):
    """Run Dbt specification."""

    def __init__(
        self,
        task: str,
        local_execution: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(task, local_execution)

        self.source = kwargs.get("source")

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

        self.inputs = kwargs.get("inputs")
        self.outputs = kwargs.get("outputs")
        self.parameters = kwargs.get("parameters")


class RunParamsDbt(RunParamsData):
    """Run Dbt parameters."""

    # Function parameters
    source: dict = None

    # Task parameters
    function: str = None
    node_selector: list[dict] = None
    volumes: list[dict] = None
    resources: dict = None
    affinity: dict = None
    tolerations: list[dict] = None
    env: list[dict] = None
    secrets: list[str] = None

    # Run parameters
    inputs: dict = None
    outputs: dict = None
    parameters: dict = None
