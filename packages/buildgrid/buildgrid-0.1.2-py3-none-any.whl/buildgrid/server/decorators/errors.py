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

import contextlib
import inspect
import itertools
import logging
from functools import wraps
from typing import Any, Callable, Iterator, Type, TypeVar, cast

import grpc
from google.protobuf.message import Message

from buildgrid._exceptions import (
    BotSessionCancelledError,
    BotSessionClosedError,
    BotSessionMismatchError,
    DuplicateBotSessionError,
    FailedPreconditionError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    RetriableError,
    StorageFullError,
    UnknownBotSessionError,
)

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def _error_context(context: grpc.ServicerContext, unhandled_message: str) -> Iterator[None]:
    try:
        yield

    except BotSessionCancelledError as e:
        LOGGER.info(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.CANCELLED)

    except BotSessionClosedError as e:
        LOGGER.debug(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.DATA_LOSS)

    except ConnectionError as e:
        LOGGER.exception(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.UNAVAILABLE)

    except DuplicateBotSessionError as e:
        LOGGER.info(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.ABORTED)

    except FailedPreconditionError as e:
        LOGGER.error(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.FAILED_PRECONDITION)

    except (InvalidArgumentError, BotSessionMismatchError, UnknownBotSessionError) as e:
        LOGGER.info(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)

    except NotFoundError as e:
        LOGGER.debug(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.NOT_FOUND)

    except NotImplementedError as e:
        LOGGER.info(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)

    except PermissionDeniedError as e:
        LOGGER.exception(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)

    except RetriableError as e:
        LOGGER.info(f"Retriable error, client should retry in: {e.retry_info.retry_delay}")
        context.abort_with_status(e.error_status)

    except StorageFullError as e:
        LOGGER.exception(e)
        context.set_details(str(e))
        context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)

    except Exception as e:
        if context.code() is None:  # type: ignore[attr-defined]
            LOGGER.exception(unhandled_message)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)


def handle_errors(
    fallback_return_type: Type[Message], get_printable_request: Callable[[Any], Any] = lambda r: str(r)
) -> Callable[[Func], Func]:
    def decorator(f: Func) -> Func:
        @wraps(f)
        def return_wrapper(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
            if isinstance(request, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                initial_request = next(request)
                printed_request = get_printable_request(initial_request)
                request = itertools.chain([initial_request], request)
            else:
                printed_request = get_printable_request(request)

            with _error_context(context, f"Unexpected error in {f.__name__}; request=[{printed_request}]"):
                return f(self, request, context)

            # This looks odd, but this code is actually reachable.
            # If _error_context suppresses an exception, we return a default.
            return fallback_return_type()

        @wraps(f)
        def yield_wrapper(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
            if isinstance(request, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                initial_request = next(request)
                printed_request = get_printable_request(initial_request)
                request = itertools.chain([initial_request], request)
            else:
                printed_request = get_printable_request(request)

            with _error_context(context, f"Unexpected error in {f.__name__}; request=[{printed_request}]"):
                yield from f(self, request, context)
                return

            # This looks odd, but this code is actually reachable.
            # If _error_context suppresses an exception, we return a default.
            yield fallback_return_type()

        if inspect.isgeneratorfunction(f):
            return cast(Func, yield_wrapper)
        return cast(Func, return_wrapper)

    return decorator
