# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._proto_namespace import _ProtoNamespace
from ._05_python_project import PythonProjectMixin
from ._06_dependency import DependencyMixin


class ExecutablesMixin(DependencyMixin, PythonProjectMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("console_scripts", "scripts")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "executables")
        for key in self.__keys():
            self._to_list("executables", key)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("executables", _ProtoNamespace())
        for key in self.__keys():
            self.auxd.executables.setdefault(key, [])

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.setdefault("executables", _ProtoNamespace())
        data = self.auxcon.executables
        data.scripts = ["scripts/say_hello"]
        data.console_scripts = ["adaux:adaux"]

    def bake(self) -> None:
        super().bake()
        config = self.auxe.python_project.config
        data = self.auxe.executables

        config.options.scripts = data.scripts
        cscr = data.console_scripts
        for i, val in enumerate(cscr):
            if "=" in val:
                continue
            name = val.rsplit(":", 1)[1]
            cscr[i] = f"{name} = {val}"

        config["options.entry_points"].console_scripts = cscr
