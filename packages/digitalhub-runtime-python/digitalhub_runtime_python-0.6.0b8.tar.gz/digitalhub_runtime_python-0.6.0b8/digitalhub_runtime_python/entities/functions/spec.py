from __future__ import annotations

from pathlib import Path
from typing import Literal

from digitalhub_core.entities.functions.spec import FunctionParams, FunctionSpec
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.generic_utils import decode_string, encode_source, encode_string
from digitalhub_core.utils.uri_utils import map_uri_scheme


class FunctionSpecPython(FunctionSpec):
    """
    Specification for a Function job.
    """

    def __init__(
        self,
        source: str | dict | None = None,
        code_src: str | None = None,
        handler: str | None = None,
        code: str | None = None,
        base64: str | None = None,
        init_function: str | None = None,
        lang: str | None = None,
        image: str | None = None,
        base_image: str | None = None,
        python_version: str | None = None,
        requirements: list | None = None,
    ) -> None:
        super().__init__()

        self.image = image
        self.base_image = base_image
        self.python_version = python_version
        self.requirements = requirements

        # Give source precedence
        if source is not None:
            source_dict = source
        else:
            source_dict = {
                "source": code_src,
                "handler": handler,
                "code": code,
                "base64": base64,
                "init_function": init_function,
                "lang": lang,
            }

        source_checked = self._source_check(source_dict)
        self.source = SourceCodeStruct(**source_checked)

    @staticmethod
    def _source_check(source: dict) -> dict:
        """
        Check source.

        Parameters
        ----------
        source : dict
            Source.

        Returns
        -------
        dict
            Checked source.
        """
        # Source check
        source_path = source.get("source")
        code = source.get("code")
        base64 = source.get("base64")
        handler = source.get("handler")
        source["lang"] = "python"

        if handler is None:
            raise EntityError("Handler must be provided.")

        if source_path is None and code is None and base64 is None:
            raise EntityError("Source must be provided.")

        if base64 is not None:
            return source

        if code is not None:
            source["base64"] = encode_string(code)
            return source

        if source_path is not None:
            if map_uri_scheme(source_path) == "local":
                if not (Path(source_path).suffix == ".py" and Path(source_path).is_file()):
                    raise EntityError("Source is not a valid python file.")
                source["base64"] = encode_source(source_path)
            else:
                if handler is None:
                    raise EntityError("Handler must be provided if source is not local.")

        return source

    def show_source_code(self) -> str:
        """
        Show source code.

        Returns
        -------
        str
            Source code.
        """
        if self.source.code is not None:
            return str(self.source.code)
        if self.source.base64 is not None:
            try:
                return decode_string(self.source.base64)
            except Exception:
                raise EntityError("Something got wrong during source code decoding.")
        if (self.source.source is not None) and (map_uri_scheme(self.source.source) == "local"):
            try:
                return Path(self.source.source).read_text()
            except Exception:
                raise EntityError("Cannot access source code.")
        return ""

    def to_dict(self) -> dict:
        """
        Override to_dict to exclude code from source.

        Returns
        -------
        dict
            Dictionary representation of the object.
        """
        dict_ = super().to_dict()
        dict_["source"] = self.source.to_dict()
        return dict_


class FunctionParamsPython(FunctionParams):
    """
    Function python parameters model.
    """

    source: dict = None
    "Source code details as dictionary"

    code_src: str = None
    "Pointer to source code"

    handler: str = None
    "Function entrypoint"

    code: str = None
    "Source code (plain text)"

    base64: str = None
    "Source code (base64 encoded)"

    init_function: str = None
    "Init function for remote nuclio execution"

    lang: str = None
    "Source code language (hint)"

    python_version: Literal["PYTHON3_9", "PYTHON3_10", "PYTHON3_11"]
    "Python version"

    image: str = None
    "Image where the function will be executed"

    base_image: str = None
    "Base image used to build the image where the function will be executed"

    requirements: list = None
    "Requirements list to be installed in the image where the function will be executed"


class SourceCodeStruct:
    """
    Source code struct.
    """

    def __init__(
        self,
        source: str | None = None,
        handler: str | None = None,
        code: str | None = None,
        base64: str | None = None,
        init_function: str | None = None,
        lang: str | None = None,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        source : str
            Source reference.
        handler : str
            Function entrypoint.
        code : str
            Source code (plain).
        base64 : str
            Source code (base64 encoded).
        init_function : str
            Init function for remote execution.
        lang : str
            Source code language (hint).
        """
        self.source = source
        self.handler = handler
        self.code = code
        self.base64 = base64
        self.init_function = init_function
        self.lang = lang

    def to_dict(self) -> dict:
        """
        Convert to dictionary.

        Returns
        -------
        dict
            Dictionary representation of the object.
        """
        dict_ = {}
        if self.source is not None:
            dict_["source"] = self.source
        if self.handler is not None:
            dict_["handler"] = self.handler
        if self.base64 is not None:
            dict_["base64"] = self.base64
        if self.init_function is not None:
            dict_["init_function"] = self.init_function
        if self.lang is not None:
            dict_["lang"] = self.lang

        return dict_

    def __repr__(self) -> str:
        return str(self.to_dict())
