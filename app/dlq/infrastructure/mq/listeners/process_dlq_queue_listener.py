import os

from app.containers import Listeners
from app.dlq.infrastructure.mq.listeners.dlq_queue_listener_base import DlqQueueListenerBase
from app.dlq.infrastructure.mq.mq_connection_params import MqConnectionParams
from app.dlq.infrastructure.mq.publishers.process_resubmitting_publisher import ProcessResubmittingPublisher


class ProcessDlqQueueListener(DlqQueueListenerBase):

    def __init__(
            self,
            process_resubmitting_publisher: ProcessResubmittingPublisher = Listeners.process_resubmitting_publisher()
    ) -> None:
        super().__init__(process_resubmitting_publisher)

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
