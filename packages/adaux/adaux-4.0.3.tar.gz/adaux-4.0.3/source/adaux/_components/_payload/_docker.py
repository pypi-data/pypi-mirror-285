# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from ..._logging import logger
from ..._proto_namespace import _ProtoNamespace
from ._base import Payload

__all__ = ["DockerPayload"]


@dc.dataclass
class DockerPayload(Payload):
    param: _ProtoNamespace = dc.field(default_factory=_ProtoNamespace)

    def _get_executor(self, dep: Payload) -> tp.Any:
        if dep.flavor in ["docker_build", "with_dependency"]:
            return dep.executor  # type: ignore
        logger.info(
            "%s only extracts parents from type DockerBuildPayload and WithDependencyPayload[DockerBuildPayload]! No parent for %s",
            self.__class__.__name__,
            dep.flavor,
        )
        return None

    def create_executor(self, parents: tp.Any) -> tp.Any:
        raise NotImplementedError()

    def hydrate(self, deps: tp.Tuple[Payload, ...] = tuple()) -> None:
        if hasattr(self, "is_hydrated"):
            return
        # pylint: disable=attribute-defined-outside-init
        self.is_hydrated = True
        parents = [self._get_executor(dep) for dep in deps]
        parents = [par for par in parents if par is not None]
        if hasattr(self, "_executor"):
            assert self.executor.parents == parents
            return
        self._executor = self.create_executor(parents)

    @property
    def executor(self) -> tp.Any:
        return self._executor

    def run(self, force: bool = False) -> None:
        with self.write_environment_variables(self.param):
            if self.is_up_to_date():
                if force:
                    self.executor.script(force=force)
            self.executor.script()
