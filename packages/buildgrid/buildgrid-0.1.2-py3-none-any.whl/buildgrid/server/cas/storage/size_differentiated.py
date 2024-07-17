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


"""
SizeDifferentiatedStorage
=========================

A storage provider which passes requests to other storage providers
based on the size of the blob being requested.

"""

import logging
from collections import defaultdict
from contextlib import ExitStack
from typing import IO, Callable, Dict, Iterable, Iterator, List, NamedTuple, Optional, Tuple, TypedDict, TypeVar

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status

from ...decorators import timed
from ...metrics_names import METRIC
from ...metrics_utils import publish_counter_metric
from ...threading import ContextThreadPoolExecutor
from .storage_abc import StorageABC

LOGGER = logging.getLogger(__name__)


class SizeLimitedStorageType(TypedDict):
    max_size: int
    storage: StorageABC


# NOTE: This exists separately to the TypedDict to allow attribute-based access
# at runtime, rather than relying on string-based access to dictionary keys.
class _SizeLimitedStorage(NamedTuple):
    max_size: int
    storage: StorageABC


_T = TypeVar("_T")
_R = TypeVar("_R")


# wrapper functions for the bulk StorageABC interfaces
def _bulk_delete_for_storage(storage_digests: Tuple[StorageABC, List[Digest]]) -> List[str]:
    storage, digests = storage_digests
    return storage.bulk_delete(digests)


def _fmb_for_storage(storage_digests: Tuple[StorageABC, List[Digest]]) -> List[Digest]:
    storage, digests = storage_digests
    return storage.missing_blobs(digests)


def _bulk_update_for_storage(
    storage_digests: Tuple[StorageABC, List[Tuple[Digest, bytes]]]
) -> Tuple[StorageABC, List[Status]]:
    storage, digest_tuples = storage_digests
    return storage, storage.bulk_update_blobs(digest_tuples)


def _bulk_read_for_storage(storage_digests: Tuple[StorageABC, List[Digest]]) -> Dict[str, bytes]:
    storage, digests = storage_digests
    return storage.bulk_read_blobs(digests)


class SizeDifferentiatedStorage(StorageABC):
    TYPE = "SizeDifferentiated"

    def __init__(
        self, storages: List[SizeLimitedStorageType], fallback: StorageABC, thread_pool_size: Optional[int] = None
    ) -> None:
        self._stack = ExitStack()
        self._fallback_storage = fallback
        self._storages = [_SizeLimitedStorage(**storage) for storage in storages]
        self._storages.sort(key=lambda storage: storage.max_size)
        self._threadpool: Optional[ContextThreadPoolExecutor] = None
        if thread_pool_size:
            self._threadpool = ContextThreadPoolExecutor(thread_pool_size, "size-differentiated-storage")

    def _storage_from_digest(self, digest: Digest) -> StorageABC:
        for storage in self._storages:
            if digest.size_bytes < storage.max_size:
                return storage.storage
        # If the blob is too big for any of the size-limited storages,
        # put it in the fallback.
        return self._fallback_storage

    def _partition_digests(self, digests: List[Digest]) -> Dict[StorageABC, List[Digest]]:
        partition: Dict[StorageABC, List[Digest]] = defaultdict(list)
        for digest in digests:
            storage = self._storage_from_digest(digest)
            partition[storage].append(digest)
        return partition

    def _map(self, fn: Callable[[_T], _R], args: Iterable[_T]) -> Iterator[_R]:
        if self._threadpool:
            return self._threadpool.map(fn, args)
        else:
            return map(fn, args)

    def start(self) -> None:
        if self._threadpool:
            self._stack.enter_context(self._threadpool)
        for storage_tuple in self._storages:
            self._stack.enter_context(storage_tuple.storage)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info(f"Stopped {type(self).__name__}")

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug(f"Checking for blob: [{digest}]")
        storage = self._storage_from_digest(digest)
        return storage.has_blob(digest)

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        LOGGER.debug(f"Getting blob: [{digest}]")
        storage = self._storage_from_digest(digest)
        return storage.get_blob(digest)

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug(f"Deleting blob: [{digest}]")
        storage = self._storage_from_digest(digest)
        storage.delete_blob(digest)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug(f"Writing blob: [{digest}]")
        storage = self._storage_from_digest(digest)
        storage.commit_write(digest, write_session)

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: List[Digest]) -> List[str]:
        failed_deletions: List[str] = []
        for result in self._map(_bulk_delete_for_storage, self._partition_digests(digests).items()):
            failed_deletions.extend(result)

        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(failed_deletions), type=self.TYPE)
        return failed_deletions

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: List[Digest]) -> List[Digest]:
        missing_blobs: List[Digest] = []

        for result in self._map(_fmb_for_storage, self._partition_digests(digests).items()):
            missing_blobs.extend(result)

        return missing_blobs

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: List[Tuple[Digest, bytes]]) -> List[Status]:
        partitioned_digests: Dict[StorageABC, List[Tuple[Digest, bytes]]] = defaultdict(list)
        idx_map: Dict[StorageABC, List[int]] = defaultdict(list)
        for orig_idx, digest_tuple in enumerate(blobs):
            storage = self._storage_from_digest(digest_tuple[0])
            partitioned_digests[storage].append(digest_tuple)
            idx_map[storage].append(orig_idx)

        results: List[Status] = [Status(code=code_pb2.INTERNAL, message="inconsistent batch results")] * len(blobs)
        for storage, statuses in self._map(_bulk_update_for_storage, partitioned_digests.items()):
            for status_idx, status in enumerate(statuses):
                results[idx_map[storage][status_idx]] = status
        return results

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        bulk_read_results: Dict[str, bytes] = {}
        for result in self._map(_bulk_read_for_storage, self._partition_digests(digests).items()):
            bulk_read_results.update(result)

        return bulk_read_results
