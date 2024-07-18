# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import io

from .._parser import ConfigParser
from .._proto_namespace import _ProtoNamespace
from ._08_pip import PipMixin


class EntryPointMixin(PipMixin):
    def formatted(self) -> None:
        super().formatted()
        if "entry_points" in self.auxcon:
            self.auxf.entry_points = _ProtoNamespace(self.auxcon.entry_points or {})

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("entry_points", _ProtoNamespace())

    def enriched(self) -> None:
        super().enriched()
        stream = io.StringIO()
        ConfigParser.write_stream(self.auxe.entry_points, stream)
        self.auxe.pip.entry_points_filecontent = stream.getvalue().replace("\n", "\\n")

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.entry_points = _ProtoNamespace()
        data = self.auxcon.entry_points
        data.plugin_hook = dict(plugin_name="plugin:func")

    def bake(self) -> None:
        super().bake()
        config = self.auxe.python_project.config
        data = self.auxe.entry_points
        config["options.entry_points"].update(data)
