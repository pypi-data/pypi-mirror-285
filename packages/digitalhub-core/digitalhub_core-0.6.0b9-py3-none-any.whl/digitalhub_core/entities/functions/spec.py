from __future__ import annotations

from digitalhub_core.entities._base.spec import Spec, SpecParams


class FunctionSpec(Spec):
    """
    Specification for a Function.
    """


class FunctionParams(SpecParams):
    """
    Function parameters model.
    """


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
