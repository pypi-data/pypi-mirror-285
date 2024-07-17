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

import logging
from typing import Optional

from buildgrid._enums import ActionCacheEntryType
from buildgrid._exceptions import NotFoundError
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ActionResult, Digest
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.cas.storage.redis import redis_client_exception_wrapper
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.redis.provider import RedisProvider

LOGGER = logging.getLogger(__name__)


class RedisActionCache(ActionCacheABC):
    def __init__(
        self,
        storage: StorageABC,
        redis: RedisProvider,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
        entry_type: Optional[ActionCacheEntryType] = ActionCacheEntryType.ACTION_RESULT_DIGEST,
        migrate_entries: Optional[bool] = False,
    ) -> None:
        """Initialises a new ActionCache instance using Redis.
        Stores the `ActionResult` message as a value.

            Args:
                storage (StorageABC): storage backend instance to be used to store ActionResults.
                redis (RedisProvider): Redis connection provider
                allow_updates (bool): allow the client to write to storage
                cache_failed_actions (bool): whether to store failed actions in the Action Cache
                entry_type (ActionCacheEntryType): whether to store ActionResults or their digests.
                migrate_entries (bool): if set, migrate entries that contain a value with
                    a different `ActionCacheEntryType` to `entry_type` as they are accessed
                    (False by default).
        """
        super().__init__(storage=storage, allow_updates=allow_updates)

        self._redis = redis
        self._cache_failed_actions = cache_failed_actions
        self._entry_type = entry_type
        self._migrate_entries = migrate_entries

    @redis_client_exception_wrapper
    def get_action_result(self, action_digest: Digest) -> ActionResult:
        key = self._get_key(action_digest)
        action_result = self._get_action_result(key, action_digest)
        if action_result is not None:
            if self.referenced_blobs_still_exist(action_digest, action_result):
                return action_result

            if self._allow_updates:
                LOGGER.debug(
                    f"Removing {action_digest.hash}/{action_digest.size_bytes}"
                    "from cache due to missing blobs in CAS"
                )
                self._redis.execute_rw(lambda r: r.delete(key))

        raise NotFoundError(f"Key not found: [{key}]")

    @redis_client_exception_wrapper
    def update_action_result(self, action_digest: Digest, action_result: ActionResult) -> None:
        if not self._allow_updates:
            raise NotImplementedError("Updating cache not allowed")

        if self._cache_failed_actions or action_result.exit_code == 0:
            assert self._storage, "Storage used before initialization"
            action_result_digest = self._storage.put_message(action_result)

            cache_key = self._get_key(action_digest)

            if self._entry_type == ActionCacheEntryType.ACTION_RESULT_DIGEST:
                self._redis.execute_rw(lambda r: r.set(cache_key, action_result_digest.SerializeToString()))
            else:
                self._redis.execute_rw(lambda r: r.set(cache_key, action_result.SerializeToString()))

            LOGGER.info(f"Result cached for action [{action_digest.hash}/{action_digest.size_bytes}]")

    def _get_key(self, action_digest: Digest) -> str:
        return f"action-cache.{action_digest.hash}_{action_digest.size_bytes}"

    def _get_action_result(self, key: str, action_digest: Digest) -> Optional[ActionResult]:
        value_in_cache = self._redis.execute_ro(lambda r: r.get(key))

        if value_in_cache is None:
            return None

        # Attempting to parse the entry as a `Digest` first:
        action_result_digest = Digest.FromString(value_in_cache)
        if len(action_result_digest.hash) == len(action_digest.hash):
            # The cache contains the `Digest` of the `ActionResult`:
            assert self._storage, "Storage used before initialization"
            action_result = self._storage.get_message(action_result_digest, ActionResult)

            # If configured, update the entry to contain an `ActionResult`:
            if self._entry_type == ActionCacheEntryType.ACTION_RESULT and self._migrate_entries:
                LOGGER.debug(
                    f"Converting entry for {action_digest.hash}/{action_digest.size_bytes} "
                    "from Digest to ActionResult"
                )
                assert action_result, "Returned result was none"
                result = action_result.SerializeToString()
                self._redis.execute_rw(lambda r: r.set(key, result))
        else:
            action_result = ActionResult.FromString(value_in_cache)

            # If configured, update the entry to contain a `Digest`:
            if self._entry_type == ActionCacheEntryType.ACTION_RESULT_DIGEST and self._migrate_entries:
                LOGGER.debug(
                    f"Converting entry for {action_digest.hash}/{action_digest.size_bytes} "
                    "from ActionResult to Digest"
                )
                assert self._storage, "Storage used before initialization"
                action_result_digest = self._storage.put_message(action_result)
                self._redis.execute_rw(lambda r: r.set(key, action_result_digest.SerializeToString()))

        return action_result
