import re
from typing import Union, cast

from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    HTTPScope,
    Scope,
    WebSocketScope,
)
from fastapi import FastAPI
from semver import Version

from authentication.core import Constants


class VersionMiddleware:
    """
    Use this middleware to parse the Accept Header if present and get an API version
    from the vendor tree. See https://www.rfc-editor.org/rfc/rfc6838#section-3.2

    If incoming http or websocket request contains an Accept header with the following
    value: `"accept/vnd.vendor_prefix.v42+json"`, the scope of the ASGI application
    will then contain an `api_version` of 42.

    If the http or websocket request does not contain an Accept header, or if the accept
    header value does not use a proper format, the scope of the ASGI application will
    then contain an `api_version` that defaults to the provided `latest_version`

    This also allows for version to be specified using the specified header key.
    """

    def __init__(self, app: ASGI3Application, vendor_prefix: str, latest_version: Version = Version(1)):
        self.app = app
        self.vendor_prefix = vendor_prefix
        self.latest_version = latest_version
        self.version_regex = re.compile(Constants.SEMVER_REGEX, re.VERBOSE)
        # Accept header regex with semver pattern embedded
        self.accept_header_regex = re.compile(Constants.ACCEPT_HEADER_VERSION_REGEX.format(
            vendor_prefix=re.escape(vendor_prefix)
        ))

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable):
        if not scope["type"] in ("http", "websocket"):
            return await self.app(scope, receive, send)

        scope = cast(Union[HTTPScope, WebSocketScope], scope)
        headers = dict(scope.get("headers", []))
        scope["latest_version"] = self.latest_version
        scope["requested_version"] = self.latest_version

        if b"accept" in headers:
            accept_header = headers[b"accept"].decode("latin1")
            match = self.accept_header_regex.match(accept_header)

            if match:
                version_str = match.group("version")
                try:
                    # Normalize version: remove 'v' prefix and ensure minor/patch exist
                    normalized = version_str.lstrip("v")
                    parts = normalized.split("-", 1)
                    version_part = parts[0]
                    prerelease = parts[1] if len(parts) > 1 else None

                    # Ensure we have at least major.minor.patch
                    version_numbers = version_part.split(".")
                    if len(version_numbers) == 1:
                        version_part = f"{version_numbers[0]}.0.0"
                    elif len(version_numbers) == 2:
                        version_part = f"{version_numbers[0]}.{version_numbers[1]}.0"

                    if prerelease:
                        normalized = f"{version_part}-{prerelease}"
                    else:
                        normalized = version_part

                    version = Version.parse(normalized)
                    scope["requested_version"] = version
                except ValueError:
                    pass

        return await self.app(scope, receive, send)


def setup_version_middleware(
    app: FastAPI,
    vendor_prefix: str,
    latest_version: Version = Version(1)
) -> None:
    """Sets up the version middleware for the ASGI application."""
    app.add_middleware(VersionMiddleware, vendor_prefix=vendor_prefix, latest_version=latest_version)
