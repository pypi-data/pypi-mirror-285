# Copyright (c) 2021-2024 Mario S. Könz; License: MIT
import json
import os
import re
import typing as tp

from .._logging import logger
from .._proto_namespace import _ProtoNamespace
from .._util import ApiRequestCommunicator
from ._00_extra_level import ExtraLevel
from ._03_meta import MetaMixin
from ._18_payload import PayloadMixin


class CiMixin(PayloadMixin, MetaMixin):
    # pylint: disable=unused-private-member
    @classmethod
    def __keys(cls) -> tp.Tuple[str, ...]:
        return (
            "mechanism",
            "docker_image",
            "trigger",
            "use_adaux_img",
            "jobs",
            "variables",
        )

    def templated(self, negative_default: bool = False) -> None:
        super().templated(negative_default)
        self.auxcon.ci = _ProtoNamespace(trigger=_ProtoNamespace())
        data = self.auxcon.ci.trigger
        data["+push"] = {
            "-tag": {
                "-openmr": {
                    "+release": {
                        "+gitlab": {
                            "gitlab-release": None,
                            "pkg-gitlab": None,
                        }
                    },
                },
            }
        }
        data["+mr"] = {
            "+draft": {
                "pre-commit": None,
            },
            "-draft": {
                "pre-commit-all": None,
            },
            "+release": {
                "check-release-notes": None,
            },
        }

        if self.is_enabled("pytest"):
            data["+mr"]["+draft"]["pytest"] = None
            if self.is_enabled("coverage"):
                data["+mr"]["-draft"].update(
                    {
                        "-vip": {
                            "pytest-mr": None,
                        },
                        "+vip": {
                            "pytest-cov-mr": None,
                        },
                    }
                )
            else:
                data["+mr"]["-draft"]["pytest-mr"] = None

        if self.is_enabled("docs"):
            data["+mr"]["-draft"]["+release"] = {"docs": None}
            data["+push"]["-tag"]["-openmr"]["+release"]["docs"] = None

    def update_to_template(self, tpl: _ProtoNamespace, full: _ProtoNamespace) -> None:
        super().update_to_template(tpl, full)

        with self.extra(ExtraLevel.HYDRATED) as auxe:  # type: ignore
            valid_payloads = auxe.payload.lookup.all_keys()

        added = []

        def deep_add(trig_chain: str, obj: tp.Any) -> None:
            last_key = trig_chain.rsplit(".", 1)[1]
            if last_key.startswith("+") or last_key.startswith("-"):
                for key, val in obj.items():
                    deep_add(trig_chain + "." + key, val)
            else:
                added.append(trig_chain)

        def deep_merge(
            tpl: tp.Optional[_ProtoNamespace],
            user: tp.Optional[_ProtoNamespace],
            trig_chain: str = "ci.trigger",
        ) -> tp.Optional[_ProtoNamespace]:
            if tpl is None and user is None:
                return None
            if tpl is None:
                return user
            if user is None:
                deep_add(trig_chain, tpl)
                return tpl
            res = _ProtoNamespace()
            all_keys = list(tpl.keys())
            all_keys += [x for x in user.keys() if x not in all_keys]

            for key in all_keys:
                res[key] = deep_merge(
                    tpl.get(key), user.get(key), trig_chain=trig_chain + "." + key
                )
            return res

        new_trigger = deep_merge(tpl.ci.trigger, self.auxf.ci.trigger)

        removed = []

        def deep_remove(
            trigger: tp.Optional[_ProtoNamespace], trig_chain: str = "ci.trigger"
        ) -> None:
            if trigger is None:
                return
            for key, val in list(trigger.items()):
                if key.startswith("+") or key.startswith("-"):
                    deep_remove(val, trig_chain=trig_chain + "." + key)
                    if not trigger[key]:
                        del trigger[key]
                elif key not in valid_payloads:
                    del trigger[key]
                    removed.append(f"{trig_chain}.{key}")

        deep_remove(new_trigger)
        overlap = set(added) & set(removed)
        if overlap:
            logger.warning("overlap (added and removed) in ci.trigger: %s", overlap)
        for add in added:
            if add not in overlap:
                self._print(f"added  {add}", fg="green")
        for rem in removed:
            if rem not in overlap:
                self._print(f"removed {rem}", fg="red")
        self.auxf.ci.trigger = new_trigger

    def demodata(self) -> None:
        super().demodata()
        self.auxcon.ci.jobs = _ProtoNamespace(
            default=_ProtoNamespace(services=["docker:dind"])
        )
        self.auxcon.ci.mechanism = "monolith"

    def formatted(self) -> None:
        super().formatted()
        self._copy_keys_over(self.__keys(), "ci")

        for key in ["trigger", "jobs", "variables"]:
            self._to_proto_ns("ci", key, iter_mapping=True)

    def defaulted(self) -> None:
        super().defaulted()
        self.auxd.setdefault("ci", _ProtoNamespace())
        data = self.auxd.ci

        data.setdefault("mechanism", "monolith")
        data.setdefault(
            "jobs", _ProtoNamespace(default=_ProtoNamespace(services=["docker:dind"]))
        )
        data.setdefault("docker_image", self.versions.ci_docker_image)
        data.setdefault("trigger", _ProtoNamespace())
        data.setdefault("use_adaux_img", True)
        data.setdefault("variables", _ProtoNamespace())
        assert data.trigger is not None
        assert data.mechanism in ["monolith"]

    def step_migrate(self) -> None:
        super().step_migrate()

        if self.to_version("3.4.0"):  # type: ignore
            data = self.auxcon.get("ci", {})
            runner = data.get("runner", None)
            if runner:
                data.pop("runner")
                if runner == "dind-cached":
                    data["jobs"] = dict(
                        default=dict(tags=[runner]), pages=dict(tags=[runner])
                    )

                elif runner == "normal":
                    data["jobs"] = dict(default=dict(services=["docker:dind"]))
                else:
                    raise NotImplementedError(runner)

    def enriched(  # pylint: disable=too-many-locals,too-many-nested-blocks
        self,
    ) -> None:
        super().enriched()
        data = self.auxe.ci

        self.job2trigger = self.trigger_tree_by_job()

        data.used_rules = _ProtoNamespace()
        data.used_tag_rules = _ProtoNamespace()
        all_rules = []
        for job, trigger in self.job2trigger.items():
            rule_used = _ProtoNamespace(
                mr=False,
                web=False,
                pipeline=False,
                schedule=False,
                trigger=False,
                api=False,
            )
            for reason in self._get_trigger_combos(trigger):
                for key in ["push", "push_no_mr"] + list(rule_used):
                    if key in ["push", "push_no_mr"]:
                        if "+push" in reason:
                            rule_used.setdefault("push", False)
                            rule_used.setdefault("push_no_mr", True)
                            if "-openmr" in reason or "+tag" in reason:
                                continue

                            rule_used["push_no_mr"] &= False
                            rule_used["push"] |= True
                    else:
                        rule_used[key] |= f"+{key}" in reason

            used_rules = [key for key, val in rule_used.items() if val]
            # will generate two tag rules for same tag, but this will be consolidated
            used_tag_rules = self._generate_used_tag_rules(rule_used, trigger=trigger)
            for x in used_rules:
                if x not in all_rules:
                    all_rules.append(x)
            data.used_rules[job] = used_rules
            data.used_tag_rules[job] = used_tag_rules

        # consolidate (multiple jobs can have tag-0 with different content atm)
        reverse_atr: tp.Dict[str, str] = {}
        for job, trigger in self.job2trigger.items():
            utr = data.used_tag_rules[job]
            new_utr = _ProtoNamespace()
            for key, val in utr.items():
                if val not in reverse_atr:
                    new_nr = f"tag-{len(reverse_atr)}"
                    reverse_atr[val] = new_nr
                new_nr = reverse_atr[val]
                new_utr[new_nr] = val
            data.used_tag_rules[job] = new_utr

        data.all_tag_rules = _ProtoNamespace({v: k for k, v in reverse_atr.items()})
        data.all_rules = all_rules

    def trigger_tree_by_job(self) -> _ProtoNamespace:
        res = _ProtoNamespace()

        def deep_set(
            obj: _ProtoNamespace, opt: _ProtoNamespace, key: str, *keys: str
        ) -> None:
            if keys:
                obj.setdefault(key, _ProtoNamespace())
                deep_set(obj[key], opt, *keys)
            else:
                obj[key] = opt

        for task, opt, reason in self._get_payload_names_and_reason(
            [], collect_all=True
        ):
            if "job" in opt and "jobs" in opt:
                raise RuntimeError("cannot specify job and jobs at the same time")

            jobs = ["default"]
            if "job" in opt:
                jobs = [opt.pop("job")]
            if "jobs" in opt:
                jobs = opt.pop("jobs")

            for job in jobs:
                deep_set(res, opt, job, *reason, task)

        return res

    def _generate_used_tag_rules(
        self,
        rule_used: tp.Dict[str, bool],
        trigger: tp.Optional[_ProtoNamespace] = None,
    ) -> tp.Dict[str, tp.Tuple[tp.Tuple[str, ...], str]]:
        tags = []
        for x in self._get_trigger_combos(trigger=trigger):
            if x[0] == "+tag":
                tags.append(x)
            if len(x) > 1 and x[1] == "+tag":
                tags.append((x[1], x[0]) + x[2:])
        tags = sorted(tags)

        # structure is +tag +push +regex
        def create_rule(*triggers: str) -> str:
            conditions = []

            def compose_rule(gitlab_var: str, sign: str, match: str) -> str:
                start, stop = (
                    '= "',
                    '"',
                )
                if match.startswith("^"):
                    start, stop = (
                        "~ /",
                        "/",
                    )
                return f"${gitlab_var} {sign}{start}{match}{stop}"

            for trigger in triggers:
                sign = "=" if trigger[0] == "+" else "!"
                val = trigger[1:]
                if val in rule_used:
                    conditions.append(f'$CI_PIPELINE_SOURCE {sign}= "{val}"')
                elif val.startswith("login="):
                    condition = compose_rule(
                        "GITLAB_USER_LOGIN", sign, val.split("login=", 1)[1]
                    )
                    conditions.append(condition)
                elif val.startswith("username="):
                    condition = compose_rule(
                        "GITLAB_USER_NAME", sign, val.split("username=", 1)[1]
                    )
                    conditions.append(condition)
                else:
                    condition = compose_rule("CI_COMMIT_TAG", sign, val)
                    conditions.append(condition)
            return " && ".join(conditions)

        return {
            f"tag-{idx}": (it[1:], create_rule(*it[1:])) for idx, it in enumerate(tags)
        }

    def run_ci(  # pylint: disable=too-many-branches
        self, trigger_str: str, dry: bool = False, job: tp.Optional[str] = None
    ) -> int:
        if trigger_str == "gitlab":
            triggers = self._triggers_from_gitlab_ci(job)
        else:
            triggers = self._triggers_from_str(trigger_str)

        # get the payload_names
        if job:
            payload_names = self._get_payload_names(
                triggers, trigger=self.job2trigger[job]
            )
        else:
            payload_names = self._get_payload_names(triggers)

        self._print(f"triggers: {', '.join(triggers)}", fg="cyan")

        if not payload_names:
            self._print("no payloads selected", fg="yellow")
            return 0
        payloads = [self.auxh.payload.lookup[x] for x in payload_names]
        success = self.payload_run(*payloads, force=False, dry=dry)
        if success:
            if "+draft" in triggers:
                return 42
            return 0
        return 1

    def _triggers_from_gitlab_ci(  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self, job: tp.Optional[str] = None
    ) -> tp.Sequence[str]:
        triggers = []

        def env(key: str) -> str:
            return os.environ.get(key, "")

        gitlab2adaux = {
            "push": "+push",
            "merge_request_event": "+mr",
            "web": "+web",
            "pipeline": "+pipeline",
            "schedule": "+schedule",
            "trigger": "+trigger",
            "api": "+api",
        }
        source_trigger = gitlab2adaux[env("CI_PIPELINE_SOURCE")]

        if env("CI_COMMIT_TAG") != "":
            assert source_trigger == "+push"
            triggers.append(source_trigger)
            source_trigger = "+tag"
        if env("CI_OPEN_MERGE_REQUESTS") != "":
            triggers.append("+openmr")
            # we dont care abound env("CI_OPEN_MERGE_REQUESTS") in push
            # draft is only an option for mr lines
        triggers.append(source_trigger)

        mr_iid = env("CI_MERGE_REQUEST_IID")
        if mr_iid != "":
            try:
                resp = self.get_mr_status(mr_iid)
                if resp["draft"]:
                    triggers.append("+draft")
                    logger.info("merge request %s is a draft", mr_iid)
                else:
                    logger.info("merge request %s is NOT a draft", mr_iid)
            except RuntimeError as err:
                self._print(
                    f"could not access gitlab api for checking mr draft ({err.args[0]})",
                    fg="red",
                )

        gitlab = self.auxh.gitlab
        if source_trigger == "+push":
            branch_or_tag = env("CI_COMMIT_BRANCH")
        if source_trigger == "+tag":
            branch_or_tag = env("CI_COMMIT_TAG")

            utr = self.auxe.ci.used_tag_rules[(job or "default")]
            for tag_triggers, _ in utr.values():
                for tag_trigger in tag_triggers:
                    if tag_trigger[1] == "^":
                        # not totally sure it works for -
                        if re.match(tag_trigger[1:], branch_or_tag):
                            triggers.append(tag_trigger)
        elif source_trigger == "+mr":
            branch_or_tag = env("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
        elif source_trigger in ["+pipeline", "+web", "+api"]:
            branch_or_tag = env("CI_COMMIT_REF_NAME")
        elif source_trigger in ["+schedule"]:
            branch_or_tag = env("CI_COMMIT_REF_NAME") or gitlab.default_branch
        elif source_trigger == "+trigger":
            with open(env("TRIGGER_PAYLOAD"), encoding="utf-8") as f:
                content = json.load(f)
                branch_or_tag = content["ref"]

        if branch_or_tag in gitlab.vip_branches:
            triggers.append("+vip")
        if branch_or_tag == gitlab.default_branch:
            triggers.append("+default")
        if branch_or_tag == gitlab.release_branch:
            triggers.append("+release")

        branch_trigger = f"+{branch_or_tag}"
        if branch_trigger not in triggers:
            triggers.append(branch_trigger)

        triggers.append("+gitlab")
        triggers.append(f"+login={env('GITLAB_USER_LOGIN')}")
        triggers.append(f"+username={env('GITLAB_USER_NAME')}")
        return triggers

    def get_mr_status(self, mr_iid: str) -> tp.Dict[str, tp.Any]:
        coord = [
            "projects",
            os.environ["CI_PROJECT_ID"],
            "merge_requests",
            mr_iid,
        ]
        api = ApiRequestCommunicator()
        token = os.environ["GITLAB_READ_API"]
        api.headers = {"PRIVATE-TOKEN": token}
        api.base_url = "https://" + os.environ["CI_SERVER_HOST"]
        return api.api_request(*coord)  # type: ignore

    def _triggers_from_str(self, trigger_str: str) -> tp.Sequence[str]:
        if trigger_str[0] not in "+-":
            trigger_str = f"+{trigger_str}"

        triggers = []
        old = 0
        for i, char in enumerate(trigger_str):
            if char in "+-":
                triggers.append(trigger_str[old:i])
                old = i
        triggers.append(trigger_str[old:])
        waste = triggers.pop(0)
        assert waste == ""
        return triggers

    def _get_payload_names(
        self, triggers: tp.Sequence[str], trigger: tp.Optional[_ProtoNamespace] = None
    ) -> tp.Sequence[str]:
        res = []
        for payload_name, _, reason in self._get_payload_names_and_reason(
            triggers, trigger=trigger
        ):
            logger.info("%s included due to %s", payload_name, "".join(reason))
            res.append(payload_name)
        return res

    def _get_payload_names_and_reason(
        self,
        triggers: tp.Sequence[str],
        collect_all: bool = False,
        trigger: tp.Optional[_ProtoNamespace] = None,
    ) -> tp.Sequence[tp.Tuple[str, _ProtoNamespace, tp.Tuple[str, ...]]]:
        payload_names_reason = []
        data = trigger or self.auxe.ci.trigger

        def dig(data: _ProtoNamespace, reason: tp.Tuple[str, ...]) -> None:
            for key, val in data.items():
                if key.startswith("-"):
                    pos_key = key.replace("-", "+")
                    if pos_key not in triggers or collect_all:
                        dig(val, reason + (key,))
                elif key.startswith("+"):
                    if key in triggers or collect_all:
                        dig(val, reason + (key,))
                else:
                    payload_names_reason.append((key, val, reason))

        dig(data, tuple())

        return payload_names_reason

    def _get_trigger_combos(
        self, trigger: tp.Optional[_ProtoNamespace] = None
    ) -> tp.Sequence[tp.Tuple[str, ...]]:
        reasons = set()
        for _, _, reason in self._get_payload_names_and_reason(
            [], collect_all=True, trigger=trigger
        ):
            reasons.add(reason)
        return list(reasons)

    def bake(self) -> None:  # pylint: disable=too-many-branches,too-many-locals
        super().bake()
        data = self.auxe.ci
        base_files = ["00-main.yml", "01-rules.yml"]
        assert data.mechanism == "monolith"

        for filename in base_files:
            self.bake_file(f"CI/{filename}")
