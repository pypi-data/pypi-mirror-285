from __future__ import annotations

from pathlib import Path
from typing import Callable, Union

from digitalhub_core.utils.uri_utils import map_uri_scheme
from digitalhub_runtime_python.utils.configuration import import_function


def parse_handler(handler: str) -> tuple[Path, str]:
    """
    Parse handler.

    Parameters
    ----------
    handler : str
        Function handler

    Returns
    -------
    tuple[Path, str]
        Function handler.
    """
    parsed = handler.split(":")
    if len(parsed) == 1:
        return None, parsed[0]
    return Path(*parsed[0].split(".")), parsed[1]


def get_function_source(source_spec: dict) -> Path:
    """
    Get function source.

    Parameters
    ----------
    source : dict
        Function source.

    Returns
    -------
    Path
        Path to function source.
    """
    path = Path("/shared")

    # Get relevant information
    base64 = source_spec.get("base64")
    source = source_spec.get("source", "main.py")
    handler = source_spec.get("handler")

    handler_path, _ = parse_handler(handler)

    # Get scheme in source
    scheme = map_uri_scheme(source)

    # Check base64. If it is set, it means
    # that the source comes from a local file
    if base64 is not None:
        if scheme == "local":
            if handler_path is not None:
                return path / handler_path / Path(source)
            return path / Path(source)
        raise RuntimeError("Source is not a local file.")

    if handler_path is not None:
        return path / handler_path.with_suffix(".py")
    raise RuntimeError("Must provide handler path in handler in form <root>.<dir>.<module>:<function_name>.")


def import_function_and_init(source: dict) -> tuple[Callable, Union[Callable, None]]:
    """
    Import function from source.

    Parameters
    ----------
    source : dict
        Function source.

    Returns
    -------
    tuple
        Function and init function.
    """

    # Get function source
    function_path = get_function_source(source)
    _, handler_name = parse_handler(source.get("handler"))

    # Import function
    fnc = import_function(function_path, handler_name)

    # Get init function
    init_handler = source.get("init_function")
    init_fnc = None
    if init_handler is not None:
        init_fnc = import_function(function_path, init_handler)

    return fnc, init_fnc
