# Copyright (C) 2019 Bloomberg LP
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
RedisStorage
==================

A storage provider that stores data in a persistent redis store.
https://redis.io/

Redis client: redis-py
https://github.com/andymccurdy/redis-py

"""
import functools
import io
import logging
from typing import IO, Any, Callable, Dict, List, Optional, Tuple, TypeVar, cast

import redis

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.redis.provider import RedisProvider
from buildgrid.settings import HASH

from ...decorators import timed
from ...metrics_names import METRIC
from .storage_abc import StorageABC

LOGGER = logging.getLogger(__name__)

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def redis_client_exception_wrapper(func: Func) -> Func:
    """Wrapper from handling redis client exceptions."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except redis.RedisError:
            LOGGER.exception(f"Redis Exception in [{func.__name__}]")
            raise RuntimeError

    return cast(Func, wrapper)


class RedisStorage(StorageABC):
    """Interface for communicating with a redis store."""

    TYPE = "Redis"

    @redis_client_exception_wrapper
    def __init__(self, redis: RedisProvider) -> None:
        self._redis = redis

    def _construct_key(self, digest: Digest) -> str:
        """Helper to get the redis key name for a particular digest"""
        return digest.hash + "_" + str(digest.size_bytes)

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug(f"Checking for blob: [{digest}]")
        return bool(self._redis.execute_ro(lambda r: r.exists(self._construct_key(digest))))

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        LOGGER.debug(f"Getting blob: [{digest}]")
        blob = self._redis.execute_ro(lambda r: r.get(self._construct_key(digest)))
        return None if blob is None else io.BytesIO(blob)

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug(f"Deleting blob: [{digest}]")
        self._redis.execute_rw(lambda r: r.delete(self._construct_key(digest)))

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug(f"Writing blob: [{digest}]")
        write_session.seek(0)
        self._redis.execute_rw(lambda r: r.set(self._construct_key(digest), write_session.read()))

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def missing_blobs(self, digests: List[Digest]) -> List[Digest]:
        # Exist takes multiple keys, but only returns the number of keys which
        # exist, not which keys do/don't exist. Instead pipeline N exist
        # calls, which allows distinguishing which keys do/don't exist.

        def validate_digests(r: "redis.Redis[bytes]") -> List[int]:
            pipe = r.pipeline()
            for digest in digests:
                pipe.exists(self._construct_key(digest))
            return pipe.execute()

        results = self._redis.execute_ro(validate_digests)

        missing_digests: List[Digest] = []
        for digest, result in zip(digests, results):
            if not result:
                missing_digests.append(digest)
        return missing_digests

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def bulk_update_blobs(self, blobs: List[Tuple[Digest, bytes]]) -> List[Status]:
        keymap: Dict[str, bytes] = {}
        results: List[Status] = []
        for blob in blobs:
            if len(blob[1]) != blob[0].size_bytes or HASH(blob[1]).hexdigest() != blob[0].hash:
                results.append(
                    Status(
                        code=code_pb2.INVALID_ARGUMENT,
                        message="Data doesn't match hash",
                    )
                )
            else:
                results.append(Status(code=code_pb2.OK))
                keymap[self._construct_key(blob[0])] = blob[1]
        self._redis.execute_rw(lambda r: r.mset(keymap))  # type: ignore[arg-type]
        # mset can't fail according to the documentation so return OK for all remaining digests
        return results

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    @redis_client_exception_wrapper
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        redis_keys = [self._construct_key(x) for x in digests]
        found_blobs = self._redis.execute_ro(lambda r: r.mget(redis_keys))
        result_map: Dict[str, bytes] = {}
        for digest, blob in zip(digests, found_blobs):
            if blob is not None:
                result_map[digest.hash] = blob
        return result_map
