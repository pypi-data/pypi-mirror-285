# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import contextlib
import logging
import os
import shlex
import shutil
import subprocess
import typing as tp
from pathlib import Path

from .._logging import logger
from .._proto_namespace import _ProtoNamespace
from .._util import subprocess_run
from ._00_extra_level import ExtraLevel
from ._03_meta import MetaMixin

__all__ = ["MultiManageMixin"]


class MultiManageMixin(MetaMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("projects", "tasks")

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.multimanage = _ProtoNamespace(
            projects=["./admem"], tasks=_ProtoNamespace(ll=["ls -la"])
        )

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "multimanage")

        self._to_list("multimanage", "projects")
        self._to_proto_ns("multimanage", "tasks")

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("multimanage", _ProtoNamespace())
        self.auxd.multimanage.setdefault("projects", [])
        self.auxd.multimanage.setdefault("tasks", _ProtoNamespace())

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.multimanage

        for project in data.projects:
            if not Path(project).exists():
                raise RuntimeError(f"project {project} does not exist")

        for _, task in data.tasks.items():
            assert isinstance(task, list)

    def mm_update(self, all_vip_branches: bool = False, prune: bool = False) -> None:
        def run(auxcon: _ProtoNamespace) -> None:
            branches = list(auxcon.gitlab["vip_branches"].keys())
            if not all_vip_branches:
                branches = branches[:1]
            prune_flag = ""
            if prune:
                prune_flag = "-p"
            self.subprocess_run_shlex(f"git fetch --all {prune_flag}".strip())
            # reversed, as we want to end up on default
            for branch in reversed(branches):
                self.subprocess_run_shlex(f"git checkout {branch}")
                self.subprocess_run_shlex("git pull")
            if prune:
                lbranches = self.subprocess_run_shlex_out(
                    "git branch --format='%(refname:short)'"
                ).split("\n")
                rbranches = self.subprocess_run_shlex_out(
                    "git branch -r --format='%(refname:short)'"
                ).split("\n")
                for lbra in lbranches:
                    if not any(lbra in rbra for rbra in rbranches):
                        ans = self._prompt(  # type: ignore
                            f"delete local branch '{lbra}' (y/n)", fg="red"
                        )
                        if ans not in "yY":
                            continue
                        self.subprocess_run_shlex(f"git branch -D {lbra}")

        summary = ["adaux mm update"]
        if all_vip_branches:
            summary.append("-a")
        if prune:
            summary.append("-p")

        self._run_with_report(run, " ".join(summary))

    def _run_with_report(
        self, run: tp.Callable[[_ProtoNamespace], None], summary_desc: str = ""
    ) -> None:
        report = []
        for project in self.auxe.multimanage.projects:
            auxcon = self.get_subproject(project, level=ExtraLevel.RAW)
            with self.project_header(auxcon), self.preserve_cwd(Path(project)):
                try:
                    run(auxcon)
                    report.append([auxcon.project.name, "pass"])
                except RuntimeError as err:
                    self._print(err.args[0], fg="red")
                    report.append([auxcon.project.name, "fail"])
                    continue

        with self.project_header(
            _ProtoNamespace(project=_ProtoNamespace(name=summary_desc))
        ):
            for name, state in report:
                col = ["red", "green"][state == "pass"]
                self._print(f"[{state}] {name}", fg=col)

    def get_subproject(
        self, project: str, level: ExtraLevel = ExtraLevel.ENRICHED
    ) -> _ProtoNamespace:
        with self.preserve_cwd():
            # pylint: disable=too-many-function-args,unexpected-keyword-arg
            x = self.__class__(Path(project), silent=True)  # type: ignore
            x.load_auxcon()
            with x.extra(level=level) as aux:  # type: ignore
                return aux  # type: ignore

    def mm_adaux(self, cmd_str: str) -> None:
        verbose = "-n"
        if logger.getEffectiveLevel() == logging.DEBUG:
            verbose = " -nv"
        self.mm_run(f"adaux {verbose} {cmd_str}")

    def mm_run(self, cmd_str: str) -> None:
        def run(auxcon: _ProtoNamespace) -> None:  # pylint: disable=unused-argument
            cmd_seq = self.auxe.multimanage.tasks.get(cmd_str, [cmd_str])
            for x in cmd_seq:
                self.subprocess_run_shlex(x, capture_output=False)

        self._run_with_report(run, f"{cmd_str}")

    @contextlib.contextmanager
    def project_header(self, auxcon: _ProtoNamespace) -> tp.Iterator[None]:
        columns, _ = shutil.get_terminal_size((80, 20))
        res = auxcon.project.name
        pad = columns - len(res) - 1
        self._print(res, fg="yellow", nl=False, bold=True)
        self._print(" " + pad * ">", fg="white")
        yield
        # self._print(pad * "<" + " " + res, fg="yellow")

    @contextlib.contextmanager
    def preserve_cwd(self, new_path: tp.Optional[Path] = None) -> tp.Iterator[None]:
        original_cwd = Path.cwd()
        if new_path:
            logger.debug("cwd changed to %s", new_path)
            os.chdir(new_path)
        try:
            yield
        finally:
            logger.debug("cwd changed to %s", original_cwd)
            os.chdir(original_cwd)

    def subprocess_run_shlex(
        self, cmd_str: str, *args: tp.Any, show: bool = True, **kwgs: tp.Any
    ) -> "subprocess.CompletedProcess[bytes]":
        kwgs.setdefault("check", True)
        kwgs.setdefault("capture_output", True)
        if show:
            columns, _ = shutil.get_terminal_size((80, 20))
            msg = f"> {cmd_str}"
            padding = columns - len(msg)
            self._print(msg, fg="blue", nl=not kwgs["capture_output"])
        cmd = shlex.split(cmd_str)
        try:
            res = subprocess_run(cmd, *args, **kwgs)
            if show:
                if kwgs["capture_output"]:
                    self._print((padding - 4) * " " + "[ok]", fg="green")
            return res
        except subprocess.CalledProcessError as err:
            if show and kwgs["capture_output"]:
                self._print((padding - 6) * " " + "[fail]", fg="red")
            raise RuntimeError(f"error when running {cmd}, see error above") from err

    def subprocess_run_shlex_out(self, *args: tp.Any, **kwgs: tp.Any) -> str:
        kwgs.setdefault("show", False)
        kwgs.setdefault("capture_output", True)
        if not kwgs["capture_output"]:
            raise RuntimeError("cannot use output_as and capture_output=False")

        res = self.subprocess_run_shlex(*args, **kwgs)

        return res.stdout.decode().strip()
