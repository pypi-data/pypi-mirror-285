# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._proto_namespace import _ProtoNamespace
from ._06_dependency import DependencyMixin


class PipMixin(DependencyMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("extra_index_url", "branch_match", "use_uv", "editable_strict")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "pip")
        self._to_proto_ns("pip", iter_mapping=True)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("pip", _ProtoNamespace())
        for key in self.__keys():
            if key == "use_uv":
                self.auxd.pip.setdefault(key, False)
            elif key == "editable_strict":
                self.auxd.pip.setdefault(key, True)
            else:
                self.auxd.pip.setdefault(key, _ProtoNamespace())

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.setdefault("pip", _ProtoNamespace())
        data = self.auxcon.pip
        data.extra_index_url = _ProtoNamespace(
            demo="https://gitlab-ci-token:$CI_JOB_TOKEN@gitlab.x.y/api/v4/projects/118/packages/pypi/simple"
        )
        data.branch_match = _ProtoNamespace(
            demo=_ProtoNamespace(
                url="https://gitlab-ci-token:$CI_JOB_TOKEN@gitlab.x.y/user/demo.git",
                fallback="develop",
            )
        )
        data.use_uv = True
        data.editable_strict = True

    def enriched(self) -> None:
        super().enriched()
        wo_creds = {}
        creds = {}

        data = self.auxe.pip
        for key, url in data.extra_index_url.items():
            if "@" in url:
                pre, url = url.split("@", 1)
                proto, cred = pre.split("//", 1)
                url = f"{proto}//{url}"
                token, var_cred = cred.split(":", 1)
                assert "$" == var_cred[0]
                creds[key] = var_cred[1:]
                assert "$" not in token

            wo_creds[key] = url

        data.extra_index_url_wo_creds = wo_creds
        data.creds = creds
        name = self.auxe.project.name
        version = self.auxe.python_project.version
        data.metadata_filecontent = (
            f"Metadata-Version: 2.1\\nName: {name}\\nVersion: {version}\\n"
        )

    def bake(self) -> None:
        super().bake()

        # we rely on .netrc for the credentials
        name = "pip/pip.conf"
        self.bake_file(name)

    def branch_match_and_cred_passing(
        self, opts: _ProtoNamespace, auxe: _ProtoNamespace
    ) -> None:
        opts.pip_extra_url = self._collect_extra_url(opts.pip_req, auxe)
        opts.pip_cred_vars = self._collect_cred_vars(opts.pip_req, auxe)
        for i, dep in enumerate(opts.pip_req):
            pkg, _ = self.parse_dep(dep)
            match = auxe.pip.branch_match.get(pkg)
            if match is None:
                continue
            # skip matching these branches
            skip = [auxe.gitlab.release_branch]
            var = f'{pkg.upper().replace(".", "_").replace("-", "_")}_MATCHING_REPO'
            opts.pip_req[i] = f"${{{var}:-{dep}}}"
            opts.pip_cred_vars.append(var)
            opts.setdefault("branch_match", [])
            opts.branch_match.append(
                (pkg, var, match["url"], skip, match.get("fallback"))
            )  # variable used by CI

    def _collect_extra_url(
        self, deps: tp.List[str], auxe: _ProtoNamespace
    ) -> tp.List[str]:
        extra_url = set()

        for dep in deps:
            pkg, _ = self.parse_dep(dep)
            url = auxe.pip.extra_index_url.get(pkg)
            if url is not None:
                extra_url.add(url)

        return list(sorted(extra_url))

    def _collect_cred_vars(
        self, deps: tp.List[str], auxe: _ProtoNamespace
    ) -> tp.List[str]:
        cred_vars = set()

        for dep in deps:
            pkg, _ = self.parse_dep(dep)
            cred = auxe.pip.creds.get(pkg)
            if cred is not None:
                cred_vars.add(cred)

        return list(sorted(cred_vars))
