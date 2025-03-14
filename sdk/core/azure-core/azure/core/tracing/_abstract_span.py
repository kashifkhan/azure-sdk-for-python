# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Protocol that defines what functions wrappers of tracing libraries should implement."""
from __future__ import annotations
from urllib.parse import urlparse

from typing import (
    Any,
    Optional,
    Union,
    Callable,
    Dict,
    Type,
    Generic,
    TypeVar,
)
from types import TracebackType
from typing_extensions import Protocol, ContextManager, runtime_checkable
from azure.core.pipeline.transport import HttpRequest, HttpResponse, AsyncHttpResponse
from azure.core.rest import (
    HttpResponse as RestHttpResponse,
    AsyncHttpResponse as AsyncRestHttpResponse,
    HttpRequest as RestHttpRequest,
)
from ._models import AttributeValue, SpanKind


HttpResponseType = Union[HttpResponse, AsyncHttpResponse, RestHttpResponse, AsyncRestHttpResponse]
HttpRequestType = Union[HttpRequest, RestHttpRequest]

Attributes = Dict[str, AttributeValue]
SpanType = TypeVar("SpanType")


@runtime_checkable
class AbstractSpan(Protocol, Generic[SpanType]):
    """Wraps a span from a distributed tracing implementation.

    If a span is given wraps the span. Else a new span is created.
    The optional argument name is given to the new span.

    :param span: The span to wrap
    :type span: Any
    :param name: The name of the span
    :type name: str
    """

    def __init__(self, span: Optional[SpanType] = None, name: Optional[str] = None, **kwargs: Any) -> None:
        pass

    def span(self, name: str = "child_span", **kwargs: Any) -> AbstractSpan[SpanType]:
        """
        Create a child span for the current span and append it to the child spans list.
        The child span must be wrapped by an implementation of AbstractSpan

        :param name: The name of the child span
        :type name: str
        :return: The child span
        :rtype: AbstractSpan
        """
        ...

    @property
    def kind(self) -> Optional[SpanKind]:
        """Get the span kind of this span.

        :rtype: SpanKind
        :return: The span kind of this span
        """
        ...

    @kind.setter
    def kind(self, value: SpanKind) -> None:
        """Set the span kind of this span.

        :param value: The span kind of this span
        :type value: SpanKind
        """
        ...

    def __enter__(self) -> AbstractSpan[SpanType]:
        """Start a span."""
        ...

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: TracebackType,
    ) -> None:
        """Finish a span.

        :param exception_type: The type of the exception
        :type exception_type: type
        :param exception_value: The value of the exception
        :type exception_value: Exception
        :param traceback: The traceback of the exception
        :type traceback: Traceback
        """
        ...

    def start(self) -> None:
        """Set the start time for a span."""
        ...

    def finish(self) -> None:
        """Set the end time for a span."""
        ...

    def to_header(self) -> Dict[str, str]:
        """Returns a dictionary with the header labels and values.

        :return: A dictionary with the header labels and values
        :rtype: dict
        """
        ...

    def add_attribute(self, key: str, value: Union[str, int]) -> None:
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: Union[str, int]
        """
        ...

    def set_http_attributes(self, request: HttpRequestType, response: Optional[HttpResponseType] = None) -> None:
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: azure.core.rest.HttpRequest
        :param response: The response received by the server. Is None if no response received.
        :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
        """
        ...

    def get_trace_parent(self) -> str:
        """Return traceparent string.

        :return: a traceparent string
        :rtype: str
        """
        ...

    @property
    def span_instance(self) -> SpanType:
        """
        Returns the span the class is wrapping.
        """
        ...

    @classmethod
    def link(cls, traceparent: str, attributes: Optional[Attributes] = None) -> None:
        """
        Given a traceparent, extracts the context and links the context to the current tracer.

        :param traceparent: A string representing a traceparent
        :type traceparent: str
        :param attributes: Any additional attributes that should be added to link
        :type attributes: dict
        """
        ...

    @classmethod
    def link_from_headers(cls, headers: Dict[str, str], attributes: Optional[Attributes] = None) -> None:
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A dictionary of the request header as key value pairs.
        :type headers: dict
        :param attributes: Any additional attributes that should be added to link
        :type attributes: dict
        """
        ...

    @classmethod
    def get_current_span(cls) -> SpanType:
        """
        Get the current span from the execution context. Return None otherwise.

        :return: The current span
        :rtype: AbstractSpan
        """
        ...

    @classmethod
    def get_current_tracer(cls) -> Any:
        """
        Get the current tracer from the execution context. Return None otherwise.

        :return: The current tracer
        :rtype: Any
        """
        ...

    @classmethod
    def set_current_span(cls, span: SpanType) -> None:
        """Set the given span as the current span in the execution context.

        :param span: The span to set as the current span
        :type span: Any
        """
        ...

    @classmethod
    def set_current_tracer(cls, tracer: Any) -> None:
        """Set the given tracer as the current tracer in the execution context.

        :param tracer: The tracer to set as the current tracer
        :type tracer: Any
        """
        ...

    @classmethod
    def change_context(cls, span: SpanType) -> ContextManager[SpanType]:
        """Change the context for the life of this context manager.

        :param span: The span to run in the new context
        :type span: Any
        :rtype: contextmanager
        :return: A context manager that will run the given span in the new context
        """
        ...

    @classmethod
    def with_current_context(cls, func: Callable) -> Callable:
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :type func: callable
        :return: The target the pass in instead of the function
        :rtype: callable
        """
        ...


class HttpSpanMixin:
    """Can be used to get HTTP span attributes settings for free."""

    _SPAN_COMPONENT = "component"
    _HTTP_USER_AGENT = "http.user_agent"
    _HTTP_METHOD = "http.method"
    _HTTP_URL = "http.url"
    _HTTP_STATUS_CODE = "http.status_code"
    _NET_PEER_NAME = "net.peer.name"
    _NET_PEER_PORT = "net.peer.port"
    _ERROR_TYPE = "error.type"

    def set_http_attributes(
        self: AbstractSpan,
        request: HttpRequestType,
        response: Optional[HttpResponseType] = None,
    ) -> None:
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: azure.core.rest.HttpRequest
        :param response: The response received from the server. Is None if no response received.
        :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
        """
        # Also see https://github.com/python/mypy/issues/5837
        self.kind = SpanKind.CLIENT
        self.add_attribute(HttpSpanMixin._SPAN_COMPONENT, "http")
        self.add_attribute(HttpSpanMixin._HTTP_METHOD, request.method)
        self.add_attribute(HttpSpanMixin._HTTP_URL, request.url)

        parsed_url = urlparse(request.url)
        if parsed_url.hostname:
            self.add_attribute(HttpSpanMixin._NET_PEER_NAME, parsed_url.hostname)
        if parsed_url.port and parsed_url.port not in [80, 443]:
            self.add_attribute(HttpSpanMixin._NET_PEER_PORT, parsed_url.port)

        user_agent = request.headers.get("User-Agent")
        if user_agent:
            self.add_attribute(HttpSpanMixin._HTTP_USER_AGENT, user_agent)
        if response and response.status_code:
            self.add_attribute(HttpSpanMixin._HTTP_STATUS_CODE, response.status_code)
            if response.status_code >= 400:
                self.add_attribute(HttpSpanMixin._ERROR_TYPE, str(response.status_code))
        else:
            self.add_attribute(HttpSpanMixin._HTTP_STATUS_CODE, 504)
            self.add_attribute(HttpSpanMixin._ERROR_TYPE, "504")
