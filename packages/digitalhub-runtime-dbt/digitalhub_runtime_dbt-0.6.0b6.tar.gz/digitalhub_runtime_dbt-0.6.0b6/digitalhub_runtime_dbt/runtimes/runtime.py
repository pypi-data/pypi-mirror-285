from __future__ import annotations

import typing
from typing import Callable

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.runtimes.base import Runtime
from digitalhub_core.utils.logger import LOGGER
from digitalhub_data.entities.dataitems.crud import dataitem_from_dict
from digitalhub_runtime_dbt.utils.cleanup import cleanup
from digitalhub_runtime_dbt.utils.configuration import (
    generate_dbt_profile_yml,
    generate_dbt_project_yml,
    generate_inputs_conf,
    generate_outputs_conf,
    get_output_table_name,
    save_function_source,
)
from digitalhub_runtime_dbt.utils.functions import transform
from digitalhub_runtime_dbt.utils.inputs import materialize_dataitem
from digitalhub_runtime_dbt.utils.outputs import build_status, create_dataitem_, parse_results

if typing.TYPE_CHECKING:
    from dbt.contracts.results import RunResult
    from digitalhub_core.runtimes.kind_registry import KindRegistry
    from digitalhub_data.entities.dataitems.entity._base import Dataitem


class RuntimeDbt(Runtime):
    """
    Runtime Dbt class.
    """

    def __init__(self, kind_registry: KindRegistry, project: str) -> None:
        super().__init__(kind_registry, project)

        ctx = get_context(self.project)
        self.root = ctx.runtime_dir
        self.tmp_dir = ctx.tmp_dir
        self.model_dir = self.root / "models"

        self.root.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # UUID for output dataitem and dbt execution
        self.uuid = build_uuid()

        # Registries
        self._input_dataitems: list[dict[str, str]] = []
        self._versioned_tables: list[str] = []

    def build(self, function: dict, task: dict, run: dict) -> dict:
        """
        Build run spec.

        Parameters
        ----------
        function : dict
            The function.
        task : dict
            The task.
        run : dict
            The run.

        Returns
        -------
        dict
            The run spec.
        """
        return {
            **function.get("spec", {}),
            **task.get("spec", {}),
            **run.get("spec", {}),
        }

    def run(self, run: dict) -> dict:
        """
        Run function.

        Parameters
        ----------
        run : dict
            The run.

        Returns
        -------
        dict
            Status of the executed run.
        """
        LOGGER.info("Validating task.")
        action = self._validate_task(run)
        executable = self._get_executable(action)

        LOGGER.info("Starting task.")
        spec = run.get("spec")
        project = run.get("project")

        LOGGER.info("Collecting inputs.")
        self._collect_inputs(spec)

        LOGGER.info("Configure execution.")
        output_table = self._configure_execution(spec, project)

        LOGGER.info("Executing run.")
        results = self._execute(executable, output_table, self.root)

        LOGGER.info("Collecting outputs.")
        output = self._collect_outputs(results, output_table, project)
        status = build_status(output, results, output_table)

        LOGGER.info("Clean up environment.")
        self._cleanup()

        # Return run status
        LOGGER.info("Task completed, returning run status.")
        return status

    @staticmethod
    def _get_executable(action: str) -> Callable:
        """
        Select function according to action.

        Parameters
        ----------
        action : str
            Action to execute.

        Returns
        -------
        Callable
            Function to execute.
        """
        if action == "transform":
            return transform
        raise NotImplementedError

    ####################
    # Inputs
    ####################

    def _collect_inputs(self, spec: dict) -> None:
        """
        Parse inputs from run spec and materialize dataitems in postgres.

        Parameters
        ----------
        spec : dict
            Run spec dict.

        Returns
        -------
        None
        """
        # Collect input dataitems
        for param, di in spec.get("inputs", {}).items():
            di = dataitem_from_dict(di)

            # Register dataitem in a dict to be used for inputs confs generation
            self._input_dataitems.append({"name": param, "id": di.id})

            # Materialize dataitem in postgres
            table = materialize_dataitem(di, param)

            # Save versioned table name to be used for cleanup
            self._versioned_tables.append(table)

    ####################
    # Configuration
    ####################

    def _configure_execution(self, spec: dict, project: str) -> str:
        """
        Initialize a dbt project with a model and a schema definition.

        Parameters
        ----------
        spec : str
            Run spec dict.
        project : str
            The project name.

        Returns
        -------
        str
            Output table name.
        """
        output_table = get_output_table_name(spec.get("outputs", []))
        query = save_function_source(self.tmp_dir, spec.get("source", {}))

        # Generate profile yaml file
        generate_dbt_profile_yml(self.root)

        # Generate project yaml file
        generate_dbt_project_yml(self.root, self.model_dir, project.replace("-", "_"))

        # Generate outputs confs
        generate_outputs_conf(self.model_dir, query, output_table, self.uuid)

        # Generate inputs confs for every dataitem
        for di in self._input_dataitems:
            generate_inputs_conf(self.model_dir, di["name"], di["id"])

        return output_table

    ####################
    # Outputs
    ####################

    def _collect_outputs(self, results: RunResult, output_table: str, project: str) -> Dataitem:
        """
        Collect outputs.

        Parameters
        ----------
        results : dict
            The dbt run results.
        output_table : str
            Output table name.
        project : str
            The project name.

        Returns
        -------
        Dataitem
            The output dataitem table.
        """
        parsed_result = parse_results(results, output_table, project)
        return create_dataitem_(parsed_result, project, self.uuid)

    ####################
    # Cleanup
    ####################

    def _cleanup(self) -> None:
        """
        Cleanup environment.

        Returns
        -------
        None
        """
        cleanup(self._versioned_tables, self.tmp_dir)
