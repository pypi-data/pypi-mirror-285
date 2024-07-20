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

import logging
import random
import re
from itertools import product
from threading import Event
from typing import Any, Iterator, List, Set, Tuple

from buildgrid.cleanup.janitor.config import JanitorConfig
from buildgrid.cleanup.janitor.index import IndexLookup
from buildgrid.cleanup.janitor.utils import check_bucket_versioning, get_s3_client
from buildgrid.server.threading import ContextWorker

LOGGER = logging.getLogger(__name__)


class S3Janitor:

    def __init__(self, config: JanitorConfig, index: IndexLookup):
        self._bucket_regex = re.compile(config.s3.bucket_regex)
        self._index = index
        self._path_prefix = config.s3.path_prefix
        self._s3 = get_s3_client(config.s3)
        self._sleep_interval = config.sleep_interval
        self._hash_prefix_size = config.s3.hash_prefix_size

        self._stop_requested = Event()
        self._worker = ContextWorker(target=self.run, name="Janitor", on_shutdown_requested=self._stop_requested.set)

    def enumerate_versioned_bucket(self, bucket: str, prefix: str) -> Iterator[Set[Tuple[str, str]]]:
        pages = self._s3.get_paginator("list_object_versions").paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            if "Versions" not in page:
                continue

            digest_version_pairs = {(item["Key"], item["VersionId"]) for item in page["Versions"]}
            yield digest_version_pairs

    def enumerate_unversioned_bucket(self, bucket: str, prefix: str) -> Iterator[Set[Tuple[str, str]]]:
        pages = self._s3.get_paginator("list_objects").paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            if "Contents" not in page:
                continue

            digest_version_pairs = {(item["Key"], "") for item in page["Contents"]}
            yield digest_version_pairs

    def delete_s3_entries(self, bucket: str, digest_versions: Set[Tuple[str, str]]) -> List[str]:
        LOGGER.info(f"Deleting {len(digest_versions)} orphaned blobs from S3")
        response = self._s3.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [{"Key": digest, "VersionId": version} for digest, version in digest_versions],
                "Quiet": False,
            },
        )
        return [key["Key"] for key in response.get("Deleted", [])]

    def get_buckets(self) -> List[str]:
        response = self._s3.list_buckets()
        return [
            bucket["Name"] for bucket in response["Buckets"] if self._bucket_regex.search(bucket["Name"]) is not None
        ]

    # Generate all the hash prefixes and shuffle them to reduce the likelihood of
    # two janitors cleaning the same hash prefix
    def generate_prefixes(self) -> List[str]:
        if self._hash_prefix_size:
            prefixes = [
                (self._path_prefix + "/" if self._path_prefix else "") + "".join(x)
                for x in product("0123456789abcdef", repeat=self._hash_prefix_size)
            ]
            random.shuffle(prefixes)
        else:
            prefixes = [self._path_prefix]
        return prefixes

    def cleanup_bucket(self, bucket: str) -> int:
        LOGGER.info(f"Cleaning up bucket: '{bucket}'")

        deleted_count = 0
        if check_bucket_versioning(self._s3, bucket):
            enumeration = self.enumerate_versioned_bucket
        else:
            enumeration = self.enumerate_unversioned_bucket

        for prefix in self.generate_prefixes():
            deleted_count_for_prefix = 0
            for page in enumeration(bucket, prefix):
                # Create a mapping between a digest as stored in S3 and a digest as stored in the index
                # by stripping off any prefix and removing all '/' used by hash_prefix_size
                digest_map = {digest: digest.replace(self._path_prefix, "").replace("/", "") for digest, _ in page}

                missing_digest_versions = set(
                    digest_version
                    for digest_version in page
                    if digest_map[digest_version[0]] in self._index.get_missing_digests(set(digest_map.values()))
                )
                if missing_digest_versions:
                    self.delete_s3_entries(bucket, missing_digest_versions)
                    deleted_count_for_prefix += len(missing_digest_versions)
            LOGGER.info(f"Deleted {deleted_count_for_prefix} blobs from '{bucket}/{prefix}'")
            deleted_count += deleted_count_for_prefix

        LOGGER.info(f"Deleted {deleted_count} blobs total from bucket '{bucket}'")
        return deleted_count

    def start(self) -> None:
        self._worker.start()
        self._worker.wait()

    def stop(self, *args: Any, **kwargs: Any) -> None:
        self._worker.stop()

    def run(self, stop_requested: Event) -> None:
        random.seed()
        while not stop_requested.is_set():
            bucket_names = self.get_buckets()

            # Shuffle the bucket names to reduce the likelihood of two janitors
            # concurrently cleaning the same bucket.
            random.shuffle(bucket_names)

            for bucket in bucket_names:
                self.cleanup_bucket(bucket)

            stop_requested.wait(timeout=self._sleep_interval)
