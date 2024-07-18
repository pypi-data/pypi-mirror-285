# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import copy
import os
import subprocess
import sys
import typing as tp
from pathlib import Path

from .._parser import ConfigParser
from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._06_dependency import DependencyMixin


class PylintMixin(DependencyMixin, MetaMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return (
            "disable",
            "good_names",
            "class_attr_rgx",
            "min_similarity_lines",
            "max_module_lines",
            "argument_rgx",
            "attr_rgx",
            "function_rgx",
            "variable_rgx",
            "method_rgx",
        )

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.pylint = _ProtoNamespace()
        self.auxcon.dependencies.dev.append(self.versions.pylint)
        data.disable = [
            "line-too-long",
            "wildcard-import",
            "use-dict-literal",
            "wrong-import-position",
            "too-few-public-methods",
        ]
        if not self.is_enabled("docs") or negative_default:
            data.disable += [
                "missing-class-docstring",
                "missing-module-docstring",
                "missing-function-docstring",
            ]

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)
        data = self.auxf.pylint
        data_full = full.pylint
        data_tpl = tpl.pylint
        # will be left alone once defined, not removed
        hysteresis = [
            "missing-class-docstring",
            "missing-module-docstring",
            "missing-function-docstring",
        ]

        old_disable = data.disable
        order = data_tpl.disable + old_disable + hysteresis

        def ordered(list_: tp.Iterable[str]) -> tp.List[str]:
            return list(sorted(list_, key=order.index))

        should_be_present = set(data_tpl.disable)
        custom = set(old_disable) - (set(data_full.disable) - set(hysteresis))

        data.disable = ordered(should_be_present | custom)

        added = set(data.disable) - set(old_disable)
        removed = set(old_disable) - set(data.disable)
        if added:
            self._print(f"pylint.disable: added {ordered(added)}", fg="green")
        if removed:
            self._print(f"pylint.disable: removed {ordered(removed)}", fg="red")

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.pylint
        data.setdefault("disable", [])
        data.disable += ["too-few-public-methods", "no-self-use"]
        data.good_names = ["t", "dt"]

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "pylint")
        self._copy_keys_over(self.__keys(), "pylint_test")
        for key in self.__keys()[:2]:
            self._to_list("pylint", key)
            self._to_list("pylint_test", key)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("pylint", _ProtoNamespace())
        self.auxd.setdefault("pylint_test", _ProtoNamespace())
        for key in self.__keys()[:2]:
            self.auxd.pylint.setdefault(key, [])
            self.auxd.pylint_test.setdefault(key, [])

    def bake(self) -> None:  # pylint: disable=too-many-locals,too-many-branches
        super().bake()
        # ensure python version
        found_version = ".".join(map(str, sys.version_info[:2]))
        if found_version != self.auxe.python_project.minimal_version:
            raise RuntimeError(
                f"you are using python {found_version}, please use python {self.auxe.python_project.minimal_version} (minimal version)."
            )

        # the home of the user has a potential .pylintrc file,
        # which will influence the creation
        env = os.environ.copy()
        pylint_rc = Path(os.environ["HOME"]) / ".pylintrc"
        if pylint_rc.exists():
            env["HOME"] = "/tmp"
        resp = subprocess.run(
            ["pylint", "--generate-rcfile"], capture_output=True, check=True, env=env
        )
        text = resp.stdout.decode()

        hooks = self.auxe.pre_commit.hooks
        configs = [ConfigParser.read_string(text)]
        self.patch(configs[0])
        keys = ["pylint"]
        writeout = ["pylint" in hooks]

        writeout.append("pylint-test" in hooks)
        if writeout[-1]:
            keys.append("pylint-test")

        for i, key in enumerate(keys):
            config = configs[-1]
            if i > 0:
                config = copy.deepcopy(config)
                configs.append(config)

            key = key.replace("-", "_")
            for key1, key2, key3 in [
                ("MESSAGES CONTROL", "disable", "disable"),
                ("BASIC", "good-names", "good_names"),
                ("SIMILARITIES", "min-similarity-lines", "min_similarity_lines"),
                ("FORMAT", "max-module-lines", "max_module_lines"),
                ("BASIC", "variable-rgx", "variable_rgx"),
                ("BASIC", "const-rgx", "const_rgx"),
                ("BASIC", "function-rgx", "function_rgx"),
                ("BASIC", "argument-rgx", "argument_rgx"),
                ("BASIC", "class-rgx", "class_rgx"),
                ("BASIC", "attr-rgx", "attr_rgx"),
                ("BASIC", "method-rgx", "method_rgx"),
                ("BASIC", "attr-rgx", "attr_rgx"),
                ("BASIC", "class-attribute-rgx", "class_attr_rgx"),
            ]:
                subconfig = config[key1]
                data = self.auxe[key]
                if key2 in ["good-names", "disable"]:
                    proplist = copy.copy(subconfig[key2])
                    for x in data[key3]:
                        proplist[-1] += ","
                        if x in proplist:
                            raise RuntimeError(f"{x} is already marked {key3}")
                        proplist.append(x)
                    subconfig[key2] = proplist
                else:
                    if key3 in data:
                        subconfig[key2] = data[key3]

            config["SIMILARITIES"]["ignore-imports"] = "yes"

        for key, config, wout in zip(keys, configs, writeout):
            if not wout:
                continue
            dest = self.target / f"pre-commit/{key}rc"
            written = ConfigParser.write(config, dest)
            if written:
                self._print(f"baked {dest}", fg="green")

    def patch(self, config: _ProtoNamespace) -> None:
        # 2023.11, due to different ordering of use-symbolic-message-instead
        # in clang and gcc pylint-3.0.2, we need to get clang to gcc
        disable: tp.List[str] = config["MESSAGES CONTROL"]["disable"]
        move_obj = "use-symbolic-message-instead,"
        if move_obj in disable:
            move_after = "use-implicit-booleaness-not-comparison-to-zero"
            disable[disable.index(move_after)] += ","
            disable.remove(move_obj)
            disable.append(move_obj[:-1])
