# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import dataclasses as dc
import getpass
import json
import string
import typing as tp
from pathlib import Path

from ._components import AllComponents


@dc.dataclass
class TodoSetter:
    ns: AllComponents
    user: str = dc.field(default_factory=getpass.getuser)
    data: tp.Dict[str, tp.Dict[str, tp.List[str]]] = dc.field(default_factory=dict)

    def __post_init__(self) -> None:
        self.load()

    @property
    def json_path(self) -> Path:
        return self.ns.target / "auxilium" / "todos_and_notes.json"

    @property
    def flavors(self) -> tp.Sequence[str]:
        return ["todo", "note"]

    def load(self) -> None:
        path = self.json_path
        if path.exists():
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

        self.data.setdefault(self.user, {})

    def dump(self) -> None:
        path = self.json_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
            f.write("\n")

    def add_gitignore(self) -> None:
        gitignore = self.json_path.parent / ".gitignore"
        if gitignore.exists():
            self._print(".gitignore already exists", fg="green")
        else:
            with open(gitignore, "w", encoding="utf-8") as f:
                f.write(self.json_path.name + "\n")
            self._print(f"added .gitignore file to ignore {self.json_path}", fg="green")

    def userlist(self, flavor: str) -> tp.List[str]:
        self.data[self.user].setdefault(flavor, [])
        return self.data[self.user][flavor]

    @property
    def id_list(self) -> tp.Sequence[str]:
        return string.ascii_uppercase

    def _print(self, *args: str, **kwgs: str) -> None:
        self.ns._print(*args, **kwgs)  # pylint: disable=protected-access

    def show(self, flavor: str = "todo", pretext: str = "") -> None:
        if not self.userlist(flavor):
            self._print(f"no {flavor}s for {self.user}", fg="green")
            return

        self._print(f"{pretext}{flavor}s for {self.user}", fg="yellow")
        for id_, todo in zip(self.id_list, self.userlist(flavor)):
            self._print(f"  [{id_}] {todo}", fg="yellow")

    def new(self, new: str, flavor: str = "todo") -> None:
        if new not in self.userlist(flavor):
            self.userlist(flavor).append(new)
            self.dump()
            self._print(f"{self.user} added {flavor} '{new}'", fg="green")
        else:
            self._print(f"{flavor} '{new}' already exists for {self.user}", fg="red")

    def close(self, close: str, flavor: str = "todo") -> None:
        idx = self.fuzzy_finder(close, flavor)
        text = self.userlist(flavor).pop(idx)
        self.dump()
        self.show(flavor, pretext="remaining ")
        self._print(f"{self.user} removed {flavor} '{text}'", fg="red")

    def fuzzy_finder(self, descr: str, flavor: str) -> int:
        if descr.upper() in self.id_list:
            return self.id_list.index(descr.upper())
        candidate = []
        for todo in self.userlist(flavor):
            if todo.startswith(descr):
                candidate.append(todo)

        if len(candidate) == 1:
            return self.userlist(flavor).index(candidate[0])
        msg = "no"
        if len(candidate) > 1:
            msg = "more than one"
        raise RuntimeError(f"{msg} {flavor} matching '{descr}' found")
