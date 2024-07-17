# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from ._docker import DockerPayload
from ._docker_executors import DockerRun

__all__ = ["DockerRunPayload"]


@dc.dataclass
class DockerRunPayload(DockerPayload):
    flavor: tp.ClassVar[str] = "docker_run"

    def create_executor(self, parents: tp.Any) -> tp.Any:
        return DockerRun(
            slug=self.auxh.project.slug,
            services=self.param.services,
            parents=parents,
            images=self.param.get("images", []),
            interactive=self.param.get("interactive", False),
            exec_join=self.param.get("exec_join", False),
            run_ports=self.param.get("run_ports", []),
        )
