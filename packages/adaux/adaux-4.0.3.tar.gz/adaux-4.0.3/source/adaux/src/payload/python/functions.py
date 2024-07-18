# pylint: disable=relative-beyond-top-level
import os
import typing as tp

import requests

from ...._components._payload._docker_executors import subprocess_run
from ...._components._payload._docker_executors import tag_image
from ...._components._payload._docker_executors import upload_to_remote
from ...._proto_namespace import _ProtoNamespace


def check_release_notes(aux: _ProtoNamespace) -> None:
    release_notes = aux.python_project.release_notes
    version = aux.python_project.version
    # check that version has a note
    if version not in release_notes:
        raise RuntimeError(f"version {version} is not in release notes, please add!")
    # check that version was not already released
    if version in aux.env_var._remote_version_tags:  # pylint: disable=protected-access
        raise RuntimeError(
            f"version {version} was already released and cannot be released again!"
        )

    print(f"version {version} has description '{release_notes[version]}'")


def env_variables(auxh: tp.Any, **kwgs: str) -> None:
    for key, val in kwgs.items():
        val = auxh.env_var.apply_format(val)
        # this is acutally persistent, as we run in the
        # same python process as the rest of adaux.
        # (would not be possible with subshells)
        os.environ[key] = val
        print(f"{key}={val}")


def trigger(
    auxh: tp.Any,
    trigger_url: str,
    ref: str,
    trigger_token: str = "{TRIGGER_TOKEN}",
    blocking: bool = False,
    **kwgs: tp.Any,
) -> None:
    if blocking:
        raise NotImplementedError("blocking mode is not implemented yet")

    trigger_url = auxh.env_var.apply_format(trigger_url)
    ref = auxh.env_var.apply_format(ref)
    trigger_token = auxh.env_var.apply_format(trigger_token)
    data = {"ref": ref, "token": trigger_token}
    for key, val in kwgs.items():
        data[f"variables[{key}]"] = val

    response = requests.post(trigger_url, data=data, timeout=20)

    if response.status_code in [200, 201]:
        print(response.json()["web_url"])
    else:
        raise RuntimeError(
            f"""Failed to trigger pipeline.
Status code: {response.status_code}
Response: {response.text}"""
        )


def tag(
    auxh: _ProtoNamespace,
    deps: tp.Any,
    tags: tp.Union[str, tp.Sequence[str]],  # pylint: disable=redefined-outer-name
) -> None:
    if isinstance(tags, str):
        tags = [tags]

    last_local_tag = ""
    for dep in deps:
        for tag_ in tags:
            tag_ = auxh.env_var.apply_format(tag_)
            local_tag, release_tag = dep.executor.tag_and_upload(tag_)
            if last_local_tag != local_tag:
                last_local_tag = local_tag
                msg = "uploaded" if dep.executor.remote_exists() else "  tagged"
                print(msg, local_tag)
            print("   -> to", release_tag)


def gittag(
    auxh: _ProtoNamespace,
    deps: tp.Any,
    tags: tp.Union[str, tp.Sequence[str], None] = None,
) -> None:
    if tags is None:
        # get it from the deps
        assert len(deps) == 1
        dep = deps[0]
        tags = dep.param["tags"]

    if isinstance(tags, str):
        tags = [tags]

    for tag_ in tags:
        tag_ = auxh.env_var.apply_format(tag_)
        subprocess_run(["git", "tag", "-f", tag_])
        url = os.environ["CI_REPOSITORY_URL"]
        protocol, rest = url.split("//", 1)
        _, rest = rest.split("@", 1)
        url = f"{protocol}//__token__:{os.environ['GITLAB_WRITE_REPOSITORY']}@{rest}"
        subprocess_run(["git", "push", url, tag_], check=True)


def img_dockerhub(
    auxh: _ProtoNamespace,
    deps: tp.Any,
    release_tag: str,
) -> None:
    if len(deps) != 1:
        raise RuntimeError(
            f"img-dockerhub job for {release_tag} should have exactly 1 dependency, not {len(deps)}!"
        )
    release_tag = auxh.env_var.apply_format(release_tag)
    local_tag = deps[0].executor.pull_if_not_existent()
    tag_image(local_tag, release_tag)
    subprocess_run(
        [
            "docker",
            "login",
            "-u",
            os.environ["DOCKERHUB_USERNAME"],
            "-p",
            os.environ["DOCKERHUB_PASSWORD"],
            "docker.io",
        ]
    )
    upload_to_remote(local_tag, release_tag)
    subprocess_run(["docker", "logout", "docker.io"])
    print("uploaded", local_tag)
    print("   -> to", release_tag)
