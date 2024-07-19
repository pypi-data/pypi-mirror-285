from __future__ import annotations

import inspect
import typing
from typing import Any, Callable

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities.artifacts.crud import artifact_from_dict
from digitalhub_core.entities.utils import parse_entity_key
from digitalhub_core.utils.logger import LOGGER
from digitalhub_data.entities.dataitems.crud import dataitem_from_dict
from digitalhub_ml.entities.entity_types import EntityTypes
from digitalhub_ml.entities.models.crud import model_from_dict
from digitalhub_ml.entities.projects.crud import get_project

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.entity import Entity
    from digitalhub_core.entities.projects.entity import Project


def get_project_(project_name: str) -> Project:
    """
    Get project.

    Parameters
    ----------
    project_name : str
        Project name.

    Returns
    -------
    Project
        Project.
    """
    try:
        ctx = get_context(project_name)
        return get_project(project_name, local=ctx.local)
    except Exception as e:
        msg = f"Error during project collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg)


def get_entity_inputs(inputs: dict) -> dict[str, Entity]:
    """
    Set inputs.

    Parameters
    ----------
    inputs : dict
        Run inputs.
    parameters : dict
        Run parameters.
    tmp_dir : Path
        Temporary directory for storing dataitms and artifacts.

    Returns
    -------
    dict
        Mlrun inputs.
    """
    try:
        inputs_objects = {}
        for k, v in inputs.items():
            _, entity_type, _, _, _ = parse_entity_key(v.get("key"))
            if entity_type == EntityTypes.DATAITEMS.value:
                inputs_objects[k] = dataitem_from_dict(v)
            elif entity_type == EntityTypes.ARTIFACTS.value:
                inputs_objects[k] = artifact_from_dict(v)
            elif entity_type == EntityTypes.MODELS.value:
                inputs_objects[k] = model_from_dict(v)
        return inputs_objects
    except Exception as e:
        msg = f"Error during inputs collection. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def compose_inputs(
    inputs: dict,
    parameters: dict,
    local_execution: bool,
    func: Callable,
    project: str | Project,
    context: Any | None = None,
    event: Any | None = None,
) -> dict:
    """
    Compose inputs.

    Parameters
    ----------
    inputs : dict
        Run inputs.
    parameters : dict
        Run parameters.
    local_execution : bool
        Local execution.
    func : Callable
        Function to execute.
    project : str
        Project name.
    context : nuclio_sdk.Context
        Nuclio context.
    event : nuclio_sdk.Event
        Nuclio event.

    Returns
    -------
    dict
        Function inputs.
    """
    try:
        entity_inputs = get_entity_inputs(inputs)
        fnc_args = {**parameters, **entity_inputs}

        fnc_parameters = inspect.signature(func).parameters

        _has_project = "project" in fnc_parameters
        _has_context = "context" in fnc_parameters
        _has_event = "event" in fnc_parameters

        # Project is reserved keyword argument
        # both in local and remote executions
        if _has_project:
            if _has_context and not local_execution:
                fnc_args["project"] = context.project
            elif isinstance(project, str):
                fnc_args["project"] = get_project_(project)
            else:
                fnc_args["project"] = project

        # Context and event are reserved keyword arguments
        # only in remote executions
        if not local_execution:
            if _has_context:
                fnc_args["context"] = context
            if _has_event:
                fnc_args["event"] = event

        return fnc_args

    except Exception as e:
        msg = f"Error during function arguments compostion. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e
