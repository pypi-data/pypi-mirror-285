# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from ._docker import DockerPayload

__all__ = ["DockerBuildPayload"]


from ._docker_executors import DockerBuild, DockerBuildx


@dc.dataclass
class DockerBuildPayload(DockerPayload):
    flavor: tp.ClassVar[str] = "docker_build"

    def create_executor(self, parents: tp.Any) -> tp.Any:
        images = []
        base = self.param.get("base")
        if base:
            images.append(base)

        kwgs = dict(
            images=images,
            slug=self.auxh.project.slug,
            service=self.param.service_name,
            image_name=self.param.image_name,
            branch_match=self.param.get("branch_match", []),
            base_match=self.param.get("base_match", []),
            parents=parents,
            always_build=self.param.get("always_build", False),
            files=[f"devops/docker/{self.param.service_name}.dockerfile"],
        )

        if "platforms" in self.param:
            return DockerBuildx(**kwgs)

        return DockerBuild(**kwgs)

    def is_up_to_date(self) -> bool:
        if self.param.get("always_build", False):
            return False
        return self.executor.is_up_to_date()  # type: ignore
