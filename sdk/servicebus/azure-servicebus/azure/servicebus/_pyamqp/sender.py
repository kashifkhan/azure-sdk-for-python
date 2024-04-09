# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import partial
import struct
import uuid
import logging
import time

from ._encode import encode_payload
from .link import Link
from .constants import MESSAGE_DELIVERY_DONE_STATES, SEND_DISPOSITION_ACCEPT, SEND_DISPOSITION_REJECT, MessageDeliveryState, ReceiverSettleMode, SessionTransferState, LinkDeliverySettleReason, LinkState, Role, SenderSettleMode, SessionState
from .error import AMQPException, AMQPLinkError, ErrorCondition, MessageException, MessageSendFailed, RetryPolicy
from .message import _MessageDelivery, Message

_LOGGER = logging.getLogger(__name__)


class PendingDelivery(object):
    def __init__(self, **kwargs):
        self.message = kwargs.get("message")
        self.sent = False
        self.frame = None
        self.on_delivery_settled = kwargs.get("on_delivery_settled")
        self.start = time.time()
        self.transfer_state = None
        self.timeout = kwargs.get("timeout")
        self.settled = kwargs.get("settled", False)
        self._network_trace_params = kwargs.get('network_trace_params')

    def on_settled(self, reason, state):
        if self.on_delivery_settled and not self.settled:
            try:
                self.on_delivery_settled(reason, state)
            except Exception as e:  # pylint:disable=broad-except
                _LOGGER.warning(
                    "Message 'on_send_complete' callback failed: %r",
                    e,
                    extra=self._network_trace_params
                )
        self.settled = True


class SenderLink(Link):
    def __init__(self, session, handle, target_address, *, send_settle_mode = SenderSettleMode.Unsettled, receive_settle_mode = ReceiverSettleMode.Second, **kwargs):
        name = kwargs.pop("name", None) or str(uuid.uuid4())
        role = Role.Sender
        self._retry_policy = kwargs.pop("retry_policy", RetryPolicy())
        if "source_address" not in kwargs:
            kwargs["source_address"] = "sender-link-{}".format(name)
        super(SenderLink, self).__init__(
            session, 
            handle, 
            name, 
            role, 
            target_address=target_address, 
            send_settle_mode = send_settle_mode, 
            receive_settle_mode = receive_settle_mode, 
            **kwargs
        )
        self._pending_deliveries = []

    @classmethod
    def from_incoming_frame(cls, session, handle, frame):
        # TODO: Assuming we establish all links for now...
        # check link_create_from_endpoint in C lib
        raise NotImplementedError("Pending")

    # In theory we should not need to purge pending deliveries on attach/dettach - as a link should
    # be resume-able, however this is not yet supported.
    def _incoming_attach(self, frame):
        try:
            super(SenderLink, self)._incoming_attach(frame)
        except AMQPLinkError:
            self._remove_pending_deliveries()
            raise
        self.current_link_credit = self.link_credit
        self._outgoing_flow()
        self.update_pending_deliveries()

    def _incoming_detach(self, frame):
        super(SenderLink, self)._incoming_detach(frame)
        self._remove_pending_deliveries()

    def _incoming_flow(self, frame):
        rcv_link_credit = frame[6]  # link_credit
        rcv_delivery_count = frame[5]  # delivery_count
        if frame[4] is not None:  # handle
            if rcv_link_credit is None or rcv_delivery_count is None:
                _LOGGER.info(
                    "Unable to get link-credit or delivery-count from incoming ATTACH. Detaching link.",
                    extra=self.network_trace_params
                )
                self._remove_pending_deliveries()
                self._set_state(LinkState.DETACHED)  # TODO: Send detach now?
            else:
                self.current_link_credit = rcv_delivery_count + rcv_link_credit - self.delivery_count
        self.update_pending_deliveries()

    def _outgoing_transfer(self, delivery):
        output = bytearray()
        encode_payload(output, delivery.message)
        delivery_count = self.delivery_count + 1
        delivery.frame = {
            "handle": self.handle,
            "delivery_tag": struct.pack(">I", abs(delivery_count)),
            "message_format": delivery.message._code,  # pylint:disable=protected-access
            "settled": delivery.settled,
            "more": False,
            "rcv_settle_mode": None,
            "state": None,
            "resume": None,
            "aborted": None,
            "batchable": None,
            "payload": output,
        }
        self._session._outgoing_transfer(  # pylint:disable=protected-access
            delivery,
            self.network_trace_params if self.network_trace else None
        )
        sent_and_settled = False
        if delivery.transfer_state == SessionTransferState.OKAY:
            self.delivery_count = delivery_count
            self.current_link_credit -= 1
            delivery.sent = True
            if delivery.settled:
                delivery.on_settled(LinkDeliverySettleReason.SETTLED, None)
                sent_and_settled = True
        # elif delivery.transfer_state == SessionTransferState.ERROR:
        # TODO: Session wasn't mapped yet - re-adding to the outgoing delivery queue?
        return sent_and_settled

    def _incoming_disposition(self, frame):
        if not frame[3]:  # settled
            return
        range_end = (frame[2] or frame[1]) + 1  # first or last
        settled_ids = list(range(frame[1], range_end))
        unsettled = []
        for delivery in self._pending_deliveries:
            if delivery.sent and delivery.frame["delivery_id"] in settled_ids:
                delivery.on_settled(LinkDeliverySettleReason.DISPOSITION_RECEIVED, frame[4])  # state
                continue
            unsettled.append(delivery)
        self._pending_deliveries = unsettled

    def _remove_pending_deliveries(self):
        for delivery in self._pending_deliveries:
            delivery.on_settled(LinkDeliverySettleReason.NOT_DELIVERED, None)
        self._pending_deliveries = []

    def _on_session_state_change(self):
        if self._session.state == SessionState.DISCARDING:
            self._remove_pending_deliveries()
        super()._on_session_state_change()

    def update_pending_deliveries(self):
        if self.current_link_credit <= 0:
            self.current_link_credit = self.link_credit
            self._outgoing_flow()
        now = time.time()
        pending = []
        for delivery in self._pending_deliveries:
            if delivery.timeout and (now - delivery.start) >= delivery.timeout:
                delivery.on_settled(LinkDeliverySettleReason.TIMEOUT, None)
                continue
            if not delivery.sent:
                sent_and_settled = self._outgoing_transfer(delivery)
                if sent_and_settled:
                    continue
            pending.append(delivery)
        self._pending_deliveries = pending

    def _send_transfer(self, message, *, send_async=False, **kwargs):
        self._check_if_closed()
        if self.state != LinkState.ATTACHED:
            raise AMQPLinkError(
                condition=ErrorCondition.ClientError,
                description="Link is not attached."
            )
        settled = self.send_settle_mode == SenderSettleMode.Settled
        if self.send_settle_mode == SenderSettleMode.Mixed:
            settled = kwargs.pop("settled", True)
        delivery = PendingDelivery(
            on_delivery_settled=kwargs.get("on_send_complete"),
            timeout=kwargs.get("timeout"),
            message=message,
            settled=settled,
            network_trace_params = self.network_trace_params
        )
        if self.current_link_credit == 0 or send_async:
            self._pending_deliveries.append(delivery)
        else:
            sent_and_settled = self._outgoing_transfer(delivery)
            if not sent_and_settled:
                self._pending_deliveries.append(delivery)
        return delivery

    def cancel_transfer(self, delivery):
        try:
            index = self._pending_deliveries.index(delivery)
        except ValueError:
            raise ValueError("Found no matching pending transfer.") from None
        delivery = self._pending_deliveries[index]
        if delivery.sent:
            raise MessageException(
                ErrorCondition.ClientError,
                message="Transfer cannot be cancelled. Message has already been sent and awaiting disposition.",
            )
        delivery.on_settled(LinkDeliverySettleReason.CANCELLED, None)
        self._pending_deliveries.pop(index)

    def _transfer_message(self, message_delivery, timeout=0):
        message_delivery.state = MessageDeliveryState.WaitingForSendAck
        on_send_complete = partial(self._on_send_complete, message_delivery)
        delivery = self._send_transfer(
            message_delivery.message,
            on_send_complete=on_send_complete,
            timeout=timeout,
            send_async=True,
        )
        return delivery
    
    @staticmethod
    def _process_send_error(message_delivery, condition, description=None, info=None):
        try:
            amqp_condition = ErrorCondition(condition)
        except ValueError:
            error = MessageException(condition, description=description, info=info)
        else:
            error = MessageSendFailed(
                amqp_condition, description=description, info=info
            )
        message_delivery.state = MessageDeliveryState.Error
        message_delivery.error = error
    
    def _on_send_complete(self, message_delivery, reason, state):
        message_delivery.reason = reason
        if reason == LinkDeliverySettleReason.DISPOSITION_RECEIVED:
            if state and SEND_DISPOSITION_ACCEPT in state:
                message_delivery.state = MessageDeliveryState.Ok
            else:
                try:
                    error_info = state[SEND_DISPOSITION_REJECT]
                    self._process_send_error(
                        message_delivery,
                        condition=error_info[0][0],
                        description=error_info[0][1],
                        info=error_info[0][2],
                    )
                except TypeError:
                    self._process_send_error(
                        message_delivery, condition=ErrorCondition.UnknownError
                    )
        elif reason == LinkDeliverySettleReason.SETTLED:
            message_delivery.state = MessageDeliveryState.Ok
        elif reason == LinkDeliverySettleReason.TIMEOUT:
            message_delivery.state = MessageDeliveryState.Timeout
            message_delivery.error = TimeoutError("Sending message timed out.")
        else:
            # NotDelivered and other unknown errors
            self._process_send_error(
                message_delivery, condition=ErrorCondition.UnknownError
            )
    
    def _send_message_impl(self, message, **kwargs):
        timeout = kwargs.pop("timeout", 0)
        expire_time = (time.time() + timeout) if timeout else None
        #self.open()
        message_delivery = _MessageDelivery(
            message, MessageDeliveryState.WaitingToBeSent, expire_time
        )
        while not self.client_ready():
            time.sleep(0.05)

        self._transfer_message(message_delivery, timeout)
        running = True
        while running and message_delivery.state not in MESSAGE_DELIVERY_DONE_STATES:
            running = self.do_work()
        if message_delivery.state not in MESSAGE_DELIVERY_DONE_STATES:
            raise MessageException(
                condition=ErrorCondition.ClientError,
                description="Send failed - connection not running."
            )

        if message_delivery.state in (
            MessageDeliveryState.Error,
            MessageDeliveryState.Cancelled,
            MessageDeliveryState.Timeout,
        ):
            try:
                raise message_delivery.error  # pylint: disable=raising-bad-type
            except TypeError:
                # This is a default handler
                raise MessageException(
                    condition=ErrorCondition.UnknownError, description="Send failed."
                ) from None
    
    def send_message(self, message: Message, **kwargs):
        retry_settings = self._retry_policy.configure_retries()
        retry_active = True
        absolute_timeout = kwargs.pop("timeout", 0) or 0
        start_time = time.time()
        while retry_active:
            try:
                if absolute_timeout < 0:
                    raise TimeoutError("Operation timed out.")
                return self._send_message_impl(message, timeout=absolute_timeout, **kwargs)
            except AMQPException as exc:
                if not self._retry_policy.is_retryable(exc):
                    raise
                if absolute_timeout >= 0:
                    retry_active = self._retry_policy.increment(retry_settings, exc)
                    if not retry_active:
                        break
                    time.sleep(self._retry_policy.get_backoff_time(retry_settings, exc))
                    if exc.condition == ErrorCondition.LinkDetachForced:
                        self.detach(close=True)  
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
    
    def do_work(self) -> bool:
        self.update_pending_deliveries()
        return self._session.do_work()