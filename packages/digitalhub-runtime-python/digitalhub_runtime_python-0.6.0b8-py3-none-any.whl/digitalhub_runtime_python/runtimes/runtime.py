from __future__ import annotations

import typing
from typing import Callable

from digitalhub_core.context.builder import get_context
from digitalhub_core.runtimes.base import Runtime
from digitalhub_core.utils.logger import LOGGER
from digitalhub_runtime_python.utils.configuration import get_function_from_source
from digitalhub_runtime_python.utils.inputs import compose_inputs
from digitalhub_runtime_python.utils.outputs import build_status, parse_outputs

if typing.TYPE_CHECKING:
    from digitalhub_core.runtimes.kind_registry import KindRegistry


class RuntimePython(Runtime):
    """
    Runtime Python class.
    """

    def __init__(self, kind_registry: KindRegistry, project: str) -> None:
        super().__init__(kind_registry, project)
        ctx = get_context(self.project)
        self.root = ctx.runtime_dir
        self.tmp_dir = ctx.tmp_dir

        self.root.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

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
        self._validate_task(run)

        LOGGER.info("Validating run.")
        self._validate_run(run)

        LOGGER.info("Starting task.")
        spec = run.get("spec")
        project = run.get("project")

        LOGGER.info("Configuring execution.")
        fnc, wrapped = self._configure_execution(spec)

        LOGGER.info("Composing function arguments.")
        fnc_args = self._compose_args(fnc, spec, project)

        LOGGER.info("Executing run.")
        if wrapped:
            results: dict = self._execute(fnc, project, **fnc_args)
        else:
            exec_result = self._execute(fnc, **fnc_args)
            LOGGER.info("Collecting outputs.")
            results = parse_outputs(exec_result, list(spec.get("outputs", {})), project)

        status = build_status(results, spec.get("outputs"))

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
        raise NotImplementedError

    @staticmethod
    def _validate_run(run: dict) -> None:
        """
        Check if run is locally allowed.

        Parameters
        ----------
        run : dict
            Run object dictionary.

        Returns
        -------
        None
        """
        task_kind = run["spec"]["task"].split(":")[0]
        local_execution = run["spec"]["local_execution"]
        if task_kind != "python+job" and local_execution:
            msg = f"Local execution not allowed for task kind {task_kind}."
            LOGGER.exception(msg)
            raise RuntimeError(msg)

    ####################
    # Configuration
    ####################

    def _configure_execution(self, spec: dict) -> tuple[Callable, bool]:
        """
        Configure execution.

        Parameters
        ----------
        spec : dict
            Run spec.

        Returns
        -------
        Callable
            Function to execute.
        """
        fnc = get_function_from_source(
            self.root,
            spec.get("source", {}),
        )
        return fnc, hasattr(fnc, "__wrapped__")

    def _compose_args(self, func: Callable, spec: dict, project: str) -> dict:
        """
        Collect inputs.

        Parameters
        ----------
        func : Callable
            Function to execute.
        spec : dict
            Run specs.
        project : str
            Project name.

        Returns
        -------
        dict
            Parameters.
        """
        inputs = spec.get("inputs", {})
        parameters = spec.get("parameters", {})
        local_execution = spec.get("local_execution")
        return compose_inputs(inputs, parameters, local_execution, func, project)
