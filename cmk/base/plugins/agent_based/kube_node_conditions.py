#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json
from typing import Mapping

from cmk.base.plugins.agent_based.agent_based_api.v1 import register, Result, Service, State
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
)
from cmk.base.plugins.agent_based.utils.kube import NodeConditions


def parse(string_table: StringTable) -> NodeConditions:
    """Parses `string_table` into a NodeConditions instance"""
    return NodeConditions(**json.loads(string_table[0][0]))


def discovery(section: NodeConditions) -> DiscoveryResult:
    yield Service()


def check(params: Mapping[str, int], section: NodeConditions) -> CheckResult:
    if all(cond and cond.is_ok() for _, cond in section):
        details = "\n".join(
            f"{name.upper()}: {cond.status} ({cond.reason}: {cond.detail})"
            for name, cond in section
        )
        yield Result(state=State.OK, summary="Ready, all conditions passed", details=details)
        return
    for name, cond in section:
        state = State.OK
        summary = f"{name.upper()}: {cond.status}"
        details = f"{summary} ({cond.reason}: {cond.detail})"
        if not cond or not cond.is_ok():
            state = State(params[name])
            summary = details
        yield Result(state=state, summary=summary, details=details)


register.agent_section(
    name="kube_node_conditions_v1",
    parsed_section_name="kube_node_conditions",
    parse_function=parse,
)

register.check_plugin(
    name="kube_node_conditions",
    service_name="Condition",
    discovery_function=discovery,
    check_function=check,
    check_default_parameters=dict(
        ready=int(State.CRIT),
        memorypressure=int(State.CRIT),
        diskpressure=int(State.CRIT),
        pidpressure=int(State.CRIT),
        networkunavailable=int(State.CRIT),
    ),
    check_ruleset_name="kube_node_conditions",
)
