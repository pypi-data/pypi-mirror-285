# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import typing as tp

from ._base import Payload


__all__ = ["DockerComposePayload"]


@dc.dataclass
class DockerComposePayload(Payload):
    flavor: tp.ClassVar[str] = "docker_compose"
    payloads: tp.List[Payload]

    def run(self, force: bool = False) -> None:
        raise NotImplementedError()
