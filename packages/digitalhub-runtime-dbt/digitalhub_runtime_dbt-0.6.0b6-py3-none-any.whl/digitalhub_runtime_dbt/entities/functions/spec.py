from __future__ import annotations

from pathlib import Path

from digitalhub_core.entities.functions.spec import FunctionParams, FunctionSpec, SourceCodeStruct
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.generic_utils import decode_string, encode_string
from digitalhub_core.utils.uri_utils import map_uri_scheme


class FunctionSpecDbt(FunctionSpec):
    """
    Specification for a Function Dbt.
    """

    def __init__(self, source: dict) -> None:
        """
        Constructor.

        Parameters
        ----------
        sql : str
            SQL query to run inside Dbt.
        """
        super().__init__()

        source = self._check_source(source)
        self.source = SourceCodeStruct(**source)

    @staticmethod
    def _check_source(source: dict) -> dict:
        """
        Check source code.

        Parameters
        ----------
        source : dict
            Source.

        Returns
        -------
        dict
            Checked source.
        """
        source_path = source.get("source")
        code = source.get("code")
        base64 = source.get("base64")
        handler = source.get("handler")

        if source.get("lang") is None:
            source["lang"] = "sql"

        if source_path is None and code is None and base64 is None:
            raise EntityError("Source must be provided.")

        # Check source code

        if base64 is not None:
            return source

        if code is not None:
            source["base64"] = encode_string(code)
            return source

        if source_path is not None:
            if map_uri_scheme(source_path) == "local":
                source["code"] = Path(source_path).read_text()
                source["base64"] = encode_string(source["code"])
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


class FunctionParamsDbt(FunctionParams):
    """
    Function Dbt parameters model.
    """

    source: dict
    """Source code."""
