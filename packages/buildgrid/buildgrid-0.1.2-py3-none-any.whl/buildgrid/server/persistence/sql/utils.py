# Copyright (C) 2020 Bloomberg LP
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

""" Holds constants and utility functions for the SQL scheduler. """


import operator
from datetime import datetime
from typing import Any, Dict, List, Tuple, cast

from sqlalchemy.sql.expression import ClauseElement, and_, or_
from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.sql.schema import Column

from buildgrid._exceptions import InvalidArgumentError
from buildgrid.server.operations.filtering import OperationFilter, SortKey
from buildgrid.server.persistence.sql.models import JobEntry, OperationEntry, PlatformEntry

DATETIME_FORMAT = "%Y-%m-%d-%H-%M-%S-%f"


LIST_OPERATIONS_PARAMETER_MODEL_MAP = cast(
    Dict[str, Column[Any]],
    {
        "stage": JobEntry.stage,
        "name": OperationEntry.name,
        "queued_time": JobEntry.queued_timestamp,
        "start_time": JobEntry.worker_start_timestamp,
        "completed_time": JobEntry.worker_completed_timestamp,
        "invocation_id": OperationEntry.invocation_id,
        "correlated_invocations_id": OperationEntry.correlated_invocations_id,
        "tool_name": OperationEntry.tool_name,
        "tool_version": OperationEntry.tool_version,
        "action_digest": JobEntry.action_digest,
        "command": JobEntry.command,
        "platform": PlatformEntry.key,
        "platform-value": PlatformEntry.value,
    },
)


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val}")


def parse_list_operations_sort_value(value: str, column: Column[Any]) -> Any:
    """Convert the string representation of a value to the proper Python type."""
    python_type = column.property.columns[0].type.python_type
    if python_type == datetime:
        return datetime.strptime(value, DATETIME_FORMAT)
    elif python_type == bool:
        # Using this distutils function to cover a few different bool representations
        return strtobool(value)
    else:
        return python_type(value)


def dump_list_operations_token_value(token_value: Any) -> str:
    """Convert a value to a string for use in the page_token."""
    if isinstance(token_value, datetime):
        return datetime.strftime(token_value, DATETIME_FORMAT)
    else:
        return str(token_value)


def build_pagination_clause_for_sort_key(
    sort_value: Any, previous_sort_values: List[Any], sort_keys: List[SortKey]
) -> ClauseElement:
    """Build part of a filter clause to figure out the starting point of the page given
    by the page_token. See the docstring of build_page_filter for more details."""
    if len(sort_keys) <= len(previous_sort_values):
        raise ValueError("Not enough keys to unpack")

    filter_clause_list = []
    for i, previous_sort_value in enumerate(previous_sort_values):
        previous_sort_col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_keys[i].name]
        filter_clause_list.append(previous_sort_col == previous_sort_value)
    sort_key = sort_keys[len(previous_sort_values)]
    sort_col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
    if sort_key.descending:
        filter_clause_list.append(sort_col < sort_value)
    else:
        filter_clause_list.append(sort_col > sort_value)
    return and_(*filter_clause_list)


def build_page_filter(page_token: str, sort_keys: List[SortKey]) -> ClauseElement:
    """Build a filter to determine the starting point of the rows to fetch, based
    on the page_token.

    The page_token is directly related to the sort order, and in this way it acts as a
    "cursor." It is given in the format Xval|Yval|Zval|..., where each element is a value
    corresponding to an orderable column in the database. If the corresponding rows are
    X, Y, and Z, then X is the primary sort key, with Y breaking ties between X, and Z
    breaking ties between X and Y. The corresponding filter clause is then:

    (X > Xval) OR (X == XVal AND Y > Yval) OR (X == Xval AND Y == Yval AND Z > Zval) ...
    """
    # The page token is used as a "cursor" to determine the starting point
    # of the rows to fetch. It is derived from the sort keys.
    token_elements = page_token.split("|")
    if len(token_elements) != len(sort_keys):
        # It is possible that an extra "|" was in the input
        # TODO: Handle extra "|"s somehow? Or at least allow escaping them
        raise InvalidArgumentError(
            f'Wrong number of "|"-separated elements in page token [{page_token}]. '
            f"Expected {len(sort_keys)}, got {len(token_elements)}."
        )

    sort_key_clause_list = []
    previous_sort_values: List[Any] = []
    # Build the compound clause for each sort key in the token
    for i, sort_key in enumerate(sort_keys):
        col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
        sort_value = parse_list_operations_sort_value(token_elements[i], col)
        filter_clause = build_pagination_clause_for_sort_key(sort_value, previous_sort_values, sort_keys)
        sort_key_clause_list.append(filter_clause)
        previous_sort_values.append(sort_value)

    return or_(*sort_key_clause_list)


def build_page_token(operation: Column[Any], sort_keys: List[SortKey]) -> str:
    """Use the sort keys to build a page token from the given operation."""
    token_values = []
    for sort_key in sort_keys:
        col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
        col_properties = col.property.columns[0]
        column_name = col_properties.name
        table_name = col_properties.table.name
        if table_name == "operations":
            token_value = getattr(operation, column_name)
        elif table_name == "jobs":
            token_value = getattr(operation.job, column_name)
        else:
            raise ValueError("Got invalid table f{table_name} for sort key {sort_key.name} while building page_token")

        token_values.append(dump_list_operations_token_value(token_value))

    next_page_token = "|".join(token_values)
    return next_page_token


def extract_sort_keys(operation_filters: List[OperationFilter]) -> Tuple[List[SortKey], List[OperationFilter]]:
    """Splits the operation filters into sort keys and non-sort filters, returning both as
    separate lists.

    Sort keys are specified with the "sort_order" parameter in the filter string. Multiple
    "sort_order"s can appear in the filter string, and all are extracted and returned."""
    sort_keys = []
    non_sort_filters = []
    for op_filter in operation_filters:
        if op_filter.parameter == "sort_order":
            if op_filter.operator != operator.eq:
                raise InvalidArgumentError('sort_order must be specified with the "=" operator.')
            sort_keys.append(op_filter.value)
        else:
            non_sort_filters.append(op_filter)

    return sort_keys, non_sort_filters


def build_sort_column_list(sort_keys: List[SortKey]) -> List["ColumnOperators[Any]"]:
    """Convert the list of sort keys into a list of columns that can be
    passed to an order_by.

    This function checks the sort keys to ensure that they are in the
    parameter-model map and raises an InvalidArgumentError if they are not."""
    sort_columns: List["ColumnOperators[Any]"] = []
    for sort_key in sort_keys:
        try:
            col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
            if sort_key.descending:
                sort_columns.append(col.desc())
            else:
                sort_columns.append(col.asc())
        except KeyError:
            raise InvalidArgumentError(f"[{sort_key.name}] is not a valid sort key.")
    return sort_columns


def convert_filter_to_sql_filter(operation_filter: OperationFilter) -> ClauseElement:
    """Convert the internal representation of a filter to a representation that SQLAlchemy
    can understand. The return type is a "ColumnElement," per the end of this section in
    the SQLAlchemy docs: https://docs.sqlalchemy.org/en/13/core/tutorial.html#selecting-specific-columns

    This function assumes that the parser has appropriately converted the filter
    value to a Python type that can be compared to the parameter."""
    try:
        param = LIST_OPERATIONS_PARAMETER_MODEL_MAP[operation_filter.parameter]
    except KeyError:
        raise InvalidArgumentError(f"Invalid parameter: [{operation_filter.parameter}]")

    if operation_filter.parameter == "command":
        if operation_filter.operator == operator.eq:
            return param.like(f"%{operation_filter.value}%")
        elif operation_filter.operator == operator.ne:
            return param.notlike(f"%{operation_filter.value}%")  # type: ignore[no-any-return]

    if operation_filter.parameter == "platform":
        key, value = operation_filter.value.split(":", 1)
        value_column = LIST_OPERATIONS_PARAMETER_MODEL_MAP["platform-value"]
        return and_(param == key, operation_filter.operator(value_column, value))

    # Better type? Returning Any from function declared to return "ClauseElement"
    return operation_filter.operator(param, operation_filter.value)  # type: ignore[no-any-return]


def build_custom_filters(operation_filters: List[OperationFilter]) -> List[ClauseElement]:
    return [
        convert_filter_to_sql_filter(operation_filter)
        for operation_filter in operation_filters
        if operation_filter.parameter != "platform"
    ]
