"""NEOS-HMAC signing implementation."""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
import typing
import urllib.parse
from collections import OrderedDict
from datetime import datetime, timezone

import httpx
import multidict

logger = logging.getLogger(__name__)


class KeyPair(typing.NamedTuple):
    """User access key pair representation."""

    access_key_id: str
    secret_access_key: str
    partition: str


_MULTI_SPACE_REGEX = re.compile(r"( +)")


def _quote(
    resource: str,
    safe: str = "/",
    encoding: str | None = None,
    errors: str | None = None,
) -> str:
    return urllib.parse.quote(
        resource,
        safe=safe,
        encoding=encoding,
        errors=errors,
    ).replace("%7E", "~")


def _to_utc(value: datetime) -> datetime:
    """Convert to UTC time if value is not naive."""
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value.tzinfo else value


def to_amz_date(value: datetime) -> str:
    """Format datetime into AMZ date formatted string."""
    return _to_utc(value).strftime("%Y%m%dT%H%M%SZ")


def to_signer_date(value: datetime) -> str:
    """Format datetime into SignatureV4 date formatted string."""
    return _to_utc(value).strftime("%Y%m%d")


def sha256_hash(data: bytes | str | None) -> str:
    """Compute SHA-256 of data and return hash as hex encoded value."""
    data = data or b""
    data_ = data.encode() if isinstance(data, str) else data
    hasher = hashlib.sha256()
    hasher.update(data_)
    sha256sum = hasher.hexdigest()
    return sha256sum.decode() if isinstance(sha256sum, bytes) else sha256sum


def _hmac_hash(
    key: bytes | bytearray,
    data: bytes,
    *,
    hexdigest: bool = False,
) -> str | bytes:
    """Return HMacSHA256 digest of given key and data."""
    hasher = hmac.new(key, data, hashlib.sha256)
    return hasher.hexdigest() if hexdigest else hasher.digest()


def _generate_canonical_headers(headers: multidict.CIMultiDict) -> tuple[str, str]:
    """Get canonical headers."""
    canonical_headers = {}
    for key, values in headers.items():
        key_ = key.lower()
        if key_ not in ("authorization", "user-agent", "accept", "accept-encoding", "connection"):
            values_ = values if isinstance(values, (list, tuple)) else [values]
            canonical_headers[key_] = ",".join([_MULTI_SPACE_REGEX.sub(" ", value) for value in values_])

    canonical_headers = OrderedDict(sorted(canonical_headers.items()))
    signed_headers = ";".join(canonical_headers.keys())
    canonical_headers = "\n".join(
        [f"{key}:{value}" for key, value in canonical_headers.items()],
    )
    return canonical_headers, signed_headers


def _generate_canonical_query_string(query: bytes | str) -> str:
    """Get canonical query string."""
    query = query or ""
    query_: str = query.decode() if isinstance(query, bytes) else query
    return "&".join(
        [
            "=".join(pair)
            for pair in sorted(
                [params.split("=") for params in query_.split("&")],
            )
        ],
    )


def _generate_signing_key(
    schema: str,
    secret_key: str,
    date: str,
    partition: str,
    service_name: str,
) -> str | bytes:
    """Get signing key."""
    logger.debug("signing_key schema: %s", schema)
    date_key = _hmac_hash(
        (schema + secret_key).encode(),
        date.encode(),
    )
    date_region_key = _hmac_hash(date_key, partition.encode())
    date_region_service_key = _hmac_hash(
        date_region_key,
        service_name.encode(),
    )
    return _hmac_hash(date_region_service_key, f"{schema.lower()}_request".encode())


def _generate_signature(signing_key: str | bytes, string_to_sign: str) -> str | bytes:
    """Get signature."""
    return _hmac_hash(signing_key, string_to_sign.encode(), hexdigest=True)


class Signer:
    """NEOS-HMAC signer implementation."""

    def __init__(self, auth_type: str) -> None:
        self.auth_type = auth_type
        self.auth_schema = auth_type.split("-")[0]
        self.header_prefix = "x-neos" if self.auth_schema == "NEOS4" else "x-amz"

    @staticmethod
    def _generate_scope(schema: str, date: datetime, partition: str, service_name: str) -> str:
        """Get scope string."""
        return f"{to_signer_date(date)}/{partition}/{service_name}/{schema.lower()}_request"

    @staticmethod
    def _generate_string_to_sign(auth_type: str, date: datetime, scope: str, canonical_request_hash: str) -> str:
        """Get string-to-sign."""
        return f"{auth_type}\n{to_amz_date(date)}\n{scope}\n{canonical_request_hash}"

    @staticmethod
    def _generate_canonical_request_hash(
        method: str,
        url: httpx.URL,
        headers: multidict.CIMultiDict,
        content_sha256: str,
    ) -> tuple[str, str]:
        """Get canonical request hash.

        https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html

        Create a canonical request by concatenating the following strings, separated by newline characters.
        This helps ensure that the signature that you calculate and the signature that the server calculates can match.

            HTTPMethod
            CanonicalUri
            CanonicalQueryString
            CanonicalHeaders
            SignedHeaders
            HashedPayload

        HTTPMethod -
            The HTTP method.

        CanonicalUri -
            The URI-encoded version of the absolute path component URL
            (everything between the host and the question mark character (?) that starts the query string parameters).
            If the absolute path is empty, use a forward slash character (/).

        CanonicalQueryString -
            The URL-encoded query string parameters, separated by ampersands (&). Percent-encode reserved characters,
            including the space character. Encode names and values separately.
            If there are empty parameters, append the equals sign to the parameter name before encoding.
            After encoding, sort the parameters alphabetically by key name.
            If there is no query string, use an empty string ("").

        CanonicalHeaders -
            The request headers, that will be signed, and their values, separated by newline characters.
            Header names must use lowercase characters, must appear in alphabetical order,
            and must be followed by a colon (:). For the values, trim any leading or trailing spaces,
            convert sequential spaces to a single space, and separate the values for a multi-value header using commas.
            You must include the host header (HTTP/1.1) or the :authority header (HTTP/2),
            and any x-amz-* headers in the signature.
            You can optionally include other standard headers in the signature, such as content-type.

        SignedHeaders -
            The list of headers that you included in CanonicalHeaders, separated by semicolons (;).
            This indicates which headers are part of the signing process.
            Header names must use lowercase characters and must appear in alphabetical order.

        HashedPayload -
            A string created using the payload in the body of the HTTP request as input to a hash function.
            This string uses lowercase hexadecimal characters. If the payload is empty,
            use an empty string as the input to the hash function.
        """
        canonical_headers, signed_headers = _generate_canonical_headers(headers)
        canonical_query_string = _generate_canonical_query_string(url.query)

        path = _quote(url.path or "/")
        # CanonicalRequest =
        #   HTTPRequestMethod + '\n' +
        #   CanonicalURI + '\n' +
        #   CanonicalQueryString + '\n' +
        #   CanonicalHeaders + '\n\n' +
        #   SignedHeaders + '\n' +
        canonical_request = (
            f"{method}\n"
            f"{path}\n"
            f"{canonical_query_string}\n"
            f"{canonical_headers}\n\n"
            f"{signed_headers}\n"
            f"{content_sha256}"
        )
        logger.debug("canonical_request: %s", canonical_request)

        return sha256_hash(canonical_request), signed_headers

    @staticmethod
    def _generate_authorization(
        auth_type: str,
        access_key: str,
        scope: str,
        signed_headers: str,
        signature: str | bytes,
    ) -> str:
        """Get authorization."""
        return f"{auth_type} Credential={access_key}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"

    def sign_v4(
        self,
        service_name: str,
        method: str,
        url: httpx.URL,
        partition: str,
        headers: multidict.CIMultiDict,
        credentials: KeyPair,
        content: bytes | None,
        date: datetime,
    ) -> multidict.CIMultiDict:
        """Sign request with NEOS-HMAC algorithm."""
        logger.debug("url: %s", url)
        logger.debug("headers: %s", headers)
        content_sha256 = sha256_hash(content) if url.scheme == "http" else "UNSIGNED-PAYLOAD"
        content_header = f"{self.header_prefix}-content-sha256"
        if content_header not in headers:
            headers[content_header] = content_sha256
        scope = self._generate_scope(self.auth_schema, date, partition, service_name)
        canonical_request_hash, signed_headers = self._generate_canonical_request_hash(
            method,
            url,
            headers,
            content_sha256,
        )
        string_to_sign = self._generate_string_to_sign(self.auth_type, date, scope, canonical_request_hash)
        logger.debug("scope: %s", scope)
        logger.debug("string_to_sign: %s", string_to_sign)
        signing_key = _generate_signing_key(
            self.auth_schema,
            credentials.secret_access_key,
            to_signer_date(date),
            partition,
            service_name,
        )
        signature = _generate_signature(signing_key, string_to_sign)
        authorization = self._generate_authorization(
            self.auth_type,
            credentials.access_key_id,
            scope,
            signed_headers,
            signature,
        )
        headers["Authorization"] = authorization
        return headers
