# Copyright 2024 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
from __future__ import annotations

from functools import partial
from typing import Callable

from qctrlworkflowclient import core_workflow
from qctrlworkflowclient.router.api import DecodedResult

from boulderopal._configuration.configuration import (
    get_configuration,
    in_local_mode,
    is_async,
)
from boulderopal._core.formatter import (
    metadata_formatter,
    metadata_local_formatter,
)


def _formatter(
    result: DecodedResult | dict,
    formatters: tuple[Callable[[DecodedResult], DecodedResult], ...] = (
        metadata_formatter,
    ),
) -> dict:
    if result is None or (isinstance(result, DecodedResult) and result.decoded is None):
        raise RuntimeError("All workflow function should return a non-nullable result.")
    if in_local_mode():
        return metadata_local_formatter(result)
    if is_async(result):
        return result
    for _func in formatters:
        result = _func(result)
    assert isinstance(result, DecodedResult)
    return result.decoded


boulder_opal_workflow = partial(core_workflow, get_configuration, formatter=_formatter)
