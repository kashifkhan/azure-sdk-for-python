# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import logging
import ssl
from typing import (
    Any,
    Iterator,
    Optional,
    Union,
    TypeVar,
    overload,
    TYPE_CHECKING,
    MutableMapping,
)
from urllib3.util.retry import Retry
from urllib3.exceptions import (
    DecodeError as CoreDecodeError,
    ReadTimeoutError,
    ProtocolError,
    NewConnectionError,
    ConnectTimeoutError,
)
import requests
from requests.adapters import BaseAdapter

from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import (
    ServiceRequestError,
    ServiceRequestTimeoutError,
    ServiceResponseError,
    ServiceResponseTimeoutError,
    IncompleteReadError,
    HttpResponseError,
    DecodeError,
)
from . import HttpRequest

from ._base import HttpTransport, HttpResponse, _HttpResponseBase
from ._bigger_block_size_http_adapters import BiggerBlockSizeHTTPAdapter
from .._tools import (
    is_rest as _is_rest,
    handle_non_stream_rest_response as _handle_non_stream_rest_response,
)

if TYPE_CHECKING:
    from ...rest import HttpRequest as RestHttpRequest, HttpResponse as RestHttpResponse

AzureErrorUnion = Union[
    ServiceRequestError,
    ServiceResponseError,
    IncompleteReadError,
    HttpResponseError,
]

PipelineType = TypeVar("PipelineType")

_LOGGER = logging.getLogger(__name__)


class _SSLContextAdapter(BiggerBlockSizeHTTPAdapter):
    """A requests adapter whose connection pool uses a caller-supplied :class:`ssl.SSLContext`.

    ``requests`` only accepts client certificates as file paths via ``cert=``. This adapter lets
    ``connection_cert`` be an in-memory ``ssl.SSLContext`` (for example one carrying a client
    certificate for mTLS token binding) by configuring the underlying urllib3 pool with it. The
    pool keys on the SSLContext, so mounting a new adapter for a rotated context yields fresh TLS
    connections while old pooled connections age out.
    """

    def __init__(self, *args: Any, ssl_context: Optional[ssl.SSLContext] = None, **kwargs: Any) -> None:
        self._ssl_context = ssl_context
        super().__init__(*args, **kwargs)  # HTTPAdapter.__init__ calls init_poolmanager

    def init_poolmanager(self, *args: Any, **kwargs: Any):  # type: ignore[override]
        if self._ssl_context is not None:
            kwargs["ssl_context"] = self._ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args: Any, **kwargs: Any):  # type: ignore[override]
        if self._ssl_context is not None:
            kwargs["ssl_context"] = self._ssl_context
        return super().proxy_manager_for(*args, **kwargs)


def _read_raw_stream(response, chunk_size=1):
    # Special case for urllib3.
    if hasattr(response.raw, "stream"):
        try:
            yield from response.raw.stream(chunk_size, decode_content=False)
        except ProtocolError as e:
            raise ServiceResponseError(e, error=e) from e
        except CoreDecodeError as e:
            raise DecodeError(e, error=e) from e
        except ReadTimeoutError as e:
            raise ServiceResponseTimeoutError(e, error=e) from e
    else:
        # Standard file-like object.
        while True:
            chunk = response.raw.read(chunk_size)
            if not chunk:
                break
            yield chunk

    # following behavior from requests iter_content, we set content consumed to True
    # https://github.com/psf/requests/blob/master/requests/models.py#L774
    response._content_consumed = True  # pylint: disable=protected-access


class _RequestsTransportResponseBase(_HttpResponseBase):
    """Base class for accessing response data.

    :param HttpRequest request: The request.
    :param requests_response: The object returned from the HTTP library.
    :type requests_response: requests.Response
    :param int block_size: Size in bytes.
    """

    def __init__(self, request, requests_response, block_size=None):
        super(_RequestsTransportResponseBase, self).__init__(request, requests_response, block_size=block_size)
        self.status_code = requests_response.status_code
        self.headers = requests_response.headers
        self.reason = requests_response.reason
        self.content_type = requests_response.headers.get("content-type")

    def body(self):
        return self.internal_response.content

    def text(self, encoding: Optional[str] = None) -> str:
        """Return the whole body as a string.

        If encoding is not provided, mostly rely on requests auto-detection, except
        for BOM, that requests ignores. If we see a UTF8 BOM, we assumes UTF8 unlike requests.

        :param str encoding: The encoding to apply.
        :rtype: str
        :return: The body as text.
        """
        if not encoding:
            # There is a few situation where "requests" magic doesn't fit us:
            # - https://github.com/psf/requests/issues/654
            # - https://github.com/psf/requests/issues/1737
            # - https://github.com/psf/requests/issues/2086
            from codecs import BOM_UTF8

            if self.internal_response.content[:3] == BOM_UTF8:
                encoding = "utf-8-sig"

        if encoding:
            if encoding == "utf-8":
                encoding = "utf-8-sig"

            self.internal_response.encoding = encoding

        return self.internal_response.text


class StreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~azure.core.pipeline.Pipeline
    :param response: The response object.
    :type response: ~azure.core.pipeline.transport.HttpResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(self, pipeline, response, **kwargs):
        self.pipeline = pipeline
        self.request = response.request
        self.response = response
        self.block_size = response.block_size
        decompress = kwargs.pop("decompress", True)
        if len(kwargs) > 0:
            raise TypeError("Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0]))
        internal_response = response.internal_response
        if decompress:
            self.iter_content_func = internal_response.iter_content(self.block_size)
        else:
            self.iter_content_func = _read_raw_stream(internal_response, self.block_size)
        self.content_length = int(response.headers.get("Content-Length", 0))

    def __len__(self):
        return self.content_length

    def __iter__(self):
        return self

    def __next__(self):
        internal_response = self.response.internal_response
        try:
            chunk = next(self.iter_content_func)
            if not chunk:
                raise StopIteration()
            return chunk
        except StopIteration:
            internal_response.close()
            raise StopIteration()  # pylint: disable=raise-missing-from
        except requests.exceptions.StreamConsumedError:
            raise
        except requests.exceptions.ContentDecodingError as err:
            raise DecodeError(err, error=err) from err
        except requests.exceptions.ChunkedEncodingError as err:
            msg = err.__str__()
            if "IncompleteRead" in msg:
                _LOGGER.warning("Incomplete download.")
                internal_response.close()
                raise IncompleteReadError(err, error=err) from err
            _LOGGER.warning("Unable to stream download.")
            internal_response.close()
            raise HttpResponseError(err, error=err) from err
        except requests.ConnectionError as err:
            internal_response.close()
            if err.args and isinstance(err.args[0], ReadTimeoutError):
                raise ServiceResponseTimeoutError(err, error=err) from err
            raise ServiceResponseError(err, error=err) from err
        except requests.RequestException as err:
            internal_response.close()
            raise ServiceResponseError(err, error=err) from err
        except Exception as err:
            _LOGGER.warning("Unable to stream download.")
            internal_response.close()
            raise

    next = __next__  # Python 2 compatibility.


class RequestsTransportResponse(HttpResponse, _RequestsTransportResponseBase):
    """Streaming of data from the response."""

    def stream_download(self, pipeline: PipelineType, **kwargs) -> Iterator[bytes]:
        """Generator for streaming request body data.

        :param pipeline: The pipeline object
        :type pipeline: ~azure.core.pipeline.Pipeline
        :rtype: iterator[bytes]
        :return: The stream of data
        """
        return StreamDownloadGenerator(pipeline, self, **kwargs)


class RequestsTransport(HttpTransport):
    """Implements a basic requests HTTP sender.

    Since requests team recommends to use one session per requests, you should
    not consider this class as thread-safe, since it will use one Session
    per instance.

    In this simple implementation:
    - You provide the configured session if you want to, or a basic session is created.
    - All kwargs received by "send" are sent to session.request directly

    :keyword requests.Session session: Request session to use instead of the default one.
    :keyword bool session_owner: Decide if the session provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.

    Environment variables (read when ``use_env_settings`` is True, the default):

    * ``HTTP_PROXY`` - Proxy URL for HTTP requests.
    * ``HTTPS_PROXY`` - Proxy URL for HTTPS requests.
    * ``NO_PROXY`` - Comma-separated list of hosts that should bypass the proxy.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sync.py
            :start-after: [START requests]
            :end-before: [END requests]
            :language: python
            :dedent: 4
            :caption: Synchronous transport with Requests.
    """

    _protocols = ["http://", "https://"]

    def __init__(self, **kwargs) -> None:
        self.session = kwargs.get("session", None)
        self._session_owner = kwargs.get("session_owner", True)
        if not self._session_owner and not self.session:
            raise ValueError("session_owner cannot be False if no session is provided")
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._use_env_settings = kwargs.pop("use_env_settings", True)
        # See https://github.com/Azure/azure-sdk-for-python/issues/25640 to understand why we track this
        self._has_been_opened = False
        # Tracks the SSLContext currently mounted for https so we only remount on change (e.g. cert rotation).
        self._mounted_ssl_context: Optional[ssl.SSLContext] = None
        self._mounted_ssl_adapter: Optional[_SSLContextAdapter] = None
        self._previous_https_adapter: Optional[BaseAdapter] = None

    def __enter__(self) -> "RequestsTransport":
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def _init_session(self, session: requests.Session) -> None:
        """Init session level configuration of requests.

        This is initialization I want to do once only on a session.

        :param requests.Session session: The session object.
        """
        session.trust_env = self._use_env_settings
        disable_retries = Retry(total=False, redirect=False, raise_on_status=False)
        adapter = BiggerBlockSizeHTTPAdapter(max_retries=disable_retries)
        for p in self._protocols:
            session.mount(p, adapter)

    def _mount_ssl_context(self, ssl_context: ssl.SSLContext) -> None:
        """Mount an https adapter using the given SSLContext, if not already mounted.

        Only remounts when the context changes, so pooled connections are reused between requests
        and dropped exactly once when the client certificate rotates (a new context is supplied).

        :param ssl.SSLContext ssl_context: The SSLContext to use for https connections.
        """
        if ssl_context is self._mounted_ssl_context:
            return
        if self._mounted_ssl_context is None:
            self._previous_https_adapter = self.session.get_adapter("https://")  # type: ignore[union-attr]

        previous_ssl_adapter = self._mounted_ssl_adapter
        disable_retries = Retry(total=False, redirect=False, raise_on_status=False)
        adapter = _SSLContextAdapter(max_retries=disable_retries, ssl_context=ssl_context)
        self.session.mount("https://", adapter)  # type: ignore[union-attr]
        self._mounted_ssl_context = ssl_context
        self._mounted_ssl_adapter = adapter
        if previous_ssl_adapter:
            previous_ssl_adapter.close()

    def _unmount_ssl_context(self) -> None:
        """Restore the previous https adapter after an SSLContext-backed request."""
        if self._mounted_ssl_context is None:
            return
        if self._previous_https_adapter is not None:
            self.session.mount("https://", self._previous_https_adapter)  # type: ignore[union-attr]
        if self._mounted_ssl_adapter:
            self._mounted_ssl_adapter.close()
        self._mounted_ssl_context = None
        self._mounted_ssl_adapter = None
        self._previous_https_adapter = None

    def _resolve_connection_cert(self, cert: Any) -> Any:
        """Resolve ``connection_cert`` for a request, applying an in-memory SSLContext if given.

        An ``ssl.SSLContext`` is applied via a dedicated https adapter (requests' ``cert=`` only accepts
        file paths) and ``None`` is returned so the context is not forwarded as ``cert=``. For any other
        value the previously mounted SSLContext adapter (if any) is unmounted so a bound certificate does
        not leak onto this request.

        :param cert: The ``connection_cert`` value (file path, (cert, key) tuple, ssl.SSLContext, or None).
        :return: The value to pass to requests as ``cert=``.
        :rtype: any
        """
        if isinstance(cert, ssl.SSLContext):
            self._mount_ssl_context(cert)
            return None
        self._unmount_ssl_context()
        return cert

    def open(self):
        """Opens the connection."""
        if self._has_been_opened and not self.session:
            raise ValueError(
                "HTTP transport has already been closed. "
                "You may check if you're calling a function outside of the `with` of your client creation, "
                "or if you called `close()` on your client already."
            )
        if not self.session:
            if self._session_owner:
                self.session = requests.Session()
                self._init_session(self.session)
            else:
                raise ValueError("session_owner cannot be False and no session is available")
        self._has_been_opened = True

    def close(self):
        """Closes the connection."""
        if self.session:
            self._unmount_ssl_context()
        if self._session_owner and self.session:
            self.session.close()
            self.session = None

    @overload
    def send(
        self, request: HttpRequest, *, proxies: Optional[MutableMapping[str, str]] = None, **kwargs
    ) -> HttpResponse:
        """Send a rest request and get back a rest response.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse

        :keyword MutableMapping proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """

    @overload
    def send(
        self, request: "RestHttpRequest", *, proxies: Optional[MutableMapping[str, str]] = None, **kwargs
    ) -> "RestHttpResponse":
        """Send an `azure.core.rest` request and get back a rest response.

        :param request: The request object to be sent.
        :type request: ~azure.core.rest.HttpRequest
        :return: An HTTPResponse object.
        :rtype: ~azure.core.rest.HttpResponse

        :keyword MutableMapping proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """

    def send(  # pylint: disable=too-many-statements
        self,
        request: Union[HttpRequest, "RestHttpRequest"],
        *,
        proxies: Optional[MutableMapping[str, str]] = None,
        **kwargs
    ) -> Union[HttpResponse, "RestHttpResponse"]:
        """Send request object according to configuration.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: ~azure.core.pipeline.transport.HttpResponse

        :keyword MutableMapping proxies: will define the proxy to use. Proxy is a dict (protocol, url)
        """
        self.open()
        response = None
        error: Optional[AzureErrorUnion] = None

        try:
            connection_timeout = kwargs.pop("connection_timeout", self.connection_config.timeout)

            if isinstance(connection_timeout, tuple):
                if "read_timeout" in kwargs:
                    raise ValueError("Cannot set tuple connection_timeout and read_timeout together")
                _LOGGER.warning("Tuple timeout setting is deprecated")
                timeout = connection_timeout
            else:
                read_timeout = kwargs.pop("read_timeout", self.connection_config.read_timeout)
                timeout = (connection_timeout, read_timeout)
            cert = self._resolve_connection_cert(kwargs.pop("connection_cert", self.connection_config.cert))
            response = self.session.request(  # type: ignore
                request.method,
                request.url,
                headers=request.headers,
                data=request.data,
                files=request.files,
                verify=kwargs.pop("connection_verify", self.connection_config.verify),
                timeout=timeout,
                cert=cert,
                allow_redirects=False,
                proxies=proxies,
                **kwargs
            )
            response.raw.enforce_content_length = True

        except AttributeError as err:
            if self.session is None:
                raise ValueError(
                    "No session available for request. "
                    "Please report this issue to https://github.com/Azure/azure-sdk-for-python/issues."
                ) from err
            raise
        except NewConnectionError as err:
            error = ServiceRequestError(err, error=err)
        except ConnectTimeoutError as err:
            error = ServiceRequestTimeoutError(err, error=err)
        except requests.exceptions.ConnectTimeout as err:
            error = ServiceRequestTimeoutError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseTimeoutError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.exceptions.ChunkedEncodingError as err:
            msg = err.__str__()
            if "IncompleteRead" in msg:
                _LOGGER.warning("Incomplete download.")
                error = IncompleteReadError(err, error=err)
            else:
                _LOGGER.warning("Unable to stream download.")
                error = HttpResponseError(err, error=err)
        except requests.RequestException as err:
            error = ServiceResponseError(err, error=err)

        if error:
            raise error
        if _is_rest(request):
            from azure.core.rest._requests_basic import RestRequestsTransportResponse

            retval: RestHttpResponse = RestRequestsTransportResponse(
                request=request,
                internal_response=response,
                block_size=self.connection_config.data_block_size,
            )
            if not kwargs.get("stream"):
                _handle_non_stream_rest_response(retval)
            return retval
        return RequestsTransportResponse(request, response, self.connection_config.data_block_size)
