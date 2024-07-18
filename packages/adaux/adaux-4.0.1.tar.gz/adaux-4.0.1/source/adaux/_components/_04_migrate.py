# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._logging import logger
from .._proto_namespace import _ProtoNamespace
from .._util import LazyVersionStr
from ._00_extra_level import ExtraLevel
from ._04_monotonic_version import MonotonicVersionMixin


class MigrateMixin(MonotonicVersionMixin):
    def __init__(self, *args: tp.Any, **kwgs: tp.Any) -> None:
        super().__init__(*args, **kwgs)
        self._migration_points = [
            "2.8.4",
            "3.0.0",
            "3.4.0",
        ]

    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("version",)

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "meta", "migrate")

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.meta.setdefault("migrate", _ProtoNamespace())
        self.auxd.meta.migrate.setdefault("version", str(LazyVersionStr()))

    def migrate(self, target_version: tp.Optional[str] = None) -> None:
        self.auxcon.setdefault("meta", _ProtoNamespace())
        self.auxcon.meta.setdefault("migrate", _ProtoNamespace())
        from_version = self.auxcon.meta.migrate.get(
            "version", self._migration_points[0]
        )
        target_version = target_version or self._migration_points[-1]
        mig_path = []
        for to_version in self._migration_points:
            if from_version < to_version <= target_version:
                mig_path.append(to_version)
        if mig_path:
            logger.info("migration path is ->%s", "->".join(mig_path))
        else:
            self._print("no migration necessary", fg="green")

        self._to_version = None
        for to_version in mig_path:
            self._to_version = to_version
            self.step_migrate()
        if self._to_version is not None:
            self._print(
                f"migrated successfully to point {self._to_version}", fg="yellow"
            )

        del self._to_version

        self.auxcon.meta.migrate.version = to_version

        with self.extra(ExtraLevel.FORMATTED) as aux:  # type: ignore
            self.save_auxcon(aux)

    def to_version(self, version: str) -> bool:
        if version not in self._migration_points:
            raise RuntimeError(
                f"version '{version}' is not within the migration points '{self._migration_points}', please correct or add"
            )
        return version == self._to_version
