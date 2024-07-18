# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import annotations
from typing import *
from .options.TargetCounterModelOptions import TargetCounterModelOptions
from .enum.TargetCounterModelResetType import TargetCounterModelResetType


class TargetCounterModel:
    counter_name: str
    value: int
    reset_type: Optional[TargetCounterModelResetType] = None

    def __init__(
        self,
        counter_name: str,
        value: int,
        options: Optional[TargetCounterModelOptions] = TargetCounterModelOptions(),
    ):
        self.counter_name = counter_name
        self.value = value
        self.reset_type = options.reset_type if options.reset_type else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.counter_name is not None:
            properties["counterName"] = self.counter_name
        if self.reset_type is not None:
            properties["resetType"] = self.reset_type.value
        if self.value is not None:
            properties["value"] = self.value

        return properties
