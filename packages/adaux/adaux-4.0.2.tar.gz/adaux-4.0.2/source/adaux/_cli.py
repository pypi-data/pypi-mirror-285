# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import contextlib
import os
import sys
import typing as tp
from pathlib import Path

import click
from click_help_colors import HelpColorsGroup

from ._cli_mixin import CliMixin
from ._cli_mixin import LazyVersionStr
from ._components import AllComponents
from ._logging import logger
from ._logging import logging

__all__ = ["adaux", "hello"]


def hello(bla: str, param: tp.Optional[click.Parameter] = None) -> str:
    r"""
    Hello:

    .. include:: example.rst
    """
    print(param)
    return bla


class _ClickPrintMixin:
    def _print(self, msg: str, **kwgs: tp.Dict[str, tp.Any]) -> None:
        if self.verbose:  # type: ignore
            click.secho(msg, **kwgs)  # type: ignore

    def _prompt(  # pylint: disable=too-many-arguments
        self,
        msg: str,
        fg: tp.Optional[str] = None,
        bg: tp.Optional[str] = None,
        bold: bool = False,
        prompt_suffix: str = ": ",
        **kwgs: tp.Any,
    ) -> str:
        return click.prompt(  # type: ignore
            click.style(msg + prompt_suffix, fg=fg, bg=bg, bold=bold),
            prompt_suffix="",
            type=str,
            **kwgs,
        )


@click.group(
    cls=HelpColorsGroup, help_headers_color="yellow", help_options_color="green"
)
@click.version_option(version=LazyVersionStr())  # type: ignore
@click.pass_context
@click.option("--root", "-c", type=Path, help="Location of the auxilium root.")
@click.option(
    "--bake-before",
    "-b",
    is_flag=True,
    default=False,
    help="Bake before executing the command.",
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    default=False,
    help="Suppress any output on success.",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    default=False,
    help="Increasing log level (INFO/DEBUG)",
)
@click.option(
    "--show-stacktrace",
    "-e",
    is_flag=True,
    default=False,
    help="Show the python stacktrace on error.",
)
@click.option(
    "-h",
    "--here",
    is_flag=True,
    default=False,
    help="Disable fuzzy finder.",
)
@click.option(
    "-n",
    "--no-greeting",
    is_flag=True,
    default=False,
    help="Do not show adaux version.",
)
def adaux(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    root: tp.Optional[Path],
    bake_before: bool,
    silent: bool,
    verbose: int,
    show_stacktrace: bool,
    here: bool,
    no_greeting: bool,
) -> None:
    if verbose:
        if verbose == 1:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.INFO)
    ctx.color = os.environ.get("NO_COLOR", "") == ""
    cls = AllComponents.compose(CliMixin, _ClickPrintMixin)
    bootstrap = cls(root, silent=True, fuzzy_finder=not here)  # type: ignore
    # the __init__ above made a cwd
    root = bootstrap.target.parent
    with convert_runtime_to_click_error(ctx):
        ctx.obj = bootstrap.type_wo_disabled()(root, silent=silent, show_stacktrace=show_stacktrace, fuzzy_finder=not here, greeting=not no_greeting)  # type: ignore

    if ctx.obj.auxcon_file.exists():
        raise_if_init_and_not_force(ctx)
        if bake_before:
            ctx.invoke(bake)
    else:
        raise_if_not_init(ctx)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-n", "--n-lines", default=3)
@click.argument("filter_words", nargs=-1)
def demo(ctx: click.Context, filter_words: tp.Tuple[str, ...], n_lines: int) -> None:
    r"""
    Print a more complex auxilium file for reference.
    """
    ctx.obj.demo(filter_words, n_lines)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-a",
    "--show-all",
    "--all",
    is_flag=True,
    default=False,
    help="display all extra settings",
)
@click.option("-n", "--n-lines", default=3)
@click.argument("filter_words", nargs=-1)
def show(
    ctx: click.Context, show_all: bool, filter_words: tp.Tuple[str, ...], n_lines: int
) -> None:
    r"""
    Read and print auxilium file in yml syntax.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.show(show_all, filter_words, n_lines)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-f", "--force", is_flag=True, default=False)
@click.option(
    "-n", "--project-name", prompt=True, default=AllComponents.deduce_project_name()
)
@click.option(
    "-s", "--project-slug", prompt=True, default=AllComponents.deduce_project_slug()
)
@click.option(
    "-p", "--python-version", prompt=True, default=AllComponents.deduce_python_version()
)
@click.option("-a", "--author", prompt=True, default=AllComponents.deduce_user())
@click.option(
    "-d",
    "--disable",
    multiple=True,
    help="Disable parts of adaux (default select all).",
)
@click.option(
    "-e", "--enable", multiple=True, help="Enable parts of adaux (default select none)."
)
@click.option(
    "--no-source",
    is_flag=True,
    default=False,
    help="Do not generate soruce files if inexistent",
)
def init(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    project_name: str,
    project_slug: str,
    python_version: str,
    author: str,
    force: bool,
    disable: tp.Tuple[str, ...],
    enable: tp.Tuple[str, ...],
    no_source: bool,
) -> None:
    r"""
    Initialize a new auxilium.aux.
    """
    if enable and "pythonproject" not in enable:
        no_source = True
    elif disable and "pythonproject" in disable:
        no_source = True

    with convert_runtime_to_click_error(ctx):
        ctx.obj.init(
            project_name,
            project_slug,
            python_version,
            author,
            force=force,
            disable=disable,
            enable=enable,
            source=not no_source,
        )


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("--bake_after", "-b", is_flag=True)
def sync(ctx: click.Context, bake_after: bool) -> None:
    r"""
    Synchronizes local auxilium file with potentially newer template.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.sync()

    if bake_after:
        ctx.obj.bake()


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("--bake_after", "-b", is_flag=True)
def migrate(ctx: click.Context, bake_after: bool) -> None:
    r"""
    Migrates local auxilium file to newer format.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.migrate()

    if bake_after:
        ctx.obj.bake()


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
def bake(ctx: click.Context) -> None:  # pylint: disable=too-many-statements
    """
    Renders various files based on an auxilium file. Will overwrite without asking.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.bake()


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.argument("auxcon_file")
def pre_commit_bake(ctx: click.Context, auxcon_file: str) -> None:
    assert "auxilium." in auxcon_file
    ctx.obj.bake()


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-M",
    "--major",
    is_flag=True,
    default=False,
    help="major tick",
)
@click.option(
    "-m",
    "--minor",
    is_flag=True,
    default=False,
    help="minor tick",
)
@click.option(
    "-c",
    "--commit",
    is_flag=True,
    default=False,
    help="commit with release message",
)
@click.argument("release_message", nargs=-1)
def tick(
    ctx: click.Context, release_message: str, major: bool, minor: bool, commit: bool
) -> None:
    r"""
    Tick the version and add the release note.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.tick(" ".join(release_message), major, minor, commit)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-f", "--force", is_flag=True, default=False)
@click.argument("src", type=click.Path(exists=True), default=Path("auxilium.cfg"))
@click.argument("dest", type=Path, default=Path("auxilium.yml"))
def convert(ctx: click.Context, src: Path, dest: Path, force: bool) -> None:
    r"""
    Convert auxilium file into different format, e.g. cfg -> yml.
    """
    src = Path(src)
    with convert_runtime_to_click_error(ctx):
        ctx.obj.convert(src, dest, force)


def fwd_all_inputs(fct: tp.Any) -> tp.Any:
    return adaux.command(context_settings={"ignore_unknown_options": True})(
        click.pass_context(click.argument("args", nargs=-1)(fct))
    )


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.argument("trigger_str", nargs=1)
@click.option("-d", "--dry", is_flag=True, default=False)
@click.option("-j", "--job", default=None)
def ci(
    ctx: click.Context, trigger_str: tp.List[str], dry: bool, job: tp.Optional[str]
) -> None:
    """
    Allows running the CI locally.
    """
    with convert_runtime_to_click_error(ctx):
        return_code = ctx.obj.ci(trigger_str, dry=dry, job=job)
    ctx.exit(return_code)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-v", "--open_html", is_flag=True, default=False)
def cov(ctx: click.Context, open_html: bool) -> None:
    """
    Creates the coverage html report.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.cov(open_html)


@fwd_all_inputs
def dcp(ctx: click.Context, args: tp.List[str]) -> None:
    """
    Shortcut for docker compose with corresponding compose file.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.dcp(*args)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.argument("payload_names", nargs=-1)
@click.option(
    "-f", "--force", is_flag=True, default=False, help="runs payload even if up to date"
)
@click.option(
    "-d",
    "--dry",
    is_flag=True,
    default=False,
    help="show what payloads would run, without running them",
)
@click.option(
    "-l", "--show-all", is_flag=True, default=False, help="show all available payloads"
)
def run(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    payload_names: tp.Tuple[str, ...],
    force: bool,
    dry: bool,
    show_all: bool,
) -> None:
    """
    Run a specified payload.
    """
    with convert_runtime_to_click_error(ctx):
        if show_all:
            if payload_names or force or dry:
                raise RuntimeError(
                    "-l needs to be used without other arguments/options"
                )
            payload_names = ("$ls",)

        ctx.obj.run(*payload_names, force=force, dry=dry)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option(
    "-v",
    "--with-detail",
    is_flag=True,
    default=False,
    help="add the parameters to the graph plot",
)
@click.option(
    "-d",
    "--with-dependency",
    is_flag=True,
    default=False,
    help="add the dependency payloads to the graph plot",
)
def graph(  # pylint: disable=too-many-arguments
    ctx: click.Context,
    with_detail: bool,
    with_dependency: bool,
) -> None:
    """
    Plot the payload dependency graph.
    Requires plantuml to be installed as CLI.
    """
    ctx.obj.graph(with_detail, with_dependency)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-h", "--open-html", is_flag=True, default=False)
def docs(ctx: click.Context, open_html: bool) -> None:
    """
    Creates the docs.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.docs(open_html)


@fwd_all_inputs
def mp(ctx: click.Context, args: tp.List[str]) -> None:
    """
    Shows the first lines of the mypy pre-commit hook.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.mp(*args)


@fwd_all_inputs
def pipi(ctx: click.Context, args: tp.List[str]) -> None:
    """
    Runs pip install with editable=strict option.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.pipi(*args)


@fwd_all_inputs
def pl(ctx: click.Context, args: tp.List[str]) -> None:
    """
    Shows the first lines of the pylint pre-commit hook.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.pl(*args)


@fwd_all_inputs
def pra(ctx: click.Context, args: tp.List[str]) -> None:
    """
    Runs all pre-commit hooks, or a specific one if supplied.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.pra(*args)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-z", "--zipped", is_flag=True, default=False)
def sdist(ctx: click.Context, zipped: bool) -> None:
    """
    Builds the release package.
    """
    with convert_runtime_to_click_error(ctx):
        ctx.obj.sdist(zipped)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-c", "--close", default=None)
@click.option("-i", "--gitignore", is_flag=True, default=False)
@click.argument("args", nargs=-1)
def todo(
    ctx: click.Context,
    args: tp.List[str],
    close: tp.Optional[str] = None,
    gitignore: bool = False,
) -> None:
    """
    Read and write todos.
    """
    with convert_runtime_to_click_error(ctx):
        new = " ".join(args) if args else None
        ctx.obj.todo_and_note("todo", new, close, gitignore)


@adaux.command()  # type: ignore[unused-ignore,misc]
@click.pass_context
@click.option("-c", "--close", default=None)
@click.option("-i", "--gitignore", is_flag=True, default=False)
@click.argument("args", nargs=-1)
def note(
    ctx: click.Context,
    args: tp.List[str],
    close: tp.Optional[str] = None,
    gitignore: bool = False,
) -> None:
    """
    Read and write notes.
    """
    with convert_runtime_to_click_error(ctx):
        new = " ".join(args) if args else None
        ctx.obj.todo_and_note("note", new, close, gitignore)


@contextlib.contextmanager
def convert_runtime_to_click_error(ctx: click.Context) -> tp.Iterator[None]:
    if ctx.obj is not None and ctx.obj.show_stacktrace:
        logger.info("showing full stack trace")
        yield
    else:
        try:
            yield
        except RuntimeError as err:
            raise click.UsageError(err.args[0])


def raise_if_not_init(ctx: click.Context) -> None:
    if ctx.invoked_subcommand not in ["init", "demo"]:
        raise click.UsageError(
            f"{ctx.obj.auxcon_file} does not exists! use 'adaux init' to create one."
        )


def raise_if_init_and_not_force(ctx: click.Context) -> None:
    if ctx.invoked_subcommand in ["init"]:
        if all(x not in sys.argv for x in ["-f", "--force"]):
            raise click.UsageError(
                f"{ctx.obj.auxcon_file} already exists, Use 'adaux sync' or -f to overwrite."
            )
