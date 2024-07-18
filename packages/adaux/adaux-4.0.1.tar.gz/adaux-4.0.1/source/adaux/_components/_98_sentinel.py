# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import collections
import contextlib
import typing as tp

from .._logging import logger
from .._proto_namespace import _ProtoNamespace
from ._00_extra_level import ExtraLevel
from ._03_meta import MetaMixin


class SentinelMixin(MetaMixin):
    def __init__(self, *args: tp.Any, **kwgs: tp.Any) -> None:
        super().__init__(*args, **kwgs)
        self._auxcon_entered = False
        self._extra_counter: tp.DefaultDict[ExtraLevel, int] = collections.defaultdict(
            int
        )

    def _part_enabled(self, part: tp.Type[tp.Any]) -> bool:  # MetaMixin related
        enable, _ = self._en_disabled_list()
        if enable:
            mro = self.__class__.__mro__
            if SentinelMixin in mro:  # keep after (and)
                if mro.index(part) <= mro.index(SentinelMixin):
                    return True

        return super()._part_enabled(part)

    def bake(self) -> None:
        with self.extra():
            super().bake()
            self.writeout()

    @contextlib.contextmanager
    def with_formatted(self) -> tp.Iterator[_ProtoNamespace]:
        level = ExtraLevel.FORMATTED
        if self._extra_counter[level] == 0:
            super().formatted()
        self._extra_counter[level] += 1
        yield self.auxf
        self._extra_counter[level] -= 1
        if self._extra_counter[level] == 0:
            del self.auxf

    @contextlib.contextmanager
    def with_defaulted(self) -> tp.Iterator[_ProtoNamespace]:
        level = ExtraLevel.DEFAULTED
        if self._extra_counter[level] == 0:
            super().defaulted()
        self._extra_counter[level] += 1
        yield self.auxd
        self._extra_counter[level] -= 1
        if self._extra_counter[level] == 0:
            del self.auxd

    @contextlib.contextmanager
    def with_enriched(self) -> tp.Iterator[_ProtoNamespace]:
        level = ExtraLevel.ENRICHED
        if self._extra_counter[level] == 0:
            super().enriched()
        self._extra_counter[level] += 1
        yield self.auxe
        self._extra_counter[level] -= 1
        if self._extra_counter[level] == 0:
            del self.auxe

    @contextlib.contextmanager
    def with_hydrated(self) -> tp.Iterator[_ProtoNamespace]:
        level = ExtraLevel.HYDRATED
        if self._extra_counter[level] == 0:
            super().hydrated()
        self._extra_counter[level] += 1
        yield self.auxh
        self._extra_counter[level] -= 1
        if self._extra_counter[level] == 0:
            del self.auxh

    @contextlib.contextmanager
    def extra(
        self, level: ExtraLevel = ExtraLevel.ENRICHED
    ) -> tp.Iterator[_ProtoNamespace]:
        # pylint: disable=contextmanager-generator-missing-cleanup
        if self._extra_counter[level] == 0:
            logger.debug("enabled %s", level)
        if level == ExtraLevel.TEMPLATED:
            self.templated()
            with self.with_formatted() as aux:
                yield aux
        elif level == ExtraLevel.TEMPLATED_WITH_NEGATIVE:
            self.templated(negative_default=True)
            with self.with_formatted() as aux:
                yield aux
        elif level == ExtraLevel.DEMODATA:
            self.templated()
            self.demodata()
            with self.with_formatted() as aux:
                yield aux
        elif level == ExtraLevel.RAW:
            yield self.auxcon
        elif level == ExtraLevel.FORMATTED:
            with self.with_formatted() as aux:
                yield aux
        elif level == ExtraLevel.DEFAULTED:
            with self.with_formatted(), self.with_defaulted() as aux:
                yield aux
        elif level == ExtraLevel.ENRICHED:
            with self.with_formatted(), self.with_defaulted(), self.with_enriched() as aux:
                yield aux
        elif level == ExtraLevel.HYDRATED:
            with self.with_formatted(), self.with_defaulted(), self.with_enriched(), self.with_hydrated() as aux:
                yield aux

        if self._extra_counter[level] == 0:
            logger.debug("disabled %s", level)
