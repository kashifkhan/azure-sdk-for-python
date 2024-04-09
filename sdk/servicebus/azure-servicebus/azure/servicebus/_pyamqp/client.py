# -------------------------------------------------------------------------  # pylint: disable=client-suffix-needed
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=client-accepts-api-version-keyword
# pylint: disable=missing-client-constructor-parameter-credential
# pylint: disable=client-method-missing-type-annotations
# pylint: disable=too-many-lines
# TODO: Check types of kwargs (issue exists for this)
import logging
import threading
import queue
import time
import uuid
from functools import partial
from typing import Any, Dict, Optional, Tuple, Union, overload, cast
import certifi
from typing_extensions import Literal

from ._connection import Connection
from .message import _MessageDelivery
from .error import (
    AMQPException,
    ErrorCondition,
    MessageException,
    MessageSendFailed,
    RetryPolicy,
    AMQPError,
)
from .outcomes import Received, Rejected, Released, Accepted, Modified

from .constants import (
    MAX_CHANNELS,
    MessageDeliveryState,
    SenderSettleMode,
    ReceiverSettleMode,
    LinkDeliverySettleReason,
    TransportType,
    SEND_DISPOSITION_ACCEPT,
    SEND_DISPOSITION_REJECT,
    AUTH_TYPE_CBS,
    MAX_FRAME_SIZE_BYTES,
    INCOMING_WINDOW,
    OUTGOING_WINDOW,
    DEFAULT_AUTH_TIMEOUT,
    MESSAGE_DELIVERY_DONE_STATES,
)

from .management_operation import ManagementOperation
from .cbs import CBSAuthenticator

Outcomes = Union[Received, Rejected, Released, Accepted, Modified]


_logger = logging.getLogger(__name__)


class AMQPClient(
    object
):  # pylint: disable=too-many-instance-attributes
    """An AMQP client.
    :param hostname: The AMQP endpoint to connect to.
    :type hostname: str
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Portion of the idle timeout time to wait before sending an
     empty frame. The default portion is 50% of the idle timeout value (i.e. `0.5`).
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    :keyword float socket_timeout: The maximum time in seconds that the underlying socket in the transport should
     wait when reading or writing data before timing out. The default value is 0.2 (for transport type Amqp),
     and 1 for transport type AmqpOverWebsocket.
    """

    

class SendClient(AMQPClient):
    """
    An AMQP client for sending messages.
    :param target: The target AMQP service endpoint. This can either be the URI as
     a string or a ~pyamqp.endpoint.Target object.
    :type target: str, bytes or ~pyamqp.endpoint.Target
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Portion of the idle timeout time to wait before sending an
     empty frame. The default portion is 50% of the idle timeout value (i.e. `0.5`).
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    """
    pass

    

class ReceiveClient(AMQPClient): # pylint:disable=too-many-instance-attributes
    """
    An AMQP client for receiving messages.
    :param source: The source AMQP service endpoint. This can either be the URI as
     a string or a ~pyamqp.endpoint.Source object.
    :type source: str, bytes or ~pyamqp.endpoint.Source
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Portion of the idle timeout time to wait before sending an
     empty frame. The default portion is 50% of the idle timeout value (i.e. `0.5`).
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    """
