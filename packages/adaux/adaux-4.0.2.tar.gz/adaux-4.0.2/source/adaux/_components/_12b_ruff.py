# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import copy
import typing as tp

from .._logging import logger
from .._parser import TomlParser
from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._06_dependency import DependencyMixin


class RuffMixin(DependencyMixin, MetaMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return (
            "select",
            "ignore",
            "per_file_ignores",
        )

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.ruff = _ProtoNamespace()
        self.auxcon.dependencies.dev.append(self.versions.ruff)
        data.select = ["E", "F", "B"]
        data.ignore = ["E501"]
        data.per_file_ignores = {"__init__.py": ["F401", "E402", "F403", "F405"]}

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)
        if "ruff" not in self.auxf:
            return
        logger.warning("ruff not fully supported for sync yet")
        data = self.auxf.ruff
        data_full = full.ruff
        data_tpl = tpl.ruff

        old_ignore = data.get("ignore", [])
        order = data_tpl.ignore + old_ignore

        def ordered(list_: tp.Iterable[str]) -> tp.List[str]:
            return list(sorted(list_, key=order.index))

        should_be_present = set(data_tpl.ignore)
        custom = set(old_ignore) - set(data_full.ignore)

        data.ignore = ordered(should_be_present | custom)

        added = set(data.ignore) - set(old_ignore)
        removed = set(old_ignore) - set(data.ignore)
        if added:
            self._print(f"ruff.ignore: added {ordered(added)}", fg="green")
        if removed:
            self._print(f"ruff.ignore: removed {ordered(removed)}", fg="red")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "ruff")
        self._copy_keys_over(self.__keys(), "ruff_test")
        for key in self.__keys()[:2]:
            self._to_list("ruff", key)
            self._to_list("ruff_test", key)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("ruff", _ProtoNamespace())
        self.auxd.setdefault("ruff_test", _ProtoNamespace())
        for key in self.__keys()[:2]:
            self.auxd.ruff.setdefault(key, [])
            self.auxd.ruff_test.setdefault(key, [])

    def bake(self) -> None:  # pylint: disable=too-many-locals,too-many-branches
        super().bake()
        if "ruff" not in self.auxf:
            return
        dest = self.target / "pre-commit/ruff.toml"
        res = copy.copy(self.auxe.ruff)
        data = {"lint": res}
        data["cache-dir"] = "devops/cache/ruff"
        for key in ["per_file_ignores"]:
            res[key.replace("_", "-")] = res.pop(key)

        written = TomlParser.write(data, dest)
        if written:
            self._print(f"baked {dest}", fg="green")

        for key, val in self.auxf.get("ruff_test", {}).items():
            prev = res.get(key, None)
            if prev is None:
                updated = val
            elif isinstance(prev, list):
                assert isinstance(val, list)
                updated = prev + val
            elif isinstance(prev, dict):
                print(prev, val)
                assert isinstance(val, dict)
                updated = {**prev, **val}
            else:
                raise NotImplementedError(prev)
            res[key] = updated

        dest = self.target / "pre-commit/ruff-test.toml"
        written = TomlParser.write(data, dest)
        if written:
            self._print(f"baked {dest}", fg="green")
