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
DiskStorage
==================

A CAS storage provider that stores files as blobs on disk.
"""

import errno
import io
import logging
import os
import tempfile
from typing import IO, Dict, List, Optional

from buildgrid._exceptions import StorageFullError
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid.settings import MAX_IN_MEMORY_BLOB_SIZE_BYTES

from ...decorators import timed
from ...metrics_names import METRIC
from .storage_abc import StorageABC

LOGGER = logging.getLogger(__name__)


class DiskStorage(StorageABC):
    TYPE = "Disk"

    def __init__(self, path: str) -> None:
        if not os.path.isabs(path):
            self.__root_path = os.path.abspath(path)
        else:
            self.__root_path = path
        self.__cas_path = os.path.join(self.__root_path, "cas")

        self.objects_path = os.path.join(self.__cas_path, "objects")
        self.temp_path = os.path.join(self.__root_path, "tmp")

        os.makedirs(self.objects_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug(f"Checking for blob: [{digest}]")
        return os.path.exists(self._get_object_path(digest))

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> Optional[IO[bytes]]:
        LOGGER.debug(f"Getting blob: [{digest}]")
        try:
            f = open(self._get_object_path(digest), "rb")
            # TODO probably need to make StorageABC generic...?
            return io.BufferedReader(f)  # type: ignore[arg-type]
        except FileNotFoundError:
            return None

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: List[Digest]) -> Dict[str, bytes]:
        LOGGER.debug(f"Getting {len(digests)} blobs")
        blobmap: Dict[str, bytes] = {}
        for digest in digests:
            blob = self.get_blob(digest)
            if blob is not None:
                with blob:
                    blobmap[digest.hash] = blob.read()
        return blobmap

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug(f"Deleting blob: [{digest}]")
        try:
            os.remove(self._get_object_path(digest))
        except OSError:
            pass

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug(f"Writing blob: [{digest}]")
        object_path = self._get_object_path(digest)

        write_session.seek(0)
        try:
            with tempfile.NamedTemporaryFile("wb", dir=self.temp_path) as f:
                while data := write_session.read(MAX_IN_MEMORY_BLOB_SIZE_BYTES):
                    f.write(data)
                os.makedirs(os.path.dirname(object_path), exist_ok=True)
                os.link(f.name, object_path)
        except FileExistsError:
            # Object is already there!
            pass
        except OSError as e:
            # Not enough space error or file too large
            if e.errno in [errno.ENOSPC, errno.EFBIG]:
                raise StorageFullError(f"Disk Error: {e.errno}") from e
            raise e

    def _get_object_path(self, digest: Digest) -> str:
        return os.path.join(self.objects_path, digest.hash[:2], digest.hash[2:])
