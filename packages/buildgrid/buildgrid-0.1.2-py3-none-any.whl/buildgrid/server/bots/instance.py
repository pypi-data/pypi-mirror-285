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
BotsInterface
=================

Instance of the Remote Workers interface.
"""
import logging
from contextlib import ExitStack
from typing import Dict, List, Optional, Tuple

from buildgrid._enums import BotStatus
from buildgrid._exceptions import InvalidArgumentError
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import DESCRIPTOR as BOTS_DESCRIPTOR
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession, Lease
from buildgrid.server.context import current_instance
from buildgrid.server.persistence.sql.impl import SQLDataStore
from buildgrid.server.servicer import Instance
from buildgrid.server.utils.cancellation import CancellationContext
from buildgrid.settings import MAX_WORKER_TTL, NETWORK_TIMEOUT

LOGGER = logging.getLogger(__name__)


class BotsInterface(Instance):
    SERVICE_NAME = BOTS_DESCRIPTOR.services_by_name["Bots"].full_name

    def __init__(self, scheduler: SQLDataStore) -> None:
        self._stack = ExitStack()
        self.scheduler = scheduler

    def start(self) -> None:
        self._stack.enter_context(self.scheduler)
        self._stack.enter_context(self.scheduler.job_assigner)
        self._stack.enter_context(self.scheduler.session_expiry_timer)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info("Stopped Bots")

    def create_bot_session(
        self, bot_session: BotSession, context: CancellationContext, deadline: Optional[float] = None
    ) -> BotSession:
        """Creates a new bot session. Server should assign a unique
        name to the session. If the bot_id already exists in the database
        then any leases already assigned to that id are requeued
        (via close_bot_session) and then the name previously associated with
        the bot_id is replaced with the new name in the database. If the bot_id
        is not in the database, a new record is created.
        """
        if not bot_session.bot_id:
            raise InvalidArgumentError("Bot's id must be set by client.")

        # Create new record
        bot_session.name = self.scheduler.add_bot_entry(
            bot_session_id=bot_session.bot_id, bot_session_status=bot_session.status
        )

        LOGGER.info(f"Created new BotSession. Requesting leases. {self._bot_log_tags(bot_session)}")
        self._request_leases(bot_session, context, deadline=deadline)
        self._assign_deadline_for_botsession(bot_session)

        LOGGER.debug(f"Completed CreateBotSession. {self._bot_log_tags(bot_session)}")
        return bot_session

    def update_bot_session(
        self, bot_session: BotSession, context: CancellationContext, deadline: Optional[float] = None
    ) -> Tuple[BotSession, List[Tuple[str, bytes]]]:
        """Client updates the server. Any changes in state to the Lease should be
        registered server side. Assigns available leases with work.
        """
        LOGGER.debug(f"Beginning initial lease synchronization. {self._bot_log_tags(bot_session)}")

        orig_lease: Optional[Lease] = None
        if bot_session.leases:
            orig_lease = bot_session.leases.pop()

        if updated_lease := self.scheduler.synchronize_bot_lease(
            bot_session.name, bot_session.bot_id, bot_session.status, orig_lease
        ):
            bot_session.leases.append(updated_lease)

        LOGGER.debug(f"Completed initial lease synchronization. {self._bot_log_tags(bot_session)}")

        # Don't request new leases if a lease was removed. This mitigates situations where the scheduler
        # is updated with the new state of the lease, but a fault thereafter causes the worker to retry
        # the old UpdateBotSession call
        if not orig_lease and not updated_lease:
            self._request_leases(bot_session, context, deadline=deadline)

        metadata = self.scheduler.get_metadata_for_leases(bot_session.leases)
        self._assign_deadline_for_botsession(bot_session)

        LOGGER.debug(f"Completed UpdateBotSession. {self._bot_log_tags(bot_session)}")
        return bot_session, metadata

    def count_bots_by_status(self) -> Dict[BotStatus, int]:
        return self.scheduler.count_bots_by_status()

    def _assign_deadline_for_botsession(self, bot_session: BotSession) -> None:
        bot_session.expire_time.FromDatetime(
            self.scheduler.refresh_bot_expiry_time(bot_session.name, bot_session.bot_id)
        )

    def _request_leases(
        self,
        bot_session: BotSession,
        context: CancellationContext,
        deadline: Optional[float] = None,
    ) -> None:
        # We do not assign new leases if we are not in the OK state.
        if bot_session.status != BotStatus.OK.value:
            LOGGER.debug(f"BotSession not healthy. Skipping lease request. {self._bot_log_tags(bot_session)}")
            return

        # Only send one lease at a time currently. If any leases are set we can abort the request.
        if bot_session.leases:
            LOGGER.debug(f"BotSession already assigned. Skipping lease request. {self._bot_log_tags(bot_session)}")
            return

        # If no deadline is set default to the max we allow workers to long-poll for work
        if deadline is None:
            deadline = MAX_WORKER_TTL

        # If the specified bot session keepalive timeout is greater than the
        # deadline it can result in active bot sessions being reaped
        deadline = min(deadline, self.scheduler.bot_session_keepalive_timeout)

        # Use 80% of the given deadline to give time to respond but no less than NETWORK_TIMEOUT
        ttl = deadline * 0.8
        if ttl < NETWORK_TIMEOUT:
            LOGGER.info(
                f"BotSession expires in less time than NETWORK_TIMEOUT=[{NETWORK_TIMEOUT}],"
                f" no leases will be assigned. {self._bot_log_tags(bot_session)}"
            )
            return

        # Wait for an update to the bot session and then resynchronize the lease.
        LOGGER.debug(f"Waiting for job assignment. {self._bot_log_tags(bot_session)} deadline=[{deadline:.2f}]")
        with self.scheduler.job_assigner.assignment_context(bot_session) as event:
            context.on_cancel(event.set)
            event.wait(ttl)

        # This is a best-effort check the see if the original request is still alive. Depending on
        # network and proxy configurations, this status may not accurately reflect the state of the
        # client connection. If we know for certain that the request is no longer being monitored,
        # we can exit now to avoid state changes not being acked by the bot.
        if context.is_cancelled():
            LOGGER.debug(f"Bot request cancelled. Skipping lease synchronization. {self._bot_log_tags(bot_session)}")
            return

        # In the case that we had a timeout, we can return without post lease synchronization. This
        # helps deal with the case of uncommunicated cancellations from the bot request. If the bot
        # is actually still waiting on work, this will be immediately followed up by a new request
        # from the worker, where the initial synchronization will begin a bot ack for the pending
        # job. In the case that the request has been abandoned, it avoids competing updates to the
        # database records in the corresponding bots session.
        if not event.is_set():
            LOGGER.debug(f"Bot assignment timeout. Skipping lease synchronization. {self._bot_log_tags(bot_session)}")
            return

        # Synchronize the lease again to pick up db changes.
        LOGGER.debug(f"Synchronizing leases after job assignment wait. {self._bot_log_tags(bot_session)}")
        if lease := self.scheduler.synchronize_bot_lease(
            bot_session.name, bot_session.bot_id, bot_session.status, None
        ):
            bot_session.leases.append(lease)

    def _bot_log_tags(self, bot_session: BotSession) -> str:
        log_tags = (
            f"instance_name=[{current_instance()}]"
            f" request.bot_name=[{bot_session.name}]"
            f" request.bot_id=[{bot_session.bot_id}]"
            f" request.bot_status=[{bot_session.status}]"
        )
        if bot_session.leases:
            lease = bot_session.leases[0]
            log_tags += f" request.lease_id=[{lease.id}] request.lease_state=[{lease.state}]"
        else:
            log_tags += " request.lease_id=[] request.lease_state=[]"
        return log_tags
