import os
from abc import ABC

from app.dlq.infrastructure.mq.exceptions.mq_exception import MqException
from app.dlq.infrastructure.mq.listeners.stomp_listener_base import StompListenerBase
from app.dlq.infrastructure.mq.publishers.resubmitting_publisher_base import ResubmittingPublisherBase


class DlqQueueListenerBase(StompListenerBase, ABC):

    def __init__(self, resubmitting_publisher: ResubmittingPublisherBase) -> None:
        super().__init__()
        self.__resubmitting_publisher = resubmitting_publisher

    def _handle_received_message(self, message_body: dict, message_id: str) -> None:
        self._logger.info(
            "Received message from DLQ Queue. Message body: {}. Message id: {}".format(str(message_body), message_id)
        )

        message_admin_metadata = message_body.get('admin_metadata')
        if message_admin_metadata is None:
            self._logger.info(
                "Received message {} does not include admin_metadata. Ignoring message...".format(message_id)
            )
            return

        retry_count = int(message_admin_metadata['retry_count'])
        self._logger.info("Received message {} has {} retries".format(message_id, retry_count))

        mq_max_retries = self.__get_message_max_retries()
        self._logger.info("Max retries permitted: {}".format(mq_max_retries))

        if retry_count < mq_max_retries:
            original_queue = message_admin_metadata['original_queue']
            self.__resubmit_message(message_body, message_id, original_queue, retry_count)
        else:
            self._logger.info("Maximum message retry count reached for message {}".format(message_id))
            self._logger.info("Sending notification message...")
            # TODO: notification message

    def __resubmit_message(self, message_body: dict, message_id: str, original_queue: str, retry_count: int) -> None:
        self._logger.info("Resubmitting message {}...".format(message_id))
        try:
            self.__resubmitting_publisher.resubmit_message(
                original_message_body=message_body,
                current_retry_count=retry_count,
                queue_name=original_queue
            )
        except MqException as me:
            self._logger.error(str(me))
            raise me

        self._logger.info("Message {} resubmitted".format(message_id))
        self._logger.info("Sending notification message...")
        # TODO: notification message

    def __get_message_max_retries(self) -> int:
        return int(os.getenv('MESSAGE_MAX_RETRIES'))
