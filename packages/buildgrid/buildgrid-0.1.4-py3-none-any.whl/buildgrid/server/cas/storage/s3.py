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
S3Storage
==================

A storage provider that stores data in an Amazon S3 bucket.
"""

import io
import logging
from collections import defaultdict
from contextlib import ExitStack
from typing import IO, TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import boto3
from botocore.exceptions import ClientError

from buildgrid._exceptions import StorageFullError
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.s3 import s3utils
from buildgrid.settings import HASH, S3_MAX_UPLOAD_SIZE, S3_TIMEOUT_READ

from ...decorators import timed
from ...metrics_names import METRIC
from ...metrics_utils import publish_counter_metric
from .storage_abc import StorageABC, create_write_session

if TYPE_CHECKING:
    from mypy_boto3_s3 import Client as S3Client

LOGGER = logging.getLogger(__name__)


class S3Storage(StorageABC):
    TYPE = "S3"

    def __init__(
        self,
        bucket: str,
        page_size: int = 1000,
        s3_read_timeout_seconds_per_kilobyte: Optional[float] = None,
        s3_write_timeout_seconds_per_kilobyte: Optional[float] = None,
        s3_read_timeout_min_seconds: float = S3_TIMEOUT_READ,
        s3_write_timeout_min_seconds: float = S3_TIMEOUT_READ,
        s3_versioned_deletes: bool = False,
        s3_hash_prefix_size: Optional[int] = None,
        s3_path_prefix_string: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._bucket_template = bucket
        self._page_size = page_size
        self._s3_read_timeout_seconds_per_kilobyte = s3_read_timeout_seconds_per_kilobyte
        self._s3_read_timeout_min_seconds = s3_read_timeout_min_seconds
        self._s3_write_timeout_seconds_per_kilobyte = s3_write_timeout_seconds_per_kilobyte
        self._s3_write_timeout_min_seconds = s3_write_timeout_min_seconds
        self._s3_versioned_deletes = s3_versioned_deletes
        self._s3_hash_prefix_size = s3_hash_prefix_size
        self._s3_path_prefix_string: Optional[str] = None
        if s3_path_prefix_string:
            self._s3_path_prefix_string = s3_path_prefix_string.strip("/")

        # Boto logs can be very verbose, restrict to WARNING
        for boto_logger_name in ["boto3", "botocore", "s3transfer", "urllib3"]:
            boto_logger = logging.getLogger(boto_logger_name)
            boto_logger.setLevel(max(boto_logger.level, logging.WARNING))

        self._s3: "S3Client" = boto3.client("s3", **kwargs)

    def _construct_key_with_prefix(self, digest: Digest) -> str:
        if not self._s3_hash_prefix_size and not self._s3_path_prefix_string:
            return self._construct_key(digest)
        else:
            try:
                prefix = ""
                if self._s3_path_prefix_string:
                    prefix += self._s3_path_prefix_string + "/"
                if self._s3_hash_prefix_size:
                    prefix += digest.hash[0 : self._s3_hash_prefix_size] + "/"
                    remaining = digest.hash[self._s3_hash_prefix_size :]
                else:
                    remaining = digest.hash
                return f"{prefix}{remaining}_{digest.size_bytes}"
            except IndexError:
                LOGGER.error(
                    f"Could not calculate bucket name for digest=[{digest}]. This "
                    "is either a misconfiguration in the BuildGrid S3 bucket "
                    "configuration, or a badly formed request."
                )
                raise

    def _get_bucket_name(self, digest: str) -> str:
        try:
            return self._bucket_template.format(digest=digest)
        except IndexError:
            LOGGER.error(
                f"Could not calculate bucket name for digest=[{digest}]. This "
                "is either a misconfiguration in the BuildGrid S3 bucket "
                "configuration, or a badly formed request."
            )
            raise

    def _construct_key(self, digest: Digest) -> str:
        return digest.hash + "_" + str(digest.size_bytes)

    def _get_s3object(self, digest: Digest) -> s3utils.S3Object:
        object = s3utils.S3Object(self._get_bucket_name(digest.hash), self._construct_key_with_prefix(digest))
        object.filesize = digest.size_bytes
        return object

    def _remove_key_prefixes(self, key: str) -> str:
        # Only interested in last two elements if hash_prefix used
        split_key = key.split("/")
        if self._s3_hash_prefix_size:
            return "".join(split_key[-2:])
        # Only need last element if only a prefix string was used
        if self._s3_path_prefix_string:
            return split_key[-1]
        return key

    def _deconstruct_key(self, key: str) -> Tuple[str, int]:
        # Remove any prefix, returning key to hash_size_bytes format
        key = self._remove_key_prefixes(key)
        parts = key.split("_")
        size_bytes = int(parts[-1])
        # This isn't as simple as just "the first part of the split" because
        # the hash part of the key itself might contain an underscore.
        digest_hash = "_".join(parts[0:-1])
        return digest_hash, size_bytes

    def _multi_delete_blobs(self, bucket_name: str, digests: List[Dict[str, str]]) -> List[str]:
        # TODO fix this:
        #    expression has type "List[Dict[str, str]]",
        #    TypedDict item "Objects" has type "Sequence[ObjectIdentifierTypeDef]"
        response = self._s3.delete_objects(
            Bucket=bucket_name, Delete={"Objects": digests}  # type: ignore[typeddict-item]
        )
        return_failed = []
        failed_deletions = response.get("Errors", [])
        for failed_key in failed_deletions:
            digest_hash, size_bytes = self._deconstruct_key(failed_key["Key"])
            return_failed.append(f"{digest_hash}/{size_bytes}")
        return return_failed

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug(f"Checking for blob: [{digest}]")
        try:
            s3utils.head_object(self._s3, self._get_s3object(digest))
        except ClientError as e:
            if e.response["Error"]["Code"] not in ["404", "NoSuchKey"]:
                raise
            return False
        return True

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        LOGGER.debug(f"Getting blob: [{digest}]")
        try:
            s3object = self._get_s3object(digest)
            s3object.fileobj = create_write_session(digest)
            s3utils.get_object(
                self._s3,
                s3object,
                timeout_seconds_per_kilobyte=self._s3_read_timeout_seconds_per_kilobyte,
                timeout_min_seconds=self._s3_read_timeout_min_seconds,
            )
            s3object.fileobj.seek(0)
            return s3object.fileobj
        except ClientError as e:
            if e.response["Error"]["Code"] not in ["404", "NoSuchKey"]:
                raise
            return None

    def _get_version_id(self, bucket: str, key: str) -> Optional[str]:
        try:
            return self._s3.head_object(Bucket=bucket, Key=key).get("VersionId")
        except ClientError as e:
            if e.response["Error"]["Code"] not in ["404", "NoSuchKey"]:
                raise
            return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug(f"Deleting blob: [{digest}]")
        bucket, key = self._get_bucket_name(digest.hash), self._construct_key_with_prefix(digest)
        try:
            if self._s3_versioned_deletes and (version_id := self._get_version_id(bucket, key)):
                self._s3.delete_object(Bucket=bucket, Key=key, VersionId=version_id)
            else:
                self._s3.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            if e.response["Error"]["Code"] not in ["404", "NoSuchKey"]:
                raise

    def _get_version_ids(self, digests: List[Digest]) -> Dict[str, Optional[str]]:
        s3objects = [self._get_s3object(digest) for digest in digests]
        s3utils.head_objects(self._s3, s3objects)
        return {
            digest.hash: s3object.response_headers.get("x-amz-version-id")
            for digest, s3object in zip(digests, s3objects)
            if s3object.error is None
        }

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: List[Digest]) -> List[str]:
        LOGGER.debug(f"Deleting {len(digests)} digests from S3 storage: [{digests}]")

        if self._s3_versioned_deletes:
            version_ids = self._get_version_ids(digests)
        else:
            version_ids = {}

        bucketed_requests: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for digest in digests:
            bucket = self._get_bucket_name(digest.hash)
            key = self._construct_key_with_prefix(digest)
            bucketed_requests[bucket].append({"Key": key})
            if version_id := version_ids.get(digest.hash):
                bucketed_requests[bucket].append({"Key": key, "VersionId": version_id})

        failed_deletions = []
        for bucket, requests in bucketed_requests.items():
            for i in range(0, len(requests), self._page_size):
                try:
                    failed_deletions += self._multi_delete_blobs(bucket, requests[i : i + self._page_size])
                except ClientError as error:
                    current_failed_deletions = [
                        self._deconstruct_key(key_versions["Key"])
                        for key_versions in requests[i : i + self._page_size]
                    ]
                    failed_deletions += [
                        f"{digest_hash}/{digest_size_bytes}"
                        for digest_hash, digest_size_bytes in current_failed_deletions
                    ]
                    LOGGER.exception(error)
                    LOGGER.exception("Error encountered when trying to delete blobs from the S3 storage")

        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(failed_deletions), type=self.TYPE)
        return failed_deletions

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug(f"Writing blob: [{digest}]")
        write_session.seek(0)
        try:
            s3object = self._get_s3object(digest)
            s3object.fileobj = write_session
            s3object.filesize = digest.size_bytes
            if digest.size_bytes <= S3_MAX_UPLOAD_SIZE:
                s3utils.put_object(
                    self._s3,
                    s3object,
                    timeout_seconds_per_kilobyte=self._s3_write_timeout_seconds_per_kilobyte,
                    timeout_min_seconds=self._s3_write_timeout_min_seconds,
                )
            else:
                s3utils.multipart_upload(self._s3, s3object)
        except ClientError as error:
            if error.response["Error"]["Code"] == "QuotaExceededException":
                raise StorageFullError("S3 Quota Exceeded.") from error
            raise error

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: List[Digest]) -> List[Digest]:
        result = []
        s3objects = []
        for digest in digests:
            s3object = self._get_s3object(digest)
            s3objects.append(s3object)
        s3utils.head_objects(self._s3, s3objects)
        for digest, s3object in zip(digests, s3objects):
            if s3object.error is not None:
                result.append(digest)
        return result

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: List[Tuple[Digest, bytes]]) -> List[Status]:
        s3object_status_list: List[Union[Tuple[None, Status], Tuple[s3utils.S3Object, None]]] = []
        s3objects = []
        with ExitStack() as stack:
            for digest, data in blobs:
                if len(data) != digest.size_bytes or HASH(data).hexdigest() != digest.hash:
                    status = Status(
                        code=code_pb2.INVALID_ARGUMENT,
                        message="Data doesn't match hash",
                    )
                    s3object_status_list.append((None, status))
                else:
                    write_session = stack.enter_context(create_write_session(digest))
                    write_session.write(data)
                    write_session.seek(0)
                    s3object = self._get_s3object(digest)
                    s3object.fileobj = write_session
                    s3object.filesize = digest.size_bytes
                    s3objects.append(s3object)
                    s3object_status_list.append((s3object, None))

            s3utils.put_objects(
                self._s3,
                s3objects,
                timeout_seconds_per_kilobyte=self._s3_write_timeout_seconds_per_kilobyte,
                timeout_min_seconds=self._s3_write_timeout_min_seconds,
            )

            result = []
            for res_s3object, res_status in s3object_status_list:
                if res_status:
                    # Failed check before S3 object creation
                    result.append(res_status)
                elif res_s3object:
                    if res_s3object.error is None:
                        # PUT was successful
                        result.append(Status(code=code_pb2.OK))
                    else:
                        result.append(Status(code=code_pb2.UNKNOWN, message=str(res_s3object.error)))

        return result

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        s3objects: List[s3utils.S3Object] = []
        for digest in digests:
            s3object = self._get_s3object(digest)
            s3object.fileobj = io.BytesIO()
            s3objects.append(s3object)

        s3utils.get_objects(
            self._s3,
            s3objects,
            timeout_seconds_per_kilobyte=self._s3_read_timeout_seconds_per_kilobyte,
            timeout_min_seconds=self._s3_read_timeout_min_seconds,
        )

        blobmap: Dict[str, bytes] = {}
        for digest, s3object in zip(digests, s3objects):
            if not s3object.error:
                if s3object.fileobj:
                    s3object.fileobj.seek(0)
                    blobmap[digest.hash] = s3object.fileobj.read()
            elif s3object.status_code != 404:
                raise s3object.error
        return blobmap
