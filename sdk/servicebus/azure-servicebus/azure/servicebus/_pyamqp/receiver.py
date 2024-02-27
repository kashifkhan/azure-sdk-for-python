# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import queue
import time
import uuid
import logging
from typing import Any, Dict, Literal, Optional, Tuple, Union, cast, overload

from ._decode import decode_payload
from .link import Link
from .constants import LinkState, ReceiverSettleMode, Role, SenderSettleMode
from .performatives import TransferFrame, DispositionFrame
from .outcomes import Received, Accepted, Rejected, Released, Modified
from .error import AMQPError, AMQPException, ErrorCondition


_LOGGER = logging.getLogger(__name__)


class ReceiverLink(Link):
    def __init__(self, session, handle, source_address, *, send_settle_mode = SenderSettleMode.Unsettled, receive_settle_mode = ReceiverSettleMode.Second, **kwargs):
        name = kwargs.pop("name", None) or str(uuid.uuid4())
        role = Role.Receiver
        self._streaming_receive = kwargs.pop("streaming_receive", False)
        self._received_messages = queue.Queue()
        self._message_received_callback = kwargs.pop("message_received_callback", None)
        self._retry_policy = kwargs.pop("retry_policy", RetryPolicy())

        # Iterator
        self._timeout = kwargs.pop("timeout", 0)
        self._timeout_reached = False
        self._last_activity_timestamp = time.time()
        
        if "target_address" not in kwargs:
            kwargs["target_address"] = "receiver-link-{}".format(name)
        super(ReceiverLink, self).__init__(
            session, 
            handle, 
            name, 
            role, 
            source_address=source_address,
            send_settle_mode=send_settle_mode,
            receive_settle_mode=receive_settle_mode,
            **kwargs
            )
        self._on_transfer = kwargs.pop("on_transfer")
        self._received_payload = bytearray()
        self._first_frame = None

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # TODO: Assuming we establish all links for now...
        # check link_create_from_endpoint in C lib
        raise NotImplementedError("Pending")

    def _process_incoming_message(self, frame, message):
        try:
            return self._on_transfer(frame, message)
        except Exception as e:  # pylint: disable=broad-except
            _LOGGER.error("Transfer callback function failed with error: %r", e, extra=self.network_trace_params)
        return None

    def _incoming_attach(self, frame):
        super(ReceiverLink, self)._incoming_attach(frame)
        if frame[9] is None:  # initial_delivery_count
            _LOGGER.info("Cannot get initial-delivery-count. Detaching link", extra=self.network_trace_params)
            self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
        self.delivery_count = frame[9]
        self.current_link_credit = self.link_credit
        self._outgoing_flow()

    def _incoming_transfer(self, frame):
        if self.network_trace:
            _LOGGER.debug("<- %r", TransferFrame(payload=b"***", *frame[:-1]), extra=self.network_trace_params)
        # If more is false --> this is the last frame of the message
        if not frame[5]:
            self.current_link_credit -= 1
        self.delivery_count += 1
        self.received_delivery_id = frame[1]  # delivery_id
        if self.received_delivery_id is not None:
            self._first_frame = frame
        if not self.received_delivery_id and not self._received_payload:
            pass  # TODO: delivery error
        if self._received_payload or frame[5]:  # more
            self._received_payload.extend(frame[11])
        if not frame[5]:
            if self._received_payload:
                message = decode_payload(memoryview(self._received_payload))
                self._received_payload = bytearray()
            else:
                message = decode_payload(frame[11])
            delivery_state = self._process_incoming_message(self._first_frame, message)
            if not frame[4] and delivery_state:  # settled
                self._outgoing_disposition(
                    first=self._first_frame[1],
                    last=self._first_frame[1],
                    settled=True,
                    state=delivery_state,
                    batchable=None
                )

    def _wait_for_response(self, wait: Union[bool, float]) -> None:
        if wait is True:
            self._session._connection.listen(wait=False) # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error
        elif wait:
            self._session._connection.listen(wait=wait) # pylint: disable=protected-access
            if self.state == LinkState.ERROR:
                if self._error:
                    raise self._error

    def _outgoing_disposition(
        self,
        first: int,
        last: Optional[int],
        settled: Optional[bool],
        state: Optional[Union[Received, Accepted, Rejected, Released, Modified]],
        batchable: Optional[bool],
    ):
        disposition_frame = DispositionFrame(
            role=self.role, first=first, last=last, settled=settled, state=state, batchable=batchable
        )
        if self.network_trace:
            _LOGGER.debug("-> %r", DispositionFrame(*disposition_frame), extra=self.network_trace_params)
        self._session._outgoing_disposition(disposition_frame) # pylint: disable=protected-access
        

    def attach(self):
        super().attach()
        self._received_payload = bytearray()
    
    def detach(self, close: bool = False, error: Optional[AMQPError] = None) -> None:
        self._received_queue: queue.Queue = queue.Queue()
        super().detach(close=close)

    def send_disposition(
        self,
        *,
        wait: Union[bool, float] = False,
        first_delivery_id: int,
        last_delivery_id: Optional[int] = None,
        settled: Optional[bool] = None,
        delivery_state: Optional[Union[Received, Accepted, Rejected, Released, Modified]] = None,
        batchable: Optional[bool] = None
    ):
        if self._is_closed:
            raise ValueError("Link already closed.")
        self._outgoing_disposition(first_delivery_id, last_delivery_id, settled, delivery_state, batchable)
        if not settled:
            self._wait_for_response(wait)
    
    def receive_message_batch(self, *, max_batch_size, on_message_received, timeout: Optional[float] = None,  **kwargs):
        """Receive a batch of messages. Messages returned in the batch have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback. This method will return as soon as some messages are
        available rather than waiting to achieve a specific batch size, and therefore the
        number of messages returned per call will vary up to the maximum allowed.

        :keyword max_batch_size: The maximum number of messages that can be returned in
         one call. This value cannot be larger than the prefetch value, and if not specified,
         the prefetch value will be used.
        :paramtype max_batch_size: int
        :keyword on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~pyamqp.message.Message object.
        :paramtype on_message_received: callable[~pyamqp.message.Message]
        :keyword timeout: The timeout in milliseconds for which to wait to receive any messages.
         If no messages are received in this time, an empty list will be returned. If set to
         0, the client will continue to wait until at least one message is received. The
         default is 0.
        :paramtype timeout: float
        :return: A list of messages.
        :rtype: list[~pyamqp.message.Message]
        """
        retry_settings = self._retry_policy.configure_retries()
        retry_active = True
        absolute_timeout = timeout or 0
        start_time = time.time()
        while retry_active:
            try:
                if absolute_timeout < 0:
                    raise TimeoutError("Operation timed out.")
                return self._receive_message_batch_impl(max_batch_size, on_message_received, timeout=absolute_timeout, **kwargs)
            except AMQPException as exc:
                if not self._retry_policy.is_retryable(exc):
                    raise
                if absolute_timeout >= 0:
                    retry_active = self._retry_policy.increment(retry_settings, exc)
                    if not retry_active:
                        break
                    time.sleep(self._retry_policy.get_backoff_time(retry_settings, exc))
                    if exc.condition == ErrorCondition.LinkDetachForced:
                        self.detach(close=True)  # if link level error, close and open a new link
                    if exc.condition in (
                        ErrorCondition.ConnectionCloseForced,
                        ErrorCondition.SocketError,
                    ):
                        # if connection detach or socket error, close and open a new connection
                        self.detach(close=True)
            finally:
                end_time = time.time()
                if absolute_timeout > 0:
                    absolute_timeout -= end_time - start_time
        raise retry_settings["history"][-1]

    def receive_messages_iter(self, timeout=None, on_message_received=None):
        """Receive messages by generator. Messages returned in the generator have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback.

        :param int or None timeout: The timeout in milliseconds for which to wait to receive any messages.
        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~pyamqp.message.Message object.
        :type on_message_received: callable[~pyamqp.message.Message]
        :return: A generator of messages.
        :rtype: generator[~pyamqp.message.Message]
        """
        self._message_received_callback = on_message_received
        return self._message_generator(timeout=timeout)

    def _message_generator(self, timeout=None):
        """Iterate over processed messages in the receive queue.

        :param int or None timeout: The timeout in milliseconds for which to wait to receive any messages.
        :return: A generator of messages.
        :rtype: generator[~pyamqp.message.Message]
        """
        self.open()
        self._timeout_reached = False
        receiving = True
        message = None
        self._last_activity_timestamp = time.time()
        self._timeout = timeout if timeout else self._timeout
        try:
            while receiving and not self._timeout_reached:
                if self._timeout > 0:
                    if time.time() - self._last_activity_timestamp >= self._timeout:
                        self._timeout_reached = True

                if not self._timeout_reached:
                    receiving = self.do_work()

                while not self._received_messages.empty():
                    message = self._received_messages.get()
                    self._last_activity_timestamp = time.time()
                    self._received_messages.task_done()
                    yield message

        finally:
            if self._shutdown:
                self.close()

    @overload
    def settle_messages(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["accepted"],
        *,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    def settle_messages(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["released"],
        *,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    def settle_messages(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["rejected"],
        *,
        error: Optional[AMQPError] = None,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    def settle_messages(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["modified"],
        *,
        delivery_failed: Optional[bool] = None,
        undeliverable_here: Optional[bool] = None,
        message_annotations: Optional[Dict[Union[str, bytes], Any]] = None,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    def settle_messages(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["received"],
        *,
        section_number: int,
        section_offset: int,
        batchable: Optional[bool] = None
    ):
        ...

    def settle_messages(
        self, delivery_id: Union[int, Tuple[int, int]], outcome: str, **kwargs
    ):
        batchable = kwargs.pop("batchable", None)
        if outcome.lower() == "accepted":
            state: Outcomes = Accepted()
        elif outcome.lower() == "released":
            state = Released()
        elif outcome.lower() == "rejected":
            state = Rejected(**kwargs)
        elif outcome.lower() == "modified":
            state = Modified(**kwargs)
        elif outcome.lower() == "received":
            state = Received(**kwargs)
        else:
            raise ValueError("Unrecognized message output: {}".format(outcome))
        try:
            first, last = cast(Tuple, delivery_id)
        except TypeError:
            first = delivery_id
            last = None
        self._link.send_disposition(
            first_delivery_id=first,
            last_delivery_id=last,
            settled=True,
            delivery_state=state,
            batchable=batchable,
            wait=True,
        )
    
    def _message_received(self, frame, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param message: Received message.
        :type message: ~pyamqp.message.Message
        :param frame: Received frame.
        :type frame: tuple
        """
        self._last_activity_timestamp = time.time()
        if self._message_received_callback:
            self._message_received_callback(message)
        if not self._streaming_receive:
            self._received_messages.put((frame, message))

    def _receive_message_batch_impl(
        self, max_batch_size=None, on_message_received=None, timeout=0
    ):
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._link_credit
        timeout = time.time() + timeout if timeout else 0
        receiving = True
        batch = []
        self.open()
        while len(batch) < max_batch_size:
            try:
                # TODO: This drops the transfer frame data
                _, message = self._received_messages.get_nowait()
                batch.append(message)
                self._received_messages.task_done()
            except queue.Empty:
                break
        else:
            return batch

        to_receive_size = max_batch_size - len(batch)
        before_queue_size = self._received_messages.qsize()

        while receiving and to_receive_size > 0:
            if timeout and time.time() > timeout:
                break

            receiving = self.do_work(batch=to_receive_size)
            cur_queue_size = self._received_messages.qsize()
            # after do_work, check how many new messages have been received since previous iteration
            received = cur_queue_size - before_queue_size
            if to_receive_size < max_batch_size and received == 0:
                # there are already messages in the batch, and no message is received in the current cycle
                # return what we have
                break

            to_receive_size -= received
            before_queue_size = cur_queue_size

        while len(batch) < max_batch_size:
            try:
                _, message = self._received_messages.get_nowait()
                batch.append(message)
                self._received_messages.task_done()
            except queue.Empty:
                break
        return batch

