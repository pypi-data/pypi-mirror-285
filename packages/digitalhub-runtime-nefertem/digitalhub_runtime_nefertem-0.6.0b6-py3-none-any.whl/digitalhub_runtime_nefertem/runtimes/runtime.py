from __future__ import annotations

import shutil
import typing
from pathlib import Path
from typing import Callable

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.runtimes.base import Runtime
from digitalhub_core.utils.logger import LOGGER
from digitalhub_data.entities.dataitems.crud import dataitem_from_dict
from digitalhub_runtime_nefertem.utils.configurations import create_client, create_nt_resources, create_nt_run_config
from digitalhub_runtime_nefertem.utils.functions import infer, metric, profile, validate
from digitalhub_runtime_nefertem.utils.inputs import persist_dataitem
from digitalhub_runtime_nefertem.utils.outputs import build_status, create_artifact_, upload_artifact

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.artifacts.entity import Artifact
    from digitalhub_core.runtimes.kind_registry import KindRegistry


class RuntimeNefertem(Runtime):
    """
    Runtime nefertem class.
    """

    def __init__(self, kind_registry: KindRegistry, project: str) -> None:
        super().__init__(kind_registry, project)
        ctx = get_context(self.project)
        ctx.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = str(ctx.tmp_dir)
        self.store = {"name": "local", "store_type": "local"}
        self.nt_id = build_uuid()

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
        inputs = self._collect_inputs(spec)

        LOGGER.info("Configure execution.")
        config = self._configure_execution(inputs, spec, action)

        LOGGER.info("Executing run.")
        results: dict = self._execute(executable, **config)

        LOGGER.info("Collecting outputs.")
        outputs = self._collect_outputs(results, project)
        status = build_status(results, outputs)

        LOGGER.info("Clean up environment.")
        self._cleanup()

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
        if action == "validate":
            return validate
        if action == "profile":
            return profile
        if action == "infer":
            return infer
        if action == "metric":
            return metric
        raise NotImplementedError

    ####################
    # Inputs
    ####################

    def _collect_inputs(self, spec: dict) -> list[dict]:
        """
        Collect dataitems inputs.

        Parameters
        ----------
        spec : dict
            Run spec.
        project : str
            The project name.

        Returns
        -------
        list[dict]
            The list of inputs dataitems.
        """
        Path(f"{self.output_path}/tmp").mkdir(parents=True, exist_ok=True)
        mapper = []
        for _, di in spec.get("inputs", {}).items():
            di = dataitem_from_dict(di)
            mapper.append(persist_dataitem(di, di.name, self.output_path))
        return mapper

    ####################
    # Configuration
    ####################

    def _configure_execution(self, inputs: list[dict], spec: dict, action: str) -> tuple[Callable, dict]:
        """
        Generate nefertem configuration.

        Parameters
        ----------
        inputs : list
            The list of inputs dataitems.
        spec : dict
            Run spec.
        action : str
            Action to execute.

        Returns
        -------
        tuple
            Function to execute and its parameters.
        """
        # Create resources
        resources = create_nt_resources(inputs, self.store)

        # Create run configuration
        framework = spec.get("framework")
        exec_args = spec.get("exec_args", {})
        parallel = spec.get("parallel", False)
        num_worker = spec.get("num_worker", 1)
        run_config = create_nt_run_config(action, framework, exec_args, parallel, num_worker)

        # Create Nefertem client
        client = create_client(self.output_path, self.store)

        # Return parameters
        return {
            "client": client,
            "resources": resources,
            "run_config": run_config,
            "run_id": self.nt_id,
            "metrics": spec.get("metrics"),
            "constraints": spec.get("constraints"),
            "error_report": spec.get("error_report"),
        }

    ####################
    # Outputs
    ####################

    def _collect_outputs(self, results: dict, project: str) -> list[Artifact]:
        """
        Collect outputs.

        Parameters
        ----------
        results : dict
            The nefertem run results.
        project : str
            The project name.

        Returns
        -------
        list
            List of artifacts paths.
        """
        output_files = results.get("output_files", [])

        LOGGER.info("Creating artifacts.")
        artifacts = [create_artifact_(i, project, self.nt_id) for i in output_files]

        LOGGER.info("Uploading artifacts to minio.")
        for i in artifacts:
            upload_artifact(i)
            i.spec.src_path = None

        return artifacts

    ####################
    # Cleanup
    ####################

    def _cleanup(self) -> None:
        """
        Cleanup after run.

        Returns
        -------
        None
        """
        shutil.rmtree(f"{self.output_path}/tmp", ignore_errors=True)
