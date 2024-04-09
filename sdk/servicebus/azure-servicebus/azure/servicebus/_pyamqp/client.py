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

    def __init__(self, hostname, **kwargs):
        # I think these are just strings not instances of target or source
        
        self._name = kwargs.pop("client_name", str(uuid.uuid4()))
        self._cbs_authenticator = None
        self._mgmt_links = {}
        self._mgmt_link_lock = threading.Lock()
        self._retry_policy = kwargs.pop("retry_policy", RetryPolicy())
        

    def auth_complete(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :return: Whether the authentication handshake is complete.
        :rtype: bool
        """
        if self._cbs_authenticator and not self._cbs_authenticator.handle_token():
            self._connection.listen(wait=self._socket_timeout)
            return False
        return True

    def client_ready(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :return: Whether the handler is ready to process messages.
        :rtype: bool
        """
        if not self.auth_complete():
            return False
        if not self._client_ready():
            try:
                self._connection.listen(wait=self._socket_timeout)
            except ValueError:
                return True
            return False
        return True

    def do_work(self, **kwargs):
        """Run a single connection iteration.
        This will return `True` if the connection is still open
        and ready to be used for further work, or `False` if it needs
        to be shut down.

        :return: Whether the connection is still open and ready to be used.
        :rtype: bool
        :raises: TimeoutError if CBS authentication timeout reached.
        """
        if self._shutdown:
            return False
        if not self.client_ready():
            return True
        return self._client_run(**kwargs)

    def mgmt_request(self, message, **kwargs):
        """
        :param message: The message to send in the management request.
        :type message: ~pyamqp.message.Message
        :keyword str operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :keyword str operation_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :keyword str node: The target node. Default node is `$management`.
        :keyword float timeout: Provide an optional timeout in seconds within which a response
         to the management request must be received.
        :returns: The response to the management request.
        :rtype: ~pyamqp.message.Message
        """

        # The method also takes "status_code_field" and "status_description_field"
        # keyword arguments as alternate names for the status code and description
        # in the response body. Those two keyword arguments are used in Azure services only.
        operation = kwargs.pop("operation", None)
        operation_type = kwargs.pop("operation_type", None)
        node = kwargs.pop("node", "$management")
        timeout = kwargs.pop("timeout", 0)
        with self._mgmt_link_lock:
            try:
                mgmt_link = self._mgmt_links[node]
            except KeyError:
                mgmt_link = ManagementOperation(self._session, endpoint=node, **kwargs)
                self._mgmt_links[node] = mgmt_link
                mgmt_link.open()

        while not mgmt_link.ready():
            self._connection.listen(wait=False)
        operation_type = operation_type or b"empty"
        status, description, response = mgmt_link.execute(
            message, operation=operation, operation_type=operation_type, timeout=timeout
        )
        return status, description, response


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

    def _client_ready(self):
        """Determine whether the client is ready to start receiving messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageReceiver must be open and in non-errored
        states.


        :return: Whether the client is ready to start receiving messages.
        :rtype: bool
        """
        # pylint: disable=protected-access
        if not self._link:
            self._link = self._session.create_sender_link(
                target_address=self.target,
                link_credit=self._link_credit,
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                properties=self._link_properties,
            )
            self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    def _client_run(self, **kwargs):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :return: Whether the client can remain open for further work.
        :rtype: bool
        """
        self._link.update_pending_deliveries()
        self._connection.listen(wait=self._socket_timeout, **kwargs)
        return True

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

    def __init__(self, hostname, source, **kwargs):
        self.source = source
        self._streaming_receive = kwargs.pop("streaming_receive", False)
        self._received_messages = queue.Queue()
        self._message_received_callback = kwargs.pop("message_received_callback", None)

        # Sender and Link settings
        self._max_message_size = kwargs.pop("max_message_size", MAX_FRAME_SIZE_BYTES)
        self._link_properties = kwargs.pop("link_properties", None)
        self._link_credit = kwargs.pop("link_credit", 300)

        # Iterator
        self._timeout = kwargs.pop("timeout", 0)
        self._timeout_reached = False
        self._last_activity_timestamp = time.time()

        super(ReceiveClient, self).__init__(hostname, **kwargs)

    def _client_ready(self):
        """Determine whether the client is ready to start receiving messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageReceiver must be open and in non-errored
        states.

        :return: True if the client is ready to start receiving messages.
        :rtype: bool
        """
        # pylint: disable=protected-access
        if not self._link:
            self._link = self._session.create_receiver_link(
                source_address=self.source,
                link_credit=0,  # link_credit=0 on flow frame sent before client is ready
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                on_transfer=self._message_received,
                properties=self._link_properties,
                desired_capabilities=self._desired_capabilities,
                on_attach=self._on_attach,
            )
            self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    def _client_run(self, **kwargs):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :return: Whether the client can remain open for further work.
        :rtype: bool
        """
        try:
            if self._link.current_link_credit <= 0:
                self._link.flow(link_credit=self._link_credit)
            self._connection.listen(wait=self._socket_timeout, **kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing receiver.", extra=self._network_trace_params)
            self._shutdown = True
            return False
        return True