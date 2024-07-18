# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import itertools
import typing as tp

from .._logging import logger
from .._parser import Jinja2Parser
from .._parser import YamlParser
from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._05_project import ProjectMixin
from ._06_dependency import DependencyMixin
from ._18_payload import PayloadMixin


class DockerMixin(PayloadMixin, DependencyMixin, ProjectMixin, MetaMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("base_match", "platform", "compose_version")

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        data = self.auxcon.payload

        data.setdefault("python", _ProtoNamespace())
        data.python["check-release-notes"] = _ProtoNamespace()

        if self.is_enabled("pre-commit"):
            data.setdefault("with_dependency", _ProtoNamespace())
            run = "pre-commit"
            build = f"build-{run}"
            data.with_dependency[build] = dict(deps=["build-python-deps"])
            data.with_dependency[run] = dict(variant={"all": dict(cmd="--all")})

        if self.is_enabled("pytest"):
            data.setdefault("with_dependency", _ProtoNamespace())
            run = "pytest"
            build = f"build-{run}"
            data.with_dependency[build] = dict(deps=["build-python-deps"])
            data.with_dependency[run] = dict()
            if self.is_enabled("coverage"):
                data.with_dependency[run]["variant"] = {
                    "mr": {"marker": ""},
                    "cov": dict(coverage=95, variant={"mr": None}),
                }

        if self.is_enabled("docs"):
            run = "docs"
            build = f"build-{run}"
            data.setdefault("with_dependency", _ProtoNamespace())
            data.with_dependency[build] = dict(
                deps=["build-python-deps"], param=dict(extra_req="docs")
            )
            data.with_dependency[run] = None

        if self.is_enabled("gitlab"):
            data.setdefault("docker_run", _ProtoNamespace())
            data.docker_run["gitlab-release"] = _ProtoNamespace(
                param=_ProtoNamespace(
                    environment=_ProtoNamespace(
                        RELEASE_TAG="{version}", RELEASE_DESCRIPTION="{release_note}"
                    )
                )
            )
            data.docker_run["pkg-gitlab"] = _ProtoNamespace()

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.payload
        data.docker_settings = _ProtoNamespace(
            platform="amd64", base_match={"mybase": dict(fallback="develop")}
        )

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)

        for flavor in ["docker_build", "docker_run", "python", "with_dependency"]:
            if flavor not in tpl.payload:
                continue
            data = self.auxf.payload.get(flavor, _ProtoNamespace())
            old = list(data)
            new = list(tpl.payload[flavor])
            last_idx = 0
            for name, payload in full.payload[flavor].items():
                if name in new and name not in old:
                    data[name] = payload
                    old.insert(last_idx + 1, name)
                    self._print(f"payload.{flavor}: added {name}", fg="green")
                elif name in old and name not in new:
                    del data[name]
                    old.remove(name)
                    self._print(f"payload.{flavor}: removed {name}", fg="red")
                if name in old and name in new:
                    last_idx = old.index(name)
            if data:
                self.auxf.payload[flavor] = data

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "payload", "docker_settings")
        self._to_proto_ns("payload", "docker_settings")
        self._to_proto_ns("payload", "docker_settings", "base_match", iter_mapping=True)

    def defaulted(self) -> None:
        super().defaulted()
        payload_data = self.auxd.payload
        payload_data.setdefault("docker_settings", _ProtoNamespace())
        data = payload_data.docker_settings
        data.setdefault("base_match", _ProtoNamespace())
        data.setdefault("platform", None)
        data.setdefault("compose_version", self.versions.docker_compose_file)

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.payload.docker_settings
        data.project_dir = "../.."
        data.source_dir = f"../../{self.auxe.project.source_dir}"
        self._docker_build_enrich()
        self._docker_run_enrich()

    def _docker_build_enrich(self) -> None:
        extra_req_default = {
            "python-deps": ["default"],
            "pytest": ["test"],
            "pre-commit": ["test", "dev"],
            "pytest-standalone": ["default", "test"],
            "docs": ["docs"],
            "ansible-deploy": ["deploy"],
            "devenv": ["test", "dev"],
        }
        deps = self.auxe.dependencies
        data = self.auxe.payload
        prefix = "build-"
        for key, payload_cfg in data.docker_build.items():
            assert key.startswith(prefix)
            name = key[len(prefix) :]
            payload_cfg.setdefault("param", _ProtoNamespace())
            assert isinstance(payload_cfg.param, _ProtoNamespace)
            param = payload_cfg.param
            if "extra_req" in param and isinstance(param.extra_req, str):
                param.extra_req = [param.extra_req]

            param.setdefault("pip_req", [])
            param.setdefault("script", [])
            param.setdefault("base", None)
            self._adjust_base_on_match_entry(param, self.auxe)

            param.setdefault("apt_req", {})

            self._set_name_and_version(param, name)

            if "mode" in param:
                supported = ["django", "django+nginx", "ansible"]
                if param.mode not in supported:
                    raise RuntimeError(
                        f"mode {param.mode} is not supported {supported}"
                    )

            # branch matching and dep settings
            fallback = extra_req_default.get(param.docker_name, [])
            needed = param.get("extra_req", fallback)
            param.pip_req = self._unique_sum(
                param.pip_req, *[deps.get(x, []) for x in needed]
            )
            param.apt_req = self._unique_sum_dict(
                param.apt_req, *[deps.get(x + "_apt", {}) for x in needed]
            )
            param.script = self._sum(
                param.script, *[deps.get(x + "_script", []) for x in needed]
            )
            assert all('"' not in x for x in param.pip_req)

            if self.is_enabled("pip"):
                self.branch_match_and_cred_passing(param, self.auxe)  # type: ignore

    def _docker_run_enrich(self) -> None:
        data = self.auxe.payload
        for key, payload_cfg in data.docker_run.items():
            payload_cfg.setdefault("param", _ProtoNamespace())
            param = payload_cfg.param

            res = []
            if "assets" in param:
                if isinstance(param.assets, str):
                    param.assets = [param.assets]

                for x in param.assets:
                    shortname = x.rsplit("/", 1)[1]
                    url = "$CI_API_V4_URL/projects/$CI_PROJECT_ID/packages/generic/" + x
                    res.append(
                        r"{\"name\":\"" + shortname + r"\",\"url\":\"" + url + r"\"}"
                    )
            param.assets = res
            self._set_name_and_version(param, key)
            param.setdefault("services", [param.service_name])

    def _set_name_and_version(self, param: _ProtoNamespace, name: str) -> None:
        slug = self.auxe.project.slug
        param.service_name = name
        if param.service_name == slug:
            raise RuntimeError(
                f"service name should not be identical to project slug '{slug}'"
            )

        param.setdefault("image_name", f"{slug}-{param.service_name}")

        param.setdefault("docker_name", name)
        param.setdefault("version", self.auxe.python_project.minimal_version)
        if not isinstance(param.version, str):
            raise RuntimeError(
                f"please specity the version '{param.version}' in {name} as a string"
            )
        param.setdefault("version_slug", param.version.replace(".", ""))

    def _adjust_base_on_match_entry(
        self,
        opts: _ProtoNamespace,
        auxe: _ProtoNamespace,
    ) -> None:
        base_match = auxe.payload.docker_settings.base_match
        if opts.base is None:
            return
        image, tag = opts.base.rsplit(":", 1)
        if image not in base_match:
            return
        fallback = base_match[image].fallback
        var = (
            f'{image.upper().replace("/", "_").replace(".", "_").replace("-", "_")}_TAG'
        )
        skip = [auxe.gitlab.release_branch]

        fallback = self.auxe.env_var.apply_format(fallback)
        tag = self.auxe.env_var.apply_format(tag)
        # changing this tuple-order affects the jinja2 files!
        opts.base_match = [(image, var, skip, fallback, tag)]

        opts.base = f"{image}:${var}"

    def bake(self) -> None:  # pylint: disable=too-many-branches
        super().bake()
        data = self.auxe.payload
        settings = self.auxe.payload.docker_settings

        config = _ProtoNamespace(
            [("version", settings.compose_version), ("services", {})]
        )

        # pylint: disable=too-many-nested-blocks
        for val in data.docker_run.values():
            self._bake_docker_compose_file(val, config)

        for val in data.docker_build.values():
            self._bake_docker_build_file(val)
            self._bake_docker_compose_file(val, config)

        dest = self.target / "docker/compose.yml"
        written = YamlParser.write(config, dest)
        if written:
            self._print(f"baked {dest}", fg="green")

        # self._add_compositions(config)

    def _bake_docker_build_file(self, payload: _ProtoNamespace) -> None:
        opts = payload.param
        display_name = opts.docker_name
        if opts.docker_name != opts.service_name:
            display_name += f"@{opts.service_name}"

        for name, from_adaux in [
            (f"docker/{opts.docker_name}.dockerfile", False),
            (f"docker/{opts.docker_name}/Dockerfile", False),
            (f"docker/services/{opts.docker_name}/Dockerfile", True),
        ]:
            try:
                self.bake_file(
                    name,
                    f"docker/{opts.service_name}.dockerfile",
                    opts=opts,
                    custom=not from_adaux,
                )
                if from_adaux:
                    logger.debug("%s: Dockerfile found@%s [adaux]", display_name, name)
                else:
                    logger.info("%s: Dockerfile found@%s", display_name, name)
                return
            except FileNotFoundError:
                logger.debug("%s: fail@%s", display_name, name)
        raise RuntimeError(
            f"Dockerfile for {display_name} not found. "
            "Run this command with -vvv to see valid file locations"
        )

    def _bake_docker_compose_file(
        self, payload: _ProtoNamespace, config: _ProtoNamespace
    ) -> None:
        # pylint: disable=too-many-locals
        opts = payload.param

        input_config, _ = self._get_part_config(opts)
        valid = {"services", "networks"}
        invalid_keys = set(input_config.keys()) - valid
        if invalid_keys:
            raise RuntimeError(
                f"only {valid} can be defined in compose files. Found {invalid_keys}"
            )

        names = [opts.service_name]  # check service first
        if opts.docker_name != opts.service_name:
            names.append(opts.docker_name)
        for valid, (key, val) in itertools.product(  # bc for-for-break
            names,
            input_config.services.items(),
        ):
            if key == valid:
                services = _ProtoNamespace({opts.service_name: val})
                self._update_config(payload, services, config)
                break
        else:
            logger.debug(
                "%s found no match, but is accepted as a collection of services: [%s]",
                opts.docker_name,
                ", ".join(opts.services),
            )

        # update networks
        config.setdefault("networks", _ProtoNamespace())
        custom_networks = input_config.get("networks", _ProtoNamespace())
        for network, val in custom_networks.items():
            if network in config["networks"]:
                if config["networks"][network] != val:
                    raise RuntimeError(
                        f"network {network} already defined differently..."
                    )
        config["networks"].update(custom_networks)
        if not config["networks"]:
            del config["networks"]

    def _get_part_config(
        self, opts: _ProtoNamespace
    ) -> tp.Tuple[_ProtoNamespace, bool]:
        logger.debug(
            "%s: looking for compose info %s...",
            opts.service_name,
            opts.docker_name,
        )
        src_dir = self.root / "docker" / "services"
        custom_dir = self.target_custom / "docker"

        # service could be a variant with no own docker name
        # docker_name must exist
        for path, from_adaux in [
            (custom_dir / opts.service_name / "compose", False),
            (custom_dir / opts.service_name, False),
            (custom_dir / opts.docker_name / "compose", False),
            (custom_dir / opts.docker_name, False),
            (src_dir / opts.docker_name / "compose", True),
            (custom_dir / "compose", False),
        ]:
            src = path.with_suffix(".yml")
            srcj = path.with_suffix(".yml.jinja2")
            if srcj.exists():
                with Jinja2Parser.render_to_tmp(srcj, aux=self.auxe, opts=opts) as src:
                    logger.info("%s: found@%s", opts.docker_name, srcj)
                    return YamlParser.read(src), from_adaux

            if src.exists():
                logger.info("%s: found@%s", opts.docker_name, src)
                return YamlParser.read(src), from_adaux
            logger.debug("%s: fail@%s[.jinja2]", opts.docker_name, src)

        raise RuntimeError(
            f"Definition for {opts.docker_name} not found. "
            "Run this command with -vvv to see valid file locations"
        )

    def _update_config(
        self,
        payload: _ProtoNamespace,
        custom_services: _ProtoNamespace,
        config: _ProtoNamespace,
    ) -> None:
        for service_name, val in custom_services.items():
            for key in list(val):
                if payload.flavor == "docker_build":
                    if key not in ["build", "image"]:
                        del val[key]
                elif payload.flavor == "docker_run":
                    if key in ["build"]:
                        del val[key]
                else:
                    raise NotImplementedError(payload.flavor)
            logger.debug("updating config with %s", service_name)
            config["services"].setdefault(service_name, val)
            config["services"][service_name].update(val)

    @staticmethod
    def _unique_sum(*args: tp.List[str]) -> tp.List[str]:
        res = []
        for part in args:
            for x in part:
                if x not in res:
                    res.append(x)
        return res

    @staticmethod
    def _unique_sum_dict(
        *args: tp.Dict[str, tp.List[str]]
    ) -> tp.Dict[str, tp.List[str]]:
        res: tp.Dict[str, tp.List[str]] = {}
        for part in args:
            for key, val in part.items():
                res.setdefault(key, [])
                for x in val:
                    if x not in res[key]:
                        res[key].append(x)

        return res

    @staticmethod
    def _sum(*args: tp.List[str]) -> tp.List[str]:
        res = []
        for part in args:
            for x in part:
                res.append(x)
        return res
