import asyncio
import functools
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
from google.auth import exceptions, transport
from google.auth._credentials_async import Credentials
from google.auth._default_async import default_async
from google.oauth2._service_account_async import Credentials as OAuthCreds

__all__ = ["Client", "AuthorizedSession"]


class _Response(transport.Response):
    """
    Requests transport response adapter.
    Args:
        response (httpx.Response): The raw Requests response.
    """

    def __init__(self, response: httpx.Response):
        self._response = response
        self._content: bytes | None = None

    @property
    def status(self) -> int:
        return self._response.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self._response.headers

    @property
    def data(self) -> bytes:
        return self._response.content

    async def raw_content(self):
        return await self.content()

    async def content(self) -> bytes:
        if self._content is None:
            self._content = await self._response.aread()
        return self._content


class Request(transport.Request):
    """Requests request adapter.
    This class is used internally for making requests using transports
    in a consistent way. If you use :class:`AuthorizedSession` you do not need
    to construct or use this class directly.
    This class can be useful if you want to manually refresh a
    :class:`~google.auth.credentials.Credentials` instance::
        import google.auth.transport.httpx_requests
        request = google.auth.transport.httpx_requests.Request()
        credentials.refresh(request)
    Args:
        client (httpx.Client): The client to use to make HTTP requests.
            If not specified, a session will be created.
    .. automethod:: __call__
    """

    def __init__(self, httpx_client: httpx.AsyncClient | None = None):
        self.client = httpx_client

    async def __call__(
        self,
        url: str,
        method: str = "GET",
        body: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float = 180,
        **kwargs,
    ):
        """
        Make an HTTP request using httpx.
        Args:
            url (str): The URL to be requested.
            method (Optional[str]):
                The HTTP method to use for the request. Defaults to 'GET'.
            body (Optional[bytes]):
                The payload or body in HTTP request.
            headers (Optional[Mapping[str, str]]):
                Request headers.
            timeout (Optional[int]): The number of seconds to wait for a
                response from the server. If not specified or if None, the
                requests default timeout will be used.
            kwargs: Additional arguments passed through to the underlying
                requests :meth:`requests.Session.request` method.
        Returns:
            google.auth.transport.Response: The HTTP response.
        Raises:
            google.auth.exceptions.TransportError: If any exception occurred.
        """

        try:
            if self.client is None:  # pragma: NO COVER
                self.client = httpx.AsyncClient(http2=True)

            response = await self.client.request(
                method,
                url,
                data=body,
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
            return _Response(response)

        except httpx.HTTPError as caught_exc:
            new_exc = exceptions.TransportError(caught_exc)
            raise new_exc from caught_exc


class AuthorizedSession(httpx.AsyncClient):
    """This is an implementation of the Authorized Session class. We utilize a
    httpx transport instance, and the interface mirrors the
    google.auth.transport.requests
    Authorized Session class, except for the change in the transport used in
    the use case.
    A Requests Session class with credentials.
    This class is used to perform requests to API endpoints that require
    authorization::
        from google.auth.transport import httpx_requests
        with httpx_requests.AuthorizedSession(credentials) as authed_session:
            response = await authed_session.request(
                'GET', 'https://www.googleapis.com/storage/v1/b')
    The underlying :meth:`request` implementation handles adding the
    credentials' headers to the request and refreshing credentials as needed.
    Args:
        credentials (google.auth._credentials.Credentials):
            The credentials to add to the request.
        refresh_status_codes (Sequence[int]): Which HTTP status codes indicate
            that credentials should be refreshed and the request should be
            retried.
        max_refresh_attempts (int): The maximum number of times to attempt to
            refresh the credentials and retry the request.
        refresh_timeout (Optional[int]): The timeout value in seconds for
            credential refresh HTTP requests.
        auth_request (google.auth.transport.httpx_requests.Request):
            (Optional) An instance of
            :class:`~google.auth.transport.httpx_requests.Request` used when
            refreshing credentials. If not passed,
            an instance of
            :class:`~google.auth.transport.httpx_requests.Request` is created.
        kwargs: Additional arguments passed through to the underlying
            ClientSession :meth:`httpx.ClientSession` object.
    """

    def __init__(
        self,
        credentials: Credentials | OAuthCreds,
        refresh_status_codes=transport.DEFAULT_REFRESH_STATUS_CODES,
        max_refresh_attempts=transport.DEFAULT_MAX_REFRESH_ATTEMPTS,
        refresh_timeout=None,
        auth_request=None,
        auto_decompress: bool = False,
        **kwargs,
    ):
        super(AuthorizedSession, self).__init__(**kwargs)
        self.credentials: Credentials = credentials
        self._refresh_status_codes = refresh_status_codes
        self._max_refresh_attempts = max_refresh_attempts
        self._refresh_timeout = refresh_timeout
        self._is_mtls = False
        self._auth_request = auth_request
        self._auth_request_session: httpx.AsyncClient | None = None
        self._auto_decompress = auto_decompress
        self._refresh_lock = asyncio.Lock()

    async def request(  # type: ignore
        self,
        method: str,
        url: str,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        max_allowed_time: float | None = None,
        timeout: float = 180.0,
        **kwargs,
    ) -> httpx.Response:
        """Implementation of Authorized Session httpx request.
        Args:
            method (str):
                The http request method used (e.g. GET, PUT, DELETE)
            url (str):
                The url at which the http request is sent.
            data (Optional[dict]): Dictionary, list of tuples, bytes, or
                file-like object to send in the body of the Request.
            headers (Optional[dict]): Dictionary of HTTP Headers to send with
                the Request.
            timeout (Optional[Union[float, httpx.ClientTimeout]]):
                The amount of time in seconds to wait for the server response
                with each individual request. Can also be passed as an
                ``httpx.ClientTimeout`` object.
            max_allowed_time (Optional[float]):
                If the method runs longer than this, a ``Timeout`` exception is
                automatically raised. Unlike the ``timeout`` parameter, this
                value applies to the total method execution time, even if
                multiple requests are made under the hood.
                Mind that it is not guaranteed that the timeout error is raised
                at ``max_allowed_time``. It might take longer, for example, if
                an underlying request takes a lot of time, but the request
                itself does not timeout, e.g. if a large file is being
                transmitted. The timout error will be raised after such
                request completes.
        """
        async with httpx.AsyncClient(http2=True) as self._auth_request_session:
            self._auth_request = Request(self._auth_request_session)

            _credential_refresh_attempt = kwargs.pop(
                "_credential_refresh_attempt", 0
            )
            request_headers = headers.copy() if headers is not None else {}

            auth_request = (
                self._auth_request
                if timeout is None
                else functools.partial(self._auth_request, timeout=timeout)
            )

            await self.credentials.before_request(
                auth_request, method, url, request_headers
            )

            response: httpx.Response = await super(
                AuthorizedSession, self
            ).request(
                method,
                url,
                data=data,
                headers=request_headers,
                timeout=timeout,
                **kwargs,
            )

            if (
                response.status_code in self._refresh_status_codes
                and _credential_refresh_attempt < self._max_refresh_attempts
            ):
                auth_request = (
                    self._auth_request
                    if timeout is None
                    else functools.partial(self._auth_request, timeout=timeout)
                )

                async with self._refresh_lock:
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        None, self.credentials.refresh, auth_request
                    )

                return await self.request(
                    method,
                    url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    _credential_refresh_attempt=_credential_refresh_attempt + 1,
                    **kwargs,
                )

        return response


@asynccontextmanager
async def Client(
    base_url: str, creds: OAuthCreds | None = None
) -> AsyncIterator[AuthorizedSession]:
    credentials = creds
    if creds is None:
        credentials, _ = default_async()

    async with AuthorizedSession(credentials) as s:  # type: ignore
        s.base_url = httpx.URL(base_url)
        yield s
