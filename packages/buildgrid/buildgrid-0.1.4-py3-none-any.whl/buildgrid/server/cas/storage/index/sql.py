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
SQLIndex
==================

A SQL index implementation. This can be pointed to either a remote SQL server
or a local SQLite database.

"""
import io
import itertools
import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import IO, Any, Deque, Dict, Iterator, List, Optional, Sequence, Tuple, cast

from sqlalchemy import Column, and_, delete, func, not_, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, load_only
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session as SessionType
from sqlalchemy.sql.elements import BooleanClauseList

from buildgrid._exceptions import StorageFullError
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_gauge_metric, publish_timer_metric
from buildgrid.server.persistence.sql.models import IndexEntry
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.utils import read_and_rewind, validate_digest_data

from ..storage_abc import StorageABC
from .index_abc import IndexABC
from .sql_dialect_delegates import PostgreSQLDelegate, SQLiteDelegate

LOGGER = logging.getLogger(__name__)
DIALECT_DELEGATES = {"postgresql": PostgreSQLDelegate, "sqlite": SQLiteDelegate}

INLINE_BLOB_SIZE_HARD_MAXIMUM = 1000000000


class SQLIndex(IndexABC):
    TYPE = "SQLIndex"

    def __init__(
        self,
        sql_provider: SqlProvider,
        storage: StorageABC,
        *,
        window_size: int = 1000,
        inclause_limit: int = -1,
        max_inline_blob_size: int = 0,
        refresh_accesstime_older_than: int = 0,
        **kwargs: Any,
    ) -> None:
        base_argnames = ["fallback_on_get"]
        base_args = {}
        for arg in base_argnames:
            if arg in kwargs:
                base_args[arg] = kwargs.pop(arg)
        super().__init__(**base_args)

        self._sql = sql_provider
        self._storage = storage

        if max_inline_blob_size > INLINE_BLOB_SIZE_HARD_MAXIMUM:
            raise ValueError(
                f"Max inline blob size is [{max_inline_blob_size}], "
                f"but must be less than [{INLINE_BLOB_SIZE_HARD_MAXIMUM}]."
            )
        if max_inline_blob_size >= 0:
            self._max_inline_blob_size = max_inline_blob_size
        else:
            raise ValueError(f"Max inline blob size is [{max_inline_blob_size}], but must be nonnegative.")

        if refresh_accesstime_older_than >= 0:
            # Measured in seconds. Helps reduce the frequency of timestamp updates during heavy read.
            self.refresh_accesstime_older_than = refresh_accesstime_older_than
        else:
            raise ValueError(
                f"'refresh_accesstime_older_than' must be nonnegative. It is {refresh_accesstime_older_than}"
            )

        # Max # of rows to fetch while iterating over all blobs
        # (e.g. in least_recent_digests)
        self._all_blobs_window_size = window_size

        # This variable stores the list of whereclauses (SQLAlchemy BooleanClauseList objects)
        # generated from the _column_windows() using time-expensive SQL query.
        # These whereclauses are used to construct the final SQL query
        # during cleanup in order to fetch blobs by time windows.
        #
        # Inside the _column_windows() a list of timestamp boarders are obtained:
        #   intervals = [t1, t2, t3, ...]
        # Then the generated whereclauses might represent semantically as, for example,:
        #   self._queue_of_whereclauses = [
        #     "WHERE t1 <= IndexEntry.accessed_timestamp < t2",
        #     "WHERE t2 <= IndexEntry.accessed_timestamp < t3",
        #     "WHERE t3 <= IndexEntry.accessed_timestamp < t4",
        #     ... and so on]
        # Note the number of entries in each window is determined by
        # the instance variable "_all_blobs_window_size".
        self._queue_of_whereclauses: Deque[BooleanClauseList[Any]] = deque()

        # Whether entries with deleted=True should be considered by mark_n_bytes.
        # This is useful to catch any half-finished deletes where a cleanup process
        # may have exited half-way through deletion. Once all premarked blobs have been
        # deleted this becomes False and is only reset after a full scan of the database
        self._delete_premarked_blobs: bool = True

        # Only pass known kwargs to db session
        available_options = {"pool_size", "max_overflow", "pool_timeout", "pool_pre_ping", "pool_recycle"}
        kwargs_keys = kwargs.keys()
        if kwargs_keys > available_options:
            unknown_args = kwargs_keys - available_options
            raise TypeError(f"Unknown keyword arguments: [{unknown_args}]")

        # Dialect-specific initialization
        self._dialect_delegate = DIALECT_DELEGATES.get(self._sql.dialect)

        if inclause_limit > 0:
            if inclause_limit > window_size:
                LOGGER.warning(
                    f"Configured inclause_limit [{inclause_limit}] " f"is greater than window_size [{window_size}]"
                )
            self._inclause_limit = inclause_limit
        else:
            # If the inlimit isn't explicitly set, we use a default that
            # respects both the window size and the db implementation's
            # inlimit.
            self._inclause_limit = min(window_size, self._sql.default_inlimit)
            LOGGER.debug("SQL index: using default inclause limit " f"of {self._inclause_limit}")

        # Make a test query against the database to ensure the connection is valid
        with self._sql.scoped_session() as session:
            session.query(IndexEntry).first()
        self._sql.remove_scoped_session()

    def start(self) -> None:
        self._storage.start()

    def stop(self) -> None:
        self._storage.stop()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        with self._sql.scoped_session() as session:
            statement = select(func.count(IndexEntry.digest_hash)).where(IndexEntry.digest_hash == digest.hash)

            num_entries = session.execute(statement).scalar()
            if num_entries is None:
                num_entries = 0

            if num_entries == 1:
                return True
            elif num_entries < 1:
                return False
            else:
                raise RuntimeError(f"Multiple results found for blob [{digest}]. The index is in a bad state.")

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        """Get a blob from the index or the backing storage. Optionally fallback and repair index"""

        # Check the index for the blob and return if found.
        with self._sql.scoped_session() as session:
            if entry := session.query(IndexEntry).filter(IndexEntry.digest_hash == digest.hash).first():
                if entry.inline_blob is not None:
                    return io.BytesIO(entry.inline_blob)
                elif blob := self._storage.get_blob(digest):
                    # Fix any blobs that should have been inlined.
                    if digest.size_bytes <= self._max_inline_blob_size:
                        self._save_digests_to_index([(digest, read_and_rewind(blob))], session)
                        session.commit()
                    return blob
                LOGGER.warning(
                    f"Blob [{digest.hash}/{digest.size_bytes}] was indexed but not in storage. Deleting from the index"
                )
                self._bulk_delete_from_index([digest], session)

        # Check the storage for the blob and repair the index if found.
        if self._fallback_on_get:
            if blob := self._storage.get_blob(digest):
                with self._sql.scoped_session() as session:
                    if digest.size_bytes <= self._max_inline_blob_size:
                        self._save_digests_to_index([(digest, read_and_rewind(blob))], session)
                    else:
                        self._save_digests_to_index([(digest, None)], session)
                    session.commit()
                return blob

        # Blob was not found in index or storage
        return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        statement = delete(IndexEntry).where(IndexEntry.digest_hash == digest.hash)
        options = {"synchronize_session": False}

        with self._sql.scoped_session() as session:
            session.execute(statement, execution_options=options)

        self._storage.delete_blob(digest)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        inline_blob = None
        if digest.size_bytes > self._max_inline_blob_size:
            self._storage.commit_write(digest, write_session)
        else:
            write_session.seek(0)
            inline_blob = write_session.read()
        try:
            with self._sql.scoped_session() as session:
                self._save_digests_to_index([(digest, inline_blob)], session)
        except DBAPIError as error:
            # Error has pgcode attribute (Postgres only)
            if hasattr(error.orig, "pgcode"):
                # imported here to avoid global dependency on psycopg2
                from psycopg2.errors import DiskFull, OutOfMemory

                # 53100 == DiskFull && 53200 == OutOfMemory
                if error.orig.pgerror in [DiskFull, OutOfMemory]:
                    raise StorageFullError(f"Postgres Error: {error.orig.pgcode}") from error
            raise error

    def _partitioned_hashes(self, digests: Sequence[Digest]) -> Iterator[Iterator[str]]:
        """Given a long list of digests, split it into parts no larger than
        _inclause_limit and yield the hashes in each part.
        """
        for part_start in range(0, len(digests), self._inclause_limit):
            part_end = min(len(digests), part_start + self._inclause_limit)
            part_digests = itertools.islice(digests, part_start, part_end)
            yield map(lambda digest: digest.hash, part_digests)

    def _bulk_select_digests(
        self, digests: Sequence[Digest], fetch_blobs: bool = False, fetch_deleted: bool = True
    ) -> Iterator[IndexEntry]:
        """Generator that selects all rows matching a digest list.

        SQLAlchemy Core is used for this because the ORM has problems with
        large numbers of bind variables for WHERE IN clauses.

        We only select on the digest hash (not hash and size) to allow for
        index-only queries on db backends that support them.
        """
        index_table = IndexEntry.__table__
        with self._sql.scoped_session() as session:
            columns = [index_table.c.digest_hash]
            if fetch_blobs:
                columns.append(index_table.c.inline_blob)
            for part in self._partitioned_hashes(digests):
                stmt = select(columns).where(index_table.c.digest_hash.in_(part))
                if not fetch_deleted:
                    stmt = stmt.where(not_(index_table.c.deleted))
                entries = session.execute(stmt)
                yield from entries  # type: ignore

    @timed(METRIC.STORAGE.SQL_INDEX.UPDATE_TIMESTAMP_DURATION)
    def _bulk_refresh_timestamps(
        self, digests: Sequence[Digest], session: SessionType, update_time: Optional[datetime] = None
    ) -> None:
        """Refresh all timestamps of the input digests.

        SQLAlchemy Core is used for this because the ORM is not suitable for
        bulk inserts and updates.

        https://docs.sqlalchemy.org/en/13/faq/performance.html#i-m-inserting-400-000-rows-with-the-orm-and-it-s-really-slow
        """
        index_table = IndexEntry.__table__
        current_time = datetime.utcnow()

        # If a timestamp was passed in, use it. And always refreshes (no threshold).
        if update_time:
            timestamp = update_time
            last_accessed_threshold = current_time
        # Otherwise timestamp of digest will not refresh if it was last accessed more recent than this threshold.
        else:
            timestamp = current_time
            last_accessed_threshold = current_time - timedelta(seconds=self.refresh_accesstime_older_than)

        for part in self._partitioned_hashes(digests):
            # Generate the SQL Statement:
            #   UPDATE index SET accessed_timestamp=<timestamp>
            #   WHERE index.digest_hash IN
            #   (SELECT index.digest_hash FROM index
            #    WHERE index.digest_hash IN <part> AND WHERE index.accessed_timestamp < <last_accessed_threshold>
            #    FOR UPDATE SKIP LOCKED)
            stmt = (
                index_table.update()
                .where(
                    index_table.c.digest_hash.in_(
                        select(index_table.c.digest_hash)
                        .where(index_table.c.digest_hash.in_(part))
                        .where(index_table.c.accessed_timestamp < last_accessed_threshold)
                        .with_for_update(skip_locked=True)
                    )
                )
                .values(accessed_timestamp=timestamp)
            )
            session.execute(stmt)
            session.commit()

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: List[Digest]) -> List[Digest]:
        # Blobs marked as deleted are considered as missing
        entries = self._bulk_select_digests(digests, fetch_deleted=False)

        found_hashes = {entry.digest_hash for entry in entries}

        # Split the digests into two found/missing lists
        found_digests, missing_digests = [], []
        for digest in digests:
            if digest.hash in found_hashes:
                found_digests.append(digest)
            else:
                missing_digests.append(digest)

        # Update all timestamps for blobs which were found
        with self._sql.scoped_session() as session:
            self._bulk_refresh_timestamps(found_digests, session)

        return missing_digests

    @timed(METRIC.STORAGE.SQL_INDEX.SAVE_DIGESTS_DURATION)
    def _save_digests_to_index(
        self, digest_blob_pairs: List[Tuple[Digest, Optional[bytes]]], session: SessionType
    ) -> None:
        """Helper to persist a list of digest/blob pairs to the index.

        Any digests present are updated, and new digests are inserted along with their inline blobs (if provided).
        Only blobs with size less than or equal to the max_inline_blob_size are inserted directly into the index.
        """
        if not digest_blob_pairs:
            return

        digest_blob_pairs = sorted(digest_blob_pairs, key=lambda pair: (pair[0].hash, pair[0].size_bytes))

        if self._dialect_delegate:
            try:
                self._dialect_delegate._save_digests_to_index(  # type: ignore
                    digest_blob_pairs, session, self._max_inline_blob_size
                )
                return
            except AttributeError:
                pass

        update_time = datetime.utcnow()
        # Figure out which digests we can just update
        digests = [digest for (digest, blob) in digest_blob_pairs]
        entries = self._bulk_select_digests(digests)
        # Map digests to new entries
        entries_not_present = {
            digest.hash: {
                "digest_hash": digest.hash,
                "digest_size_bytes": digest.size_bytes,
                "accessed_timestamp": update_time,
                "inline_blob": (blob if digest.size_bytes <= self._max_inline_blob_size else None),
                "deleted": False,
            }
            for (digest, blob) in digest_blob_pairs
        }

        entries_present = {}
        for entry in entries:
            entries_present[entry.digest_hash] = entries_not_present[entry.digest_hash]
            del entries_not_present[entry.digest_hash]

        if entries_not_present:
            session.bulk_insert_mappings(IndexEntry, entries_not_present.values())  # type: ignore
        if entries_present:
            session.bulk_update_mappings(IndexEntry, entries_present.values())  # type: ignore

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(  # pylint: disable=arguments-renamed
        self, digest_blob_pairs: List[Tuple[Digest, bytes]]
    ) -> List[Status]:
        """Implement the StorageABC's bulk_update_blobs method.

        The StorageABC interface takes in a list of digest/blob pairs and
        returns a list of results. The list of results MUST be ordered to
        correspond with the order of the input list."""
        pairs_to_store = []
        result_map = {}

        # For each blob, determine whether to store it in the backing storage or inline it
        for digest, blob in digest_blob_pairs:
            if validate_digest_data(digest, blob):
                if digest.size_bytes > self._max_inline_blob_size:
                    pairs_to_store.append((digest, blob))
                else:
                    result_map[digest.hash] = Status(code=code_pb2.OK)
            else:
                result_map[digest.hash] = Status(code=code_pb2.INVALID_ARGUMENT, message="Data doesn't match hash")
        missing_blobs = self.missing_blobs([digest for digest, _ in pairs_to_store])
        missing_blob_pairs = []
        for digest, blob in pairs_to_store:
            if digest not in missing_blobs:
                result_map[digest.hash] = Status(code=code_pb2.OK)
            else:
                missing_blob_pairs.append((digest, blob))

        backup_results = self._storage.bulk_update_blobs(missing_blob_pairs)

        for digest, result in zip(missing_blobs, backup_results):
            if digest.hash in result_map:
                # ERROR: blob was both inlined and backed up
                raise RuntimeError("Blob was both inlined and backed up.")
            result_map[digest.hash] = result

        # Generate the final list of results
        pairs_to_inline: List[Tuple[Digest, Optional[bytes]]] = []
        results = []
        for digest, blob in digest_blob_pairs:
            status = result_map.get(
                digest.hash,
                Status(code=code_pb2.UNKNOWN, message="SQL Index: unable to determine the status of this blob"),
            )
            results.append(status)
            if status.code == code_pb2.OK:
                pairs_to_inline.append((digest, blob))

        with self._sql.scoped_session() as session:
            self._save_digests_to_index(pairs_to_inline, session)

        return results

    def _bulk_read_blobs_with_fallback(self, digests: List[Digest]) -> Dict[str, bytes]:
        hash_to_digest: Dict[str, Digest] = {digest.hash: digest for digest in digests}
        results: Dict[str, bytes] = {}

        expected_storage_digests: List[Digest] = []
        # Fetch inlined blobs directly from the index
        entries = self._bulk_select_digests(digests, fetch_blobs=True)
        for e in entries:
            blob, digest_hash, digest = e.inline_blob, e.digest_hash, hash_to_digest[e.digest_hash]
            if blob is not None:
                results[digest_hash] = blob
                hash_to_digest.pop(digest_hash)
            else:
                # If a blob is not inlined then the blob is expected to be in storage
                expected_storage_digests.append(digest)

        # Fetch everything that wasn't inlined from the backing storage
        fetched_digests = self._storage.bulk_read_blobs(list(hash_to_digest.values()))

        # Save everything fetched from storage, inlining the blobs if they're small enough
        digest_pairs_to_save: List[Tuple[Digest, Optional[bytes]]] = []
        for digest_hash, blob_data in fetched_digests.items():
            if blob_data is not None:
                digest = hash_to_digest[digest_hash]
                if digest.size_bytes <= self._max_inline_blob_size:
                    digest_pairs_to_save.append((digest, blob_data))
                else:
                    digest_pairs_to_save.append((digest, None))
                results[digest_hash] = blob_data

        # List of digests found in storage
        acutal_storage_digest_hashes = set(
            digest_hash for (digest_hash, blob_data) in fetched_digests.items() if blob_data is not None
        )
        # Get a list of all the digests that were in the index but not found in storage
        digests_expected_not_in_storage: List[Digest] = []
        for expected_digest in expected_storage_digests:
            if expected_digest.hash not in acutal_storage_digest_hashes:
                LOGGER.warning(f"Blob [{expected_digest}] was indexed but not in storage. Deleting from the index")
                digests_expected_not_in_storage.append(expected_digest)

        with self._sql.scoped_session() as session:
            self._save_digests_to_index(digest_pairs_to_save, session)
            if digests_expected_not_in_storage:
                self._bulk_delete_from_index(digests_expected_not_in_storage, session)
            session.commit()

        return results

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        if self._fallback_on_get:
            return self._bulk_read_blobs_with_fallback(digests)

        # If fallback is disabled, query the index first and only
        # query the storage for blobs that weren't inlined there

        hash_to_digest = {digest.hash: digest for digest in digests}  # hash -> digest map
        results: Dict[str, bytes] = {}  # The final list of results (return value)
        digests_to_fetch: List[Digest] = []  # Digests that need to be fetched from storage
        digest_pairs_to_save: List[Tuple[Digest, Optional[bytes]]] = []  # Digests that need to be updated in the index

        # Fetch all of the digests in the database
        # Anything that wasn't already inlined needs to be fetched
        entries = self._bulk_select_digests(digests, fetch_blobs=True)
        for index_entry in entries:
            digest = hash_to_digest[index_entry.digest_hash]
            if index_entry.inline_blob is not None:
                results[index_entry.digest_hash] = index_entry.inline_blob
            else:
                digests_to_fetch.append(digest)

        # Caution: digest whose blob cannot be found from storage will be dropped.
        if digests_to_fetch:
            fetched_digests = self._storage.bulk_read_blobs(digests_to_fetch)
        else:
            fetched_digests = {}

        # Generate the list of inputs for _save_digests_to_index
        #
        # We only need to send blob data for small blobs fetched
        # from the storage since everything else is either too
        # big or already inlined
        for digest in digests_to_fetch:
            if blob_data := fetched_digests.get(digest.hash):
                if digest.size_bytes <= self._max_inline_blob_size:
                    digest_pairs_to_save.append((digest, blob_data))

        acutal_storage_digests = set(digest_hash for (digest_hash, _) in fetched_digests.items())
        # Get a list of all the digests that were in the index but not found in storage
        digests_expected_not_in_storage: List[Digest] = []
        for expected_digest in digests_to_fetch:
            if expected_digest.hash not in acutal_storage_digests:
                LOGGER.warning(
                    f"Blob [{expected_digest.hash}/{expected_digest.size_bytes}] "
                    "was indexed but not in storage. Deleting from the index"
                )
                digests_expected_not_in_storage.append(expected_digest)

        # Update any blobs which need to be inlined
        with self._sql.scoped_session() as session:
            self._save_digests_to_index(digest_pairs_to_save, session)
            if digests_expected_not_in_storage:
                self._bulk_delete_from_index(digests_expected_not_in_storage, session)
            session.commit()

        results.update(fetched_digests)
        return results

    def _column_windows(self, session: SessionType, column: Column[Any]) -> Iterator[BooleanClauseList[Any]]:
        """Adapted from the sqlalchemy WindowedRangeQuery recipe.
        https://github.com/sqlalchemy/sqlalchemy/wiki/WindowedRangeQuery

        This method breaks the timestamp range into windows and yields
        the borders of these windows to the callee. For example, the borders
        yielded by this might look something like
        ('2019-10-08 18:25:03.699863', '2019-10-08 18:25:03.751018')
        ('2019-10-08 18:25:03.751018', '2019-10-08 18:25:03.807867')
        ('2019-10-08 18:25:03.807867', '2019-10-08 18:25:03.862192')
        ('2019-10-08 18:25:03.862192',)

        _windowed_lru_digests uses these borders to form WHERE clauses for its
        SELECTs. In doing so, we make sure to repeatedly query the database for
        live updates, striking a balance between loading the entire resultset
        into memory and querying each row individually, both of which are
        inefficient in the context of a large index.

        The window size is a parameter and can be configured. A larger window
        size will yield better performance (fewer SQL queries) at the cost of
        memory (holding on to the results of the query) and accuracy (blobs
        may get updated while you're working on them), and vice versa for a
        smaller window size.
        """

        def int_for_range(start_id: Any, end_id: Any) -> BooleanClauseList[Any]:
            if end_id:
                return and_(column >= start_id, column < end_id)
            else:
                return column >= start_id  # type: ignore[no-any-return]

        # Constructs a query that:
        # 1. Gets all the timestamps in sorted order.
        # 2. Assign a row number to each entry.
        # 3. Only keep timestamps that are every other N row number apart. N="_all_blobs_window_size".
        # SELECT
        #   anon_1.index_accessed_timestamp AS anon_1_index_accessed_timestamp
        #   FROM (
        #       SELECT
        #       index.accessed_timestamp AS index_accessed_timestamp,
        #       row_number() OVER (ORDER BY index.accessed_timestamp) AS rownum
        #       FROM index
        #       )
        #  AS anon_1
        #  WHERE rownum % 1000=1
        #
        # Note:
        #  - This query can be slow due to checking each entry with "WHERE rownum % 1000=1".
        #  - These timestamps will be the basis for constructing the SQL "WHERE" clauses later.
        q = session.query(column, func.row_number().over(order_by=column).label("rownum")).from_self(column)
        if self._all_blobs_window_size > 1:
            q = q.filter(text(f"rownum % {self._all_blobs_window_size}=1"))

        # Execute the underlying query against the database.
        # Ex: intervals = [t1, t1001, t2001, ...], q = [(t1, ), (t1001, ), (t2001, ), ...]
        intervals = [id for id, in q]

        # Generate the whereclauses
        while intervals:
            start = intervals.pop(0)
            if intervals:
                end = intervals[0]
            else:
                end = None
            # Ex: yield "WHERE IndexEntry.accessed_timestamp >= start AND IndexEntry.accessed_timestamp < end"
            yield int_for_range(start, end)

    def _windowed_lru_digests(self, q: "Query[Any]", column: Column[Any]) -> Iterator[Tuple[IndexEntry, bool]]:
        """Generate a query for each window produced by _column_windows
        and yield the results one by one.
        """
        # Determine whether the conditions are met to make an SQL call to get new windows.
        msg = "Using stored LRU windows"
        if len(self._queue_of_whereclauses) == 0:
            msg = "Requesting new LRU windows."
            self._queue_of_whereclauses = deque(self._column_windows(q.session, column))  # type: ignore
            self._delete_premarked_blobs = True

        msg += f" Number of windows remaining: {len(self._queue_of_whereclauses)}"
        LOGGER.debug(msg)

        while self._queue_of_whereclauses:
            whereclause = self._queue_of_whereclauses[0]
            window = q.filter(whereclause).order_by(column.asc())
            yield from window

            # If yield from window doesn't get to this point that means
            # the cleanup hasn't consumed all the content in a whereclause and exited.
            # Otherwise, the whereclause is exhausted and can be discarded.
            self._queue_of_whereclauses.popleft()

    def least_recent_digests(self) -> Iterator[Digest]:
        with self._sql.scoped_session() as session:
            q = session.query(IndexEntry)
            for entry in self._windowed_lru_digests(q, IndexEntry.accessed_timestamp):
                # TODO make this generic or delete this method only used by tests.
                index_entry = cast(IndexEntry, entry)
                assert isinstance(index_entry.digest_hash, str)
                assert isinstance(index_entry.digest_size_bytes, int)
                yield Digest(hash=index_entry.digest_hash, size_bytes=index_entry.digest_size_bytes)

    @timed(METRIC.STORAGE.SQL_INDEX.SIZE_CALCULATION_DURATION)
    def get_total_size(self) -> int:
        statement = select(func.sum(IndexEntry.digest_size_bytes))
        with self._sql.scoped_session() as session:
            result = session.execute(statement).scalar()
            if result is None:
                result = 0
            return result

    @timed(METRIC.STORAGE.SQL_INDEX.DELETE_N_BYTES_DURATION)
    def delete_n_bytes(
        self, n_bytes: int, dry_run: bool = False, protect_blobs_after: Optional[datetime] = None
    ) -> int:
        """
        When using a SQL Index, entries with a delete marker are "in the process of being deleted".
        This is required because storage operations can't be safely tied to the SQL index transaction
        (one may fail independently of the other, and you end up inconsistent).

        The workflow is roughly as follows:
        - Start a SQL transaction.
        - Lock and mark the indexed items you want to delete.
        - Close the SQL transaction.
        - Perform the storage deletes
        - Start a SQL transaction.
        - Actually delete the index entries.
        - Close the SQL transaction.

        This means anything with deleted=False will always be present in the backing store. If it is marked
        deleted=True, and the process gets killed when deleting from the backing storage, only
        some of the items might actually be gone.

        The next time the cleaner starts up, it can try to do that delete again (ignoring 404s).
        Eventually that will succeed and the item will actually be removed from the DB. Only during
        the first run of batches do we consider already marked items. This avoids multiple cleanup
        daemons from competing with each other on every batch.
        """
        if protect_blobs_after is None:
            protect_blobs_after = datetime.utcnow()

        # Used for metric publishing
        delete_start_time = time.time()

        storage_digests: List[Digest] = []
        marked_digests: List[Digest] = []
        collected_bytes = 0

        with self._sql.scoped_session(exceptions_to_not_rollback_on=[StaleDataError]) as session:
            base_query = session.query(IndexEntry, IndexEntry.inline_blob != None).options(  # noqa
                load_only("digest_hash", "digest_size_bytes")
            )

            if self._delete_premarked_blobs:
                LOGGER.info("Starting to gather pre-marked records")
                premarked_query = base_query.filter_by(deleted=True)
                for [entry, is_inline] in premarked_query.all():
                    digest = Digest(hash=entry.digest_hash, size_bytes=entry.digest_size_bytes)
                    marked_digests.append(digest)
                    if not is_inline:
                        storage_digests.append(digest)
                    collected_bytes += entry.digest_size_bytes

                if not dry_run:
                    publish_counter_metric(METRIC.STORAGE.SQL_INDEX.PREMARKED_DELETED_COUNT, len(marked_digests))
                LOGGER.info(f"Gathered pre-marked {collected_bytes} out of {n_bytes} bytes(max)")
                self._delete_premarked_blobs = False

            if collected_bytes < n_bytes:
                LOGGER.info("Searching for records to mark deleted")
                unmarked_query = (
                    base_query.filter_by(deleted=False)
                    .filter(IndexEntry.accessed_timestamp < protect_blobs_after)
                    .with_for_update(skip_locked=True)
                )
                window = self._windowed_lru_digests(unmarked_query, IndexEntry.accessed_timestamp)
                mark_deleted_start = time.perf_counter()
                for [entry, is_inline] in window:
                    digest = Digest(hash=entry.digest_hash, size_bytes=entry.digest_size_bytes)
                    marked_digests.append(digest)
                    if not is_inline:
                        storage_digests.append(digest)
                    collected_bytes += entry.digest_size_bytes
                    if not dry_run:
                        entry.deleted = True
                    if collected_bytes >= n_bytes:
                        break
                mark_deleted_duration = timedelta(seconds=time.perf_counter() - mark_deleted_start)
                if not dry_run:
                    publish_timer_metric(METRIC.STORAGE.SQL_INDEX.MARK_DELETED_DURATION, mark_deleted_duration)
                LOGGER.info(f"Gathered {collected_bytes} out of {n_bytes} bytes(max)")

        if dry_run:
            return collected_bytes

        failed_deletes = self._storage.bulk_delete(storage_digests)
        digests_to_delete = [x for x in marked_digests if f"{x.hash}/{x.size_bytes}" not in failed_deletes]

        with self._sql.scoped_session(exceptions_to_not_rollback_on=[StaleDataError]) as session:
            failed_deletes.extend(self._bulk_delete_from_index(digests_to_delete, session))
        for digest in digests_to_delete:
            if digest in failed_deletes:
                collected_bytes -= digest.size_bytes

        batch_duration = time.time() - delete_start_time
        blobs_deleted_per_second = (len(digests_to_delete) - len(failed_deletes)) / batch_duration
        publish_gauge_metric(METRIC.CLEANUP.BLOBS_DELETED_PER_SECOND, blobs_deleted_per_second)
        return collected_bytes

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: List[Digest]) -> List[str]:
        # Delete from the index and then delete from the backing storage.
        with self._sql.scoped_session(exceptions_to_not_rollback_on=[StaleDataError]) as session:
            failed_deletes = self._bulk_delete_from_index(digests, session)

        digests_to_delete = [x for x in digests if f"{x.hash}/{x.size_bytes}" not in failed_deletes]
        failed_deletes.extend(self._storage.bulk_delete(digests_to_delete))
        return failed_deletes

    @timed(METRIC.STORAGE.SQL_INDEX.BULK_DELETE_INDEX_DURATION)
    def _bulk_delete_from_index(self, digests: List[Digest], session: Session) -> List[str]:
        LOGGER.info(f"Deleting {len(digests)} digests from the index")
        index_table = IndexEntry.__table__
        hashes = [x.hash for x in digests]

        # Make sure we don't exceed maximum size of an IN clause
        n = self._inclause_limit
        hash_chunks = [hashes[i : i + n] for i in range(0, len(hashes), n)]

        # We will not raise, rollback, or log on StaleDataErrors.
        # These errors occur when we delete fewer rows than we were expecting.
        # This is fine, since the missing rows will get deleted eventually.
        # When running bulk_deletes concurrently, StaleDataErrors
        # occur too often to log.
        num_blobs_deleted = 0
        for chunk in hash_chunks:
            # Do not wait for locks when deleting rows. Skip locked rows to
            # avoid deadlocks.
            stmt = index_table.delete().where(
                index_table.c.digest_hash.in_(
                    select([index_table.c.digest_hash], index_table.c.digest_hash.in_(chunk)).with_for_update(
                        skip_locked=True
                    )
                )
            )
            num_blobs_deleted += session.execute(stmt).rowcount  # type: ignore
        LOGGER.info(f"{num_blobs_deleted}/{len(digests)} blobs deleted from the index")

        # bulk_delete is typically expected to return the digests that were not deleted,
        # but delete only returns the number of rows deleted and not what was/wasn't
        # deleted. Getting this info would require extra queries, so assume that
        # everything was either deleted or already deleted. Failures will continue to throw
        return []
