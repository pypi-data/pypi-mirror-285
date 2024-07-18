# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import copy
import typing as tp
from pathlib import Path

from .._parser import ConfigParser
from .._proto_namespace import _ProtoNamespace
from ._06_dependency import DependencyMixin


class PytestMixin(DependencyMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("asyncio_mode", "markers", "addopts", "cache_dir")

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.pytest = _ProtoNamespace()
        self.auxcon.dependencies.test.append(self.versions.pytest)
        data.markers = _ProtoNamespace({"merge_only": "run test only on merge request"})
        data.addopts = '--strict-markers -m "not merge_only"'

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)
        self.auxf.setdefault("pytest", _ProtoNamespace())
        data = self.auxf.pytest
        if "markers" not in data:
            data.setdefault("markers", tpl.pytest.markers)
            self._print(f"added pytest.markers: {data.markers}", fg="green")
        if "addopts" not in data:
            data.setdefault("addopts", tpl.pytest.addopts)
            self._print(f"added pytest.markers: {data.addopts}", fg="green")

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.pytest
        data.asyncio_mode = "strict"

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "pytest")
        self._to_proto_ns("pytest", "markers")

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("pytest", _ProtoNamespace())
        self.auxd.pytest.setdefault("cache_dir", str(self.target / "cache" / "pytest"))
        self.auxd.pytest.setdefault("markers", _ProtoNamespace())

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.pytest
        if data.markers:
            data.markers = [f"{key}: {val}" for key, val in data.markers.items()]
        else:
            del data.markers

    def bake(self) -> None:
        super().bake()
        data = self.auxe.pytest
        project = self.auxe.project
        self.auxe.python_project.config["tool:pytest"] = data

        if project.source_dir == ".":
            # no need for pytest.ini, as setup.cfg handles it
            return

        # we need the ini, as pytest only mounts the source_dir
        # for tests, and then we dont have the setup information
        src_data = copy.deepcopy(data)
        for _ in project.source_dir.split("/"):
            src_data.cache_dir = Path("..") / src_data.cache_dir
        src_data.cache_dir = str(src_data.cache_dir)
        config = _ProtoNamespace(pytest=src_data)

        dest = self.target.parent / project.source_dir / "pytest.ini"
        written = ConfigParser.write(config, dest)
        if written:
            self._print(f"baked {dest}", fg="green")
