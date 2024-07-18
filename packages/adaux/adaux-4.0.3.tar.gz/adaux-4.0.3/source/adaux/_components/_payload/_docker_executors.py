# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import functools
import hashlib
import logging
import os
import re
import shutil
import subprocess
import typing as tp
from pathlib import Path

import requests

from ..._logging import logger
from ..._util import canonical_machine
from ..._util import subprocess_run


@dc.dataclass(frozen=True)
class DockerShared:
    slug: str
    parents: tp.Tuple["DockerShared", ...] = tuple()
    images: tp.List[str] = dc.field(default_factory=list)

    # Run local registry:
    # docker run -d -p 5000:5000 --name registry registry:2
    # docker container stop registry && docker container rm -v registry
    # export CI_REGISTRY=localhost:5000
    @property
    def registry_host(self) -> str:
        if not self.remote_exists():
            raise RuntimeError(
                "Your run needs a remote registry.\n"
                "In case you have not already, you can launch a local registry with\n"
                "  docker run -d -p 5000:5000 --name registry registry:2\n"
                "and run\n"
                "  export CI_REGISTRY=localhost:5000"
            )
        return os.environ["CI_REGISTRY"]

    def remote_exists(self) -> bool:
        return "CI_REGISTRY" in os.environ

    @property
    def build_deps(self) -> tp.Iterator["DockerBuildMixin"]:
        for parent in self.parents:
            if isinstance(parent, DockerBuildMixin):
                yield parent

    def script(self, force: bool = False) -> None:  # pylint: disable=unused-argument
        # get dependencies
        for job in self.build_deps:
            local_tag = job.local_tag
            # if not exists_locally(local_tag):
            #     if self.remote_exists():
            #         remote_tag = job.remote_tag
            #         if not exists_locally(remote_tag):
            #             cmd = ["docker", "pull", remote_tag]
            #             subprocess_run(cmd, check=True, capture_output=True)
            #             logger.info("pulled '%s'", remote_tag)

            #         tag_image(remote_tag, job.local_tag)
            if self.remote_exists() and local_tag:
                remote_tag = job.remote_tag
                cmd = ["docker", "pull", remote_tag]
                subprocess_run(cmd, check=True, capture_output=True)
                logger.info("pulled '%s'", remote_tag)
                tag_image(remote_tag, job.local_tag)

            # I tag every time as it allows different dependencies to
            # map to the same service name without raising issues
            # (useful for local development)
            tag_image(job.local_tag, job.use_tag)

        # download other images which are not a direct dependency (cross-repo)
        for image_tag in self.images:
            if self.remote_exists():
                image_remote_tag = (
                    f"{self.registry_host}/{self._remove_namespace_local(image_tag)}"
                )
                check_and_pull_if_not_existent(image_remote_tag, image_tag)
            else:
                tag = self._remove_namespace_local(image_tag)
                tag_image(tag, image_tag)

    def _get_tag_parts(self) -> tp.Iterator[tp.Union[bytes, str]]:
        for job in self.build_deps:
            yield job.tag

    def _remove_namespace_local(self, image: str) -> str:
        if not self.remote_exists() or self.registry_host.startswith("localhost"):
            return image.rsplit("/", 1)[1]
        return image


@dc.dataclass(frozen=True)
class _DockerBuildMixinState:
    service: str
    image_name: str


@dc.dataclass(frozen=True)
class DockerBuildMixin(DockerShared, _DockerBuildMixinState):
    files: tp.List[str] = dc.field(default_factory=list)
    always_build: bool = False

    def script(self, force: bool = False) -> None:
        # this tag need to be evaluated before super script, otherwise base-matching hasnt happened.
        local_tag = self.local_tag  # triggeres matching
        super().script(force=force)
        if self.remote_exists():
            remote_tag = self.remote_tag
            check_and_pull_if_not_existent(remote_tag, local_tag, self.service)

        if not exists_locally(self.local_tag) or self.always_build or force:
            cmd = self._get_build_cmd()
            logger.info(" ".join(cmd))
            subprocess_run(cmd, check=True)

        # upload
        tag_image(self.use_tag, local_tag)
        if self.remote_exists():
            upload_to_remote(local_tag, remote_tag)
            logger.info("uploaded %s to %s", local_tag, remote_tag)

    def _get_build_cmd(self) -> tp.List[str]:
        cmd = [
            "docker",
            "--log-level",
            "ERROR",
            "compose",
            "-p",
            self.slug,
            "-f",
            "devops/docker/compose.yml",
            "build",
            self.service,
        ]
        if not self.remote_exists():
            cmd.append("--pull=false")
        return cmd

    @functools.cached_property
    def tag(self) -> str:
        hasher = hashlib.md5()

        for part in self._get_tag_parts():
            if isinstance(part, str):
                hasher.update(part.encode("utf8"))
            else:
                hasher.update(part)

        tag = hasher.hexdigest()[:16]
        prefix = "loc"
        if self.remote_exists():
            prefix = "aux"
        return f"{prefix}-{canonical_machine()}-{tag}"

    def _get_tag_parts(self) -> tp.Iterator[tp.Union[bytes, str]]:
        yield from super()._get_tag_parts()
        for file in self.files:
            with open(file, "rb") as f:
                yield f.read()

        # we assume the image tag is not moving (i.e. no latest)
        yield from self.images

    @functools.cached_property
    def remote_tag(self) -> str:
        return f"{self.registry_host}/{self.local_tag}"

    @functools.cached_property
    def local_tag(self) -> str:
        image = self.get_image_name()
        return f"{image}:{self.tag}"

    @functools.cached_property
    def use_tag(self) -> str:
        return self.image_name.lower()

    def get_image_name(self) -> str:
        if "CI_PROJECT_NAMESPACE" in os.environ:
            group = os.environ["CI_PROJECT_NAMESPACE"]
            repo = os.environ["CI_PROJECT_NAME"]
            return f"{group}/{repo}/{self.use_tag}".lower()
        return f"{self.use_tag}"

    def _docker_registry_header_and_url(
        self, image: str
    ) -> tp.Tuple[tp.Dict[str, str], str]:
        protocol = "http"
        headers = {}
        if not self.registry_host.startswith("localhost"):
            protocol = "https"
            headers["Authorization"] = f"Bearer {registry_api_token(image)}"

        # https://gitlab.com/gitlab-org/gitlab/-/issues/19470
        url = f"{protocol}://{self.registry_host}/v2"
        return headers, url

    def is_up_to_date(self) -> bool:
        if self.remote_exists():
            return self.exists_remotely()
        return exists_locally(self.local_tag)

    def exists_remotely(self) -> bool:
        headers, api_url = self._docker_registry_header_and_url(self.get_image_name())
        try:
            req = requests.get(
                api_url + f"/{self.get_image_name()}/tags/list",
                headers=headers,
                timeout=10,
            )
        except requests.ConnectionError as err:
            raise RuntimeError(
                f"are you sure the registry {self.registry_host} is reachable?\n"
                "use: docker run -d -p 5000:5000 --name registry registry:2\n"
                "or: unset CI_REGISTRY"
            ) from err

        if req.status_code != 200:
            return False
        tags = req.json()["tags"] or []
        return self.tag in tags

    def tag_and_upload(self, tag: str) -> tp.Tuple[str, str]:
        local_tag = self.local_tag
        if self.remote_exists():
            remote_tag = self.remote_tag
            assert isinstance(self, DockerBuild)
            check_and_pull_if_not_existent(remote_tag, local_tag)
            release_tag = remote_tag.replace(self.tag, tag)
            upload_to_remote(local_tag, release_tag)
        else:
            logger.warning(
                "no remote exists (export CI_REGISTRY=localhost:5000), fallback on local tagging"
            )
            release_tag = local_tag.replace(self.tag, tag)
            tag_image(local_tag, release_tag)
        return local_tag, release_tag

    def pull_if_not_existent(self) -> str:
        remote_tag = self.remote_tag
        local_tag = self.local_tag
        assert isinstance(self, DockerBuild)
        check_and_pull_if_not_existent(remote_tag, local_tag)
        return local_tag


@dc.dataclass(frozen=True)
class _DockerBuildBranchMatchMixinState(_DockerBuildMixinState):
    branch_match: tp.List[tp.Tuple[str, str, str, tp.List[str], tp.Optional[str]]]


@dc.dataclass(frozen=True)
class MatchCommonImpl:
    @classmethod
    def _get_git_branch(cls) -> str:
        branch = os.environ.get("CI_COMMIT_BRANCH", "") + os.environ.get(
            "CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", ""
        )
        if not branch:
            # we are running it locally, and try to get it from git
            proc = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                check=False,
                capture_output=True,
            )
            if proc.returncode == 0:
                branch = proc.stdout.decode("utf-8").strip()

        assert branch
        return branch


@dc.dataclass(frozen=True)
class DockerBuildBranchMatchMixin(
    MatchCommonImpl, DockerBuildMixin, _DockerBuildBranchMatchMixinState
):
    def _get_tag_parts(self) -> tp.Iterator[tp.Union[bytes, str]]:
        yield from super()._get_tag_parts()

        branch = self._get_git_branch()

        for pkg, var, url, skip, fallback in self.branch_match:
            if branch in skip:
                logger.info("skipping matching branch '%s' for '%s'", branch, pkg)
                continue
            secret = re.search(r"\$(\w+)@", url).group(1)  # type: ignore
            url = url.replace(f"${secret}", os.environ[secret])
            # figure out if matching branch exists

            try_branches = [(branch, "matching")]
            if fallback:
                try_branches.append((fallback, "fallback"))

            for branch, reason in try_branches:
                exists, sha = self._matching_branch_exist(url, branch)
                if exists:
                    logger.info("found %s branch '%s' for '%s'", reason, branch, pkg)
                    yield sha
                    os.environ[var] = f"{pkg}@git+{url}@{branch}"
                    break

    @classmethod
    def _matching_branch_exist(cls, url: str, branch: str) -> tp.Tuple[bool, str]:
        cmd = f"git ls-remote {url} {branch}".split(" ")
        res = subprocess_run(cmd, check=False, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.decode("utf8"))
        parts = res.stdout.decode("utf8").split()
        if parts:
            sha, refs = parts
            assert branch in refs
            return True, sha
        return False, ""


@dc.dataclass(frozen=True)
class _DockerBuildBaseMatchMixinState(_DockerBuildMixinState):
    base_match: tp.List[tp.Tuple[str, str, tp.List[str], str, str]]


@dc.dataclass(frozen=True)
class DockerBuildBaseMatchMixin(
    MatchCommonImpl, DockerBuildMixin, _DockerBuildBaseMatchMixinState
):
    def _get_tag_parts(self) -> tp.Iterator[tp.Union[bytes, str]]:
        yield from super()._get_tag_parts()
        branch = self._get_git_branch()

        for image_w_ns, var, skip, fallback, default in self.base_match:
            # locally, we do not use the group and repo prefix, hence
            # it needs to be removed
            image = self._remove_namespace_local(image_w_ns)
            if branch in skip:
                logger.info(
                    "skipping matching base '%s' for '%s', using default '%s'",
                    branch,
                    image,
                    default,
                )
                self._fix_environ_and_image(image, var, default)
                yield default
                return

            try_bases = [(fallback, "fallback")]

            for tag, reason in try_bases:
                if not self.remote_exists():
                    self._call_upstream_adaux(image_w_ns, image, tag)

                exists, sha = self._matching_base_exist(image, tag)
                if exists:
                    logger.info("found %s tag '%s' for '%s'", reason, tag, image)
                    self._fix_environ_and_image(image, var, tag)
                    yield sha
                    break
            else:
                logger.info(
                    "no matching base found for '%s', using default '%s'",
                    image,
                    default,
                )
                self._fix_environ_and_image(image, var, default)
                yield tag

    def _fix_environ_and_image(self, image: str, var: str, tag: str) -> None:
        unevaluated = f"{image}:${var}"
        os.environ[var] = tag

        for i, candidate in enumerate(self.images):
            if candidate.endswith(unevaluated):
                self.images[i] = candidate.replace(f"${var}", tag)

    def _matching_base_exist(self, image: str, tag: str) -> tp.Tuple[bool, str]:
        if self.remote_exists():
            headers, api_url = self._docker_registry_header_and_url(image)
            try:
                headers["Accept"] = (
                    "application/vnd.docker.distribution.manifest.v2+json"
                )
                req = requests.get(
                    api_url + f"/{image}/manifests/{tag}", headers=headers, timeout=10
                )
                sha = req.json()["config"]["digest"]
                logger.info("base matched image %s:%s has digest %s", image, tag, sha)
                return True, sha
            except (requests.ConnectionError, KeyError):
                return False, ""
        else:
            res = subprocess_run(
                "docker inspect --format='{{.Id}}'".split(" ") + [f"{image}:{tag}"],
                capture_output=True,
            )
            if res.returncode == 0:
                return True, res.stdout.decode("utf-8")
            return False, ""

    def _call_upstream_adaux(  # pylint: disable=too-many-locals,too-many-branches
        self, image_w_ns: str, image: str, tag: str
    ) -> None:
        _, project, image = image_w_ns.split("/")
        orig_path = Path.cwd()
        slug = image.split("-", 1)[0]
        candidates = [project]
        if "_" in project:
            candidates += [project.replace("_", "-"), project.rsplit("_", 1)[1]]
        if "-" in project:
            candidates += [project.replace("-", "_"), project.rsplit("-", 1)[1]]
        for cand in candidates:
            upstream = orig_path.parent / cand
            if upstream.exists():
                break
        else:
            logger.warning(
                "project %s not found as a sibling directory, checked for %s",
                project,
                candidates,
            )
            return

        verbose = ""
        if logger.getEffectiveLevel() == logging.DEBUG:
            verbose = " -v"
        os.chdir(upstream)
        machine = canonical_machine()
        if tag.endswith(machine):
            tag = tag.rsplit("-", 1)[0]
        with subprocess.Popen(
            f"adaux{verbose} run tag-{tag}".split(" "),
            stdout=subprocess.PIPE,
            text=True,
        ) as process:
            assert process.stdout is not None
            columns, _ = shutil.get_terminal_size((80, 20))
            print(">" * columns)
            for line in iter(process.stdout.readline, ""):
                prefix = f"|{slug}|"
                if line.startswith("|"):
                    if verbose:
                        prefix = "|"
                    else:
                        prefix = ""
                line = prefix + line
                # adjust column wide lines as terminal size is wrong in subcall
                if ">>>>>>>" in line:
                    line = line.split(">", 1)[0]
                    line += ">" * (columns - len(line)) + "\n"
                if "<<<<<<<" in line:
                    line = line.split("<", 1)[0]
                    line += "<" * (columns - len(line)) + "\n"
                print(f"{line}", end="", flush=True)
            print("<" * columns, flush=True)
        os.chdir(orig_path)


@dc.dataclass(frozen=True)
class _DockerRunMixinState:
    services: tp.List[str]


@dc.dataclass(frozen=True)
class DockerRunMixin(DockerShared, _DockerRunMixinState):
    interactive: bool = False
    exec_join: bool = False
    run_ports: tp.List[str] = dc.field(default_factory=list)

    def script(self, force: bool = False) -> None:
        super().script(force=force)
        base_cmd = [
            "docker",
            "--log-level",
            "ERROR",
            "compose",
            "-p",
            self.slug,
            "-f",
            "devops/docker/compose.yml",
        ]
        if self.interactive:
            if len(self.services) > 1:
                raise NotImplementedError(
                    "cannot run more than one service in interactive mode"
                )
            service = self.services[0]
            sub_cmd = ["run", "--rm", "-ti"]
            for port in self.run_ports:
                sub_cmd.append("-p")
                sub_cmd.append(port)

            if self.exec_join:
                res = subprocess_run(
                    [
                        "docker",
                        "ps",
                        "--filter",
                        f"label=com.docker.compose.service={service}",
                        "--format",
                        "{{.ID}}",
                    ],
                    capture_output=True,
                )
                container_id = res.stdout.decode("utf-8").strip()
                logger.info(
                    "using exec instead of run, as container %s=%s exists",
                    service,
                    container_id,
                )
                if container_id:
                    res = subprocess_run(
                        [
                            "docker",
                            "inspect",
                            "--format",
                            "{{.Config.Cmd}}",
                            container_id,
                        ],
                        capture_output=True,
                    )
                    # very simple listification for now
                    orig_cmd = res.stdout.decode("utf-8").strip()[1:-1].split(",")
                    # service instead of container_id bc of compose
                    sub_cmd = ["exec", "-ti", service] + orig_cmd
                else:
                    sub_cmd.append(service)
            else:
                sub_cmd.append(service)
            cmd = base_cmd + sub_cmd
        else:
            cmd = base_cmd + [
                "up",
                "--no-build",
                "--abort-on-container-exit",
            ]
            if len(self.services) <= 1:
                cmd.append("--no-log-prefix")
            cmd += self.services

        subprocess_run(cmd, check=True)


@dc.dataclass(frozen=True)
class DockerBuild(
    DockerBuildBaseMatchMixin,
    DockerBuildBranchMatchMixin,
    _DockerBuildBaseMatchMixinState,
    _DockerBuildBranchMatchMixinState,
):
    pass


@dc.dataclass(frozen=True)
class DockerBuildx(DockerBuild):
    platforms: tp.List[str] = dc.field(default_factory=list)

    def _get_build_cmd(self) -> tp.List[str]:
        cmd = super()._get_build_cmd()
        idx = cmd.index("-p")
        cmd.remove("-p")
        cmd.pop(idx)

        idx = cmd.index("compose")
        cmd[idx] = "buildx"
        cmd.insert(idx + 1, "bake")
        cmd.remove("build")
        cmd.append("--provenance=0")
        if self.remote_exists():
            cmd.append("--push")
        else:
            cmd.append("--set=*.platform=linux/arm64")
            cmd.append("--load")
        return cmd


@dc.dataclass(frozen=True)
class DockerRun(DockerRunMixin, _DockerRunMixinState):
    pass


# try to download for caching (or reuse if already there)
def check_and_pull_if_not_existent(
    remote_tag: str, local_tag: str, service: tp.Optional[str] = None
) -> None:
    cmd = ["docker", "pull", remote_tag]
    res = subprocess_run(cmd, check=False, capture_output=True)
    if res.returncode != 0:
        return

    tag_image(remote_tag, local_tag)
    if service:
        tag_image(remote_tag, service)


def upload_to_remote(
    local_tag: str, remote_tag: str, registry: tp.Optional[str] = None
) -> None:
    tag_image(local_tag, remote_tag)
    cmd = ["docker", "push", remote_tag]
    if registry:
        cmd += [registry]
    subprocess_run(cmd, check=True, capture_output=True)
    logger.info("pushed '%s'", remote_tag)


def tag_image(src_tag: str, dest_tag: str) -> None:
    cmd = ["docker", "image", "tag", src_tag, dest_tag]
    subprocess_run(cmd, check=True, capture_output=True)
    logger.info("tagged '%s' -> '%s'", src_tag, dest_tag)


def exists_locally(local_tag: str) -> bool:
    cmd = ["docker", "image", "inspect", local_tag]
    res = subprocess_run(cmd, check=False, capture_output=True)
    return res.returncode == 0


@functools.lru_cache
def registry_api_token(image: str) -> str:
    # https://www.pimwiddershoven.nl/entry/request-an-api-bearer-token-from-gitlab-jwt-authentication-to-control-your-private-docker-registry
    # curl --user 'user:pw' 'https://gitlab.com/jwt/auth?client_id=docker&offline_token=true&service=container_registry&scope=repository:administratum/auxilium/adaux-pytest-39:pull,push'
    # curl -H 'Authorization: Bearer token' https://gitlab.com:5050/v2/administratum/auxilium/adaux-pytest-39/tags/list
    server = os.environ["CI_SERVER_URL"]
    url = f"{server}/jwt/auth?client_id=docker&offline_token=true&service=container_registry&scope=repository:{image}:pull,push"
    req = requests.get(
        url,
        auth=(os.environ["CI_REGISTRY_USER"], os.environ["CI_JOB_TOKEN"]),
        timeout=10,
    )
    return req.json()["token"]  # type: ignore
