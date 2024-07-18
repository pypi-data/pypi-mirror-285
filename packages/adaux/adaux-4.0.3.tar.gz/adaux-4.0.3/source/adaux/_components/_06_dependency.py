# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import re
import typing as tp

from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._05_python_project import PythonProjectMixin


class DependencyMixin(PythonProjectMixin, MetaMixin):
    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.dependencies = _ProtoNamespace()
        data.default = []
        data.test = []
        data.dev = []
        data.dev_apt = []

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.dependencies
        data.default_apt = ["postgres", {"linux/arm64": "build-essential"}]
        data.default_apt = ["postgres"]
        data.default = ["numpy"]
        data.dev.pop(-1)

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)
        data = self.auxf.dependencies

        for mod in full.dependencies:
            if mod in tpl.dependencies and mod not in data:
                data[mod] = tpl.dependencies[mod]
                self._print(f"dependencies.{mod}: added {data[mod]}", fg="green")
            elif mod in data and mod not in tpl.dependencies:
                self._print(f"dependencies.{mod}: removed {data[mod]}", fg="red")
                del data[mod]

        for mod in tpl.dependencies:
            if mod not in ["test", "docs", "dev"]:
                continue
            newer = {"adaux": self.parse_dep(self.versions.adaux)[1]}
            for dep in tpl.dependencies[mod]:
                pkg, version = self.parse_dep(dep)
                if version is not None:
                    newer[pkg] = version

            dep_list = data.get(mod, [])
            for i, dep in enumerate(dep_list):
                pkg, version = self.parse_dep(dep)
                if version is not None:
                    if pkg in newer and newer[pkg] != version:
                        self._print(
                            f"dependencies.{mod}: updated {pkg} {version}->{newer[pkg]}",
                            fg="green",
                        )
                        dep_list[i] = dep.replace(version, newer[pkg])

    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("default", "default_apt", "test", "test_apt", "dev", "dev_apt")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "dependencies", allow_unknown=True)
        for key in self.__keys():
            self._to_list("dependencies", key)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("dependencies", _ProtoNamespace())
        data = self.auxd.dependencies
        for key in self.__keys():
            data.setdefault(key, [])

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.dependencies
        for key in data:
            if not key.endswith("_apt"):
                continue
            res = _ProtoNamespace()
            for pkg_or_map in data[key] or []:
                if isinstance(pkg_or_map, str):
                    res.setdefault("all", [])
                    res.all.append(pkg_or_map)
                elif isinstance(pkg_or_map, tp.Mapping):
                    assert len(pkg_or_map) == 1
                    arch, arch_pkgs = next(iter(pkg_or_map.items()))
                    if isinstance(arch_pkgs, str):
                        arch_pkgs = [arch_pkgs]
                    assert isinstance(arch_pkgs, tp.Sequence)
                    res[arch] = arch_pkgs
            data[key] = res

        # warn if dev dependency is outdated
        for pkg in data.dev:
            if pkg.startswith("adaux"):
                compare = self.auxe.versions.adaux
                if pkg != compare:
                    self._print(
                        f"WARNING: your dev dependency {pkg} is different from installed {compare}, please fix.",
                        fg="red",
                    )

    @classmethod
    def parse_dep(cls, dep: str) -> tp.Tuple[str, tp.Optional[str]]:
        if "=" in dep:
            pkg, version = re.split("[=><~]{2}", dep, 1)
        else:
            pkg = dep
            version = None
        return pkg, version

    def bake(self) -> None:
        super().bake()
        config = self.auxe.python_project.config

        for key, deps in self.auxe.dependencies.items():
            if key.endswith("_apt") or key.endswith("_script"):
                continue
            if key == "default":
                # my config writer will mess up dependencies with environment markers
                # if ' are present, but I need ' in auxilium.cfg for the docker files
                # as some are "${VAR}" and '${VAR}' does not work
                config.options.install_requires = [x.replace("'", '"') for x in deps]
            elif deps:
                config["options.extras_require"][key] = deps
