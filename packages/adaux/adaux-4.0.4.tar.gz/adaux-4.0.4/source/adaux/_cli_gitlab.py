# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import os
import time

from ._cli import adaux
from ._cli import click
from ._cli import convert_runtime_to_click_error


@adaux.group()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-t",
    "--token",
    prompt=os.environ.get("GITLAB_API_TOKEN", "") == "",
    help="Gitlab Access Token with API Scope.",
    default="env:GITLAB_API_TOKEN",
)
def gitlab(ctx: click.Context, token: str) -> None:
    ctx.obj.token = _get_token_from_env(token)


@gitlab.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
def init(ctx: click.Context) -> None:
    r"""
    Sets various settings on the remote gitlab repositroy.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.gitlab(ctx.obj.token)


@gitlab.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-w",
    "--watch",
    default=False,
    is_flag=True,
    help="Check the pipeline status all 30 seconds.",
)
@click.option(
    "-a",
    "--show-success",
    is_flag=True,
    default=False,
    help="Show successful jobs.",
)
def pipeline(ctx: click.Context, watch: bool, show_success: bool) -> None:
    r"""
    Shows the most recend pipeline on the cli.
    """
    with convert_runtime_to_click_error(ctx):
        while True:
            done, _ = ctx.obj.pipeline(ctx.obj.token, show_success)
            if done or not watch:
                break
            time.sleep(30)


@gitlab.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-w",
    "--watch",
    default=False,
    is_flag=True,
    help="Check the release status all 30 seconds.",
)
@click.option(
    "-p",
    "--pipeline-check",
    default=False,
    is_flag=True,
    help="Wait for successful pipeline status before executing release.",
)
@click.option(
    "-r",
    "--rerelease",
    default=False,
    is_flag=True,
    help="Allow the MR to have the same name as past closed MR.",
)
def release(  # pylint: disable=too-many-arguments
    ctx: click.Context, watch: bool, pipeline_check: bool, rerelease: bool
) -> None:
    r"""
    Create and display release merge request.
    """
    with convert_runtime_to_click_error(ctx):
        success = not pipeline_check
        if pipeline_check:
            while True:
                done, success = ctx.obj.pipeline(ctx.obj.token, show_success=False)
                if done or not watch:
                    break
                time.sleep(30)

        # will be skipped if pipeline is checked and failed
        while success:
            done, _ = ctx.obj.release(ctx.obj.token, rerelease)
            if done or not watch:
                break
            time.sleep(30)


@gitlab.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.argument("mr_message", nargs=-1)
def mr(ctx: click.Context, mr_message: str) -> None:
    """
    Create a merge request from the current branch to the default branch.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.merge_request(ctx.obj.token, " ".join(mr_message))


def _get_token_from_env(token: str) -> str:
    default = os.environ.get("GITLAB_API_TOKEN", "")
    if default == "":
        if token == "env:GITLAB_API_TOKEN":
            raise click.UsageError("GITLAB_API_TOKEN is not set!")
        click.secho(
            f"if you want to avoid re-entering, run: ' export GITLAB_API_TOKEN={token}'",
            fg="yellow",
        )

    if token == "env:GITLAB_API_TOKEN":
        token = default
    return token
