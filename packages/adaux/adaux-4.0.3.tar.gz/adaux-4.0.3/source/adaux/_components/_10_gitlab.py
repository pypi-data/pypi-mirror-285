# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import subprocess

from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._05_project import ProjectMixin


class GitlabMixin(ProjectMixin, MetaMixin):
    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        self.auxcon.gitlab = _ProtoNamespace(
            vip_branches=_ProtoNamespace(
                develop=_ProtoNamespace(push_access_level=40, allow_force_push=True),
                release=_ProtoNamespace(),
            )
        )

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.gitlab
        data.default_branch = "develop"
        data.release_branch = "release"
        data.remote_user = "administratum"
        data.remote_name = "auxilium"
        data.remote_url = "gitlab.x.y"
        data.squash = True

    def formatted(self) -> None:
        super().formatted()
        keys = [
            "remote_user",
            "remote_name",
            "remote_url",
            "default_branch",
            "release_branch",
            "vip_branches",
            "squash",
        ]
        self._copy_keys_over(keys, "gitlab")
        self._to_proto_ns("gitlab", "vip_branches", iter_mapping=True)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("gitlab", _ProtoNamespace())
        data = self.auxd.gitlab
        data.setdefault("vip_branches", _ProtoNamespace())

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)
        if "gitlab" not in self.auxf:
            self.auxf.gitlab = tpl.gitlab
            self._print("gitlab added", fg="green")
            return
        data = self.auxf.gitlab
        if self.is_enabled("docs"):
            if "remote_url" in data and "remote_user" in data:
                return
            proc = subprocess.run(
                ["git", "remote", "-v"], capture_output=True, check=False
            )
            if proc.returncode != 0:
                return
            full_url = proc.stdout.decode("utf-8").split()[1]
            _, url = full_url.split("@", 1)
            defaults = {}
            defaults["remote_url"], rest = url.split(":", 1)
            defaults["remote_user"], rest = rest.split("/", 1)
            defaults["remote_name"] = rest.replace(".git", "")
            key = "remote_url"
            for key, val in defaults.items():
                if key not in data:
                    if key == "remote_name" and val == self.auxf.project.name:
                        continue
                    data[key] = val
                    self._print(f"gitlab.{key}: added {data[key]}", fg="green")

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.gitlab
        vip_branch_names = list(data.vip_branches)
        defaults = dict(
            default_branch=vip_branch_names[0], release_branch=vip_branch_names[-1]
        )
        for key, val in defaults.items():
            data.setdefault(key, val)

        data.setdefault("squash", True)
        assert isinstance(data.squash, bool)
        # https://docs.gitlab.com/ee/api/protected_branches.html
        default_branch_settings = {
            (False, False): dict(
                allow_force_push=True, push_access_level=30, merge_access_level=30
            ),
            (True, False): dict(push_access_level=0, merge_access_level=30),
            (False, True): dict(push_access_level=0, merge_access_level=40),
            (True, True): dict(push_access_level=0, merge_access_level=40),
        }
        for key, val in data.vip_branches.items():
            mark = (key == data.default_branch, key == data.release_branch)
            for skey, sval in default_branch_settings[mark].items():
                val.setdefault(skey, sval)

        if self.is_enabled("pythonproject"):
            if "remote_user" in data and "remote_url" in data:
                remote_name = data.get(
                    "remote_name", self.auxe.python_project.second_name
                )
                self.auxe.python_project.project_urls.Source = (
                    f"https://{data.remote_url}/{data.remote_user}/{remote_name}"
                )

        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0:
            data.setdefault("current_branch", proc.stdout.decode("utf-8").strip())
