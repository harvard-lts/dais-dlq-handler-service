from abc import ABC

from app.dlq.domain.services.dlq_service import DlqService
from app.dlq.infrastructure.mq.listeners.stomp_listener_base import StompListenerBase


class DlqQueueListenerBase(StompListenerBase, ABC):

    def __init__(self, dlq_service: DlqService) -> None:
        super().__init__()
        self.__dlq_service = dlq_service

    def _handle_received_message(self, message_body: dict, message_id: str) -> None:
        self._logger.info(
            "Received message from DLQ Queue. Message body: {}. Message id: {}".format(str(message_body), message_id)
        )
        self.__dlq_service.handle_dlq_message(message_body, message_id)
