# Copyright (C) 2018 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Execution Controller
====================

An instance of the Execution controller.

All this stuff you need to make the execution service work.

Contains scheduler, execution instance, an interface to the bots
and an operations instance.
"""
from typing import Iterable, Optional

from .._enums import ServiceName
from ..settings import DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE
from .bots.instance import BotsInterface
from .execution.instance import ExecutionInstance
from .operations.instance import OperationsInstance
from .persistence.sql.impl import SQLDataStore


class ExecutionController:
    def __init__(
        self,
        scheduler: SQLDataStore,
        *,
        operation_stream_keepalive_timeout: Optional[int] = None,
        services: Iterable[str] = ServiceName.default_services(),
        max_list_operations_page_size: int = DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
    ) -> None:
        self.execution_instance: Optional[ExecutionInstance] = None
        if ServiceName.EXECUTION.value in services:
            self.execution_instance = ExecutionInstance(scheduler, operation_stream_keepalive_timeout)

        self.operations_instance: Optional[OperationsInstance] = None
        if ServiceName.OPERATIONS.value in services:
            self.operations_instance = OperationsInstance(scheduler, max_list_operations_page_size)

        self.bots_interface: Optional[BotsInterface] = None
        if ServiceName.BOTS.value in services:
            self.bots_interface = BotsInterface(scheduler)
