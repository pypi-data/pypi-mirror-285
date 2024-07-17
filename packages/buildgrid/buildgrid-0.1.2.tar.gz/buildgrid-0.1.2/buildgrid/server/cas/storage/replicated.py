# Copyright (C) 2024 Bloomberg LP
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
ReplicatedStorage
=========================

A storage provider which stores data in multiple storages, replicating
any data missing in some but present in others.

"""

import logging
from contextlib import ExitStack
from typing import IO, Dict, List, Optional, Set, Tuple

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric
from buildgrid.utils import HashableDigest

from ...decorators import timed
from .storage_abc import StorageABC

LOGGER = logging.getLogger(__name__)


class ReplicatedStorage(StorageABC):
    TYPE = "Replicated"

    def __init__(self, storages: List[StorageABC]) -> None:
        self._stack = ExitStack()
        self._storages = dict(enumerate(storages))

    def start(self) -> None:
        for storage in self._storages.values():
            self._stack.enter_context(storage)

    def stop(self) -> None:
        self._stack.close()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        has_blob: Set[int] = set(i for i in self._storages if self._storages[i].has_blob(digest))
        missing_blob = set(self._storages.keys()) - has_blob
        if len(missing_blob) < len(self._storages):
            publish_counter_metric(METRIC.STORAGE.REPLICATED.REQUIRED_REPLICATION_COUNT, len(missing_blob))
        return len(has_blob) > 0

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        has_blob: Set[int] = set(i for i in self._storages if self._storages[i].has_blob(digest))
        missing_blob = set(self._storages.keys()) - has_blob
        blob = None
        failed_writes = 0
        for idx in has_blob:
            if blob := self._storages[idx].get_blob(digest):
                break
            LOGGER.error(f"Storage #{idx} reported {digest} exists but downloading failed")
            missing_blob.add(idx)
        if len(missing_blob) < len(self._storages):
            assert blob is not None
            for idx in missing_blob:
                try:
                    self._storages[idx].commit_write(digest, blob)
                    LOGGER.debug(f"Replicated {digest.hash}/{digest.size_bytes} to storage #{idx}")
                except Exception as e:
                    LOGGER.warning(f"Failed to replicate {digest.hash}/{digest.size_bytes} to storage #{idx}: {e}")
                    failed_writes += 1
                blob.seek(0)

            publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, failed_writes)
            publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_COUNT, len(missing_blob) - failed_writes)
        return blob

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        for storage in self._storages.values():
            storage.delete_blob(digest)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        failed_writes = 0
        error_msgs: List[str] = []
        for idx, storage in self._storages.items():
            try:
                storage.commit_write(digest, write_session)
            except Exception as error:
                LOGGER.warning(f"Failed to write {digest.hash}/{digest.size_bytes} to storage #{idx}: {error}")
                error_msgs.append(str(error))
                failed_writes += 1
            write_session.seek(0)

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, failed_writes)
        if failed_writes == len(self._storages):
            error_string = "Writes to all storages failed with the following errors:\n"
            error_string += "\n".join(error_msgs)
            LOGGER.error(error_string)
            raise RuntimeError(error_string)

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: List[Digest]) -> List[str]:
        failed_deletions_set: Set[str] = set()
        for storage in self._storages.values():
            failed_deletions_set.union(storage.bulk_delete(digests))
        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(failed_deletions_set), type=self.TYPE)
        return list(failed_deletions_set)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: List[Digest]) -> List[Digest]:
        """Call missing_blobs on each storage and only report a blob is missing if it's in none of the
        storages. The number of blobs missing from a storage but present in others is logged and published
        as a metric
        """
        digest_set: Set[HashableDigest] = {HashableDigest(digest.hash, digest.size_bytes) for digest in digests}
        missing_from_all_storages = digest_set.copy()
        missing_for_storage: Dict[int, Set[HashableDigest]] = {}

        blobs_needing_replication_count = 0
        for idx, storage in self._storages.items():
            response = storage.missing_blobs(digests)
            missing_for_storage[idx] = {HashableDigest(digest.hash, digest.size_bytes) for digest in response}

        missing_from_all_storages = set.intersection(*missing_for_storage.values())
        digests_in_at_least_one_storage: Set[HashableDigest] = digest_set - missing_from_all_storages
        # Figure out what blobs are present in some storages but not all to report metrics
        for idx, missing_digests in missing_for_storage.items():
            inconsistent_digests_for_storage = missing_digests & digests_in_at_least_one_storage
            if inconsistent_digests_for_storage:
                LOGGER.info(
                    f"Storage #{idx} has {len(inconsistent_digests_for_storage)} blobs which need to be replicated"
                )
                blobs_needing_replication_count += len(inconsistent_digests_for_storage)

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REQUIRED_REPLICATION_COUNT, blobs_needing_replication_count)
        missing_blobs_list = [hdigest.to_digest() for hdigest in missing_from_all_storages]
        return missing_blobs_list

    # Bulk write to all storages. Errors are not fatal as long as one storage is
    # successfully written to
    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: List[Tuple[Digest, bytes]]) -> List[Status]:
        digest_result: Dict[HashableDigest, Status] = {}
        errored_blobs_total = 0
        for idx, storage in self._storages.items():
            errored_blobs_for_storage = 0
            results = storage.bulk_update_blobs(blobs)
            for digest_blob_tuple, result in zip(blobs, results):
                digest, _ = digest_blob_tuple
                hdigest = HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes)

                if result.code != code_pb2.OK:
                    errored_blobs_for_storage += 1

                # Keep track of the status code for this digest, preferring OK over errors
                if hdigest not in digest_result or digest_result[hdigest].code != code_pb2.OK:
                    digest_result[hdigest] = result

            if errored_blobs_for_storage > 0:
                LOGGER.warning(f"Failed to write {errored_blobs_for_storage}/{len(results)} digests to storage #{idx}")
                errored_blobs_total += errored_blobs_for_storage

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, errored_blobs_total)
        return [digest_result[hdigest] for hdigest in digest_result]

    # Read blobs from all storages, writing any missing blobs into storages missing
    # them from storages that have them
    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        digest_set = set(HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes) for digest in digests)
        missing_blobs: Dict[int, Set[HashableDigest]] = {}
        bulk_read_results: Dict[str, bytes] = {}
        # Find what blobs are missing for this storage and read what's available
        for idx, storage in self._storages.items():
            missing_blobs[idx] = set(
                [
                    HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes)
                    for digest in storage.missing_blobs(digests)
                ]
            )
            present_blobs = digest_set - missing_blobs[idx]
            blobs_to_read = [x.to_digest() for x in present_blobs if x.hash not in bulk_read_results]
            bulk_read_results.update(self._storages[idx].bulk_read_blobs(blobs_to_read))

        replicated_blobs_count = 0
        errored_blobs_count = 0
        for idx, missing in missing_blobs.items():
            # Write any blobs that exist in other storages which are missing from this storage
            write_batch: List[Tuple[Digest, bytes]] = []
            for digest in missing:
                if digest.hash in bulk_read_results:
                    write_batch.append((digest.to_digest(), bulk_read_results[digest.hash]))
            if write_batch:
                update_results = self._storages[idx].bulk_update_blobs(write_batch)
                for result in update_results:
                    if result.code != code_pb2.OK:
                        errored_blobs_count += 1
                    else:
                        replicated_blobs_count += 1
                LOGGER.debug(f"Replicated {len(write_batch)} blobs to storage #{idx}")

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_COUNT, replicated_blobs_count)
        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, errored_blobs_count)
        return bulk_read_results
