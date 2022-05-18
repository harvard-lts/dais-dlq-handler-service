import os

from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.publishers.stomp_publisher_base import StompPublisherBase


class TransferResubmittingPublisher(StompPublisherBase):

    def publish_message(self, original_message_body: dict, current_retry_count: int, queue_name: str) -> None:
        self._logger.info("Increasing message retry count...")
        original_message_body['admin_metadata']['current_retry_count'] = current_retry_count + 1
        self._logger.info("Publishing message with body {} to queue {}".format(str(original_message_body), queue_name))
        self._publish_message(original_message_body, queue_name)

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_TRANSFER_HOST'),
            mq_port=os.getenv('MQ_TRANSFER_PORT'),
            mq_ssl_enabled=os.getenv('MQ_TRANSFER_SSL_ENABLED'),
            mq_user=os.getenv('MQ_TRANSFER_USER'),
            mq_password=os.getenv('MQ_TRANSFER_PASSWORD')
        )
