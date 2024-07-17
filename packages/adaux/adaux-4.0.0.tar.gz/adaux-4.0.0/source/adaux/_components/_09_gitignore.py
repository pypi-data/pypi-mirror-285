# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._parser import Jinja2Parser
from .._proto_namespace import _ProtoNamespace
from ._05_project import ProjectMixin


class GitIgnoreMixin(ProjectMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("root", "source")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "git_ignore")
        for key in self.__keys():
            self._to_list("git_ignore", key)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("git_ignore", _ProtoNamespace())
        for key in self.__keys():
            self.auxd.git_ignore.setdefault(key, [])

    def bake(self) -> None:
        super().bake()
        self.bake_file("gitignore", ".gitignore")

        data = self.auxe.project

        name1 = "root/gitignore"
        name2 = "root/source/gitignore"
        src1 = self.root / f"{name1}.jinja2"
        src2 = self.root / f"{name2}.jinja2"
        dest = self.target / ".." / ".gitignore"
        if data.source_dir != ".":
            self.bake_file(name1, "../.gitignore")
            self.bake_file(name2, f"../{data.source_dir}/.gitignore")

            if self.is_enabled("pythonproject"):
                pdata = self.auxe.python_project
                flip = False
                for key in list(pdata.config):
                    if flip:
                        pdata.config.move_to_end(key)
                    if key == "options":
                        flip = True
                        pdata.config["options.packages.find"] = dict(
                            where=data.source_dir
                        )

        else:
            tpl1 = Jinja2Parser.read(src1)
            tpl2 = Jinja2Parser.read(src2)
            tpl = f"{tpl1.render(aux=self.auxe)}\n{tpl2.render(aux=self.auxe)}"
            written = Jinja2Parser.write(tpl, dest)
            if written:
                self._print(f"baked {dest}", fg="green")
