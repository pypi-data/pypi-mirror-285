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


import faulthandler
import logging
import logging.handlers
import os
import signal
import sys
import threading
import time
import traceback
from collections import defaultdict
from contextlib import ExitStack
from datetime import datetime
from queue import Empty, Queue
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import grpc
from grpc_reflection.v1alpha import reflection

from buildgrid._enums import LeaseState, LogRecordLevel, MetricCategories, OperationStage
from buildgrid._exceptions import PermissionDeniedError
from buildgrid._protos.buildgrid.v2.monitoring_pb2 import LogRecord
from buildgrid._types import OnServerStartCallback, PortAssignedCallback
from buildgrid.server.actioncache.service import ActionCacheService
from buildgrid.server.auth.config import InstanceAuthorizationConfig
from buildgrid.server.auth.enums import AuthMetadataAlgorithm, AuthMetadataMethod
from buildgrid.server.auth.manager import HeadersAuthManager, JWTAuthManager, set_auth_manager
from buildgrid.server.bots.service import BotsService
from buildgrid.server.build_events.service import PublishBuildEventService, QueryBuildEventsService
from buildgrid.server.capabilities.instance import CapabilitiesInstance
from buildgrid.server.capabilities.service import CapabilitiesService
from buildgrid.server.cas.service import ByteStreamService, ContentAddressableStorageService
from buildgrid.server.context import instance_context
from buildgrid.server.controller import ExecutionController
from buildgrid.server.execution.service import ExecutionService
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_gauge_metric
from buildgrid.server.monitoring import (
    MonitoringBus,
    MonitoringOutputFormat,
    MonitoringOutputType,
    StatsDTagFormat,
    get_monitoring_bus,
    set_monitoring_bus,
)
from buildgrid.server.operations.service import OperationsService
from buildgrid.server.persistence.sql.impl import DataStoreMetrics, SQLDataStore
from buildgrid.server.servicer import Instance, InstancedServicer
from buildgrid.server.threading import ContextThreadPoolExecutor, ContextWorker
from buildgrid.settings import (
    DEFAULT_JWKS_REFETCH_INTERVAL_MINUTES,
    LOG_RECORD_FORMAT,
    MIN_THREAD_POOL_SIZE,
    MONITORING_PERIOD,
    SHUTDOWN_ALARM_DELAY,
)
from buildgrid.utils import read_file

LOGGER = logging.getLogger(__name__)


def load_tls_server_credentials(
    server_key: Optional[str] = None, server_cert: Optional[str] = None, client_certs: Optional[str] = None
) -> Optional[grpc.ServerCredentials]:
    """Looks-up and loads TLS server gRPC credentials.

    Every private and public keys are expected to be PEM-encoded.

    Args:
        server_key(str): private server key file path.
        server_cert(str): public server certificate file path.
        client_certs(str): public client certificates file path.

    Returns:
        :obj:`ServerCredentials`: The credentials for use for a
        TLS-encrypted gRPC server channel.
    """
    if not server_key or not os.path.exists(server_key):
        return None

    if not server_cert or not os.path.exists(server_cert):
        return None

    server_key_pem = read_file(server_key)
    server_cert_pem = read_file(server_cert)
    if client_certs and os.path.exists(client_certs):
        client_certs_pem = read_file(client_certs)
    else:
        client_certs_pem = None
        client_certs = None

    credentials = grpc.ssl_server_credentials(
        [(server_key_pem, server_cert_pem)], root_certificates=client_certs_pem, require_client_auth=bool(client_certs)
    )

    # TODO: Fix this (missing stubs?) "ServerCredentials" has no attribute
    credentials.server_key = server_key  # type: ignore[attr-defined]
    credentials.server_cert = server_cert  # type: ignore[attr-defined]
    credentials.client_certs = client_certs  # type: ignore[attr-defined]

    return credentials


class Server:
    """Creates a BuildGrid server instance.

    The :class:`Server` class binds together all the gRPC services.
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,
        monitor: bool = False,
        mon_endpoint_type: MonitoringOutputType = MonitoringOutputType.STDOUT,
        mon_endpoint_location: Optional[str] = None,
        mon_serialisation_format: MonitoringOutputFormat = MonitoringOutputFormat.JSON,
        mon_metric_prefix: str = "",
        mon_tag_format: StatsDTagFormat = StatsDTagFormat.INFLUX_STATSD,
        mon_additional_tags: Optional[Dict[str, str]] = None,
        auth_method: AuthMetadataMethod = AuthMetadataMethod.NONE,
        auth_secret: Optional[str] = None,
        auth_jwks_url: Optional[str] = None,
        auth_audience: Optional[str] = None,
        auth_jwks_fetch_minutes: Optional[int] = None,
        auth_algorithm: AuthMetadataAlgorithm = AuthMetadataAlgorithm.UNSPECIFIED,
        auth_acl_config: Optional[Dict[str, InstanceAuthorizationConfig]] = None,
        auth_allow_unauthorized_instances: Optional[List[str]] = None,
        enable_server_reflection: bool = True,
        grpc_compression: grpc.Compression = grpc.Compression.NoCompression,
        monitoring_period: float = MONITORING_PERIOD,
    ):
        """Initializes a new :class:`Server` instance.

        Args:
            max_workers (int, optional): A pool of max worker threads.
            monitor (bool, optional): Whether to globally activate server
                monitoring. Defaults to ``False``.
            auth_method (AuthMetadataMethod, optional): Authentication method to
                be used for request authorization. Defaults to ``NONE``.
            auth_secret (str, optional): The secret or key to be used for
                authorizing request using `auth_method`. Defaults to ``None``.
            auth_jwks_url (str, optional): The url to fetch the JWKs.
                Either secret or this field must be specified. Defaults to ``None``.
            auth_audience (str): The audience used to validate jwt tokens against.
                The tokens must have an audience field.
            auth_jwks_fetch_minutes (int): The number of minutes to wait before
                refetching the jwks set. Default: 60 minutes.
            auth_algorithm (AuthMetadataAlgorithm, optional): The crytographic
                algorithm to be uses in combination with `auth_secret` for
                authorizing request using `auth_method`. Defaults to
                ``UNSPECIFIED``.
            auth_acl_config (Dict[str, InstanceAuthorizationConfig], optional): The acl
                rules to configure in what context a request is authorized
            auth_allow_unauthorized_instances (List[str], optional): List of instances that should
                be allowed to have unautheticated access
            enable_server_reflection (bool): Whether to enable grpc reflection for
                registered services. Defaults to ``True``.
            grpc_compression (grpc.Compression): The transport compression algorithm to use for sending responses,
                defaults to NoCompression
        """
        self._stack = ExitStack()

        self._is_instrumented = monitor

        self._action_cache_service = ActionCacheService()
        self._bots_service = BotsService()
        self._bytestream_service = ByteStreamService()
        self._capabilities_service = CapabilitiesService()
        self._cas_service = ContentAddressableStorageService()
        self._execution_service = ExecutionService()
        self._operations_service = OperationsService()

        # Special cases
        self._build_events_service = PublishBuildEventService()
        self._query_build_events_service = QueryBuildEventsService()

        self._schedulers: Dict[str, Set[SQLDataStore]] = defaultdict(set)

        self._ports: List[Tuple[str, Optional[Dict[str, str]]]] = []
        self._port_map: Dict[str, int] = {}

        self._server_reflection = enable_server_reflection
        self._grpc_compression = grpc_compression

        self._logging_queue: Queue[Any] = Queue()
        self._monitoring_period = monitoring_period

        if max_workers is None:
            # Use max_workers default from Python 3.4+
            max_workers = max(MIN_THREAD_POOL_SIZE, (os.cpu_count() or 1) * 5)

        elif max_workers < MIN_THREAD_POOL_SIZE:
            LOGGER.warning(
                f"Specified thread-limit=[{max_workers}] is too small, " f"bumping it to [{MIN_THREAD_POOL_SIZE}]"
            )
            # Enforce a minumun for max_workers
            max_workers = MIN_THREAD_POOL_SIZE

        self._max_grpc_workers = max_workers

        if self._is_instrumented:
            set_monitoring_bus(
                MonitoringBus(
                    endpoint_type=mon_endpoint_type,
                    endpoint_location=mon_endpoint_location,
                    metric_prefix=mon_metric_prefix,
                    serialisation_format=mon_serialisation_format,
                    tag_format=mon_tag_format,
                    additional_tags=mon_additional_tags,
                )
            )

        if auth_method == AuthMetadataMethod.JWT:
            if auth_jwks_fetch_minutes is None:
                auth_jwks_fetch_minutes = DEFAULT_JWKS_REFETCH_INTERVAL_MINUTES
            set_auth_manager(
                JWTAuthManager(
                    secret=auth_secret,
                    algorithm=auth_algorithm,
                    jwks_url=auth_jwks_url,
                    audience=auth_audience,
                    jwks_fetch_minutes=auth_jwks_fetch_minutes,
                    acls=auth_acl_config,
                    allow_unauthorized_instances=(
                        set(auth_allow_unauthorized_instances) if auth_allow_unauthorized_instances else None
                    ),
                )
            )
        elif auth_method == AuthMetadataMethod.HEADERS:
            set_auth_manager(
                HeadersAuthManager(
                    acls=auth_acl_config,
                    allow_unauthorized_instances=(
                        set(auth_allow_unauthorized_instances) if auth_allow_unauthorized_instances else None
                    ),
                )
            )

        LOGGER.debug(f"Setting up gRPC server with thread-limit=[{max_workers}]")

    def register_instance(self, instance_name: str, instance: Instance) -> None:
        """
        Register an instance with the server. Handled the logic of mapping instances to the
        correct servicer container.

        Args:
            instance_name (str): The name of the instance.

            instance (Instance): The instance implementation.
        """

        # Special case to handle the ExecutionController which combines the service interfaces.
        if isinstance(instance, ExecutionController):
            if bots_interface := instance.bots_interface:
                self.register_instance(instance_name, bots_interface)
            if execution_instance := instance.execution_instance:
                self.register_instance(instance_name, execution_instance)
            if operations_instance := instance.operations_instance:
                self.register_instance(instance_name, operations_instance)

        elif action_instance := self._action_cache_service.cast(instance):
            self._action_cache_service.add_instance(instance_name, action_instance)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_action_cache_instance(action_instance)

        elif bots_instance := self._bots_service.cast(instance):
            self._bots_service.add_instance(instance_name, bots_instance)
            self._schedulers[instance_name].add(bots_instance.scheduler)

        elif bytestream_instance := self._bytestream_service.cast(instance):
            self._bytestream_service.add_instance(instance_name, bytestream_instance)

        elif cas_instance := self._cas_service.cast(instance):
            self._cas_service.add_instance(instance_name, cas_instance)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_cas_instance(cas_instance)

        elif execution_instance := self._execution_service.cast(instance):
            self._execution_service.add_instance(instance_name, execution_instance)
            self._schedulers[instance_name].add(execution_instance.scheduler)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_execution_instance(execution_instance)

        elif operations_instance := self._operations_service.cast(instance):
            self._operations_service.add_instance(instance_name, operations_instance)

        # The Build Events Services have no support for instance names, so this
        # is a bit of a special case where the storage backend itself is the
        # trigger for creating the gRPC services.
        elif instance.SERVICE_NAME == "BuildEvents":
            self._build_events_service.add_instance("", instance)  # type: ignore[arg-type]
            self._query_build_events_service.add_instance("", instance)  # type: ignore[arg-type]

        else:
            raise ValueError(f"Instance of type {type(instance)} not supported by {type(self)}")

    @property
    def _services(self) -> Iterable[InstancedServicer[Any]]:
        return (
            self._action_cache_service,
            self._bots_service,
            self._bytestream_service,
            self._capabilities_service,
            self._cas_service,
            self._execution_service,
            self._operations_service,
            # Special cases
            self._build_events_service,
            self._query_build_events_service,
        )

    def add_port(self, address: str, credentials: Optional[Dict[str, str]]) -> None:
        """Adds a port to the server.

        Must be called before the server starts. If a credentials object exists,
        it will make a secure port.

        Args:
            address (str): The address with port number.
            credentials (:obj:`grpc.ChannelCredentials`): Credentials object.
        """
        self._ports.append((address, credentials))

    @property
    def is_instrumented(self) -> bool:
        return self._is_instrumented

    def start(
        self,
        *,
        on_server_start_cb: Optional[OnServerStartCallback] = None,
        port_assigned_callback: Optional[PortAssignedCallback] = None,
        run_forever: bool = True,
    ) -> None:
        """Starts the BuildGrid server.

        BuildGrid server startup consists of 3 stages,

        1. Starting logging and monitoring

        This step starts up the logging coroutine, the periodic status metrics
        coroutine, and the monitoring bus' publishing subprocess. Since this
        step involves forking, anything not fork-safe needs to be done *after*
        this step.

        2. Instantiate gRPC

        This step instantiates the gRPC server, and tells all the instances
        which have been attached to the server to instantiate their gRPC
        objects. It is also responsible for creating the various service
        objects and connecting them to the server and the instances.

        After this step, gRPC core is running and its no longer safe to fork
        the process.

        3. Start instances

        Several of BuildGrid's services use background threads that need to
        be explicitly started when BuildGrid starts up. Rather than doing
        this at configuration parsing time, this step provides a hook for
        services to start up in a more organised fashion.

        4. Start the gRPC server

        The final step is starting up the gRPC server. The callback passed in
        via ``on_server_start_cb`` is executed in this step once the server
        has started. After this point BuildGrid is ready to serve requests.

        The final thing done by this method is adding a ``SIGTERM`` handler
        which calls the ``Server.stop`` method to the event loop, and then
        that loop is started up using ``run_forever()``.

        Args:
            on_server_start_cb (Callable): Callback function to execute once
                the gRPC server has started up.
            port_assigned_callback (Callable): Callback function to execute
                once the gRPC server has started up. The mapping of addresses
                to ports is passed to this callback.

        """

        # 1. Start logging and monitoring
        self._stack.enter_context(
            ContextWorker(
                self._logging_worker,
                "ServerLogger",
                # Add a dummy value to the queue to unblock the get call.
                on_shutdown_requested=lambda: self._logging_queue.put(None),
            )
        )
        if self._is_instrumented:
            self._stack.enter_context(get_monitoring_bus())
            self._stack.enter_context(ContextWorker(self._state_monitoring_worker, "ServerMonitor"))

        # 2. Instantiate gRPC objects
        grpc_server = self.setup_grpc()

        # 3. Start background threads
        for service in self._services:
            self._stack.enter_context(service)

        # 4. Start the gRPC server.
        grpc_server.start()
        self._stack.callback(grpc_server.stop, None)

        if on_server_start_cb:
            on_server_start_cb()
        if port_assigned_callback:
            port_assigned_callback(port_map=self._port_map)

        # Add the stop handler and run the event loop
        if run_forever:
            grpc_server.wait_for_termination()

    def setup_grpc(self) -> grpc.Server:
        """Instantiate the gRPC objects.

        This creates the gRPC server, and causes the instances attached to
        this server to instantiate any gRPC channels they need. This also
        sets up the services which route to those instances, and sets up
        gRPC reflection.

        """
        grpc_server = grpc.server(
            ContextThreadPoolExecutor(self._max_grpc_workers, "gRPC_Executor", immediate_copy=True),
            maximum_concurrent_rpcs=self._max_grpc_workers,
            compression=self._grpc_compression,
        )

        # Add the requested ports to the gRPC server
        for address, credentials in self._ports:
            port_number = 0
            if credentials is not None:
                LOGGER.info(f"Adding secure connection on: [{address}]")
                server_key = credentials.get("tls-server-key")
                server_cert = credentials.get("tls-server-cert")
                client_certs = credentials.get("tls-client-certs")
                server_credentials = load_tls_server_credentials(
                    server_cert=server_cert, server_key=server_key, client_certs=client_certs
                )
                # TODO should this error out??
                if server_credentials:
                    port_number = grpc_server.add_secure_port(address, server_credentials)

            else:
                LOGGER.info(f"Adding insecure connection on [{address}]")
                port_number = grpc_server.add_insecure_port(address)

            if not port_number:
                raise PermissionDeniedError("Unable to configure socket")

            self._port_map[address] = port_number

        for service in self._services:
            service.setup_grpc(grpc_server)

        if self._server_reflection:
            reflection_services = [service.FULL_NAME for service in self._services if service.enabled]
            LOGGER.info(f"Server reflection is enabled for the following services: {reflection_services}")
            reflection.enable_server_reflection([reflection.SERVICE_NAME] + reflection_services, grpc_server)
        else:
            LOGGER.info("Server reflection is not enabled.")

        return grpc_server

    def stop(self, *args: Any, **kwargs: Any) -> None:
        LOGGER.info("Stopping BuildGrid server")

        def alarm_handler(*args: Any, **kwargs: Any) -> None:
            LOGGER.warning(
                f"Shutdown still ongoing after {SHUTDOWN_ALARM_DELAY} seconds. "
                f"There are {threading.active_count()} currently running threads:"
            )
            for thread in threading.enumerate():
                LOGGER.warning(f"  - {thread.name}")
            LOGGER.warning("Traceback for all threads:")
            faulthandler.dump_traceback()

        LOGGER.debug("Setting alarm for delayed shutdown")
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(SHUTDOWN_ALARM_DELAY)

        self._stack.close()

    def _logging_worker(self, shutdown_requested: threading.Event) -> None:
        """Publishes log records to the monitoring bus."""

        logging_formatter = logging.Formatter(fmt=LOG_RECORD_FORMAT)
        logging_handler = logging.handlers.QueueHandler(self._logging_queue)

        # Setup the main logging handler:
        root_logger = logging.getLogger()

        for log_filter in root_logger.filters[:]:
            logging_handler.addFilter(log_filter)
            root_logger.removeFilter(log_filter)

        for log_handler in root_logger.handlers[:]:
            for log_filter in log_handler.filters[:]:
                logging_handler.addFilter(log_filter)
            root_logger.removeHandler(log_handler)
        root_logger.addHandler(logging_handler)

        def logging_worker() -> None:
            monitoring_bus = get_monitoring_bus()

            try:
                log_record = self._logging_queue.get(timeout=self._monitoring_period)
            except Empty:
                return
            if log_record is None:
                return

            # Print log records to stdout, if required:
            if not self._is_instrumented or not monitoring_bus.prints_records:
                record = logging_formatter.format(log_record)
                # TODO: Investigate if async write would be worth here.
                sys.stdout.write(f"{record}\n")
                sys.stdout.flush()

            # Emit a log record if server is instrumented:
            if self._is_instrumented:
                log_record_level = LogRecordLevel(int(log_record.levelno / 10))
                log_record_creation_time = datetime.fromtimestamp(log_record.created)
                # logging.LogRecord.extra must be a str to str dict:
                if "extra" in log_record.__dict__ and log_record.extra:
                    log_record_metadata = log_record.extra
                else:
                    log_record_metadata = None
                forged_record = self._forge_log_record(
                    domain=log_record.name,
                    level=log_record_level,
                    message=log_record.message,
                    creation_time=log_record_creation_time,
                    metadata=log_record_metadata,
                )
                monitoring_bus.send_record_nowait(forged_record)

        while not shutdown_requested.is_set():
            try:
                logging_worker()
            except Exception:
                # The thread shouldn't exit on exceptions, but output the exception so that
                # it can be found in the logs.
                #
                # Note, we DO NOT use `LOGGER` here, because we don't want to write
                # anything new to the logging queue in case the Exception isn't some transient
                # issue.
                try:
                    sys.stdout.write("Exception in logging worker\n")
                    sys.stdout.flush()
                    traceback.print_exc()
                except Exception:
                    # There's not a lot we can do at this point really.
                    pass

        if shutdown_requested.is_set():
            # Reset logging, so any logging after shutting down the logging worker
            # still gets written to stdout and the queue doesn't get any more logs
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setFormatter(logging_formatter)
            root_logger = logging.getLogger()

            for log_filter in root_logger.filters[:]:
                stream_handler.addFilter(log_filter)
                root_logger.removeFilter(log_filter)

            for log_handler in root_logger.handlers[:]:
                for log_filter in log_handler.filters[:]:
                    stream_handler.addFilter(log_filter)
                root_logger.removeHandler(log_handler)
            root_logger.addHandler(stream_handler)

            # Drain the log message queue
            while self._logging_queue.qsize() > 0:
                logging_worker()

    def _forge_log_record(
        self,
        *,
        domain: str,
        level: LogRecordLevel,
        message: str,
        creation_time: datetime,
        metadata: Optional[Dict[str, str]] = None,
    ) -> LogRecord:
        log_record = LogRecord()

        log_record.creation_timestamp.FromDatetime(creation_time)
        log_record.domain = domain
        log_record.level = level.value
        log_record.message = message
        if metadata is not None:
            log_record.metadata.update(metadata)

        return log_record

    def _state_monitoring_worker(self, shutdown_requested: threading.Event) -> None:
        """Periodically publishes state metrics to the monitoring bus."""
        while not shutdown_requested.is_set():
            start = time.time()
            try:
                if self._execution_service.enabled:
                    for instance_name in self._execution_service.instances:
                        self._publish_client_metrics_for_instance(instance_name)

                if self._bots_service.enabled:
                    for instance_name in self._bots_service.instances:
                        self._publish_bot_metrics_for_instance(instance_name)

                if self._schedulers:
                    for instance_name in self._schedulers:
                        self._publish_scheduler_metrics_for_instance(instance_name)
            except Exception:
                # The thread shouldn't exit on exceptions, but log at a severe enough level
                # that it doesn't get lost in logs
                LOGGER.exception("Exception while gathering state metrics")

            end = time.time()
            shutdown_requested.wait(timeout=max(0, self._monitoring_period - (end - start)))

    def _publish_client_metrics_for_instance(self, instance_name: str) -> None:
        """Queries the number of clients connected for a given instance"""
        with instance_context(instance_name):
            n_clients = self._execution_service.query_connected_clients_for_instance(instance_name)
            publish_gauge_metric(METRIC.CONNECTIONS.CLIENT_COUNT, n_clients)

    def _publish_bot_metrics_for_instance(self, instance_name: str) -> None:
        with instance_context(instance_name):
            for bot_status, count in self._bots_service.count_bots_by_status(instance_name).items():
                publish_gauge_metric(METRIC.SCHEDULER.BOTS_COUNT, count, state=bot_status.name)

            n_workers = self._bots_service.query_connected_bots_for_instance(instance_name)
            publish_gauge_metric(METRIC.CONNECTIONS.WORKER_COUNT, n_workers)

    def _publish_scheduler_metrics_for_instance(self, instance_name: str) -> None:
        with instance_context(instance_name):
            # Since multiple schedulers may be active for this instance, but should
            # be using the same data-store, just use the first one
            scheduler_metrics: Optional[DataStoreMetrics] = None
            for scheduler in self._schedulers[instance_name]:
                scheduler_metrics = scheduler.get_metrics()
            if scheduler_metrics is None:
                return

            # Jobs
            for stage, n_jobs in scheduler_metrics[MetricCategories.JOBS.value].items():
                stage = OperationStage(stage)
                publish_gauge_metric(METRIC.SCHEDULER.JOB_COUNT, n_jobs, state=stage.name)
            # Leases
            for state, n_leases in scheduler_metrics[MetricCategories.LEASES.value].items():
                state = LeaseState(state)
                publish_gauge_metric(METRIC.SCHEDULER.LEASE_COUNT, n_leases, state=state.name)
