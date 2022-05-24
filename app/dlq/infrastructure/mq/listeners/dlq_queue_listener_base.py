from abc import ABC

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.domain.services.exceptions.dlq_service_exception import DlqServiceException
from app.dlq.infrastructure.mq.listeners.stomp_listener_base import StompListenerBase


class DlqQueueListenerBase(StompListenerBase, ABC):

    def __init__(self, dlq_service: DlqService) -> None:
        super().__init__()
        self.__dlq_service = dlq_service

    def _handle_received_message(self, message_body: dict, message_id: str, message_subscription: str) -> None:
        self._logger.info(
            "Received message from DLQ Queue. Message body: {}. Message id: {}".format(str(message_body), message_id)
        )
        try:
            self.__dlq_service.handle_dlq_message(message_body, message_id)
        except DlqServiceException as dse:
            self._logger.error(str(dse))
            return

        self._logger.info("Acknowledging the consumption of message with id: {}...".format(message_id))
        self._connection.ack(id=message_id, subscription=message_subscription)
