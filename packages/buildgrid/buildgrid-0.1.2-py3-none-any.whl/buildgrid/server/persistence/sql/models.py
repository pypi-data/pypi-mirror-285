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
import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Table,
    UniqueConstraint,
    false,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from buildgrid._enums import LeaseState
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Action, Digest
from buildgrid._protos.google.devtools.remoteworkers.v1test2 import bots_pb2

Base = declarative_base()


job_platform_association = Table(
    "job_platforms",
    Base.metadata,
    Column("job_name", ForeignKey("jobs.name", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("platform_id", ForeignKey("platform_properties.id"), primary_key=True),
)


class PlatformEntry(Base):
    __tablename__ = "platform_properties"
    __table_args__ = (UniqueConstraint("key", "value"),)

    id: int = Column(Integer, autoincrement=True, primary_key=True)
    key: str = Column(String)
    value: str = Column(String)

    jobs: List["JobEntry"] = relationship("JobEntry", secondary=job_platform_association, back_populates="platform")


class JobEntry(Base):
    __tablename__ = "jobs"

    name: str = Column(String, primary_key=True)
    instance_name: Optional[str] = Column(String, index=True)
    action_digest: str = Column(String, index=True, nullable=False)
    action: bytes = Column(LargeBinary)
    priority: int = Column(Integer, default=1, index=True, nullable=False)
    stage: int = Column(Integer, default=0, index=True, nullable=False)
    do_not_cache: bool = Column(Boolean, default=False, nullable=False)
    cancelled: bool = Column(Boolean, default=False, nullable=False)
    queued_timestamp: Optional[datetime.datetime] = Column(DateTime, index=True)
    queued_time_duration: Optional[int] = Column(Integer)
    worker_start_timestamp: Optional[datetime.datetime] = Column(DateTime)
    worker_completed_timestamp: Optional[datetime.datetime] = Column(DateTime)
    result: Optional[str] = Column(String)
    assigned: Optional[bool] = Column(Boolean, default=False)
    n_tries: Optional[int] = Column(Integer, default=0)
    # This is a hash of the platform properties, used for matching jobs to workers
    platform_requirements: Optional[str] = Column(String, nullable=True)
    status_code: Optional[int] = Column(Integer, nullable=True)
    stdout_stream_name: Optional[str] = Column(String, nullable=True)
    stdout_stream_write_name: Optional[str] = Column(String, nullable=True)
    stderr_stream_name: Optional[str] = Column(String, nullable=True)
    stderr_stream_write_name: Optional[str] = Column(String, nullable=True)
    command: Optional[str] = Column(String, nullable=True)

    leases: List["LeaseEntry"] = relationship("LeaseEntry", backref="job")
    active_states: List[int] = [
        LeaseState.UNSPECIFIED.value,
        LeaseState.PENDING.value,
        LeaseState.ACTIVE.value,
        LeaseState.CANCELLED.value,
    ]
    active_leases: List["LeaseEntry"] = relationship(
        "LeaseEntry",
        primaryjoin=f"and_(LeaseEntry.job_name==JobEntry.name, LeaseEntry.state.in_({active_states}))",
        order_by="LeaseEntry.id.desc()",
        overlaps="job,leases",
    )

    operations: List["OperationEntry"] = relationship("OperationEntry", backref="job")

    platform: List["PlatformEntry"] = relationship(
        "PlatformEntry", secondary=job_platform_association, back_populates="jobs"
    )

    __table_args__ = (
        Index(
            "ix_worker_start_timestamp",
            worker_start_timestamp,
            unique=False,
            postgresql_where=worker_start_timestamp.isnot(None),
            sqlite_where=worker_start_timestamp.isnot(None),
        ),
        Index(
            "ix_worker_completed_timestamp",
            worker_completed_timestamp,
            unique=False,
            postgresql_where=worker_completed_timestamp.isnot(None),
            sqlite_where=worker_completed_timestamp.isnot(None),
        ),
    )


class LeaseEntry(Base):
    __tablename__ = "leases"

    job: JobEntry
    id: int = Column(Integer, primary_key=True)
    job_name: str = Column(
        String, ForeignKey("jobs.name", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False
    )
    status: Optional[int] = Column(Integer)
    state: int = Column(Integer, nullable=False)
    worker_name: Optional[str] = Column(String, index=True, default=None)

    def to_protobuf(self) -> bots_pb2.Lease:
        lease = bots_pb2.Lease()
        lease.id = self.job_name

        if self.job.action is not None:
            action = Action()
            action.ParseFromString(self.job.action)
            lease.payload.Pack(action)
        else:
            lease.payload.Pack(string_to_digest(self.job.action_digest))

        lease.state = self.state  # type: ignore[assignment]
        if self.status is not None:
            lease.status.code = self.status
        return lease


class ClientIdentityEntry(Base):
    __tablename__ = "client_identities"
    __table_args__ = (UniqueConstraint("instance", "workflow", "actor", "subject"),)

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    instance: str = Column(String, nullable=False)
    workflow: str = Column(String, nullable=False)
    actor: str = Column(String, nullable=False)
    subject: str = Column(String, nullable=False)

    def __str__(self) -> str:
        return (
            f"ClientIdentity: [instance={self.instance} workflow={self.workflow}"
            f" actor={self.actor} subject={self.subject}]"
        )


class OperationEntry(Base):
    __tablename__ = "operations"

    job: JobEntry
    name: str = Column(String, primary_key=True)
    job_name: str = Column(
        String, ForeignKey("jobs.name", ondelete="CASCADE", onupdate="CASCADE"), index=True, nullable=False
    )
    cancelled: bool = Column(Boolean, default=False, nullable=False)
    tool_name: Optional[str] = Column(String, nullable=True)
    tool_version: Optional[str] = Column(String, nullable=True)
    invocation_id: Optional[str] = Column(String, nullable=True)
    correlated_invocations_id: Optional[str] = Column(String, nullable=True)
    client_identity_id: Optional[int] = Column(Integer, ForeignKey("client_identities.id"), nullable=True)
    client_identity: Optional[ClientIdentityEntry] = relationship("ClientIdentityEntry")


class IndexEntry(Base):
    __tablename__ = "index"

    digest_hash: str = Column(String, nullable=False, index=True, primary_key=True)
    digest_size_bytes: int = Column(BigInteger, nullable=False)
    accessed_timestamp: datetime.datetime = Column(DateTime, index=True, nullable=False)
    deleted: bool = Column(Boolean, nullable=False, server_default=false())
    inline_blob: Optional[bytes] = Column(LargeBinary, nullable=True)


# This table is used to store the bot session state. It also stores the
# assigned leases, instead of making use of the 'leases' table through an
# SQLAlchemy relationship, as the 'leases' table is dependent on the type of
# data store selected, and might never be populated.
class BotEntry(Base):
    __tablename__ = "bots"

    name: str = Column(String, nullable=False, index=True, primary_key=True)
    bot_id: str = Column(String, nullable=False, index=True)
    last_update_timestamp: datetime.datetime = Column(DateTime, index=True, nullable=False)
    bot_status: int = Column(Integer, nullable=False)
    expiry_time: Optional[datetime.datetime] = Column(DateTime, index=True, nullable=True)
    lease_id: Optional[str] = Column(String, nullable=True)
    instance_name: Optional[str] = Column(String, nullable=True)


# This table is used by the SQLStorage CAS backend to store blobs
# in a database.
class BlobEntry(Base):
    __tablename__ = "blobs"

    digest_hash: str = Column(String, primary_key=True)
    digest_size_bytes: int = Column(BigInteger, nullable=False)
    data: bytes = Column(LargeBinary, nullable=False)


def digest_to_string(digest: Digest) -> str:
    return f"{digest.hash}/{digest.size_bytes}"


def string_to_digest(string: str) -> Digest:
    digest_hash, size_bytes = string.split("/", 1)
    return Digest(hash=digest_hash, size_bytes=int(size_bytes))
