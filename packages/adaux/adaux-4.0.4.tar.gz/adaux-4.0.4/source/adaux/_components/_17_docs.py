# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._proto_namespace import _ProtoNamespace
from ._05_python_project import PythonProjectMixin


class DocsMixin(PythonProjectMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("strict", "framework", "root")

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        self.auxcon.dependencies.docs = [
            self.versions.sphinx,
            self.versions.sphinx_rtd_theme,
            self.versions.sphinx_click,
            self.versions.jupyter_sphinx,
            self.versions.bash_kernel,
        ]

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.docs = _ProtoNamespace()
        data.root = "source/docs"

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "docs")

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("docs", _ProtoNamespace())
        data = self.auxd.docs
        data.setdefault("root", f"{self.auxd.project.source_dir}/docs")
        data.setdefault("framework", "sphinx")

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.docs
        gitlab = self.auxd.gitlab
        if "url" not in data:
            pages_url = gitlab.remote_url.replace("gitlab", "pages")
            remote_name = gitlab.get(
                "remote_name", self.auxe.python_project.second_name
            )
            data.setdefault(
                "url",
                f"https://{gitlab.remote_user}.{pages_url}/{remote_name}",
            )
        self.auxe.python_project.project_urls.Documentation = self.auxe.docs.url

    def bake(self) -> None:
        super().bake()
        data = self.auxe.docs

        # user docs dir
        dest_rel = f"../{data.root}"
        if data.framework == "sphinx":
            self.bake_file(
                "docs/user/conf.py", f"{dest_rel}/conf.py", only_if_inexistent=True
            )
            self.bake_file(
                "docs/user/index.rst", f"{dest_rel}/index.rst", only_if_inexistent=True
            )
            self.bake_file("docs/user/gitignore", f"{dest_rel}/.gitignore")

            for name in ["static"]:
                path = self.target / f"{dest_rel}/{name}"
                path.mkdir(parents=True, exist_ok=True)

            # devops docs dir
            dest_rel = "docs"
            for name in ["static", "templates"]:
                path = self.target / f"{dest_rel}/{name}"
                path.mkdir(parents=True, exist_ok=True)

            self.bake_file("docs/default_conf.py")
            self.bake_file("docs/postprocess_html.py")
            self.bake_file("docs/static/git-link-color.css")
