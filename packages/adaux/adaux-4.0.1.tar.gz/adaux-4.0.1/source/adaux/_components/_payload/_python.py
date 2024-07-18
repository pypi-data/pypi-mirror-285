# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import inspect
import types
import typing as tp

from ..._proto_namespace import _ProtoNamespace
from ._base import Payload

__all__ = ["PythonPayload"]


@dc.dataclass
class PythonPayload(Payload):
    flavor: tp.ClassVar[str] = "python"
    fct: tp.Callable[
        [
            tp.Dict[str, tp.Any],
        ],
        bool,
    ]
    param: _ProtoNamespace = dc.field(default_factory=_ProtoNamespace)

    def run(self, force: bool = False) -> None:
        with self.write_environment_variables(self.param) as param:
            sig_params = inspect.signature(self.fct).parameters
            for key in ["aux", "auxh"]:
                if key in sig_params:
                    param[key] = self.auxh  # type: ignore
            if "deps" in sig_params:
                param["deps"] = self._deps  # type: ignore

            self.fct(**param)  # type: ignore

    @classmethod
    def import_function(
        cls, name: str, custom_ppyload: tp.Optional[types.ModuleType]
    ) -> tp.Callable[
        [
            tp.Dict[str, tp.Any],
        ],
        bool,
    ]:
        # pylint: disable=import-outside-toplevel
        from ...src.payload.python import functions as fallback

        fname = name.replace("-", "_")
        try:
            return getattr(custom_ppyload, fname)  # type: ignore
        except AttributeError:
            return getattr(fallback, fname)  # type: ignore

    def hydrate(self, deps: tp.Tuple["Payload", ...] = tuple()) -> None:
        if hasattr(self, "is_hydrated"):
            return
        # pylint: disable=attribute-defined-outside-init
        self.is_hydrated = True
        if deps:
            self._deps = deps
