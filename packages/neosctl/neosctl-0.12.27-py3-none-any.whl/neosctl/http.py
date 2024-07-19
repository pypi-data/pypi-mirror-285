"""HTTP Client implementation for calling NEOS services."""

import logging
import re
import typing
from datetime import datetime, timezone
from enum import Enum

import httpcore
import httpx

from neosctl import signer

logger = logging.getLogger(__name__)


CONVERT_RE = re.compile(r"(?<!^)(?=[A-Z])")


class RequestException(Exception):  # noqa: N818
    """Base class for all http request failures."""

    def __init__(
        self: ...,
        type_: str,
        status: int = 500,
    ) -> None:
        self._type = type_
        self.status = status

    @property
    def type(self: ...) -> str:
        """Expose private type attribute."""
        return self._type


class Method(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


def log_request(request: httpx.Request) -> None:
    """Event hook for httpx events to log requests."""
    logger.info(
        "[Request] %s %s",
        request.method.upper(),
        request.url,
    )


class NeosBearerClientAuth:
    """Bearer token auth implementation for httpx."""

    def __init__(self, token: str) -> None:
        self.token = token

    def __call__(self, request: httpx.Request) -> httpx.Request:
        """Generate authorization header."""
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

    def __eq__(self, other: object) -> bool:  # noqa: D105
        return isinstance(other, NeosBearerClientAuth) and other.token == self.token


class NeosSignatureClientAuth:
    """NEOS-HMAC auth implementation for httpx."""

    def __init__(self, key_pair: signer.KeyPair, service: str) -> None:
        self.key_pair = key_pair
        self.service = service

    def __call__(self, request: httpx.Request) -> httpx.Request:
        """Generate authorization header."""
        dt = datetime.now(tz=timezone.utc)
        request.headers["x-neos-date"] = signer.to_amz_date(dt)
        request.headers["host"] = request.url.netloc.decode("utf-8")

        body = request.content.decode("utf-8")
        if body:
            request.headers["Content-Length"] = str(len(body))

        s = signer.Signer("NEOS4-HMAC-SHA256")
        s.sign_v4(
            self.service,
            request.method,
            request.url,
            self.key_pair.partition,
            request.headers,
            self.key_pair,
            body,
            dt,
        )

        return request

    def __eq__(self, other: object) -> bool:  # noqa: D105
        return isinstance(other, NeosSignatureClientAuth) and other.key_pair == self.key_pair


class NeosClient:
    """Generic HTTP client supporting Bearer and NEOS-HMAC-SHA256 auth."""

    def __init__(
        self,
        service: str,
        token: typing.Optional[str],
        key_pair: typing.Optional[signer.KeyPair],
        proxy: typing.Optional[str] = None,
    ) -> None:
        self._service = service
        self._token = token
        self._key_pair = key_pair
        self._proxy = proxy

    @property
    def service_name(self) -> str:
        """Name of service being called."""
        return self._service

    @property
    def token(self) -> typing.Optional[str]:
        """Bearer token, if provided."""
        return self._token

    @property
    def key_pair(self) -> typing.Optional[signer.KeyPair]:
        """Signing keypair, if provided."""
        return self._key_pair

    def request(
        self,
        url: str,
        method: Method,
        params: typing.Optional[dict] = None,
        headers: typing.Optional[dict] = None,
        json: typing.Optional[dict] = None,
        *,
        verify: bool = True,
        **kwargs: ...,
    ) -> httpx.Response:
        """Call requested url."""
        if self.key_pair is not None:
            auth = NeosSignatureClientAuth(
                self.key_pair,
                self.service_name,
            )
        elif self.token:
            auth = NeosBearerClientAuth(self.token)
        else:
            auth = None

        with httpx.Client(event_hooks={"request": [log_request]}, verify=verify, proxy=self._proxy) as client:
            try:
                r = client.request(
                    url=url,
                    method=method.value,
                    params=params,
                    json=json,
                    headers=headers,
                    auth=auth,
                    **kwargs,
                )
            except httpcore.ConnectTimeout as e:
                raise RequestException(type_="service-connect-timeout") from e
            except httpcore.ReadTimeout as e:
                raise RequestException(type_="service-read-timeout") from e
            except httpx.ConnectError as e:
                raise RequestException(type_="service-connection-error") from e

        return r
