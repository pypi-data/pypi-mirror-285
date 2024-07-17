# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import collections
import io
import os
import shutil
import subprocess
import sys
import typing as tp
from pathlib import Path

from ._components import AllComponents
from ._components import ExtraLevel
from ._components._02_base import BaseComponent
from ._components._03_meta import MetaMixin
from ._components._98_sentinel import SentinelMixin
from ._gitlab import GitlabSetter
from ._logging import logger
from ._proto_namespace import _ProtoNamespace
from ._tick import TickSetter
from ._todo import TodoSetter
from ._util import LazyVersionStr


class CliMixin(  # pylint: disable=too-many-public-methods
    SentinelMixin, MetaMixin, BaseComponent
):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        root: Path,
        silent: bool = False,
        greeting: bool = True,
        show_stacktrace: bool = False,
        fuzzy_finder: bool = True,
    ) -> None:
        super().__init__()
        self.show_stacktrace = show_stacktrace
        self.verbose = not silent
        if root:
            self.target = root / "devops"
        else:
            self.target = Path("devops")

        try:
            self.target = self.target.relative_to(Path.cwd())
        except ValueError:
            pass

        valid_suffix = [".yml", ".yaml", ".cfg"]
        candidates = [
            (self.target.parent / "auxilium").with_suffix(sfx) for sfx in valid_suffix
        ]
        self.auxcon_file = candidates[0]

        if fuzzy_finder:  # via git root
            if not any(cand.exists() for cand in candidates) and root is None:
                resp = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    check=False,
                )
                if resp.returncode == 0:
                    git_root = Path(resp.stdout.decode().strip())
                    self.target = git_root / "devops"
                    candidates = [
                        (git_root / "auxilium").with_suffix(sfx) for sfx in valid_suffix
                    ]

        for cand in candidates:
            if cand.exists():
                self.auxcon_file = cand
                workroot = self.auxcon_file.parent
                logger.debug("cwd changed to %s", workroot)

                pre_cwd_target = self.target.resolve()
                os.chdir(workroot)  # switch to the root dir
                # re-adjust filepaths
                self.target = pre_cwd_target.relative_to(Path.cwd())
                self.auxcon_file = Path(self.auxcon_file.name)
                self.load_auxcon()
                # adaux assumes to be executed from root
                break
        if greeting:
            self._print(f"adaux {LazyVersionStr()} at your service", fg="blue")

    def demo(
        self: "CliMixin", filter_words: tp.Tuple[str, ...] = tuple(), n_lines: int = 3
    ) -> None:
        out = io.StringIO()
        self.save_auxcon_to_stream(out, level=ExtraLevel.DEMODATA)
        self.show_matching(out.getvalue(), filter_words, n_lines)

    def show(
        self: "CliMixin",
        show_all: bool = False,
        filter_words: tp.Tuple[str, ...] = tuple(),
        n_lines: int = 3,
    ) -> None:
        out = io.StringIO()
        self.save_auxcon_to_stream(
            out, level=ExtraLevel.ENRICHED if show_all else ExtraLevel.DEFAULTED
        )
        self.show_matching(out.getvalue(), filter_words, n_lines)

    def show_matching(
        self, output: str, filter_words: tp.Tuple[str, ...] = tuple(), n_lines: int = 3
    ) -> None:
        val = output.split("\n")
        if filter_words:
            keep = {}
            hist: tp.Deque[tp.Tuple[int, str]] = collections.deque(maxlen=n_lines)
            trailing_add = 0
            for i, line in enumerate(val):
                if any(word in line for word in filter_words):
                    keep.update(dict(hist))
                    trailing_add = n_lines + 1
                if trailing_add:
                    trailing_add -= 1
                    keep[i] = line
                hist.append((i, line))

            last_i = -1
            val = []
            longest_line = max(map(len, keep.values()), default=0)
            for i, line in keep.items():
                if last_i not in [i - 1, -1]:
                    val.append("~" * longest_line)
                last_i = i
                val.append(line)

        for line in val:
            kwgs = {}
            if filter_words and any(word in line for word in filter_words):
                kwgs["fg"] = "green"
            self._print(line, **kwgs)

    def init(  # pylint: disable=too-many-arguments
        self: "CliMixin",
        project_name: str,
        project_slug: str,
        python_version: str,
        author: str,
        force: bool = False,
        disable: tp.Tuple[str, ...] = tuple(),
        enable: tp.Tuple[str, ...] = tuple(),
        source: bool = True,
    ) -> None:
        self.auxcon.project = _ProtoNamespace(
            name=project_name,
            slug=project_slug,
            author=author,
        )
        self.auxcon.python_project = _ProtoNamespace(
            minimal_version=python_version,
        )
        self.auxcon.meta = _ProtoNamespace(disable=disable, enable=enable)
        self.target.mkdir(parents=True, exist_ok=True)

        reduced = self.type_wo_disabled()(self.target.parent, greeting=False)  # type: ignore
        reduced.auxcon = self.auxcon
        reduced.save_auxcon_and_print(ExtraLevel.TEMPLATED, force=force)  # type: ignore

        # create source skeleton
        if source and reduced.is_enabled("project"):
            with reduced.extra(level=ExtraLevel.DEFAULTED):  # type: ignore
                reduced.create_source()  # type: ignore

    def save_auxcon_and_print(self, level: ExtraLevel, force: bool = False) -> None:
        dest = self.auxcon_file
        over, fg_col = "", "green"
        if dest.exists():
            if not force:
                raise RuntimeError(f"{dest} exists, use -f or --force to overwrite.")
            over, fg_col = "over", "yellow"

        with self.extra(level=level) as aux:
            self.save_auxcon(aux)

        # pylint: disable=protected-access
        self._print(f"{over}written template to {dest}", fg=fg_col)

    def sync(self: "CliMixin") -> None:
        with self.extra(ExtraLevel.FORMATTED) as aux:
            proj = aux.project
            python_proj = aux.get(
                "python_project", _ProtoNamespace(minimal_version="0.0.0")
            )
        clean: SentinelMixin = self.type_wo_disabled(discard_before="SentinelMixin")()  # type: ignore
        # full holds all possible defaults (in case something got disabled)
        full: SentinelMixin = AllComponents().type_wo_disabled(  # type: ignore
            discard_before="SentinelMixin"
        )()

        for ns in [clean, full]:
            # pylint: disable=no-member
            ns.auxcon.project = _ProtoNamespace(
                name=proj.name,
                slug=proj.slug,
                author=proj.author,
            )
            ns.auxcon.python_project = _ProtoNamespace(
                minimal_version=python_proj.minimal_version,
            )

        with self.extra(ExtraLevel.FORMATTED) as aux, clean.extra(
            ExtraLevel.TEMPLATED
        ), full.extra(ExtraLevel.TEMPLATED_WITH_NEGATIVE):
            self.update_to_template(clean.auxf, full.auxf)
            self.save_auxcon(aux)

    def bake(self: "CliMixin") -> None:
        if not self.auxcon_file.exists():
            raise RuntimeError(f"{self.auxcon_file} does not exists! use 'aux init'")
        super().bake()

    def gitlab(self: "CliMixin", token: str) -> None:
        with self.extra():
            gls = GitlabSetter(self, token)  # type: ignore
            gls.bake()

    def pipeline(
        self: "CliMixin", token: str, show_success: bool
    ) -> tp.Tuple[bool, bool]:
        with self.extra():
            gls = GitlabSetter(self, token)  # type: ignore
            return gls.pipeline(show_success)

    def merge_request(self: "CliMixin", token: str, mr_message: str = "") -> None:
        with self.extra():
            gls = GitlabSetter(self, token, greeting=False)  # type: ignore
            gls.merge_request(mr_message)

    def tick(
        self: "CliMixin",
        release_message: str,
        major: bool = False,
        minor: bool = False,
        commit: bool = False,
    ) -> None:
        if major and minor:
            raise RuntimeError("cannot set major and minor tick at the same time!")
        # empty mode, commit only
        commit_with_release_msg = False
        if len(release_message) == 0 and commit:
            assert minor is False
            assert major is False
            commit_with_release_msg = True
        elif len(release_message) < 16:
            raise RuntimeError("message cannot be shorter than 16 char")
        with self.extra() as aux:
            if commit_with_release_msg:
                release_message = next(iter(aux.python_project.release_notes.values()))
            ticker = TickSetter(self, release_message, major, minor)  # type: ignore
            if not commit_with_release_msg:
                ticker.bake()
            if commit:
                ticker.commit()

    def release(
        self: "CliMixin", token: str, rerelease: bool = False
    ) -> tp.Tuple[bool, bool]:
        with self.extra():
            gls = GitlabSetter(self, token)  # type: ignore
            return gls.release(rerelease)

    def convert(self: "CliMixin", src: Path, dest: Path, force: bool = False) -> None:
        self.auxcon_file = src
        self.load_auxcon()
        self.auxcon_file = dest
        self.save_auxcon_and_print(ExtraLevel.DEFAULTED, force=force)

    def ci(
        self: "CliMixin",
        trigger_str: str,
        dry: bool = False,
        job: tp.Optional[str] = None,
    ) -> int:
        self._raise_if_disabled("ci")
        with self.extra(ExtraLevel.HYDRATED), self.cwd_to_root():
            return self.run_ci(trigger_str, dry=dry, job=job)  # type: ignore

    def cov(self: "CliMixin", open_html: bool = False) -> None:
        self._raise_if_disabled("coverage")
        cov_cache = self.target / "cache" / "coverage"
        datafile = cov_cache / "data_file"
        cov_file = self.target.parent / ".coverage"
        if datafile.exists():
            if cov_file.exists():
                datafile.unlink()
            else:
                datafile.rename(cov_file)

        with self.extra(ExtraLevel.FORMATTED) as aux:
            # pylint: disable=no-member
            cmd = [
                "pytest",
                "--cov",
                f"--cov={aux.project.name}",
                f"--cov-report=html:{cov_cache}",
            ]
            subprocess.run(cmd, check=True)
            cov_file.rename(datafile)

            if open_html:
                cmd = ["open", str(cov_cache / "index.html")]
                subprocess.run(cmd, check=True)

    def dcp(self: "CliMixin", *args: str) -> None:
        self._raise_if_disabled("docker")
        with self.extra() as aux:
            cmd = [
                "docker",
                "compose",
                "-p",
                aux.project.slug,
                "-f",
                str(self.target / "docker" / "compose.yml"),
                *args,
            ]
            subprocess.run(cmd, check=False)

    def run(
        self: "CliMixin", *payload_names: str, force: bool = False, dry: bool = False
    ) -> None:
        self._raise_if_disabled("payload")
        with self.extra(ExtraLevel.HYDRATED), self.cwd_to_root():
            data = self.auxh.payload
            if payload_names == ("$ls",):
                for title, flavor in [
                    ("payloads", "docker_build"),
                    ("with deps", "with_dependency"),
                ]:
                    list_ = list(data.lookup.level(flavor).values())
                    if not list_:
                        continue
                    self._print("=" * len(title))
                    self._print(title)
                    self._print("=" * len(title))
                    for payload in list_:
                        print("-", payload.name)

                return
            try:
                payloads = [data.lookup[x] for x in payload_names]
            except KeyError as err:
                raise RuntimeError(
                    f"payload '{payload_names}' not found! Use 'adaux run -l', or check the {self.auxcon_file.name} file."
                ) from err
            success = self.payload_run(*payloads, force=force, dry=dry)  # type: ignore
            if not success:
                sys.exit(1)

    def graph(
        self: "CliMixin", with_detail: bool = True, with_dependency: bool = True
    ) -> None:
        self._raise_if_disabled("payload")
        with self.extra(ExtraLevel.HYDRATED), self.cwd_to_root():
            self.plot_dependency_graph(with_detail=with_detail, with_dependency=with_dependency)  # type: ignore

    def docs(self: "CliMixin", open_html: bool = False) -> None:
        self._raise_if_disabled("docs")

        docs_cache = self.target / "cache" / "docs"

        with self.extra() as aux:
            # pylint: disable=no-member
            if aux.docs.framework == "sphinx":
                cmd = [
                    "sphinx-apidoc",
                    "-o",
                    aux.docs.root,
                    aux.python_project.module_dir,
                ]
                subprocess.run(cmd, check=True)
                cmd = ["sphinx-build", "-M", "html", aux.docs.root, docs_cache]
                if aux.docs.get("strict", True):
                    cmd.append("-W")
                subprocess.run(cmd, check=True)
                cmd = [
                    "python",
                    self.target / "docs" / "postprocess_html.py",
                    (docs_cache / "html" / aux.python_project.second_name).with_suffix(
                        ".html"
                    ),
                ]
                subprocess.run(cmd, check=True)
            elif aux.docs.framework == "mkdocs":
                cmd = ["mkdocs", "build", "-f", f"{aux.docs.root}/mkdocs.yml"]
                subprocess.run(cmd, check=True)
            else:
                raise NotImplementedError(aux.docs.framework)

        if open_html:
            cmd = ["open", docs_cache / "html" / "index.html"]
            subprocess.run(cmd, check=True)

    def mp(self: "CliMixin", *args: str) -> None:
        self._raise_if_disabled("mypy")
        cmd = ["git", "add", "-u"]
        subprocess.run(cmd, check=True)
        cmd = [
            "pre-commit",
            "run",
            f"--config={self.target/'pre-commit'/'config.yaml'}",
            "mypy",
            *args,
        ]
        self._run_with_line_limit(cmd)

    def pipi(self: "CliMixin", *args: str) -> None:
        self._raise_if_disabled("pip")
        optional = ""
        if args:
            optional = f'[{",".join(args)}]'
        cmd = [
            "pip",
            "install",
            "-e",
            f"{self.target.parent}{optional}",
            "--config-settings",
            "editable_mode=strict",
        ]
        subprocess.run(cmd, check=False)

    def pl(self: "CliMixin", *args: str) -> None:
        self._raise_if_disabled("pylint")
        cmd = ["git", "add", "-u"]
        subprocess.run(cmd, check=True)
        cmd = [
            "pre-commit",
            "run",
            f"--config={self.target/'pre-commit'/'config.yaml'}",
            "pylint",
            *args,
        ]
        self._run_with_line_limit(cmd)

    def pra(self: "CliMixin", *args: str) -> None:
        self._raise_if_disabled("pre-commit")
        cmd = ["git", "add", "-u"]
        subprocess.run(cmd, check=True)
        if not args:
            args = ("--all",)
        cmd = [
            "pre-commit",
            "run",
            f"--config={self.target/'pre-commit'/'config.yaml'}",
            *args,
        ]
        subprocess.run(cmd, check=False)

    def sdist(self: "CliMixin", zipped: bool = False) -> None:
        self._raise_if_disabled("package")
        cmd = ["python", "setup.py", "sdist"]
        subprocess.run(cmd, check=True)

        if not zipped:
            files = list((self.target.parent / "dist").glob("*.tar.gz"))
            for file in files:
                path = file.with_name(file.name.replace(".tar.gz", ""))
                if path.exists():
                    shutil.rmtree(path, ignore_errors=True)
            cmd = ["tar", "-zxf", *map(str, files), "-C", "dist"]
            subprocess.run(cmd, check=True)
            for file in files:
                file.unlink()

    def todo_and_note(
        self: "CliMixin",
        flavor: str,
        new: tp.Optional[str] = None,
        close: tp.Optional[str] = None,
        gitignore: bool = False,
    ) -> None:
        if new and close:
            raise RuntimeError("cannot set new and close an the same time")

        with self.extra(), self.cwd_to_root():
            todo = TodoSetter(self)  # type: ignore
            if gitignore:
                todo.add_gitignore()
            if new:
                todo.new(new, flavor)
            elif close:
                todo.close(close, flavor)
            else:
                todo.show(flavor)

    def _raise_if_disabled(self, component: str) -> None:
        if not self.is_enabled(component):
            raise RuntimeError(
                f"{component} disabled for this project, check your auxilium file."
            )

    @staticmethod
    def _run_with_line_limit(cmd: tp.List[str], limit: int = 50) -> None:
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE)
        i = 0
        for i, line in enumerate(proc.stdout.decode("utf-8").split("\n")):
            if i < limit:
                print(line)
        if i >= limit:
            print(f"{i-limit} more lines not shown, only the first {limit}...")


class CliRenderer(CliMixin, AllComponents):  # pylint: disable=too-many-ancestors
    pass
