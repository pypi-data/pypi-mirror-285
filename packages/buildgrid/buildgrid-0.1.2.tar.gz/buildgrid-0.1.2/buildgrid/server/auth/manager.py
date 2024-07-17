# Copyright (C) 2023 Bloomberg LP
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
import sys
from abc import ABC, abstractmethod
from contextvars import ContextVar
from typing import Any, Dict, Mapping, Optional, Set, Tuple, Type, Union, cast

import grpc

from buildgrid._exceptions import InvalidArgumentError
from buildgrid.server.auth.config import InstanceAuthorizationConfig
from buildgrid.server.auth.enums import AuthMetadataAlgorithm
from buildgrid.server.auth.exceptions import (
    AuthError,
    ExpiredTokenError,
    InvalidAuthorizationHeaderError,
    InvalidTokenError,
    MissingTokenError,
    UnboundedTokenError,
    UnexpectedTokenParsingError,
)
from buildgrid.settings import AUTH_CACHE_SIZE

LOGGER = logging.getLogger(__name__)


# Since jwt authorization is not required, make it optional.
# If used, but module not imported/found, will raise an exception.
try:
    import jwt

    AlgorithmType = Union[
        Type[jwt.algorithms.RSAAlgorithm], Type[jwt.algorithms.ECAlgorithm], Type[jwt.algorithms.HMACAlgorithm]
    ]

    # Algorithm classes defined in: https://github.com/jpadilla/pyjwt/blob/master/jwt/algorithms.py
    ALGORITHM_TO_PYJWT_CLASS: Dict[str, AlgorithmType] = {
        "RSA": jwt.algorithms.RSAAlgorithm,
        "EC": jwt.algorithms.ECAlgorithm,
        "oct": jwt.algorithms.HMACAlgorithm,
    }

except ImportError:
    pass


def _log_and_raise(request_name: str, exception: AuthError) -> str:
    LOGGER.info(f"Authorization error. Rejecting '{request_name}' request: " f"Reason=[{str(exception)}]")
    raise exception


class JwtParser:
    def __init__(
        self,
        secret: Optional[str] = None,
        algorithm: AuthMetadataAlgorithm = AuthMetadataAlgorithm.UNSPECIFIED,
        jwks_url: Optional[str] = None,
        audience: Optional[str] = None,
        jwks_fetch_minutes: int = 60,
    ) -> None:
        self._check_jwt_support(algorithm)

        self._algorithm = algorithm
        self._audience = audience
        self._jwks_client = None

        if (secret is None and jwks_url is None) or (secret is not None and jwks_url is not None):
            raise TypeError("Exactly one of `secret` or `jwks_url` must be set")

        self._secret = secret

        if jwks_url is not None:
            try:
                jwks_lifespan = jwks_fetch_minutes * 60
                self._jwks_client = jwt.PyJWKClient(jwks_url, lifespan=jwks_lifespan, max_cached_keys=AUTH_CACHE_SIZE)
            except NameError:
                LOGGER.error("JWT auth is enabled but PyJWT could not be imported.")
                raise

    def _check_jwt_support(self, algorithm: AuthMetadataAlgorithm) -> None:
        """Ensures JWT and possible dependencies are available."""
        if algorithm == AuthMetadataAlgorithm.UNSPECIFIED:
            raise InvalidArgumentError("JWT authorization method requires an algorithm to be specified")

        if "jwt" not in sys.modules:
            raise InvalidArgumentError("JWT authorization method requires PyJWT")

    def parse(self, token: str) -> Dict[str, Any]:
        payload: Optional[Dict[str, Any]] = None
        try:
            if self._secret is not None:
                payload = jwt.decode(
                    token,
                    self._secret,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audience,
                    options={"require": ["exp"], "verify_exp": True},
                )

            elif self._jwks_client is not None:
                signing_key = self._jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[self._algorithm.value.upper()],
                    audience=self._audience,
                    options={"require": ["exp"], "verify_exp": True},
                )

        except jwt.exceptions.ExpiredSignatureError as e:
            raise ExpiredTokenError() from e

        except jwt.exceptions.MissingRequiredClaimError as e:
            raise UnboundedTokenError("Missing required JWT claim, likely 'exp' was not set") from e

        except jwt.exceptions.InvalidTokenError as e:
            raise InvalidTokenError() from e

        except Exception as e:
            raise UnexpectedTokenParsingError() from e

        if payload is None:
            raise InvalidTokenError()

        return payload

    def identity_from_token(self, token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        payload = self.parse(token)
        return payload.get("act"), payload.get("sub"), payload.get("aud")


class AuthManager(ABC):
    @abstractmethod
    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        """Determine whether or not a request is authorized.

        This method takes a ``ServicerContext`` for an incoming gRPC request,
        along with the name of the request, and the name of the instance that
        the request is intended for. Information about the identity of the
        requester is extracted from the context, for example a JWT token.

        This identity information is compared to the ACL configuration given
        to this class at construction time to determine authorization for the
        request.

        Args:
            context (ServicerContext): The context for the gRPC request to check
                the authz status of.

            instance_name (str): The name of the instance that the gRPC request
                will be interacting with. This is used for per-instance ACLs.

            request_name (str): The name of the request being authorized, for
                example `Execute`.

        Returns:
            bool: Whether the request is authorized.

        """


class JWTAuthManager(AuthManager):
    def __init__(
        self,
        secret: Optional[str] = None,
        algorithm: AuthMetadataAlgorithm = AuthMetadataAlgorithm.UNSPECIFIED,
        jwks_url: Optional[str] = None,
        audience: Optional[str] = None,
        jwks_fetch_minutes: int = 60,
        acls: Optional[Mapping[str, InstanceAuthorizationConfig]] = None,
        allow_unauthorized_instances: Optional[Set[str]] = None,
    ) -> None:
        """Initializes a new :class:`JWTAuthManager`.

        Args:
            secret (str): The secret or key to be used for validating request,
                depending on `method`. Defaults to ``None``.

            algorithm (AuthMetadataAlgorithm): The crytographic algorithm used
                to encode `secret`. Defaults to ``UNSPECIFIED``.

            jwks_url (str): The url to fetch the JWKs. Either secret or
                this field must be specified if the authentication method is JWT.
                Defaults to ``None``.

            audience (str): The audience used to validate jwt tokens against.
                The tokens must have an audience field.

            jwks_fetch_minutes (int): The number of minutes to cache JWKs fetches
                for. Defaults to 60.

            acls (Mapping[str, InstanceAuthorizationConfig] | None): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.

            allow_unauthorized_instances(Set[str] | None): List of instances that should
                be allowed to have unautheticated access

        Raises:
            InvalidArgumentError: If `algorithm` is not supported.

        """
        self._acls = acls
        self._allow_unauthorized_instances = allow_unauthorized_instances
        self._token_parser = JwtParser(secret, algorithm, jwks_url, audience, jwks_fetch_minutes)

    def _token_from_request_context(self, context: grpc.ServicerContext, request_name: str) -> str:
        try:
            bearer = cast(str, dict(context.invocation_metadata())["authorization"])

        except KeyError:
            # Reject requests not carrying a token
            _log_and_raise(request_name, MissingTokenError())

        # Reject requests with malformatted bearer
        if not bearer.startswith("Bearer "):
            _log_and_raise(request_name, InvalidAuthorizationHeaderError())

        return bearer[7:]

    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        # No need to authorize if unauthorized access is allowed for the instance
        if self._allow_unauthorized_instances and instance_name in self._allow_unauthorized_instances:
            return True
        try:
            token = self._token_from_request_context(context, request_name)
            actor, subject, workflow = self._token_parser.identity_from_token(token)
        except NameError:
            LOGGER.error("JWT auth is enabled but PyJWT is not installed.")
            return False
        except AuthError as e:
            LOGGER.info(f"Error authorizing JWT token: {str(e)}")
            return False

        # If no ACL config was provided at all, don't do any more validation
        if self._acls is None:
            return True

        instance_acl_config = self._acls.get(instance_name)
        if instance_acl_config is not None:
            return instance_acl_config.is_authorized(request_name, actor=actor, subject=subject, workflow=workflow)

        # If there is an ACL, but no config for this instance, deny all
        return False


class HeadersAuthManager(AuthManager):
    def __init__(
        self,
        acls: Optional[Mapping[str, InstanceAuthorizationConfig]] = None,
        allow_unauthorized_instances: Optional[Set[str]] = None,
    ) -> None:
        """Initializes a new :class:`HeadersAuthManager`.

        Args:
            acls (Mapping[str, InstanceAuthorizationConfig] | None): An optional
                map of instance name -> ACL config to use for per-instance
                authorization.

            allow_unauthorized_instances(Set[str] | None): List of instances that should
                be allowed to have unautheticated access

        """
        self._acls = acls
        self._allow_unauthorized_instances = allow_unauthorized_instances

    def authorize(self, context: grpc.ServicerContext, instance_name: str, request_name: str) -> bool:
        # No need to authorize if unauthorized access is allowed for the instance
        if self._allow_unauthorized_instances and instance_name in self._allow_unauthorized_instances:
            return True
        metadata_dict = dict(context.invocation_metadata())
        actor = str(metadata_dict.get("x-request-actor"))
        subject = str(metadata_dict.get("x-request-subject"))
        workflow = str(metadata_dict.get("x-request-workflow"))

        # If no ACL config was provided at all, don't do any more validation
        if self._acls is None:
            return True

        instance_acl_config = self._acls.get(instance_name)
        if instance_acl_config is not None:
            return instance_acl_config.is_authorized(request_name, actor=actor, subject=subject, workflow=workflow)

        # If there is an ACL, but no config for this instance, deny all
        return False


# TODO: Once https://github.com/grpc/grpc/issues/33071 is resolved this AuthContext can be
# replaced with a gRPC interceptor stores the AuthManager in a request-local ContextVar.
AuthContext: "ContextVar[Optional[AuthManager]]" = ContextVar("AuthManager", default=None)


def set_auth_manager(manager: Optional[AuthManager]) -> None:
    AuthContext.set(manager)


def get_auth_manager() -> Optional[AuthManager]:
    return AuthContext.get()


def authorize_request(request_context: grpc.ServicerContext, instance_name: str, request_name: str) -> None:
    manager = get_auth_manager()

    # If no auth is configured, don't do authz
    if manager is None:
        return

    if manager.authorize(request_context, instance_name, request_name):
        return

    LOGGER.info("Authentication failed for request=[" f"{request_name}], peer=[{request_context.peer()}]")
    # No need to yield here since calling `abort` raises an Exception
    request_context.abort(grpc.StatusCode.UNAUTHENTICATED, "No valid authorization or authentication provided")
