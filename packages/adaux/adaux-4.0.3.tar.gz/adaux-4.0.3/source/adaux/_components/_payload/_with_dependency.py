# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from ..._proto_namespace import _ProtoNamespace
from ._base import Payload
from ._docker import DockerPayload

__all__ = ["WithDependencyPayload"]


@dc.dataclass
class WithDependencyPayload(Payload):
    flavor: tp.ClassVar[str] = "with_dependency"
    payload: Payload
    deps: tp.Tuple[Payload, ...]

    def run(self, force: bool = False) -> None:
        if force or not self.is_up_to_date():
            for dep in self.deps:
                dep.run(force)
        self.payload.run(force)

    def is_up_to_date(self) -> bool:
        return self.payload.is_up_to_date()

    def hydrate(self, deps: tp.Tuple[Payload, ...] = tuple()) -> None:
        if hasattr(self, "is_hydrated"):
            return
        # pylint: disable=attribute-defined-outside-init
        self.is_hydrated = True
        assert not deps
        for dep in self.deps:
            dep.hydrate()
        self.payload.hydrate(self.deps)

    @property
    def executor(self) -> tp.Any:
        if isinstance(self.payload, DockerPayload):
            return self.payload.executor
        return None

    @property
    def param(self) -> _ProtoNamespace:
        # pylint: disable=no-member
        return self.payload.param  # type: ignore
