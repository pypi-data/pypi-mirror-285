# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import contextlib
import copy
import dataclasses as dc
import os
import typing as tp

from ..._logging import logger
from ..._proto_namespace import _ProtoNamespace

__all__ = ["Payload"]


@dc.dataclass
class Payload:
    flavor: tp.ClassVar[str]
    name: str
    auxh: _ProtoNamespace
    environment: tp.Dict[str, str]

    def run(self, force: bool) -> None:  # pylint: disable=unused-argument
        raise NotImplementedError()

    def is_up_to_date(self) -> bool:
        return False

    def hydrate(self, deps: tp.Tuple["Payload", ...] = tuple()) -> None:
        pass

    @contextlib.contextmanager
    def write_environment_variables(
        self, param: _ProtoNamespace
    ) -> tp.Iterator[tp.Dict[str, str]]:
        param = copy.copy(param)
        old_env = {}
        for key, val in param.pop("environment", {}).items():
            old_env[key] = os.environ.get(key, None)
            os.environ[key] = self.auxh.env_var.apply_format(val)
            from_tpl = ""
            if os.environ[key] != val:
                from_tpl = f" <- {val}"
            logger.info(
                "payload %s env: %s = %s%s", self.name, key, os.environ[key], from_tpl
            )
        yield param
        for key, val in old_env.items():
            if val is None:
                del os.environ[key]
                logger.info("payload %s env: %s [removed]", self.name, key)
            else:
                os.environ[key] = val
                logger.info("payload %s env: %s = %s [restored]", self.name, key, val)
