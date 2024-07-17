from __future__ import annotations

import shutil
import typing
from typing import Callable

from digitalhub_core.context.builder import get_context
from digitalhub_core.runtimes.base import Runtime
from digitalhub_core.utils.logger import LOGGER
from digitalhub_runtime_mlrun.utils.configurations import (
    get_dhcore_function,
    get_exec_config,
    get_mlrun_function,
    get_mlrun_project,
    parse_function_specs,
    save_function_source,
)
from digitalhub_runtime_mlrun.utils.functions import run_build, run_job
from digitalhub_runtime_mlrun.utils.inputs import get_inputs_parameters
from digitalhub_runtime_mlrun.utils.outputs import build_status, build_status_build, parse_mlrun_artifacts
from mlrun.projects.operations import BuildStatus
from mlrun.runtimes.base import RunObject

if typing.TYPE_CHECKING:
    from digitalhub_core.runtimes.kind_registry import KindRegistry
    from mlrun.runtimes import BaseRuntime


class RuntimeMlrun(Runtime):
    """
    Runtime Mlrun class.
    """

    def __init__(self, kind_registry: KindRegistry, project: str) -> None:
        super().__init__(kind_registry, project)
        ctx = get_context(self.project)
        self.root = ctx.runtime_dir
        self.tmp_dir = ctx.tmp_dir
        self.root.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.function_source = None

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
        function_args = self._collect_inputs(spec)

        LOGGER.info("Configure execution.")
        mlrun_function, exec_config = self._configure_execution(spec, project)

        LOGGER.info("Executing function.")
        results = self._execute(executable, mlrun_function, exec_config, function_args)

        LOGGER.info("Collecting outputs.")
        status = self._collect_outputs(results, spec, project)

        LOGGER.info("Cleanup")
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
        if action == "job":
            return run_job
        if action == "build":
            return run_build
        raise NotImplementedError

    ####################
    # Helpers
    ####################

    def _collect_inputs(self, spec: dict) -> dict:
        """
        Collect inputs.

        Parameters
        ----------
        spec : dict
            Run specs.
        project : str
            Project name.

        Returns
        -------
        dict
            Parameters.
        """
        LOGGER.info("Getting inputs.")
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        return get_inputs_parameters(spec.get("inputs", {}), spec.get("parameters", {}), self.tmp_dir)

    ####################
    # Configuration
    ####################

    def _configure_execution(self, spec: dict, project: str) -> tuple[BaseRuntime, dict]:
        """
        Create Mlrun project and function and prepare parameters.

        Parameters
        ----------
        spec : dict
            Run specs.
        project : str
            Project name.

        Returns
        -------
        tuple
            Mlrun function and parameters.
        """

        # Setup function source and specs
        LOGGER.info("Getting function source and specs.")
        dhcore_function = get_dhcore_function(spec.get("function"))
        function_source = save_function_source(self.tmp_dir, dhcore_function.spec.to_dict().get("source"))
        function_specs = parse_function_specs(dhcore_function.spec.to_dict())

        # Create Mlrun project
        LOGGER.info("Creating Mlrun project and function.")
        mlrun_project = get_mlrun_project(project)
        mlrun_function = get_mlrun_function(mlrun_project, dhcore_function.name, function_source, function_specs)
        exec_config = get_exec_config(spec)

        return mlrun_function, exec_config

    ####################
    # Outputs
    ####################

    def _collect_outputs(self, results: RunObject | BuildStatus, spec: dict, project: str) -> dict:
        """
        Collect outputs.

        Parameters
        ----------
        results : RunObject | BuildStatus
            Execution results.
        spec : dict
            Run specs.
        project : str
            Project name.

        Returns
        -------
        dict
            Status of the executed run.
        """
        if isinstance(results, RunObject):
            execution_outputs = parse_mlrun_artifacts(results, project)
            return build_status(results, execution_outputs, spec.get("outputs"), spec.get("values", []))
        if isinstance(results, BuildStatus):
            return build_status_build(results)

    ####################
    # Cleanup
    ####################

    def _cleanup(self) -> None:
        """
        Cleanup root folder.

        Returns
        -------
        None
        """
        shutil.rmtree(self.root, ignore_errors=True)
