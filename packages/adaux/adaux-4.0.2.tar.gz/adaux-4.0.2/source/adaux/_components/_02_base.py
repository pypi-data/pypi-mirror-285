# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import copy
import typing as tp

from .._logging import logger
from .._proto_namespace import _ProtoNamespace
from .._util import EnvironmentVariables
from .._util import LazyVersionStr
from ._01_file_io_support import FileIOSupport


class BaseComponent(FileIOSupport):
    def __init__(self) -> None:
        super().__init__()
        self.versions = _ProtoNamespace(
            pytest="pytest~=8.2.2",
            pytest_cov="pytest-cov~=5.0.0",
            pre_commit="pre-commit>=3.3.3",
            mypy="mypy==1.10.1",
            pylint="pylint==3.2.0",
            black="black==24.4.2",
            sphinx="sphinx==6.2.1",  # rtd-theme forces sphinx <7
            sphinx_rtd_theme="sphinx-rtd-theme>=1.2.2",
            sphinx_click="sphinx-click>=4.4.0",
            jupyter_sphinx="jupyter-sphinx>=0.4",
            bash_kernel="bash_kernel>=0.8",
            blacken_docs="blacken-docs==1.16.0",
            pre_commit_hooks="pre-commit-hooks==v4.6.0",
            pyupgrade="pyupgrade==v3.16.0",
            pycln="pycln==v2.4.0",
            reorder_python_imports="reorder_python_imports==v3.12.0",
            isort="isort==5.12.0",
            encryption_check="encryption_check==v1.0.0",
            docstr_coverage="docstr-coverage==v2.3.0",
            requests="requests==2.32.3",
            types_requests="types-requests",
            adaux=f"adaux=={LazyVersionStr()}",
            docker_compose_file="3.8",
            ci_docker_image="docker:27.0.3",  # if you touch this, build build-docker-with-adaux locally first && mm run docker-upgrade
            ci_precursor_image="registry.gitlab.prostructura.ch/administratum/auxilium/dind-with-precursor:latest",
            ci_adaux_image=f"docker.io/prostructura/adaux:{LazyVersionStr()}",
            ruff="ruff==v0.4.10",
            uv="uv==0.1.45",
        )
        self.auxcon = _ProtoNamespace()

    def migrate(self) -> None:
        logger.info("no migration plugin detected")

    def formatted(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.auxf = _ProtoNamespace()

    def defaulted(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.auxd = copy.deepcopy(self.auxf)

    def templated(self, negative_default: bool = False) -> None:
        # uses auxcon directly
        pass

    def demodata(self) -> None:
        # uses auxcon directly
        pass

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        pass

    def enriched(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.auxe = copy.deepcopy(self.auxd)
        self.auxe.versions = self.versions
        self.auxe.env_var = EnvironmentVariables(self.auxe)

    def hydrated(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.auxh = copy.deepcopy(self.auxe)

    def bake(self) -> None:
        pass

    def writeout(self) -> None:
        pass

    @classmethod
    def compose(cls, *types: type) -> "tp.Type[BaseComponent]":
        if cls not in types:
            types = (cls,) + types
        bases = tuple(reversed(types))
        return type("DynComponent", bases, {})

    def step_migrate(self) -> None:
        logger.info("migrating to %s", self._to_version)  # type: ignore  # pylint: disable=no-member

    def _copy_keys_over(
        self,
        keys: tp.Sequence[str],
        cat: str,
        *subcats: str,
        allow_unknown: bool = False,
    ) -> None:
        scat, parent, data = self._drill_down((cat,) + subcats, self.auxcon)
        if scat is None:
            return

        res = _ProtoNamespace()
        for key in keys:
            if key in data:
                res[key] = copy.deepcopy(data[key])
        unknown = set(data) - set(keys)
        if unknown and allow_unknown:
            for key in filter(lambda x: x in unknown, data):
                res[key] = copy.deepcopy(data[key])
        unknown = set(data) - set(res)
        if unknown:
            raise RuntimeError(
                f"unknows options {unknown} for {'.'.join((cat,)+subcats)}"
            )

        if res:
            dest = self.auxf
            for scat in (cat,) + subcats:
                dest.setdefault(scat, _ProtoNamespace())
                parent = dest
                dest = dest[scat]

            if scat in parent:
                parent[scat].update(res)
            else:
                parent[scat] = res

    def _to_list(self, *cats: str) -> None:
        scat, parent, data = self._drill_down(cats, self.auxf)
        if scat is None:
            return
        parent[scat] = data or []

    def _to_proto_ns(
        self,
        *cats: str,
        iter_mapping: bool = False,
        source: tp.Optional[_ProtoNamespace] = None,
    ) -> None:
        source = source or self.auxf
        scat, parent, data = self._drill_down(cats, source)
        if scat is None:
            return
        parent[scat] = data = _ProtoNamespace(data or {})

        if iter_mapping:
            for key in data:
                if isinstance(data.get(key, None), tp.Mapping):
                    self._to_proto_ns(key, source=data, iter_mapping=True)
                elif data[key] is None:
                    data[key] = _ProtoNamespace()

    def _drill_down(
        self, cats: tp.Tuple[str, ...], data: _ProtoNamespace
    ) -> tp.Tuple[tp.Optional[str], _ProtoNamespace, _ProtoNamespace]:
        cat = None
        for cat in cats:
            parent = data
            if data is None or cat not in data:
                return None, parent, parent
            data = data[cat]
        return cat, parent, data
