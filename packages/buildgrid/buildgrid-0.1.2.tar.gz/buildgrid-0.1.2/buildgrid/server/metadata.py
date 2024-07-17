# Copyright (C) 2022 Bloomberg LP
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


from contextvars import ContextVar
from typing import Any, Dict, Iterable, Optional, Tuple, Union

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import RequestMetadata, ToolDetails
from buildgrid.server.persistence.sql.models import ClientIdentityEntry
from buildgrid.settings import REQUEST_METADATA_HEADER_NAME, REQUEST_METADATA_TOOL_NAME, REQUEST_METADATA_TOOL_VERSION

ctx_request_metadata: ContextVar[RequestMetadata] = ContextVar(
    "ctx_request_metadata",
    default=RequestMetadata(
        tool_details=ToolDetails(
            tool_name=REQUEST_METADATA_TOOL_NAME,
            tool_version=REQUEST_METADATA_TOOL_VERSION,
        ),
    ),
)


def metadata_list() -> Tuple[Tuple[str, Union[str, bytes]], ...]:
    """Helper function to construct the metadata list from the ContextVar."""
    metadata = ctx_request_metadata.get()
    return ((REQUEST_METADATA_HEADER_NAME, metadata.SerializeToString()),)


ctx_grpc_request_id: ContextVar[Optional[str]] = ContextVar("grpc_request_id", default=None)


def printable_request_metadata(metadata_entries: Any) -> str:
    """Given a metadata object, return a human-readable representation
    of its `RequestMetadata` entry.

    Args:
        metadata_entries: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A string with the metadata contents.
    """
    metadata = extract_request_metadata(metadata_entries)
    return request_metadata_to_string(metadata)


def extract_request_metadata(metadata_entries: Any) -> RequestMetadata:
    """Given a list of string tuples, extract the RequestMetadata
    header values if they are present. If they were not provided,
    returns an empty message.

    Args:
        metadata_entries: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A `RequestMetadata` proto. If the metadata is not defined in the
        request, the message will be empty.
    """
    request_metadata_entry = next(
        (entry for entry in metadata_entries if entry.key == REQUEST_METADATA_HEADER_NAME), None
    )

    request_metadata = RequestMetadata()
    if request_metadata_entry:
        request_metadata.ParseFromString(request_metadata_entry.value)
    return request_metadata


def request_metadata_to_string(request_metadata: RequestMetadata) -> str:
    if request_metadata.tool_details:
        tool_name = request_metadata.tool_details.tool_name
        tool_version = request_metadata.tool_details.tool_version
    else:
        tool_name = tool_version = ""

    return (
        f'tool_name="{tool_name}", tool_version="{tool_version}", '
        f'action_id="{request_metadata.action_id}", '
        f'tool_invocation_id="{request_metadata.tool_invocation_id}", '
        f'correlated_invocations_id="{request_metadata.correlated_invocations_id}"'
    )


def request_metadata_from_scheduler_dict(scheduler_request_metadata: Dict[str, str]) -> RequestMetadata:
    tool_details = ToolDetails()
    tool_details.tool_name = scheduler_request_metadata["tool-name"]
    tool_details.tool_version = scheduler_request_metadata["tool-version"]

    request_metadata = RequestMetadata()
    request_metadata.tool_details.CopyFrom(tool_details)
    request_metadata.tool_invocation_id = scheduler_request_metadata["invocation-id"]
    request_metadata.correlated_invocations_id = scheduler_request_metadata["correlated-invocations-id"]

    return request_metadata


def extract_client_identity(
    instance: str, invocation_metadata: Iterable[Tuple[str, Any]]
) -> Optional[ClientIdentityEntry]:
    """Extract the ClientIdentity from gRPC metadata

    Args:
        invocation_metadata (List[Tuple[str, str]]): grpc metadata

    Returns:
        Optional[ClientIdentityEntry]: identity of the client if exists
    """
    metadata_dict = dict(invocation_metadata)
    workflow = metadata_dict.get("x-request-workflow", None)
    actor = metadata_dict.get("x-request-actor", None)
    subject = metadata_dict.get("x-request-subject", None)

    # None or empty strings are invalid
    if workflow and actor and subject:
        return ClientIdentityEntry(instance=instance, workflow=workflow, actor=actor, subject=subject)

    return None


def printable_client_identity(instance: str, invocation_metadata: Iterable[Tuple[str, Any]]) -> str:
    """Given a metadata object, return a human-readable representation
    of its `ClientIdentity` entry.

    Args:
        instance: REAPI instance name
        invocation_metadata: tuple of entries obtained from a gRPC context
            with, for example, `context.invocation_metadata()`.

    Returns:
        A string with the ClientIdentity contents.
    """
    client_id = extract_client_identity(instance, invocation_metadata)
    return str(client_id)
