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


import os
import sys
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, TypedDict, Union
from urllib.parse import urlparse

import buildgrid_metering.client as metering
import click
import grpc
import requests
import yaml
from buildgrid_metering.client.exceptions import MeteringServiceClientError, MeteringServiceError
from importlib_resources import files
from jsonschema import Draft7Validator, validators
from jsonschema.exceptions import ValidationError

from buildgrid._enums import ActionCacheEntryType
from buildgrid.client.asset import AssetClient
from buildgrid.client.authentication import ClientCredentials
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.actioncache.caches.lru_cache import LruActionCache
from buildgrid.server.actioncache.caches.mirrored_cache import MirroredCache
from buildgrid.server.actioncache.caches.remote_cache import RemoteActionCache
from buildgrid.server.actioncache.caches.s3_cache import S3ActionCache
from buildgrid.server.actioncache.caches.with_cache import WithCacheActionCache
from buildgrid.server.actioncache.caches.write_once_cache import WriteOnceActionCache
from buildgrid.server.actioncache.instance import ActionCache
from buildgrid.server.bots.instance import BotsInterface
from buildgrid.server.build_events.storage import BuildEventStreamStorage
from buildgrid.server.cas.instance import ByteStreamInstance, ContentAddressableStorageInstance
from buildgrid.server.cas.storage.disk import DiskStorage
from buildgrid.server.cas.storage.index.sql import SQLIndex
from buildgrid.server.cas.storage.lru_memory_cache import LRUMemoryCache
from buildgrid.server.cas.storage.remote import RemoteStorage
from buildgrid.server.cas.storage.replicated import ReplicatedStorage
from buildgrid.server.cas.storage.s3 import S3Storage
from buildgrid.server.cas.storage.sharded import ShardedStorage
from buildgrid.server.cas.storage.size_differentiated import SizeDifferentiatedStorage, SizeLimitedStorageType
from buildgrid.server.cas.storage.sql import SQLStorage
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.cas.storage.with_cache import WithCacheStorage
from buildgrid.server.controller import ExecutionController
from buildgrid.server.persistence.sql.impl import AgedJobHandlerOptions, SQLDataStore
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.settings import (
    DEFAULT_MAX_EXECUTION_TIMEOUT,
    DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
    DEFAULT_PLATFORM_PROPERTY_KEYS,
    S3_MAX_RETRIES,
    S3_TIMEOUT_CONNECT,
    S3_TIMEOUT_READ,
    S3_USERAGENT_NAME,
)
from buildgrid.utils import insecure_uri_schemes, secure_uri_schemes

from ..._enums import ServiceName
from ...client.channel import setup_channel


# TODO clean up this construction. The abstract class definition has no well defined ctor.
class YamlFactory(yaml.YAMLObject):
    """Base class for contructing maps or scalars from tags."""

    yaml_tag: Optional[str] = None
    schema: Optional[str] = None

    @classmethod
    def _get_schema(cls):
        schema = {}
        if cls.schema is not None:
            schema_text = files("buildgrid._app.settings.schemas").joinpath(cls.schema).read_text()
            schema = yaml.safe_load(schema_text)
        return schema

    @classmethod
    def _validate(cls, values):
        click.echo(click.style(f"\nValidating {cls.yaml_tag}...", fg="yellow"))
        schema = cls._get_schema()
        validator = get_validator(schema=schema)
        try:
            validator.validate(instance=values)
        except ValidationError as e:
            click.echo(click.style(f"ERROR: {cls.yaml_tag} failed validation: {e}", fg="red", bold=True), err=True)
            sys.exit(-1)

    @classmethod
    def from_yaml(cls, loader, node):
        yaml_filename = loader.name
        # We'll pass the name of the file being parsed as
        # `_yaml_filename`.
        # (Enables things like resolving a path in the config
        # relative to the YAML file itself.)

        if isinstance(node, yaml.ScalarNode):
            value = loader.construct_scalar(node)
            return cls(_yaml_filename=yaml_filename, path=value)  # type: ignore[call-arg]

        else:
            values = loader.construct_mapping(node, deep=True)
            cls._validate(values)
            for key, value in dict(values).items():
                values[key.replace("-", "_")] = values.pop(key)

            values["_yaml_filename"] = yaml_filename
            return cls(**values)


class Channel(YamlFactory):
    """Creates a GRPC channel.

    The :class:`Channel` class returns a `grpc.Channel` and is generated from
    the tag ``!channel``. Creates either a secure or insecure channel.

    Usage
        .. code:: yaml

            - !channel
              address (str): Address for the channel. (For example,
                'localhost:50055' or 'unix:///tmp/sock')
              port (int): A port for the channel (only if no address was specified).
              insecure-mode: false
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert

    Args:
        port (int): A port for the channel.
        insecure_mode (bool): If ``True``, generates an insecure channel, even
            if there are credentials. Defaults to ``True``.
        credentials (dict, optional): A dictionary in the form::

            tls-server-key: /path/to/server-key
            tls-server-cert: /path/to/server-cert
            tls-client-certs: /path/to/client-certs
    """

    yaml_tag = "!channel"
    schema = os.path.join("misc", "channel.yaml")

    def __init__(
        self,
        _yaml_filename: str,
        insecure_mode: bool,
        address: Optional[str] = None,
        port: Optional[int] = None,
        credentials: Optional[Dict[str, str]] = None,
    ):
        # TODO: When safe, deprecate the `port` option.
        if port:
            click.echo(
                click.style(
                    "Warning: the 'port' option will be deprecated. "
                    f"Consider specifying 'address: localhost:{port}' instead.",
                    fg="bright_yellow",
                )
            )

        self.address = address if address else f"[::]:{port}"
        self.credentials = None

        if not insecure_mode:
            self.credentials = credentials
            _validate_server_credentials(self.credentials)


class ExpandPath(YamlFactory):
    """Returns a string of the user's path after expansion.

    The :class:`ExpandPath` class returns a string and is generated from the
    tag ``!expand-path``.

    Usage
        .. code:: yaml

            path: !expand-path ~/bgd-data/cas

    Args:
        path (str): Can be used with strings such as: ``~/dir/to/something``
            or ``$HOME/certs``
    """

    yaml_tag = "!expand-path"

    def __new__(cls, _yaml_filename: str, path: str):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        return path


class ExpandVars(YamlFactory):
    """Expand environment variables in a string.

    The :class:`ExpandVars` class returns a string and is generated from the
    tag ``!expand-vars``.

    Usage
        .. code:: yaml

            endpoint: !expand-vars $ENDPOINT

    Args:
        path (str): Can be used with strings such as: ``http://$ENDPOINT``
    """

    yaml_tag = "!expand-vars"

    def __new__(cls, _yaml_filename: str, path: str):
        return os.path.expandvars(path)


class ReadFile(YamlFactory):
    """Returns a string of the contents of the specified file.

    The :class:`ReadFile` class returns a string and is generated from the
    tag ``!read-file``.

    Usage
        .. code:: yaml

            secret_key: !read-file /var/bgd/s3-secret-key

    Args:
        path (str): Can be used with strings such as: ``~/path/to/some/file``
            or ``$HOME/myfile`` or ``/path/to/file``
    """

    yaml_tag = "!read-file"

    def __new__(cls, _yaml_filename: str, path):
        # Expand path
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)

        if not os.path.exists(path):
            click.echo(
                click.style(
                    f"ERROR: read-file `{path}` failed due to it not existing or bad permissions.",
                    fg="red",
                    bold=True,
                ),
                err=True,
            )
            sys.exit(-1)
        else:
            with open(path, "r", encoding="utf-8") as file:
                try:
                    file_contents = "\n".join(file.readlines()).strip()
                    return file_contents
                except IOError as e:
                    click.echo(f"ERROR: read-file failed to read file `{path}`: {e}", err=True)
                    sys.exit(-1)


class Disk(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.disk.DiskStorage` using the tag ``!disk-storage``.

    Usage
        .. code:: yaml

            - !disk-storage
              path: /opt/bgd/cas-storage

    Args:
        path (str): Path to directory to storage.

    """

    yaml_tag = "!disk-storage"
    schema = os.path.join("storage", "disk.yaml")

    def __new__(cls, _yaml_filename: str, path: str):
        """Creates a new disk

        Args:
           path (str): Some path
        """
        return DiskStorage(path)


class LRU(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.lru_memory_cache.LRUMemoryCache` using the tag ``!lru-storage``.

    Usage
        .. code:: yaml

            - !lru-storage
              size: 2048M

    Args:
        size (int): Size e.g ``10kb``. Size parsed with
            :meth:`buildgrid._app.settings.parser._parse_size`.
    """

    yaml_tag = "!lru-storage"
    schema = os.path.join("storage", "lru.yaml")

    def __new__(cls, _yaml_filename: str, size: str):
        return LRUMemoryCache(_parse_size(size))


class S3(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.s3.S3Storage` using the tag ``!s3-storage``.

    Usage
        .. code:: yaml

            - !s3-storage
              bucket: bgd-bucket-{digest[0]}{digest[1]}
              endpoint: http://127.0.0.1:9000
              access_key: !read-file /var/bgd/s3-access-key
              secret_key: !read-file /var/bgd/s3-secret-key
              read_timeout_seconds_per_kilobyte: 0.01
              write_timeout_seconds_per_kilobyte: 0.01
              read_timeout_min_seconds: 120
              write_timeout_min_seconds: 120

    Args:
        bucket (str): Name of bucket
        endpoint (str): URL of endpoint.
        access-key (str): S3-ACCESS-KEY
        secret-key (str): S3-SECRET-KEY
        read_timeout_seconds_per_kilobyte (float): S3 Read timeout in seconds/kilobyte
        write_timeout_seconds_per_kilobyte (float): S3 Write timeout in seconds/kilobyte
        read_timeout_min_seconds (float): The minimal timeout for S3 read
        write_timeout_min_seconds (float): The minimal timeout for S3 writes
        versioned_deletes (bool): Query and use the VersionId when performing deletes.
        hash-prefix-size (int): Number of hash characters to use as prefix in s3 object name.
        path-prefix-string (str): Additional string for path prefix
    """

    yaml_tag = "!s3-storage"
    schema = os.path.join("storage", "s3.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        bucket: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
        read_timeout_seconds_per_kilobyte: Optional[float] = None,
        write_timeout_seconds_per_kilobyte: Optional[float] = None,
        read_timeout_min_seconds: float = S3_TIMEOUT_READ,
        write_timeout_min_seconds: float = S3_TIMEOUT_READ,
        versioned_deletes: bool = False,
        hash_prefix_size: Optional[int] = None,
        path_prefix_string: Optional[str] = None,
    ):
        from botocore.config import Config as BotoConfig  # pylint: disable=import-outside-toplevel

        boto_config = BotoConfig(
            user_agent=S3_USERAGENT_NAME,
            connect_timeout=S3_TIMEOUT_CONNECT,
            read_timeout=S3_TIMEOUT_READ,
            retries={"max_attempts": S3_MAX_RETRIES},
            signature_version="s3v4",
        )

        return S3Storage(
            bucket,
            endpoint_url=endpoint,
            s3_read_timeout_seconds_per_kilobyte=read_timeout_seconds_per_kilobyte,
            s3_write_timeout_seconds_per_kilobyte=write_timeout_seconds_per_kilobyte,
            s3_read_timeout_min_seconds=read_timeout_min_seconds,
            s3_write_timeout_min_seconds=write_timeout_min_seconds,
            s3_versioned_deletes=versioned_deletes,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=boto_config,
            s3_hash_prefix_size=hash_prefix_size,
            s3_path_prefix_string=path_prefix_string,
        )


class RedisConnection(YamlFactory):
    """Generates :class:`buildgrid.server.redis.provider.RedisProvider` using the tag ``!redis-connection``

    Usage
        .. code:: yaml

            - !redis-connection
              host: redis
              port: 6379
              password: !read-file /var/bgd/redis-pass
              db: 0
              dns-srv-record: <Domain name of SRV record>
              sentinel-master-name: <service_name of Redis sentinel's master instance>
              retries: 3


    Args:
        host (str | None): The hostname of the Redis server to use.
        port (int | None): The port that Redis is served on.
        password (str | None): The Redis database password to use.
        db (int): The Redis database number to use.
        dns-srv-record (str): Domain name of SRV record used to discover host/port
        sentinel-master-name (str): Service name of Redis master instance, used
            in a Redis sentinel configuration
        retries (int): Max number of times to retry (default 3). Backoff between retries is about 2^(N-1),
            where N is the number of attempts
    """

    yaml_tag = "!redis-connection"
    schema = os.path.join("connections", "redis.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        db: Optional[int] = None,
        dns_srv_record: Optional[str] = None,
        sentinel_master_name: Optional[str] = None,
        retries: int = 3,
    ):
        # Import here so there is no global buildgrid dependency on redis
        from buildgrid.server.redis.provider import RedisProvider

        # ... validations like host/port xor dns srv record
        return RedisProvider(
            host=host,
            port=port,
            password=password,
            db=db,
            dns_srv_record=dns_srv_record,
            sentinel_master_name=sentinel_master_name,
            retries=retries,
        )


class Redis(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.redis.RedisStorage` using the tag ``!redis-storage``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !redis-storage
              redis: *redis-connection

    Args:
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.

    Other Parameters:
        host (str): hostname of endpoint.
            This parameter is deprecated in favour of ``redis``.

        port (int): port on host.
            This parameter is deprecated in favour of ``redis``.

        password (str): redis database password
            This parameter is deprecated in favour of ``redis``.

        db (int) : db number
            This parameter is deprecated in favour of ``redis``.
    """

    yaml_tag = "!redis-storage"
    schema = os.path.join("storage", "redis.yaml")

    if TYPE_CHECKING:
        from buildgrid.server.redis.provider import RedisProvider

    def __new__(
        cls,
        _yaml_filename: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        password: Optional[str] = None,
        db: Optional[int] = None,
        redis: Optional["RedisProvider"] = None,
    ):
        # Import here so there is no global buildgrid dependency on redis
        from buildgrid.server.cas.storage.redis import RedisStorage
        from buildgrid.server.redis.provider import RedisProvider

        if redis is None:
            click.echo(
                click.style(
                    "Warning: Redis connection-related parameters for !redis-storage are deprecated. "
                    "Separately define a Redis connection using !redis-connection and reference it "
                    "in the `redis` key.",
                    fg="bright_yellow",
                )
            )
            redis = RedisProvider(
                host=host,
                port=port,
                password=password,
                db=db,
            )

        return RedisStorage(redis)


class Redis_Index(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.index.redis.RedisIndex`
    using the tag ``!redis-index``.

    Usage
        .. code:: yaml

            - !redis-index
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage
              redis: *redis

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be a storage object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.
    """

    yaml_tag = "!redis-index"
    schema = os.path.join("storage", "redis-index.yaml")

    if TYPE_CHECKING:
        from buildgrid.server.redis.provider import RedisProvider

    def __new__(cls, _yaml_filename: str, storage: StorageABC, redis: "RedisProvider"):
        # Import here so there is no global buildgrid dependency on redis
        from buildgrid.server.cas.storage.index.redis import RedisIndex

        return RedisIndex(redis=redis, storage=storage)


class Replicated_Storage(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.replicated.ReplicatedStorage`
    using the tag ``!replicated-storage``.

    Usage
        .. code:: yaml

            - !replicated-storage
              storages:
                - &storageA
                - &storageB


    Args:
        Storages (list): List of storages to mirror reads/writes for.
            A minimum of two storages is required.
    """

    yaml_tag = "!replicated-storage"
    schema = os.path.join("storage", "replicated.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storages: List[StorageABC],
    ):
        return ReplicatedStorage(storages)


class Remote(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.remote.RemoteStorage`
    using the tag ``!remote-storage``.

    Usage
        .. code:: yaml

            - !remote-storage
              url: https://storage:50052/
              instance-name: main
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert
                auth-token: /path/to/auth/token
                token-refresh-seconds: 6000
              channel-options:
                lb-policy-name: round_robin
              request-timeout: 15


    Args:
        url (str): URL to remote storage. If used with ``https``, needs credentials.
        instance_name (str): Instance of the remote to connect to.
        credentials (dict, optional): A dictionary in the form::

           tls-client-key: /path/to/client-key
           tls-client-cert: /path/to/client-cert
           tls-server-cert: /path/to/server-cert
           auth-token: /path/to/auth/token
           token-refresh-seconds (int): seconds to wait before reading the token from the file again

        channel-options (dict, optional): A dictionary of grpc channel options in the form::

          some-channel-option: channel_value
          other-channel-option: another-channel-value
        See https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
        for the valid channel options
        retries (int): Max number of times to retry (default 3). Backoff between retries is about 2^(N-1),
            where N is the number of attempts
        max_backoff (int): Maximum backoff in seconds (default 64)
        request_timeout (float): gRPC request timeout in seconds (default None)
    """

    yaml_tag = "!remote-storage"
    schema = os.path.join("storage", "remote.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        url: str,
        instance_name: str,
        credentials: Optional[ClientCredentials] = None,
        channel_options: Optional[Dict[str, Any]] = None,
        retries: int = 3,
        max_backoff: int = 64,
        request_timeout: Optional[float] = None,
    ):
        options_tuple = None
        if channel_options:
            # Transform the channel options into the format expected
            # by grpc channel creation
            parsed_options = []
            for option_name, option_value in channel_options.items():
                parsed_options.append((f"grpc.{option_name.replace('-', '_')}", option_value))
            options_tuple = tuple(parsed_options)
        else:
            options_tuple = ()

        if not _validate_url_and_credentials(url, credentials=credentials):
            sys.exit(-1)

        return RemoteStorage(
            remote=url,
            instance_name=instance_name,
            channel_options=options_tuple,
            credentials=credentials,
            retries=retries,
            max_backoff=max_backoff,
            request_timeout=request_timeout,
        )


class WithCache(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.with_cache.WithCacheStorage`
    using the tag ``!with-cache-storage``.

    Usage
        .. code:: yaml

            - !with-cache-storage
              cache:
                !lru-storage
                size: 2048M
              fallback:
                !disk-storage
                path: /opt/bgd/cas-storage
              defer-fallback-writes: no

    Args:
        cache (StorageABC): Storage instance to use as a cache
        fallback (StorageABC): Storage instance to use as a fallback on
            cache misses
        defer-fallback-writes (bool): If true, `commit_write` returns once
            writing to the cache is done, and the write into the fallback
            storage is done in a background thread
        fallback-writer-threads (int): The maximum number of threads to use
            for writing blobs into the fallback storage. Defaults to 20.
    """

    yaml_tag = "!with-cache-storage"
    schema = os.path.join("storage", "with-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        cache: StorageABC,
        fallback: StorageABC,
        defer_fallback_writes: bool = False,
        fallback_writer_threads: int = 20,
    ):
        return WithCacheStorage(
            cache,
            fallback,
            defer_fallback_writes=defer_fallback_writes,
            fallback_writer_threads=fallback_writer_threads,
        )


class Sharded(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.Sharded.ShardedStorage`
    using the tag ``!sharded-storage``.

    Usage
        .. code:: yaml

            - !sharded-storage
              shards:
                - name: A
                  storage: &storageA
                - name: B
                  storage: !lru-storage
                    size: 2048M
              thread-pool-size: 40


    Args:
        shards (list): List of dictionaries. The dictionaries are expected to
            have ``name`` and ``storage`` keys defining a storage shard. The
            name must be unique within a configuration and should be the same
            for any configuration using the same underlying storage.
        thread-pool-size (int|None): Number of worker threads to use for bulk
            methods to allow parallel requests to each shard. If not set no
            threadpool is created and requests are made serially to each shard.
    """

    class ShardType(TypedDict):
        name: str
        storage: StorageABC

    yaml_tag = "!sharded-storage"
    schema = os.path.join("storage", "sharded.yaml")

    def __new__(cls, _yaml_filename: str, shards: List[ShardType], thread_pool_size: Optional[int] = None):
        parsed_shards: Dict[str, StorageABC] = {}
        for shard in shards:
            if shard["name"] in parsed_shards:
                click.echo(
                    f"ERROR: Duplicate shard name '{shard['name']}'. Please fix the config.\n",
                    err=True,
                )
                sys.exit(-1)
            parsed_shards[shard["name"]] = shard["storage"]
        return ShardedStorage(parsed_shards, thread_pool_size)


_SizeLimitedStorageConfig = TypedDict("_SizeLimitedStorageConfig", {"max-size": int, "storage": StorageABC})


class SizeDifferentiated(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.size_differentiated.SizeDifferentiatedStorage`
    using the tag ``!size-differentiated-storage``.

    Usage
        .. code:: yaml

            - !size-differentiated-storage
              size-limited-storages:
                - max-size: 1M
                  storage:
                    !lru-storage
                    size: 2048M
              fallback:
                !disk-storage
                path: /opt/bgd/cas-storage
              thread-pool-size: 40

    Args:
        size_limited_storages (list): List of dictionaries. The dictionaries are expected
            to have ``max-size`` and ``storage`` keys, defining a storage provider to use
            to store blobs with size up to ``max-size``.
        fallback (StorageABC): Storage instance to use as a fallback for blobs which
            are too big for the options defined in ``size_limited_storages``.
        thread-pool-size (int|None): Number of worker threads to use for bulk
            methods to allow parallel requests to each storage. This thread pool
            is separate from the gRPC server thread-pool-size and should be tuned
            separately. If not set no threadpool is created and requests are made
            serially to each storage.
    """

    yaml_tag = "!size-differentiated-storage"
    schema = os.path.join("storage", "size-differentiated.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        size_limited_storages: List[_SizeLimitedStorageConfig],
        fallback: StorageABC,
        thread_pool_size: Optional[int] = None,
    ):
        parsed_storages: List[SizeLimitedStorageType] = []
        for storage_config in size_limited_storages:
            parsed_storages.append(
                {"max_size": _parse_size(storage_config["max-size"]), "storage": storage_config["storage"]}
            )
        return SizeDifferentiatedStorage(parsed_storages, fallback, thread_pool_size)


class SQL_Storage(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.sql.SQLStorage`
    using the tag ``!sql-storage``.

    Usage
        .. code:: yaml

            - !sql-storage
              sql: *sql
              sql_ro: *sql
    Args:
        sql (:class:`buildgrid.server.sql.provider.SqlProvider`): A configured SQL
            connection manager. This must be an object with an ``!sql-connection`` YAML tag.
        sql_ro (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for readonly backend transactions.
            If set, it should be configured with a replica of main DB using an optional but
            encouraged readonly role. Permission check is not executed by BuildGrid.
            If not set, readonly transactions are executed by `sql` object.
    """

    yaml_tag = "!sql-storage"
    schema = os.path.join("storage", "sql.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        sql: SqlProvider,
        sql_ro: Optional[SqlProvider] = None,
    ):
        return SQLStorage(sql, sql_ro_provider=sql_ro)


class SQLConnection(YamlFactory):
    """Generates :class:`buildgrid.server.sql.provider.SqlProvider` using the
    tag ``!sql-connection``.

    Example:
        .. code:: yaml

            - !sql-connection &sql
              connection_string: postgresql://bgd:insecure@database/bgd
              automigrate: yes
              connection_timeout: 5
              lock_timeout: 5
              pool-size: 5
              pool-timeout: 30
              max-overflow: 10

    """

    yaml_tag = "!sql-connection"
    schema = os.path.join("connections", "sql.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        automigrate: bool = False,
        connection_string: Optional[str] = None,
        connection_timeout: int = 5,
        lock_timeout: int = 5,
        connect_args: Optional[Dict[str, Any]] = None,
        max_overflow: Optional[int] = None,
        pool_pre_ping: Optional[bool] = None,
        pool_recycle: Optional[int] = None,
        pool_size: Optional[int] = None,
        pool_timeout: Optional[int] = None,
    ):
        return SqlProvider(
            automigrate=automigrate,
            connection_string=connection_string,
            connection_timeout=connection_timeout,
            lock_timeout=lock_timeout,
            connect_args=connect_args,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
        )


class SQLSchedulerConfig(YamlFactory):
    """Generates :class:`buildgrid.server.persistence.sql.impl.SQLDataStore` using
    the tag ``!sql-scheduler``.

    Example:

        .. code:: yaml

            - !sql-scheduler
              storage: *cas-storage
              sql: *sql
              pruner-job-max-age:
                days: 90

        This usage example assumes that the ``cas-storage`` reference refers to a
        storage backend, eg. ``!disk-storage``, and the ``sql`` reference refers
        to an SQL connection manager using ``!sql-connection``.

    Args:

        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`): Instance
            of storage to use for getting actions and storing job results. This must be
            an object constructed using a YAML tag ending in ``-storage``, for example
            ``!disk-storage``.

        sql (:class:`buildgrid.server.sql.provider.SqlProvider`): A configured SQL
            connection manager. This must be an object with an ``!sql-connection`` YAML tag.

        sql_ro (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for readonly backend transactions.
            If set, it should be configured with a replica of main DB using an optional but
            encouraged readonly role. Permission check is not executed by BuildGrid.
            If not set, readonly transactions are executed by `sql` object.

        sql_notifier (:class:`buildgrid.server.sql.provider.SqlProvider`): Similar to `sql`,
            but used for operation notifier.
            If not set, transactions are executed by `sql` object.

        property_keys (list): The platform property keys available to use in routing Actions to workers

        wildcard_property_keys (list): The platform property keys which can be set
            in Actions but are not used to select workers

        pruner_job_max_age (dict): Allow the storage to remove old entries by specifying the
            maximum amount of time that a row should be kept after its job finished. If
            this value is None, pruning is disabled and the background pruning thread
            is never created.

        pruner_period (dict): How often to attempt to remove old entries. If pruning
            is enabled (see above) and this value is None, it is set to 5 minutes by default.

        pruner_max_delete_window (int): Maximum number of records removed in a single
            cleanup pass. If pruning is enabled and this value is None, it is set to 10000
            by default. This allows to put a limit on the time that the database
            will be blocked on a single invocation of the cleanup routine.
            (A smaller value reduces the performance impact of removing entries,
            but makes the recovery of storage space slower.)

        queue_timeout_job_max_age (dict): If set, allow storage to abort jobs that have been queued
            for a long period of time.

        queue_timeout_period (dict): How often to find aged queued jobs. If not set,
            default to 5 minutes.

        queue_timeout_max_window (int): Maximum number of jobs to timeout per batch.
            If not set, default to 10000.

        action_cache (:class:`ActionCache`): Instance of action cache to use.

        action_browser_url (str): The base URL to use to generate Action Browser links to users.
            If a single Web interface serves several Buildgrid installations then this URL
            should include the namespace configured for the current Buildgrid installation,
            see https://gitlab.com/BuildGrid/bgd-browser#multi-buildgrid-setup.

        max_execution_timeout (int): The maximum time jobs are allowed to be in
            'OperationStage.EXECUTING'. This is a periodic check.
            When this time is exceeded in executing stage, the job will be cancelled.

        metering_service_client: Optional client to check whether resource usage of a client
            is above a predefined threshold

        bot_session_keepalive_timeout (int): The longest time (in seconds) we'll wait
            for a bot to send an update before it assumes it's dead. Defaults to 600s
            (10 minutes).

        logstream (Dict): Configuration options for connecting a logstream instance to ongoing
            jobs. Is a dict with items "url", "credentials", and "instance-name"

        asset_client (Optional[AssetClient]): Client of remote-asset service

        queued_action_retention_hours (Optional[float]): Minimum retention for queued actions in hours

        completed_action_retention_hours (Optional[float]): Minimum retention for completed actions in hours

        action_result_retention_hours (Optional[float]): Minimum retention for action results in hours

        max_job_attempts (int): The number of times a job will be assigned to workers before marking
            the job failed. Reassignment happens when a worker fails to report the outcome of a job.
            Minimum value allowed is 1. Default value is 5.

        priority_assignment_percentage (int): A value between 0 and 100 (inclusive) representing
            the percentage of workers to assign jobs to in priority order. The remainder will be
            assigned work in oldest-first order. Defaults to 100, or all work assigned in priority
            order.

    Other Parameters:

        connection_string (str): SQLAlchemy connection string to use for connecting to
            the database.
                This parameter is deprecated in favour of ``sql``.

        automigrate (bool): Whether to attempt to automatically upgrade an existing
            DB schema to the newest version (this will also create everything from
            scratch if given an empty database).
                This parameter is deprecated in favour of ``sql``.

        connection_timeout (int): Time to wait for an SQLAlchemy connection to be
            available in the pool before timing out.
                This parameter is deprecated in favour of ``sql``.

        lock_timeout (int): The timeout to use when the connection
            holds a lock in the database. This is supported only if the database
            backend is PostgresQL.
    """

    yaml_tag = "!sql-scheduler"
    schema = os.path.join("scheduler", "sql.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        sql: Optional[SqlProvider] = None,
        sql_ro: Optional[SqlProvider] = None,
        sql_notifier: Optional[SqlProvider] = None,
        connection_string: Optional[str] = None,
        automigrate: bool = False,
        connection_timeout: int = 5,
        lock_timeout: int = 5,
        property_keys: Optional[Union[str, List[str]]] = None,
        wildcard_property_keys: Optional[Union[str, List[str]]] = None,
        pruner_job_max_age: Optional[Dict[str, float]] = None,
        pruner_period: Optional[Dict[str, float]] = None,
        pruner_max_delete_window: Optional[int] = None,
        queue_timeout_job_max_age: Optional[Dict[str, float]] = None,
        queue_timeout_period: Optional[Dict[str, float]] = None,
        queue_timeout_max_window: Optional[int] = None,
        action_cache: Optional[ActionCacheABC] = None,
        action_browser_url: Optional[str] = None,
        max_execution_timeout: int = DEFAULT_MAX_EXECUTION_TIMEOUT,
        metering_service_client: Optional[metering.SyncMeteringServiceClient] = None,
        bot_session_keepalive_timeout: int = 600,
        logstream: Optional[Dict[str, Any]] = None,
        asset_client: Optional[AssetClient] = None,
        queued_action_retention_hours: Optional[float] = None,
        completed_action_retention_hours: Optional[float] = None,
        action_result_retention_hours: Optional[float] = None,
        max_job_attempts: int = 5,
        priority_assignment_percentage: int = 100,
        **kwargs,
    ):
        click.echo(
            f"SQLScheduler: storage={type(storage).__name__}, "
            f"automigrate={automigrate}, "
            f"connection_timeout={connection_timeout}, "
            f"pruner_job_max_age={pruner_job_max_age}, "
            f"pruner_period={pruner_period}, "
            f"pruner_max_delete_window={pruner_max_delete_window}"
        )
        click.echo(click.style("Creating an SQL scheduler backend\n", fg="green", bold=True))

        if bot_session_keepalive_timeout <= 0:
            msg = f"ERROR: bot_session_keepalive_timeout must be greater than zero: {bot_session_keepalive_timeout}"
            click.echo(click.style(msg, fg="red", bold=True), err=True)
            sys.exit(-1)

        if max_job_attempts < 1:
            msg = f"ERROR: max_job_attempts must be greater than zero: {max_job_attempts}"
            click.echo(click.style(msg, fg="red", bold=True), err=True)
            sys.exit(-1)

        try:
            # Create the full set of platform property keys, and also the set of
            # keys to actually use when matching Jobs to workers
            merged_property_keys = DEFAULT_PLATFORM_PROPERTY_KEYS.copy()
            match_properties = DEFAULT_PLATFORM_PROPERTY_KEYS.copy()
            if property_keys:
                if isinstance(property_keys, str):
                    match_properties.add(property_keys)
                    merged_property_keys.add(property_keys)
                else:
                    match_properties.update(property_keys)
                    merged_property_keys.update(property_keys)

            if wildcard_property_keys:
                if isinstance(wildcard_property_keys, str):
                    merged_property_keys.add(wildcard_property_keys)
                else:
                    merged_property_keys.update(wildcard_property_keys)

            pruning_options = (
                AgedJobHandlerOptions.from_config(pruner_job_max_age, pruner_period, pruner_max_delete_window)
                if pruner_job_max_age
                else None
            )
            queue_timeout_options = (
                AgedJobHandlerOptions.from_config(
                    queue_timeout_job_max_age, queue_timeout_period, queue_timeout_max_window
                )
                if queue_timeout_job_max_age
                else None
            )

            if sql is None:
                click.echo(
                    click.style(
                        "Warning: SQL-related parameters for !sql-index are deprecated. "
                        "Separately define an SQL connection using !sql-connection and reference it "
                        "in the `sql` key.",
                        fg="bright_yellow",
                    )
                )
                sql = SqlProvider(
                    automigrate=automigrate,
                    connection_string=connection_string,
                    connection_timeout=connection_timeout,
                    lock_timeout=lock_timeout,
                    connect_args=kwargs.get("connect_args"),
                    max_overflow=kwargs.get("max_overflow"),
                    pool_pre_ping=kwargs.get("pool_pre_ping"),
                    pool_recycle=kwargs.get("pool_recycle"),
                    pool_size=kwargs.get("pool_size"),
                    pool_timeout=kwargs.get("pool_timeout"),
                )
            sql_ro = sql_ro or sql
            sql_notifier = sql_notifier or sql

            logstream_url, logstream_credentials, logstream_instance = get_logstream_connection_info(logstream)
            logstream_channel: Optional[grpc.Channel] = None
            if logstream_url is not None:
                logstream_credentials = logstream_credentials or {}
                logstream_channel, _ = setup_channel(
                    logstream_url,
                    auth_token=None,
                    client_key=logstream_credentials.get("tls-client-key"),
                    client_cert=logstream_credentials.get("tls-client-cert"),
                    server_cert=logstream_credentials.get("tls-server-cert"),
                )

            return SQLDataStore(
                sql,
                storage,
                property_keys=merged_property_keys,
                match_properties=match_properties,
                pruning_options=pruning_options,
                queue_timeout_options=queue_timeout_options,
                sql_ro_provider=sql_ro,
                sql_notifier_provider=sql_notifier,
                action_cache=action_cache,
                action_browser_url=action_browser_url,
                max_execution_timeout=max_execution_timeout,
                metering_client=metering_service_client,
                bot_session_keepalive_timeout=bot_session_keepalive_timeout,
                logstream_channel=logstream_channel,
                logstream_instance=logstream_instance,
                asset_client=asset_client,
                queued_action_retention_hours=queued_action_retention_hours,
                completed_action_retention_hours=completed_action_retention_hours,
                action_result_retention_hours=action_result_retention_hours,
                priority_assignment_percentage=priority_assignment_percentage,
            )

        except TypeError as type_error:
            click.echo(type_error, err=True)
            sys.exit(-1)


class SQLDataStoreConfig(YamlFactory):
    """Generates :class:`buildgrid.server.persistence.sql.impl.SQLDataStore` using
    the tag ``!sql-data-store``.

    .. warning::
        This is deprecated and only used for compatibility with old configs.

    Usage
        .. code:: yaml

            - !sql-data-store
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage
              connection_string: postgresql://bgd:insecure@database/bgd
              automigrate: yes
              connection_timeout: 5

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`): Instance
            of storage to use for getting actions and storing job results. This must be
            an object constructed using a YAML tag ending in ``-storage``, for example
            ``!disk-storage``.
        connection_string (str): SQLAlchemy connection string to use for connecting
            to the database.
        automigrate (bool): Whether to attempt to automatically upgrade an existing
            DB schema to the newest version (this will also create everything from
            scratch if given an empty database).
        connection_timeout (int): Time to wait for an SQLAlchemy connection to be
            available in the pool before timing out.
        lock_timeout (int): The timeout to use when the connection
            holds a lock in the database. This is supported only if the database
            backend is PostgresQL.

    """

    yaml_tag = "!sql-data-store"
    schema = os.path.join("scheduler", "sql.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        connection_string: Optional[str] = None,
        automigrate: bool = False,
        connection_timeout: int = 5,
        lock_timeout: int = 5,
        **kwargs,
    ):
        click.echo(
            click.style(
                "Warning: !sql-data-store YAML tag is deprecated. Use !sql-scheduler instead.", fg="bright_yellow"
            )
        )
        click.echo(
            f"SQLScheduler: storage={type(storage).__name__}, "
            f"automigrate={automigrate}, "
            f"connection_timeout={connection_timeout}"
        )
        click.echo(click.style("Creating an SQL scheduler backend\n", fg="green", bold=True))
        try:
            sql = SqlProvider(
                automigrate=automigrate,
                connection_string=connection_string,
                connection_timeout=connection_timeout,
                lock_timeout=lock_timeout,
                connect_args=kwargs.get("connect_args"),
                max_overflow=kwargs.get("max_overflow"),
                pool_pre_ping=kwargs.get("pool_pre_ping"),
                pool_recycle=kwargs.get("pool_recycle"),
                pool_size=kwargs.get("pool_size"),
                pool_timeout=kwargs.get("pool_timeout"),
            )
            return SQLDataStore(sql, storage)
        except TypeError as type_error:
            click.echo(type_error, err=True)
            sys.exit(-1)


class MemorySchedulerConfig(YamlFactory):
    """Generates :class:`buildgrid.server.persistence.mem.impl.MemoryDataStore` using
    the tag ``!memory-scheduler``.

    Usage
        .. code:: yaml

            - !memory-scheduler
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`): Instance
            of storage to use for getting actions and storing job results. This must be
            an object constructed using a YAML tag ending in ``-storage``, for example
            ``!disk-storage``.

    """

    yaml_tag = "!memory-scheduler"
    schema = os.path.join("scheduler", "memory.yaml")

    def __new__(cls, _yaml_filename: str, storage: StorageABC):
        click.echo(
            click.style(
                "Warning: !memory-scheduler and !memory-data-store YAML tags have deprecated. "
                "Use !sql-scheduler instead. A SQL Scheduler with a SQLite temporary file will be used instead.",
                fg="bright_yellow",
            )
        )
        click.echo(f"MemoryScheduler: storage={type(storage).__name__}")
        click.echo(click.style("Creating an in-memory scheduler backend\n", fg="green", bold=True))
        return SQLDataStore(storage=storage, sql_provider=SqlProvider())


class MemoryDataStoreConfig(YamlFactory):
    """Generates :class:`buildgrid.server.persistence.mem.impl.MemoryDataStore` using
    the tag ``!memory-data-store``.

    .. warning::
        This is deprecated and only used for compatibility with old configs. Use
        :class:`MemorySchedulerConfig` instead.

    Usage
        .. code:: yaml

            - !memory-data-store
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`): Instance
            of storage to use for getting actions and storing job results. This must be
            an object constructed using a YAML tag ending in ``-storage``, for example
            ``!disk-storage``.

    """

    yaml_tag = "!memory-data-store"
    schema = os.path.join("scheduler", "memory.yaml")

    def __new__(cls, _yaml_filename: str, storage: StorageABC):
        click.echo(
            click.style(
                "Warning: !memory-scheduler and !memory-data-store YAML tags have deprecated. "
                "Use !sql-scheduler instead. A SQL Scheduler with a SQLite temporary file will be used instead.",
                fg="bright_yellow",
            )
        )
        click.echo(f"MemoryScheduler: storage={type(storage).__name__}")
        click.echo(click.style("Creating an in-memory scheduler backend\n", fg="green", bold=True))
        return SQLDataStore(storage=storage, sql_provider=SqlProvider())


class SQL_Index(YamlFactory):
    """Generates :class:`buildgrid.server.cas.storage.index.sql.SQLIndex`
    using the tag ``!sql-index``.

    Usage
        .. code:: yaml

            - !sql-index
              # This assumes that a storage instance is defined elsewhere
              # with a `&cas-storage` anchor
              storage: *cas-storage
              sql: *sql
              window-size: 1000
              inclause-limit: -1
              fallback-on-get: no
              max-inline-blob-size: 256
              refresh-accesstime-older-than: 0

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be a storage object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        connection_string (str): SQLAlchemy connection string
        automigrate (bool): Attempt to automatically upgrade an existing DB schema to
            the newest version.
        window_size (uint): Maximum number of blobs to fetch in one SQL operation
            (larger resultsets will be automatically split into multiple queries)
        inclause_limit (int): If nonnegative, overrides the default number of variables
            permitted per "in" clause. See the buildgrid.server.cas.storage.index.sql.SQLIndex
            comments for more details.
        fallback_on_get (bool): By default, the SQL Index only fetches blobs from the
            underlying storage if they're present in the index on ``get_blob``/``bulk_read_blobs``
            requests to minimize interactions with the storage. If this is set, the index
            instead checks the underlying storage directly on ``get_blob``/``bulk_read_blobs``
            requests, then loads all blobs found into the index.
        max_inline_blob_size (int): Blobs of this size or smaller are stored directly in the index
            and not in the backing storage (must be nonnegative).
        refresh-accesstime-older-than (int): When reading a blob, its access timestamp will not be
            updated if the current time is not at least refresh-accesstime-older-than seconds newer
            than the access timestamp. Set this to reduce load associated with frequent timestamp updates.
    """

    yaml_tag = "!sql-index"
    schema = os.path.join("storage", "sql-index.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        connection_string: Optional[str] = None,
        sql: Optional[SqlProvider] = None,
        automigrate: bool = False,
        window_size: int = 1000,
        inclause_limit: int = -1,
        fallback_on_get: bool = False,
        max_inline_blob_size: int = 0,
        refresh_accesstime_older_than: int = 0,
        **kwargs,
    ):
        storage_type = type(storage).__name__
        click.echo(
            f"SQLIndex: storage={storage_type}, "
            f"automigrate={automigrate}, "
            f"window_size={window_size}, "
            f"inclause_limit={inclause_limit}, "
            f"fallback_on_get={fallback_on_get}"
        )
        click.echo(click.style(f"Creating an SQL CAS Index for {storage_type}\n", fg="green", bold=True))
        if sql is None:
            click.echo(
                click.style(
                    "Warning: SQL-related parameters for !sql-index are deprecated. "
                    "Separately define an SQL connection using !sql-connection and reference it "
                    "in the `sql` key.",
                    fg="bright_yellow",
                )
            )
            sql = SqlProvider(
                automigrate=automigrate,
                connection_string=connection_string,
                connect_args=kwargs.get("connect_args"),
                max_overflow=kwargs.get("max_overflow"),
                pool_pre_ping=kwargs.get("pool_pre_ping"),
                pool_recycle=kwargs.get("pool_recycle"),
                pool_size=kwargs.get("pool_size"),
                pool_timeout=kwargs.get("pool_timeout"),
            )
        return SQLIndex(
            sql,
            storage,
            window_size=window_size,
            inclause_limit=inclause_limit,
            fallback_on_get=fallback_on_get,
            max_inline_blob_size=max_inline_blob_size,
            refresh_accesstime_older_than=refresh_accesstime_older_than,
        )


class Execution(YamlFactory):
    """Generates :class:`buildgrid.server.execution.service.ExecutionService`
    using the tag ``!execution``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !execution
              action-cache: *remote-cache
              action-browser-url: http://localhost:8080
              scheduler: *state-database
              property-keys:
                - runnerType
              wildcard-property-keys:
                - chrootDigest
              operation-stream-keepalive-timeout: 600
              bot-session-keepalive-timeout: 600
              endpoints:
                - execution
                - operations
                - bots
              discard-unwatched-jobs: no
              max-execution-timeout: 7200
              max-list-operations-page-size: 1000

    Args:
        scheduler(:class:`SQLDataStore`): Instance of data store to use for the scheduler's state.
        operation_stream_keepalive_timeout (int): The longest time (in seconds)
            we'll wait before sending the current status in an Operation response
            stream of an `Execute` or `WaitExecution` request. Defaults to 600s
            (10 minutes).
        endpoints (list): List of service/endpoint types to enable. Possible services are
            ``execution``, ``operations``, and ``bots``. By default all three are enabled.
        max_list_operations_page_size (int): The maximum number of operations that can
            be returned in a ListOperations response. A page token will be returned
            with the response to allow the client to get the next page of results.

        property_keys: Deprecated field. Set this in the scheduler.
        wildcard_property_keys: Deprecated field. Set this in the scheduler.
        storage: Deprecated field. All internal state is now managed by the provided scheduler.
        sql: Deprecated field. All internal state is now managed by the provided scheduler.
        discard_unwatched_jobs: Deprecated field. Unused.
        permissive_bot_session: Deprecated field. UpdateBotSession is always validated.
        action_cache: Deprecated field. Set this in the scheduler.
        action_browser_url: Deprecated field. Set this in the scheduler.
        max_execution_timeout: Deprecated field. Set this in the scheduler.
        metering_service_client: Deprecated field. Set this in the scheduler.
        bot_session_keepalive_timeout: Deprecated field. Set this in the scheduler.
        priority_assignment_percentage: Deprecated field. Set this in the scheduler.
    """

    yaml_tag = "!execution"
    schema = os.path.join("services", "execution.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        operation_stream_keepalive_timeout=600,
        endpoints=ServiceName.default_services(),
        max_list_operations_page_size=DEFAULT_MAX_LIST_OPERATION_PAGE_SIZE,
        # Deprecated options kept to support migrations.
        data_store=None,
        scheduler=None,
        property_keys=None,
        wildcard_property_keys=None,
        logstream=None,
        storage: Optional[StorageABC] = None,
        sql: Optional[SqlProvider] = None,
        action_cache: Optional[ActionCacheABC] = None,
        action_browser_url: Optional[str] = None,
        permissive_bot_session: Optional[bool] = None,
        discard_unwatched_jobs: Optional[bool] = None,
        metering_service_client: Optional[metering.SyncMeteringServiceClient] = None,
        max_execution_timeout: Optional[int] = None,
        bot_session_keepalive_timeout: Optional[int] = None,
        priority_assignment_percentage: Optional[int] = None,
    ):
        scheduler = _validate_scheduler(cls, scheduler, data_store, fallback=True, storage=storage)
        if isinstance(action_cache, ActionCache):
            click.echo(
                click.style(
                    "Warning: Passing an ActionCache instance (!action-cache) to an Execution "
                    "service is deprecated. Use a cache backend such as !lru-action-cache instead.",
                    fg="bright_yellow",
                )
            )

        click.echo(
            "Execution: "
            f"scheduler={type(scheduler).__name__}, "
            f"max_execution_timeout={max_execution_timeout}, "
            f"operation_stream_keepalive_timeout={operation_stream_keepalive_timeout}, "
            f"bot_session_keepalive_timeout={bot_session_keepalive_timeout}"
        )

        if metering_service_client:
            click.echo(f"Metering service client base url: {metering_service_client._base_url}")

        click.echo(f"Enabled endpoints:\n{yaml.dump(list(endpoints)).strip()}")

        click.echo(click.style(f"Creating an Execution service using {scheduler}\n", fg="green", bold=True))

        if storage is not None:
            click.echo(
                click.style(
                    "Warning: Separately defining a storage for execution is deprecated. "
                    "All actions now happen through the scheduler. Ignoring option.",
                    fg="bright_yellow",
                )
            )

        if sql is not None:
            click.echo(
                click.style(
                    "Warning: Separately defining a SQL connection for execution is deprecated. "
                    "All actions now happen through the scheduler. Ignoring option.",
                    fg="bright_yellow",
                )
            )

        if permissive_bot_session is not None:
            click.echo(
                click.style(
                    "Warning: Permissive Bot Session mode is deprecated. "
                    "All session will be validated when calling UpdateBotSession.",
                    fg="bright_yellow",
                )
            )

        deprecated_msg = "option is deprecated. Set this value in the scheduler instead. Overriding scheduler value."

        if property_keys or wildcard_property_keys:
            click.echo(click.style(f"Warning: Property Keys {deprecated_msg}", fg="bright_yellow"))
            # Create the full set of platform property keys, and also the set of
            # keys to actually use when matching Jobs to workers
            merged_property_keys = DEFAULT_PLATFORM_PROPERTY_KEYS.copy()
            match_properties = DEFAULT_PLATFORM_PROPERTY_KEYS.copy()
            if property_keys:
                if isinstance(property_keys, str):
                    match_properties.add(property_keys)
                    merged_property_keys.add(property_keys)
                else:
                    match_properties.update(property_keys)
                    merged_property_keys.update(property_keys)

            if wildcard_property_keys:
                if isinstance(wildcard_property_keys, str):
                    merged_property_keys.add(wildcard_property_keys)
                else:
                    merged_property_keys.update(wildcard_property_keys)
            click.echo("Supported platform property keys:\n" f"{yaml.dump(list(merged_property_keys)).strip()}")
            scheduler.property_keys = merged_property_keys
            scheduler.match_properties = match_properties

        if action_cache is not None:
            click.echo(click.style(f"Warning: Action Cache {deprecated_msg}", fg="bright_yellow"))
            scheduler.action_cache = action_cache

        if action_browser_url is not None:
            click.echo(click.style(f"Warning: Action Browser URL {deprecated_msg}", fg="bright_yellow"))
            scheduler.action_browser_url = action_browser_url

        if metering_service_client is not None:
            click.echo(click.style(f"Warning: Metering Service {deprecated_msg}", fg="bright_yellow"))
            scheduler.metering_client = metering_service_client

        if max_execution_timeout is not None:
            click.echo(click.style(f"Warning: Execution Timeout {deprecated_msg}", fg="bright_yellow"))
            scheduler.max_execution_timeout = max_execution_timeout

        if bot_session_keepalive_timeout is not None:
            if bot_session_keepalive_timeout <= 0:
                click.echo(
                    click.style(
                        "ERROR: bot_session_keepalive_timeout must be greater "
                        f"than zero: {bot_session_keepalive_timeout}",
                        fg="red",
                        bold=True,
                    ),
                    err=True,
                )
                sys.exit(-1)
            click.echo(click.style(f"Warning: Action Cache {deprecated_msg}", fg="bright_yellow"))
            scheduler.bot_session_keepalive_timeout = bot_session_keepalive_timeout

        if logstream is not None:
            click.echo(click.style(f"Warning: Logstream {deprecated_msg}", fg="bright_yellow"))
            logstream_url, logstream_credentials, logstream_instance = get_logstream_connection_info(logstream)
            if logstream_url is not None:
                logstream_credentials = logstream_credentials or {}
                logstream_channel, _ = setup_channel(
                    logstream_url,
                    auth_token=None,
                    client_key=logstream_credentials.get("tls-client-key"),
                    client_cert=logstream_credentials.get("tls-client-cert"),
                    server_cert=logstream_credentials.get("tls-server-cert"),
                )
                scheduler.logstream_instance = logstream_instance
                scheduler.logstream_channel = logstream_channel

        if priority_assignment_percentage is not None:
            click.echo(click.style(f"Warning: Priority Assignment Percentage {deprecated_msg}", fg="bright_yellow"))
            scheduler.job_assigner.priority_assignment_percentage = priority_assignment_percentage

        return ExecutionController(
            scheduler,
            operation_stream_keepalive_timeout=operation_stream_keepalive_timeout,
            services=endpoints,
            max_list_operations_page_size=max_list_operations_page_size,
        )


class Bots(YamlFactory):
    """Generates :class:`buildgrid.server.bots.instance.BotsInterface`
    using the tag ``!bots``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !bots
              action-cache: *remote-cache
              scheduler: *state-database
              bot-session-keepalive-timeout: 600
              permissive-bot-session: yes

    Args:
        scheduler(:class:`SQLDataStore`): Instance of data store to use for the scheduler's state.
        priority_assignment_percentage (int): A value between 0 and 100 (inclusive) representing
            the percentage of workers to assign jobs to in priority order. The remainder will be
            assigned work in oldest-first order. Defaults to 100, or all work assigned in priority
            order.

        storage: Deprecated field. All internal state is now managed by the provided scheduler.
        sql: Deprecated field. All internal state is now managed by the provided scheduler.
        action_cache: Deprecated field. Set this in the scheduler.
        bot_session_keepalive_timeout: Deprecated field. Set this in the scheduler.
        permissive_bot_session: Deprecated field. UpdateBotSession is always validated
        metering_service_client: Deprecated field. Set this in the scheduler.
    """

    yaml_tag = "!bots"
    schema = os.path.join("services", "bots.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: Optional[StorageABC] = None,
        sql: Optional[SqlProvider] = None,
        action_cache=None,
        bot_session_keepalive_timeout: Optional[int] = None,
        data_store=None,
        scheduler=None,
        permissive_bot_session: Optional[bool] = None,
        logstream=None,
        metering_service_client: Optional[metering.SyncMeteringServiceClient] = None,
        priority_assignment_percentage: int = 100,
    ):
        scheduler = _validate_scheduler(cls, scheduler, data_store)
        if isinstance(action_cache, ActionCache):
            click.echo(
                click.style(
                    "Warning: Passing an ActionCache instance (!action-cache) to an Execution "
                    "service is deprecated. Use a cache backend such as !lru-action-cache instead.",
                    fg="bright_yellow",
                )
            )

        click.echo(
            f"Bots: storage={type(storage).__name__}, "
            f"scheduler={type(scheduler).__name__}, "
            f"bot_session_keepalive_timeout={bot_session_keepalive_timeout}"
        )

        click.echo(click.style(f"Creating a Bots service using {scheduler}\n", fg="green", bold=True))

        if storage is not None:
            click.echo(
                click.style(
                    "Warning: Separately defining a storage for bots is deprecated. "
                    "All actions now happen through the scheduler. Ignoring option.",
                    fg="bright_yellow",
                )
            )

        if sql is not None:
            click.echo(
                click.style(
                    "Warning: Separately defining a SQL connection for bots is deprecated. "
                    "All actions now happen through the scheduler. Ignoring option.",
                    fg="bright_yellow",
                )
            )

        if permissive_bot_session is not None:
            click.echo(
                click.style(
                    "Warning: Permissive Bot Session mode is deprecated. "
                    "All session will be validated when calling UpdateBotSession.",
                    fg="bright_yellow",
                )
            )

        deprecated_msg = "option is deprecated. Set this value in the scheduler instead. Overriding scheduler value."
        if action_cache is not None:
            click.echo(click.style(f"Warning: Action Cache {deprecated_msg}", fg="bright_yellow"))
            scheduler.action_cache = action_cache

        if bot_session_keepalive_timeout is not None:
            if bot_session_keepalive_timeout <= 0:
                click.echo(
                    click.style(
                        "ERROR: bot_session_keepalive_timeout "
                        f"must be greater than zero: {bot_session_keepalive_timeout}",
                        fg="red",
                        bold=True,
                    ),
                    err=True,
                )
                sys.exit(-1)
            click.echo(click.style(f"Warning: Bot Keepalive Timeout {deprecated_msg}", fg="bright_yellow"))
            scheduler.bot_session_keepalive_timeout = bot_session_keepalive_timeout

        if metering_service_client is not None:
            click.echo(click.style(f"Warning: Metering Service {deprecated_msg}", fg="bright_yellow"))
            scheduler.metering_client = metering_service_client

        if logstream is not None:
            click.echo(click.style(f"Warning: Logstream {deprecated_msg}", fg="bright_yellow"))
            logstream_url, logstream_credentials, logstream_instance = get_logstream_connection_info(logstream)
            if logstream_url is not None:
                logstream_credentials = logstream_credentials or {}
                logstream_channel, _ = setup_channel(
                    logstream_url,
                    auth_token=None,
                    client_key=logstream_credentials.get("tls-client-key"),
                    client_cert=logstream_credentials.get("tls-client-cert"),
                    server_cert=logstream_credentials.get("tls-server-cert"),
                )
                scheduler.logstream_instance = logstream_instance
                scheduler.logstream_channel = logstream_channel

        deprecated_msg = "option is deprecated. Set this value in the scheduler instead. Overriding scheduler value."
        if priority_assignment_percentage is not None:
            click.echo(click.style(f"Warning: Priority Assignment Percentage {deprecated_msg}", fg="bright_yellow"))
            scheduler.job_assigner.priority_assignment_percentage = priority_assignment_percentage

        return BotsInterface(scheduler)


class Action(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.service.ActionCacheService`
    using the tag ``!action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !action-cache
              cache: *lru-cache

    Args:
        cache (ActionCacheABC): The ActionCache backend to use for this cache.

    """

    yaml_tag = "!action-cache"
    schema = os.path.join("services", "action-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: Optional[StorageABC] = None,
        max_cached_refs: Optional[int] = None,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
        cache: Optional[ActionCacheABC] = None,
    ):
        if cache is None:
            # Old-style configuration, create an LRU Action Cache
            click.echo(
                click.style(
                    "Warning: !action-cache YAML tag now takes a `cache` key. Old-style "
                    "config should be changed to use an !lru-action-cache in the `cache` key.",
                    fg="bright_yellow",
                )
            )
            storage_type = type(storage).__name__
            click.echo(
                f"LruActionCache: storage={storage_type}, "
                f"max_cached_refs={max_cached_refs}, "
                f"allow_updates={allow_updates}, "
                f"cache_failed_actions={cache_failed_actions}"
            )
            click.echo(
                click.style(f"Creating an LruActionCache using `{storage_type}` storage\n", fg="green", bold=True)
            )
            cache = LruActionCache(storage, max_cached_refs, allow_updates, cache_failed_actions)  # type: ignore

        cache_type = type(cache).__name__
        click.echo(f"ActionCache: cache={cache_type}")
        click.echo(click.style(f"Creating an ActionCache service using `{cache_type}`\n", fg="green", bold=True))
        return ActionCache(cache)


class MirroredCacheFactory(YamlFactory):
    """Generates:class:`buildgrid.server.actioncache.caches.mirrored_cache.MirroredCache`
    using the tag ``!mirrored-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !mirrored-action-cache
              first: *first-action-cache
              second: *second-action-cache
    """

    yaml_tag = "!mirrored-action-cache"
    schema = os.path.join("caches", "mirrored-cache.yaml")

    def __new__(cls, _yaml_filename: str, first: ActionCacheABC, second: ActionCacheABC):
        return MirroredCache(first=first, second=second)


class WithCacheAction(YamlFactory):
    """Generates:class:`buildgrid.server.actioncache.caches.with_cache.WithCacheActionCache`
    using the tag ``!with-cache-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !with-cache-action-cache
              storage: *cas-storage
              cache: *cache-ac
              fallback: *fallback-ac

    Args:
        cache (ActionCacheABC): ActionCache instance to use as a local cache
        fallback (ActionCacheABC): ActionCache instance to use as a fallback on
            local cache misses
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit
            code) actions. Default to ``True``.
    """

    yaml_tag = "!with-cache-action-cache"
    schema = os.path.join("caches", "with-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        cache: ActionCacheABC,
        fallback: ActionCacheABC,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
    ):
        return WithCacheActionCache(
            cache, fallback, allow_updates=allow_updates, cache_failed_actions=cache_failed_actions
        )


class LruAction(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.caches.lru_cache.LruActionCache`
    using the tag ``!lru-action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !lru-action-cache
              storage: *cas-storage
              max-cached-refs: 1024
              cache-failed-actions: yes
              allow-updates: yes

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use.
        max_cached_refs(int): Max number of cached actions.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit
            code) actions. Default to ``True``.

    """

    yaml_tag = "!lru-action-cache"
    schema = os.path.join("caches", "lru-action-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        max_cached_refs: int,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
    ):
        storage_type = type(storage).__name__
        click.echo(
            f"LruActionCache: storage={storage_type}, max_cached_refs={max_cached_refs}, "
            f"allow_updates={allow_updates}, cache_failed_actions={cache_failed_actions}"
        )
        click.echo(click.style(f"Creating an LruActionCache using `{storage_type}` storage\n", fg="green", bold=True))
        return LruActionCache(storage, max_cached_refs, allow_updates, cache_failed_actions)


class S3Action(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.caches.s3_cache.S3ActionCache`
    using the tag ``!s3action-cache``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !s3action-cache
              storage: *cas-storage
              allow-updates: yes
              cache-failed-actions: yes
              entry-type: action-result-digest
              migrate-entries: no
              bucket: bgd-action-cache
              endpoint: http://localhost:9000/
              access-key: !read-file /var/bgd/s3-access-key
              secret-key: !read-file /var/bgd/s3-secret-key

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit code)
            actions. Default to ``True``.
        entry_type (str): whether entries in S3 will store an ``'action-result'``
            or an ``'action-result-digest'`` (default).
        migrate_entries (bool): Whether to automatically update the values of
            entries that contain a different type of value to `entry_type` as
            they are queried. Default to ``False``.
        bucket (str): Name of bucket
        endpoint (str): URL of endpoint.
        access-key (str): S3-ACCESS-KEY
        secret-key (str): S3-SECRET-KEY

    """

    yaml_tag = "!s3action-cache"
    schema = os.path.join("services", "s3-action-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
        entry_type: Optional[str] = None,
        migrate_entries: Optional[bool] = False,
        bucket: Optional[str] = None,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        storage_type = type(storage).__name__
        cache_entry_type = None

        if entry_type is None or entry_type.lower() == "action-result-digest":
            cache_entry_type = ActionCacheEntryType.ACTION_RESULT_DIGEST
        elif entry_type.lower() == "action-result":
            cache_entry_type = ActionCacheEntryType.ACTION_RESULT
        else:
            click.echo(
                click.style(f"ERROR: entry_type value is not valid: {cache_entry_type}", fg="red", bold=True), err=True
            )
            sys.exit(-1)

        click.echo(
            f"S3ActionCache: storage={storage_type}, allow_updates={allow_updates}, "
            f"cache_failed_actions={cache_failed_actions}, bucket={bucket}, "
            f"entry_type={entry_type}, migrate_entries={migrate_entries}, "
            f"endpoint={endpoint}"
        )
        click.echo(
            click.style(f"Creating an S3ActionCache service using `{storage_type}` storage\n", fg="green", bold=True)
        )

        from botocore.config import Config as BotoConfig  # pylint: disable=import-outside-toplevel

        boto_config = BotoConfig(
            user_agent=S3_USERAGENT_NAME,
            connect_timeout=S3_TIMEOUT_CONNECT,
            read_timeout=S3_TIMEOUT_READ,
            retries={"max_attempts": S3_MAX_RETRIES},
        )

        return S3ActionCache(
            storage,
            allow_updates=allow_updates,
            cache_failed_actions=cache_failed_actions,
            entry_type=cache_entry_type,
            migrate_entries=migrate_entries,
            bucket=bucket,
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=boto_config,
        )


class RemoteAction(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.caches.remote.RemoteActionCache`
    using the tag ``!remote-action-cache``.

    Usage
        .. code:: yaml

            - !remote-action-cache
              url: https://action-cache:50053
              instance-name: main
              credentials:
                tls-server-key: !expand-path ~/.config/buildgrid/server.key
                tls-server-cert: !expand-path ~/.config/buildgrid/server.cert
                tls-client-certs: !expand-path ~/.config/buildgrid/client.cert
                auth-token: /path/to/auth/token
                token-refresh-seconds: 6000
              channel-options:
                lb-policy-name: round_robin

    Args:
        url (str): URL to remote action cache
        instance_name (str): Instance of the remote to connect to.
        credentials (dict, optional): A dictionary in the form::

           tls-client-key: /path/to/client-key
           tls-client-cert: /path/to/client-cert
           tls-server-cert: /path/to/server-cert
           auth-token: /path/to/auth/token
           token-refresh-seconds (int): seconds to wait before reading the token from the file again

        channel-options (dict, optional): A dictionary of grpc channel options in the form::

          some-channel-option: channel_value
          other-channel-option: another-channel-value
        See https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
        for the valid channel options

    """

    yaml_tag = "!remote-action-cache"
    schema = os.path.join("services", "remote-action-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        url: str,
        instance_name: str,
        retries: int = 3,
        max_backoff: int = 64,
        request_timeout: Optional[float] = None,
        credentials: Optional[ClientCredentials] = None,
        channel_options: Optional[Dict[str, Any]] = None,
    ):
        options_tuple = None
        if channel_options:
            # Transform the channel options into the format expected
            # by grpc channel creation
            parsed_options = []
            for option_name, option_value in channel_options.items():
                parsed_options.append((f"grpc.{option_name.replace('-', '_')}", option_value))
            options_tuple = tuple(parsed_options)
        else:
            options_tuple = ()

        if not _validate_url_and_credentials(url, credentials=credentials):
            sys.exit(-1)

        click.echo(f"RemoteActionCache: url={url}, instance_name={instance_name}, ")
        click.echo(click.style(f"Creating an RemoteActionCache service for {url}\n", fg="green", bold=True))

        return RemoteActionCache(
            url,
            instance_name,
            retries,
            max_backoff,
            request_timeout,
            channel_options=options_tuple,
            credentials=credentials,
        )


class WriteOnceAction(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.caches.write_once_cache.WriteOnceActionCache`
    using the tag ``!write-once-action-cache``.

    This allows a single update for a given key, essentially making it possible
    to create immutable ActionCache entries, rather than making the cache read-only
    as the ``allow-updates`` property of other ActionCache implementations does.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !write-once-action-cache
              action-cache: *remote-cache

    Args:
        action_cache (ActionCache): The action cache instance to make immutable.

    """

    yaml_tag = "!write-once-action-cache"
    schema = os.path.join("services", "write-once-action-cache.yaml")

    def __new__(cls, _yaml_filename: str, action_cache):
        return WriteOnceActionCache(action_cache)


class RedisAction(YamlFactory):
    """Generates :class:`buildgrid.server.actioncache.caches.redis_cache.RedisActionCache`
    using the tag ``!redis-action-cache``.

    This creates an Action Cache which stores the mapping from Action digests to
    ActionResults in Redis.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !redis-action-cache
              storage: *cas-storage
              allow-updates: yes
              cache-failed-actions: yes
              entry-type: action-result-digest
              migrate-entries: no
              redis: *redis-connection

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
        allow_updates(bool): Allow updates pushed to the Action Cache.
            Defaults to ``True``.
        cache_failed_actions(bool): Whether to store failed (non-zero exit code)
            actions. Default to ``True``.
        entry_type (str): whether entries in Redis will store an ``'action-result'``
            or an ``'action-result-digest'`` (default).
        migrate_entries (bool): Whether to automatically update the values of
            entries that contain a different type of value to `entry_type` as
            they are queried. Default to ``False``.
        redis (:class:`buildgrid.server.redis.provider.RedisProvider`): A configured Redis
            connection manager. This must be an object with an ``!redis-connection`` YAML tag.

    Other Parameters:
        host (str): The hostname of the Redis server to use.
            This parameter is deprecated in favour of ``redis``.

        port (int): The port that Redis is served on.
            This parameter is deprecated in favour of ``redis``.

        db (int): The Redis database number to use.
            This parameter is deprecated in favour of ``redis``.

        dns-srv-record (str): Domain name of SRV record used to discover host/port
            This parameter is deprecated in favour of ``redis``.

        sentinel-master-name (str): Service name of Redis master instance, used
            in a Redis sentinel configuration
            This parameter is deprecated in favour of ``redis``.

        retries (int): Max number of times to retry (default 3). Backoff between retries is about 2^(N-1),
            where N is the number of attempts
            This parameter is deprecated in favour of ``redis``.
    """

    yaml_tag = "!redis-action-cache"
    schema = os.path.join("caches", "redis-action-cache.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        host: Optional[str] = None,
        port: Optional[int] = None,
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
        entry_type: Optional[str] = None,
        migrate_entries: Optional[bool] = False,
        password: Optional[str] = None,
        db: int = 0,
        dns_srv_record: Optional[str] = None,
        sentinel_master_name: Optional[str] = None,
        retries: int = 3,
        redis: Optional[Any] = None,  # Should be Optional[RedisProvider] but we are trying to
        # avoid a global dependency on redis. Parser should have validated this already and we
        # assert below
    ):
        cache_entry_type = None
        if entry_type is None or entry_type.lower() == "action-result-digest":
            cache_entry_type = ActionCacheEntryType.ACTION_RESULT_DIGEST
        elif entry_type.lower() == "action-result":
            cache_entry_type = ActionCacheEntryType.ACTION_RESULT
        else:
            click.echo(
                click.style(f"ERROR: entry_type value is not valid: {cache_entry_type}", fg="red", bold=True), err=True
            )
            sys.exit(-1)
        # Import here so there is no global buildgrid dependency on redis
        from buildgrid.server.actioncache.caches.redis_cache import RedisActionCache
        from buildgrid.server.redis.provider import RedisProvider

        try:
            if redis is None:
                click.echo(
                    click.style(
                        "Warning: Redis connection-related parameters for !redis-action-cache are deprecated. "
                        "Separately define a Redis connection using !redis-connection and reference it "
                        "in the `redis` key.",
                        fg="bright_yellow",
                    )
                )
                redis = RedisProvider(
                    host=host,
                    port=port,
                    password=password,
                    db=db,
                    dns_srv_record=dns_srv_record,
                    sentinel_master_name=sentinel_master_name,
                    retries=retries,
                )

            assert isinstance(redis, RedisProvider)

            return RedisActionCache(
                storage,
                redis,
                allow_updates=allow_updates,
                cache_failed_actions=cache_failed_actions,
                entry_type=cache_entry_type,
                migrate_entries=migrate_entries,
            )
        except Exception as e:
            click.echo(click.style(f"ERROR: {e},", fg="red", bold=True), err=True)
            sys.exit(-1)


class CAS(YamlFactory):
    """Generates :class:`buildgrid.server.cas.service.ContentAddressableStorageService`
    using the tag ``!cas``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !cas
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.

        tree_cache_size (Optional[int]): Size of GetTreeResponse cache, default to None.
            This feature is experimental for testing purposes.
            It could be deprecated in favor of a redis cache in future.

        tree_cache_ttl_minutes (float): TTL of GetTreeResponse cache, default to 60 minutes.
            This feature is experimental for testing purposes.
            It could be deprecated in favor of a redis cache in future.
    """

    yaml_tag = "!cas"
    schema = os.path.join("services", "cas.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        read_only: bool = False,
        tree_cache_size: Optional[int] = None,
        tree_cache_ttl_minutes: float = 60,
    ):
        storage_type = type(storage).__name__
        click.echo(f"CAS: storage={storage_type}, read_only={read_only}")
        click.echo(click.style(f"Creating a CAS service using {storage_type}\n", fg="green", bold=True))
        return ContentAddressableStorageInstance(
            storage,
            read_only=read_only,
            tree_cache_size=tree_cache_size,
            tree_cache_ttl_minutes=tree_cache_ttl_minutes,
        )


class ByteStream(YamlFactory):
    """Generates :class:`buildgrid.server.cas.service.ByteStreamService`
    using the tag ``!bytestream``.

    Usage
        .. code:: yaml

            # This assumes that the YAML anchors are defined elsewhere
            - !bytestream
              storage: *cas-storage

    Args:
        storage(:class:`buildgrid.server.cas.storage.storage_abc.StorageABC`):
            Instance of storage to use. This must be an object constructed using
            a YAML tag ending in ``-storage``, for example ``!disk-storage``.
    """

    yaml_tag = "!bytestream"
    schema = os.path.join("services", "bytestream.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        storage: StorageABC,
        read_only: bool = False,
        disable_overwrite_early_return: bool = False,
    ):
        storage_type = type(storage).__name__
        click.echo(
            f"ByteStream: storage={storage_type}, "
            f"read_only={read_only}, "
            f"disable_overwrite_early_return={disable_overwrite_early_return}"
        )

        click.echo(
            click.style(
                f"Creating a ByteStream service using storage {storage_type}",
                fg="green",
                bold=True,
            )
        )
        return ByteStreamInstance(
            storage,
            read_only=read_only,
            disable_overwrite_early_return=disable_overwrite_early_return,
        )


class MemoryBuildEvents(YamlFactory):
    """Generates :class:`buildgrid.server.build_events.storage.BuildEventStreamStorage`
    using the tag ``!memory-build-events-storage``.

    Usage
        .. code:: yaml

            - !memory-build-events

    """

    yaml_tag = "!memory-build-events"

    def __new__(cls, _yaml_filename: str, *args, **kwargs):
        return BuildEventStreamStorage()


class MeteringServiceClientFactory(YamlFactory):
    """Generates :class:`buildgrid_metering.client.SyncMeteringServiceClient`
    using the tag ``!metering-service-client``.

    Usage
        .. code:: yaml

            - !metering-service-client
              token-path: /tmp/path/to/token
              retry-max-attempts: 3
              retry-exp-base: 2
              retry-multiplier: 1
              retry-http-statuses: [503]
              retry-exceptions: ["metering-service-client-error"]
    """

    yaml_tag = "!metering-service-client"
    schema = os.path.join("clients", "metering-service-client.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        base_url: str,
        token_path: Optional[str] = None,
        retry_max_attempts: int = 0,  # Default to no retry
        retry_exp_base: float = 1.5,
        retry_multiplier: float = 1.0,
        retry_max_wait: float = 10.0,
        retry_http_statuses: Optional[List[int]] = None,
        retry_exceptions: Optional[List[str]] = None,
        retry_cause_exceptions: Optional[List[str]] = None,
    ):
        if token_path is not None:
            auth_config = metering.auth.AuthTokenConfig(mode=metering.auth.AuthTokenMode.FILEPATH, value=token_path)
        else:
            auth_config = metering.auth.AuthTokenConfig(mode=metering.auth.AuthTokenMode.NONE, value="")

        def _get_exception_class(name: str) -> Type[Exception]:
            exception_classes = {
                "metering-service-error": MeteringServiceError,
                "metering-service-client-error": MeteringServiceClientError,
                "timeout-error": requests.ConnectionError,
            }
            try:
                return exception_classes[name]
            except KeyError:
                raise ValueError(f"Unsupported exception class: {name}. Supported classes: {exception_classes.keys()}")

        retry_config = metering.RetryConfig(
            max_attempts=retry_max_attempts,
            exp_base=retry_exp_base,
            multiplier=retry_multiplier,
            max_wait=retry_max_wait,
            http_statuses=tuple(retry_http_statuses or []),
            exception_types=tuple(_get_exception_class(e) for e in (retry_exceptions or [])),
            cause_exception_types=tuple(_get_exception_class(e) for e in (retry_cause_exceptions or [])),
        )
        click.echo(f"Metering service client {retry_config=}")

        return metering.SyncMeteringServiceClient(
            base_url, token_loader=metering.auth.AuthTokenLoader(auth_config), retry_config=retry_config
        )


class AssetClientFactory(YamlFactory):
    """Generates :class:`buildgrid_metering.client.AssetClient`
    using the tag ``!asset-client``.

    Usage
        .. code:: yaml

            - !asset-client
              url: https://remote-asset.com
              instance-name: dev
              credentials:
                tls-client-cert: /path/to/cert
                auth-token: /path/to/token
              request-timeout: 5
              retries: 3
    """

    yaml_tag = "!asset-client"
    schema = os.path.join("clients", "asset-client.yaml")

    def __new__(
        cls,
        _yaml_filename: str,
        url: str,
        credentials: Optional[ClientCredentials] = None,
        instance_name: str = "",
        request_timeout: float = 5.0,
        retries: int = 3,
    ):
        credentials = credentials or {}
        channel, *_ = setup_channel(
            remote_url=url,
            auth_token=credentials.get("auth-token"),
            client_key=credentials.get("tls-client-key"),
            client_cert=credentials.get("tls-client-cert"),
            server_cert=credentials.get("tls-server-cert"),
            timeout=request_timeout,
        )
        return AssetClient(channel=channel, instance_name=instance_name, retries=retries)


def _parse_size(size):
    """Convert a string containing a size in bytes (e.g. '2GB') to a number."""
    _size_prefixes = {"k": 2**10, "m": 2**20, "g": 2**30, "t": 2**40}
    size = size.lower()

    if size[-1] == "b":
        size = size[:-1]
    if size[-1] in _size_prefixes:
        return int(size[:-1]) * _size_prefixes[size[-1]]
    return int(size)


def _validate_url_and_credentials(url: str, credentials: Optional[ClientCredentials]) -> bool:
    """Validate a URL and set of credentials for the URL.

    This parses the given URL, to determine if it should be used with
    credentials (ie. to create a secure gRPC channel), or not (ie. to create
    an insecure gRPC channel).

    ClientCredentials will be ignored for insecure channels, but if specified need
    to be valid for secure channels. Secure client channels with no specified
    credentials are valid, since gRPC will attempt to fall back to a default
    root certificate location used with no private key or certificate chain.

    If the credentials are invalid, then this function will output the error
    using ``click.echo``, and return ``False``. Otherwise this function will
    return True

    Args:
        url (str): The URL to use for validation.
        credentials (dict, optional): The credentials configuration to validate.

    """
    try:
        parsed_url = urlparse(url)
    except ValueError:
        click.echo(
            click.style(
                "ERROR: Failed to parse URL for gRPC channel construction.\n" + f"The problematic URL was: {url}.\n",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        return False
    unix_socket = parsed_url.scheme == "unix"

    if parsed_url.scheme in insecure_uri_schemes:
        # Its a URL for an insecure channel that we recognize
        if credentials is not None:
            click.echo(
                click.style(
                    "WARNING: credentials were specified for a gRPC channel, but "
                    f"`{url}` uses an insecure scheme. The credentials will be "
                    "ignored.\n",
                    fg="bright_yellow",
                )
            )
        return True

    elif parsed_url.scheme not in secure_uri_schemes and not unix_socket:
        # Its not insecure, and its not a recognized secure scheme, so error out.
        click.echo(click.style(f"ERROR: URL {url} uses an unsupported scheme.\n", fg="red", bold=True), err=True)
        return False

    if not credentials:
        # Unix sockets are treated as secure only if credentials are set
        if not unix_socket:
            click.echo(
                click.style(
                    f"WARNING: {url} uses a secure scheme but no credentials were "
                    "specified. gRPC will attempt to fall back to defaults.\n",
                    fg="bright_yellow",
                )
            )
        return True

    client_key = credentials.get("tls-client-key")
    client_cert = credentials.get("tls-client-cert")
    server_cert = credentials.get("tls-server-cert")

    valid = True
    missing = {}
    if server_cert is not None and not os.path.exists(server_cert):
        valid = False
        missing["tls-server-cert"] = server_cert
    if client_key is not None and not os.path.exists(client_key):
        valid = False
        missing["tls-client-key"] = client_key
    if client_cert is not None and not os.path.exists(client_cert):
        valid = False
        missing["tls-client-cert"] = client_cert

    if not valid:
        click.echo(
            click.style(
                "ERROR: one or more configured TLS credentials files were "
                + "missing.\nSet remote url scheme to `http` or `grpc` in order to "
                + "deactivate TLS encryption.\nMissing files:",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        for key, path in missing.items():
            click.echo(click.style(f"  - {key}: {path}", fg="red", bold=True), err=True)
        return False
    return True


def _validate_server_credentials(credentials: Optional[Dict[str, str]]) -> None:
    """Validate a configured set of credentials.

    If the credentials are invalid, then this function will call ``sys.exit``
    and stop the process, since there's no point continuing. If this function
    returns without exiting the program, then the credentials were valid.

    Args:
        credentials (dict): The credentials configuration to validate.

    """
    if not credentials:
        click.echo(
            click.style(
                "ERROR: no TLS certificates were specified for the server's network config.\n"
                + "Set `insecure-mode` to True to deactivate TLS encryption.\n",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        sys.exit(-1)

    server_key = credentials.get("tls-server-key")
    server_cert = credentials.get("tls-server-cert")
    client_certs = credentials.get("tls-client-certs")

    valid = True
    missing = {}
    if server_cert is None or not os.path.exists(server_cert):
        valid = False
        missing["tls-server-cert"] = server_cert
    if server_key is None or not os.path.exists(server_key):
        valid = False
        missing["tls-server-key"] = server_key
    if client_certs is not None and not os.path.exists(client_certs):
        valid = False
        missing["tls-client-certs"] = client_certs

    if not valid:
        click.echo(
            click.style(
                "ERROR: Couldn't find certificates for secure server port.\n"
                "Set `insecure-mode` to True to deactivate TLS encryption.\n"
                "Missing files:",
                fg="red",
                bold=True,
            ),
            err=True,
        )
        for key, path in missing.items():
            click.echo(click.style(f"  - {key}: {path}", fg="red", bold=True), err=True)
        sys.exit(-1)


def _validate_scheduler(
    cls: Type[YamlFactory],
    scheduler: Optional[SQLDataStore],
    data_store: Optional[SQLDataStore],
    fallback: bool = False,
    storage: Optional[StorageABC] = None,
) -> SQLDataStore:
    """Validate an object that is supposed to be a SQLDataStore implementation.

    This function handles falling back to a default or exiting with a useful error if
    neither of the two keys are given, as well as warning of deprecation for the
    ``data-store`` key and checking that the provided object actually is a
    ``SQLDataStore`` implementation.

    Args:
        cls (YamlFactory): The class being used to parse a given YAML tag.
        scheduler (Optional[SQLDataStore]): The object given in the ``scheduler`` key, to be
            validated as a ``SQLDataStore`` implementation.
        data_store (Optional[SQLDataStore]): The object given in the ``data_store`` key, to be
            validated as a ``SQLDataStore`` implementation.
        fallback (bool): If set, fallback to a default SQLDataStore
            backed scheduler if both keys are unset. If this is true,
            then ``storage`` must also be provided.
        storage (StorageABC): The storage backend to use for the default data
            store (only used when ``fallback`` is True and both ``scheduler``
            and ``data_store`` are None).

    Returns:
        SQLDataStore: An instance of an implementation of the
            ``SQLDataStore``, for the scheduler to use to store state.

    """
    # If the data_store key is specified, warn about deprecation but still use
    # it if no scheduler key is available.
    if data_store is not None:
        click.echo(
            click.style(
                f"WARNING: `data-store` key in {cls.yaml_tag} config is deprecated "
                "and will be removed in the future. Use `scheduler` instead.",
                fg="bright_yellow",
            )
        )

    if scheduler:
        return scheduler

    if data_store:
        return data_store

    # If the configuration doesn't define a data store type, fallback to a default scheduler
    if fallback and storage:
        click.echo(
            click.style(
                f"WARNING: No `scheduler` key provided in {cls.yaml_tag}, "
                f"falling back to default `{MemorySchedulerConfig.yaml_tag}`.",
                fg="bright_yellow",
            )
        )
        return SQLDataStore(storage=storage, sql_provider=SqlProvider())

    click.echo(
        click.style(
            f"ERROR: No `scheduler` key provided in {cls.yaml_tag}. "
            f"{cls.yaml_tag} requires a scheduler backend to be defined.",
            fg="red",
            bold=True,
        ),
        err=True,
    )
    sys.exit(-1)


def get_logstream_connection_info(logstream) -> Tuple[Optional[str], Optional[Dict[str, str]], Optional[str]]:
    logstream_url = None
    credentials = None
    logstream_instance_name = None
    if logstream:
        logstream_url = logstream["url"]
        credentials = logstream.get("credentials")
        if not _validate_url_and_credentials(logstream_url, credentials=credentials):
            sys.exit(-1)
        logstream_instance_name = logstream.get("instance-name", "")

    return logstream_url, credentials, logstream_instance_name


def get_parser():
    yaml.SafeLoader.add_constructor(Channel.yaml_tag, Channel.from_yaml)
    yaml.SafeLoader.add_constructor(ExpandPath.yaml_tag, ExpandPath.from_yaml)
    yaml.SafeLoader.add_constructor(ExpandVars.yaml_tag, ExpandVars.from_yaml)
    yaml.SafeLoader.add_constructor(ReadFile.yaml_tag, ReadFile.from_yaml)
    yaml.SafeLoader.add_constructor(Execution.yaml_tag, Execution.from_yaml)
    yaml.SafeLoader.add_constructor(Bots.yaml_tag, Bots.from_yaml)
    yaml.SafeLoader.add_constructor(Action.yaml_tag, Action.from_yaml)
    yaml.SafeLoader.add_constructor(LruAction.yaml_tag, LruAction.from_yaml)
    yaml.SafeLoader.add_constructor(RemoteAction.yaml_tag, RemoteAction.from_yaml)
    yaml.SafeLoader.add_constructor(S3Action.yaml_tag, S3Action.from_yaml)
    yaml.SafeLoader.add_constructor(WriteOnceAction.yaml_tag, WriteOnceAction.from_yaml)
    yaml.SafeLoader.add_constructor(RedisAction.yaml_tag, RedisAction.from_yaml)
    yaml.SafeLoader.add_constructor(WithCacheAction.yaml_tag, WithCacheAction.from_yaml)
    yaml.SafeLoader.add_constructor(MirroredCacheFactory.yaml_tag, MirroredCacheFactory.from_yaml)
    yaml.SafeLoader.add_constructor(Disk.yaml_tag, Disk.from_yaml)
    yaml.SafeLoader.add_constructor(LRU.yaml_tag, LRU.from_yaml)
    yaml.SafeLoader.add_constructor(S3.yaml_tag, S3.from_yaml)
    yaml.SafeLoader.add_constructor(Redis.yaml_tag, Redis.from_yaml)
    yaml.SafeLoader.add_constructor(Remote.yaml_tag, Remote.from_yaml)
    yaml.SafeLoader.add_constructor(WithCache.yaml_tag, WithCache.from_yaml)
    yaml.SafeLoader.add_constructor(SizeDifferentiated.yaml_tag, SizeDifferentiated.from_yaml)
    yaml.SafeLoader.add_constructor(SQL_Index.yaml_tag, SQL_Index.from_yaml)
    yaml.SafeLoader.add_constructor(SQL_Storage.yaml_tag, SQL_Storage.from_yaml)
    yaml.SafeLoader.add_constructor(CAS.yaml_tag, CAS.from_yaml)
    yaml.SafeLoader.add_constructor(ByteStream.yaml_tag, ByteStream.from_yaml)
    yaml.SafeLoader.add_constructor(SQLDataStoreConfig.yaml_tag, SQLDataStoreConfig.from_yaml)
    yaml.SafeLoader.add_constructor(MemoryDataStoreConfig.yaml_tag, MemoryDataStoreConfig.from_yaml)
    yaml.SafeLoader.add_constructor(SQLSchedulerConfig.yaml_tag, SQLSchedulerConfig.from_yaml)
    yaml.SafeLoader.add_constructor(MemorySchedulerConfig.yaml_tag, MemorySchedulerConfig.from_yaml)
    yaml.SafeLoader.add_constructor(MemoryBuildEvents.yaml_tag, MemoryBuildEvents.from_yaml)
    yaml.SafeLoader.add_constructor(SQLConnection.yaml_tag, SQLConnection.from_yaml)
    yaml.SafeLoader.add_constructor(MeteringServiceClientFactory.yaml_tag, MeteringServiceClientFactory.from_yaml)
    yaml.SafeLoader.add_constructor(Sharded.yaml_tag, Sharded.from_yaml)
    yaml.SafeLoader.add_constructor(RedisConnection.yaml_tag, RedisConnection.from_yaml)
    yaml.SafeLoader.add_constructor(Redis_Index.yaml_tag, Redis_Index.from_yaml)
    yaml.SafeLoader.add_constructor(AssetClientFactory.yaml_tag, AssetClientFactory.from_yaml)
    yaml.SafeLoader.add_constructor(Replicated_Storage.yaml_tag, Replicated_Storage.from_yaml)

    return yaml


def get_schema():
    schema_text = files("buildgrid._app.settings.schemas").joinpath("config.yaml").read_text()
    schema = yaml.safe_load(schema_text)
    return schema


def check_type(*expected_types: Any) -> Callable[[Any, Any], bool]:
    def _check_type(checker: Any, instance: Any) -> bool:
        return any(isinstance(instance, t) for t in expected_types)

    return _check_type


def check_redis_provider_type() -> Callable[[Any, Any], bool]:
    def _check_type(checker: Any, instance: Any) -> bool:
        try:
            from buildgrid.server.redis.provider import RedisProvider

            return isinstance(instance, RedisProvider)
        except ImportError:
            return False

    return _check_type


def get_validator(schema=None):
    if schema is None:
        schema = get_schema()

    type_checker = Draft7Validator.TYPE_CHECKER.redefine_many(
        definitions={
            "cache": check_type(ActionCacheABC),
            "connection": check_type(SqlProvider),
            "redis-connection": check_redis_provider_type(),
            "storage": check_type(StorageABC),
            "scheduler": check_type(SQLDataStore),
            "!execution": check_type(ExecutionController),
            "!bots": check_type(BotsInterface),
            "!cas": check_type(ContentAddressableStorageInstance),
            "!bytestream": check_type(ByteStreamInstance),
            "!action-cache": check_type(ActionCache),
            "!s3action-cache": check_type(S3ActionCache),
            "!remote-action-cache": check_type(RemoteActionCache),
            "!write-once-action-cache": check_type(WriteOnceActionCache),
            "!memory-build-events": check_type(BuildEventStreamStorage),
            "!with-cache-action-cache": check_type(WithCacheActionCache),
            "!metering-service-client": check_type(metering.SyncMeteringServiceClient),
            "!asset-client": check_type(AssetClient),
        }
    )

    BgdValidator = validators.create(
        meta_schema=Draft7Validator.META_SCHEMA, validators=dict(Draft7Validator.VALIDATORS), type_checker=type_checker
    )
    return BgdValidator(schema)
