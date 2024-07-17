# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import typing as tp

from .._parser import Jinja2Parser
from .._parser import YamlParser
from .._proto_namespace import _ProtoNamespace
from ._03_meta import MetaMixin
from ._05_project import ProjectMixin
from ._06_dependency import DependencyMixin


class PrecommitMixin(DependencyMixin, ProjectMixin, MetaMixin):
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return ("hooks", "rev_overwrite")

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)

        data = self.auxcon.dependencies
        data.dev.append(self.versions.pre_commit)
        data.dev_apt.append("git-core")

        data = self.auxcon.pre_commit = _ProtoNamespace(hooks=_ProtoNamespace())
        data.hooks["check-yaml"] = _ProtoNamespace(exclude="devops/CI")
        data.hooks["check-toml"] = _ProtoNamespace()
        data.hooks["check-json"] = _ProtoNamespace()
        data.hooks["end-of-file-fixer"] = _ProtoNamespace()
        data.hooks["add-copy-right"] = _ProtoNamespace()
        data.hooks["trailing-whitespace"] = _ProtoNamespace()
        data.hooks.black = _ProtoNamespace()
        data.hooks["blacken-docs"] = _ProtoNamespace()
        data.hooks.pyupgrade = _ProtoNamespace()
        data.hooks.pycln = _ProtoNamespace()
        data.hooks["reorder-python-imports"] = _ProtoNamespace()

        if self.is_enabled("mypy"):
            data.hooks.mypy = _ProtoNamespace()

        if self.is_enabled("pylint"):
            data.hooks.pylint = _ProtoNamespace()

    def demodata(self) -> None:
        super().demodata()
        data = self.auxcon.pre_commit
        data.hooks["pylint-test"] = dict(files="tests/")
        data.rev_overwrite = _ProtoNamespace(black="21.9b0")

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "pre_commit")
        for key in self.__keys():
            iter_mapping = key == "hooks"
            self._to_proto_ns("pre_commit", key, iter_mapping=iter_mapping)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("pre_commit", _ProtoNamespace())
        data = self.auxd.pre_commit
        for key in self.__keys():
            data.setdefault(key, _ProtoNamespace())

    def enriched(self) -> None:
        super().enriched()
        data = self.auxe.pre_commit
        custom_config = self.target_custom / "pre-commit" / "config.yaml"
        self.auxe.versions.update(
            {key: f"{key}=={val}" for key, val in data.rev_overwrite.items()}
        )
        data.custom = ""
        if custom_config.exists():
            with open(custom_config, encoding="utf-8") as f:
                data.custom = f.read()

    def bake(self) -> None:  # pylint: disable=too-many-branches
        super().bake()

        data = self.auxe.pre_commit
        srcj = self.root / "pre-commit/config.yaml.jinja2"
        with Jinja2Parser.render_to_tmp(srcj, aux=self.auxe) as src:
            config = YamlParser.read(src)

        requested_hooks = list(data.hooks.keys())

        self._raise_if_unsupported_hooks(config, requested_hooks)

        multi_hook_repo = ""
        # remove the ones not selected
        for repo in reversed(config.repos):

            def keep_selected(hook: _ProtoNamespace) -> bool:
                return hook.id in requested_hooks

            if len(repo.hooks) > 1:
                multi_hook_repo = repo.repo
            repo.hooks = list(filter(keep_selected, repo.hooks))
            if not repo.hooks:  # remove repo if empty
                config.repos.remove(repo)

            # integrate options
            for hook in repo.hooks:
                for key, val in data.hooks[hook.id].items():
                    if isinstance(val, list):
                        val = "|".join(val)
                    if key in ["coverage"]:
                        continue
                    if key not in ["files", "exclude"]:
                        raise NotImplementedError(
                            f"support for option '{key}' of {hook.id} not implemented yet"
                        )
                    if key in hook:
                        hook[key] += "|" + val
                    else:
                        hook[key] = val

        # check if local python files are required from the hook
        for repo in config.repos:
            for hook in repo.hooks:
                entry = hook.get("entry")
                if entry and entry.startswith("devops/") and "custom" not in entry:
                    self.bake_file(entry.replace("devops/", ""), chmod=0o755)

        # order the config according to the requested_hooks
        if multi_hook_repo != "":
            self._print(
                f"pre-commit: cannot sort repos: '{multi_hook_repo}' has multiple hooks",
                fg="red",
            )
        config.repos = sorted(
            config.repos, key=lambda x: requested_hooks.index(x.hooks[0].id)
        )

        dest = self.target / "pre-commit/config.yaml"
        written = YamlParser.write(config, dest)
        data.config = config
        if written:
            self._print(f"baked {dest}", fg="green")

    @classmethod
    def _raise_if_unsupported_hooks(
        cls, config: _ProtoNamespace, requested_hooks: tp.Iterable[str]
    ) -> None:
        available_hooks: tp.List[str] = sum(
            ([hook.id for hook in repo.hooks] for repo in config.repos), []
        )
        unknown_hooks = set(requested_hooks) - set(available_hooks)
        if unknown_hooks:
            raise RuntimeError(
                f"pre-commit hooks are not supported by aux: {unknown_hooks}.\n"
                "       Hint: You could add them in the custom directory."
            )
