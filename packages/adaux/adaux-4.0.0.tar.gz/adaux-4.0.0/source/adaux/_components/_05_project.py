# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import datetime
import os

from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin


class ProjectMixin(MetaMixin):
    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.setdefault("project", _ProtoNamespace())
        data.creation_year = self.get_current_year()

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.project
        data.name = "hallo.world"
        data.slug = "hlw"
        data.author = "anonymous"
        data.license = "MIT"

    def formatted(self) -> None:
        super().formatted()
        keys = [
            "name",
            "slug",
            "author",
            "creation_year",
            "license",
            "source_dir",
        ]
        self._copy_keys_over(keys, "project")

    def defaulted(self) -> None:
        # pylint: disable=no-member
        super().defaulted()
        data = self.auxd.project
        data.setdefault("license", "Proprietary")
        data.setdefault("source_dir", "source")

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.project
        data.active_years = self.get_active_years()

    def bake(self) -> None:
        super().bake()
        # license
        data = self.auxe.project
        if data.license != "Proprietary":
            self.bake_file(
                f"license/{data.license}.txt",
                (self.target / ".." / "LICENSE.txt").resolve(),
            )

    @classmethod
    def deduce_user(cls) -> str:
        return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    def get_active_years(self) -> str:
        current_year = self.get_current_year()
        creation_year = self.auxd.project.creation_year
        if creation_year == current_year:
            return f"{creation_year}"

        return f"{creation_year}-{current_year}"

    @classmethod
    def get_current_year(cls) -> str:
        return str(datetime.date.today().year)

    def step_migrate(self) -> None:
        super().step_migrate()

        if self.to_version("3.0.0"):  # type: ignore
            data = self.auxcon.project
            pdata = _ProtoNamespace()
            for key in ["minimal_version", "supported_versions", "project_urls"]:
                if key in data:
                    pdata[key] = data.pop(key)
            if pdata:
                self.auxcon.python_project = pdata
