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
LRUMemoryCache
==================

A storage provider that stores data in memory. When the size limit
is reached, items are deleted from the cache with the least recently
used item being deleted first.
"""

import collections
import io
import logging
import threading
from typing import IO, Any, Optional, Tuple

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest

from ...decorators import timed
from ...metrics_names import METRIC
from .storage_abc import StorageABC

LOGGER = logging.getLogger(__name__)


class _NullBytesIO(io.BufferedIOBase):
    """A file-like object that discards all data written to it."""

    def writable(self) -> bool:
        return True

    # TODO how to type an override here? __buffer: bytes | bytearray | memoryview | array | mmap
    def write(self, b: Any) -> int:
        return len(b)


class LRUMemoryCache(StorageABC):
    TYPE = "LRU"

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._storage: "collections.OrderedDict[Tuple[str, int], bytes]" = collections.OrderedDict()
        self._bytes_stored = 0
        self._lock = threading.Lock()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug(f"Checking for blob: [{digest}]")
        with self._lock:
            key = (digest.hash, digest.size_bytes)
            result = key in self._storage
            if result:
                self._storage.move_to_end(key)
            return result

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        LOGGER.debug(f"Getting blob: [{digest}]")
        with self._lock:
            key = (digest.hash, digest.size_bytes)
            if key in self._storage:
                self._storage.move_to_end(key)
                return io.BytesIO(self._storage[key])
            return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug(f"Deleting blob: [{digest}]")
        key = (digest.hash, digest.size_bytes)
        with self._lock:
            deleted_blob = self._storage.pop(key, None)
            if deleted_blob:
                self._bytes_stored -= digest.size_bytes

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug(f"Writing blob: [{digest}]")
        if digest.size_bytes > self._limit:
            # We can't cache this object, so return without doing anything.
            return
        with self._lock:
            key = (digest.hash, digest.size_bytes)
            if key in self._storage:
                # Digest already in cache, mark it as recently used
                self._storage.move_to_end(key)
                return

            size_after_write = self._bytes_stored + digest.size_bytes
            if size_after_write > self._limit:
                # Delete stuff until there's enough space to write this blob
                LOGGER.debug(
                    f"LRU cleanup triggered. current_size=[{self._bytes_stored}], "
                    f"limit=[{self._limit}], additional_bytes=[{digest.size_bytes}"
                )
                while size_after_write > self._limit:
                    deleted_key = self._storage.popitem(last=False)[0]
                    self._bytes_stored -= deleted_key[1]
                    size_after_write -= deleted_key[1]
                LOGGER.debug(f"LRU cleanup finished, current_size=[{self._bytes_stored}]")
            elif size_after_write < 0:
                # This should never happen
                LOGGER.error(
                    f"Overflow: writing a additional_bytes=[{digest.size_bytes}] "
                    f"causes the current_size=[{self._bytes_stored}] to become "
                    f"size_after_write=[{size_after_write}]"
                )
                raise OverflowError()

            write_session.seek(0)
            self._storage[key] = write_session.read()
            self._bytes_stored += digest.size_bytes
