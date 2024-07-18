# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import collections
import typing as tp

from .._proto_namespace import _ProtoNamespace
from ._02_base import BaseComponent


class MetaMixin(BaseComponent):
    def formatted(self) -> None:
        super().formatted()
        keys = ["disable", "enable", "migrate"]
        self._copy_keys_over(keys, "meta")
        self._to_list("meta", "disable")
        self._to_list("meta", "enable")
        # migrate is handeled by MigrateMixin

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("meta", _ProtoNamespace())
        self.auxd.meta.setdefault("disable", [])
        self.auxd.meta.setdefault("enable", [])

        if self.auxd.meta.disable and self.auxd.meta.enable:
            self._error_both()

    def _error_both(self) -> None:
        raise RuntimeError("Cannot set enable and disable at the same time.")

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.meta = _ProtoNamespace(disable=["docs"])

    def is_enabled(self, component_name: str) -> bool:
        for x in self.__class__.__mro__:
            if self._comp_name_type_match(component_name, x):
                return self._component_enabled(component_name)
        return False

    def type_wo_disabled(
        self,
        *,
        discard_before: str = "",
        check_absence: bool = True,
    ) -> "tp.Type[MetaMixin]":
        res: tp.List[type] = []
        keep_after = "MetaMixin"
        for part in self.__class__.__mro__:
            if part.__name__ == keep_after:
                res.append(part)
                continue
            if part.__name__ == discard_before:
                res.clear()
            if part.__name__ in ["AllComponents", "DynComponent"]:
                continue
            if self._part_enabled(part):
                res.append(part)

        res_type = BaseComponent.compose(*reversed(res))

        # check if disabled did not get added by enabled
        if self._uses_disable() and check_absence:
            compare_to = self.type_wo_disabled(
                discard_before="SentinelMixin", check_absence=False
            )
            parents: tp.MutableMapping[type, tp.Sequence[type]] = (
                collections.defaultdict(list)
            )
            for part in compare_to.__mro__[1:]:  # remove bottom dyn
                parents[part] = part.__mro__[1:]  # remove self == part
                if not self._part_enabled(part):
                    used_by = [
                        key.__name__ for key, val in parents.items() if part in val
                    ]
                    used_by2 = [val for key, val in parents.items() if part in val]
                    print(used_by2)
                    raise RuntimeError(
                        f"{part.__name__} cannot be disabled, as it is used by '{', '.join(used_by)}'"
                    )

        return res_type  # type: ignore

    def _en_disabled_list(self) -> tp.Tuple[tp.List[str], tp.List[str]]:
        disable = self.auxcon.get("meta", _ProtoNamespace()).get("disable", [])
        enable = self.auxcon.get("meta", _ProtoNamespace()).get("enable", [])
        return enable, disable

    def _component_enabled(self, component_name: str) -> bool:
        enable, disable = self._en_disabled_list()
        if enable:
            if disable:
                self._error_both()
            return component_name in enable
        if disable:
            return component_name not in disable
        return True

    def _uses_disable(self) -> bool:
        enable, disable = self._en_disabled_list()
        if enable:
            if disable:
                self._error_both()
            return False
        return True

    def _part_enabled(self, part: tp.Type[tp.Any]) -> bool:
        enable, disable = self._en_disabled_list()
        if enable:
            if disable:
                self._error_both()
            if part in MetaMixin.__mro__:  # keep before (and)
                return True
            # see SentinelMixin for other end
            return any(self._comp_name_type_match(x, part) for x in enable)
        if disable:
            return not any(self._comp_name_type_match(x, part) for x in disable)
        return True

    @classmethod
    def _comp_name_type_match(
        cls, component_name: str, component_type: tp.Type[tp.Any]
    ) -> bool:
        return cls._canon_comp_name(component_name) == cls._canon_type_name(
            component_type
        )

    @classmethod
    def _canon_type_name(cls, component_type: tp.Type[tp.Any]) -> str:
        return component_type.__name__.lower().replace("mixin", "")

    @classmethod
    def _canon_comp_name(cls, component_name: str) -> str:
        return component_name.replace("-", "")

    def step_migrate(self) -> None:
        super().step_migrate()

        if self.to_version("3.0.0"):  # type: ignore
            if "meta" in self.auxcon and "disabled" in self.auxcon.meta:
                self.auxcon.meta.disable = self.auxcon.meta.pop("disabled")
