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


import hashlib
import json
import os
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from operator import attrgetter
from typing import (
    IO,
    AnyStr,
    BinaryIO,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from urllib.parse import urljoin

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid.settings import BROWSER_URL_FORMAT, HASH, HASH_LENGTH

T = TypeVar("T")


secure_uri_schemes = ["https", "grpcs"]
insecure_uri_schemes = ["http", "grpc"]


class BrowserURL:
    __url_markers = (
        "%(instance)s",
        "%(type)s",
        "%(hash)s",
        "%(sizebytes)s",
    )

    def __init__(self, base_url: str, instance_name: Optional[str] = None) -> None:
        """Begins browser URL helper initialization."""
        self.__base_url = base_url
        self.__initialized = False
        self.__url_spec = {
            "%(instance)s": instance_name or "",
        }

    def for_message(self, message_type: str, message_digest: Digest) -> bool:
        """Completes browser URL initialization for a protobuf message."""
        if self.__initialized:
            return False

        self.__url_spec["%(type)s"] = message_type
        self.__url_spec["%(hash)s"] = message_digest.hash
        self.__url_spec["%(sizebytes)s"] = str(message_digest.size_bytes)

        self.__initialized = True
        return True

    def generate(self) -> Optional[Union[str, bytes]]:
        """Generates a browser URL string."""
        if not self.__base_url or not self.__initialized:
            return None

        url_tail = BROWSER_URL_FORMAT

        for url_marker in self.__url_markers:
            if url_marker not in self.__url_spec:
                return None
            if url_marker not in url_tail:
                continue
            url_tail = url_tail.replace(url_marker, self.__url_spec[url_marker])

        return urljoin(self.__base_url, url_tail)


@dataclass(frozen=True)
class HashableDigest:
    hash: str
    size_bytes: int

    def to_digest(self) -> Digest:
        return Digest(hash=self.hash, size_bytes=self.size_bytes)


def get_hash_type() -> "remote_execution_pb2.DigestFunction.Value.ValueType":
    """Returns the hash type."""
    hash_name = HASH().name
    if hash_name == "sha256":
        return remote_execution_pb2.DigestFunction.SHA256
    return remote_execution_pb2.DigestFunction.UNKNOWN


def create_digest(bytes_to_digest: bytes) -> remote_execution_pb2.Digest:
    """Computes the :obj:`Digest` of a piece of data.

    The :obj:`Digest` of a data is a function of its hash **and** size.

    Args:
        bytes_to_digest (bytes): byte data to digest.

    Returns:
        :obj:`Digest`: The :obj:`Digest` for the given byte data.
    """
    return remote_execution_pb2.Digest(hash=HASH(bytes_to_digest).hexdigest(), size_bytes=len(bytes_to_digest))


def create_digest_from_file(file_obj: BinaryIO) -> remote_execution_pb2.Digest:
    """Computed the :obj:`Digest` of a file-like object.

    The :obj:`Digest` contains a hash of the file's contents and the size of
    those contents. This function only reads the content in chunks for hashing,
    so is safe to use on large files.

    Args:
        file_obj (BinaryIO): A file-like object of some kind.

    Returns:
        :obj:`Digest`: The :obj:`Digest` for the given file object.
    """
    digest = remote_execution_pb2.Digest()

    # Make sure we're hashing from the start of the file
    file_obj.seek(0)

    # Generate the file hash and keep track of the file size
    hasher = HASH()
    digest.size_bytes = 0
    for block in iter(partial(file_obj.read, 8192), b""):
        hasher.update(block)
        digest.size_bytes += len(block)
    digest.hash = hasher.hexdigest()

    # Return to the start of the file ready for future reads
    file_obj.seek(0)
    return digest


def parse_digest(digest_string: str) -> Optional[remote_execution_pb2.Digest]:
    """Creates a :obj:`Digest` from a digest string.

    A digest string should alway be: ``{hash}/{size_bytes}``.

    Args:
        digest_string (str): the digest string.

    Returns:
        :obj:`Digest`: The :obj:`Digest` read from the string or None if
            `digest_string` is not a valid digest string.
    """
    digest_hash, digest_size = digest_string.split("/")

    if len(digest_hash) == HASH_LENGTH and digest_size.isdigit():
        return remote_execution_pb2.Digest(hash=digest_hash, size_bytes=int(digest_size))

    return None


def validate_digest_data(digest: remote_execution_pb2.Digest, data: bytes) -> bool:
    """Validate that the given digest corresponds to the given data."""
    return len(data) == digest.size_bytes and HASH(data).hexdigest() == digest.hash


def read_file(file_path: str) -> bytes:
    """Loads raw file content in memory.

    Args:
        file_path (str): path to the target file.

    Returns:
        bytes: Raw file's content until EOF.

    Raises:
        OSError: If `file_path` does not exist or is not readable.
    """
    with open(file_path, "rb") as byte_file:
        return byte_file.read()


def read_and_rewind(read_head: IO[AnyStr]) -> Optional[AnyStr]:
    """Reads from an IO object and returns the data found there
    after rewinding the object to the beginning.

    Args:
        read_head (IO): readable IO head

    Returns:
        AnyStr: readable content from `read_head`.
    """
    if not read_head:
        return None

    data = read_head.read()
    read_head.seek(0)
    return data


def merkle_tree_maker(
    directory_path: str,
) -> Iterator[Tuple[Union[remote_execution_pb2.FileNode, remote_execution_pb2.DirectoryNode], BinaryIO, str]]:
    """Walks a local folder tree, generating :obj:`FileNode` and
    :obj:`DirectoryNode`.

    Args:
        directory_path (str): absolute or relative path to a local directory.

    Yields:
        :obj:`Message`, bytes, str: a tutple of either a :obj:`FileNode` or
        :obj:`DirectoryNode` message, the corresponding blob and the
        corresponding node path.
    """
    directory_name = os.path.basename(directory_path)

    # Actual generator, yields recursively FileNodes and DirectoryNodes:
    def __merkle_tree_maker(directory_path: str, directory_name: str) -> Generator[
        Tuple[Union[remote_execution_pb2.FileNode, remote_execution_pb2.DirectoryNode], BinaryIO, str],
        None,
        Tuple[Union[remote_execution_pb2.FileNode, remote_execution_pb2.DirectoryNode], BinaryIO, str],
    ]:
        if not os.path.isabs(directory_path):
            directory_path = os.path.abspath(directory_path)

        directory = remote_execution_pb2.Directory()

        files, directories, symlinks = [], [], []
        for directory_entry in os.scandir(directory_path):
            node_name, node_path = directory_entry.name, directory_entry.path

            node: Union[remote_execution_pb2.FileNode, remote_execution_pb2.DirectoryNode]
            node_blob: BinaryIO
            if directory_entry.is_file(follow_symlinks=False):
                with open(directory_entry.path, "rb") as node_blob:
                    node_digest = create_digest_from_file(node_blob)

                    node = remote_execution_pb2.FileNode()
                    node.name = node_name
                    node.digest.CopyFrom(node_digest)
                    node.is_executable = os.access(node_path, os.X_OK)

                    files.append(node)

                    yield node, node_blob, node_path

            elif directory_entry.is_dir(follow_symlinks=False):
                node, node_blob, _ = yield from __merkle_tree_maker(node_path, node_name)

                directories.append(cast(remote_execution_pb2.DirectoryNode, node))

                yield node, node_blob, node_path

            # Create a SymlinkNode;
            elif os.path.islink(directory_entry.path):
                node_target = os.readlink(directory_entry.path)

                symlink_node = remote_execution_pb2.SymlinkNode()
                symlink_node.name = directory_entry.name
                symlink_node.target = node_target

                symlinks.append(symlink_node)

        files.sort(key=attrgetter("name"))
        directories.sort(key=attrgetter("name"))
        symlinks.sort(key=attrgetter("name"))

        directory.files.extend(files)
        directory.directories.extend(directories)
        directory.symlinks.extend(symlinks)

        node_data = directory.SerializeToString()
        node_digest = create_digest(node_data)

        dir_node = remote_execution_pb2.DirectoryNode()
        dir_node.name = directory_name
        dir_node.digest.CopyFrom(node_digest)

        return dir_node, BytesIO(node_data), directory_path

    node, node_blob, node_path = yield from __merkle_tree_maker(directory_path, directory_name)

    yield node, node_blob, node_path


def convert_values_to_sorted_lists(
    dictionary: Mapping[str, Union[str, Sequence[str], Set[str]]]
) -> Dict[str, List[str]]:
    """Given a dictionary, do the following:

    1. Turn strings into singleton lists
    2. Turn all other sequence types into sorted lists with list()

    This returns the converted dictionary and does not change the dictionary
    that was passed in.

    """
    normalized: Dict[str, List[str]] = {}
    for key, value in dictionary.items():
        if isinstance(value, str):
            normalized[key] = [value]
        else:
            try:
                normalized[key] = sorted(list(value))
            except TypeError:
                raise ValueError(f"{value} cannot be sorted")
    return normalized


def hash_from_dict(dictionary: Mapping[str, List[str]]) -> str:
    """Get the hash represntation of a dictionary"""
    return hashlib.sha1(json.dumps(dictionary, sort_keys=True).encode()).hexdigest()


def get_unique_objects_by_attribute(objects: Sequence[T], attribute: str) -> Iterable[T]:
    """Return a list of unique objects based on a hashable attribute or chained attributes.

    Note that this does not provide any sanitization, and any problematic elements will
    only raise exceptions when iterated on."""

    attrs_seen = set()

    for obj in objects:
        if obj:
            attr_value = attrgetter(attribute)(obj)
            if attr_value not in attrs_seen:
                attrs_seen.add(attr_value)
                yield obj


def retry_delay(retry_attempt: int, delay_base: int = 1) -> float:
    attempt = min(5, retry_attempt)  # Limit the delay to ~10.5x the base time
    return round(delay_base * (1.6**attempt), 1)


def flatten_capabilities(capabilities: Mapping[str, Union[Set[str], List[str]]]) -> List[Tuple[str, str]]:
    """Flatten a capabilities dictionary.

    This method takes a capabilities dictionary and flattens it into a
    list of key/value tuples describing all the platform properties
    that the capabilities map to. To do this, it assumes that all of the
    dictionary's values are iterable.

    For example,

        ``{'OSFamily': {'Linux'}, 'ISA': {'x86-32', 'x86-64'}}``

    becomes

        ``[('OSFamily', 'Linux'), ('ISA', 'x86-32'), ('ISA', 'x86-64')]``

    Args:
        capabilities (dict): The capabilities dictionary to flatten.

    Returns:
        list containing the flattened dictionary key-value tuples.

    """
    return [(name, value) for name, value_list in capabilities.items() for value in value_list]
