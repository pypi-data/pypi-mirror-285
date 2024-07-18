# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import functools
import json
import os
import platform
import re
import subprocess
import sys
import typing as tp

import requests

from ._logging import logger
from ._proto_namespace import _ProtoNamespace
from ._yaml import yaml  # type: ignore

__all__ = [
    "LazyVersionStr",
    "EnvironmentVariables",
    "canoncial_arch",
    "canonical_machine",
]


class LazyVersionStr:
    def __str__(self) -> str:
        # pylint: disable=import-outside-toplevel,cyclic-import
        import adaux

        return adaux.__version__


@dc.dataclass
class ApiRequestCommunicator:
    base_url: str = dc.field(init=False)
    headers: tp.Dict[str, str] = dc.field(init=False)

    def url(self, *args: str) -> str:
        root = (self.base_url,)
        return "/".join(map(str, root + args))

    def api(self, *args: tp.Any) -> str:
        return self.url("api", "v4", *args)

    def api_request(self, *args: tp.Any, mode: str = "get", **kwgs: tp.Any) -> tp.Any:
        url = self.api(*args)
        if mode == "get":
            for key in kwgs:
                if key not in ["params"]:
                    raise RuntimeError("only params is allowed as kwgs")
            return self.get_request(url, **kwgs)
        if mode == "put":
            return self.put_request(url, json=kwgs)
        if mode == "post":
            return self.post_request(url, json=kwgs)
        if mode == "delete":
            return self.delete_request(url)

        raise NotImplementedError(mode)

    def graphql(self, *args: tp.Any) -> str:
        # https://gitlab.com/-/graphql-explorer
        return self.url("api", "graphql", *args)

    def graphql_request(
        self, mode: str = "get", **kwgs: tp.Any
    ) -> tp.Dict[str, tp.Any]:
        url = self.graphql()
        if mode == "get":
            return self.get_request(url, json=kwgs)
        raise NotImplementedError(mode)

    def get_request(self, url: str, **kwgs: tp.Any) -> tp.Dict[str, tp.Any]:
        req = requests.get(url, headers=self.headers, timeout=10, **kwgs)
        if req.status_code != 200:
            raise RuntimeError(f"{req} {req.text}")
        return json.loads(req.text)  # type: ignore

    def put_request(self, url: str, **kwgs: tp.Any) -> tp.Dict[str, tp.Any]:
        req = requests.put(url, headers=self.headers, timeout=10, **kwgs)
        self.assert_with_debug(req, 200)
        return json.loads(req.text)  # type: ignore

    def post_request(self, url: str, **kwgs: tp.Any) -> tp.Dict[str, tp.Any]:
        req = requests.post(url, headers=self.headers, timeout=10, **kwgs)
        self.assert_with_debug(req, 201)
        return json.loads(req.text)  # type: ignore

    def delete_request(self, url: str, **kwgs: tp.Any) -> tp.Dict[str, tp.Any]:
        req = requests.delete(url, headers=self.headers, timeout=10, **kwgs)
        self.assert_with_debug(req, 204)
        return {}

    @classmethod
    def assert_with_debug(cls, req: tp.Any, code: int) -> None:
        if req.status_code != code:
            print(req, req.text)
            assert req.status_code == code


def subprocess_run(
    *args: tp.Any, **kwgs: tp.Any
) -> "subprocess.CompletedProcess[bytes]":
    sys.stdout.flush()
    try:
        # pylint: disable=subprocess-run-check
        return subprocess.run(*args, **kwgs)
    except subprocess.CalledProcessError as err:
        if err.stdout:
            print("========>> stdout")
            print(err.stdout.decode("utf-8"))
        if err.stderr:
            print("========>> stderr")
            print(err.stderr.decode("utf-8"))
        raise


@dc.dataclass(frozen=True)
class EnvironmentVariables:
    aux: _ProtoNamespace
    regex_release: str = r"^(?:v)?(\d+)\.(\d+)\.(\d+)$"
    regex_version: str = r"(?:v)?(\d+)\.(\d+)\.(\d+)"

    def apply_format(self, val: str) -> str:
        if "{incr}" in val:
            val = val.replace("{incr}", "{{incr}}")
        res = val.format_map(self)
        if "{incr}" in val:
            res = self.auto_incr_process(res)
        return res

    @functools.cached_property
    def release_note(self) -> str:
        release_notes = self.aux.python_project.release_notes
        version = self.aux.python_project.version
        res: str = release_notes[version]
        return res

    @functools.cached_property
    def version(self) -> str:
        res: str = self.aux.python_project.version
        return res

    @functools.cached_property
    def branch(self) -> str:
        res: str = self.aux.gitlab.current_branch
        return res

    @functools.cached_property
    def ci_adaux_image(self) -> str:
        res: str = self.aux.versions.ci_adaux_image
        return res

    @functools.cached_property
    def arch(self) -> str:
        return canoncial_arch()

    @functools.cached_property
    def machine(self) -> str:
        return canonical_machine()

    @functools.cached_property
    def machine_overwrite_postfix(self) -> str:
        res = os.environ.get("machine_overwrite", "")
        if res:
            return f"-{res}"
        return ""

    @functools.cached_property
    def commit_tag(self) -> str:
        res = os.environ.get("CI_COMMIT_TAG", "")
        if res:
            return res
        reason = "empty" if "CI_COMMIT_TAG" in os.environ else "inexistent"
        raise ValueError(f"commit_tag is {reason}")

    @functools.cached_property
    def _remote_version_tags(self) -> tp.List[str]:
        out = subprocess_run(
            ["git", "ls-remote", "-q", "--tags"], check=True, capture_output=True
        )

        res = list(re.findall(r"tags/(.+)\n", out.stdout.decode()))
        return self._version_sorted(res)

    def _version_sorted(self, tags: tp.List[str]) -> tp.List[str]:
        res = []
        for tag in tags:
            match = re.match(self.regex_version, tag)
            if match:
                major, minor, patch = match.groups()
                res.append((int(major), int(minor), int(patch), tag))
            else:
                res.append((0, 0, 0, tag))
        res = sorted(res)
        return [x[-1] for x in res]

    @functools.cached_property
    def last_release(self) -> str:
        for tag in reversed(self._remote_version_tags):
            match = re.match(self.regex_release, tag)
            if match:
                return tag
        return "0.0.0"

    def auto_incr_process(self, tag: str) -> str:
        pattern = tag.replace("{incr}", r"(\d+)")
        candidates = []
        for candidate in reversed(self._remote_version_tags):
            match = re.match(f"^{pattern}$", candidate)
            if match:
                (incr,) = match.groups()
                candidates.append((int(incr), candidate))

        if candidates:
            incr, candidate = list(sorted(candidates))[-1]
            incr_val = incr + 1
        else:
            incr_val = 1
        return tag.format(incr=incr_val)

    @functools.cached_property
    def autoincr(self) -> str:
        tags_used = self._remote_version_tags
        for tag in tags_used:
            logger.info("tag %s available", tag)
        for tag in reversed(tags_used):
            # get the first tag that matches the format
            regex = self.regex_version
            match = re.match(regex, tag)

            if match:
                major, minor, patch = match.groups()
                return f"{major}.{minor}.{int(patch)+1}"

        raise ValueError(f"no tag adheres to {regex}")

    def __getitem__(self, key: str) -> str:
        if "|" in key:
            *keys, fallback = key.split("|")
        else:
            keys = [key]
            fallback = None

        for skey in keys:
            res = ""
            try:
                res = getattr(self, skey)
                assert isinstance(res, str)
            except AttributeError:
                pass
            if skey in os.environ:
                res = os.environ[skey]
            if res:
                return res

        if fallback:
            return fallback
        raise AttributeError(key)


def repr_env_var(
    representer: tp.Any, env_var: tp.Any  # pylint: disable=unused-argument
) -> tp.Any:
    return representer.represent_str("n/a")


yaml.representer.add_representer(EnvironmentVariables, repr_env_var)


def canoncial_arch() -> str:
    arch = platform.machine()
    remap = {
        "aarch64": "arm64",
        "x86_64": "amd64",
    }
    arch = remap.get(arch, arch)
    valid_archs = ["arm64", "amd64"]
    if arch not in valid_archs:
        raise RuntimeError(f"{arch} is not in valid {valid_archs}")
    return arch


def canonical_machine() -> str:
    """
    returns the machine information which can be
    overwritten with an environment variable.
    """
    machine = canoncial_arch()
    return os.environ.get("machine_overwrite", machine)
