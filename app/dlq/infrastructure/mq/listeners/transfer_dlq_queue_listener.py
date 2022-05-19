import os

from app.containers import Listeners
from app.dlq.infrastructure.mq.exceptions.mq_exception import MqException
from app.dlq.infrastructure.mq.listeners.stomp_listener_base import StompListenerBase
from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.publishers.transfer_resubmitting_publisher import TransferResubmittingPublisher


class TransferDlqQueueListener(StompListenerBase):

    def __init__(
            self,
            transfer_resubmitting_publisher: TransferResubmittingPublisher = Listeners.transfer_resubmitting_publisher()
    ) -> None:
        super().__init__()
        self.__transfer_resubmitting_publisher = transfer_resubmitting_publisher

    def _get_queue_name(self) -> str:
        return os.getenv('MQ_TRANSFER_QUEUE_DLQ')

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_TRANSFER_HOST'),
            mq_port=os.getenv('MQ_TRANSFER_PORT'),
            mq_ssl_enabled=os.getenv('MQ_TRANSFER_SSL_ENABLED'),
            mq_user=os.getenv('MQ_TRANSFER_USER'),
            mq_password=os.getenv('MQ_TRANSFER_PASSWORD')
        )

    def _handle_received_message(self, message_body: dict) -> None:
        self._logger.info("Received message from Transfer DLQ Queue. Message body: " + str(message_body))

        message_admin_metadata = message_body.get('admin_metadata')
        if message_admin_metadata is None:
            self._logger.info("Received message does not include admin_metadata. Ignoring message...")
            return

        original_queue = message_admin_metadata.get('original_queue')
        if original_queue is None:
            self._logger.info(
                "Received message does not include original_queue inside admin_metadata. Ignoring message..."
            )
            return

        retry_count = message_admin_metadata.get('retry_count')
        if retry_count is None:
            self._logger.info(
                "Received message does not include current_retry_count inside admin_metadata. Ignoring message..."
            )
            return

        retry_count = int(retry_count)
        self._logger.info("Received message has {} retries".format(retry_count))

        mq_max_retries = self.__get_mq_max_retries()
        self._logger.info("Max retries permitted: {}".format(mq_max_retries))

        if retry_count < mq_max_retries:
            self._logger.info("Resubmitting message...")
            try:
                self.__transfer_resubmitting_publisher.publish_message(
                    original_message_body=message_body,
                    current_retry_count=retry_count,
                    queue_name=original_queue
                )
            except MqException as me:
                self._logger.error(str(me))

            self._logger.info("Message resubmitted")
            self._logger.info("Sending notification message...")
            # TODO: notification message
        else:
            self._logger.info("Maximum message retry count reached")
            self._logger.info("Sending notification message...")
            # TODO: notification message

    def __get_mq_max_retries(self) -> int:
        return int(os.getenv('MQ_TRANSFER_MAX_RETRIES'))
