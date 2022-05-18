import os

from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.listeners.stomp_listener_base import StompListenerBase


class ProcessDlqQueueListener(StompListenerBase):

    def _get_queue_name(self) -> str:
        return os.getenv('MQ_PROCESS_QUEUE_DLQ')

    def _get_mq_connection_params(self) -> MqConnectionParams:
        return MqConnectionParams(
            mq_host=os.getenv('MQ_PROCESS_HOST'),
            mq_port=os.getenv('MQ_PROCESS_PORT'),
            mq_ssl_enabled=os.getenv('MQ_PROCESS_SSL_ENABLED'),
            mq_user=os.getenv('MQ_PROCESS_USER'),
            mq_password=os.getenv('MQ_PROCESS_PASSWORD')
        )

    def _handle_received_message(self, message_body: dict) -> None:
        self._logger.info("Received message from Process DLQ Queue. Message body: " + str(message_body))
