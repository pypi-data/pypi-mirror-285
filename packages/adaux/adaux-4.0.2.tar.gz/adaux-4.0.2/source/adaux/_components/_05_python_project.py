# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import sys
import typing as tp
from pathlib import Path

from .._logging import logger
from .._parser import ConfigParser
from .._parser import Jinja2Parser
from .._proto_namespace import _ProtoNamespace
from ._05_project import ProjectMixin


class PythonProjectMixin(ProjectMixin):
    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        self.auxcon.setdefault("python_project", _ProtoNamespace())

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.python_project
        data.minimal_version = (self.deduce_python_version(),)

    def formatted(self) -> None:
        super().formatted()
        keys = [
            "minimal_version",
            "supported_versions",
            "project_urls",
        ]
        self._copy_keys_over(keys, "python_project")
        self._to_list("python_project", "project_urls")

    def defaulted(self) -> None:
        # pylint: disable=no-member
        super().defaulted()
        data = self.auxd.python_project
        defaults = dict(
            project_urls=_ProtoNamespace(),
            supported_versions=[self.auxf.python_project.minimal_version],
        )
        for key, val in defaults.items():
            data.setdefault(key, val)

    def enriched(self) -> None:
        super().enriched()
        pro = self.auxe.project
        data = self.auxe.python_project
        data.minimal_version_slug = data.minimal_version.replace(".", "")
        data.module_dir = pro.source_dir + "/" + pro.name.replace(".", "/")
        data.namespace_name, data.second_name = "", pro.name
        if "." in pro.name:
            data.namespace_name, data.second_name = pro.name.split(".", 1)
        data.setup_fields = [
            "name",
            "author",
            "license",
            "description",
            "long_description",
            "project_urls",
        ]
        data.version, _ = self.get_current_version_and_lines(data)
        data.release_notes = self.get_release_notes(self.auxd)

    def bake(self) -> None:
        super().bake()
        pro = self.auxe.project
        data = self.auxe.python_project
        self.bake_file("install-dev.sh", chmod=0o755)
        self.bake_file("root/_setup.py", "../setup.py")

        srcj = self.root / "root/setup.cfg.jinja2"
        with Jinja2Parser.render_to_tmp(srcj, aux=self.auxe) as src:
            data.config = ConfigParser.read(src)
            for key in data.setup_fields:
                if key in data:
                    val = data[key]
                elif key in pro:
                    val = pro[key]
                else:
                    continue

                if val:
                    data.config.metadata[key] = val

    def writeout(self) -> None:
        super().writeout()
        if self.is_enabled("pip"):
            dest = self.target / "../setup.cfg"
            written = ConfigParser.write(self.auxe.python_project.pop("config"), dest)
            if written:
                self._print(f"baked {dest}", fg="green")

    @classmethod
    def deduce_project_name(cls, path: tp.Optional[Path] = None) -> str:
        path = path or (Path.cwd())

        # level 1
        for obj in path.glob("*/__init__.py"):
            with obj.open("r", encoding="utf-8") as f:
                if "__version__" in f.read():
                    lvl1 = obj.parent.stem
                    return lvl1
        # level 2
        for obj in path.glob("*/*/__init__.py"):
            with obj.open("r", encoding="utf-8") as f:
                if "__version__" in f.read():
                    lvl1 = obj.parent.stem
                    lvl2 = obj.parent.parent.stem
                    if lvl2 in ["source"]:
                        return lvl1
                    return f"{lvl2}.{lvl1}"
        return "not-found"

    @classmethod
    def deduce_project_slug(cls) -> str:
        proj_name = cls.deduce_project_name()
        if proj_name.count(".") == 1:
            ns, sub = proj_name.split(".")
            return ns[:2] + sub[:3]
        return proj_name[:3]

    @classmethod
    def deduce_python_version(cls) -> str:
        return ".".join(map(str, sys.version_info[:2]))

    def get_current_version_and_lines(
        self, data: tp.Optional[_ProtoNamespace] = None
    ) -> tp.Tuple[str, tp.List[str]]:
        data = data or self.auxe.python_project
        dir_ = data.module_dir
        init = self.auxcon_file.parent / dir_ / "__init__.py"
        if not init.exists():
            logger.warning(
                "%s/%s does not exist, retuning 'n/a' as version!", dir_, init.name
            )
            return "n/a", []

        with init.open("r", encoding="utf8") as f:
            lines = f.readlines()
            for line in lines:
                if "__version__" in line:
                    version = line.strip().split('"', 2)[1]
                    break
            else:
                raise RuntimeError(f"version not found in {init}")

        return version, lines

    def get_release_notes(
        self, auxd: tp.Optional[_ProtoNamespace] = None
    ) -> tp.Dict[str, str]:
        data = auxd or self.auxd
        dir_ = data.project.source_dir
        notes = self.auxcon_file.parent / dir_ / "release-notes.txt"
        release_note: tp.Dict[str, str] = {}

        if not notes.exists():
            logger.warning(
                "%s/%s does not exist, retuning an empty dict!", dir_, notes.name
            )
            return {}
        with notes.open("r", encoding="utf8") as f:
            for line in f.readlines():
                version, note = line.strip().split(" ", 1)
                release_note[version] = note

        return release_note

    def create_source(self) -> None:
        source_dir = Path(self.auxd.project.source_dir)
        module_dir = source_dir / self.auxd.project.name.replace(".", "/")
        tests_dir = source_dir / "tests"

        for path in [source_dir, module_dir, tests_dir]:
            path.mkdir(parents=True, exist_ok=True)

        init_file = module_dir / "__init__.py"
        rn_file = source_dir / "release-notes.txt"
        if not init_file.exists():
            with init_file.open("w", encoding="utf-8") as f:
                f.write('__version__ = "0.0.0"\n')
        if not rn_file.exists():
            with rn_file.open("w", encoding="utf-8") as f:
                f.write("0.0.0 unreleased\n")
