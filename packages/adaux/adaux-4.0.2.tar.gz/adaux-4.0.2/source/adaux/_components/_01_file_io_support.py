# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import contextlib
import filecmp
import os
import shutil
import sys
import typing as tp
from pathlib import Path

from .._base_parser import FileOpsConvenience
from .._parser import BaseParser
from .._parser import ConfigParser
from .._parser import Jinja2Parser
from .._parser import YamlParser
from .._proto_namespace import _ProtoNamespace
from ._00_extra_level import ExtraLevel


class FileIOSupport(FileOpsConvenience):
    def __init__(self) -> None:
        super().__init__()
        self.root = Path(__file__).resolve().parent.parent / "src"
        self.verbose = True
        self.auxcon_file: Path = Path()
        self.target: Path = Path()

    def _print(
        self, msg: str, **kwgs: tp.Any  # pylint: disable=unused-argument
    ) -> None:
        if self.verbose:
            print(msg)

    @contextlib.contextmanager
    def cwd_to_root(self) -> tp.Iterator[Path]:
        old = os.getcwd()
        new = self.auxcon_file.parent
        os.chdir(new)
        yield new
        os.chdir(old)

    @contextlib.contextmanager
    def preprend_to_sys_path(self, path: Path) -> tp.Iterator[None]:
        sys.path.insert(0, str(path))
        yield
        sys.path.pop(0)

    def load_auxcon(self) -> None:
        # pylint: disable=attribute-defined-outside-init
        self.auxcon = self.get_parser().read(self.auxcon_file)

    def save_auxcon(self, aux: _ProtoNamespace) -> None:
        self.get_parser().write(aux, self.auxcon_file)

    @property
    def target_custom(self) -> Path:
        return self.target / "custom"

    def get_parser(self) -> tp.Type[BaseParser]:
        suffix = self.auxcon_file.suffix
        if suffix in [".ini", ".cfg"]:
            return ConfigParser
        if suffix in [".yaml", ".yml"]:
            return YamlParser

        raise NotImplementedError(f"filetype {suffix} not supported!")

    def save_auxcon_to_stream(
        self, ost: tp.TextIO, level: ExtraLevel = ExtraLevel.DEFAULTED
    ) -> None:
        # pylint: disable=no-member
        with self.extra(level=level) as aux:  # type: ignore
            YamlParser.write_stream(aux, ost)

    def copy_file(
        self,
        name: tp.Union[str, Path],
        dest_name: tp.Union[str, Path] = "",
        chmod: tp.Optional[int] = None,
        custom: bool = False,
    ) -> None:
        if isinstance(name, str):
            if custom:
                src = self.target_custom / name
            else:
                src = self.root / name
        else:
            src = name
            assert dest_name != ""

        dest_name = dest_name or name
        if isinstance(name, str):
            dest = self.target / dest_name
        else:
            dest = Path(dest_name)

        self.ensure_parent(dest)

        if dest.exists() and filecmp.cmp(src, dest):
            return

        shutil.copyfile(src, dest)
        if chmod:
            self.chmod(dest, chmod)
        self._print(f"copied {dest}", fg="blue")

    def bake_file(  # pylint: disable=too-many-arguments
        self,
        name: str,
        dest_name: tp.Union[str, Path] = "",
        chmod: tp.Optional[int] = None,
        only_if_inexistent: bool = False,
        custom: bool = False,
        ignore_absent: bool = False,
        **kwgs: tp.Any,
    ) -> None:
        dest_name = dest_name or name
        src_dir = self.target_custom if custom else self.root
        dest = self.target / dest_name
        if only_if_inexistent and dest.exists():
            return

        src = src_dir / name
        if src.exists():
            self.copy_file(name, dest_name, chmod=chmod, custom=custom)
            return

        jinja_src = src.with_suffix(src.suffix + ".jinja2")
        if not jinja_src.exists():
            if ignore_absent:
                return
            raise FileNotFoundError(jinja_src)

        # pylint: disable=no-member
        written = Jinja2Parser.render_to_dest(jinja_src, dest, aux=self.auxe, **kwgs)  # type: ignore
        if written:
            if chmod:
                self.chmod(dest, chmod)
            self._print(f"baked {dest}", fg="green")

    def combine_files(self, *names: str, dest_name: str) -> None:
        tmp_combo = self.root / "temp-combination"
        if tmp_combo.exists():
            tmp_combo.unlink()
        with open(tmp_combo, "a", encoding="utf-8") as tmp:
            for name in names:
                src = self.root / name
                with open(src, encoding="utf-8") as in_:
                    tmp.writelines(in_.readlines())
                    if name != names[-1]:
                        tmp.write("\n")

        self.copy_file(tmp_combo.name, dest_name)
        tmp_combo.unlink()

    @classmethod
    def chmod(cls, dest: Path, chmod: int) -> None:
        os.chmod(dest, chmod)

    def copy_many_files(self, *names: str) -> None:
        for name in names:
            self.copy_file(name)
